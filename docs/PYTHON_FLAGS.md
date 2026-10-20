# Readable Python flag slice

The Python runtime reconstructs direct flag/unflag calls on the admitted synthetic 2x3 visible states. It does not implement a complete Minesweeper game, digging, mine generation, win/loss or enabled undo.

## Inspect the code

- `python/neutral_runtime.py`: interpretation of declared actions, predicates, ordered branches/effects, explicit invocation context and typed state. It does not switch on Minesweeper action/object IDs.
- `python/flag_adapter.py`: native input letters, coordinate selection, snapshot formatting and observed message text. It does not own cell-change conditions or counter deltas.
- `python/run_flags.py`: validates and resolves the current source before reading commands. There is no raw/unvalidated-model CLI option.
- `model/flag-rules.dodge.json`: reusable recovered rules. Scenario cells and initial counters derive from committed native sources.

## Use GitHub Actions

Run **DODGE flags validation**. In addition to G1–G4 and the 30 fatal-gate checks, it compares runtime outputs with all six native fixture sequences, repeats each three times, invokes the real CLI for each sequence, and validates/resolves the declared synthetic setup again before its perturbation check.

Download `dodge-flags-validation` for comparison records, effect traces, CLI transcripts, validation reports, perturbation evidence and `rea-example-python-source.zip`. The source ZIP is a readable source distribution, not a standalone executable. It contains the pinned-spec manifest and acquisition instructions; the external DODGE checkout is obtained separately.

## Run from source

With Python 3.12+, Git and the exact DODGE checkout described in `docs/DODGE_AUDIT.md`:

```sh
python -m pip install -r requirements-dodge.txt
python python/run_flags.py /path/to/pinned-dodge --case flag-revealed
```

Type commands, one per line:

```text
f 0 2
f 1 2
u 1 2
```

The first call rejects flagging the revealed cell, returning native result 2. The next two flag and unflag a hidden cell, returning 0. Each output line is JSON with the command, before/after native-compatible state, result and observed native message. End stdin to finish. In PowerShell, a pipeline works too:

```powershell
"f 0 2", "f 1 2", "u 1 2" | python python/run_flags.py C:\path\to\pinned-dodge --case flag-revealed
```

Malformed or out-of-scope input exits with code 2. Probe/adapter admission errors are not invented native gameplay results. Successful command execution exits 0; an action result of 2 or 8 remains inside the JSON record rather than becoming a process exit code.

## What the comparisons prove

The six retained native cases contain 11 action observations. Three runtime replays yield 33 exact comparisons, including result, all captured before/after fields, and message. Six separate CLI invocations provide 11 additional comparisons through the shared adapter/runtime. Rejected actions leave captured native state unchanged; the separate output-result binding can change.

The source-map and runtime effect traces connect the observed transitions to resolved conditions/effects. The executable consumes the resolved model without recovering rules from fixture expected outputs. Native fixture outputs are used by the test oracle and the presentation message table, not the transition interpreter.

## Explicit authority perturbation

`model/synthetic-setup.json` declares a separate setup based on `flag-revealed`: its revealed cell becomes unknown. Original native fixture bytes and the evidence lock remain unchanged. The optional scenario is derived from this new, hash-pinned source; the recovered action graph stays identical. The same command changes from result 2 to result 0 after revalidation/resolution.

Application profile 0.2.0 adds validation of this explicitly declared scenario variant while retaining the original six fixture checks and exact recovered-rule checks. It does not authorize changed rule deltas, mine caps, arbitrary fixture mutation, or invented native observations. The synthetic result is not claimed as equivalence to the unchanged original fixture.

## Maturity and next decision

The demonstrated maturity is G5 for this bounded mechanic, with a CLI projection consuming the same neutral runtime. No formal G6 export-release, full game, browser adapter, executable package or Pages deployment is claimed. After milestone 8, stop and reassess the next small mechanic or presentation scope rather than silently broadening the experiment.
