"""Capture six synthetic native cases, repeat them, and retain raw observations."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('binary', type=Path)
parser.add_argument('output', type=Path)
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)
# Expected outcomes are explicit acceptance examples, not a second implementation.
cases = [
    ('flag-success', '#F1###', 'f 1 2\n', [(0, '#F1##F', 2)]),
    ('flag-already-flagged', '#F1###', 'f 0 1\n', [(2, '#F1###', 1)]),
    ('flag-revealed', '#F1###', 'f 0 2\n', [(2, '#F1###', 1)]),
    ('unflag-success', '#F1###', 'u 0 1\n', [(0, '##1###', 0)]),
    ('unflag-unflagged', '#F1###', 'u 1 0\n', [(8, '#F1###', 1)]),
    ('repeated-sequence', '######', 'f 0 0\nf 0 0\nu 0 0\nu 0 0\nf 1 2\nu 1 2\n',
     [(0, 'F#####', 1), (2, 'F#####', 1), (0, '######', 0),
      (8, '######', 0), (0, '#####F', 1), (0, '######', 0)]),
]
identity = {'binary': str(args.binary.resolve()),
            'sha256': hashlib.sha256(args.binary.read_bytes()).hexdigest()}
for name, setup, commands, expected in cases:
    runs = []
    for repetition in range(3):
        run = subprocess.run([str(args.binary.resolve()), setup], input=commands,
                             text=True, capture_output=True, timeout=5)
        if run.returncode or run.stderr:
            raise RuntimeError((name, run.returncode, run.stderr))
        observations = [json.loads(line) for line in run.stdout.splitlines()]
        initial = observations[0]['initialized']
        assert initial == dict(rows=2, columns=3, mines=1, visible='######', flags=0,
                               generation=1, undo_index=0, undo_enabled=False, grid_initialized=False)
        assert observations[0]['setup']['visible'] == setup
        assert len(observations) == len(expected) + 1
        for index, (record, (result, visible, flags)) in enumerate(zip(observations[1:], expected)):
            assert (record['result'], record['after']['visible'], record['after']['flags']) == (result, visible, flags), name
            assert record['before'] == (observations[0]['setup'] if index == 0 else observations[index]['after'])
            for key in ['rows', 'columns', 'mines', 'generation', 'undo_index', 'undo_enabled', 'grid_initialized']:
                assert record['before'][key] == record['after'][key], (name, key)
            if result:
                assert record['before'] == record['after'], name
        runs.append(dict(returncode=run.returncode, stdout=run.stdout, stderr=run.stderr))
    assert all(run == runs[0] for run in runs), name
    fixture = dict(case=name, setup_kind='synthetic-visible-state', setup=setup,
                   stdin=commands, target=identity, repetitions=3, runs=runs)
    (args.output / (name + '.json')).write_text(json.dumps(fixture, indent=2) + '\n')
    print(name + ': three identical runs, explicit state/result checks passed')
    print('ORACLE_FIXTURE ' + json.dumps(fixture, separators=(',', ':')))
