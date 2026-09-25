import bz2
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import urllib.request

BASE = '8aae2f2efefc30bc8695d8f3c24fd4806ac06061'
REPO = 'harish-042002/harish-skills'
PATCH_SHA = 'a4c97e3f360d4055502f637b49b929dfe5cb4a10e909c0c21e2c8e4142d989a0'
TREE_DIGEST = '53d43bc7dadf05cb4981a62d4d20c19d8420c8d7c653767ca52a1588ec8cf148'

def run(args):
    subprocess.run(args, check=True, timeout=300)

def output(args):
    return subprocess.check_output(args, text=True, timeout=30).strip()

def replace_once(text, old, new):
    if text.count(old) != 1:
        raise RuntimeError('Expected exactly one release metadata anchor: ' + old[:80])
    return text.replace(old, new, 1)

def api(path, payload=None):
    body = None if payload is None else json.dumps(payload).encode()
    request = urllib.request.Request('https://api.github.com/repos/' + REPO + path, data=body,
        headers={'Authorization': 'Bearer ' + os.environ['GH_TOKEN'],
                 'Accept': 'application/vnd.github+json', 'Content-Type': 'application/json',
                 'X-GitHub-Api-Version': '2022-11-28'})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)

def skill_digest():
    root = Path('skills/plat')
    digest = hashlib.sha256()
    for path in sorted(root.rglob('*')):
        if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc':
            digest.update(path.relative_to(root).as_posix().encode() + b'\0' + path.read_bytes() + b'\0')
    return digest.hexdigest()

raw = b''.join((Path('.plat-publish') / f'part-{i:02}').read_bytes() for i in range(6))
assert hashlib.sha256(raw).hexdigest() == '98c812c320f049b04604a30dbb4e3bd11a9f1727877dd10fcac1b29612d9da9d'
patch = bz2.decompress(raw)
assert hashlib.sha256(patch).hexdigest() == PATCH_SHA
assert api('/git/ref/heads/main')['object']['sha'] == BASE, 'main advanced; do not overwrite'
patch_path = Path(tempfile.gettempdir()) / 'plat-verified-rc2.patch'
patch_path.write_bytes(patch)
run(['git', 'switch', '--detach', BASE])
run(['git', 'apply', '--check', str(patch_path)])
run(['git', 'apply', '--index', str(patch_path)])
assert skill_digest() == TREE_DIGEST

release = Path('.github/workflows/release-plat.yml')
text = release.read_text()
text = replace_once(text, '      - name: Validate Plat\n',
    '      - uses: actions/setup-python@v5\n        with:\n          python-version: "3.12"\n\n'
    '      - name: Evaluation dependencies\n        run: python -m pip install -r benchmarks/requirements.txt\n\n'
    '      - name: Validate Plat\n')
start = text.index('          ## Highlights\n')
end = text.index('          The release asset', start)
text = text[:start] + '''          ## Highlights

          - Minimal ordinary execution; deeper runtime helpers remain optional.
          - Context occupancy is separate from cumulative cache and read traffic.
          - Lossless evidence continuation, complete binding constraints, and bounded optional commands.
          - Corrected usage accounting and independent benchmark verifiers.
          - 166 local regression tests and runtime-helper timings; no verified end-to-end model cost or speed gain.
          - Version 2.4.0-rc.2 is a benchmark candidate, not a stable-quality certification.

''' + text[end:]
text = replace_once(text, '          if gh release view "$TAG"',
    '          RELEASE_FLAGS=()\n          if [[ "$VERSION" == *-* ]]; then\n'
    '            RELEASE_FLAGS+=(--prerelease)\n          fi\n\n'
    '          if gh release view "$TAG"')
text = replace_once(text, 'gh release edit "$TAG" --title',
    'gh release edit "$TAG" "${RELEASE_FLAGS[@]}" --title')
text = replace_once(text, 'gh release create "$TAG" skill.zip SHA256SUMS.txt',
    'gh release create "$TAG" skill.zip SHA256SUMS.txt "${RELEASE_FLAGS[@]}"')
