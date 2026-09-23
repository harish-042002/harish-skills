from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "plat" / "scripts" / "discover_skills.py"


def write_skill(path: Path, name: str, description: str, folded: bool = False) -> None:
    path.mkdir(parents=True, exist_ok=True)
    if folded:
        body = "---\nname: " + name + "\ndescription: >\n  " + description + "\n---\n\n# Test\n"
    else:
        body = f'---\nname: {name}\ndescription: "{description}"\n---\n\n# Test\n'
    (path / "SKILL.md").write_text(body, encoding="utf-8")


class DiscoverSkillsTests(unittest.TestCase):
    def run_discovery(self, home: Path, project: Path, query: str):
        env = os.environ.copy()
        env["HOME"] = str(home)
        env.pop("CODEX_HOME", None)
        env.pop("CLAUDE_CONFIG_DIR", None)
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--cwd",
                str(project),
                "--query",
                query,
                "--limit",
                "10",
                "--json",
            ],
            check=True,
            capture_output=True,
            text=True,
            env=env,
        )
        return json.loads(result.stdout)["skills"]

    def test_project_skill_beats_global_duplicate_and_plat_is_excluded(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            home = root / "home"
            project = root / "repo"
            (project / ".git").mkdir(parents=True)

            write_skill(
                home / ".codex" / "skills" / "rag-implementation",
                "rag-implementation",
                "Generic RAG retrieval implementation",
            )
            write_skill(
                project / ".agents" / "skills" / "rag-implementation",
                "rag-implementation",
                "Project-local hybrid retrieval ranking and RAG tuning",
            )
            write_skill(
                project / ".agents" / "skills" / "plat",
                "plat",
                "Plat itself",
            )

            skills = self.run_discovery(home, project, "hybrid retrieval")
            self.assertEqual(skills[0]["name"], "rag-implementation")
            self.assertEqual(skills[0]["scope"], "project")
            self.assertIn(str(project / ".agents" / "skills"), skills[0]["path"])
            self.assertNotIn("plat", [x["name"].lower() for x in skills])

    def test_folded_description_and_hyphen_tokens_are_searchable(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            home = root / "home"
            project = root / "repo"
            (project / ".git").mkdir(parents=True)

            write_skill(
                home / ".cursor" / "skills" / "security-threat-model",
                "security-threat-model",
                "Threat modeling for authentication authorization and security boundaries",
                folded=True,
            )

            skills = self.run_discovery(home, project, "auth security")
            self.assertEqual(len(skills), 1)
            self.assertEqual(skills[0]["name"], "security-threat-model")
            self.assertGreater(skills[0]["score"], 0)

    def test_unrelated_skill_is_not_forced(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            home = root / "home"
            project = root / "repo"
            (project / ".git").mkdir(parents=True)

            write_skill(
                home / ".claude" / "skills" / "frontend-design",
                "frontend-design",
                "Design polished frontend interfaces",
            )

            skills = self.run_discovery(home, project, "postgres isolation")
            self.assertEqual(skills, [])

    def test_specific_specialist_outranks_broad_orchestrator(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            home = root / "home"
            project = root / "repo"
            (project / ".git").mkdir(parents=True)

            write_skill(
                home / ".codex" / "skills" / "agent-orchestrator",
                "agent-orchestrator",
                "General-purpose agent orchestration workflow for many engineering tasks",
            )
            write_skill(
                home / ".codex" / "skills" / "postgres-isolation",
                "postgres-isolation",
                "Postgres transaction isolation locking and concurrent write debugging",
            )

            skills = self.run_discovery(home, project, "postgres isolation")
            self.assertEqual(skills[0]["name"], "postgres-isolation")
            self.assertFalse(skills[0]["broad"])
            broad = next(x for x in skills if x["name"] == "agent-orchestrator")
            self.assertTrue(broad["broad"])
            self.assertGreater(skills[0]["score"], broad["score"])

    def test_json_output_includes_match_explanation(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            home = root / "home"
            project = root / "repo"
            (project / ".git").mkdir(parents=True)

            write_skill(
                home / ".claude" / "skills" / "rag-ranking",
                "rag-ranking",
                "Hybrid retrieval ranking and RAG evaluation",
            )

            skills = self.run_discovery(home, project, "hybrid retrieval")
            self.assertEqual(skills[0]["name"], "rag-ranking")
            self.assertIn("retrieval", skills[0]["matched_terms"])
            self.assertIn("broad", skills[0])


if __name__ == "__main__":
    unittest.main()
