"""Test only isolated installer rule functions; never run an installation."""
from pathlib import Path
import subprocess
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]

class ActivationEconomyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.file = Path(self.tmp.name)/'AGENTS.md'
        text=(ROOT/'install.sh').read_text()
        self.functions=text[text.index('append_block() {'):text.index('wire_known_agents() {')]

    def apply(self):
        return subprocess.run(['bash','-c', self.functions+'\nappend_block "$1"','test',str(self.file)],capture_output=True,text=True,timeout=5)

    def test_update_existing_rule_preserves_user_instructions(self):
        self.file.write_text('BEFORE\n<!-- plat:start -->\nFor software engineering requests, use the installed Plat skill.\n<!-- plat:end -->\nAFTER\n')
        self.assertEqual(self.apply().returncode,0)
        result=self.file.read_text()
        self.assertTrue(result.startswith('BEFORE\n'))
        self.assertTrue(result.endswith('\nAFTER\n'))
        self.assertIn('without loading Plat unless explicitly requested',result)

    def test_rule_is_idempotent(self):
        self.assertEqual(self.apply().returncode,0)
        result=self.file.read_bytes()
        self.assertEqual(self.apply().returncode,0)
        self.assertEqual(self.file.read_bytes(),result)
        self.assertEqual(result.count(b'<!-- plat:start -->'),1)

    def test_malformed_markers_leave_file_unchanged(self):
        original='USER\n<!-- plat:start -->\nUSER TAIL'
        self.file.write_text(original)
        self.assertNotEqual(self.apply().returncode,0)
        self.assertEqual(self.file.read_text(),original)

    def test_powershell_has_same_tiny_task_gate(self):
        # Static parity only, not a native Windows execution test.
        text=(ROOT/'install.ps1').read_text()
        self.assertIn('without loading Plat unless explicitly requested',text)
        self.assertNotIn('Plat instruction already present:',text)

if __name__=='__main__':
    unittest.main()
