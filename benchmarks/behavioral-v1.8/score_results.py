#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


def load(paths: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for raw in paths:
        data = json.loads(Path(raw).read_text(encoding="utf-8"))
        if data.get("schema_version") != 1:
            raise ValueError(f"{raw}: unsupported schema")
        rows.extend(data.get("results", []))
    return rows


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[str(row.get("condition", "unknown"))].append(row)
    out: dict[str, Any] = {}
    for condition, items in sorted(groups.items()):
        passed = sum(bool(x.get("passed")) for x in items)
        telemetry_keys = sorted({k for x in items for k in x.get("telemetry", {})})
        telem = {}
        for key in telemetry_keys:
            values = [float(x.get("telemetry", {}).get(key, 0)) for x in items]
            telem[key] = round(mean(values), 4)
        out[condition] = {
            "runs": len(items),
            "passed": passed,
            "pass_rate": round(passed / len(items), 4) if items else 0,
            "mean_changed_files": round(mean(len(x.get("changed_files", [])) for x in items), 4) if items else 0,
            "mean_lines_changed": round(mean(int(x.get("lines_added", 0)) + int(x.get("lines_deleted", 0)) for x in items), 4) if items else 0,
            "mean_wall_seconds": round(mean(float(x.get("wall_seconds", 0)) for x in items), 4) if items else 0,
            "mean_telemetry": telem,
        }
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Summarize Plat behavioral eval result JSON files.")
    ap.add_argument("results", nargs="+")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    summary = summarize(load(args.results))
    if args.json:
        print(json.dumps(summary, indent=2))
        return 0
    print("| Condition | Runs | Passed | Pass rate | Mean files | Mean LOC changed | Mean wall s |")
    print("| --- | ---: | ---: | ---: | ---: | ---: | ---: |")
    for condition, data in summary.items():
        print(f"| {condition} | {data['runs']} | {data['passed']} | {data['pass_rate']:.1%} | {data['mean_changed_files']} | {data['mean_lines_changed']} | {data['mean_wall_seconds']} |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
