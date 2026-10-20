"""Validate, resolve, then run stdin commands through the shared interpreter."""
import argparse
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from build_flags import build
from dodge_common import ValidationError
from flag_adapter import FlagSession

def main():
    parser = argparse.ArgumentParser(description='Direct flag/unflag slice; commands: f ROW COL or u ROW COL')
    parser.add_argument('dodge_checkout', type=Path)
    parser.add_argument('--case', default='flag-revealed')
    args = parser.parse_args()
    try:
        with tempfile.TemporaryDirectory(dir=ROOT.parent) as output:
            _, model, _ = build(ROOT, args.dodge_checkout, output)
            session = FlagSession(model, args.case, ROOT)
            for line in sys.stdin:
                if line.strip():
                    print(json.dumps(session.command(line), separators=(',', ':')))
        return 0
    except (ValidationError, ValueError, KeyError) as error:
        print('Rejected: ' + str(error), file=sys.stderr)
        return 2

if __name__ == '__main__':
    sys.exit(main())
