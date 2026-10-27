"""Run pinned REA CLI operations and retain complete outputs, including failures."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

parser = argparse.ArgumentParser()
parser.add_argument('cli', type=Path)
parser.add_argument('binary', type=Path)
parser.add_argument('output', type=Path)
parser.add_argument('--playable', action='store_true', help='Also inspect direct dig/win dependencies')
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)
binary = args.binary.resolve()
identity = {'path': str(binary), 'sha256': hashlib.sha256(binary.read_bytes()).hexdigest()}
(args.output / 'target.json').write_text(json.dumps(identity, indent=2) + '\n')
operations = [
    ('version', ['--version']),
    ('doctor', ['doctor', '--provider', 'ghidra', '--json']),
    ('overview', ['analyze', str(binary), '--provider', 'ghidra', '--json']),
    ('flag', ['decompile', str(binary), 'msw_flag', '--provider', 'ghidra', '--json']),
    ('unflag', ['decompile', str(binary), 'msw_unflag', '--provider', 'ghidra', '--json']),
    *[(name, ['decompile', str(binary), name, '--provider', 'ghidra', '--json'])
      for name in ['msw_get_visible', 'msw_set_visible', 'msw_set_visible_noundo',
                   'msw_index', 'msw_init', 'run_game']],
]
if args.playable:
    operations += [(name, ['decompile', str(binary), name, '--provider', 'ghidra', '--json'])
                   for name in ['msw_dig', 'msw_won', 'msw_in_bounds', 'msw_get_grid',
                                'msw_initial_grid', 'msw_generate_grid']]
records = []
for name, command_args in operations:
    command = ['node', str(args.cli.resolve()), *command_args]
    started = time.time()
    stdout_path = args.output / (name + '.stdout.json')
    stderr_path = args.output / (name + '.stderr.txt')
    with stdout_path.open('w') as stdout, stderr_path.open('w') as stderr:
        try:
            result = subprocess.run(command, stdout=stdout, stderr=stderr, timeout=420)
            code = result.returncode
        except subprocess.TimeoutExpired:
            code = 124
    record = {'name': name, 'command': command, 'returncode': code,
              'started_epoch': started, 'elapsed_seconds': time.time() - started}
    records.append(record)
    (args.output / 'commands.json').write_text(json.dumps(records, indent=2) + '\n')
    print(f'{name}: exit {code}', flush=True)
    # Keep focused decompilation visible in job logs for remote review.
    if command_args[0] == 'decompile' or code:
        content = stdout_path.read_text()
        print(content[:40000], flush=True)
        if len(content) > 40000:
            print('Log preview truncated; complete output is in the artifact.', flush=True)
        print(stderr_path.read_text()[:6000], flush=True)
    if code:
        sys.exit(code if 0 < code < 126 else 1)
