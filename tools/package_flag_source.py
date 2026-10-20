"""Package tracked experiment sources, not a platform executable."""
import argparse
from pathlib import Path
import subprocess
import zipfile

parser = argparse.ArgumentParser()
parser.add_argument('output', type=Path)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
paths = subprocess.check_output(['git', '-C', str(root), 'ls-files', '-z']).decode().split('\0')
args.output.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(args.output, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
    for name in sorted(x for x in paths if x):
        archive.write(root / name, 'rea_example/' + name)
print('Source archive: ' + str(args.output))
