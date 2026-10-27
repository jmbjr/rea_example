"""DODGE core checks for an explicitly bounded supported language subset.

Unknown features fail admission; this is not a universal DODGE validator.
"""
from dodge_common import identifier, keys, local_path, file_hash, matches, require, unique

SECTIONS = ('values', 'conditions', 'effects', 'actions', 'procedures')

def validate_core(d, root):
    keys(d, ['dodge_version', 'document_id', 'game_id', 'title', 'description', 'sources',
             'archetypes', 'objects', 'scenes', 'scenarios', 'rules', 'validation'])
    for name in ['document_id', 'game_id']:
        identifier(d[name])
    for section in ['sources', 'archetypes', 'objects', 'scenes', 'scenarios']:
        for name in d[section]:
            identifier(name)
    for source in d['sources'].values():
        keys(source, ['kind', 'uri', 'version', 'authority', 'description', 'sha256'], ['sha256'])
        require(file_hash(local_path(root, source['uri'])) == source['sha256'], 'source hash mismatch: ' + source['uri'])
    rules = d['rules']
    keys(rules, SECTIONS, SECTIONS)
    all_ids = [ref for section in SECTIONS for ref in rules[section]]
    unique(all_ids, 'rule ID across kinds')
    for ref in all_ids:
        identifier(ref)
    values = rules['values']

    def trace(item):
        if 'source_ref' in item:
            require(item['source_ref'] in d['sources'], 'missing source reference')

    def subject(s, owner=None):
        require(type(s) is dict and len(s) == 1, 'ambiguous or absent subject')
        if 'relative' in s:
            require(s['relative'] in ['target', 'scenario'], 'unsupported relative selector')
            if owner:
                require(s['relative'] == ('target' if owner == 'object' else 'scenario'), 'subject ownership mismatch')
        else:
            require(owner in (None, 'object'), 'static subject ownership mismatch')
            keys(s, ['instance_ref'], ['instance_ref'])
            require(owner in (None, 'object'), 'scenario binding cannot own an instance')

    for definition in values.values():
        keys(definition, ['name', 'description', 'type', 'owner_scope', 'persistence_scope',
                          'minimum', 'maximum', 'enum_values', 'default', 'source_ref', 'authority'])
        require(definition['owner_scope'] in ['object', 'scenario'], 'unsupported owner')
        require(definition['persistence_scope'] == 'scenario', 'unsupported persistence')
        require(definition.get('minimum', float('-inf')) <= definition.get('maximum', float('inf')), 'inverted bounds')
        if definition['type'] == 'enum':
            require(bool(definition.get('enum_values')), 'enum values missing')
        if 'default' in definition:
            matches(definition, definition['default'])
        trace(definition)
    condition_graph = {}
    for ref, condition in rules['conditions'].items():
        trace(condition)
        if condition['op'] in ('all', 'any', 'not'):
            keys(condition, ['op', 'conditions', 'source_ref'], ['op', 'conditions'])
            children = condition['conditions']
            require(bool(children) and all(type(x) is str and x in rules['conditions'] for x in children), 'invalid composite predicate')
            require(condition['op'] != 'not' or len(children) == 1, 'not requires one condition')
            condition_graph[ref] = children
        else:
            keys(condition, ['op', 'left', 'right', 'source_ref'], ['op', 'left', 'right'])
            require(condition['op'] == 'eq', 'unsupported predicate')
            operand = condition['left']
            keys(operand, ['ref', 'subject'], ['ref', 'subject'])
            require(operand['ref'] in values, 'operand reference wrong kind or missing')
            definition = values[operand['ref']]
            subject(operand['subject'], definition['owner_scope'])
            matches(definition, condition['right'])
            condition_graph[ref] = []
    def acyclic(graph, label):
        active, visited = set(), set()
        def visit(node):
            require(node not in active, label + ' reference cycle')
            if node in visited:
                return
            active.add(node)
            for child in graph[node]:
                visit(child)
            active.remove(node)
            visited.add(node)
        for node in graph:
            visit(node)
    acyclic(condition_graph, 'condition')
    for effect in rules['effects'].values():
        keys(effect, ['op', 'target_ref', 'subject', 'value', 'source_ref'], ['op', 'target_ref', 'subject', 'value'])
        require(effect['op'] in ['set', 'add', 'subtract'], 'unsupported effect')
        require(effect['target_ref'] in values, 'effect target wrong kind or missing')
        definition = values[effect['target_ref']]
        subject(effect['subject'], definition['owner_scope'])
        if effect['op'] == 'set':
            matches(definition, effect['value'])
        else:
            require(definition['type'] in ['integer', 'number'], 'numeric effect on nonnumeric state')
            require(type(effect['value']) in ([int] if definition['type'] == 'integer' else [int, float]), 'invalid numeric delta')
        trace(effect)
    graph = {ref: [] for section in ['actions', 'procedures'] for ref in rules[section]}

    def steps(items, parent, allowed=('effect', 'procedure', 'action', 'branch')):
        require(type(items) is list, 'executable sequence must be a list')
        for step in items:
            kind = step['kind']
            require(kind in allowed, 'unsupported step')
            if kind == 'branch':
                keys(step, ['kind', 'branches', 'else_steps'], ['branches', 'else_steps'])
                for branch in step['branches']:
                    keys(branch, ['condition', 'steps'], ['condition', 'steps'])
                    require(type(branch['condition']) is str and branch['condition'] in rules['conditions'], 'branch condition wrong kind or missing')
                    steps(branch['steps'], parent)
                steps(step['else_steps'], parent)
            else:
                keys(step, ['kind', 'ref'], ['ref'])
                require(step['ref'] in rules[kind + 's'], 'step reference wrong kind or missing')
                if kind in ('action', 'procedure'):
                    graph[parent].append(step['ref'])
    for name, procedure in rules['procedures'].items():
        keys(procedure, ['name', 'steps', 'source_ref'], ['steps'])
        trace(procedure)
        steps(procedure['steps'], name)
    for name, action in rules['actions'].items():
        keys(action, ['name', 'target', 'procedure_ref', 'source_ref'], ['target', 'procedure_ref'])
        require(action['target'] == {'relative': 'target'}, 'unsupported action target')
        require(action['procedure_ref'] in rules['procedures'], 'action procedure wrong kind or missing')
        graph[name].append(action['procedure_ref'])
        trace(action)
    active, visited = set(), set()
    def visit(node):
        require(node not in active, 'procedure/action reference cycle')
        if node in visited:
            return
        active.add(node)
        for child in graph[node]:
            visit(child)
        active.remove(node)
        visited.add(node)
    for node in graph:
        visit(node)
    for archetype in d['archetypes'].values():
        keys(archetype, ['kind'])
        require(archetype['kind'] == 'token', 'unsupported archetype kind')
    for obj in d['objects'].values():
        keys(obj, ['kind', 'archetype_ref', 'name', 'invocations'], ['invocations'])
        require(obj['archetype_ref'] in d['archetypes'], 'missing archetype')
        require(obj['kind'] == d['archetypes'][obj['archetype_ref']]['kind'], 'object/archetype mismatch')
        unique([inv['id'] for inv in obj['invocations']], 'invocation ID')
        unique([inv['trigger'] for inv in obj['invocations']], 'invocation trigger in supported adapter')
        for inv in obj['invocations']:
            keys(inv, ['id', 'trigger', 'steps', 'subject_bindings', 'source_ref'], ['subject_bindings'])
            trace(inv)
            unique([x['slot'] for x in inv['subject_bindings']], 'subject slot')
            require(inv['subject_bindings'] == [{'slot': 'target', 'source': 'using-object'}], 'missing/unsupported target context')
            # This subset exposes only explicitly referenced actions, not inferred ID matching.
            for step in inv['steps']:
                keys(step, ['kind', 'ref'], ['kind', 'ref'])
                require(step['kind'] == 'action' and step['ref'] in rules['actions'], 'invocation action reference')
    for scene in d['scenes'].values():
        keys(scene, ['name', 'source_ref', 'instances'])
        trace(scene)
        unique([x['id'] for x in scene['instances']], 'scene instance ID')
        for inst in scene['instances']:
            keys(inst, ['id', 'object_ref', 'quantity'], ['quantity'])
            require(inst['object_ref'] in d['objects'], 'missing object')
            require(type(inst['quantity']) is int and inst['quantity'] >= 1, 'invalid quantity')
    require(bool(d['scenarios']), 'no selected scenarios')
    for scenario in d['scenarios'].values():
        keys(scenario, ['name', 'scene_ref', 'source_ref', 'action_refs', 'initial_state', 'authority', 'assumptions', 'end_conditions'], ['initial_state', 'action_refs'])
        trace(scenario)
        require(scenario['scene_ref'] in d['scenes'], 'missing selected scene')
        scene = d['scenes'][scenario['scene_ref']]
        ids = {x['id'] for x in scene['instances']}
        unique(scenario['action_refs'], 'available action')
        require(set(scenario['action_refs']) <= set(rules['actions']), 'missing available action')
        ends = scenario.get('end_conditions', [])
        unique([x['id'] for x in ends], 'end condition ID')
        for end in ends:
            keys(end, ['id', 'outcome', 'condition'], ['id', 'outcome', 'condition'])
            require(end['condition'] in rules['conditions'], 'missing terminal predicate')
            require(end['outcome'] in ('win', 'loss'), 'unsupported terminal outcome')
        for collection in ('conditions', 'effects'):
            for item in rules[collection].values():
                owner = item.get('subject', item.get('left', {}).get('subject', {}))
                if 'instance_ref' in owner:
                    require(owner['instance_ref'] in ids, 'static subject missing from scope')
        seen = []
        for binding in scenario['initial_state']:
            keys(binding, ['ref', 'subject', 'value'], ['subject'])
            require(binding['ref'] in values, 'binding wrong kind or missing')
            definition = values[binding['ref']]
            subject(binding['subject'])
            if definition['owner_scope'] == 'object':
                require(binding['subject'].get('instance_ref') in ids, 'binding instance missing')
            else:
                require(binding['subject'] == {'relative': 'scenario'}, 'scenario owner mismatch')
            matches(definition, binding['value'])
            seen.append((binding['ref'], tuple(binding['subject'].items())))
        unique(seen, 'state binding')
        for inst in scene['instances']:
            for inv in d['objects'][inst['object_ref']]['invocations']:
                require(all(x['ref'] in scenario['action_refs'] for x in inv['steps']), 'invoked action unavailable')
        # Prove every required lookup/mutation has one concrete binding per possible cell target.
        read_refs = {x['left']['ref'] for x in rules['conditions'].values() if 'left' in x}
        read_refs |= {x['target_ref'] for x in rules['effects'].values() if x['op'] != 'set'}
        output_refs = {x['target_ref'] for x in rules['effects'].values() if x['op'] == 'set'} - read_refs
        for ref, definition in values.items():
            if ref in output_refs:  # Write-only outputs may be unset; the application owns path completeness.
                continue
            owners = [{'instance_ref': x} for x in ids] if definition['owner_scope'] == 'object' else [{'relative': 'scenario'}]
            for owner in owners:
                require((ref, tuple(owner.items())) in seen, 'required binding missing: ' + ref)
    return {
        'profile_id': 'dodge-core', 'version': d['dodge_version'], 'stage': 'core',
        '1_references': 'pass', '2_kind_face_agreement': 'pass; token subset, no faces',
        '3_cycles': 'pass; explicit action/procedure DFS; collections rejected',
        '4_quantities_dimensions': 'pass; positive quantities; physical components rejected',
        '5_source_hashes': 'pass', '6_scoped_identity': 'pass',
        '7_topology_edges': 'not-applicable; topology input rejected',
        '8_reference_kinds': 'pass', '9_types_defaults_bounds': 'pass',
        '10_order_end_conditions': 'pass; ordered branches/effects; declared end-condition order; priority/effects/phases rejected',
        '11_ai': 'not-applicable; AI input rejected',
        '12_target_contract': 'not-applicable; no exporter invoked',
        'invocations': 'pass; direct token inheritance, unique IDs/slots, explicit target and availability',
        'conditional_features': 'representations/equipment/modifiers/etc rejected when supplied',
    }
