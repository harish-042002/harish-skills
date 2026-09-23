#!/usr/bin/env python3
"""Discover installed specialist skills without trusting or loading their bodies."""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Iterable

TOKEN_RE = re.compile(r"[a-z0-9]+(?:[-_][a-z0-9]+)*", re.I)
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MAX_FRONTMATTER_BYTES = 32 * 1024
ALLOWED_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}

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


def base_tokens(text: str) -> set[str]:
    out = {t.lower().replace("_", "-") for t in TOKEN_RE.findall(text or "")}
    expanded = set(out)
    for token in list(out):
        expanded.update(part for part in token.split("-") if part)
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
        expanded = path.expanduser()
        try:
            key = expanded.resolve()
        except OSError:
            key = expanded.absolute()
        if key in seen:
            continue
        seen.add(key)
        result.append((scope, expanded))
    return result


def iter_skill_files(root: Path, max_depth: int = 3) -> Iterable[Path]:
    """Walk without following symlink directories and yield bounded SKILL.md paths."""
    if not root.is_dir():
        return
    for current, dirs, files in os.walk(root, followlinks=False):
        cur = Path(current)
        try:
            depth = len(cur.relative_to(root).parts)
        except ValueError:
            continue
        if depth >= max_depth:
            dirs[:] = []
        else:
            dirs[:] = [d for d in dirs if not (cur / d).is_symlink()]
        if "SKILL.md" in files:
            yield cur / "SKILL.md"


def safe_skill_file(root: Path, path: Path) -> bool:
    """Reject symlink/path escapes before reading untrusted skill metadata."""
    try:
        rel = path.relative_to(root)
    except ValueError:
        return False

    cur = root
    for part in rel.parts:
        cur = cur / part
        if cur.is_symlink():
            return False

    try:
        root_real = root.resolve(strict=True)
        path_real = path.resolve(strict=True)
        path_real.relative_to(root_real)
    except (OSError, ValueError):
        return False
    return path_real.is_file() and path_real.name == "SKILL.md"


def read_frontmatter(path: Path) -> str | None:
    try:
        with path.open("rb") as fh:
            raw = fh.read(MAX_FRONTMATTER_BYTES + 1)
    except OSError:
        return None
    if len(raw) > MAX_FRONTMATTER_BYTES:
        return None
    text = raw.decode("utf-8", errors="replace").replace("\r\n", "\n")
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end < 0:
        return None
    return text[4:end]


def _plain_scalar(value: str) -> str:
    value = value.strip()
    if " #" in value:
        value = value.split(" #", 1)[0].rstrip()
    return value


def _quoted_scalar(lines: list[str], i: int, value: str) -> tuple[str | None, int]:
    quote = value[0]
    parts = [value]
    while len(" ".join(parts)) < MAX_FRONTMATTER_BYTES:
        joined = " ".join(x.strip() for x in parts)
        if len(joined) >= 2 and joined.rstrip().endswith(quote):
            inner = joined[1:-1]
            if quote == "'":
                return inner.replace("''", "'"), i + 1
            try:
                return json.loads(joined), i + 1
            except json.JSONDecodeError:
                return inner.replace(r'\"', '"').replace(r"\\", "\\"), i + 1
        i += 1
        if i >= len(lines):
            return None, i
        parts.append(lines[i])
    return None, i


def parse_frontmatter_text(text: str) -> tuple[dict[str, str], str | None]:
    lines = text.splitlines()
    data: dict[str, str] = {}
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue
        if line[:1].isspace():
            # Nested metadata belongs to the previous top-level mapping; discovery ignores it.
            i += 1
            continue
        if ":" not in line:
            return {}, "invalid top-level YAML line"
        key, raw_value = line.split(":", 1)
        key = key.strip()
        value = raw_value.strip()
        if key not in ALLOWED_KEYS:
            return {}, f"unsupported frontmatter key: {key}"
        if key == "metadata":
            data[key] = value or "{}"
            i += 1
            while i < len(lines) and (not lines[i].strip() or lines[i][:1].isspace()):
                i += 1
            continue

        if re.fullmatch(r"[>|][+-]?", value):
            style = value[0]
            chunks: list[str] = []
            i += 1
            while i < len(lines) and (not lines[i].strip() or lines[i][:1].isspace()):
                chunks.append(lines[i].strip())
                i += 1
            if style == ">":
                data[key] = " ".join(x for x in chunks if x).strip()
            else:
                data[key] = "\n".join(chunks).strip()
            continue

        if value.startswith(("'", '"')):
            parsed, next_i = _quoted_scalar(lines, i, value)
            if parsed is None:
                return {}, f"unterminated quoted scalar: {key}"
            data[key] = parsed
            i = next_i
            continue

        data[key] = _plain_scalar(value)
        i += 1
    return data, None


