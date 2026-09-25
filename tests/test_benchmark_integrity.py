"""Harness tests use scripted edits, NOT model trajectories or cost measurements."""
import importlib.util
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / 'benchmarks/behavioral-v1.8'

def load(name, path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod

class BenchmarkIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runner=load('benchmark_hardened',BENCH/'run_behavioral_eval.py')
        cls.scorer=load('score_hardened',BENCH/'score_results.py')
        cls.cases=cls.runner.load_cases(BENCH/'cases.json')
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup); self.root=Path(self.tmp.name)
    def case(self,name):
        return next(x for x in self.cases if x['id']==name)
    def scripted(self,source,*,name='tiny-timeout-only',timeout=5):
        script=self.root/'adapter.py';script.write_text(source)
        return self.runner.run_case(self.case(name),shlex.join([sys.executable,str(script)]),'fixture-only',1,timeout,
                                    artifacts=self.root/'artifacts',metadata={'kind':'scripted_fixture_test','model_calls':0})
    def verify(self,fixture,edits):
        dest=self.root/'workspace';shutil.copytree(BENCH/'fixtures'/fixture,dest)
        for path,content in edits.items(): (dest/path).write_text(content)
        env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1'
        return subprocess.run([sys.executable,'verify.py'],cwd=dest,env=env,capture_output=True,timeout=10)
    def test_missing_cost_is_not_zero(self):
        rows=[{'condition':'c','passed':True,'wall_seconds':1,'telemetry':{'cost_usd':10}},
              {'condition':'c','passed':False,'wall_seconds':2,'telemetry':{}}]
        s=self.scorer.summarize(rows)['c']
        self.assertEqual(s['mean_telemetry']['cost_usd'],10)
        self.assertFalse(s['telemetry_coverage']['cost_usd']['complete'])
    def test_invalid_telemetry_rejected(self):
        p=self.root/'t.json';p.write_text('{"cost_usd": NaN, "input_tokens": -1, "output_tokens": true, "arbitrary": 9}')
        self.assertEqual(self.runner.numeric_telemetry(p),{})
    def test_non_object_telemetry_safe(self):
        p=self.root/'t.json';p.write_text('[]');self.assertEqual(self.runner.numeric_telemetry(p),{})
    def test_untracked_scope_violation_rejected(self):
        r=self.scripted("from pathlib import Path\nPath('config.py').write_text('TIMEOUT_SECONDS = 30\\nRETRIES = 3\\n')\nPath('surprise.py').write_text('telemetry = True\\n')\n")
        self.assertFalse(r['passed']);self.assertIn('surprise.py',r['unexpected_changed_files'])
    def test_git_commit_does_not_hide_changes(self):
        r=self.scripted("from pathlib import Path\nimport subprocess\nPath('config.py').write_text('TIMEOUT_SECONDS = 30\\nRETRIES = 3\\n')\nPath('surprise.py').write_text('bad=1\\n')\nsubprocess.run(['git','add','.'],check=True)\nsubprocess.run(['git','commit','-qm','hide'],check=True)\n")
        self.assertFalse(r['passed']);self.assertIn('surprise.py',r['unexpected_changed_files'])
    def test_verifier_modification_rejected(self):
        r=self.scripted("from pathlib import Path\nPath('verify.py').write_text('print(\\\"pass\\\")\\n')\n")
        self.assertFalse(r['passed']);self.assertFalse(r['verifier_intact'])
    def test_timeout_is_result_not_exception(self):
        r=self.scripted('import time\ntime.sleep(20)\n',timeout=.15)
        self.assertFalse(r['passed']);self.assertEqual(r['agent_failures'][0]['returncode'],124)
    def test_failed_attempt_cost_is_retained(self):
        r=self.scripted("import json,os\nfrom pathlib import Path\nPath(os.environ['PLAT_EVAL_RESULT_FILE']).write_text(json.dumps({'cost_usd':2.5}))\nraise SystemExit(7)\n")
        self.assertFalse(r['passed']);self.assertEqual(r['telemetry']['cost_usd'],2.5)
    def test_correct_edit_and_raw_logs_retained(self):
        r=self.scripted("from pathlib import Path\nprint('raw marker')\nPath('config.py').write_text('TIMEOUT_SECONDS = 30\\nRETRIES = 3\\n')\n")
        self.assertTrue(r['passed']);self.assertIn('raw marker',(Path(r['artifacts'])/'agent-1.stdout').read_text())
    def test_noop_idempotency_cannot_pass(self):
        r=self.verify('aws-sqs-idempotency',{'handler.py':"# store.claim(\nsent=[]\ndef lambda_handler(event,context=None):\n    return {'batchItemFailures': []}\n"})
        self.assertNotEqual(r.returncode,0)
    def test_durable_idempotency_reference_passes(self):
        r=self.verify('aws-sqs-idempotency',{'handler.py':"import store\nsent=[]\ndef lambda_handler(event,context=None):\n    for record in event['Records']:\n        if store.claim(record['messageId']):\n            sent.append(record['body'])\n    return {'batchItemFailures': []}\n"})
        self.assertEqual(r.returncode,0,r.stderr)
    def test_deploy_keyword_comments_do_not_pass(self):
        r=self.verify('aws-deploy-guard',{'deploy.sh':'#!/bin/bash\n# aws sts get-caller-identity EXPECTED_AWS_ACCOUNT_ID AWS_REGION cloudformation deploy\nexit 0\n'})
        self.assertNotEqual(r.returncode,0)
    def test_guarded_deploy_reference_passes_fake_cli(self):
        r=self.verify('aws-deploy-guard',{'deploy.sh':'''#!/usr/bin/env bash
set -euo pipefail
: "${EXPECTED_AWS_ACCOUNT_ID:?expected account required}"
: "${AWS_REGION:?region required}"
actual=$(aws sts get-caller-identity --query Account --output text --region "$AWS_REGION")
[[ "$actual" == "$EXPECTED_AWS_ACCOUNT_ID" ]] || exit 1
aws cloudformation deploy --stack-name app --template-file template.yml --region "$AWS_REGION"
'''})
        self.assertEqual(r.returncode,0,r.stderr)
    def test_iam_keyword_comments_do_not_pass(self):
        old=(BENCH/'fixtures/aws-iam-least-privilege/template.yaml').read_text()
        malicious=old.replace("Action: '*'",'Action: ["*"]').replace("Resource: '*'",'Resource: ["*"]')+'\n# s3:GetObject arn:aws:s3:::my-bucket/assets/*\n'
        self.assertNotEqual(self.verify('aws-iam-least-privilege',{'template.yaml':malicious}).returncode,0)
    def test_iam_minimum_policy_passes(self):
        old=(BENCH/'fixtures/aws-iam-least-privilege/template.yaml').read_text()
        valid=old.replace("Action: '*'",'Action: s3:GetObject').replace("Resource: '*'",'Resource: arn:aws:s3:::my-bucket/assets/*')
        r=self.verify('aws-iam-least-privilege',{'template.yaml':valid});self.assertEqual(r.returncode,0,r.stderr)
    def test_manifest_follows_no_external_symlink(self):
        work=self.root/'work';work.mkdir();(work/'escape').symlink_to(self.root,target_is_directory=True)
        self.assertEqual(set(self.runner.manifest(work)),{'escape'})
    def test_unknown_cost_remains_missing(self):
        r=self.scripted("from pathlib import Path\nPath('config.py').write_text('TIMEOUT_SECONDS = 30\\nRETRIES = 3\\n')\n")
        self.assertNotIn('cost_usd',r['telemetry'])

if __name__=='__main__':unittest.main()
