"""Acceptance of the actual candidate: deterministic resolution and fatal negatives."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import shutil
from assemble_flags import assemble
from build_flags import build
from dodge_common import ValidationError, canonical, read_json, require

parser = argparse.ArgumentParser()
parser.add_argument('dodge_checkout', type=Path)
parser.add_argument('output', type=Path)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
args.output.mkdir(parents=True, exist_ok=True)
(args.output / 'acceptance.json').unlink(missing_ok=True)
candidate = assemble(root)
_, first, positive = build(root, args.dodge_checkout, args.output / 'positive')
_, second, _ = build(root, args.dodge_checkout, args.output / 'repeat')
require(canonical(first) == canonical(second), 'resolution not deterministic')
sc = next(iter(candidate['scenarios']))
scene = candidate['scenarios'][sc]['scene_ref']
negatives = []

def reject(name, stage, edit=None, resolved_edit=None):
    altered = deepcopy(candidate)
    if edit:
        edit(altered)
    output = args.output / ('negative-' + name)
    output.mkdir(exist_ok=True)
    # A stale successful artifact must not survive a rejected rebuild.
    (output / 'resolved-game.json').write_text('stale')
    try:
        build(root, args.dodge_checkout, output, candidate=altered, resolved_edit=resolved_edit)
    except ValidationError:
        report = read_json(output / 'validation-report.json')
        require(report['stages'][-1]['stage'] == stage, name + ': wrong rejection stage')
        require(not (output / 'resolved-game.json').exists(), name + ': failed gate published/survived output')
        negatives.append(dict(case=name, expected_stage=stage, status='pass', rejection=report['error']))
        return
    raise AssertionError(name + ': invalid model accepted')

reject('schema-invalid-quantity', 'G1-schema', lambda d: d['scenes'][scene]['instances'][0].update(quantity=0))
reject('missing-effect', 'G2-core', lambda d: d['rules']['effects'].pop('flag-cell'))
reject('wrong-reference-kind', 'G2-core', lambda d: d['rules']['actions']['flag'].update(procedure_ref='flag-eligible'))
reject('procedure-cycle', 'G2-core', lambda d: d['rules']['procedures']['flag-procedure'].update(steps=[dict(kind='procedure', ref='flag-procedure')]))
reject('duplicate-instance', 'G2-core', lambda d: d['scenes'][scene]['instances'][1].update(id=d['scenes'][scene]['instances'][0]['id']))
reject('source-hash', 'G2-core', lambda d: d['sources']['rea-flag'].update(sha256='0' * 64))
reject('typed-default', 'G2-core', lambda d: d['rules']['values']['flags'].update(default=False))
reject('duplicate-coordinate', 'G3-required-source-profile', lambda d: d['scenarios'][sc]['initial_state'][4].update(value=0))
reject('incoherent-counter', 'G3-required-source-profile', lambda d: next(b for b in d['scenarios'][sc]['initial_state'] if b['ref']=='flags').update(value=4))
reject('undo-enabled', 'G3-required-source-profile', lambda d: next(b for b in d['scenarios'][sc]['initial_state'] if b['ref']=='undo-enabled').update(value=True))
reject('missing-target-context', 'G2-core', lambda d: d['objects']['cell']['invocations'][0].update(subject_bindings=[]))
reject('missing-else', 'G2-core', lambda d: d['rules']['procedures']['flag-procedure']['steps'][0].pop('else_steps'))
reject('missing-result', 'G3-required-source-profile', lambda d: d['rules']['procedures']['flag-procedure']['steps'][0]['branches'][0]['steps'].pop())
reject('changed-delta', 'G3-required-source-profile', lambda d: d['rules']['effects']['flag-count'].update(value=2))
reject('invented-mine-cap', 'G3-required-source-profile', lambda d: d['rules']['values']['flags'].update(maximum=1))
reject('missing-profile', 'G3-required-source-profile', lambda d: d['validation'].update(required_profiles=[]))
reject('profile-version', 'G3-required-source-profile', lambda d: d['validation']['required_profiles'][0].update(version='9'))
reject('validator-missing', 'G2-core', lambda d: d['sources']['flag-profile'].update(uri='tools/does-not-exist.py'))
reject('validator-kind', 'G3-required-source-profile', lambda d: d['sources']['flag-profile'].update(kind='text'))
reject('unsupported-topology', 'G2-core', lambda d: d.update(topologies={}))
reject('wrong-cell-type', 'G2-core', lambda d: d['scenarios'][sc]['initial_state'][2].update(value=1))
reject('lost-binding', 'G2-core', lambda d: d['scenarios'][sc]['initial_state'].pop())
reject('resolved-counter', 'G4-generic-resolved', resolved_edit=lambda r: r['scenarios'][0]['values'].update(flags=4))
reject('resolved-counter-type', 'G4-generic-resolved', resolved_edit=lambda r: r['scenarios'][0]['values'].update(flags=True))
reject('resolved-integer-type', 'G4-generic-resolved', resolved_edit=lambda r: r['scenarios'][0]['values'].update(rows=2.0))
reject('resolved-cell-dropped', 'G4-generic-resolved', resolved_edit=lambda r: r['scenarios'][0]['inventory'].pop())
reject('resolved-invocation', 'G4-generic-resolved', resolved_edit=lambda r: r['scenarios'][0]['inventory'][0].update(invocations=[]))
reject('resolved-effect-order', 'G4-generic-resolved', resolved_edit=lambda r: r['rules']['procedures']['flag-procedure']['steps'][0]['branches'][0]['steps'].reverse())
reject('resolved-scope-order', 'G4-generic-resolved', resolved_edit=lambda r: r['scenarios'].reverse())
# Prove the required resolved-stage validator's own failure is fatal, even when
# schema/core/source and generic resolution passed. Modify only a disposable copy.
with tempfile.TemporaryDirectory(dir=root.parent) as temporary:
    copied = Path(temporary) / 'repo'
    shutil.copytree(root, copied, ignore=shutil.ignore_patterns('.git', 'build', '__pycache__'))
    profile = copied / 'tools/flag_profile.py'
    profile.write_text(profile.read_text() + '\ndef validate_resolved(d, r, root):\n    raise ValueError("injected resolved validator failure")\n')
    output = args.output / 'negative-required-resolved-validator'
    try:
        build(copied, args.dodge_checkout, output)
    except ValidationError:
        report = read_json(output / 'validation-report.json')
        require(report['stages'][-1]['stage'] == 'G4-required-resolved-profile', 'resolved validator failure bypassed')
        require(not (output / 'resolved-game.json').exists(), 'resolved validator failure published output')
        negatives.append(dict(case='required-resolved-validator', expected_stage='G4-required-resolved-profile', status='pass', rejection=report['error']))
    else:
        raise AssertionError('required resolved validator failure accepted')
summary = dict(status='pass', maturity='G4', deterministic_resolution=True,
               candidate_sha256=positive['candidate_sha256'], resolved_sha256=positive['resolved_sha256'],
               negatives=negatives, runtime_execution='not implemented; milestone 8')
(args.output / 'acceptance.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps(summary, indent=2))
