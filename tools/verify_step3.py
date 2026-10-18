"""Capture or verify fixed-clock CLI observations; uses only Python stdlib."""
import argparse
import json
import os
from pathlib import Path
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('binary', type=Path)
parser.add_argument('preload', type=Path)
parser.add_argument('fixtures', type=Path)
args = parser.parse_args()
env = dict(os.environ, LD_PRELOAD=str(args.preload.resolve()))
for fixture in sorted(args.fixtures.glob('*.json')):
    if fixture.name == 'uncontrolled.json':
        continue
    data = json.loads(fixture.read_text())
    expected = data['runs'][0]
    for repetition in range(3):
        run = subprocess.run(
            [str(args.binary.resolve()), *data['argv'][1:]],
            input=data['stdin'], text=True, capture_output=True,
            env=env, timeout=5,
        )
        actual = dict(returncode=run.returncode, stdout=run.stdout, stderr=run.stderr)
        if actual != expected:
            raise SystemExit(f'{fixture.name}: mismatch on repetition {repetition + 1}')
    print(f'{fixture.name}: 3 exact matches')
