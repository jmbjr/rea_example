# Milestone 4 complete: first hosted REA analysis

## Verified run

- [GitHub Actions run 39089679725](https://github.com/jmbjr/rea_example/actions/runs/39089679725), attempt 1, completed successfully on 2026-10-18 UTC.
- Workflow/source commit: 3283f345b39c7a8708809535643dfe146592babb.
- Ubuntu 24.04.5 x86_64 runner image 20261012.334.1; REA npm 6.5.0; Node 24.19.0; Temurin JDK 21.0.12+1; Ghidra 12.1.4.
- Official Ghidra archive SHA-256 verification passed.
- Target upstream remains c7cadf1f7ed57d950b400d965a7d3bbab5e50bed with the previously documented CLI-only stubs.
- Runner executable SHA-256: fb83433214e68ae8e82409266ff5818a82906db063ec7a0772382536213ec7aa. This differs from the earlier workspace binary; all findings below bind to the runner hash.
- Four fixture sequences each matched three times on the hosted runner.
- REA version, scoped doctor, overview, flag decompilation and unflag decompilation all returned exit 0.
- Full [rea-native-evidence artifact](https://github.com/jmbjr/rea_example/actions/runs/39089679725/artifacts/12122575224): 24 files, ZIP SHA-256 7bb0150ee9c56dcc66fb049049b67c10f3b6a1dd86f252a9562acf5aa8b6acd6. Current expiry 2026-11-17T02:20:55Z.

The two complete REA evidence records printed in job logs were parsed as JSON and retained unchanged in meaning in this directory. Other raw outputs, executable/license, environment details and dependency lock remain in the linked artifact. Preserve them before expiry if needed.

## Bounded findings

| Finding | Evidence | Boundary |
| --- | --- | --- |
| Flag checks visible cell for '#'; on that branch it calls the visible-cell setter with 'F', increments flags, and returns 0 | msw_flag.json, normalized_result | Static decompilation; helper internals not inspected in this pass |
| Otherwise flag returns 2 | msw_flag.json, normalized_result | Numeric result only; user-facing error interpretation requires caller/message evidence |
| Unflag checks visible cell for 'F'; on that branch it calls the setter with '#', decrements flags, and returns 0 | msw_unflag.json, normalized_result | Static decompilation, not proof of every runtime side effect |
| Otherwise unflag returns 8 | msw_unflag.json, normalized_result | Caller behavior not established by this function alone |
| Visible flag/unflag transitions agree with recorded CLI behavior after a dig | step 3 flag-unflag fixture and hosted replay logs | Runtime corroboration of visible transitions; counter is not directly observed by this fixture |

Evidence IDs:

- Flag: ev_53abb1dcac9725a9fe258a93540c949eea02ac3b6da982e8ca220d920e740db9
- Unflag: ev_a9089ac87bea7ef4d386225c7017fc72a385b1fb04f8b199336571740b4ab0d7

Both records report provider Ghidra 12.1.4, operation procedure_pseudo_code, observed confidence, shipped-artifact authority, and matching subject SHA-256. Their analysis-profile digest is 9c7f6b24be69294e61da046e4583e3856cb9e40433b149c1bf8bb534d2fe03ef.

## Interpretation and limits

This establishes that the hosted native-analysis route works on the actual experiment executable and recovers a bounded state transition. The target retains debug symbols/types; function names were already known through source exposure. Counter increments/decrements were also previously exposed in commit diffs. This is corroborated recovery, not independent blind discovery or a stripped-binary benchmark.

Ghidra pseudocode is not original source. A getter/setter name does not prove its full implementation. Bounds checks, undo effects, full state shape, flag count invariants, dig/flood-fill, generation, win/loss and pre-dig CLI crash behavior have not been fully recovered by REA. Do not generalize this finding to complete game reconstruction.

The scratch-host blocker remains documented in evidence/step4; GitHub Actions cleared it by supplying a suitable environment. No Windows setup is required.

## Roadmap reassessment

The initial four milestones are complete. Stop implementation here as issue #1 requires. The defensible next scope is the flag/unflag transition and its immediate state/helper/caller contract, rather than the whole game. Before modeling, pin the exact DODGE draft revision/schema and resolve those dependencies. Python source remains the first reconstruction target.

GitHub Pages can later present a static browser version or download links. It cannot run native REA/Ghidra. The browser runtime/adapter choice remains deferred until the bounded reconstruction is established.
