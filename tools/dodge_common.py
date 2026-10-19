"""Shared identity and admission helpers; no gameplay execution."""
import hashlib
import json
import re
from pathlib import Path

class ValidationError(ValueError):
    pass

def require(condition, message):
    if not condition:
        raise ValidationError(message)

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()

def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()

def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read_json(path):
    return json.loads(Path(path).read_text())

def local_path(root, uri):
    root = Path(root).resolve()
    path = (root / uri).resolve()
    require(path.is_relative_to(root) and not Path(uri).is_absolute(), 'source must be repository-local: ' + uri)
    require(path.is_file(), 'missing source: ' + uri)
    return path

def keys(value, allowed, required=()):
    require(set(value) <= set(allowed), 'unsupported fields: ' + str(sorted(set(value) - set(allowed))))
    require(set(required) <= set(value), 'missing fields: ' + str(sorted(set(required) - set(value))))

def unique(items, label):
    require(len(items) == len(set(items)), 'duplicate ' + label)

def identifier(value):
    require(isinstance(value, str) and re.fullmatch(r'[a-z0-9][a-z0-9._:-]*', value), 'invalid identifier')

def matches(definition, value):
    kind = definition['type']
    valid = {'integer': type(value) is int, 'number': type(value) in (int, float),
             'boolean': type(value) is bool, 'string': type(value) is str,
             'enum': any(type(value) is type(x) and value == x for x in definition.get('enum_values', []))}[kind]
    require(valid, 'state type/enum mismatch')
    if type(value) in (int, float):
        require(value >= definition.get('minimum', float('-inf')), 'state below minimum')
        require(value <= definition.get('maximum', float('inf')), 'state above maximum')

def fixture_records(fixture):
    runs = fixture['runs']
    require(fixture['repetitions'] == 3 and len(runs) == 3, 'oracle repetitions missing')
    require(all(x == runs[0] for x in runs), 'oracle repetitions diverge')
    require(runs[0]['returncode'] == 0 and not runs[0]['stderr'], 'oracle failed')
    return [json.loads(line) for line in runs[0]['stdout'].splitlines()]
