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
import math
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
    "reasoning_output_tokens": ("reasoning_output_tokens",),
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
    if isinstance(value, (int, float)) and math.isfinite(value) and value >= 0:
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

    details = obj.get("input_tokens_details", obj.get("prompt_tokens_details"))
    if isinstance(details, dict):
        cached = _number(details.get("cached_tokens"))
        if cached is not None:
            out["cache_read_tokens"] = max(
                out.get("cache_read_tokens", 0.0),
                cached,
            )
    details = obj.get("output_tokens_details", obj.get("completion_tokens_details"))
    if isinstance(details, dict):
        reasoning = _number(details.get("reasoning_tokens"))
        if reasoning is not None:
            out["reasoning_output_tokens"] = reasoning
    return out


def _usage_candidates(obj: Any) -> list[dict[str, Any]]:
    """Only documented envelopes, not arbitrary user text or tool payloads."""
    if not isinstance(obj, dict):
        return []
    found = [_extract_from_dict(obj)]
    for path in (("usage",), ("message", "usage"),
                 ("payload", "info", "total_token_usage")):
        cur = obj
        for key in path:
            cur = cur.get(key) if isinstance(cur, dict) else None
        if isinstance(cur, dict):
            found.append(_extract_from_dict(cur))
    return [x for x in found if x]


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


def _named_dict(obj: Any, name: str) -> dict | None:
    if not isinstance(obj, dict):
        return None
    paths = ((name,), ("message", name), ("payload", "info", name), ("info", name))
    for path in paths:
        cur = obj
        for key in path:
            cur = cur.get(key) if isinstance(cur, dict) else None
        if isinstance(cur, dict):
            return cur
    return None


def parse_jsonl(path: Path) -> dict[str, Any]:
    """Read one session. Known cumulative snapshots replace, never add to totals.

    Only explicit usage dictionaries are treated as per-message usage. Unknown
    log schemas stay unavailable instead of recursively counting arbitrary data.
    """
    counters = ("input_tokens", "output_tokens", "cache_read_tokens", "cache_write_tokens", "reasoning_output_tokens", "cost_usd")
    contexts = ("context_used_tokens", "context_limit_tokens")
    events: dict[str, dict] = {}
    cumulative: dict | None = None
    current: dict = {}
    cumulative_records = 0
    reported_cost = None
    with path.open(encoding="utf-8", errors="replace") as fh:
        for line_no, line in enumerate(fh, 1):
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(obj, dict):
                continue
            total = _named_dict(obj, "total_token_usage")
            usage = total if total is not None else _named_dict(obj, "usage")
            if usage is None:
                # Canonical rows must explicitly identify their counter semantics.
                if obj.get("usage_kind") not in {"cumulative", "per_request"}:
                    continue
                usage = obj
            event = _extract_from_dict(usage)
            # Claude terminal result usage is aggregate; its cost is outside usage.
            if obj.get("type") == "result":
                cost = _number(obj.get("total_cost_usd"))
                if cost is not None:
                    reported_cost = cost
            if not event:
                continue
            for key in contexts:
                value = event.get(key, _number(obj.get(key)))
                if value is not None:
                    current[key] = value
            if total is not None or obj.get("usage_kind") == "cumulative" or obj.get("type") == "result":
                cumulative = {key: value for key, value in event.items() if key in counters}
                cumulative_records += 1
            else:
                # A later record of the same message may contain final usage.
                identity = _dedupe_id(obj, line_no)
                events[identity] = {**events.get(identity, {}), **event}
    if cumulative is not None:
        totals = cumulative
        kind = "latest_cumulative_snapshot"
        records = cumulative_records
    else:
        totals = {}
        for event in events.values():
            for key in counters:
                if key in event:
                    totals[key] = totals.get(key, 0) + event[key]
        kind = "unique_message_totals"
        records = len(events)
    if reported_cost is not None:
        totals["cost_usd"] = reported_cost
    return {**totals, **current, "records": records, "counter_semantics": kind,
            "observed_at": dt.datetime.fromtimestamp(path.stat().st_mtime, dt.timezone.utc).isoformat()}


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
        "available": bool(merged) and payload.get("available") is not False,
        "host": host if host and host != "unknown" else str(payload.get("host", "unknown")),
        "source": source,
        "observed_at": payload.get("observed_at") or now_iso(),
        "capabilities": {
            key: value is True
            for key, value in capabilities.items()
            if key in {
                "isolated_context",
                "precompact_hook",
                "usage_telemetry",
            }
        },
    }
    if payload.get("counter_semantics"):
        snapshot["counter_semantics"] = payload["counter_semantics"]
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

    canonical = CANONICAL_FILE
    if canonical.exists():
        payload = _load_json_payload(canonical.read_text(encoding="utf-8"))
        snap = normalize(payload, host=host, source=str(canonical))
        snap["upstream_source"] = payload.get("source")
        # A cache is a historical record, not fresh host occupancy. Keep usage for
        # reporting, but require fresh input before taking a context-reset action.
        snap.pop("context_utilization", None)
        snap["occupancy_fresh"] = False
        return snap

    capabilities = {}
    env_caps = os.environ.get(CAPABILITIES_ENV)
    if env_caps:
        parsed_caps = json.loads(env_caps)
        if isinstance(parsed_caps, dict):
            capabilities = {
                key: value is True
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
