"""Required bounded source/resolved admission; no native outputs are model inputs."""
from dodge_common import digest, require, read_json, file_hash
from playable_model import assemble
from resolve_flags import resolve, validate_resolved_core
PROFILE_ID = 'rea-minesweeper-playable'
VERSION = '1'

def validate_source(d, root):
    template = read_json(root / 'model/dig-template.json')
    # These constraints bind the reviewed template to REA/native claims. A changed
    # template needs a new evidence review, not merely a fresh source hash.
    require(template['neighbor_offsets'] == [[-1,-1],[-1,0],[-1,1],[0,-1],[0,1],[1,-1],[1,0],[1,1]], 'unreviewed neighbor order')
    require(template['results'] == dict(ok=0,bounds=1,flagged=5,mine=7), 'unreviewed result semantics')
    require([b['condition'] for b in template['procedure']['steps'][0]['branches']] == ['expand','flagged','is-mine'], 'unreviewed branch precedence')
    # Lock the reviewed rule template, flag rules and raw REA evidence independently
    # of the document's mutable source declarations.
    lock = read_json(root / 'model/playable-evidence-lock.json')
    for uri, expected in lock.items():
        require(file_hash(root / uri) == expected, 'reviewed evidence/template changed: '+uri)
    expected = assemble(root)
    require(digest(d) == digest(expected), 'playable graph/bindings/end semantics differ from canonical specialization')
    return dict(complete_specialization='pass', depth_bound=16, last_neighbor_layer=16,
                native_outputs_used_as_rules=False, ordered_end_conditions='win then loss',
                scenarios=len(d['scenarios']), procedures=len(d['rules']['procedures']))

def validate_resolved(d, r, root):
    validate_source(d, root)
    validate_resolved_core(d, r)
    require(digest(r) == digest(resolve(d)), 'resolved playable semantics changed')
    return dict(profile_id=PROFILE_ID, version=VERSION, stage='resolved-game', complete_semantics='pass')
