"""Specialize source-backed dig templates into ordinary finite DODGE primitives.

No expected action outputs are read here. Setup supplies mine positions only.
"""
from copy import deepcopy
from pathlib import Path
from dodge_common import read_json, file_hash, digest, require, keys, unique

ROOT = Path(__file__).resolve().parents[1]

def layout(board, setup):
    rows, cols = setup['rows'], setup['columns']
    mines = set(board['mines'])
    return ''.join('!' if i in mines else str(sum(
        r * cols + c in mines
        for r in range(max(0, i // cols - 1), min(rows, i // cols + 2))
        for c in range(max(0, i % cols - 1), min(cols, i % cols + 2))
        if (r, c) != divmod(i, cols))) for i in range(rows * cols))

def validate_setup(setup):
    keys(setup, ['version','boards','rows','columns','initial_visible','assumptions'], ['version','boards','rows','columns','initial_visible','assumptions'])
    require(setup['version'] == '1' and type(setup['rows']) is int and type(setup['columns']) is int and setup['rows'] == setup['columns'] == 4, 'admitted setup is 4x4 only')
    require(setup['initial_visible'] == '#' * 16, 'only all-hidden starting boards admitted')
    require(bool(setup['boards']), 'missing boards')
    unique([b['id'] for b in setup['boards']], 'board ID')
    for b in setup['boards']:
        keys(b, ['id','name','mines'], ['id','name','mines'])
        unique(b['mines'], 'mine position')
        require(0 < len(b['mines']) < 16 and all(type(i) is int and 0 <= i < 16 for i in b['mines']), 'invalid mine positions')

def assemble(root=ROOT, setup=None):
    root = Path(root)
    setup = read_json(root / 'model/playable-setup.json') if setup is None else deepcopy(setup)
    validate_setup(setup)
    t = read_json(root / 'model/dig-template.json')
    d = read_json(root / 'model/flag-rules.dodge.json')
    d.update(document_id='rea.minesweeper.playable', game_id='rea-minesweeper-playable', title='Fixed-board playable reconstruction')
    # Historical source references remain, but executable flag rules stay authored once.
    for name, uri, kind in [
        ('rea-dig','evidence/step9/rea/msw_dig.json','rules'),
        ('rea-win','evidence/step9/rea/msw_won.json','rules'),
        ('rea-caller-playable','evidence/step9/rea/run_game.json','rules'),
        ('dig-template','model/dig-template.json','rules'),
        ('playable-evidence-lock','model/playable-evidence-lock.json','rules'),
        ('playable-setup','model/playable-setup.json','scenario'),
        ('playable-profile','tools/playable_profile.py','semantic_validator'),
        ('playable-compiler','tools/playable_model.py','rules')]:
        d['sources'][name] = dict(kind=kind, uri=uri, version='1', authority='authoritative' if name in ('dig-template','playable-setup','playable-profile') else 'reference')
    for src in d['sources'].values():
        src['sha256'] = file_hash(root / src['uri'])
    d['validation']['required_profiles'] = [dict(profile_id='rea-minesweeper-playable',version='1',kind='application',stages=['source','resolved-game'],validator_source_ref='playable-profile')]
    rules = d['rules']; vals = rules['values']; cond = rules['conditions']; eff = rules['effects']; proc = rules['procedures']
    vals['cell-visible']['enum_values'].append('!')
    vals['cell-grid'] = dict(type='enum',owner_scope='object',persistence_scope='scenario',enum_values=list('012345678!'))
    vals['result']['enum_values'] = sorted(set(vals['result']['enum_values'] + list(t['results'].values())))
    proc['dig-noop'] = dict(name='No mutation',steps=[],source_ref='rea-dig')
    def eq(ref, subject, right, source='rea-dig'):
        return dict(op='eq', left=dict(ref=ref,subject=subject),right=right,source_ref=source)
    def step(kind, ref):
        return dict(kind=kind,ref=ref)
    cond['mine-result'] = eq('result', {'relative':'scenario'}, t['results']['mine'])
    for label, result in t['results'].items():
        eff['dig-'+label] = dict(op='set',target_ref='result',subject={'relative':'scenario'},value=result,source_ref='rea-dig')
    proc['dig-outside-procedure'] = dict(name='Out of bounds',steps=[step('effect','dig-bounds')],source_ref='rea-dig')
    rules['actions']['dig-outside'] = dict(name='Out-of-bounds dig',target={'relative':'target'},procedure_ref='dig-outside-procedure',source_ref='rea-dig')
    d['objects']['cell']['invocations'].append(dict(id='dig-outside-cell',trigger='dig-outside',steps=[step('action','dig-outside')],subject_bindings=[dict(slot='target',source='using-object')],source_ref='rea-dig'))
    for board in setup['boards']:
        bid = board['id']; grid = layout(board, setup); ids = [f'cell-{i//4}-{i%4}' for i in range(16)]
        win_parts = []
        for i, cid in enumerate(ids):
            prefix = bid+'-'+cid
            subject = {'instance_ref':cid}
            for suffix, right in [('zero',t['zero']),('flagged',t['flag']),('is-mine',t['mine'])]:
                ref = 'cell-visible' if suffix == 'flagged' else 'cell-grid'
                cond[prefix+'-'+suffix] = eq(ref,subject,right)
            cond[prefix+'-revealed-zero'] = eq('cell-visible',subject,t['zero'])
            cond[prefix+'-not-zero'] = dict(op='not',conditions=[prefix+'-revealed-zero'],source_ref='rea-dig')
            cond[prefix+'-expand'] = dict(op='all',conditions=[prefix+'-zero',prefix+'-not-zero'],source_ref='rea-dig')
            eff[prefix+'-reveal'] = dict(op='set',target_ref='cell-visible',subject=subject,value=grid[i],source_ref='rea-dig')
            if grid[i] == t['mine']:
                cond[prefix+'-hidden'] = eq('cell-visible',subject,t['hidden'],'rea-win')
                cond[prefix+'-won'] = dict(op='any',conditions=[prefix+'-hidden',prefix+'-flagged'],source_ref='rea-win')
            else:
                cond[prefix+'-won'] = eq('cell-visible',subject,grid[i],'rea-win')
            win_parts.append(prefix+'-won')
            # N expanded zeros is a strict upper bound. The last calls at depth N
            # remain present; a new zero there is unreachable (at least one mine).
            for depth in range(17):
                for root_call in ([False,True] if depth == 0 else [False]):
                    name = prefix + ('-root' if root_call else f'-depth-{depth}')
                    body = deepcopy(t['procedure']['steps'])
                    def specialize(items):
                        out = []
                        for item in items:
                            if item['kind'] == 'branch':
                                for branch in item['branches']:
                                    branch['condition'] = prefix+'-'+branch['condition']
                                    branch['steps'] = specialize(branch['steps'])
                                item['else_steps'] = specialize(item['else_steps'])
                                out.append(item)
                            elif item['ref'] == 'neighbors':
                                if depth < 16:
                                    for dr, dc in t['neighbor_offsets']:
                                        r,c = i//4+dr,i%4+dc
                                        if 0 <= r < 4 and 0 <= c < 4:
                                            out.append(step('procedure', f'{bid}-cell-{r}-{c}-depth-{depth+1}'))
                            elif item['ref'] == 'reveal':
                                out.append(step('effect',prefix+'-reveal'))
                            elif root_call:
                                label = {'ok':'ok','flagged-result':'flagged','mine-result':'mine'}[item['ref']]
                                out.append(step('effect','dig-'+label))
                        return out or [step('procedure','dig-noop')]
                    proc[name] = dict(name=name,steps=specialize(body),source_ref='rea-dig')
            action_id = prefix+'-dig'
            rules['actions'][action_id] = dict(name='Dig',target={'relative':'target'},procedure_ref=prefix+'-root',source_ref='rea-dig')
            obj_id = bid+'-cell-object-'+str(i)
            obj = deepcopy(d['objects']['cell'])
            obj['invocations'].append(dict(id='dig-cell',trigger='dig',steps=[step('action',action_id)],subject_bindings=[dict(slot='target',source='using-object')],source_ref='rea-dig'))
            d['objects'][obj_id] = obj
        cond[bid+'-won'] = dict(op='all',conditions=win_parts,source_ref='rea-win')
        instances = [dict(id=cid,object_ref=bid+'-cell-object-'+str(i),quantity=1) for i,cid in enumerate(ids)]
        bindings = []
        for i, cid in enumerate(ids):
            for ref,value in [('cell-row',i//4),('cell-column',i%4),('cell-visible','#'),('cell-grid',grid[i])]:
                bindings.append(dict(ref=ref,subject={'instance_ref':cid},value=value))
        for ref,value in [('rows',4),('columns',4),('mines',len(board['mines'])),('flags',0),('generation',1),('undo-index',0),('undo-enabled',False),('grid-initialized',True),('result',0)]:
            bindings.append(dict(ref=ref,subject={'relative':'scenario'},value=value))
        d['scenes'][bid] = dict(name=board['name'],source_ref='playable-setup',instances=instances)
        d['scenarios'][bid] = dict(name=board['name'],scene_ref=bid,source_ref='playable-setup',initial_state=bindings,action_refs=['flag','unflag','dig-outside']+[bid+'-'+cid+'-dig' for cid in ids],end_conditions=[dict(id='complete',outcome='win',condition=bid+'-won'),dict(id='mine-hit',outcome='loss',condition='mine-result')],authority='derived',assumptions=setup['assumptions'])
    # Base object is a reusable definition, not another logical cell.
    return d
