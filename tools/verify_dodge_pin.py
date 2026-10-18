"""Verify the exact DODGE checkout and source bytes; this is not game validation."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('checkout', type=Path)
parser.add_argument('--manifest', type=Path, default=Path(__file__).resolve().parents[1] / 'spec' / 'dodge-pin.json')
args = parser.parse_args()
manifest = json.loads(args.manifest.read_text())
checkout = args.checkout.resolve()
head = subprocess.check_output(['git', '-C', str(checkout), 'rev-parse', 'HEAD'], text=True).strip()
if head != manifest['commit']:
    raise SystemExit('DODGE commit mismatch')
if subprocess.check_output(['git', '-C', str(checkout), 'status', '--porcelain'], text=True):
    raise SystemExit('DODGE checkout is not clean')
results = []
for entry in manifest['files']:
    data = (checkout / entry['path']).read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != entry['sha256'] or len(data) != entry['size_bytes']:
        raise SystemExit('DODGE file mismatch: ' + entry['path'])
    if entry['path'].endswith('.json'):
        json.loads(data)
    results.append({'path': entry['path'], 'sha256': digest, 'status': 'pass'})
print(json.dumps({'check': 'dodge-pin-integrity', 'commit': head, 'files': results,
                  'conformance_claim': 'none'}, indent=2))
