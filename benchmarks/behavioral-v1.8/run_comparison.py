#!/usr/bin/env python3
"""Rotate no-Plat / v2.3 / candidate tasks. Preflight is free; --run calls the model.
Uses a temporary isolated HOME and CODEX_HOME, retaining only local CLI auth.
Never uploads or records credential files. Not a Windows-tested launcher.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import shlex
import shutil
import subprocess
import sys
import tempfile
import time

from run_behavioral_eval import load_cases, run_case, ROOT
from score_results import summarize


def sha_tree(path):
    h=hashlib.sha256()
    for p in sorted(path.rglob('*')):
        if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc':
            h.update(p.relative_to(path).as_posix().encode()+b'\0'+p.read_bytes())
    return h.hexdigest()


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--model',required=True,help='Exact model ID accepted by your authenticated Codex host')
    ap.add_argument('--effort',required=True,help='Same supported effort for all arms')
    ap.add_argument('--baseline',required=True,type=Path,help='Frozen v2.3 plat skill directory')
    ap.add_argument('--candidate',type=Path,default=ROOT.parents[1]/'skills/plat')
    ap.add_argument('--repetitions',type=int,default=3)
    ap.add_argument('--timeout',type=float,default=180,help='Per-task total agent deadline; verifier up to 30s extra')
    ap.add_argument('--case',action='append',default=[])
    ap.add_argument('--output',type=Path,default=Path('comparison-results'))
    ap.add_argument('--rates',type=Path,help='Optional explicit current rate table. Produces ESTIMATES, not actual charges.')
    ap.add_argument('--run',action='store_true',help='Actually invoke authenticated model; may consume paid usage')
    a=ap.parse_args()
    if a.repetitions<1 or a.timeout<=0:ap.error('positive repetitions and timeout required')
    a.output.mkdir(parents=True,exist_ok=True)
    cli=shutil.which('codex')
    auth=Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex')))/'auth.json'
    blockers=[]
    if not cli:blockers.append('Codex CLI is not installed in this environment')
    if not auth.is_file() and not os.environ.get('CODEX_API_KEY'):
        blockers.append('No local Codex auth.json or process-scoped CODEX_API_KEY is available')
    for label,path in [('baseline',a.baseline),('candidate',a.candidate)]:
        if not (path/'SKILL.md').is_file():blockers.append(label+' skill directory is missing')
    if cli:
        help_result=subprocess.run([cli,'exec','--help'],capture_output=True,text=True,timeout=10)
        if help_result.returncode!=0 or any(flag not in help_result.stdout for flag in ('--json','--sandbox','--ephemeral','--model')):
            blockers.append('Installed Codex CLI does not expose required benchmark flags')
    preflight={'kind':'live_model_preflight','model_requested':a.model,'effort_requested':a.effort,
               'live_model_calls':0,'blockers':blockers,'run_requested':a.run,
               'actual_cost_usd':None,'planned_arms':['no-plat','v2.3','candidate']}
    (a.output/'preflight.json').write_text(json.dumps(preflight,indent=2))
    if blockers:
        print(json.dumps(preflight,indent=2));return 2
    if not a.run:
        print('Preflight passed. No model invoked. Add --run to start the controlled comparison.');return 0
    cases=load_cases(ROOT/'cases.json')
    if a.case:
        unknown=set(a.case)-{c['id'] for c in cases}
        if unknown:ap.error('unknown case(s): '+','.join(sorted(unknown)))
        cases=[c for c in cases if c['id'] in set(a.case)]
    version=subprocess.run([cli,'--version'],capture_output=True,text=True,timeout=10).stdout.strip()
    metadata={'kind':'native_agent_comparison','model_requested':a.model,'effort_requested':a.effort,
              'cli_version':version,'baseline_sha256':sha_tree(a.baseline),'candidate_sha256':sha_tree(a.candidate),
              'task_pack_sha256':sha_tree(ROOT/'fixtures'),'session_semantics':'fresh process per user turn; workspace persists; user history and final responses supplied',
              'cache_state':'not controlled by provider; order rotated','actual_cost_usd':None}
    plans=[(rep,c) for rep in range(1,a.repetitions+1) for c in cases]
    results=[]
    old_env=os.environ.copy()
    with tempfile.TemporaryDirectory(prefix='plat-benchmark-private-') as td:
        home=Path(td);codex_home=home/'.codex';codex_home.mkdir(mode=0o700)
        if auth.is_file():
            shutil.copyfile(auth,codex_home/'auth.json');(codex_home/'auth.json').chmod(0o600)
        os.environ.update(HOME=str(home),CODEX_HOME=str(codex_home),PLAT_EVAL_CODEX_EXECUTABLE=cli,
                          PLAT_EVAL_MODEL=a.model,PLAT_EVAL_EFFORT=a.effort)
        if a.rates:os.environ['PLAT_EVAL_RATES']=str(a.rates.resolve())
        adapter=shlex.join([sys.executable,str(ROOT/'codex_adapter.py')])
        try:
            for pos,(rep,case) in enumerate(plans):
                arms=['no-plat','v2.3','candidate'];arms=arms[pos%3:]+arms[:pos%3]
                for arm in arms:
                    skill=None if arm=='no-plat' else (a.baseline if arm=='v2.3' else a.candidate)
                    activation=('Use the installed Plat skill for every engineering request.\n' if arm=='v2.3' else
                                'For obvious, local, reversible edits, work directly and verify the result without loading Plat unless explicitly requested. Use the installed Plat skill for non-trivial engineering work, unresolved risk, or multi-step changes.\n')
                    row=run_case(case,adapter,arm,rep,a.timeout,artifacts=a.output/'artifacts',skill_path=skill,
                                 activation=activation,metadata=metadata)
                    results.append(row)
                    payload={'schema_version':1,'metadata':metadata,'results':results,'summary':summarize(results)}
                    target=a.output/'results.json';temp=target.with_suffix('.tmp');temp.write_text(json.dumps(payload,indent=2,allow_nan=False));temp.replace(target)
                    print(arm,case['id'],rep,'PASS' if row['passed'] else 'FAIL',row['wall_seconds'],flush=True)
                    # Don't burn through all tasks when authentication/provider setup is broken.
                    if not row['telemetry'].get('input_tokens') and row['agent_failures']:
                        print('Stopped: failed run has no reported model usage. Inspect retained logs.');return 2
        finally:
            os.environ.clear();os.environ.update(old_env)
    return 0 if all(x['passed'] for x in results) else 1

if __name__=='__main__':raise SystemExit(main())
