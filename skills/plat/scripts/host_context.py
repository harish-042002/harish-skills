#!/usr/bin/env python3
"""Cross-agent telemetry normalizer for Plat.

The core protocol is host-neutral. Rich hosts may provide usage via environment,
JSON files, transcripts, hooks, or wrappers. Unknown hosts simply return
available=false and Plat keeps using deterministic context proxies.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
CANONICAL_FILE = Path(".plat/telemetry.json")
ENV_JSON = "PLAT_TELEMETRY_JSON"
ENV_FILE = "PLAT_TELEMETRY_FILE"
CAPABILITIES_ENV = "PLAT_HOST_CAPABILITIES_JSON"
TRANSCRIPT_ENV_VARS = (
    "PLAT_TRANSCRIPT_PATH",
    "CLAUDE_TRANSCRIPT_PATH",
    "CODEX_TRANSCRIPT_PATH",
    "CURSOR_TRANSCRIPT_PATH",
    "AGENT_TRANSCRIPT_PATH",
)

_COUNTER_KEYS = {
    "input_tokens": ("input_tokens", "prompt_tokens"),
    "output_tokens": ("output_tokens", "completion_tokens"),
    "cache_read_tokens": (
        "cache_read_tokens",
        "cache_read_input_tokens",
        "cached_input_tokens",
    ),
    "cache_write_tokens": (
        "cache_write_tokens",
        "cache_creation_input_tokens",
    ),
    "context_used_tokens": (
        "context_used_tokens",
        "context_tokens",
    ),
    "context_limit_tokens": (
        "context_limit_tokens",
        "context_window",
    ),
}


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def _number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _extract_from_dict(obj: dict[str, Any]) -> dict[str, float]:
    out: dict[str, float] = {}
    for canonical, aliases in _COUNTER_KEYS.items():
        for alias in aliases:
            value = _number(obj.get(alias))
            if value is not None:
                out[canonical] = max(out.get(canonical, 0.0), value)

    cost = _number(obj.get("cost_usd"))
    if cost is None:
        cost = _number(obj.get("total_cost_usd"))
    if cost is not None:
        out["cost_usd"] = max(out.get("cost_usd", 0.0), cost)

    details = obj.get("prompt_tokens_details")
    if isinstance(details, dict):
        cached = _number(details.get("cached_tokens"))
        if cached is not None:
            out["cache_read_tokens"] = max(
                out.get("cache_read_tokens", 0.0),
                cached,
            )
    return out


def _usage_candidates(obj: Any) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    if isinstance(obj, dict):
        direct = _extract_from_dict(obj)
        if direct:
            found.append(direct)
        for value in obj.values():
            found.extend(_usage_candidates(value))
    elif isinstance(obj, list):
        for value in obj:
            found.extend(_usage_candidates(value))
    return found


def _dedupe_id(obj: dict[str, Any], line_no: int) -> str:
    for path in (
        ("message", "id"),
        ("id",),
        ("request_id",),
        ("uuid",),
    ):
        cur: Any = obj
        ok = True
        for key in path:
            if not isinstance(cur, dict) or key not in cur:
                ok = False
                break
            cur = cur[key]
        if ok and isinstance(cur, str) and cur:
            return cur
    return f"line:{line_no}"


def parse_jsonl(path: Path) -> dict[str, Any]:
    totals = {
        "input_tokens": 0.0,
        "output_tokens": 0.0,
        "cache_read_tokens": 0.0,
        "cache_write_tokens": 0.0,
        "cost_usd": 0.0,
    }
    maxima = {
        "context_used_tokens": 0.0,
        "context_limit_tokens": 0.0,
    }
    seen: set[str] = set()
    records = 0

    with path.open("r", encoding="utf-8", errors="replace") as fh:
        for line_no, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(obj, dict):
                continue
            identity = _dedupe_id(obj, line_no)
            if identity in seen:
                continue
            seen.add(identity)

            candidates = _usage_candidates(obj)
            if not candidates:
                continue

            # One logical event can contain the same usage at multiple nesting
            # levels. Take the maximum per counter for that event, then sum
            # events. Context-window fields are maxima, not additive.
            event: dict[str, float] = {}
            for candidate in candidates:
                for key, value in candidate.items():
                    event[key] = max(event.get(key, 0.0), value)

            for key in totals:
                totals[key] += event.get(key, 0.0)
            for key in maxima:
                maxima[key] = max(maxima[key], event.get(key, 0.0))
            records += 1

    return {
        **{k: int(v) if float(v).is_integer() else v for k, v in totals.items()},
        **{k: int(v) if float(v).is_integer() else v for k, v in maxima.items()},
        "records": records,
    }


def normalize(payload: dict[str, Any], *, host: str = "unknown", source: str = "canonical") -> dict[str, Any]:
    usage_candidates = _usage_candidates(payload)
    merged: dict[str, float] = {}
    for candidate in usage_candidates:
        for key, value in candidate.items():
            merged[key] = max(merged.get(key, 0.0), value)

    capabilities = payload.get("capabilities")
    if not isinstance(capabilities, dict):
        capabilities = {}
    env_caps = os.environ.get(CAPABILITIES_ENV)
    if env_caps:
        parsed_caps = json.loads(env_caps)
        if isinstance(parsed_caps, dict):
            capabilities = {**capabilities, **parsed_caps}

    snapshot: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "available": bool(merged),
        "host": host or "unknown",
        "source": source,
        "observed_at": now_iso(),
        "capabilities": {
            key: bool(value)
            for key, value in capabilities.items()
            if key in {
                "isolated_context",
                "precompact_hook",
                "usage_telemetry",
            }
        },
    }
    for key, value in merged.items():
        snapshot[key] = int(value) if float(value).is_integer() else value

    if (
        snapshot.get("context_used_tokens") is not None
        and snapshot.get("context_limit_tokens")
    ):
        limit = float(snapshot["context_limit_tokens"])
        used = float(snapshot["context_used_tokens"])
        if limit > 0:
            snapshot["context_utilization"] = max(0.0, min(1.0, used / limit))
    return snapshot


def _load_json_payload(value: str) -> dict[str, Any]:
    parsed = json.loads(value)
    if not isinstance(parsed, dict):
        raise ValueError("telemetry payload must be a JSON object")
    return parsed


def discover(*, host: str = "unknown", transcript: Path | None = None) -> dict[str, Any]:
    raw_json = os.environ.get(ENV_JSON)
    if raw_json:
        return normalize(
            _load_json_payload(raw_json),
            host=host,
            source=f"env:{ENV_JSON}",
        )

    raw_file = os.environ.get(ENV_FILE)
    if raw_file:
        path = Path(raw_file).expanduser()
        payload = _load_json_payload(path.read_text(encoding="utf-8"))
        return normalize(payload, host=host, source=str(path))

    canonical = CANONICAL_FILE
    if canonical.exists():
        payload = _load_json_payload(canonical.read_text(encoding="utf-8"))
        snap = normalize(payload, host=host or str(payload.get("host", "unknown")), source=str(canonical))
        if payload.get("source"):
            snap["upstream_source"] = payload.get("source")
        return snap

    transcript_path = transcript
    if transcript_path is None:
        for name in TRANSCRIPT_ENV_VARS:
            value = os.environ.get(name)
            if value:
                transcript_path = Path(value).expanduser()
                break

    if transcript_path and transcript_path.exists():
        parsed = parse_jsonl(transcript_path)
        snap = normalize(parsed, host=host, source=str(transcript_path))
        snap["records"] = parsed.get("records", 0)
        return snap

    capabilities = {}
    env_caps = os.environ.get(CAPABILITIES_ENV)
    if env_caps:
        parsed_caps = json.loads(env_caps)
        if isinstance(parsed_caps, dict):
            capabilities = {
                key: bool(value)
                for key, value in parsed_caps.items()
                if key in {
                    "isolated_context",
                    "precompact_hook",
                    "usage_telemetry",
                }
            }
    return {
        "schema_version": SCHEMA_VERSION,
        "available": False,
        "host": host or "unknown",
        "source": "none",
        "observed_at": now_iso(),
        "capabilities": capabilities,
    }


def save(path: Path, snapshot: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize optional coding-agent telemetry for Plat.")
    parser.add_argument("--host", default=os.environ.get("PLAT_HOST", "unknown"))
    parser.add_argument("--transcript")
    parser.add_argument("--output", default=".plat/telemetry.json")
    parser.add_argument("--json", dest="json_payload")
    args = parser.parse_args()

    if args.json_payload:
        snapshot = normalize(
            _load_json_payload(args.json_payload),
            host=args.host,
            source="cli-json",
        )
    else:
        snapshot = discover(
            host=args.host,
            transcript=Path(args.transcript).expanduser() if args.transcript else None,
        )
    save(Path(args.output), snapshot)
    print(json.dumps(snapshot, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
