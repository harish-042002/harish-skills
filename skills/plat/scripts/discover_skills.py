#!/usr/bin/env python3
"""Discover installed coding-agent skills without loading their full bodies."""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Iterable

try:
    import yaml as _yaml  # type: ignore
except Exception:
    _yaml = None

TOKEN_RE = re.compile(r"[a-z0-9]+(?:[-_][a-z0-9]+)*", re.I)
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FRONTMATTER_RE = re.compile(r"^---\\s*\\n(.*?)\\n---(?:\\s*\\n|$)", re.S)
MAX_HEADER_BYTES = 64 * 1024
MAX_DESCRIPTION = 1024
ALLOWED_FIELDS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}

BROAD_MARKERS = {
    "orchestrator",
    "orchestration",
    "general-purpose",
    "generalist",
    "all-purpose",
    "workflow",
    "control-plane",
}

ALIASES = {
    "debug": {"debug", "bug", "root", "cause", "failure"},
    "testing": {"test", "testing", "pytest", "jest", "playwright", "e2e", "mutation", "property"},
    "backend": {"backend", "server", "service", "api", "worker", "queue", "microservice"},
    "frontend": {"frontend", "react", "vue", "angular", "browser", "ui"},
    "mobile": {"mobile", "flutter", "ios", "android"},
    "database": {"database", "sql", "postgres", "mysql", "query", "index", "migration"},
    "security": {"security", "auth", "authorization", "authentication", "threat", "vulnerability"},
    "performance": {"performance", "profiling", "latency", "throughput", "capacity", "optimization"},
    "ai": {"ai", "llm", "rag", "agent", "retrieval", "embedding", "prompt", "eval"},
    "delivery": {"delivery", "deploy", "deployment", "cicd", "ci", "cd", "terraform", "kubernetes", "docker"},
    "design": {"design", "ux", "ui", "accessibility", "motion", "visual"},
}

def tokens(text: str) -> set[str]:
    out = {t.lower().replace("_", "-") for t in TOKEN_RE.findall(text or "")}
    expanded = set(out)
    for token in list(out):
        expanded.update(part for part in token.split("-") if part)
    for key, vals in ALIASES.items():
        if key in out or out & vals:
            expanded.add(key)
            expanded.update(vals)
    return expanded

def project_root(start: Path) -> Path:
    cur = start.resolve()
    for p in [cur, *cur.parents]:
        if (p / ".git").exists():
            return p
    return cur

def candidate_roots(cwd: Path) -> list[tuple[str, Path]]:
    home = Path.home()
    root = project_root(cwd)
    roots = [
        ("project", root / ".agents" / "skills"),
        ("project", root / ".claude" / "skills"),
        ("project", root / ".cursor" / "skills"),
        ("project", root / ".codex" / "skills"),
        ("global", Path(os.environ.get("CLAUDE_CONFIG_DIR", home / ".claude")) / "skills"),
        ("global", Path(os.environ.get("CODEX_HOME", home / ".codex")) / "skills"),
        ("global", home / ".cursor" / "skills"),
        ("global", home / ".agents" / "skills"),
    ]
    seen: set[Path] = set()
    result: list[tuple[str, Path]] = []
    for scope, path in roots:
        try:
            key = path.expanduser().resolve()
        except FileNotFoundError:
            key = path.expanduser()
        if key in seen:
            continue
        seen.add(key)
        result.append((scope, path.expanduser()))
    return result

def iter_skill_files(root: Path, max_depth: int = 3) -> Iterable[Path]:
    if not root.is_dir():
        return
    base_depth = len(root.parts)
    for path in root.rglob("SKILL.md"):
        if len(path.parts) - base_depth <= max_depth + 1:
            yield path

def _read_frontmatter_text(path: Path) -> str | None:
    try:
        with path.open("r", encoding="utf-8", errors="strict") as handle:
            text = handle.read(MAX_HEADER_BYTES)
    except (OSError, UnicodeError):
        return None
    match = FRONTMATTER_RE.match(text)
    return match.group(1) if match else None


def _quoted_closed(value: str, quote: str) -> bool:
    if len(value) < 2 or not value.startswith(quote):
        return False
    if quote == "'":
        inner = value[1:]
        return inner.endswith("'") and not inner.endswith("'''")
    escaped = False
    for idx, ch in enumerate(value[1:], start=1):
        if ch == "\\" and not escaped:
            escaped = True
            continue
        if ch == '"' and not escaped and idx == len(value) - 1:
            return True
        escaped = False
    return False


def _parse_scalar(raw: str) -> object:
    raw = raw.strip()
    if not raw:
        return ""
    if raw.startswith('"') and raw.endswith('"'):
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return raw[1:-1]
    if raw.startswith("'") and raw.endswith("'"):
        return raw[1:-1].replace("''", "'")
    lowered = raw.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if lowered in {"null", "~"}:
        return None
    return raw.split(" #", 1)[0].rstrip()


def _fallback_yaml(frontmatter: str) -> dict[str, object]:
    lines = frontmatter.splitlines()
    data: dict[str, object] = {}
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#") or line[:1].isspace() or ":" not in line:
            i += 1
            continue
        key, raw = line.split(":", 1)
        key, raw = key.strip(), raw.strip()

        if raw in {">", ">-", ">+", "|", "|-", "|+"}:
            block: list[str] = []
            i += 1
            while i < len(lines) and (not lines[i].strip() or lines[i][:1].isspace()):
                block.append(lines[i].strip())
                i += 1
            data[key] = (" ".join(x for x in block if x).strip()
                         if raw.startswith(">") else "\n".join(block).strip("\n"))
            continue

        if raw.startswith('"') and not _quoted_closed(raw, '"'):
            parts = [raw]
            i += 1
            while i < len(lines):
                parts.append(lines[i].strip())
                if _quoted_closed(" ".join(parts), '"'):
                    i += 1
                    break
                i += 1
            raw = " ".join(parts)
        elif raw.startswith("'") and not _quoted_closed(raw, "'"):
            parts = [raw]
            i += 1
            while i < len(lines):
                parts.append(lines[i].strip())
                if _quoted_closed(" ".join(parts), "'"):
                    i += 1
                    break
                i += 1
            raw = " ".join(parts)
        else:
            i += 1
        data[key] = _parse_scalar(raw)
    return data


