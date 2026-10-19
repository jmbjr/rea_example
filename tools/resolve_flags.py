"""Materialize ordered instances and inherited invocations into one neutral model."""
from copy import deepcopy
from dodge_common import digest, keys, require

def resolve(d):
    result = dict(resolved_version='rea-flags-resolved/1',
        document_identity=dict(document_id=d['document_id'], dodge_version=d['dodge_version'], sha256=digest(d)),
        sources=deepcopy(d['sources']), rules=deepcopy(d['rules']),
        archetypes=deepcopy(d['archetypes']), objects=deepcopy(d['objects']), scenarios=[])
    for scenario_id, scenario in d['scenarios'].items():
        scope = dict(id=scenario_id, scene_ref=scenario['scene_ref'], source_ref=scenario['source_ref'],
                     action_refs=deepcopy(scenario['action_refs']), values={}, inventory=[])
        for binding in scenario['initial_state']:
            if binding['subject'] == {'relative': 'scenario'}:
                scope['values'][binding['ref']] = deepcopy(binding['value'])
        for inst in d['scenes'][scenario['scene_ref']]['instances']:
            item = dict(instance_id=inst['id'], object_ref=inst['object_ref'], quantity=inst['quantity'], values={},
                        invocations=deepcopy(d['objects'][inst['object_ref']]['invocations']),
                        provenance=dict(scene_ref=scenario['scene_ref'], source_ref=scenario['source_ref']))
            for binding in scenario['initial_state']:
                if binding['subject'] == {'instance_ref': inst['id']}:
                    item['values'][binding['ref']] = deepcopy(binding['value'])
            scope['inventory'].append(item)
        result['scenarios'].append(scope)
    return result

def validate_resolved_core(d, r):
    keys(r, ['resolved_version', 'document_identity', 'rules', 'sources', 'archetypes', 'objects', 'scenarios'],
         ['resolved_version', 'document_identity', 'rules', 'sources', 'archetypes', 'objects', 'scenarios'])
    require(r['resolved_version'] == 'rea-flags-resolved/1', 'unknown resolved format')
    from dodge_common import digest
    require(r['document_identity'] == dict(document_id=d['document_id'], dodge_version=d['dodge_version'], sha256=digest(d)), 'resolved source identity changed')
    require(r['rules'] == d['rules'] and r['sources'] == d['sources'], 'dropped/invented rule or source semantics')
    require(r['objects'] == d['objects'] and r['archetypes'] == d['archetypes'], 'dropped/invented object semantics')
    require([s['id'] for s in r['scenarios']] == list(d['scenarios']), 'resolved scope order/content changed')
    for scope in r['scenarios']:
        scenario = d['scenarios'][scope['id']]
        keys(scope, ['id', 'scene_ref', 'source_ref', 'action_refs', 'values', 'inventory'])
        require(scope['scene_ref'] == scenario['scene_ref'] and scope['source_ref'] == scenario['source_ref'], 'resolved scope provenance changed')
        require(scope['action_refs'] == scenario['action_refs'], 'resolved action availability changed')
        source_values = {b['ref']: b['value'] for b in scenario['initial_state'] if b['subject'] == {'relative': 'scenario'}}
        require(scope['values'] == source_values, 'resolved scenario bindings changed')
        instances = d['scenes'][scenario['scene_ref']]['instances']
        require(len(scope['inventory']) == len(instances), 'resolved inventory incomplete')
        for item, inst in zip(scope['inventory'], instances):
            expected_values = {b['ref']: b['value'] for b in scenario['initial_state'] if b['subject'] == {'instance_ref': inst['id']}}
            expected = dict(instance_id=inst['id'], object_ref=inst['object_ref'], quantity=inst['quantity'],
                values=expected_values, invocations=d['objects'][inst['object_ref']]['invocations'],
                provenance={'scene_ref': scenario['scene_ref'], 'source_ref': scenario['source_ref']})
            require(item == expected, 'resolved cell state/invocation/provenance changed')
    return {'exact_downstream_model': 'pass', 'ordered_scenarios': len(r['scenarios'])}
