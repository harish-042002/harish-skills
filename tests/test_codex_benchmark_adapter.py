"""Deterministic schema tests, not live Codex executions."""
import importlib.util
from pathlib import Path
import unittest
P=Path(__file__).resolve().parents[1]/'benchmarks/behavioral-v1.8/codex_adapter.py'
spec=importlib.util.spec_from_file_location('adapter',P);adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(adapter)
class AdapterTests(unittest.TestCase):
    def test_missing_usage_is_missing(self):
        usage,_=adapter.normalized_usage([]);self.assertNotIn('input_tokens',usage)
    def test_codex_cache_inclusive_accounting(self):
        u,failed=adapter.normalized_usage([{'type':'turn.completed','usage':{'input_tokens':1000,'cached_input_tokens':800,'output_tokens':100,'reasoning_output_tokens':80}}])
        rates={'input_usd_per_million':1,'cached_input_usd_per_million':.1,'output_usd_per_million':2}
        self.assertAlmostEqual(adapter.estimate_cost(u,rates),.00048);self.assertFalse(failed)
    def test_unknown_cache_no_estimate(self):
        self.assertIsNone(adapter.estimate_cost({'input_tokens':2,'output_tokens':1},{'input_usd_per_million':1,'cached_input_usd_per_million':1,'output_usd_per_million':1}))
    def test_error_event_preserved(self):
        _,failed=adapter.normalized_usage([{'type':'turn.failed'}]);self.assertTrue(failed)
    def test_nonfinite_usage_ignored(self):
        u,_=adapter.normalized_usage([{'type':'turn.completed','usage':{'input_tokens':float('inf'),'output_tokens':True}}]);self.assertNotIn('input_tokens',u);self.assertNotIn('output_tokens',u)
    def test_tool_calls_deduplicated(self):
        event={'type':'item.completed','item':{'id':'a','type':'command_execution'}}
        u,_=adapter.normalized_usage([event,event]);self.assertEqual(u['tool_calls'],1)
    def test_all_user_constraints_survive_prompt(self):
        rows=[{'role':'developer','content':f'Requirement {i}'} for i in range(30)]
        text=adapter.prompt_from_transcript(rows)
        for row in rows:self.assertIn(row['content'],text)
    def test_tool_logs_not_replayed(self):
        text=adapter.prompt_from_transcript([{'role':'assistant','content':'{"type":"item.completed","item":{"type":"command_execution","aggregated_output":"very large log"}}'}])
        self.assertNotIn('very large log',text)
if __name__=='__main__':unittest.main()
