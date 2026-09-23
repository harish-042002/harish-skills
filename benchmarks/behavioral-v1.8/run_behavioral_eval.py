#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
from typing import Any

ROOT = Path(__file__).resolve().parent
DEFAULT_CASES = ROOT / "cases.json"


def load_cases(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1:
        raise ValueError("cases schema_version must be 1")
    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("cases must be a non-empty list")
    seen: set[str] = set()
    for case in cases:
        cid = case.get("id")
        if not isinstance(cid, str) or not cid or cid in seen:
            raise ValueError(f"invalid/duplicate case id: {cid!r}")
        seen.add(cid)
        if not isinstance(case.get("turns"), list) or not case["turns"]:
            raise ValueError(f"{cid}: turns must be non-empty")
        fixture = ROOT / str(case.get("fixture", ""))
        if not fixture.is_dir():
            raise ValueError(f"{cid}: fixture not found: {fixture}")
        if not case.get("verifier"):
            raise ValueError(f"{cid}: verifier required")
    return cases


def run(cmd: str, cwd: Path, env: dict[str, str] | None = None, timeout: int = 900) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, env=env, shell=True, text=True, capture_output=True, timeout=timeout)


def init_repo(workspace: Path) -> None:
    for cmd in [
        "git init -q",
        "git config user.email plat-eval@example.invalid",
        "git config user.name plat-eval",
        "git add .",
        "git commit -qm baseline",
    ]:
        proc = run(cmd, workspace)
        if proc.returncode != 0:
            raise RuntimeError(f"failed to initialize fixture repo: {cmd}\n{proc.stderr}")


def changed_stats(workspace: Path) -> tuple[list[str], int, int]:
    names = run("git diff --name-only HEAD", workspace)
    changed = [x.strip() for x in names.stdout.splitlines() if x.strip()]
    numstat = run("git diff --numstat HEAD", workspace)
    added = deleted = 0
    for line in numstat.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
            added += int(parts[0])
            deleted += int(parts[1])
    return changed, added, deleted


def allowed_path(path: str, globs: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in globs)


def scan_forbidden(workspace: Path, changed: list[str], patterns: list[str]) -> list[dict[str, str]]:
    import re
    hits: list[dict[str, str]] = []
    compiled = [(p, re.compile(p, re.I)) for p in patterns]
    for rel in changed:
        path = workspace / rel
        if not path.is_file() or path.stat().st_size > 512_000:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeError:
            continue
        for raw, rx in compiled:
            if rx.search(text):
                hits.append({"path": rel, "pattern": raw})
    return hits


def numeric_telemetry(path: Path) -> dict[str, float]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return {k: float(v) for k, v in data.items() if isinstance(v, (int, float)) and not isinstance(v, bool)}


