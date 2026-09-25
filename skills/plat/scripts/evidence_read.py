#!/usr/bin/env python3
"""Bounded file reads with consumed-evidence masking.

Mask only a fully delivered range in the same confirmed context epoch.
Truncated ranges remain readable; character offsets provide lossless continuation.
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
INDEX_VERSION = 2


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


READ_CHUNK_CHARS = 64 * 1024


def _window(path: Path, start: int, end: int | None, offset: int, limit: int):
    """Stream bounded chunks, including a single very long line.

    Preserve exact decoded LF/CRLF text, including the final newline. Range
    hashes are recomputed for correctness, but no whole-file string or
    unbounded readline is allocated. Line numbers use LF delimiters.
    """
    before = path.stat()
    signature = lambda st: (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns)
    digest = hashlib.sha256()
    selected = []
    total = 0
    line = 1
    last = start - 1
    with path.open(encoding="utf-8", errors="replace", newline="") as fh:
        while True:
            chunk = fh.read(READ_CHUNK_CHARS)
            if not chunk:
                break
            # Skip entire blocks preceding the requested starting line.
            if line < start:
                count = chunk.count("\n")
                if line + count < start:
                    line += count
                    continue
                at = 0
                while line < start:
                    at = chunk.index("\n", at) + 1
                    line += 1
                chunk = chunk[at:]
            stop = False
            if end is not None:
                if line > end:
                    break
                count = chunk.count("\n")
                if line + count > end:
                    at = 0
                    for _ in range(end - line + 1):
                        at = chunk.index("\n", at) + 1
                    chunk = chunk[:at]
                    stop = True
            if chunk:
                digest.update(chunk.encode("utf-8"))
                lo = max(0, offset - total)
                hi = min(len(chunk), offset + limit - total)
                if hi > lo:
                    selected.append(chunk[lo:hi])
                total += len(chunk)
                line += chunk.count("\n")
                last = line - 1 if chunk.endswith("\n") else line
            if stop:
                break
    if signature(path.stat()) != signature(before):
        raise ValueError("source changed during read; restart this read")
    return "".join(selected), start, last, total, digest.hexdigest()


def read_evidence(
    path: Path,
    *,
    start: int | None = None,
    end: int | None = None,
    max_return_bytes: int = DEFAULT_MAX_RETURN_BYTES,
    index_path: Path = Path(".plat/evidence-index.json"),
    context_state: Path = Path(".plat/context.json"),
    refresh: bool = False,
    offset: int = 0,
    expected_sha256: str | None = None,
) -> dict:
    path = path.expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(path)
    if max_return_bytes < 1024:
        raise ValueError("max_return_bytes must be >= 1024")
    first = 1 if start is None else start
    if first < 1 or (end is not None and end < first) or offset < 0:
        raise ValueError("invalid line range or character offset")
    content, first, last, total, digest = _window(path, first, end, offset, max_return_bytes)
    if expected_sha256 and expected_sha256 != digest:
        raise ValueError("source changed during pagination; restart this read")
    if offset > total:
        raise ValueError("offset is beyond the requested range")
    key = f"{path}#L{first}-L{last}"
    state = context_guard.load(context_state)
    # Legacy state has no usable consumption epoch; establish one, never reuse old masks.
    if not state.get("context_epoch"):
        state = context_guard.reset_context(state)
    epoch = state["context_epoch"]
    index = load_index(index_path)
    entries = index.setdefault("entries", {})
    previous = entries.get(key)
    masked = bool(not refresh and offset == 0 and isinstance(previous, dict)
                  and previous.get("sha256") == digest
                  and previous.get("context_epoch") == epoch
                  and previous.get("fully_delivered") is True)
    result = {
        "path": str(path), "range": f"L{first}-L{last}", "sha256": digest,
        "masked": masked, "pointer": key, "context_health": "YELLOW",
    }
    if masked:
        result["summary"] = "unchanged range delivered fully in this context; --refresh rereads it"
    else:
        result.update(content="", offset=offset, truncated=False, next_offset=None)
        # Fit the serialized JSON, not raw text: escapes and Unicode can expand it.
        def candidate(n):
            result["content"] = content[:n]
            result["truncated"] = offset + n < total
            result["next_offset"] = offset + n if result["truncated"] else None
            return len(json.dumps(result, indent=2, sort_keys=True).encode("utf-8"))
        low, high = 0, len(content)
        if candidate(0) > max_return_bytes:
            raise ValueError("metadata exceeds return budget; shorten the path or raise the limit")
        while low < high:
            mid = (low + high + 1) // 2
            if candidate(mid) <= max_return_bytes:
                low = mid
            else:
                high = mid - 1
        candidate(low)
        if result["truncated"] and low == 0:
            raise ValueError("return budget leaves no room for content")
        # A partial page is not evidence that the whole range was consumed.
        if offset == 0 and not result["truncated"]:
            entries[key] = {"sha256": digest, "context_epoch": epoch, "fully_delivered": True}
            save_index(index_path, index)
    rendered = json.dumps(result, indent=2, sort_keys=True)
    state = context_guard.record(state, returned_bytes=len(rendered.encode("utf-8")), kind="read", key=key)
    context_guard.save(context_state, state)
    result["context_health"] = state["health"]["status"]
    if len(json.dumps(result, indent=2, sort_keys=True).encode("utf-8")) > max_return_bytes:
        raise RuntimeError("evidence read exceeds hard return limit")
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
    parser.add_argument("--offset", type=int, default=0, help="Character offset within the requested range")
    parser.add_argument("--expected-sha256", help="Reject continuation if the source has changed")
    args = parser.parse_args()

    result = read_evidence(
        Path(args.path),
        start=args.start,
        end=args.end,
        max_return_bytes=args.max_return_bytes,
        index_path=Path(args.index),
        context_state=Path(args.context_state),
        refresh=args.refresh,
        offset=args.offset,
        expected_sha256=args.expected_sha256,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
