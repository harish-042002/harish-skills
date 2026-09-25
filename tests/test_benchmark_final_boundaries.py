"""Final boundary checks; synthetic unit events are not model benchmark evidence."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]/'benchmarks/behavioral-v1.8'
def load(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/(name+'.py'))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

class BenchmarkFinalBoundaries(unittest.TestCase):
    def test_non_object_events_do_not_break_prompt(self):
        adapter=load('codex_adapter')
        content='\n'.join(json.dumps(e) for e in [None,[],7,{'type':'item.completed','item':None},{'type':'item.completed','item':{'type':'agent_message','text':'done'}}])
        prompt=adapter.prompt_from_transcript([{'role':'assistant','content':content}])
        self.assertIn('done',prompt)
    def test_partial_turn_cost_excluded_not_zero(self):
        scorer=load('score_results')
        common=dict(condition='candidate',passed=True,wall_seconds=1,attempted_turns=3)
        rows=[dict(common,telemetry={'cost_usd':10},telemetry_coverage={'cost_usd':3}),
              dict(common,telemetry={'cost_usd':2},telemetry_coverage={'cost_usd':1})]
        out=scorer.summarize(rows)['candidate']
        self.assertEqual(out['mean_telemetry']['cost_usd'],10)
        self.assertEqual(out['telemetry_coverage']['cost_usd']['partial_runs'],1)
        self.assertFalse(out['telemetry_coverage']['cost_usd']['complete'])
    def test_all_partial_cost_stays_unknown(self):
        scorer=load('score_results')
        out=scorer.summarize([dict(condition='x',passed=False,wall_seconds=1,attempted_turns=2,
                                  telemetry={'cost_usd':2},telemetry_coverage={'cost_usd':1})])['x']
        self.assertIsNone(out['mean_telemetry']['cost_usd'])

if __name__=='__main__':unittest.main()