def run_case(case: dict[str, Any], agent_command: str, condition: str, repetition: int, timeout: int) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix=f"plat-eval-{case['id']}-") as td:
        workspace = Path(td) / "workspace"
        shutil.copytree(ROOT / case["fixture"], workspace)
        init_repo(workspace)
        transcript: list[dict[str, str]] = []
        telemetry: dict[str, float] = {}
        agent_failures: list[dict[str, Any]] = []
        started = time.monotonic()

        for idx, turn in enumerate(case["turns"], start=1):
            transcript.append({"role": "developer", "content": turn})
            turn_file = Path(td) / f"turn-{idx}.txt"
            turn_file.write_text(turn, encoding="utf-8")
            transcript_file = Path(td) / "transcript.json"
            transcript_file.write_text(json.dumps(transcript, indent=2), encoding="utf-8")
            result_file = Path(td) / f"agent-result-{idx}.json"
            env = os.environ.copy()
            env["PYTHONDONTWRITEBYTECODE"] = "1"
            env.update({
                "PLAT_EVAL_WORKSPACE": str(workspace),
                "PLAT_EVAL_CASE_ID": case["id"],
                "PLAT_EVAL_TURN_INDEX": str(idx),
                "PLAT_EVAL_TURN_FILE": str(turn_file),
                "PLAT_EVAL_TRANSCRIPT_FILE": str(transcript_file),
                "PLAT_EVAL_RESULT_FILE": str(result_file),
                "PLAT_EVAL_CONDITION": condition,
            })
            cmd = agent_command.format(
                workspace=str(workspace),
                case_id=case["id"],
                turn=idx,
                turn_file=str(turn_file),
                transcript_file=str(transcript_file),
                result_file=str(result_file),
                condition=condition,
            )
            proc = run(cmd, workspace, env=env, timeout=timeout)
            if proc.returncode != 0:
                agent_failures.append({"turn": idx, "returncode": proc.returncode, "stderr": proc.stderr[-2000:]})
                break
            for key, value in numeric_telemetry(result_file).items():
                telemetry[key] = telemetry.get(key, 0.0) + value

        verifier_env = os.environ.copy()
        verifier_env["PYTHONDONTWRITEBYTECODE"] = "1"
        verifier = run(case["verifier"], workspace, env=verifier_env, timeout=timeout)
        changed, added, deleted = changed_stats(workspace)
        unexpected = [p for p in changed if not allowed_path(p, case.get("allowed_changed_globs", ["*"]))]
        forbidden_hits = scan_forbidden(workspace, changed, case.get("forbidden_regex", []))
        duration = time.monotonic() - started
        passed = verifier.returncode == 0 and not agent_failures and not unexpected and not forbidden_hits

        return {
            "case_id": case["id"],
            "category": case.get("category", "uncategorized"),
            "condition": condition,
            "repetition": repetition,
            "passed": passed,
            "verifier_returncode": verifier.returncode,
            "verifier_stdout": verifier.stdout[-4000:],
            "verifier_stderr": verifier.stderr[-4000:],
            "agent_failures": agent_failures,
            "changed_files": changed,
            "unexpected_changed_files": unexpected,
            "forbidden_hits": forbidden_hits,
            "lines_added": added,
            "lines_deleted": deleted,
            "wall_seconds": round(duration, 4),
            "telemetry": telemetry,
        }


def main() -> int:
    ap = argparse.ArgumentParser(description="Run Plat behavioral coding-agent evaluations.")
    ap.add_argument("--cases", default=str(DEFAULT_CASES))
    ap.add_argument("--agent-command", help="Host wrapper command; may use {workspace}, {turn_file}, {transcript_file}, {result_file}, {condition}, {case_id}, {turn}.")
    ap.add_argument("--condition", default="plat")
    ap.add_argument("--repetitions", type=int, default=1)
    ap.add_argument("--case", action="append", default=[])
    ap.add_argument("--results", default="behavioral-results.json")
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--plan", action="store_true")
    args = ap.parse_args()

    cases = load_cases(Path(args.cases))
    if args.case:
        wanted = set(args.case)
        cases = [c for c in cases if c["id"] in wanted]
        missing = wanted - {c["id"] for c in cases}
        if missing:
            raise SystemExit("unknown case(s): " + ", ".join(sorted(missing)))

    if args.plan:
        print(f"behavioral eval plan: {len(cases)} cases")
        for case in cases:
            print(f"- {case['id']}: {len(case['turns'])} turn(s), category={case.get('category')}")
        return 0

    if not args.agent_command:
        ap.error("--agent-command is required unless --plan is used")
    if args.repetitions < 1:
        ap.error("--repetitions must be >= 1")

    results: list[dict[str, Any]] = []
    for rep in range(1, args.repetitions + 1):
        for case in cases:
            result = run_case(case, args.agent_command, args.condition, rep, args.timeout)
            results.append(result)
            state = "PASS" if result["passed"] else "FAIL"
            print(f"{state} {case['id']} rep={rep} files={len(result['changed_files'])} wall={result['wall_seconds']}s")

    payload = {
        "schema_version": 1,
        "condition": args.condition,
        "repetitions": args.repetitions,
        "cases": [c["id"] for c in cases],
        "results": results,
    }
    Path(args.results).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"wrote {args.results}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
