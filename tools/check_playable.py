"""Native differential acceptance, terminal-session boundaries and fatal gates."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import time
sys.path.insert(0,str(Path(__file__).resolve().parents[1] / 'python'))
from build_playable import build
from dodge_common import read_json, fixture_records, require, digest, file_hash, ValidationError
from playable_model import assemble, layout
from playable_session import PlayableSession
from play import load_bundle

ROOT = Path(__file__).resolve().parents[1]
TRIGGERS = {'d':'dig','f':'flag','u':'unflag'}

def capture(binary, output):
    setup = read_json(ROOT/'model/playable-setup.json')
    fixtures = []
    for board in setup['boards']:
        grid = layout(board,setup)
        cases = [(f'dig-{i}',f'd {i//4} {i%4}\n') for i in range(16)]
        cases += [(f'flag-dig-{i}',f'f {i//4} {i%4}\nd {i//4} {i%4}\nu {i//4} {i%4}\n') for i in range(16)]
        safe = ''.join(f'd {i//4} {i%4}\n' for i in range(16) if grid[i] != '!')
        flags = ''.join(f'f {i//4} {i%4}\n' for i in board['mines'])
        cases += [('win',safe),('flagged-win',flags+safe),('bounds','d -1 0\nd 4 0\nd 0 4\n')]
        rng = random.Random(20261027)
        cases += [('mixed',''.join(f'{rng.choice("dfu")} {rng.randrange(4)} {rng.randrange(4)}\n' for _ in range(100)))]
        for name, commands in cases:
            runs = []
            for _ in range(3):
                run = subprocess.run([str(binary.resolve()),grid,'#'*16],input=commands,text=True,capture_output=True,timeout=10)
                require(run.returncode == 0 and not run.stderr,'native capture failed')
                runs.append(dict(returncode=run.returncode,stdout=run.stdout,stderr=run.stderr))
            require(all(r == runs[0] for r in runs),'native replay diverged')
            fixtures.append(dict(case=board['id']+'-'+name,board=board['id'],stdin=commands,repetitions=3,runs=runs,target_sha256=file_hash(binary)))
    output.mkdir(parents=True,exist_ok=True)
    (output/'native-fixtures.json').write_text(json.dumps(fixtures,indent=2)+'\n')
    return fixtures

def compare(model, fixtures):
    comparisons, prefixes = 0,0
    digests = []
    for fixture in fixtures:
        records = fixture_records(fixture)
        scenario = fixture.get('board','corners')
        traces = []
        for _ in range(3):
            core = PlayableSession(model,scenario)
            require(core.snapshot() == records[0]['setup'],'initial state differs: '+fixture['case'])
            events = []
            for record in records[1:]:
                observed = core.core_move(TRIGGERS[record['action']],record['row'],record['column'])
                require(observed == {k:record[k] for k in ['before','after','result']},'core mismatch: '+fixture['case']+' '+str(record))
                events.append(dict(record=observed,trace=deepcopy(core.runtime.trace)))
                comparisons += 1
            traces.append(digest(events))
        require(len(set(traces)) == 1,'Python replay diverged')
        digests.append(dict(case=fixture['case'],trace_sha256=traces[0]))
        session = PlayableSession(model,scenario)
        for record in records[1:]:
            # Session input rejects outside-board coordinates; direct core above
            # verifies native bounds result separately.
            if not (0 <= record['row'] < 4 and 0 <= record['column'] < 4):
                before = session.view()
                try: session.move(TRIGGERS[record['action']],record['row'],record['column'])
                except ValidationError: pass
                else: raise AssertionError('out-of-bounds session admission')
                require(session.view() == before,'invalid input mutated session')
                continue
            observed = session.move(TRIGGERS[record['action']],record['row'],record['column'])
            expected_outcome = 'win' if record['after']['won'] else 'loss' if record['result']==7 else None
            require(observed['result'] == record['result'] and observed['outcome'] == expected_outcome,'session outcome mismatch')
            require(session.snapshot() == record['after'],'session state mismatch')
            prefixes += 1
            if record['cli_would_stop']:
                before = deepcopy(session.runtime.scope)
                try: session.move('dig',0,1)
                except ValidationError: pass
                else: raise AssertionError('terminal session accepted move')
                require(session.runtime.scope == before,'terminal rejection mutated state')
                break
        session.reset()
        require(session.snapshot() == records[0]['setup'] and session.terminal is None,'reset changed setup')
    return dict(core_comparisons=comparisons,session_prefix_comparisons=prefixes,replay_trace_hashes=digests)

def negatives(checkout, output, d):
    cases = {}
    def omit_neighbor(c):
        c['rules']['procedures']['corners-cell-0-3-root']['steps'][0]['branches'][0]['steps'].pop(1)
    cases['omitted-neighbor'] = omit_neighbor
    def swap_neighbor(c):
        steps=c['rules']['procedures']['corners-cell-0-3-root']['steps'][0]['branches'][0]['steps']
        steps[1],steps[2]=steps[2],steps[1]
    cases['changed-neighbor-order'] = swap_neighbor
    cases['weak-win'] = lambda c:c['rules']['conditions']['corners-won']['conditions'].pop()
    cases['missing-binding'] = lambda c:c['scenarios']['corners']['initial_state'].pop(0)
    cases['missing-terminal'] = lambda c:c['scenarios']['corners'].pop('end_conditions')
    cases['wrong-terminal-order'] = lambda c:c['scenarios']['corners']['end_conditions'].reverse()
    cases['wrong-root-result'] = lambda c:c['rules']['effects']['dig-mine'].update(value=0)
    cases['condition-cycle'] = lambda c:c['rules']['conditions']['corners-won'].update(conditions=['corners-won'])
    cases['static-missing'] = lambda c:c['rules']['effects']['corners-cell-0-3-reveal'].update(subject={'instance_ref':'absent'})
    cases['procedure-cycle'] = lambda c:c['rules']['procedures']['corners-cell-0-3-depth-1']['steps'].append(dict(kind='procedure',ref='corners-cell-0-3-depth-1'))
    cases['unsupported-field'] = lambda c:c['scenarios']['corners'].update(extensions={'unhandled':True})
    for name, edit in cases.items():
        c = deepcopy(d); edit(c); directory=output/name
        try: build(ROOT,checkout,directory,candidate=c)
        except ValidationError: pass
        else: raise AssertionError('accepted '+name)
        require(not (directory/'resolved-game.json').exists(),'failure published '+name)
    def tamper(r): r['scenarios'][0]['end_conditions'].reverse()
    try: build(ROOT,checkout,output/'resolved-terminal-tamper',candidate=d,resolved_edit=tamper)
    except ValidationError: pass
    else: raise AssertionError('accepted resolved tampering')
    require(not (output/'resolved-terminal-tamper/resolved-game.json').exists(),'failed G4 published output')
    # Verify a previously passing output is removed on a later failed validation.
    directory=output/'reuse'; build(ROOT,checkout,directory,candidate=d)
    c=deepcopy(d); cases['missing-binding'](c)
    try: build(ROOT,checkout,directory,candidate=c)
    except ValidationError: pass
    require(not (directory/'resolved-game.json').exists(),'stale validated output survived failure')
    return list(cases)+['resolved-terminal-tamper','stale-output']

def perturb(checkout, output, original):
    # A separate source tree gives the modified owned setup an honest hash.
    with tempfile.TemporaryDirectory() as temporary:
        root=Path(temporary)/'variant'
        shutil.copytree(ROOT,root,ignore=shutil.ignore_patterns('.git','build','__pycache__'))
        setup=read_json(root/'model/playable-setup.json')
        setup['boards'][0]['mines']=[1,15]
        (root/'model/playable-setup.json').write_text(json.dumps(setup,indent=2)+'\n')
        _,variant,report=build(root,checkout,output)
        before=PlayableSession(original,'corners'); after=PlayableSession(variant,'corners')
        a=before.move('dig',0,0); b=after.move('dig',0,0)
        require(a['result']==7 and a['outcome']=='loss' and b['result']==0 and b['outcome'] is None,'layout authority did not change execution')
        return dict(synthetic=True,original=a,variant=b,validated_resolved_sha256=report['resolved_sha256'],executor_sha256=file_hash(ROOT/'python/neutral_runtime.py'))

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('checkout',type=Path);parser.add_argument('binary',type=Path);parser.add_argument('output',type=Path)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    start=time.perf_counter()
    d,r,report=build(ROOT,args.checkout,args.output/'bundle')
    build_seconds=time.perf_counter()-start
    fresh=capture(args.binary,args.output)
    historical=[read_json(p) for p in sorted((ROOT/'evidence/step9/oracle').glob('*.json')) if p.name!='acceptance.json']
    start=time.perf_counter(); results=compare(r,historical+fresh); execution_seconds=time.perf_counter()-start
    negative=negatives(args.checkout,args.output/'negative',d)
    variant=perturb(args.checkout,args.output/'synthetic',r)
    (args.output/'perturbation.json').write_text(json.dumps(variant,indent=2)+'\n')
    # Actual terminal adapter, same admitted bytes and session.
    cli=subprocess.run([sys.executable,str(ROOT/'python/play.py'),str((args.output/'bundle').resolve()),'--board','corners','--json'],input='d 0 0\nd 0 1\nreset\nf 0 0\nu 0 0\nquit\n',text=True,capture_output=True)
    require(cli.returncode==0 and not cli.stderr,'CLI failed '+cli.stderr)
    lines=[json.loads(x) for x in cli.stdout.splitlines()]
    require(lines[1]['outcome']=='loss' and 'error' in lines[2] and lines[3]['board']['outcome'] is None and lines[5]['result']==0,'CLI/reset mismatch')
    (args.output/'cli.json').write_text(json.dumps(lines,indent=2)+'\n')
    loaded=load_bundle(args.output/'bundle');require(digest(loaded)==digest(r),'bundle loader changed model')
    (args.output/'bundle'/'resolved-game.json').write_text(json.dumps(r))
    altered=deepcopy(r);altered['scenarios'][0]['values']['flags']=1
    (args.output/'bundle'/'resolved-game.json').write_text(json.dumps(altered))
    try: load_bundle(args.output/'bundle')
    except ValidationError: pass
    else: raise AssertionError('loader accepted tampering')
    (args.output/'bundle'/'resolved-game.json').write_text(json.dumps(r,indent=2)+'\n')
    repeated=assemble(ROOT);require(digest(d)==digest(repeated),'nondeterministic assembly')
    receipt=dict(status='pass',maturity='bounded G5; no browser/G6 release claim',boards=3,historical_cases=len(historical),fresh_cases=len(fresh),
        **results,negative_cases=negative,build_seconds=build_seconds,comparison_seconds=execution_seconds,
        candidate_sha256=report['candidate_sha256'],resolved_sha256=report['resolved_sha256'],
        resolved_bytes=(args.output/'bundle/resolved-game.json').stat().st_size,
        binary_sha256=file_hash(args.binary),upstream='c7cadf1f7ed57d950b400d965a7d3bbab5e50bed',
        runtime_sha256={p.name:file_hash(p) for p in (ROOT/'python').glob('*.py')})
    (args.output/'acceptance.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k!='replay_trace_hashes'},indent=2))
if __name__=='__main__':main()
