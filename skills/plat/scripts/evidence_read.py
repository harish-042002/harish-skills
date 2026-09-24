#!/usr/bin/env python3
"""Bounded file reads with consumed-evidence masking.

An unchanged read range is returned once. Subsequent reads return only a
pointer/digest unless --refresh is explicitly requested.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import context_guard

DEFAULT_MAX_RETURN_BYTES = 6 * 1024
INDEX_VERSION = 1


def load_index(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return {"schema_version": INDEX_VERSION, "entries": {}}


def save_index(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _slice_lines(path: Path, start: int | None, end: int | None) -> tuple[str, int, int]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    if not lines:
        return "", 1, 0
    first = max(1, start or 1)
    last = min(len(lines), end or len(lines))
    if last < first:
        return "", first, last
    return "\n".join(lines[first - 1:last]), first, last


def _cap(text: str, max_bytes: int) -> str:
    data = text.encode("utf-8")
    if len(data) <= max_bytes:
        return text
    suffix = b"\n...[read truncated]"
    keep = max(0, max_bytes - len(suffix))
    return data[:keep].decode("utf-8", errors="ignore").rstrip() + suffix.decode("utf-8")


def read_evidence(
    path: Path,
    *,
    start: int | None = None,
    end: int | None = None,
    max_return_bytes: int = DEFAULT_MAX_RETURN_BYTES,
    index_path: Path = Path(".plat/evidence-index.json"),
    context_state: Path = Path(".plat/context.json"),
    refresh: bool = False,
) -> dict:
    path = path.expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(path)
    if max_return_bytes < 1024:
        raise ValueError("max_return_bytes must be >= 1024")

    content, first, last = _slice_lines(path, start, end)
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    key = f"{path}#L{first}-L{last}"

    index = load_index(index_path)
    entries = index.setdefault("entries", {})
    previous = entries.get(key)
    masked = bool(
        not refresh
        and isinstance(previous, dict)
        and previous.get("sha256") == digest
    )

    if masked:
        result = {
            "path": str(path),
            "range": f"L{first}-L{last}",
            "sha256": digest,
            "masked": True,
            "pointer": key,
            "summary": "unchanged evidence already consumed; re-read only if a new question requires it",
        }
    else:
        meta = {
            "path": str(path),
            "range": f"L{first}-L{last}",
            "sha256": digest,
            "masked": False,
            "pointer": key,
        }
        overhead = len(json.dumps(meta, indent=2, sort_keys=True).encode("utf-8")) + 128
        visible = _cap(content, max(1024, max_return_bytes - overhead))
        result = {**meta, "content": visible}
        entries[key] = {
            "sha256": digest,
            "bytes": len(content.encode("utf-8")),
        }
        save_index(index_path, index)

    rendered = json.dumps(result, indent=2, sort_keys=True)
    if len(rendered.encode("utf-8")) > max_return_bytes:
        if "content" in result:
            result["content"] = _cap(result["content"], max(256, max_return_bytes // 2))
        rendered = json.dumps(result, indent=2, sort_keys=True)
    if len(rendered.encode("utf-8")) > max_return_bytes:
        raise RuntimeError("evidence read exceeds hard return limit")

    state = context_guard.load(context_state)
    state = context_guard.record(
        state,
        returned_bytes=len(rendered.encode("utf-8")),
        kind="read",
        key=key,
    )
    context_guard.save(context_state, state)
    result["context_health"] = state["health"]
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Read source evidence with masking for unchanged rereads.")
    parser.add_argument("path")
    parser.add_argument("--start", type=int)
    parser.add_argument("--end", type=int)
    parser.add_argument("--max-return-bytes", type=int, default=DEFAULT_MAX_RETURN_BYTES)
    parser.add_argument("--index", default=".plat/evidence-index.json")
    parser.add_argument("--context-state", default=".plat/context.json")
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()

    result = read_evidence(
        Path(args.path),
        start=args.start,
        end=args.end,
        max_return_bytes=args.max_return_bytes,
        index_path=Path(args.index),
        context_state=Path(args.context_state),
        refresh=args.refresh,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
