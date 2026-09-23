#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "plat" / "SKILL.md"
ROUTING = ROOT / "skills" / "plat" / "references" / "routing.md"
ORCHESTRATION = ROOT / "skills" / "plat" / "references" / "orchestration.md"
DISCOVER_SKILLS = ROOT / "skills" / "plat" / "scripts" / "discover_skills.py"
VERSION = ROOT / "VERSION"
SKILL_VERSION = ROOT / "skills" / "plat" / "VERSION"
CASES = ROOT / "tests" / "routing-cases.json"
UPDATE_CHECK = ROOT / "skills" / "plat" / "scripts" / "update_check.py"
ORCHESTRATION_POLICY = ROOT / "skills" / "plat" / "scripts" / "orchestration_policy.py"
ORCHESTRATION_CASES = ROOT / "tests" / "orchestration-cases.json"
MAINTENANCE_GATE = ROOT / "scripts" / "maintenance_gate.py"
MAINTENANCE_EVIDENCE = ROOT / "docs" / "maintenance-evidence.json"
MAINTENANCE_DOC = ROOT / "docs" / "MAINTENANCE.md"
RESEARCH_LOG = ROOT / "docs" / "RESEARCH_LOG.md"
AWS_DEEP = ROOT / "skills" / "plat" / "references" / "aws-deep.md"
BEHAVIORAL_DIR = ROOT / "benchmarks" / "behavioral-v1.8"
BEHAVIORAL_CASES = BEHAVIORAL_DIR / "cases.json"
BEHAVIORAL_TRIGGERS = BEHAVIORAL_DIR / "trigger-cases.json"
BEHAVIORAL_RUNNER = BEHAVIORAL_DIR / "run_behavioral_eval.py"
BEHAVIORAL_SCORER = BEHAVIORAL_DIR / "score_results.py"

errors: list[str] = []

def require(cond: bool, msg: str) -> None:
    if not cond:
        errors.append(msg)

skill = SKILL.read_text(encoding="utf-8")
routing = ROUTING.read_text(encoding="utf-8")
orchestration = ORCHESTRATION.read_text(encoding="utf-8") if ORCHESTRATION.exists() else ""

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
    "hard scope constraints",
    "purges task-local work",
]:
    require(phrase in skill, f"missing critical root rule: {phrase}")

for heading in [
    "## Active-intent evidence",
    "## Vague-message resolution",
    "## Confidence gate",
    "## Fast path",
    "## Scope lock",
    "## Diff-expansion circuit breaker",
    "## Correction severity",
    "## Correction purge",
    "## Dependency invalidation",
    "## Re-route protocol",
    "## Repository inspection budget",
    "## Specialist budget",
    "## Ambiguous debugging",
    "## Stop conditions",
]:
    require(heading in routing, f"routing.md missing section: {heading}")


require(ORCHESTRATION.exists(), "specialist orchestration reference is missing")
require(DISCOVER_SKILLS.exists(), "installed-skill discovery broker is missing")
if DISCOVER_SKILLS.exists():
    discovery_text = DISCOVER_SKILLS.read_text(encoding="utf-8")
    for phrase in [
        "skill-file-symlink",
        "name-directory-mismatch",
        "invalid-description-length",
        "spec_valid",
        "rejected_invalid",
    ]:
        require(phrase in discovery_text, f"skill discovery missing trust/conformance control: {phrase}")
for heading in [
    "## Control topology",
    "## Orchestration gate",
    "## Specialist tiers",
    "## Manager vs handoff",
    "## External-skill discovery",
    "## Dispatch contract",
    "## Result contract",
    "## Evidence arbitration",
    "## Integration and output fidelity",
    "## Parallel vs sequential scheduling",
    "## Mutation ownership",
    "## Cost/token/time discipline",
    "## Circuit breakers",
    "## Stop conditions",
]:
    require(heading in orchestration, f"orchestration.md missing section: {heading}")

for phrase in [
    "External skills are bounded consultants",
    "Quick/ordinary Standard tasks should normally use **zero external skills**",
]:
    require(phrase in skill, f"missing external-specialist hot-path rule: {phrase}")

# All referenced Plat markdown files must exist.
for ref in re.findall(r"`(?:references/)?([a-z0-9-]+\.md)`", skill):
    p = ROOT / "skills" / "plat" / "references" / ref
    require(p.exists(), f"missing referenced file: {p.relative_to(ROOT)}")

