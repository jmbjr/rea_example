"""Native-equivalence, replay, CLI and declared authority-perturbation evidence."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'python'))
from assemble_flags import assemble
from build_flags import build
from dodge_common import ValidationError, canonical, digest, file_hash, fixture_records, read_json, require
from flag_adapter import FlagSession

def compare(checkout, output):
    output.mkdir(parents=True, exist_ok=True)
    (output / 'runtime-acceptance.json').unlink(missing_ok=True)
    _, model, validation = build(ROOT, checkout, output / 'baseline')
    cases = []
    for path in sorted((ROOT / 'evidence/step5/oracle').glob('*.json')):
        fixture = read_json(path)
        native = fixture_records(fixture)
        runs = []
        for repetition in range(3):
            session = FlagSession(model, fixture['case'], ROOT)
            require(canonical(session.snapshot()) == canonical(native[0]['setup']), 'initial state differs from oracle')
            observations, traces = [], []
            for command, expected in zip(fixture['stdin'].splitlines(), native[1:]):
                observation = session.command(command)
                require(canonical(observation) == canonical(expected), 'native divergence: ' + fixture['case'])
                observations.append(observation)
                traces.append(deepcopy(session.runtime.trace))
            runs.append(dict(observations=observations, traces=traces))
        require(all(canonical(run) == canonical(runs[0]) for run in runs), 'runtime replay differs')
        # Execute the real CLI. It independently rebuilds through every validation gate.
        cli = subprocess.run([sys.executable, str(ROOT / 'python/run_flags.py'), str(checkout), '--case', fixture['case']],
                             input=fixture['stdin'], capture_output=True, text=True, timeout=30)
        require(cli.returncode == 0 and not cli.stderr, 'CLI failed: ' + cli.stderr)
        cli_records = [json.loads(line) for line in cli.stdout.splitlines()]
        require(canonical(cli_records) == canonical(native[1:]), 'CLI projection diverges from native evidence')
        case = dict(case=fixture['case'], native_fixture_sha256=file_hash(path), repetitions=3,
                    native_target=fixture['target'], runs=runs,
                    cli=dict(returncode=cli.returncode, stdout=cli.stdout, stderr=cli.stderr))
        (output / (fixture['case'] + '.json')).write_text(json.dumps(case, indent=2) + '\n')
        cases.append(dict(case=fixture['case'], actions=len(native)-1, repetitions=3, status='pass', cli='pass'))
    config = read_json(ROOT / 'model/synthetic-setup.json')
    variant_document = assemble(ROOT, synthetic=True)
    _, variant, variant_validation = build(ROOT, checkout, output / 'synthetic', candidate=variant_document)
    require(digest(variant['rules']) == digest(model['rules']), 'perturbation changed recovered rules')
    baseline_session = FlagSession(model, config['base_case'], ROOT)
    synthetic_session = FlagSession(variant, config['scenario_id'], ROOT)
    # The selected coordinate is the changed source cell; not a runtime rule constant.
    base_values = baseline_session.snapshot()['visible']
    changed = [i for i, (old, new) in enumerate(zip(base_values, config['visible'])) if old != new]
    require(len(changed) == 1, 'perturbation must change one input cell')
    row, col = divmod(changed[0], baseline_session.snapshot()['columns'])
    command = f'f {row} {col}'
    old_result = baseline_session.command(command)
    new_result = synthetic_session.command(command)
    require(old_result['result'] == 2 and new_result['result'] == 0, 'authority perturbation did not affect execution')
    perturbation = dict(label='synthetic input variant; not unchanged-native equivalence',
        source='model/synthetic-setup.json', source_sha256=file_hash(ROOT / 'model/synthetic-setup.json'),
        candidate_sha256=variant_validation['candidate_sha256'], resolved_sha256=variant_validation['resolved_sha256'],
        recovered_rules_unchanged=True, command=command, original=old_result, synthetic=new_result)
    (output / 'perturbation.json').write_text(json.dumps(perturbation, indent=2) + '\n')
    # Admission errors must leave state unchanged.
    session = FlagSession(model, config['base_case'], ROOT)
    before = deepcopy(session.runtime.scope)
    try:
        session.command('f 99 99')
    except ValidationError:
        require(canonical(before) == canonical(session.runtime.scope), 'invalid input mutated state')
    else:
        raise AssertionError('out-of-scope input accepted')
    # A schema-valid but altered rule must never reach the executor.
    invalid = assemble(ROOT)
    invalid['rules']['effects']['flag-count']['value'] = 2
    try:
        build(ROOT, checkout, output / 'rejected-before-runtime', candidate=invalid)
    except ValidationError:
        require(not (output / 'rejected-before-runtime/resolved-game.json').exists(), 'failed validation exposed executable model')
    else:
        raise AssertionError('invalid rule passed execution gates')
    summary = dict(status='pass', maturity='G5', cli_projection='shared neutral/runtime semantics; no export-release claim',
        candidate_sha256=validation['candidate_sha256'], resolved_sha256=validation['resolved_sha256'], cases=cases,
        native_action_comparisons=sum(x['actions'] * x['repetitions'] for x in cases),
        cli_action_comparisons=sum(x['actions'] for x in cases), deterministic_replay=True,
        authority_perturbation='pass; coherent synthetic source, validated/resolved again',
        invalid_input_no_mutation='pass', invalid_rule_gated_before_runtime='pass',
        executor_sha256=file_hash(ROOT / 'python/neutral_runtime.py'))
    (output / 'runtime-acceptance.json').write_text(json.dumps(summary, indent=2) + '\n')
    return summary

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dodge_checkout', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    print(json.dumps(compare(args.dodge_checkout.resolve(), args.output.resolve()), indent=2))
