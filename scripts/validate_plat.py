#!/usr/bin/env python3
from __future__ import annotations
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "plat" / "SKILL.md"
ROUTING = ROOT / "skills" / "plat" / "references" / "routing.md"
ORCHESTRATION = ROOT / "skills" / "plat" / "references" / "orchestration.md"
CONTEXT = ROOT / "skills" / "plat" / "references" / "context.md"
EFFICIENCY = ROOT / "skills" / "plat" / "references" / "efficiency.md"
TASK_STATE = ROOT / "skills" / "plat" / "scripts" / "task_state.py"
POLICY = ROOT / "skills" / "plat" / "scripts" / "orchestration_policy.py"
CONTEXT_GUARD = ROOT / "skills" / "plat" / "scripts" / "context_guard.py"
EVIDENCE_EXEC = ROOT / "skills" / "plat" / "scripts" / "evidence_exec.py"
BRAIN_PACKET = ROOT / "skills" / "plat" / "scripts" / "brain_packet.py"
DISCOVERY = ROOT / "skills" / "plat" / "scripts" / "discover_skills.py"
UPDATE_CHECK = ROOT / "skills" / "plat" / "scripts" / "update_check.py"
INSTALL_SH = ROOT / "install.sh"
INSTALL_PS1 = ROOT / "install.ps1"
VERSION = ROOT / "VERSION"
SKILL_VERSION = ROOT / "skills" / "plat" / "VERSION"
MAINTENANCE_GATE = ROOT / "scripts" / "maintenance_gate.py"
MAINTENANCE_EVIDENCE = ROOT / "docs" / "maintenance-evidence.json"
RESEARCH_LOG = ROOT / "docs" / "RESEARCH_LOG.md"
AWS_DEEP = ROOT / "skills" / "plat" / "references" / "aws-deep.md"
BEHAVIORAL_DIR = ROOT / "benchmarks" / "behavioral-v1.8"

errors=[]

def require(cond,msg):
    if not cond: errors.append(msg)

skill=SKILL.read_text(encoding="utf-8")
context=CONTEXT.read_text(encoding="utf-8")
efficiency=EFFICIENCY.read_text(encoding="utf-8")
orchestration=ORCHESTRATION.read_text(encoding="utf-8")
policy=POLICY.read_text(encoding="utf-8")
task_state=TASK_STATE.read_text(encoding="utf-8")

require(len(skill)<=7000,f"SKILL.md hot path too large: {len(skill)} chars > 7000")
require(len(skill.splitlines())<=150,f"SKILL.md too many lines: {len(skill.splitlines())} > 150")

m=re.match(r"^---\n(.*?)\n---",skill,re.S)
require(bool(m),"SKILL.md missing valid frontmatter")
if m:
    keys=[line.split(":",1)[0].strip() for line in m.group(1).splitlines() if ":" in line and not line.startswith((" ","\t"))]
    require(keys==["name","description"],f"frontmatter keys must be name,description only; got {keys}")

for phrase in [
    "latest developer request/correction","DIRECT","STANDARD","ESCALATED","0 specialists",
    "Model tiers, not model names","Worker tier:","Brain tier:","Brain reviewer","five-minute",
    "Task capsule and compaction","Do not follow reference-to-reference chains automatically",
    "context_guard.py","evidence_exec.py","brain_packet.py","fresh-context worker",
    "fresh evidence after the final relevant edit",
]:
    require(phrase.lower() in skill.lower(),f"missing v2 hot-path rule: {phrase}")

for phrase in ["Target <= 2 KB","4 KB","Context-pressure recovery","fresh-context worker","current_slice","brain_reviews","hidden chain-of-thought"]:
    require(phrase.lower() in context.lower(),f"context capsule missing control: {phrase}")

for phrase in ["Output firewall","Context watchdog","Five-minute watchdog","YELLOW","RED","ACT / VERIFY / REROUTE","4 KB","aggregate model/API time"]:
    require(phrase.lower() in efficiency.lower(),f"efficiency watchdog missing control: {phrase}")

for phrase in ["Brain reviewer","Routine budget: <=2 Brain reviews","Fresh-context worker","Hard cap: 4 KB","DIRECT/STANDARD tasks do not delegate","one consultant maximum","untrusted instruction-bearing packages","Do not vote"]:
    require(phrase.lower() in orchestration.lower(),f"orchestration missing v2 control: {phrase}")

require("cost-efficient-latest" in policy,"policy must use generic worker capability tier")
require("one-tier-stronger-cost-effective" in policy,"policy must use generic Brain capability tier")
require("MAX_BRAIN_REVIEWS = 2" in policy,"policy must cap routine Brain reviews")
require('VALID_PATHS = {"DIRECT", "STANDARD", "ESCALATED"}' in policy,"policy must expose DIRECT/STANDARD/ESCALATED")
require('execution_path == "DIRECT"' in policy,"DIRECT must stay single-agent")
require('execution_path == "STANDARD"' in policy,"STANDARD must keep specialist budget zero by default")
require("VALID_CONTEXT_HEALTH" in policy,"policy must expose context health")
require("MAX_FRESH_CONTEXT_WORKERS = 1" in policy,"policy must cap fresh-context workers")
require('"fresh-context-worker"' in policy,"policy must support context-isolation recovery")