require(ORCHESTRATION_POLICY.exists(), "deterministic orchestration policy script is missing")
require(MAINTENANCE_GATE.exists(), "maintenance evidence gate is missing")
require(MAINTENANCE_EVIDENCE.exists(), "machine-readable maintenance evidence is missing")
require(MAINTENANCE_DOC.exists(), "maintenance protocol is missing")
require(RESEARCH_LOG.exists(), "research log is missing")
require(AWS_DEEP.exists(), "AWS deep specialist reference is missing")
if AWS_DEEP.exists():
    aws_text = AWS_DEEP.read_text(encoding="utf-8")
    for phrase in [
        "aws sts get-caller-identity",
        "human access should use federation/SSO and temporary credentials",
        "A module-level in-memory dedupe set is not a durable idempotency mechanism",
        "review \`cdk diff\` / CloudFormation change sets",
        "multi-region is a major data/traffic/operational commitment",
        "Verify current quota values",
    ]:
        require(phrase.lower() in aws_text.lower(), f"AWS deep reference missing control: {phrase}")
require(BEHAVIORAL_CASES.exists(), "v1.8 behavioral case pack is missing")
require(BEHAVIORAL_TRIGGERS.exists(), "v1.8 trigger case pack is missing")
require(BEHAVIORAL_RUNNER.exists(), "v1.8 behavioral runner is missing")
require(BEHAVIORAL_SCORER.exists(), "v1.8 behavioral scorer is missing")
if BEHAVIORAL_CASES.exists():
    behavioral = json.loads(BEHAVIORAL_CASES.read_text(encoding="utf-8"))
    bc = behavioral.get("cases", [])
    require(len(bc) >= 5, f"behavioral case pack too small: {len(bc)} < 5")
    require(any(len(x.get("turns", [])) >= 3 for x in bc), "behavioral pack must include a multi-turn correction case")
if BEHAVIORAL_TRIGGERS.exists():
    triggers = json.loads(BEHAVIORAL_TRIGGERS.read_text(encoding="utf-8")).get("cases", [])
    require(len(triggers) >= 20, f"trigger case pack too small: {len(triggers)} < 20")
    require(any(x.get("expect_aws_deep") is True for x in triggers), "trigger pack must exercise AWS deep routing")
    require(any(x.get("expect_plat") is False for x in triggers), "trigger pack must include negative controls")
if MAINTENANCE_EVIDENCE.exists():
    maintenance_data = json.loads(MAINTENANCE_EVIDENCE.read_text(encoding="utf-8"))
    require(maintenance_data.get("schema_version") == 1, "maintenance evidence schema_version must be 1")
    maintenance_entries = maintenance_data.get("entries", [])
    require(isinstance(maintenance_entries, list) and len(maintenance_entries) >= 1, "maintenance evidence must contain entries")
require(ORCHESTRATION_CASES.exists(), "orchestration regression corpus is missing")
if ORCHESTRATION_CASES.exists():
    orchestration_data = json.loads(ORCHESTRATION_CASES.read_text(encoding="utf-8"))
    orchestration_items = orchestration_data.get("cases", [])
    require(len(orchestration_items) >= 20, f"orchestration corpus too small: {len(orchestration_items)} < 20")
    orchestration_ids = [x.get("id") for x in orchestration_items]
    require(len(orchestration_ids) == len(set(orchestration_ids)), "orchestration case ids are not unique")

for phrase in [
    "P-01 retains:",
    "Specialists do not directly overrule one another",
    "one level",
    "smallest discriminating check",
    "Three agreeing specialists do not beat one direct failing test",
    "same-question",
    "untrusted instruction-bearing packages",
    "license/provenance",
]:
    require(phrase.lower() in orchestration.lower(), f"missing orchestration control: {phrase}")

require(VERSION.read_text().strip() == SKILL_VERSION.read_text().strip(), "root VERSION and skill VERSION differ")
require(UPDATE_CHECK.exists(), "daily update checker script is missing")
if UPDATE_CHECK.exists():
    update_text = UPDATE_CHECK.read_text(encoding="utf-8")
    require("StartInterval" in update_text and "86400" in update_text, "daily checker must keep 24h macOS interval")
    require("OnUnitActiveSec=24h" in update_text, "daily checker must keep 24h Linux timer")
    require("LATEST_RELEASE_API" in update_text, "daily checker must use release discovery outside agent prompts")

data = json.loads(CASES.read_text(encoding="utf-8"))
items = data.get("cases", [])
require(len(items) >= 25, f"routing corpus too small: {len(items)} < 25")
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
