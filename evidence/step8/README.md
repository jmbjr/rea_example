# Milestone 8: readable Python execution

[GitHub Actions run 39359003853](https://github.com/jmbjr/rea_example/actions/runs/39359003853) passed on Ubuntu 24.04 for source commit `ff10ab4800c7e95b3c810b52104c159ccc21687b`. All validation, runtime comparison and source packaging steps succeeded.

Download [the source/evidence artifact](https://github.com/jmbjr/rea_example/actions/runs/39359003853/artifacts/12236064618). It contains `rea-example-python-source.zip`, full baseline/synthetic models, source maps, stage diagnostics, runtime traces and CLI outputs. Artifact expiry: 2026-11-19; identity and digest are retained in `artifact.json`. [Source usage and code guide](../../docs/PYTHON_FLAGS.md).

## Retained evidence

`runtime-acceptance.json`, `perturbation.json`, `gate-acceptance.json` and `validation-report.json` are exact JSON payloads extracted from hosted job log markers. The six per-case JSON files are local reproductions with the same source code and native fixtures; the complete local acceptance and perturbation payloads matched the hosted payloads exactly. Original native oracle bytes and executable identities remain in [milestone 5](../step5/README.md).

The gate-only acceptance report's legacy `runtime_execution` wording describes that suite, which does not invoke gameplay; the separate runtime acceptance report establishes execution. The historical milestone 7 reports remain unchanged.

Current canonical candidate SHA-256: `2f499d041594a0556e01b12edc5927fa2fee3d610474d9fc0b35b0441571455f`. Resolved SHA-256: `28429061762636e06202bd82d9c3b51d2625a9919b82b06b747645e068142468`. Required application profile 0.2.0 admits the separately declared synthetic source while preserving the original six fixture and recovered-rule checks. This explains the identity change from milestone 7; it is not changed native evidence.

## Execution claims matrix

| Claim | Evidence | Boundary |
| --- | --- | --- |
| Flag unknown cell updates cell/counter and returns 0 | `flag-success.json`, `repeated-sequence.json` | Direct calls on admitted initialized visible state |
| Flag flagged/revealed cell returns 2 without changing captured state | `flag-already-flagged.json`, `flag-revealed.json` | Separate output-result binding may change |
| Unflag flagged cell updates cell/counter and returns 0 | `unflag-success.json`, `repeated-sequence.json` | Undo disabled |
| Unflag unknown cell returns 8 without changing captured state | `unflag-unflagged.json` | Captured native fields only |
| All six fixture sequences match native result, board, counter, message and unchanged fields | `runtime-acceptance.json`, six per-case records | 11 actions, repeated three times: 33 exact comparisons |
| Real CLI consumes shared validated model/runtime | Same six records, CLI transcripts | 11 additional exact comparisons; no formal G6 export-release claim |
| Replay is deterministic | Three observation/effect-trace repetitions per case | Explicit fixture setup, no random generation |
| Owned semantic setup controls execution without duplicated Python rules | `perturbation.json`: `f 0 2` changes result 2 → 0; recovered rule graph unchanged | New synthetic source, not unchanged-native equivalence |
| Required validation blocks execution | 30 fatal negative cases in `gate-acceptance.json`; altered delta rejected before runtime | No resolved artifact survives a rejected build |
| Out-of-scope coordinate cannot mutate state | Runtime acceptance admission check | Adapter rejection, not invented native error behavior |

## Actual maturity and reassessment

This establishes bounded G5 for flag/unflag, with a readable source distribution and a CLI projection through shared neutral semantics. The generic executor owns interpretation; the adapter owns coordinates, native formatting and observed messages. Expected native transition outputs are comparison evidence, not execution rules.

This remains a source/debug-assisted REA experiment on controlled 2x3 synthetic setups. It does not establish whole-game equivalence, blind binary recovery, mine generation/dig/flood fill, win/loss, enabled undo, browser execution, a formal export release or a fix for the upstream pre-dig CLI crash. The validator remains a strict supported subset of pinned DODGE rather than a general implementation.

Milestones 1–8 are complete. Stop here and reassess the next small mechanic or presentation scope before adding more steps. GitHub Pages remains a later delivery option.
