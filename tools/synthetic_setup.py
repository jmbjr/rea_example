"""An explicit scenario-input variant; never edits historical native recordings."""
from copy import deepcopy
from dodge_common import file_hash, read_json

def add_synthetic_setup(document, root):
    config = read_json(root / 'model/synthetic-setup.json')
    source_ref = 'synthetic-setup'
    scenario = deepcopy(document['scenarios'][config['base_case']])
    scene = deepcopy(document['scenes'][scenario['scene_ref']])
    scenario_id = config['scenario_id']
    scene_id = scenario_id + '-scene'
    document['sources'][source_ref] = dict(kind='scenario', uri='model/synthetic-setup.json',
        version='synthetic-1', authority='authoritative', sha256=file_hash(root / 'model/synthetic-setup.json'),
        description=config['purpose'])
    scenario.update(name=scenario_id, source_ref=source_ref, scene_ref=scene_id,
                    assumptions=['Synthetic input perturbation; not native equivalence evidence.'])
    scene.update(name=scenario_id, source_ref=source_ref)
    indices = {inst['id']: index for index, inst in enumerate(scene['instances'])}
    for binding in scenario['initial_state']:
        if binding['ref'] == 'cell-visible':
            binding['value'] = config['visible'][indices[binding['subject']['instance_ref']]]
        elif binding['ref'] == 'flags':
            binding['value'] = config['visible'].count('F')
    document['scenarios'][scenario_id] = scenario
    document['scenes'][scene_id] = scene
    return document
