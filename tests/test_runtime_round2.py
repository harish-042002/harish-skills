import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import tracemalloc
import unittest

SCRIPTS=Path(__file__).resolve().parents[1]/'skills/plat/scripts'
sys.path.insert(0,str(SCRIPTS))
import evidence_read as reader
import host_context as host

class RuntimeRoundTwo(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.opts={'index_path':self.root/'index','context_state':self.root/'state','max_return_bytes':2048}
    def test_preserves_final_newline_and_crlf(self):
        p=self.root/'text';text='a\r\nb\r\n';p.write_bytes(text.encode())
        self.assertEqual(reader.read_evidence(p,**self.opts)['content'],text)
    def test_line_range_preserves_ending(self):
        p=self.root/'text';p.write_bytes(b'a\nb\nc\n')
        self.assertEqual(reader.read_evidence(p,start=2,end=2,**self.opts)['content'],'b\n')
    def test_zero_start_rejected(self):
        p=self.root/'text';p.write_text('x')
        with self.assertRaises(ValueError):reader.read_evidence(p,start=0,**self.opts)
    def test_long_line_memory_is_bounded(self):
        p=self.root/'long';p.write_bytes(b'x'*(8*1024*1024))
        tracemalloc.start()
        try:
            reader.read_evidence(p,**self.opts)
            _,peak=tracemalloc.get_traced_memory()
        finally:tracemalloc.stop()
        self.assertLess(peak,1024*1024)
    def test_line_range_across_chunk_boundary(self):
        p=self.root/'big';text=('x'*65534)+'\r\n'+'KEEP\r\n'+'last';p.write_bytes(text.encode())
        self.assertEqual(reader.read_evidence(p,start=2,end=2,**self.opts)['content'],'KEEP\r\n')
    def test_claude_terminal_aggregate_not_double_counted(self):
        p=self.root/'trace';p.write_text('\n'.join(json.dumps(r) for r in [
            {'message':{'id':'m1','usage':{'input_tokens':10,'output_tokens':2}}},
            {'type':'result','usage':{'input_tokens':10,'output_tokens':2},'total_cost_usd':.03}]))
        r=host.parse_jsonl(p);self.assertEqual(r['input_tokens'],10);self.assertEqual(r['cost_usd'],.03)
    def test_embedded_unrelated_usage_ignored(self):
        self.assertFalse(host.normalize({'untrusted':{'usage':{'input_tokens':999}}})['available'])
        p=self.root/'trace';p.write_text(json.dumps({'tool_output':{'usage':{'input_tokens':999}}}))
        self.assertNotIn('input_tokens',host.parse_jsonl(p))
    def test_reasoning_output_not_added_to_output(self):
        r=host.normalize({'output_tokens':100,'output_tokens_details':{'reasoning_tokens':80}})
        self.assertEqual(r['output_tokens'],100);self.assertEqual(r['reasoning_output_tokens'],80)
    def test_string_false_is_not_capability(self):
        r=host.normalize({'capabilities':{'isolated_context':'false'}})
        self.assertFalse(r['capabilities']['isolated_context'])
    def test_old_transcript_does_not_become_fresh(self):
        p=self.root/'trace';p.write_text(json.dumps({'usage':{'input_tokens':1}}));os.utime(p,(1,1))
        self.assertTrue(host.parse_jsonl(p)['observed_at'].startswith('1970-'))

if __name__=='__main__':unittest.main()
