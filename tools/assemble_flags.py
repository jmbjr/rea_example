"""Derive scenario composition from retained native fixtures, never action rules."""
from copy import deepcopy
from pathlib import Path
import argparse
import json
from dodge_common import file_hash, fixture_records, read_json

def assemble(root):
    root = Path(root)
    document = deepcopy(read_json(root / 'model/flag-rules.dodge.json'))
    for source in document['sources'].values():
        source['sha256'] = file_hash(root / source['uri'])
    for path in sorted((root / 'evidence/step5/oracle').glob('*.json')):
        fixture = read_json(path)
        case = fixture['case']
        source_ref = 'oracle-' + case
        document['sources'][source_ref] = dict(kind='scenario', uri=str(path.relative_to(root)),
            version='milestone-5', authority='authoritative', sha256=file_hash(path),
            description='Synthetic native fixture; historical input and output, not a rule definition.')
        setup = fixture_records(fixture)[0]['setup']
        instances, bindings = [], []
        for index, cell in enumerate(setup['visible']):
            row, column = divmod(index, setup['columns'])
            instance = f'cell-{row}-{column}'
            instances.append(dict(id=instance, object_ref='cell', quantity=1))
            for ref, value in [('cell-row', row), ('cell-column', column), ('cell-visible', cell)]:
                bindings.append(dict(ref=ref, subject={'instance_ref': instance}, value=value))
        for ref, field in [('rows', 'rows'), ('columns', 'columns'), ('mines', 'mines'), ('flags', 'flags'),
                           ('generation', 'generation'), ('undo-index', 'undo_index'),
                           ('undo-enabled', 'undo_enabled'), ('grid-initialized', 'grid_initialized')]:
            bindings.append(dict(ref=ref, subject={'relative': 'scenario'}, value=setup[field]))
        scene_id = case + '-scene'
        document['scenes'][scene_id] = dict(name=case, source_ref=source_ref, instances=instances)
        document['scenarios'][case] = dict(name=case, scene_ref=scene_id, source_ref=source_ref,
            action_refs=['flag', 'unflag'], initial_state=bindings, authority='derived',
            assumptions=['Synthetic fixture scope; command-list exhaustion is not a Minesweeper end condition.'])
    return document

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(assemble(Path(__file__).resolve().parents[1]), indent=2) + '\n')