def validate_metadata(meta: dict[str, str], parent_name: str) -> str | None:
    name = meta.get("name", "").strip()
    description = meta.get("description", "").strip()
    if not name or not description:
        return "name and description are required"
    if len(name) > 64 or not NAME_RE.fullmatch(name) or "--" in name:
        return "invalid Agent Skills name"
    if name != parent_name:
        return "name must match parent directory"
    if len(description) > 1024:
        return "description exceeds 1024 characters"
    compatibility = meta.get("compatibility", "").strip()
    if compatibility and len(compatibility) > 500:
        return "compatibility exceeds 500 characters"
    return None


def load_metadata(root: Path, path: Path) -> tuple[dict[str, str] | None, str | None]:
    if not safe_skill_file(root, path):
        return None, "unsafe path or symlink"
    frontmatter = read_frontmatter(path)
    if frontmatter is None:
        return None, "missing or oversized frontmatter"
    meta, error = parse_frontmatter_text(frontmatter)
    if error:
        return None, error
    error = validate_metadata(meta, path.parent.name)
    if error:
        return None, error
    return meta, None


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
    name_text = name.lower()
    desc_text = description.lower()

    value = len(direct_name) * 14 + len(direct_desc) * 3
    value += len(semantic_overlap - direct_name - direct_desc)
    if q_base and q_base <= n_base:
        value += 12
    if phrase and phrase in name_text:
        value += 16
    elif phrase and phrase in desc_text:
        value += 4

    broad = bool((n_base | d_base) & BROAD_MARKERS)
    if broad:
        value = max(0, value - 36)

    candidate_terms = n_base | d_base
    if candidate_terms:
        specificity = len(q_base & candidate_terms) / len(candidate_terms)
        value += round(12 * specificity)
    if len(d_base) > 80:
        value = max(0, value - min(8, (len(d_base) - 80) // 20 + 1))

    matched = sorted(q_base & candidate_terms)
    if not matched:
        matched = sorted(q & (n | d))
    return value, matched, broad


def score(query: str, name: str, description: str) -> int:
    return score_details(query, name, description)[0]


def main() -> int:
    p = argparse.ArgumentParser(description="Discover installed specialist skills safely.")
    p.add_argument("--query", default="", help="Capability/problem to match.")
    p.add_argument("--limit", type=int, default=5)
    p.add_argument("--cwd", default=os.getcwd())
    p.add_argument("--json", action="store_true")
    p.add_argument("--diagnostics", action="store_true", help="Include rejected package paths/reasons.")
    args = p.parse_args()

    by_name: dict[str, dict] = {}
    rejected: list[dict[str, str]] = []
    for scope, root in candidate_roots(Path(args.cwd)):
        for skill_file in iter_skill_files(root) or []:
            meta, error = load_metadata(root, skill_file)
            if error:
                if args.diagnostics:
                    rejected.append({"path": str(skill_file), "reason": error})
                continue
            assert meta is not None
            name = meta["name"]
            if name.lower() == "plat":
                continue
            description = meta["description"]
            item_score, matched_terms, broad = score_details(args.query, name, description)
            item = {
                "name": name,
                "path": str(skill_file),
                "scope": scope,
                "score": item_score,
                "matched_terms": matched_terms,
                "broad": broad,
                "trust": "untrusted-installed-skill",
                "declared_license": meta.get("license") or None,
                "compatibility_declared": bool(meta.get("compatibility")),
            }
            existing = by_name.get(name.lower())
            if existing is None or (existing["scope"] == "global" and scope == "project"):
                by_name[name.lower()] = item

    items = list(by_name.values())
    if args.query:
        items = [x for x in items if x["score"] > 0]
    items.sort(key=lambda x: (-x["score"], 0 if x["scope"] == "project" else 1, x["name"].lower()))
    items = items[: max(args.limit, 0)]

    if args.json:
        payload: dict[str, object] = {"query": args.query, "skills": items}
        if args.diagnostics:
            payload["rejected"] = rejected
        print(json.dumps(payload, indent=2))
    else:
        if not items:
            print("No matching installed specialist skills found.")
            return 0
        for item in items:
            marker = "\tbroad" if item.get("broad") else ""
            matched = ",".join(item.get("matched_terms", []))
            license_text = item.get("declared_license") or "unspecified"
            print(f"{item['name']}\t{item['scope']}\tscore={item['score']}\tmatch={matched}{marker}\tlicense={license_text}\t{item['path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
