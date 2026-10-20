"""Application-owned recovered-contract checks. No transition execution here."""
from dodge_common import file_hash, fixture_records, keys, local_path, read_json, require

PROFILE_ID = 'rea-minesweeper-flags'
VERSION = '0.2.0'
STATE_FIELDS = {'rows': 'rows', 'columns': 'columns', 'mines': 'mines', 'flags': 'flags',
                'generation': 'generation', 'undo-index': 'undo_index',
                'undo-enabled': 'undo_enabled', 'grid-initialized': 'grid_initialized'}
NATIVE_FIELDS = {'rows': 2, 'columns': 3, 'mines': 1, 'generation': 1, 'undo_index': 0,
                 'undo_enabled': False, 'grid_initialized': False}

def _validate_original_source(d, root):
    lock = read_json(root / 'model/evidence-lock.json')
    for uri, sha in lock['files'].items():
        require(file_hash(local_path(root, uri)) == sha, 'retained evidence differs from lock')
        if '/rea/' in uri:
            evidence = read_json(root / uri)
            require(evidence['subject']['digest']['sha256'] == lock['rea_baseline_sha256'], 'wrong analyzed executable')
            require(evidence['provider'] == dict(id='ghidra', name='Ghidra', version='12.1.4'), 'unexpected evidence provider')
            require(bool(evidence['evidence_id']) and evidence['operation'] == 'procedure_pseudo_code', 'missing native evidence identity')
    # These scope assertions come from CONTRACT.md, not from the assembler.
    values = d['rules']['values']
    require(set(values) == set(STATE_FIELDS) | {'cell-row', 'cell-column', 'cell-visible', 'result'}, 'slice state vocabulary changed')
    require(values['cell-visible']['type'] == 'enum' and values['cell-visible']['enum_values'] == ['#', 'F', *map(str, range(9))], 'cell enum changed')
    require(values['result']['type'] == 'enum' and values['result']['enum_values'] == [0, 2, 8], 'result vocabulary changed')
    require(all(type(x) is int for x in values['result']['enum_values']), 'native result codes must be integers')
    for ref, definition in values.items():
        require('default' not in definition, 'defaults must not mask fixture bindings')
        require(definition['owner_scope'] == ('object' if ref.startswith('cell-') else 'scenario'), 'state ownership changed')
        require(definition['persistence_scope'] == 'scenario', 'state persistence changed')
        expected_type = 'enum' if ref in ['cell-visible', 'result'] else 'boolean' if ref in ['undo-enabled', 'grid-initialized'] else 'integer'
        require(definition['type'] == expected_type, 'native scalar type changed')
    require('maximum' not in values['flags'], 'invented flag cap')
    require(set(d['archetypes']) == {'cell'} and set(d['objects']) == {'cell'}, 'cell inventory vocabulary changed')
    cell = d['objects']['cell']
    require(len(cell['invocations']) == 2, 'required invocations missing')
    rules = d['rules']
    require([len(rules[x]) for x in ['conditions', 'effects', 'actions', 'procedures']] == [2, 8, 2, 2], 'extra/dropped executable declarations')
    invocations = {x['trigger']: x for x in cell['invocations']}
    require(set(invocations) == {'flag', 'unflag'}, 'required triggers missing')
    action_refs = []
    for trigger, before, after, operation, failure in [('flag', '#', 'F', 'add', 2), ('unflag', 'F', '#', 'subtract', 8)]:
        inv = invocations[trigger]
        require(len(inv['steps']) == 1, 'invocation must execute one action')
        action_ref = inv['steps'][0]['ref']
        action_refs.append(action_ref)
        action = rules['actions'][action_ref]
        source_ref = action['source_ref']
        require(d['sources'][source_ref]['uri'] == 'evidence/step5/rea/msw_' + trigger + '.json', 'action evidence association changed')
        require(inv.get('source_ref') == source_ref, 'invocation provenance missing')
        require(set(action) == {'name', 'target', 'procedure_ref', 'source_ref'}, 'cost/requirement alters rejected-call semantics')
        procedure = rules['procedures'][action['procedure_ref']]
        require(procedure.get('source_ref') == source_ref and len(procedure['steps']) == 1, 'procedure provenance/shape')
        branch = procedure['steps'][0]
        require(branch['kind'] == 'branch' and len(branch['branches']) == 1, 'one predicate branch required')
        success = branch['branches'][0]
        condition = rules['conditions'][success['condition']]
        require(condition == dict(op='eq', left={'ref': 'cell-visible', 'subject': {'relative': 'target'}}, right=before, source_ref=source_ref), 'eligibility differs from evidence')
        require(len(success['steps']) == 3 and len(branch['else_steps']) == 1, 'success/rejection sequence incomplete')
        observed_effects = [rules['effects'][s['ref']] for s in success['steps'] + branch['else_steps']]
        expected = [('set', 'cell-visible', 'target', after), (operation, 'flags', 'scenario', 1),
                    ('set', 'result', 'scenario', 0), ('set', 'result', 'scenario', failure)]
        for step, actual, (op, ref, subject, value) in zip(success['steps'] + branch['else_steps'], observed_effects, expected):
            require(step['kind'] == 'effect', 'contract requires direct effect steps')
            require(actual == dict(op=op, target_ref=ref, subject={'relative': subject}, value=value, source_ref=source_ref), 'effect/order differs from recovered contract')
    require(len(set(action_refs)) == 2, 'two triggers must not share incompatible action')
    paths = sorted((root / 'evidence/step5/oracle').glob('*.json'))
    require(len(paths) == 6 and len(d['scenarios']) == len(d['scenes']) == 6, 'fixture/scenario coverage incomplete')
    require(set(d['scenarios']) == {read_json(p)['case'] for p in paths}, 'scenario identities differ from sources')
    messages = {}
    for path in paths:
        f = read_json(path)
        require(f['setup_kind'] == 'synthetic-visible-state', 'fixture authority unclear')
        require(f['target']['sha256'] == lock['oracle_sha256'], 'wrong native oracle identity')
        records = fixture_records(f)
        setup = records[0]['setup']
        for key, expected in NATIVE_FIELDS.items():
            require(type(setup[key]) is type(expected) and setup[key] == expected, 'fixture outside admitted scope')
        require(len(setup['visible']) == 6 and set(setup['visible']) <= set(values['cell-visible']['enum_values']), 'invalid fixture cell')
        require(setup['flags'] == setup['visible'].count('F') and setup['visible'] == f['setup'], 'incoherent fixture counter/setup')
        require(len(f['stdin'].splitlines()) == len(records) - 1, 'fixture command/observation count')
        previous = setup
        for command, rec in zip(f['stdin'].splitlines(), records[1:]):
            parts = command.split()
            require(parts == [rec['action'], str(rec['row']), str(rec['column'])], 'fixture command differs from observation')
            require(rec['action'] in ['f', 'u'] and 0 <= rec['row'] < 2 and 0 <= rec['column'] < 3, 'out-of-domain command')
            require(rec['before'] == previous, 'native state continuity broken')
            if rec['result'] in messages:
                require(messages[rec['result']] == rec['message'], 'inconsistent native message')
            messages[rec['result']] = rec['message']
            previous = rec['after']
        scenario = d['scenarios'][f['case']]
        require(scenario['action_refs'] == action_refs, 'scenario action order/availability')
        source = d['sources'][scenario['source_ref']]
        require(source['kind'] == 'scenario' and source['uri'] == str(path.relative_to(root)), 'scenario source mismatch')
        scene = d['scenes'][scenario['scene_ref']]
        require(scene['source_ref'] == scenario['source_ref'], 'scene provenance mismatch')
        instances = scene['instances']
        require(len(instances) == 6 and all(x['object_ref'] == 'cell' and x['quantity'] == 1 for x in instances), 'cell quantity mismatch')
        # Independently reconstruct required bindings from native input, not from assemble().
        expected_bindings = []
        for index, inst in enumerate(instances):
            row, col = divmod(index, setup['columns'])
            for ref, value in [('cell-row', row), ('cell-column', col), ('cell-visible', setup['visible'][index])]:
                expected_bindings.append(dict(ref=ref, subject={'instance_ref': inst['id']}, value=value))
        for ref, field in STATE_FIELDS.items():
            expected_bindings.append(dict(ref=ref, subject={'relative': 'scenario'}, value=setup[field]))
        require(scenario['initial_state'] == expected_bindings, 'fixture projection/binding order differs from source')
    require(set(messages) == {0, 2, 8}, 'result/message coverage incomplete')
    return {'fixture_count': 6, 'messages': messages, 'scope': 'direct calls; valid 2x3 synthetic state; undo disabled'}