for phrase in ["DEFAULT_CHECKPOINT_SECONDS = 300","YELLOW_AFTER_SECONDS = 300","RED_AFTER_SECONDS = 600","ORDINARY_BRAIN_AFTER_SECONDS = 1200","MAX_BRAIN_REVIEWS = 2",'"BLOCKED"']:
    require(phrase in task_state,f"task-state helper missing: {phrase}")

for path,msg in [(DISCOVERY,"installed-skill discovery broker is missing"),(CONTEXT_GUARD,"context guard is missing"),(EVIDENCE_EXEC,"evidence executor is missing"),(BRAIN_PACKET,"Brain packet builder is missing"),(ROUTING,"routing reference is missing"),(AWS_DEEP,"AWS deep knowledge card is missing"),(MAINTENANCE_GATE,"maintenance evidence gate is missing"),(MAINTENANCE_EVIDENCE,"maintenance evidence is missing"),(RESEARCH_LOG,"research log is missing")]:
    require(path.exists(),msg)

for ref in re.findall(r"`(?:references/)?([a-z0-9-]+\.md)`",skill):
    p=ROOT/"skills"/"plat"/"references"/ref
    require(p.exists(),f"missing referenced file: {p.relative_to(ROOT)}")

require(VERSION.read_text().strip()==SKILL_VERSION.read_text().strip(),"root VERSION and skill VERSION differ")
require(VERSION.read_text().strip()=="2.2.0","Plat context-economy release must be version 2.2.0")

payload=json.loads(MAINTENANCE_EVIDENCE.read_text(encoding="utf-8"))
require(payload.get("schema_version")==1,"maintenance evidence schema_version must be 1")
require(any(x.get("id")=="2026-09-24-v2.0.2-all-agent-installer" for x in payload.get("entries",[])),"missing v2.0.2 all-agent maintenance evidence entry")
require(any(x.get("id")=="2026-09-24-v2.1-final-runtime-contract" for x in payload.get("entries",[])),"missing v2.1 runtime maintenance evidence entry")
require(any(x.get("id")=="2026-09-24-v2.2-context-economy" for x in payload.get("entries",[])),"missing v2.2 context-economy maintenance evidence entry")

context_guard=CONTEXT_GUARD.read_text(encoding="utf-8")
evidence_exec=EVIDENCE_EXEC.read_text(encoding="utf-8")
brain_packet=BRAIN_PACKET.read_text(encoding="utf-8")
for phrase in [
    "TOOL_RESULT_TARGET_BYTES = 6 * 1024",
    "YELLOW_RETURNED_BYTES = 64 * 1024",
    "RED_RETURNED_BYTES = 128 * 1024",
    "MAX_FRESH_CONTEXT_WORKERS = 1",
]:
    require(phrase in context_guard,f"context guard missing v2.2 control: {phrase}")
for phrase in [
    "DEFAULT_MAX_RETURN_BYTES = 6 * 1024",
    ".plat/logs",
    "context_guard.record",
]:
    require(phrase in evidence_exec,f"evidence executor missing v2.2 control: {phrase}")
for phrase in [
    "DEFAULT_MAX_BYTES = 4096",
    "brain packet exceeds hard limit",
]:
    require(phrase in brain_packet,f"Brain packet missing v2.2 control: {phrase}")

update_check=UPDATE_CHECK.read_text(encoding="utf-8")
for phrase in [
    "CHECK_INTERVAL_SECONDS = 2 * 60 * 60",
    "OnUnitActiveSec=2h",
    "\"HOURLY\"",
    "--update-all",
    "last_notified_signature",
    "skills@latest",
    "\"update\"",
]:
    require(phrase in update_check,f"update checker missing v2.0.1 control: {phrase}")

for phrase in [
    "def register_scope",
    '"list", "--json"',
    "agent_selector",
    "display_installation",
    'command.extend(["-a", "*" if selector == "all" else selector])',
]:
    require(phrase in update_check,f"update checker missing all-agent control: {phrase}")

install_sh=INSTALL_SH.read_text(encoding="utf-8")
install_ps1=INSTALL_PS1.read_text(encoding="utf-8")
for phrase in [
    "--agent all|<skills-cli-agent-id>",
    'AGENT="*"',
    "--register-scope",
    "skills@latest",
]:
    require(phrase in install_sh,f"Bash installer missing all-agent control: {phrase}")
for phrase in [
    '[string]$Agent',
    'return "*"',
    "--register-scope",
    "skills@latest",
]:
    require(phrase in install_ps1,f"PowerShell installer missing all-agent control: {phrase}")
require('ValidateSet("claude-code","codex","cursor")' not in install_ps1,"PowerShell installer must not restore a three-agent whitelist")

for name in ["cases.json","trigger-cases.json","run_behavioral_eval.py","score_results.py"]:
    require((BEHAVIORAL_DIR/name).exists(),f"behavioral asset missing: {name}")

if errors:
    print("PLAT VALIDATION FAILED")
    for e in errors: print(f"- {e}")
    sys.exit(1)

print("PLAT VALIDATION PASSED")
print(f"- hot path: {len(skill)} chars / {len(skill.splitlines())} lines")
print(f"- version: {VERSION.read_text().strip()}")
print("- v2 runtime: task capsule + watchdog + bounded Brain")
