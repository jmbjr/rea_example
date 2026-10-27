# Playable Python session (milestone 10)

This is the terminal assessment build. Browser delivery remains milestones 11–12.
Three curated 4x4 boards are supported: `corners`, `crossroads`, and `pockets`.
They are fixed, concealed layouts. Restart repeats the layout. **First clicks can
hit a mine.** This is source/debug-assisted reconstruction, not blind recovery or
whole-game equivalence. Undo, chording, AI and random generation are absent.

## Try the downloadable build

In the **Playable Python acceptance** Actions run, download
`playable-python-evidence`, unzip it, then unzip `minesweeper-python.zip`.
The inner archive contains `START_HERE.txt`, the validated model, and readable
Python source. Python 3.10+ is needed; playing needs no pip dependencies.

Windows, from the extracted directory:

```console
py python/play.py bundle --board crossroads
```

Linux/macOS:

```console
python3 python/play.py bundle --board crossroads
```

Commands use zero-based row/column coordinates: `d 0 0` digs, `f 1 2` flags,
`u 1 2` unflags, `reset` restarts and `quit` exits. Choose another board with
`--board corners` or `--board pockets`. A terminal session rejects further moves
on win/loss until reset. It preserves the native action code separately from the
session outcome. `--json` exposes the same adapter for automated tests.

## Rebuild and verify

```console
python -m pip install -r requirements-dodge.txt
python tools/build_playable.py /path/to/pinned-DODGE build/playable
python python/play.py build/playable --board crossroads
cc -std=c99 -O0 -g -I /path/to/pinned-minesweeper/src target/playable-oracle.c /path/to/pinned-minesweeper/src/minesweeper.c -o build/native-oracle
python tools/check_playable.py /path/to/pinned-DODGE build/native-oracle build/acceptance
python tools/package_playable.py build/acceptance/bundle build/minesweeper-python.zip
```

Exact commits remain in `spec/dodge-pin.json` and `target/README.md`. The new
workflow acquires these pins, compiles unchanged upstream code into the retained
probe, reruns original flag gates/runtime tests, and publishes evidence even on
failure. The downloadable application is packaged only after acceptance passes.

## Authority and implementation

- `model/playable-setup.json` owns board dimensions and mine positions. Neighbor
  counts are setup derivation, not native random-generator equivalence. There is
  no lookup of expected native action outputs while assembling the model.
- `model/dig-template.json` is the source-backed canonical template, not a new
  DODGE language extension. It declares branch order, results, tokens and neighbor
  order. `tools/playable_model.py` specializes it into pinned-schema DODGE
  branches, conditions, effects and procedures. Historical flag rules are reused.
- Each cell has procedures for depth 0 through 16 plus a root entry. Every
  expanding zero is marked before neighbor calls. A path cannot expand the same
  zero twice. At least one of 16 cells is a mine; therefore fewer than 16 distinct
  zeros can expand. Final non-expanding calls at depth 16 remain in the graph;
  entering a new zero there is unreachable under admitted setup. Each child calls
  only the next depth. No cyclic procedures, recursion extension or UI flood
  implementation is needed. Nested results are discarded; the root writes its
  result after expansion. The runtime uses an explicit stack.
- The required profile locks reviewed templates/evidence, verifies canonical
  specialization including all ordered neighbor calls, bindings and terminal
  conditions, and checks the exact resolved model. It shares the compiler when
  checking specialization; it is **not an independent proof of compiler
  correctness**. Independent differential observations supply that evidence for
  the exercised cases. Unknown features still fail admission.
- `python/neutral_runtime.py` interprets generic predicates/branches/effects.
  `python/playable_session.py` owns admission, ordered model end-condition
  evaluation and reset. `python/play.py` owns command parsing/rendering. None
  contains a flood or game-specific victory algorithm. The diagnostic full
  snapshot is separate from the public view; the view conceals underlying mines.
- Core probes continue after terminal events; session comparisons stop at the
  first CLI-equivalent terminal observation. Out-of-bounds dig has an explicit
  model result path for direct-core comparisons, while session input rejects
  invalid coordinates before execution. Flag/unflag bounds remain admission-only.
- End conditions are evaluated in declared array order: model win first, then
  loss from root result. No persistent native loss field is invented. A rejected
  input or post-terminal move leaves state untouched. Native flagged-zero flag
  counter drift is preserved.

G1–G4 are required before model publication; a failed stage removes even stale
resolved output. Bundle loading verifies the report/model hash. This detects
accidental mixing/tampering; it is not a cryptographic signature from a trusted
release authority. The profile and toolchain hashes bind reports to source.

## What acceptance establishes

Thirteen historical native cases plus 108 fresh cases exercise the three boards:
every first dig, every flag/dig/unflag target, safe-cell wins, flagged wins, bounds,
and deterministic mixed commands. Three replay passes compare every complete
before/after native snapshot and result. Terminal prefixes, blocked later input,
reset, CLI execution, package extraction and loader identity are checked too.
A separate synthetic layout changes the same click from mine/loss to safe/playing
without changing the interpreter or recovered template; no native-equivalence
claim is made for that synthetic variant.

Fatal negatives cover missing/reordered neighbors, weakened victory, missing
state, terminal removal/order, changed results, reference cycles, missing static
subjects, unsupported fields, resolved tampering and stale output. The original
30 flag negative cases and native/CLI comparisons remain required regressions.

The measured resolved model is approximately 1.9 MB as indented JSON. Build and
comparison timing is retained in `acceptance.json`; browser load cost is still
unmeasured. All declared assessment boards remain 4x4. This does not establish all
possible command sequences, puzzle difficulty, browser usability or a G6 release.