def validate_source(d, root):
    if 'synthetic-setup' not in d['sources']:
        return _validate_original_source(d, root)
    from copy import deepcopy
    source = d['sources']['synthetic-setup']
    require(source['kind'] == 'scenario' and source['uri'] == 'model/synthetic-setup.json' and
            source['version'] == 'synthetic-1', 'synthetic source identity mismatch')
    config = read_json(root / source['uri'])
    keys(config, ['version', 'scenario_id', 'base_case', 'visible', 'purpose'],
         ['version', 'scenario_id', 'base_case', 'visible', 'purpose'])
    require(config['version'] == '1', 'unsupported synthetic setup')
    require(type(config['visible']) is str and len(config['visible']) == 6 and
            set(config['visible']) <= set('#F012345678'), 'invalid synthetic visible input')
    variant = d['scenarios'][config['scenario_id']]
    original = deepcopy(d)
    original['scenarios'].pop(config['scenario_id'])
    original['scenes'].pop(variant['scene_ref'])
    result = _validate_original_source(original, root)
    require(config['base_case'] in original['scenarios'], 'synthetic base is not an original fixture')
    base = original['scenarios'][config['base_case']]
    base_scene = original['scenes'][base['scene_ref']]
    expected = deepcopy(base)
    expected.update(name=config['scenario_id'], source_ref='synthetic-setup', scene_ref=config['scenario_id'] + '-scene',
                    assumptions=['Synthetic input perturbation; not native equivalence evidence.'])
    # Independently check the variant projection, without calling its assembler.
    visible_bindings = [b for b in expected['initial_state'] if b['ref'] == 'cell-visible']
    for index, binding in enumerate(visible_bindings):
        binding['value'] = config['visible'][index]
    next(b for b in expected['initial_state'] if b['ref'] == 'flags')['value'] = config['visible'].count('F')
    from dodge_common import digest
    require(digest(variant) == digest(expected), 'synthetic setup projection changed')
    expected_scene = deepcopy(base_scene)
    expected_scene.update(name=config['scenario_id'], source_ref='synthetic-setup')
    require(digest(d['scenes'][variant['scene_ref']]) == digest(expected_scene), 'synthetic scene projection changed')
    result['synthetic_scenario'] = config['scenario_id']
    return result

def validate_resolved(d, r, root):
    validate_source(d, root)
    for scope in r['scenarios']:
        require('result' not in scope['values'], 'initial result must remain unset')
        visible = ''.join(x['values']['cell-visible'] for x in scope['inventory'])
        require(scope['values']['flags'] == visible.count('F'), 'resolved counter incoherent')
        require(len({(x['values']['cell-row'], x['values']['cell-column']) for x in scope['inventory']}) == 6, 'resolved coordinates ambiguous')
        require(scope['values']['undo-enabled'] is False and scope['values']['grid-initialized'] is False, 'resolved scope weakened')
    return {'profile_id': PROFILE_ID, 'version': VERSION, 'stage': 'resolved-game', 'status': 'pass'}