def parse_frontmatter(path: Path) -> dict[str, object]:
    frontmatter = _read_frontmatter_text(path)
    if frontmatter is None:
        return {}
    if _yaml is not None:
        try:
            value = _yaml.safe_load(frontmatter)
            return value if isinstance(value, dict) else {}
        except Exception:
            return {}
    return _fallback_yaml(frontmatter)


def validate_skill_metadata(path: Path, meta: dict[str, object]) -> tuple[bool, str]:
    try:
        if path.is_symlink():
            return False, "skill-file-symlink"
        resolved_file = path.resolve(strict=True)
        resolved_parent = path.parent.resolve(strict=True)
    except OSError:
        return False, "unresolvable-path"
    if resolved_file.parent != resolved_parent:
        return False, "path-escape"

    if set(meta) - ALLOWED_FIELDS:
        return False, "unexpected-frontmatter-field"
    name = meta.get("name")
    description = meta.get("description")
    if not isinstance(name, str) or not isinstance(description, str):
        return False, "missing-name-or-description"
    name, description = name.strip(), description.strip()
    if not (1 <= len(name) <= 64) or not NAME_RE.fullmatch(name) or "--" in name:
        return False, "invalid-name"
    if name != path.parent.name:
        return False, "name-directory-mismatch"
    if not (1 <= len(description) <= MAX_DESCRIPTION):
        return False, "invalid-description-length"
    compatibility = meta.get("compatibility")
    if compatibility is not None and (not isinstance(compatibility, str) or not (1 <= len(compatibility) <= 500)):
        return False, "invalid-compatibility"
    metadata = meta.get("metadata")
    if metadata is not None and (not isinstance(metadata, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in metadata.items())):
        return False, "invalid-metadata-map"
    return True, "valid"


def base_tokens(text: str) -> set[str]:
    out = {t.lower().replace("_", "-") for t in TOKEN_RE.findall(text or "")}
    expanded = set(out)
    for token in list(out):
        expanded.update(part for part in token.split("-") if part)
    return expanded


def score_details(query: str, name: str, description: str) -> tuple[int, list[str], bool]:
    if not query:
        return 0, [], False

    q_base = base_tokens(query)
    n_base = base_tokens(name)
    d_base = base_tokens(description)
    q = tokens(query)
    n = tokens(name)
    d = tokens(description)

    direct_name = q_base & n_base
    direct_desc = q_base & d_base
    semantic_overlap = q & (n | d)
    phrase = query.lower().strip()
    haystack = f"{name} {description}".lower()

    value = len(direct_name) * 8 + len(direct_desc) * 4
    value += len(semantic_overlap - direct_name - direct_desc)
    if phrase and phrase in haystack:
        value += 10

    broad = bool((n_base | d_base) & BROAD_MARKERS)
    # Broad orchestrators are fallback consultants, not preferred specialists.
    # Keyword stuffing must not let a generalist beat a focused specialist.
    if broad:
        value = int(value * 0.35)

    matched = sorted(q_base & (n_base | d_base))
    if not matched:
        matched = sorted(q & (n | d))
    return value, matched, broad


def score(query: str, name: str, description: str) -> int:
    return score_details(query, name, description)[0]

def main() -> int:
    p = argparse.ArgumentParser(description="Discover installed specialist skills.")
    p.add_argument("--query", default="", help="Capability/problem to match.")
    p.add_argument("--limit", type=int, default=5)
    p.add_argument("--cwd", default=os.getcwd())
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    by_name: dict[str, dict] = {}
    rejected = 0
    for scope, root in candidate_roots(Path(args.cwd)):
        for skill_file in iter_skill_files(root) or []:
            meta = parse_frontmatter(skill_file)
            valid, _reason = validate_skill_metadata(skill_file, meta)
            if not valid:
                rejected += 1
                continue
            name = str(meta["name"]).strip()
            if name.lower() == "plat":
                continue
            description = str(meta["description"]).strip()
            item_score, matched_terms, broad = score_details(args.query, name, description)
            license_value = meta.get("license")
            item = {
                "name": name,
                "path": str(skill_file),
                "scope": scope,
                "score": item_score,
                "matched_terms": matched_terms,
                "broad": broad,
                "spec_valid": True,
                "license": license_value if isinstance(license_value, str) else None,
            }
            existing = by_name.get(name.lower())
            if existing is None or (existing["scope"] == "global" and scope == "project"):
                by_name[name.lower()] = item

    items = list(by_name.values())
    if args.query:
        items = [x for x in items if x["score"] > 0]
    items.sort(key=lambda x: (-x["score"], 1 if x["broad"] else 0, 0 if x["scope"] == "project" else 1, x["name"].lower()))
    items = items[: max(args.limit, 0)]

    if args.json:
        print(json.dumps({"query": args.query, "skills": items, "rejected_invalid": rejected}, indent=2))
    else:
        if not items:
            print("No matching validated installed specialist skills found.")
            return 0
        for item in items:
            marker = "\tbroad" if item.get("broad") else ""
            matched = ",".join(item.get("matched_terms", []))
            print(f"{item['name']}\t{item['scope']}\tscore={item['score']}\tmatch={matched}{marker}\t{item['path']}")
            if item["description"]:
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
