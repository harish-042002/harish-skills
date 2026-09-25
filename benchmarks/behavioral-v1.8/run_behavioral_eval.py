#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import math
import re
import shlex
import signal
import sys
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


def run(cmd, cwd: Path, env=None, timeout: float = 900, log_prefix: Path | None = None):
    """Bound time/output, retain raw logs, and reap the whole finite process group."""
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("timeout must be finite and positive")
    with tempfile.TemporaryDirectory(prefix="plat-command-") as tmp:
        prefix = log_prefix or Path(tmp) / "command"
        prefix.parent.mkdir(parents=True, exist_ok=True)
        paths = [Path(str(prefix) + ext) for ext in (".stdout", ".stderr")]
        code = None
        with paths[0].open("wb") as out, paths[1].open("wb") as err:
            proc = subprocess.Popen(cmd, shell=isinstance(cmd, str), cwd=cwd, env=env,
                                    stdin=subprocess.DEVNULL, stdout=out, stderr=err,
                                    start_new_session=(os.name == "posix"))
            deadline = time.monotonic() + timeout
            try:
                while proc.poll() is None:
                    if time.monotonic() >= deadline:
                        code = 124
                        break
                    if os.fstat(out.fileno()).st_size + os.fstat(err.fileno()).st_size > 64 * 1024 * 1024:
                        code = 125
                        break
                    time.sleep(.02)
            finally:
                if os.name == "posix":
                    try:
                        os.killpg(proc.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                elif proc.poll() is None:
                    subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
                if proc.poll() is None:
                    proc.kill()
                proc.wait(timeout=5)
        def tail(path):
            with path.open("rb") as stream:
                stream.seek(max(0, path.stat().st_size - 65536))
                return stream.read().decode("utf-8", errors="replace")
        return subprocess.CompletedProcess(cmd, code if code is not None else proc.returncode,
                                           tail(paths[0]), tail(paths[1]))


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


def manifest(workspace: Path) -> dict[str, dict]:
    """Do not trust git HEAD or ignore rules after an agent has edited the repo."""
    out = {}
    for base, dirs, names in os.walk(workspace, followlinks=False):
        dirs[:] = sorted(x for x in dirs if x not in {".git", "__pycache__", ".pytest_cache", ".plat"})
        links = [x for x in dirs if (Path(base) / x).is_symlink()]
        dirs[:] = [x for x in dirs if x not in links]
        for name in sorted(names + links):
            path = Path(base) / name
            rel = path.relative_to(workspace).as_posix()
            digest = hashlib.sha256()
            lines = 0
            if path.is_symlink():
                digest.update(os.readlink(path).encode())
                mode = "symlink"
            else:
                mode = str(path.stat().st_mode & 0o777)
                with path.open("rb") as fh:
                    for chunk in iter(lambda: fh.read(65536), b""):
                        digest.update(chunk)
                        lines += chunk.count(b"\n")
            out[rel] = {"sha256": digest.hexdigest(), "lines": lines, "mode": mode}
    return out


def changed_stats(workspace: Path, before: dict | None = None) -> tuple[list[str], int, int]:
    if before is not None:
        after = manifest(workspace)
        changed = sorted(p for p in before.keys() | after.keys() if before.get(p) != after.get(p))
        # Manifest counts are entire changed-file lines; do not call them a minimal diff.
        return changed, sum(after.get(p, {}).get("lines", 0) for p in changed), sum(before.get(p, {}).get("lines", 0) for p in changed)
    names = run(["git", "diff", "--name-only", "-z", "HEAD"], workspace)
    untracked = run(["git", "ls-files", "--others", "-z"], workspace)
    if names.returncode or untracked.returncode:
        raise RuntimeError("cannot measure workspace changes")
    changed = sorted(set(x for x in (names.stdout + untracked.stdout).split("\0") if x))
    numstat = run(["git", "diff", "--numstat", "HEAD"], workspace)
    added = deleted = 0
    for line in numstat.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
            added += int(parts[0]); deleted += int(parts[1])
    for rel in untracked.stdout.split("\0"):
        if rel:
            path = workspace / rel
            if path.is_file() and not path.is_symlink():
                with path.open("rb") as fh:
                    added += sum(chunk.count(b"\n") for chunk in iter(lambda: fh.read(65536), b""))
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


TELEMETRY_KEYS = {"input_tokens", "output_tokens", "cache_read_tokens", "cache_write_tokens",
                  "reasoning_output_tokens", "tool_calls", "repair_turns", "cost_usd",
                  "reported_cost_usd", "estimated_cost_usd"}


def numeric_telemetry(path: Path) -> dict[str, float]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(data, dict):
        return {}
    return {k: float(v) for k, v in data.items()
            if k in TELEMETRY_KEYS and isinstance(v, (int, float))
            and not isinstance(v, bool) and math.isfinite(v) and v >= 0}


def run_case(case, agent_command, condition, repetition, timeout, *, artifacts=None,
             skill_path=None, activation=None, metadata=None):
    artifact_dir = Path(artifacts or "behavioral-artifacts").resolve() / f"{condition}-{case['id']}-{repetition}"
    artifact_dir.mkdir(parents=True, exist_ok=False)
    with tempfile.TemporaryDirectory(prefix=f"plat-eval-{case['id']}-") as td:
        workspace = Path(td) / "workspace"
        shutil.copytree(ROOT / case["fixture"], workspace)
        if skill_path is not None:
            shutil.copytree(Path(skill_path), workspace / ".agents/skills/plat",
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            (workspace / "AGENTS.md").write_text(activation or "Use the installed Plat skill for engineering tasks.\n")
        init_repo(workspace)
        baseline_commit = run(["git", "rev-parse", "HEAD"], workspace).stdout.strip()
        baseline = manifest(workspace)
        original_verifier = (workspace / "verify.py").read_bytes()
        frozen = artifact_dir / "frozen_verify.py"
        frozen.write_bytes(original_verifier)
        transcript, telemetry, failures, coverage = [], {}, [], {}
        started = time.monotonic()
        deadline = started + timeout
        agent_seconds = 0.0
        attempted = 0
        for idx, turn in enumerate(case["turns"], start=1):
            attempted += 1
            transcript.append({"role": "developer", "content": turn})
            turn_file = artifact_dir / f"turn-{idx}.txt"
            turn_file.write_text(turn, encoding="utf-8")
            transcript_file = artifact_dir / "transcript.json"
            transcript_file.write_text(json.dumps(transcript, indent=2), encoding="utf-8")
            result_file = artifact_dir / f"agent-result-{idx}.json"
            env = os.environ.copy()
            env["PYTHONDONTWRITEBYTECODE"] = "1"
            env.update({"PLAT_EVAL_WORKSPACE": str(workspace), "PLAT_EVAL_CASE_ID": case["id"],
                        "PLAT_EVAL_TURN_INDEX": str(idx), "PLAT_EVAL_TURN_FILE": str(turn_file),
                        "PLAT_EVAL_TRANSCRIPT_FILE": str(transcript_file),
                        "PLAT_EVAL_RESULT_FILE": str(result_file), "PLAT_EVAL_CONDITION": condition})
            values = dict(workspace=workspace, case_id=case["id"], turn=idx, turn_file=turn_file,
                          transcript_file=transcript_file, result_file=result_file, condition=condition)
            cmd = agent_command
            for key, value in values.items():
                cmd = cmd.replace("{" + key + "}", shlex.quote(str(value)))
            t = time.monotonic()
            remaining = deadline - t
            proc = (run(cmd, workspace, env=env, timeout=remaining,
                        log_prefix=artifact_dir / f"agent-{idx}") if remaining > 0
                    else subprocess.CompletedProcess(cmd, 124, "", "case deadline exhausted"))
            agent_seconds += time.monotonic() - t
            # Failed attempts still consumed time and can still have usage/cost.
            for key, value in numeric_telemetry(result_file).items():
                telemetry[key] = telemetry.get(key, 0.0) + value
                coverage[key] = coverage.get(key, 0) + 1
            transcript.append({"role": "assistant", "content": proc.stdout})
            if proc.returncode != 0:
                failures.append({"turn": idx, "returncode": proc.returncode, "stderr": proc.stderr[-2000:]})
                break
        verifier_intact = (workspace / "verify.py").is_file() and not (workspace / "verify.py").is_symlink() and (workspace / "verify.py").read_bytes() == original_verifier
        env = os.environ.copy()
        env.update(PYTHONDONTWRITEBYTECODE="1", PYTHONPATH=str(workspace))
        verifier_start = time.monotonic()
        verifier = run([sys.executable, str(frozen)], workspace, env=env, timeout=min(timeout, 30),
                       log_prefix=artifact_dir / "verifier") if verifier_intact else subprocess.CompletedProcess([], 1, "", "verifier was modified")
        changed, added, deleted = changed_stats(workspace, baseline)
        unexpected = [p for p in changed if not allowed_path(p, case.get("allowed_changed_globs", ["*"]))]
        forbidden = scan_forbidden(workspace, changed, case.get("forbidden_regex", []))
        # Preserve full tracked patch even if the agent committed its edits.
        diff = run(["git", "diff", "--binary", baseline_commit], workspace,
                   log_prefix=artifact_dir / "tracked-diff")
        shutil.copyfile(artifact_dir / "tracked-diff.stdout", artifact_dir / "changes.diff")
        # Git diff omits untracked files: retain changed contents separately.
        for rel in changed:
            path = workspace / rel
            if path.is_file() and not path.is_symlink():
                target = artifact_dir / "changed-files" / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, target)
        (artifact_dir / "before-manifest.json").write_text(json.dumps(baseline, indent=2))
        (artifact_dir / "after-manifest.json").write_text(json.dumps(manifest(workspace), indent=2))
        passed = verifier.returncode == 0 and verifier_intact and not failures and not unexpected and not forbidden
        row = dict(case_id=case["id"], category=case.get("category", "uncategorized"), condition=condition,
                   repetition=repetition, passed=passed, verifier_returncode=verifier.returncode,
                   verifier_stdout=verifier.stdout[-4000:], verifier_stderr=verifier.stderr[-4000:],
                   verifier_intact=verifier_intact, agent_failures=failures, changed_files=changed,
                   unexpected_changed_files=unexpected, forbidden_hits=forbidden,
                   lines_added=added, lines_deleted=deleted, line_count_semantics="whole_changed_files_not_minimal_diff",
                   wall_seconds=round(time.monotonic()-started, 6), agent_wall_seconds=round(agent_seconds, 6),
                   verifier_and_measurement_seconds=round(time.monotonic()-verifier_start, 6),
                   attempted_turns=attempted, telemetry=telemetry, telemetry_coverage=coverage,
                   artifacts=str(artifact_dir), metadata=metadata or {"kind":"unspecified_adapter"})
        (artifact_dir / "result.json").write_text(json.dumps(row, indent=2, allow_nan=False))
        return row


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
    ap.add_argument("--artifacts", default="behavioral-artifacts")
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
            result = run_case(case, args.agent_command, args.condition, rep, args.timeout, artifacts=args.artifacts)
            results.append(result)
            # Persist completed runs before starting another potentially failing one.
            Path(args.results).write_text(json.dumps({"schema_version":1, "condition":args.condition,
                                                     "results":results}, indent=2, allow_nan=False))
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
    return 0 if all(row["passed"] for row in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
