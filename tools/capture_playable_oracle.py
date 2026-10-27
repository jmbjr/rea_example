"""Capture fixed-layout native behavior; no Python transition implementation."""
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

# Setup derivation only. Supplied layouts bypass native random generation.
def grid_from_mines(positions):
    return ''.join('!' if i in positions else str(sum(
        rr * 4 + cc in positions
        for rr in range(max(0, i // 4 - 1), min(4, i // 4 + 2))
        for cc in range(max(0, i % 4 - 1), min(4, i % 4 + 2))
        if (rr, cc) != divmod(i, 4))) for i in range(16))

grid = grid_from_mines({0, 15})
safe_digs = ''.join(f'd {i // 4} {i % 4}\n' for i in range(16) if grid[i] != '!')
cases = [
    ('numbered-cell', 'd 0 1\n'),
    ('empty-expansion', 'd 0 3\n'),
    ('mine-and-raw-post-loss', 'd 0 0\nd 0 1\n'),
    ('flagged-number', 'f 0 1\nd 0 1\nu 0 1\nd 0 1\n'),
    ('flagged-zero', 'f 0 3\nd 0 3\nu 0 3\n'),
    ('expansion-flagged-zero', 'f 1 3\nd 0 3\n'),
    ('expansion-flagged-number', 'f 0 1\nd 0 3\n'),
    ('repeated-number', 'd 0 1\nd 0 1\n'),
    ('win-without-flags', safe_digs),
    ('win-with-flags', 'f 0 0\nf 3 3\n' + safe_digs),
    ('flag-before-dig-initialized', 'f 0 0\nu 0 0\nd 0 1\n'),
    ('dig-bounds', 'd -1 0\nd 4 0\nd 0 4\n'),
    ('raw-post-win', safe_digs + 'f 0 0\nu 0 0\nd 0 0\n'),
]
identity = dict(sha256=hashlib.sha256(args.binary.read_bytes()).hexdigest())
fixtures = []
for name, commands in cases:
    runs = []
    for _ in range(3):
        run = subprocess.run([str(args.binary.resolve()), grid, '#' * 16],
                             input=commands, text=True, capture_output=True, timeout=5)
        if run.returncode or run.stderr:
            raise RuntimeError((name, run.returncode, run.stderr))
        records = [json.loads(line) for line in run.stdout.splitlines()]
        assert len(records) == len(commands.splitlines()) + 1
        assert records[0]['setup']['grid'] == grid
        previous = records[0]['setup']
        for record in records[1:]:
            assert record['before'] == previous
            assert record['after']['grid'] == grid
            for field in ['rows', 'columns', 'mines', 'generation', 'undo_index', 'undo_enabled', 'grid_initialized']:
                assert record['before'][field] == record['after'][field]
            previous = record['after']
        runs.append(dict(returncode=run.returncode, stdout=run.stdout, stderr=run.stderr))
    assert all(r == runs[0] for r in runs)
    fixtures.append(dict(case=name, setup_kind='synthetic-fixed-initialized-layout',
                         grid=grid, visible='#' * 16, stdin=commands, target=identity,
                         repetitions=3, runs=runs))

# Finite evidence assertions, not a duplicate dig/flood/win algorithm.
def actions(name):
    return [json.loads(line) for line in next(f for f in fixtures if f['case'] == name)['runs'][0]['stdout'].splitlines()][1:]
assert actions('numbered-cell')[0]['after']['visible'] == '#1##############'
assert actions('mine-and-raw-post-loss')[0]['result'] == 7
assert actions('mine-and-raw-post-loss')[1]['after']['visible'].startswith('!1')
assert actions('flagged-number')[1]['result'] == 5
assert actions('flagged-number')[1]['before'] == actions('flagged-number')[1]['after']
assert actions('flagged-zero')[1]['result'] == 0
assert actions('flagged-zero')[1]['after']['visible'][3] == '0'
assert actions('flagged-zero')[1]['after']['flags'] == 1
assert actions('flagged-zero')[2]['result'] == 8
assert actions('expansion-flagged-zero')[1]['after']['visible'][7] == '0'
assert actions('expansion-flagged-zero')[1]['after']['flags'] == 1
assert actions('expansion-flagged-number')[1]['after']['visible'][1] == 'F'
assert actions('repeated-number')[1]['before'] == actions('repeated-number')[1]['after']
assert actions('win-without-flags')[-1]['after']['won'] == 1
assert actions('win-without-flags')[-1]['after']['flags'] == 0
assert actions('win-with-flags')[-1]['after']['won'] == 1
assert actions('raw-post-win')[-1]['result'] == 7
assert actions('raw-post-win')[-1]['after']['won'] == 0
assert all(r['result'] == 1 and r['before'] == r['after'] for r in actions('dig-bounds'))
assert actions('flag-before-dig-initialized')[0]['result'] == 0
assert actions('empty-expansion')[0]['after']['visible'] == '#10011000011001#'

for fixture in fixtures:
    (args.output / (fixture['case'] + '.json')).write_text(json.dumps(fixture, indent=2) + '\n')
    print('PLAYABLE_FIXTURE ' + json.dumps(fixture, separators=(',', ':')))
summary = dict(status='pass', cases=len(fixtures), repetitions=3,
               action_observations=sum(len(f['stdin'].splitlines()) * 3 for f in fixtures),
               target=identity, upstream_commit='c7cadf1f7ed57d950b400d965a7d3bbab5e50bed',
               scope='native direct calls; initialized fixed 4x4 layout; undo disabled; raw post-terminal probes')
(args.output / 'acceptance.json').write_text(json.dumps(summary, indent=2) + '\n')
print('PLAYABLE_ACCEPTANCE ' + json.dumps(summary, separators=(',', ':')))
