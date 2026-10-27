"""Run a previously validated playable bundle. No build tools run at play time."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from dodge_common import read_json, digest, require
from playable_session import PlayableSession

def load_bundle(path):
    model = read_json(path / 'resolved-game.json')
    report = read_json(path / 'validation-report.json')
    require(report['status'] == 'pass' and report['maturity'] == 'G4' and report['resolved_sha256'] == digest(model), 'bundle identity/validation failed')
    return model

def draw(session):
    view = session.view()
    print('    '+' '.join(str(i) for i in range(view['columns'])))
    for r in range(view['rows']):
        print(f'{r:2}  '+' '.join(view['visible'][r*view['columns']:(r+1)*view['columns']]))
    print(f"Flags: {view['flags']} / {view['mines']}   Outcome: {view['outcome'] or 'playing'}")

def main():
    parser = argparse.ArgumentParser(description='Fixed boards; first click is not protected. d/f/u ROW COL, reset, quit.')
    parser.add_argument('bundle',type=Path)
    parser.add_argument('--board',default='crossroads')
    parser.add_argument('--json',action='store_true',help='line-oriented JSON for automation')
    args = parser.parse_args()
    session = PlayableSession(load_bundle(args.bundle),args.board)
    print(json.dumps(session.view()) if args.json else 'Fixed layout. First click can hit a mine. Commands: d/f/u ROW COL, reset, quit.')
    if not args.json: draw(session)
    for line in sys.stdin:
        try:
            parts = line.split()
            if parts == ['quit']: break
            if parts == ['reset']:
                result = dict(board=session.reset())
            else:
                require(len(parts)==3 and parts[0] in ('d','f','u'), 'expected d/f/u ROW COL, reset or quit')
                result = session.move({'d':'dig','f':'flag','u':'unflag'}[parts[0]],int(parts[1]),int(parts[2]))
            if args.json: print(json.dumps(result))
            else: draw(session)
        except (ValueError,KeyError) as error:
            print(json.dumps(dict(error=str(error))) if args.json else str(error))

if __name__ == '__main__': main()
