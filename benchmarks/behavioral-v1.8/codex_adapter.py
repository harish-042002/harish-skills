#!/usr/bin/env python3
"""Native Codex adapter. Run through run_comparison.py in a disposable host.
Reports provider/CLI token usage; dollar costs, when requested, are estimates.
Never embeds an API key in arguments, output, or result files.
"""
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys


def normalized_usage(events):
    usage = None
    calls = set()
    failed = False
    for event in events:
        if not isinstance(event, dict):
            continue
        if event.get('type') == 'turn.completed' and isinstance(event.get('usage'), dict):
            usage = event['usage']
        if event.get('type') in {'turn.failed', 'error'}:
            failed = True
        item = event.get('item', {})
        if isinstance(item, dict) and event.get('type') == 'item.completed' and item.get('type') in {'command_execution','mcp_tool_call','web_search','file_change'}:
            calls.add(item.get('id', json.dumps(item, sort_keys=True)))
    out = {'tool_calls':len(calls)}
    if usage is not None:
        for source,target in [('input_tokens','input_tokens'),('cached_input_tokens','cache_read_tokens'),
                              ('output_tokens','output_tokens'),('reasoning_output_tokens','reasoning_output_tokens')]:
            val=usage.get(source)
            if isinstance(val,(int,float)) and not isinstance(val,bool) and math.isfinite(val) and val>=0:
                out[target]=val
    return out,failed


def estimate_cost(usage, rates):
    # Codex input includes cached input; reasoning is already in output.
    keys=('input_usd_per_million','cached_input_usd_per_million','output_usd_per_million')
    for key in keys:
        val=rates.get(key)
        if not isinstance(val,(int,float)) or isinstance(val,bool) or not math.isfinite(val) or val<0:
            raise ValueError('invalid/missing rate: '+key)
    if not all(key in usage for key in ('input_tokens','cache_read_tokens','output_tokens')):
        return None
    if usage['cache_read_tokens']>usage['input_tokens']:
        raise ValueError('cached input cannot exceed total input for this adapter')
    return ((usage['input_tokens']-usage['cache_read_tokens'])*rates[keys[0]]+
            usage['cache_read_tokens']*rates[keys[1]]+usage['output_tokens']*rates[keys[2]])/1e6


def prompt_from_transcript(rows):
    out=[]
    for row in rows:
        if row['role']=='developer':
            out.append('User requirement:\n'+row['content'])
        else:
            # Previous raw JSON is retained in artifacts, not replayed as model context.
            messages=[]
            for line in row['content'].splitlines():
                try:
                    e=json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(e, dict):
                    continue
                item=e.get('item',{})
                if isinstance(item, dict) and e.get('type')=='item.completed' and item.get('type')=='agent_message':
                    messages.append(item.get('text',''))
            if messages:
                out.append('Previous response (may be superseded):\n'+'\n'.join(messages))
    out.append('Apply the latest requirements to the current workspace. Verify the result. Do not deploy, contact AWS, or modify the independent verifier.')
    return '\n\n'.join(out)


def main():
    cli=os.environ.get('PLAT_EVAL_CODEX_EXECUTABLE') or shutil.which('codex')
    if not cli:
        print('BLOCKED: Codex CLI not installed',file=sys.stderr);return 2
    model=os.environ.get('PLAT_EVAL_MODEL')
    effort=os.environ.get('PLAT_EVAL_EFFORT')
    if not model or not effort:
        print('BLOCKED: exact model and effort required',file=sys.stderr);return 2
    rows=json.loads(Path(os.environ['PLAT_EVAL_TRANSCRIPT_FILE']).read_text())
    command=[cli,'exec','--json','--ephemeral','--sandbox','workspace-write','--model',model,
             '-c','model_reasoning_effort='+json.dumps(effort),'-']
    # Same process group as the outer bounded harness, so its timeout reaps both.
    proc=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=None,text=True)
    proc.stdin.write(prompt_from_transcript(rows));proc.stdin.close()
    events=[]
    for line in proc.stdout:
        print(line,end='',flush=True)
        try:
            event=json.loads(line)
            # Keep only usage and compact item metadata, never entire tool responses.
            if isinstance(event,dict):
                if event.get('type') in {'turn.completed','turn.failed','error'}:
                    events.append(event)
                elif event.get('type')=='item.completed':
                    item=event.get('item',{})
                    if isinstance(item, dict):
                        events.append({'type':'item.completed','item':{k:item[k] for k in ('id','type') if k in item}})
        except json.JSONDecodeError:
            pass
    code=proc.wait()
    usage,failed=normalized_usage(events)
    usage.update(model_requested=model,effort_requested=effort,kind='native_codex_usage',
                 billing_note='No actual invoice amount. Optional costs are rate-table estimates.')
    if os.environ.get('PLAT_EVAL_RATES'):
        rates=json.loads(Path(os.environ['PLAT_EVAL_RATES']).read_text())
        if rates.get('model')!=model:
            raise ValueError('rate table model does not match requested model')
        value=estimate_cost(usage,rates)
        if value is not None:usage['estimated_cost_usd']=value
    Path(os.environ['PLAT_EVAL_RESULT_FILE']).write_text(json.dumps(usage,indent=2,allow_nan=False))
    return code or (1 if failed else 0)

if __name__=='__main__':raise SystemExit(main())
