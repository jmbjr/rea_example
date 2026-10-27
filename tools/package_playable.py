"""Package the admitted terminal build; standard-library Python at runtime."""
import argparse
from pathlib import Path
import zipfile
from dodge_common import read_json, digest, require, file_hash
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('bundle',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
r=read_json(a.bundle/'resolved-game.json');report=read_json(a.bundle/'validation-report.json')
require(report['status']=='pass' and report['resolved_sha256']==digest(r),'unvalidated package')
a.output.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(a.output,'w',zipfile.ZIP_DEFLATED) as z:
    for name in ['resolved-game.json','validation-report.json','candidate.dodge.json','source-map.json']:
        z.write(a.bundle/name,'bundle/'+name)
    for name in ['neutral_runtime.py','playable_session.py','play.py']:
        z.write(ROOT/'python'/name,'python/'+name)
    z.write(ROOT/'tools/dodge_common.py','tools/dodge_common.py')
    z.write(ROOT/'target/LICENSE.minesweeper.txt','LICENSE.minesweeper.txt')
    z.writestr('START_HERE.txt','Unzip first. Python 3.10+; no pip packages needed to play.\nWindows: py python/play.py bundle --board crossroads\nLinux/macOS: python3 python/play.py bundle --board crossroads\nCommands: d ROW COL, f ROW COL, u ROW COL, reset, quit. Coordinates start at zero.\nOther boards: corners, pockets. Restart repeats a fixed layout; first click can hit a mine.\nThis is a source/debug-assisted, fixed-board reconstruction, not full native-game equivalence.\n')
print('PLAYABLE_PACKAGE '+str(a.output)+' sha256='+file_hash(a.output))
