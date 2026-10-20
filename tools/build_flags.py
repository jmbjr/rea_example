"""Fatal validation lifecycle through G4. Does not execute game actions."""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from jsonschema import Draft202012Validator
from assemble_flags import assemble
from dodge_common import ValidationError, digest, file_hash, local_path, read_json, require
from dodge_core import validate_core
from resolve_flags import resolve, validate_resolved_core
from flag_source_map import source_map

def load_profile(d, root):
    requirements = d['validation']['required_profiles']
    require(len(requirements) == 1, 'selected slice requires one application profile')
    requirement = requirements[0]
    require(requirement == dict(profile_id='rea-minesweeper-flags', version='0.2.0', kind='application',
            stages=['source', 'resolved-game'], validator_source_ref='flag-profile'), 'missing/unsupported/version-mismatched required profile')
    source = d['sources'][requirement['validator_source_ref']]
    require(source['kind'] == 'semantic_validator' and source['version'] == requirement['version'], 'validator kind/version mismatch')
    path = local_path(root, source['uri'])
    require(path == root / 'tools/flag_profile.py', 'unsupported validator implementation')
    spec = importlib.util.spec_from_file_location('selected_flag_profile', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    require(module.PROFILE_ID == requirement['profile_id'] and module.VERSION == requirement['version'], 'loaded validator identity mismatch')
    return module

def build(root, checkout, output, candidate=None, resolved_edit=None):
    root, checkout, output = Path(root).resolve(), Path(checkout).resolve(), Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    resolved_path = output / 'resolved-game.json'
    resolved_path.unlink(missing_ok=True)
    report = {'status': 'running', 'maturity': 'none', 'stages': [],
              'toolchain_sha256': {p.name: file_hash(p) for p in sorted((root / 'tools').glob('*.py'))}}
    def stage(name, run):
        try:
            details = run()
        except Exception as error:
            report['stages'].append(dict(stage=name, status='fail', error=str(error)))
            raise
        report['stages'].append(dict(stage=name, status='pass', details=details))
    try:
        def pin():
            result = subprocess.run([sys.executable, str(root / 'tools/verify_dodge_pin.py'), str(checkout)], capture_output=True, text=True)
            require(result.returncode == 0, result.stderr or result.stdout)
            return json.loads(result.stdout)
        stage('pin-integrity', pin)
        d = assemble(root) if candidate is None else candidate
        (output / 'candidate.dodge.json').write_text(json.dumps(d, indent=2) + '\n')
        report['candidate_sha256'] = digest(d)
        schema = read_json(checkout / 'draft/v0.2.1/schemas/dodge.schema.v0.2.1.json')
        stage('G1-schema', lambda: Draft202012Validator(schema).validate(d))
        stage('G2-core', lambda: validate_core(d, root))
        profile = None
        def source_profile():
            nonlocal profile
            profile = load_profile(d, root)
            return dict(profile_id=profile.PROFILE_ID, version=profile.VERSION, stage='source',
                        validator_sha256=d['sources']['flag-profile']['sha256'], validated_sha256=digest(d),
                        results=profile.validate_source(d, root))
        stage('G3-required-source-profile', source_profile)
        r = resolve(d)
        if resolved_edit:
            resolved_edit(r)
        stage('G4-generic-resolved', lambda: validate_resolved_core(d, r))
        def resolved_profile():
            details = profile.validate_resolved(d, r, root)
            details.update(validator_sha256=d['sources']['flag-profile']['sha256'], validated_sha256=digest(r))
            return details
        stage('G4-required-resolved-profile', resolved_profile)
        (output / 'source-map.json').write_text(json.dumps(source_map(d, root), indent=2) + '\n')
        report.update(status='pass', maturity='G4', resolved_sha256=digest(r),
                      hashing='UTF-8 canonical JSON: sorted keys, compact separators, no newline')
        temporary = output / 'resolved-game.json.tmp'
        temporary.write_text(json.dumps(r, indent=2) + '\n')
        temporary.replace(resolved_path)
        return d, r, report
    except Exception as error:
        report.update(status='fail', error=str(error))
        raise ValidationError(str(error)) from error
    finally:
        (output / 'validation-report.json').write_text(json.dumps(report, indent=2) + '\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dodge_checkout', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--candidate', type=Path)
    args = parser.parse_args()
    try:
        _, _, report = build(Path(__file__).resolve().parents[1], args.dodge_checkout, args.output,
                             None if args.candidate is None else read_json(args.candidate))
        print(json.dumps(report, indent=2))
    except ValidationError as error:
        print('Validation failed: ' + str(error), file=sys.stderr)
        sys.exit(1)
