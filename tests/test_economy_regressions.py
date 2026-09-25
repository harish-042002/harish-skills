"""Adversarial cases for failures reproduced against upstream v2.3.0.
These test runtime behavior, not model quality or production cost savings.
"""
import datetime as dt
import importlib
import inspect
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1] / 'skills/plat/scripts'
sys.path.insert(0, str(SCRIPTS))
import context_guard as guard
import evidence_exec as runner
import evidence_read as reader
import host_context as telemetry
import brain_packet as brain
import task_state

class EconomyRegressions(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.read_opts = dict(index_path=self.root/'index.json', context_state=self.root/'context.json', max_return_bytes=2048)

    def source(self, text):
        p = self.root/'source.txt'
        p.write_text(text, encoding='utf-8')
        return p

    def parse(self, rows):
        p = self.root/'transcript.jsonl'
        p.write_text('\n'.join(json.dumps(x) for x in rows)+'\n')
        return telemetry.parse_jsonl(p)

    def test_tiny_reads_do_not_prove_context_full(self):
        state = guard.new_state()
        for i in range(24):
            state = guard.record(state, returned_bytes=10, kind='read', key=str(i))
        self.assertNotEqual(state['health']['status'], 'RED')
        self.assertNotIn(state['health']['action'], ['fresh-context-worker', 'checkpoint-compact'])

    def test_cache_replay_is_cost_not_occupancy(self):
        state = guard.new_state()
        for n in [0, 21000000]:
            state = guard.apply_telemetry(state, {'available': True, 'cache_read_tokens': n, 'context_utilization': .4})
        self.assertEqual(state['health']['status'], 'GREEN')
        self.assertEqual(state['efficiency']['status'], 'YELLOW')

    def test_real_occupancy_still_escalates(self):
        state = guard.apply_telemetry(guard.new_state(), {'available': True, 'context_utilization': .85})
        self.assertEqual(state['health']['status'], 'RED')

    def test_confirmed_reset_starts_new_epoch_not_new_worker_budget(self):
        state = guard.new_state()
        epoch = state['context_epoch']
        state = guard.record_fresh_context_worker(state)
        state = guard.record(state, returned_bytes=200000, kind="command")
        state = guard.reset_context(state)
        self.assertEqual(state['returned_bytes'], 0)
        self.assertEqual(state['health']['status'], 'GREEN')
        self.assertEqual(state['fresh_context_workers'], 1)
        self.assertNotEqual(state['context_epoch'], epoch)

    def test_partial_read_is_never_masked(self):
        p = self.source('a'*20000+'DO_NOT_DROP_REQUIREMENT')
        one = reader.read_evidence(p, **self.read_opts)
        two = reader.read_evidence(p, **self.read_opts)
        self.assertTrue(one['truncated'])
        self.assertFalse(two['masked'])
        self.assertIsNotNone(one['next_offset'])

    def test_unicode_pagination_is_lossless_and_bounded(self):
        text = ('\u0ba4\u0bae\u0bbf\u0bb4\u0bcd "quoted" \\slashes\t' * 350) + '\nFINAL_REQUIREMENT'
        p = self.source(text)
        pieces, offset, digest = [], 0, None
        for _ in range(200):
            result = reader.read_evidence(p, offset=offset, expected_sha256=digest, **self.read_opts)
            self.assertLessEqual(len(json.dumps(result, indent=2, sort_keys=True).encode()), 2048)
            pieces.append(result['content'])
            digest = result['sha256']
            if not result['truncated']:
                break
            self.assertGreater(result['next_offset'], offset)
            offset = result['next_offset']
        else:
            self.fail('pagination did not terminate')
        self.assertEqual(''.join(pieces), text)

    def test_pagination_rejects_changed_source(self):
        p = self.source('a'*10000)
        one = reader.read_evidence(p, **self.read_opts)
        p.write_text('b'*10000)
        with self.assertRaisesRegex(ValueError, 'changed'):
            reader.read_evidence(p, offset=one['next_offset'], expected_sha256=one['sha256'], **self.read_opts)

    def test_new_context_must_read_again(self):
        p = self.source('important')
        reader.read_evidence(p, **self.read_opts)
        self.assertTrue(reader.read_evidence(p, **self.read_opts)['masked'])
        guard.save(self.read_opts['context_state'], guard.reset_context(guard.load(self.read_opts['context_state'])))
        self.assertFalse(reader.read_evidence(p, **self.read_opts)['masked'])

    def test_refresh_returns_full_delivered_evidence(self):
        p = self.source('proof')
        reader.read_evidence(p, **self.read_opts)
        self.assertEqual(reader.read_evidence(p, refresh=True, **self.read_opts)['content'], 'proof')

    def test_cumulative_counters_not_summed(self):
        parsed = self.parse([{'payload': {'info': {'total_token_usage': {'input_tokens': n, 'output_tokens': n//10}}}} for n in [100, 200]])
        self.assertEqual(parsed['input_tokens'], 200)
        self.assertEqual(parsed['output_tokens'], 20)

    def test_latest_usage_for_duplicate_id(self):
        parsed = self.parse([{'message': {'id': 'm1', 'usage': {'input_tokens': 10, 'output_tokens': n}}} for n in [1, 5]])
        self.assertEqual(parsed['input_tokens'], 10)
        self.assertEqual(parsed['output_tokens'], 5)

    def test_context_occupancy_can_decrease(self):
        parsed = self.parse([{'id': str(i), 'usage': {'input_tokens': 1, 'context_used_tokens': n, 'context_limit_tokens': 1000}} for i,n in enumerate([900, 200])])
        self.assertEqual(telemetry.normalize(parsed)['context_utilization'], .2)

    def test_responses_cached_token_details(self):
        parsed = telemetry.normalize({'input_tokens': 100, 'input_tokens_details': {'cached_tokens': 75}})
        self.assertEqual(parsed['cache_read_tokens'], 75)

    def test_no_usage_is_unavailable_not_zero(self):
        parsed = self.parse([{'message': {'content': 'nothing'}}, {'arbitrary_config': {'input_tokens': 999}}])
        self.assertFalse(telemetry.normalize(parsed)['available'])
        self.assertNotIn('input_tokens', parsed)

    def test_explicit_transcript_beats_saved_snapshot(self):
        canonical = self.root/'telemetry.json'
        canonical.write_text(json.dumps({'input_tokens': 999, 'observed_at': '2020-01-01T00:00:00+00:00'}))
        self.parse([{'id':'a', 'usage': {'input_tokens': 12}}])
        with mock.patch.object(telemetry, 'CANONICAL_FILE', canonical), mock.patch.dict(os.environ, {}, clear=True):
            result = telemetry.discover(transcript=self.root/'transcript.jsonl')
        self.assertEqual(result['input_tokens'], 12)

    def test_saved_snapshot_not_made_fresh(self):
        canonical = self.root/'telemetry.json'
        stamp = '2020-01-01T00:00:00+00:00'
        canonical.write_text(json.dumps({'host':'codex', 'context_used_tokens':900, 'context_limit_tokens':1000, 'observed_at':stamp}))
        with mock.patch.object(telemetry, 'CANONICAL_FILE', canonical), mock.patch.dict(os.environ, {}, clear=True):
            result = telemetry.discover()
        self.assertEqual(result['observed_at'], stamp)
        self.assertEqual(result['host'], 'codex')
        self.assertNotIn('context_utilization', result)

    def test_non_finite_counters_rejected(self):
        result = telemetry.normalize({'input_tokens': float('nan'), 'output_tokens': -1, 'cost_usd': float('inf')})
        self.assertFalse(result['available'])

    def test_all_binding_requirements_preserved(self):
        state = {'goal':'fix', 'must':[f'requirement-{i}' for i in range(9)], 'must_not':[f'forbidden-{i}' for i in range(9)], 'preserve':['contract'], 'proof':['all cases']}
        result = brain.build_packet(state, question='review')
        for key in state:
            self.assertEqual(result[key], state[key])
        self.assertTrue(result['contract_complete'])

    def test_oversize_contract_rejected_not_silently_clipped(self):
        with self.assertRaisesRegex(ValueError, 'binding contract'):
            brain.build_packet({'must_not':['FORBIDDEN'*1000]}, question='review', max_bytes=1024)

    def test_timeout_stops_command(self):
        start = time.monotonic()
        result = runner.run_command([sys.executable, '-c', 'import time;time.sleep(10)'], log_dir=self.root/'logs', context_state=self.root/'ctx.json', timeout_seconds=.12)
        self.assertEqual(result['exit_code'], 124)
        self.assertTrue(result['timed_out'])
        self.assertLess(time.monotonic()-start, 3)

    def test_cli_preserves_nonzero_exit_code(self):
        proc = subprocess.run([sys.executable, str(SCRIPTS/'evidence_exec.py'), '--', sys.executable, '-c', 'raise SystemExit(7)'], cwd=self.root, capture_output=True, timeout=10)
        self.assertEqual(proc.returncode, 7)

    def test_output_limit_stops_flood(self):
        result = runner.run_command([sys.executable, '-c', 'import os,time\nwhile True:\n os.write(1,b"x"*8192);time.sleep(.001)'], log_dir=self.root/'logs', context_state=self.root/'ctx.json', max_output_bytes=32768, timeout_seconds=3)
        self.assertTrue(result['output_limited'])
        self.assertEqual(result['exit_code'], 125)

    def test_invalid_timeout_rejected(self):
        for timeout in [0, -1, float('inf'), float('nan')]:
            with self.assertRaises(ValueError):
                runner.run_command([sys.executable, '-c', 'pass'], timeout_seconds=timeout)

    @unittest.skipUnless(os.name == 'posix', 'POSIX process-group cleanup')
    def test_termination_cleans_live_descendant(self):
        marker, ready = self.root/'leaked.txt', self.root/'ready.txt'
        child = f'from pathlib import Path;import time;Path({str(ready)!r}).write_text("ready");time.sleep(.8);Path({str(marker)!r}).write_text("leak")'
        parent = f'import subprocess,sys,time;subprocess.Popen([sys.executable,"-c",{child!r}]);time.sleep(10)'
        proc = subprocess.Popen([sys.executable, '-c', parent], start_new_session=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            deadline = time.monotonic()+5
            while not ready.exists() and time.monotonic()<deadline:
                time.sleep(.01)
            self.assertTrue(ready.exists(), 'test must observe a live child before termination')
            runner._terminate(proc)
            time.sleep(1)
            self.assertFalse(marker.exists())
        finally:
            if proc.poll() is None:
                runner._terminate(proc)

    def test_progress_before_checkpoint_is_not_lost(self):
        state = task_state.new_state('x', started_at='2026-09-25T00:00:00Z')
        task_state.evaluate_checkpoint(state, at='2026-09-25T00:04:00Z', meaningful_progress=True)
        self.assertEqual(state['execution']['last_progress_at'], '2026-09-25T00:04:00Z')
        result = task_state.evaluate_checkpoint(state, at='2026-09-25T00:06:00Z')
        self.assertEqual(result['state']['health']['status'], 'GREEN')

    def test_waiting_without_deadline_is_not_green_forever(self):
        state = task_state.new_state('x', started_at='2026-09-25T00:00:00Z')
        result = task_state.evaluate_checkpoint(state, at='2026-09-25T02:00:00Z', waiting=True)
        self.assertEqual(result['state']['health']['status'], 'BLOCKED')
        self.assertFalse(result['brain_recommended'])

    def test_known_wait_deadline_expires(self):
        state = task_state.new_state('x', started_at='2026-09-25T00:00:00Z')
        task_state.evaluate_checkpoint(state, at='2026-09-25T00:01:00Z', waiting=True, waiting_until='2026-09-25T00:02:00Z')
        self.assertEqual(state['health']['status'], 'GREEN')
        task_state.evaluate_checkpoint(state, at='2026-09-25T00:03:00Z', waiting=True)
        self.assertEqual(state['health']['status'], 'BLOCKED')

    def test_unknown_isolation_is_not_assumed_available(self):
        from orchestration_policy import decide
        self.assertFalse(decide(execution_path='STANDARD', context_health='RED').fresh_context_worker)

    def test_stale_context_measurement_is_not_current(self):
        state = guard.apply_telemetry(guard.new_state(), {'available':True, 'context_utilization':.99, 'observed_at':'2020-01-01T00:00:00Z'})
        self.assertNotEqual(state['health']['status'], 'RED')

    def test_oversized_optional_brief_stays_capped_without_dropping_contract(self):
        contract = {'goal':'fix', 'must_not':['do not deploy'], 'proof':['focused test']}
        state = {**contract, 'owner':['x'*1000 for _ in range(10)], 'next':'n'*10000}
        result = brain.build_packet(state, question='review', evidence=['e'*1000 for _ in range(10)], max_bytes=1024)
        self.assertLessEqual(len(json.dumps(result, indent=2, sort_keys=True).encode()),1024)
        for key,value in contract.items():
            self.assertEqual(result[key], value)

    def test_bad_optional_state_does_not_hide_command_result(self):
        ctx = self.root/'bad.json'
        ctx.write_text('{broken')
        result = runner.run_command([sys.executable, '-c', 'raise SystemExit(7)'], context_state=ctx, log_dir=self.root/'logs')
        self.assertEqual(result['exit_code'],7)
        self.assertEqual(result['context_health']['status'],'UNKNOWN')
        self.assertIn('telemetry_warning',result)

    def test_small_return_budget_with_unicode_metadata_keeps_result(self):
        command = [sys.executable, '-c', 'pass # '+chr(0x0ba4)*1000]
        result = runner.run_command(command, context_state=self.root/'ctx.json', log_dir=self.root/'logs', max_return_bytes=1024)
        self.assertEqual(result['exit_code'],0)
        self.assertLessEqual(len(json.dumps(result,indent=2,sort_keys=True).encode()),1024)

    def test_unterminated_command_cannot_read_stdin_forever(self):
        result = runner.run_command([sys.executable, '-c', 'import sys;print(repr(sys.stdin.read()))'], context_state=self.root/'ctx.json', log_dir=self.root/'logs', timeout_seconds=3)
        self.assertEqual(result['exit_code'],0)
        self.assertFalse(result['timed_out'])

if __name__ == '__main__':
    unittest.main()
