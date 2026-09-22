#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "plat" / "SKILL.md"
ROUTING = ROOT / "skills" / "plat" / "references" / "routing.md"
VERSION = ROOT / "VERSION"
SKILL_VERSION = ROOT / "skills" / "plat" / "VERSION"
CASES = ROOT / "tests" / "routing-cases.json"

errors: list[str] = []

def require(cond: bool, msg: str) -> None:
    if not cond:
        errors.append(msg)

skill = SKILL.read_text(encoding="utf-8")
routing = ROUTING.read_text(encoding="utf-8")

# Hot-path budget: keep the always-loaded router lean.
require(len(skill) <= 7000, f"SKILL.md hot path too large: {len(skill)} chars > 7000")
require(len(skill.splitlines()) <= 190, f"SKILL.md too many lines: {len(skill.splitlines())} > 190")

# Frontmatter must remain only name + description.
m = re.match(r"^---\n(.*?)\n---", skill, re.S)
require(bool(m), "SKILL.md missing valid frontmatter")
if m:
    keys = []
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith((" ", "\t")):
            keys.append(line.split(":", 1)[0].strip())
    require(keys == ["name", "description"], f"frontmatter keys must be name,description only; got {keys}")

# Critical routing controls.
for phrase in [
    "latest developer request/correction",
    "minimum sufficient depth",
    "Stop discovery once ownership",
    "detailed/deep answer changes output detail, not engineering depth",
    "Local, Behavioral, or Structural",
    "fresh evidence after the final relevant edit",
]:
    require(phrase in skill, f"missing critical root rule: {phrase}")

for heading in [
    "## Active-intent evidence",
    "## Vague-message resolution",
    "## Confidence gate",
    "## Fast path",
    "## Correction severity",
    "## Dependency invalidation",
    "## Re-route protocol",
    "## Repository inspection budget",
    "## Specialist budget",
    "## Ambiguous debugging",
    "## Stop conditions",
]:
    require(heading in routing, f"routing.md missing section: {heading}")

# All referenced Plat markdown files must exist.
for ref in re.findall(r"`(?:references/)?([a-z0-9-]+\.md)`", skill):
    p = ROOT / "skills" / "plat" / "references" / ref
    require(p.exists(), f"missing referenced file: {p.relative_to(ROOT)}")

require(VERSION.read_text().strip() == SKILL_VERSION.read_text().strip(), "root VERSION and skill VERSION differ")

data = json.loads(CASES.read_text(encoding="utf-8"))
items = data.get("cases", [])
require(len(items) >= 20, f"routing corpus too small: {len(items)} < 20")
ids = [x.get("id") for x in items]
require(len(ids) == len(set(ids)), "routing case ids are not unique")
valid_depth = {"Quick","Standard","Deep","Research"}
valid_correction = {"None","Local","Behavioral","Structural"}
for case in items:
    exp = case.get("expect", {})
    require(exp.get("depth") in valid_depth, f"{case.get('id')}: invalid depth")
    require(exp.get("correction") in valid_correction, f"{case.get('id')}: invalid correction")
    require(isinstance(exp.get("clarify"), bool), f"{case.get('id')}: clarify must be bool")

if errors:
    print("PLAT VALIDATION FAILED")
    for e in errors:
        print(f"- {e}")
    sys.exit(1)

print("PLAT VALIDATION PASSED")
print(f"- hot path: {len(skill)} chars / {len(skill.splitlines())} lines")
print(f"- routing corpus: {len(items)} cases")
print(f"- version: {VERSION.read_text().strip()}")
