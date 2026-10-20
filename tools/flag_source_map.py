"""Derived diagnostic locators. This file supplies no executable semantics."""
from dodge_common import digest, file_hash, read_json

def source_map(document, root):
    entries = []
    for section, definitions in document['rules'].items():
        for ref, definition in definitions.items():
            pointer = '/rules/' + section + '/' + ref
            entry = dict(candidate_pointer=pointer, authored_uri='model/flag-rules.dodge.json',
                         authored_pointer=pointer, authored_sha256=file_hash(root / 'model/flag-rules.dodge.json'))
            if 'source_ref' in definition:
                source = document['sources'][definition['source_ref']]
                evidence = read_json(root / source['uri'])
                entry.update(evidence_source_ref=definition['source_ref'], evidence_id=evidence['evidence_id'],
                             evidence_sha256=source['sha256'], evidence_pointer='/normalized_result')
            entries.append(entry)
    field_names = dict(rows='rows', columns='columns', mines='mines', flags='flags', generation='generation',
                       **{'undo-index': 'undo_index', 'undo-enabled': 'undo_enabled', 'grid-initialized': 'grid_initialized'})
    for scenario_id, scenario in document['scenarios'].items():
        source = document['sources'][scenario['source_ref']]
        synthetic = source['version'] == 'synthetic-1'
        config = read_json(root / source['uri']) if synthetic else None
        columns = next(b['value'] for b in scenario['initial_state'] if b['ref'] == 'columns')
        instances = document['scenes'][scenario['scene_ref']]['instances']
        for index, binding in enumerate(scenario['initial_state']):
            entry = dict(candidate_pointer=f'/scenarios/{scenario_id}/initial_state/{index}',
                         source_ref=scenario['source_ref'], source_sha256=source['sha256'],
                         source_pointer='/runs/0/stdout', decode='JSON Lines', decoded_line=0)
            if 'instance_ref' in binding['subject']:
                position = next(i for i, inst in enumerate(instances) if inst['id'] == binding['subject']['instance_ref'])
                entry.update(decoded_pointer='/setup/visible', character_index=position)
                if binding['ref'] in ['cell-row', 'cell-column']:
                    entry.update(derivation='divmod(character_index, setup.columns)', columns=columns)
            else:
                entry['decoded_pointer'] = '/setup/' + field_names[binding['ref']]
            if synthetic:
                entry.pop('decode', None)
                entry.pop('decoded_line', None)
                entry.pop('decoded_pointer', None)
                entry['source_pointer'] = '/visible'
                entry['synthetic'] = True
                if binding['ref'] == 'flags':
                    entry['derivation'] = 'count F in declared synthetic visible input'
                elif binding['ref'] not in ['cell-visible']:
                    base_ref = document['scenarios'][config['base_case']]['source_ref']
                    entry.update(base_source_ref=base_ref, base_source_sha256=document['sources'][base_ref]['sha256'],
                                 base_pointer='/runs/0/stdout', base_decode='JSON Lines; line 0 /setup')
            entries.append(entry)
    return dict(source_map_version=1, candidate_sha256=digest(document), entries=entries,
                authority='derived diagnostic; never executed as rules')