release.write_text(text)

readme = Path('README.md')
text = readme.read_text()
text = replace_once(text, '**v2.3.0', '**v2.4.0-rc.2')
text = text.replace('## Install\n',
    '> **Benchmark candidate:** main carries 2.4.0-rc.2. Runtime regressions are tested; live model speed/cost improvements remain unverified. Stable-release update checks may still report v2.3.0; benchmark a pinned main commit.\n\n## Install\n', 1)
readme.write_text(text)
evidence = Path('docs/maintenance-evidence.json')
data = json.loads(evidence.read_text())
latest = data['entries'][-1]
assert latest['id'] == '2026-09-25-v2.4-rc2-runtime-benchmark-integrity'
latest['material_files'].append(str(release))
latest['adopted'].append('Publish unchanged rc2 skill to main; install evaluation dependencies in release CI and mark prerelease tags accurately.')
evidence.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
log = Path('docs/RESEARCH_LOG.md')
log.write_text(log.read_text() + '\nPublication note for 2026-09-25-v2.4-rc2-runtime-benchmark-integrity: the skill bytes remain unchanged. Release CI now installs the evaluation dependency and labels prereleases; main documentation identifies rc2 as an unproven live-performance candidate.\n')
run(['git', 'add', str(release), str(readme), str(evidence), str(log)])
run(['git', '-c', 'user.name=Plat release preparation', '-c', 'user.email=plat-release@users.noreply.github.com',
     'commit', '-m', 'fix: publish Plat 2.4.0-rc.2 runtime and benchmark integrity fixes'])
run([sys.executable, '-m', 'pip', 'install', '-r', 'benchmarks/requirements.txt'])
run([sys.executable, 'scripts/validate_plat.py'])
run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_*.py'])
run([sys.executable, '-m', 'compileall', '-q', 'scripts', 'skills/plat/scripts', 'tests', 'benchmarks'])
run(['bash', '-n', 'install.sh'])
run([sys.executable, 'scripts/maintenance_gate.py', '--base-ref', BASE])
run(['git', 'diff', '--check', BASE, 'HEAD'])
assert skill_digest() == TREE_DIGEST
assert not output(['git', 'status', '--porcelain', '--untracked-files=no'])
paths = output(['git', 'diff', '--name-only', BASE, 'HEAD']).splitlines()
assert len(paths) == 44, paths
assert not any(p.startswith('.plat-publish/') or p.endswith('prepare-plat-rc2.yml') for p in paths)
entries = []
for path in paths:
    mode = output(['git', 'ls-files', '-s', '--', path]).split()[0]
    entries.append({'path': path, 'mode': mode, 'type': 'blob', 'content': Path(path).read_text()})
assert api('/git/ref/heads/main')['object']['sha'] == BASE, 'main advanced during validation'
tree = api('/git/trees', {'base_tree': '180addfccc08ec1eb4bf34a327469bca46011fa2', 'tree': entries})
assert tree['sha'] == output(['git', 'rev-parse', 'HEAD^{tree}']), 'Remote tree differs from validated tree'
commit = api('/git/commits', {'message': 'fix: publish Plat 2.4.0-rc.2 runtime and benchmark integrity fixes\n\n166 regression tests; unchanged candidate skill. End-to-end model speed/cost remains unverified. Correct release dependency and prerelease metadata.', 'tree': tree['sha'], 'parents': [BASE]})
manifest = {'commit': commit['sha'], 'tree': tree['sha'], 'base': BASE, 'version': '2.4.0-rc.2',
            'skill_digest': TREE_DIGEST, 'files': paths, 'validation': 'all gates passed', 'main_updated': False}
Path('publish-manifest.json').write_text(json.dumps(manifest, indent=2))
print('PREPARED_COMMIT=' + commit['sha'], flush=True)
with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as report:
    report.write('Validated rc2 commit prepared (main not moved): `' + commit['sha'] + '`\n')
