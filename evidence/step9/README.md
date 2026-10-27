# Milestone 9 — playable native contract

[Hosted run 40549592617](https://github.com/jmbjr/rea_example/actions/runs/40549592617) succeeded for source commit `328fad6ee0f071888f356a516fef4fd39ea4dc01`. Ubuntu 24.04, REA 6.5.0 and verified Ghidra 12.1.4 were used. All 17 REA operations passed, including 14 focused decompilations. Existing CLI replay and flag oracle checks also passed.

The new native probe captured **13 fixed-layout cases, each repeated three times: 210 action observations**. It calls unchanged native functions, supplies an explicit initialized 4x4 layout, and disables undo. Dig, expansion, numbered/flagged cells, mine hit, win with/without flags, bounds, flag-before-dig on initialized setup, repeated operations and raw post-terminal calls are covered.

## Evidence identities and retention

- REA baseline executable SHA-256: `fb83433214e68ae8e82409266ff5818a82906db063ec7a0772382536213ec7aa` (same analyzed bytes as earlier baseline).
- Separate playable probe executable SHA-256: `29bafb6daf9160935d5cf33546c450aefe8d0b8164a3ef97fcae3eb764e41d75`.
- Upstream unchanged at `c7cadf1f7ed57d950b400d965a7d3bbab5e50bed`; source file hashes and exposure are in `source-identity.json`.
- [Full hosted artifact](https://github.com/jmbjr/rea_example/actions/runs/40549592617/artifacts/12754173588), expiry 2026-11-26. Its identity/digest are retained in `artifact.json`. It includes executables/licenses, environment/toolchain/dependency lock, all command records and original stdout/stderr files.
- `oracle/*.json` are complete hosted JSON fixture payloads extracted from `PLAYABLE_FIXTURE` job-log markers; `oracle/acceptance.json` is the hosted acceptance marker. All fixture return codes/stdout/stderr repetitions also matched a local run exactly; executable hashes differ by build environment.
- `rea/*.json` preserve complete parsed JSON outputs emitted in the job log for all 14 decompilations, including evidence IDs, target/provider identity, pseudocode, analysis profile, authority and limitations. Formatting has been normalized to JSON; these are not hashes of original stdout bytes. Every extracted payload parsed completely, without a truncated log preview.

Reproduce the native capture after obtaining the clean pinned upstream checkout:

```sh
gcc -std=c99 -g -Wall -Wextra -I/path/to/upstream/src /path/to/upstream/src/minesweeper.c target/playable-oracle.c -o build/playable-oracle
python tools/capture_playable_oracle.py build/playable-oracle build/playable
```

Create `build/` first if needed. REA acquisition and commands are in the pinned Actions workflow; `capture_rea.py --playable` adds six decompilations to the established set. Function names and source were already exposed; no blind discovery claim is made.

## Reviewed findings and next boundary

[Playable contract, claims matrix and DODGE/browser compatibility audit](../../docs/PLAYABLE_CONTRACT.md) record the reviewed behavior and implementation boundary. Important findings include empty-cell expansion preceding flag rejection (and leaving counter drift), victory not requiring flags, and core functions continuing after terminal observations while the CLI stops.

The `cli_would_stop` field is probe-derived from reviewed caller logic; it is not a native stored terminal state. Long sequences deliberately include raw post-terminal calls. A playable session comparison must use the prefix through the first terminal event, while direct-core comparisons may use the full sequence. The 4x4 flood fixture can win on one dig and is not claimed as a sufficiently interesting assessment puzzle.

The exact DODGE pin and six hashes were reverified. A bounded acyclic dig-procedure compilation is selected for implementation and comparison in milestone 10. It is not yet implemented or proven equivalent. No DODGE pin change, schema extension, new Python gameplay mechanic or browser deployment is included in this evidence milestone.

Native behavior is sufficiently defined to proceed with a bounded implementation. No user help is needed. Next: milestone 10, then a shared-runtime browser build and Pages play assessment. Existing maturity remains G5 for flag/unflag; new dig/playable maturity is planning/evidence only.
