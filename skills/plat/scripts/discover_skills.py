#!/usr/bin/env python3
"""Discover installed coding-agent skills without loading their full bodies."""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Iterable

TOKEN_RE = re.compile(r"[a-z0-9]+(?:[-_][a-z0-9]+)*", re.I)

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

def parse_frontmatter(path: Path) -> dict[str, str]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.S)
    if not m:
        return {}
    data: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" not in line or line[:1].isspace():
            continue
        key, value = line.split(":", 1)
        value = value.strip().strip('"').strip("'")
        data[key.strip()] = value
    return data

def score(query: str, name: str, description: str) -> int:
    if not query:
        return 0
    q = tokens(query)
    n = tokens(name)
    d = tokens(description)
    phrase = query.lower().strip()
    haystack = f"{name} {description}".lower()
    value = len(q & n) * 5 + len(q & d) * 2
    if phrase and phrase in haystack:
        value += 8
    return value

def main() -> int:
    p = argparse.ArgumentParser(description="Discover installed specialist skills.")
    p.add_argument("--query", default="", help="Capability/problem to match.")
    p.add_argument("--limit", type=int, default=5)
    p.add_argument("--cwd", default=os.getcwd())
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    by_name: dict[str, dict] = {}
    for scope, root in candidate_roots(Path(args.cwd)):
        for skill_file in iter_skill_files(root) or []:
            meta = parse_frontmatter(skill_file)
            name = meta.get("name") or skill_file.parent.name
            if name.lower() == "plat":
                continue
            description = meta.get("description", "")
            item = {
                "name": name,
                "description": description,
                "path": str(skill_file),
                "scope": scope,
                "score": score(args.query, name, description),
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
        print(json.dumps({"query": args.query, "skills": items}, indent=2))
    else:
        if not items:
            print("No matching installed specialist skills found.")
            return 0
        for item in items:
            print(f"{item['name']}\t{item['scope']}\tscore={item['score']}\t{item['path']}")
            if item["description"]:
                print(f"  {item['description']}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
