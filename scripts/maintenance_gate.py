#!/usr/bin/env python3
"""Enforce evidence-backed maintenance for material Plat changes.

This script is a repository-maintenance/CI helper. It is intentionally outside
Plat's runtime path: normal engineering requests must not perform market scans.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_PATH = ROOT / "docs" / "maintenance-evidence.json"
RESEARCH_LOG_PATH = ROOT / "docs" / "RESEARCH_LOG.md"

MATERIAL_EXACT = {
    "install.sh",
    "install.ps1",
    ".github/workflows/validate-plat.yml",
    ".github/workflows/release-plat.yml",
}
MATERIAL_PREFIXES = ("skills/plat/", "scripts/")
NON_BEHAVIORAL_SKILL_FILES = {"skills/plat/LICENSE.txt"}
VALID_REUSE = {"principle-only", "adapted", "copied"}


@dataclass(frozen=True)
class GateResult:
    required: bool
    passed: bool
    material_files: tuple[str, ...]
    evidence_id: str | None
    errors: tuple[str, ...]


def normalize_paths(paths: Iterable[str]) -> list[str]:
    normalized = set()
    for raw in paths:
        value = str(raw).strip().replace("\\", "/")
        if not value:
            continue
        while value.startswith("./"):
            value = value[2:]
        value = value.lstrip("/")
        normalized.add(value)
    return sorted(normalized)


def is_material(path: str) -> bool:
    path = path.replace("\\", "/")
    while path.startswith("./"):
        path = path[2:]
    path = path.lstrip("/")
    if path in NON_BEHAVIORAL_SKILL_FILES:
        return False
    if path in MATERIAL_EXACT:
        return True
    return any(path.startswith(prefix) for prefix in MATERIAL_PREFIXES)


def material_changes(changed_files: Iterable[str]) -> list[str]:
    return [p for p in normalize_paths(changed_files) if is_material(p)]


def _latest_entry(payload: dict) -> dict | None:
    entries = payload.get("entries")
    if not isinstance(entries, list) or not entries:
        return None
    entry = entries[-1]
    return entry if isinstance(entry, dict) else None


def evaluate(
    changed_files: Iterable[str],
    evidence_payload: dict | None,
    research_log: str,
) -> GateResult:
    changed = normalize_paths(changed_files)
    material = material_changes(changed)
    if not material:
        return GateResult(False, True, (), None, ())

    errors: list[str] = []
    if "docs/maintenance-evidence.json" not in changed:
        errors.append("material Plat changes require docs/maintenance-evidence.json to change")
    if "docs/RESEARCH_LOG.md" not in changed:
        errors.append("material Plat changes require docs/RESEARCH_LOG.md to change")

    payload = evidence_payload or {}
    if payload.get("schema_version") != 1:
        errors.append("maintenance evidence schema_version must be 1")

    entry = _latest_entry(payload)
    if entry is None:
        errors.append("maintenance evidence must contain at least one entry")
        return GateResult(True, False, tuple(material), None, tuple(errors))

    evidence_id = entry.get("id") if isinstance(entry.get("id"), str) else None
    for key in ("id", "date", "capability", "adopted", "rejected", "tests", "material_files", "sources"):
        value = entry.get(key)
        if value in (None, "", []):
            errors.append(f"latest maintenance evidence entry missing non-empty {key}")

    sources = entry.get("sources") if isinstance(entry.get("sources"), list) else []
    if len(sources) < 2:
        errors.append("latest maintenance evidence entry must inspect at least 2 public sources")
    for idx, source in enumerate(sources):
        if not isinstance(source, dict):
            errors.append(f"source[{idx}] must be an object")
            continue
        for key in ("repo", "license", "inspected", "reuse"):
            if not source.get(key):
                errors.append(f"source[{idx}] missing {key}")
        reuse = source.get("reuse")
        if reuse and reuse not in VALID_REUSE:
            errors.append(f"source[{idx}] reuse must be one of {sorted(VALID_REUSE)}")
        if isinstance(source.get("license"), str) and source["license"].strip().lower() in {"unknown", "none", "no license"}:
            if reuse != "principle-only":
                errors.append(f"source[{idx}] with unknown/no license must be principle-only")

    recorded_files = normalize_paths(entry.get("material_files", []) if isinstance(entry.get("material_files"), list) else [])
    missing_coverage = sorted(set(material) - set(recorded_files))
    if missing_coverage:
        errors.append("maintenance evidence does not cover material files: " + ", ".join(missing_coverage))

    tests = entry.get("tests") if isinstance(entry.get("tests"), list) else []
    if not tests:
        errors.append("latest maintenance evidence entry must record tests added/run")

    if evidence_id:
        if evidence_id not in research_log:
            errors.append(f"RESEARCH_LOG.md must reference maintenance evidence id {evidence_id}")
        for source in sources:
            repo = source.get("repo") if isinstance(source, dict) else None
            if repo and repo not in research_log:
                errors.append(f"RESEARCH_LOG.md must mention inspected source {repo}")

    return GateResult(True, not errors, tuple(material), evidence_id, tuple(errors))


def changed_files_from_git(base_ref: str) -> list[str]:
    proc = subprocess.run(
        ["git", "diff", "--name-only", f"{base_ref}...HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return normalize_paths(proc.stdout.splitlines())


def infer_base_ref() -> str:
    base = os.environ.get("GITHUB_BASE_REF")
    if base:
        return f"origin/{base}"
    return "HEAD^"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate market-scan evidence for material Plat changes.")
    parser.add_argument("--base-ref", help="Git base ref used to detect changed files.")
    parser.add_argument("--changed-file", action="append", default=[], help="Explicit changed path; repeatable for tests/local checks.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable result.")
    args = parser.parse_args()

    try:
        changed = args.changed_file or changed_files_from_git(args.base_ref or infer_base_ref())
        payload = load_json(EVIDENCE_PATH) if EVIDENCE_PATH.exists() else {}
        research = RESEARCH_LOG_PATH.read_text(encoding="utf-8") if RESEARCH_LOG_PATH.exists() else ""
        result = evaluate(changed, payload, research)
    except (OSError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        if args.json:
            print(json.dumps({"required": True, "passed": False, "errors": [f"{type(exc).__name__}: {exc}"]}, indent=2))
        else:
            print(f"PLAT MAINTENANCE GATE FAILED\n- {type(exc).__name__}: {exc}")
        return 1

    if args.json:
        print(json.dumps(asdict(result), indent=2))
    elif result.passed:
        if result.required:
            print("PLAT MAINTENANCE GATE PASSED")
            print(f"- evidence: {result.evidence_id}")
            print(f"- material files: {len(result.material_files)}")
        else:
            print("PLAT MAINTENANCE GATE PASSED")
            print("- no material Plat behavior/runtime changes detected")
    else:
        print("PLAT MAINTENANCE GATE FAILED")
        for error in result.errors:
            print(f"- {error}")

    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
