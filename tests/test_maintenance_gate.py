from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "maintenance_gate.py"


def load_module():
    spec = importlib.util.spec_from_file_location("plat_maintenance_gate", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class MaintenanceGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_module()

    def valid_payload(self, material_files=None):
        material_files = material_files or ["skills/plat/SKILL.md"]
        return {
            "schema_version": 1,
            "entries": [{
                "id": "2026-09-23-market-gate",
                "date": "2026-09-23",
                "capability": "Enforce evidence-backed Plat maintenance",
                "material_files": material_files,
                "sources": [
                    {"repo": "NVIDIA/skills", "license": "Apache-2.0 + CC-BY-4.0", "inspected": "benchmark and validation governance", "reuse": "principle-only"},
                    {"repo": "jscraik/Agent-Skills", "license": "Apache-2.0", "inspected": "proof lanes and changed-surface validation", "reuse": "principle-only"},
                ],
                "adopted": ["changed-file-aware CI evidence gate"],
                "rejected": ["runtime market scans"],
                "tests": ["python -m unittest tests.test_maintenance_gate"],
            }],
        }

    def valid_log(self):
        return "2026-09-23-market-gate\nNVIDIA/skills\njscraik/Agent-Skills\n"

    def test_docs_only_change_does_not_require_market_evidence(self):
        result = self.mod.evaluate(["README.md"], {}, "")
        self.assertFalse(result.required)
        self.assertTrue(result.passed)

    def test_material_skill_change_requires_evidence_files_to_change(self):
        result = self.mod.evaluate(["skills/plat/SKILL.md"], self.valid_payload(), self.valid_log())
        self.assertTrue(result.required)
        self.assertFalse(result.passed)
        self.assertIn("docs/maintenance-evidence.json", "\n".join(result.errors))
        self.assertIn("docs/RESEARCH_LOG.md", "\n".join(result.errors))

    def test_valid_material_change_passes(self):
        changed = ["skills/plat/SKILL.md", "docs/maintenance-evidence.json", "docs/RESEARCH_LOG.md"]
        result = self.mod.evaluate(changed, self.valid_payload(), self.valid_log())
        self.assertTrue(result.required)
        self.assertTrue(result.passed, result.errors)

    def test_two_public_sources_are_required(self):
        payload = self.valid_payload()
        payload["entries"][-1]["sources"] = payload["entries"][-1]["sources"][:1]
        changed = ["skills/plat/SKILL.md", "docs/maintenance-evidence.json", "docs/RESEARCH_LOG.md"]
        result = self.mod.evaluate(changed, payload, self.valid_log())
        self.assertFalse(result.passed)
        self.assertTrue(any("at least 2 public sources" in e for e in result.errors))

    def test_source_license_and_reuse_are_required(self):
        payload = self.valid_payload()
        payload["entries"][-1]["sources"][0]["license"] = ""
        payload["entries"][-1]["sources"][1]["reuse"] = "borrowed"
        changed = ["skills/plat/SKILL.md", "docs/maintenance-evidence.json", "docs/RESEARCH_LOG.md"]
        result = self.mod.evaluate(changed, payload, self.valid_log())
        self.assertFalse(result.passed)
        self.assertTrue(any("missing license" in e for e in result.errors))
        self.assertTrue(any("reuse must be one of" in e for e in result.errors))

    def test_unknown_license_cannot_be_copied(self):
        payload = self.valid_payload()
        payload["entries"][-1]["sources"][0]["license"] = "unknown"
        payload["entries"][-1]["sources"][0]["reuse"] = "copied"
        changed = ["skills/plat/SKILL.md", "docs/maintenance-evidence.json", "docs/RESEARCH_LOG.md"]
        result = self.mod.evaluate(changed, payload, self.valid_log())
        self.assertFalse(result.passed)
        self.assertTrue(any("must be principle-only" in e for e in result.errors))

    def test_every_material_file_must_be_covered(self):
        changed = [
            "skills/plat/SKILL.md",
            "install.sh",
            "docs/maintenance-evidence.json",
            "docs/RESEARCH_LOG.md",
        ]
        result = self.mod.evaluate(changed, self.valid_payload(), self.valid_log())
        self.assertFalse(result.passed)
        self.assertTrue(any("install.sh" in e for e in result.errors))

    def test_tests_must_be_recorded(self):
        payload = self.valid_payload()
        payload["entries"][-1]["tests"] = []
        changed = ["skills/plat/SKILL.md", "docs/maintenance-evidence.json", "docs/RESEARCH_LOG.md"]
        result = self.mod.evaluate(changed, payload, self.valid_log())
        self.assertFalse(result.passed)
        self.assertTrue(any("tests" in e for e in result.errors))

    def test_research_log_must_reference_entry_and_sources(self):
        changed = ["skills/plat/SKILL.md", "docs/maintenance-evidence.json", "docs/RESEARCH_LOG.md"]
        result = self.mod.evaluate(changed, self.valid_payload(), "unrelated text")
        self.assertFalse(result.passed)
        joined = "\n".join(result.errors)
        self.assertIn("maintenance evidence id", joined)
        self.assertIn("NVIDIA/skills", joined)
        self.assertIn("jscraik/Agent-Skills", joined)

    def test_behavioral_script_and_ci_workflow_are_material(self):
        self.assertTrue(self.mod.is_material("skills/plat/scripts/discover_skills.py"))
        self.assertTrue(self.mod.is_material("scripts/validate_plat.py"))
        self.assertTrue(self.mod.is_material(".github/workflows/validate-plat.yml"))
        self.assertFalse(self.mod.is_material("tests/test_skill_discovery.py"))
        self.assertFalse(self.mod.is_material("skills/plat/LICENSE.txt"))


if __name__ == "__main__":
    unittest.main()
