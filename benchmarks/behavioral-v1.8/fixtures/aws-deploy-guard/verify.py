"""Exercise fail-closed behavior against a fake AWS CLI. Never contacts AWS."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

with tempfile.TemporaryDirectory(prefix='plat-fake-aws-') as td:
    root = Path(td)
    aws = root / 'aws'
    aws.write_text('#!' + sys.executable + '\n' + '''import json, os, sys
from pathlib import Path
args = sys.argv[1:]
with Path(os.environ['FAKE_AWS_CALLS']).open('a') as out:
    out.write(json.dumps(args) + '\\n')
if args[:2] == ['sts', 'get-caller-identity']:
    if os.environ.get('FAKE_STS_FAIL') == '1':
        raise SystemExit(23)
    account = os.environ['FAKE_ACCOUNT']
    print(account if '--query' in args and 'Account' in args else json.dumps({'Account': account}))
elif args[:2] == ['cloudformation', 'deploy']:
    pass
else:
    raise SystemExit(24)
''')
    aws.chmod(0o700)
    for name, overrides, valid in [
        ('correct', {}, True),
        ('wrong-account', {'FAKE_ACCOUNT': '222222222222'}, False),
        ('missing-expected-account', {'EXPECTED_AWS_ACCOUNT_ID': None}, False),
        ('missing-region', {'AWS_REGION': None, 'AWS_DEFAULT_REGION': None}, False),
        ('sts-failure', {'FAKE_STS_FAIL': '1'}, False),
    ]:
        calls = root / (name + '.jsonl')
        env = os.environ.copy()
        for key in list(env):
            if key.startswith('AWS_'):
                env.pop(key)
        env.update(PATH=str(root) + os.pathsep + env.get('PATH', ''),
                   FAKE_AWS_CALLS=str(calls), FAKE_ACCOUNT='111111111111',
                   EXPECTED_AWS_ACCOUNT_ID='111111111111', AWS_REGION='eu-west-2',
                   AWS_EC2_METADATA_DISABLED='true')
        for key, value in overrides.items():
            if value is None:
                env.pop(key, None)
            else:
                env[key] = value
        proc = subprocess.run([shutil.which('bash') or 'bash', 'deploy.sh'], env=env,
                              capture_output=True, text=True, timeout=5)
        commands = [json.loads(x) for x in calls.read_text().splitlines()] if calls.exists() else []
        deploys = [x for x in commands if x[:2] == ['cloudformation', 'deploy']]
        if valid:
            assert proc.returncode == 0 and len(deploys) == 1, (name, proc.returncode, commands, proc.stderr)
        else:
            assert proc.returncode != 0 and not deploys, (name, proc.returncode, commands)
print('AWS guard behavior passed (fake CLI; no cloud deployment)')
