#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean, median
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
        telem, coverage = {}, {}
        for key in telemetry_keys:
            def complete(row):
                counts = row.get("telemetry_coverage")
                # Historical rows have no turn-level provenance; never invent it.
                return counts is None or counts.get(key, 0) == row.get("attempted_turns", 1)
            values = [float(x["telemetry"][key]) for x in items
                      if complete(x) and isinstance(x.get("telemetry", {}).get(key), (int, float))
                      and not isinstance(x["telemetry"][key], bool)
                      and math.isfinite(x["telemetry"][key]) and x["telemetry"][key] >= 0]
            telem[key] = round(mean(values), 6) if values else None
            coverage[key] = {"reported":len(values), "total":len(items), "complete":len(values)==len(items),
                             "partial_runs":sum(key in x.get("telemetry", {}) and not complete(x) for x in items),
                             "turn_coverage_unknown_runs":sum("telemetry_coverage" not in x for x in items)}
        out[condition] = {
            "runs": len(items),
            "passed": passed,
            "pass_rate": round(passed / len(items), 4) if items else 0,
            "mean_changed_files": round(mean(len(x.get("changed_files", [])) for x in items), 4) if items else 0,
            "mean_lines_changed": round(mean(int(x.get("lines_added", 0)) + int(x.get("lines_deleted", 0)) for x in items), 4) if items else 0,
            "mean_wall_seconds": round(mean(float(x.get("wall_seconds", 0)) for x in items), 4) if items else 0,
            "mean_telemetry": telem,
            "telemetry_coverage": coverage,
            "median_wall_seconds": median([float(x["wall_seconds"]) for x in items]),
            "p95_wall_seconds": sorted(float(x["wall_seconds"]) for x in items)[math.ceil(.95 * len(items)) - 1],
            "timeouts": sum(any(f.get("returncode") == 124 for f in x.get("agent_failures", [])) for x in items),
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
