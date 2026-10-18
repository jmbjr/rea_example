# Milestone 5 complete

The direct flag/unflag slice now has an evidence-backed [contract](CONTRACT.md), eight complete [REA records](rea/), and six [native oracle fixtures](oracle/).

## Hosted receipt

- [Successful run 39092445931](https://github.com/jmbjr/rea_example/actions/runs/39092445931), attempt 1, source/workflow commit 9fa29452eadeccb19aef813abb8061699869df4d.
- [Full evidence artifact](https://github.com/jmbjr/rea_example/actions/runs/39092445931/artifacts/12123566125), SHA-256 b3b51e16bea3495bb048f426a3e9911db3497bf8171337d058dff1187450adb7; expires 2026-11-17T03:11:18Z.
- CLI baseline analyzed by REA: fb83433214e68ae8e82409266ff5818a82906db063ec7a0772382536213ec7aa.
- Separately built native oracle: 0dffd8e23302e47c47e89f6ef534ff77e055eef0d075927bc9e51078404914c0.
- Same pinned upstream core as baseline, linked to target/flag-oracle.c rather than CLI/main. The oracle binary is not substituted for the baseline analyzed by REA.
- Fixture raw stdout/stderr/return codes, synthetic setup and oracle hash are committed under oracle/. The executable, license, full environment, resolved dependency lock, and command output remain in the linked artifact.
- REA 6.5.0 / Ghidra 12.1.4; actual runner/JDK/compiler versions are retained in the artifact.
- Earlier dependency-only [run 39092444862](https://github.com/jmbjr/rea_example/actions/runs/39092444862) produced the committed eight evidence records; the final run reproduced the same evidence IDs and analyzed target hash.

## Acceptance results

| Case | Hosted outcome |
| --- | --- |
| Successful flag | 3 identical runs; expected selected cell and counter update |
| Already-flagged rejection | 3 identical runs; result 2 and captured state unchanged |
| Revealed-cell rejection | 3 identical runs; result 2 and captured state unchanged |
| Successful unflag | 3 identical runs; expected selected cell and counter update |
| Unflagged-cell rejection | 3 identical runs; result 8 and captured state unchanged |
| Repeated flag/unflag sequence | 3 identical runs across 6 actions, including rejected repetitions |
| Existing CLI replay suite | Four fixtures, 3 exact matches each |
| REA readiness / overview | Exit 0 |
| Action/helper/initializer/caller decompilation | All 8 returned exit 0; complete records retained |

This is 18 hosted oracle processes covering 33 action observations, plus 12 CLI replay processes. Local development also ran the six fixtures three times each and checked that the probe rejects an out-of-scope coordinate before calling upstream.

The recovered flag behavior permits flags to exceed the configured mine count. The slice deliberately preserves that behavior. Direct functions require valid coordinates and coherent allocated state; they do not inherit safety checks from the probe.

## Reproduce and next step

Use the hosted REA native experiment workflow; see docs/GITHUB_ACTIONS.md. Native harness source and capture/acceptance script are versioned. Both are experiment tools, not a Python reconstruction.

The finite scope, state authority, source assistance and exclusions are in CONTRACT.md. Undo execution, game generation, full CLI turn behavior and win/loss remain excluded. The existing pre-dig CLI crash is not fixed.

Milestone 5 is complete. Next is milestone 6: select an exact DODGE revision and audit this contract. No DODGE modeling or reconstruction work was performed here.
