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
            require(owner is None, 'static rule subjects unsupported in this subset')
            keys(s, ['instance_ref'], ['instance_ref'])
            require(owner in (None, 'object'), 'scenario binding cannot own an instance')

    for definition in values.values():
        keys(definition, ['name', 'description', 'type', 'owner_scope', 'persistence_scope',
                          'minimum', 'maximum', 'enum_values', 'default', 'source_ref', 'authority'])
        require(definition['owner_scope'] in ['object', 'scenario'], 'unsupported owner')
        require(definition['persistence_scope'] == 'scenario', 'unsupported persistence')
        require(definition.get('minimum', float('-inf')) <= definition.get('maximum', float('inf')), 'inverted bo…1515 tokens truncated… in scene['instances']}
        unique(scenario['action_refs'], 'available action')
        require(set(scenario['action_refs']) <= set(rules['actions']), 'missing available action')
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
        read_refs = {x['left']['ref'] for x in rules['conditions'].values()}
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
        '10_order_end_conditions': 'pass; ordered branches/effects; phases/end loops rejected',
        '11_ai': 'not-applicable; AI input rejected',
        '12_target_contract': 'not-applicable; no exporter invoked',
        'invocations': 'pass; direct token inheritance, unique IDs/slots, explicit target and availability',
        'conditional_features': 'representations/equipment/modifiers/etc rejected when supplied',
    }
