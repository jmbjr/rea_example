# REA → DODGE → Python

## Playable Python assessment build

Milestone 10 adds digging, empty-area expansion, flag/unflag, win/loss and restart on three fixed 4x4 boards. [Download/run instructions and authority boundaries](docs/PLAYABLE_PYTHON.md). The **Playable Python acceptance** Actions artifact contains `minesweeper-python.zip`; Python 3.10+ is sufficient to play. Browser/Pages delivery remains the next milestones.


An experiment in recovering a small application's behavior from a compiled binary, representing the recovered game semantics in DODGE, and building an understandable Python implementation.

## Status

Milestones 1–8 complete. The bounded flag/unflag behavior now executes in readable Python through validated DODGE-derived semantics. [Hosted execution evidence](evidence/step8/README.md) records 33 native replay comparisons, 11 CLI comparisons, deterministic replay, a synthetic authority perturbation and 30 fatal validation cases. [Run the Python source](docs/PYTHON_FLAGS.md) or download the source/evidence artifact linked in the receipt.

The scope remains direct flag/unflag calls on controlled visible states, with undo disabled. The upstream pre-dig CLI crash remains unfixed. This is source/debug-assisted reconstruction, not whole-game or blind-binary equivalence. No browser deployment or formal G6 export release is claimed.

DODGE draft 0.2.1 is pinned to `9af5804719bc4dc421d1cd76d3587f5b678d3f81`; see the [authority audit](docs/DODGE_AUDIT.md), [validation pipeline](docs/DODGE_PIPELINE.md), [native contract](evidence/step5/README.md), and [REA findings](evidence/step4-hosted/README.md). Milestone 9 has now established the [native playable contract and evidence](evidence/step9/README.md). The [next bounded implementation](docs/PLAYABLE_CONTRACT.md) adds dig, expansion and terminal sessions, followed by browser delivery for user assessment. These new mechanics are not yet implemented; the existing G5 claim remains flag/unflag only.

## Working decisions

- Use official REA (`morluto/rea`) as a separate tool. Fork it only if changes to REA become necessary.
- Start with a small open-source game or application with a manageable, deterministic command-line interface.
- First reconstruction target: readable Python, runnable from source. Packaging into an executable is a separate later step.
- Use `jmbjr/DODGE` draft `v0.2.1` as the working format baseline because it includes structured rules and executable bindings. It is a draft, not the official 0.2.0 baseline. Pin a commit and schema before implementation.
- Keep the original source as evaluation ground truth, separate from initial binary-only analysis. A source-informed experiment must be labeled as such.

## Experiment stages

1. Select the target; record upstream license, commit, build commands, and toolchain.
2. Build a baseline binary; record its SHA-256 and representative input/output traces.
3. Install a pinned REA version and verify an available native-analysis provider. CLI use can be evaluated independently of MCP integration.
4. Analyze the binary with REA; preserve actual tool output, evidence, limitations, and provisional interpretations.
5. Map recovered objects, state, actions, and end conditions into DODGE. Preserve unsupported semantics in declared sidecars/extensions; do not silently invent executable rules.
6. Validate the exact schema, core semantics, required application profiles, and resolved neutral model before target generation. Keep incomplete gates explicitly incomplete.
7. Implement a readable Python consumer of the resolved semantics and compare behavior against baseline traces.
8. Change an authoritative rule and verify the runtime follows it. Add negative validation cases and deterministic replay evidence.
9. Choose subsequent variants: rule changes, alternate presentation, another language/engine, or platform packages.

## Planned layout

These directories will be created when their corresponding stage has real content:

- `target/`: provenance, license, pinned source reference, build instructions
- `evidence/`: binary hashes, REA captures, input/output traces, claims matrix
- `model/`: DODGE document and declared canonical sources/sidecars
- `tools/`: validation and neutral resolution
- `python/`: first readable runtime and command-line adapter
- `tests/`: behavioral comparisons, negative cases, and authority perturbations

## Success criterion

A bounded behavior recovered using REA is represented with traceable DODGE semantics, executes in Python, and matches the original binary on recorded cases. Changes to modeled authoritative inputs affect the Python behavior without editing duplicated rule constants.

REA supplies inspection evidence; the evidence-to-DODGE mapping and Python implementation are work performed by this experiment. No automatic binary-to-DODGE compiler is assumed.
