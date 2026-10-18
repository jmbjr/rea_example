# Flag/unflag contract — milestone 5

## Scope

This contract describes direct calls to the pinned upstream msw_flag and msw_unflag functions. It does not describe a complete CLI turn or a playable Minesweeper game.

The concrete oracle scenario is a synthetic 2-row, 3-column board with mines=1. Allocation succeeds; visible memory exists; coordinates are in bounds; undo is disabled; initial flags equals the number of visible F cells. Visible cells admitted by the probe are #, F, or digits 0–8. No claim is made that every synthetic board is reachable through play.

The hidden mine grid remains NULL. REA confirms these two actions and their visible helpers do not read it. The direct-call oracle therefore requires no first dig, PRNG, seed, hidden mine placement, or C/Python PRNG equivalence. It must not call CLI win checking.

These dimensions, synthetic cells, disabled undo and admission restrictions are experiment choices. The recovered transition rules below are executable observations, not arbitrary fixture rules.

## State and result contract

| Field | Established meaning and constraint | Evidence |
| --- | --- | --- |
| rows / columns | Fixture dimensions 2 / 3; index is row * columns + column | Probe setup; rea/msw_get_visible.json; rea/msw_index.json |
| visible | Row-major six-character buffer; # and F govern these actions | REA getter/setters and action records |
| flags | Coherent initial F count; increment/decrement on successful action only | REA actions; native before/after observations |
| mines | Fixed fixture value 1; not consulted by flag/unflag | Probe setup; complete action/helper decompilations |
| undo_enabled | false; setter skips history branch when undo pointer is NULL | rea/msw_set_visible.json; native snapshots |
| generation / undo_index | Initialize to 1 / 0 and remain unchanged in this scope | rea/msw_init.json; native snapshots |
| grid_initialized | false throughout these direct calls | Initialization + action/helper evidence; native snapshots |

Pointer addresses, allocator contents, uninitialized undo capacity and unused AI internals are not serialized game facts. Undo execution and allocation-failure semantics are not modeled.

| Operation and visible input | Result | Visible update | Flag delta |
| --- | --- | --- | --- |
| flag on # | 0 | selected cell becomes F | +1 |
| flag on anything else admitted | 2 | unchanged | 0 |
| unflag on F | 0 | selected cell becomes # | -1 |
| unflag on anything else admitted | 8 | unchanged | 0 |

All non-selected visible cells and captured bookkeeping fields stay unchanged. Rejected actions leave the entire captured state unchanged. No mine-count cap is applied by the recovered flag function: the successful fixture increases flags from 1 to 2 while mines remains 1.

The oracle reads the actual upstream MSW_MSG table: 0 maps to "Make a move.", 2 to "Can only flag an unknown cell.", and 8 to "Can only unflag a flagged cell.". These message observations are native runtime evidence, not string-table recovery through REA.

## Preconditions and safety boundary

The upstream helpers directly index memory; the decompiled action/helper bodies do not perform coordinate bounds checks. The harness rejects out-of-scope coordinates before invoking them. That is a probe guard, not a recovered game rule. Invalid pointers, dimensions, coordinates, incoherent counters, integer overflow, enabled undo and arbitrary cell bytes are outside the supported comparison domain.

A local probe admission check for row=2 on this two-row board returned 2 without calling the action. Harness process exit codes are distinct from upstream action result codes recorded in JSON.

## Native oracle and fixture setup

target/flag-oracle.c includes the pinned public header, invokes upstream msw_init, snapshots its actual state, overlays the synthetic visible buffer and coherent counter, then calls upstream actions. The harness owns setup, admission and JSON serialization only. It links the unchanged src/minesweeper.c; it does not copy the transition implementation.

Build from the experiment repo with the pinned source directory:

~~~sh
gcc -std=c99 -g -Wall -Wextra -I"$MINESWEEPER_SOURCE/src" "$MINESWEEPER_SOURCE/src/minesweeper.c" target/flag-oracle.c -o flag-oracle
python3 tools/capture_flag_oracle.py ./flag-oracle oracle-output
~~~

The source checkout must be clean at c7cadf1f7ed57d950b400d965a7d3bbab5e50bed. Hosted workflow checks this through the baseline build step. Exact build commands, tool versions, hashes and source commit are retained by Actions.

Six fixtures cover successful flag, flag-already-flagged, flag-revealed, successful unflag, unflag-unflagged, and repeated flag/unflag including rejected repetitions. Each fixture is run three times and compared exactly; explicit acceptance examples check state/result, and unchanged-state checks protect rejected actions. Existing step 3 CLI fixtures remain separate and continue to run.

Snapshots cover before/after visible state, flags, dimensions, mine count, generation, undo index, undo-enabled status and grid-initialized status. Complete messages and process stdout/stderr/return code are retained.

## Evidence and source-exposure ledger

Dependency analysis: [run 39092444862](https://github.com/jmbjr/rea_example/actions/runs/39092444862), source/workflow commit 771dadcd587564fb1ed84f3c3802fd94bcdc2e2f. REA 6.5.0 / Ghidra 12.1.4. The eight complete records in rea/ bind to baseline SHA-256 fb83433214e68ae8e82409266ff5818a82906db063ec7a0772382536213ec7aa.

| Claim | Record / Evidence ID |
| --- | --- |
| Flag branches, count and result | msw_flag.json / ev_53abb1dcac9725a9fe258a93540c949eea02ac3b6da982e8ca220d920e740db9 |
| Unflag branches, count and result | msw_unflag.json / ev_a9089ac87bea7ef4d386225c7017fc72a385b1fb04f8b199336571740b4ab0d7 |
| Visible getter indexing | msw_get_visible.json / ev_488e86c93b50655a54afd7a421703ec6cf16ae378bd4440e9f3e5a0341cda038 |
| Conditional undo bookkeeping | msw_set_visible.json / ev_94ada1cc0e4c006b59316462327f0e082f215dbd7a298c1ab56788bf92d58aa5 |
| Visible write indexing | msw_set_visible_noundo.json / ev_097a2c67803936720fccb65c4538d50d84b6a716fdf65988617defac5c9e8a57 |
| Index arithmetic | msw_index.json / ev_984605ee67c890d17182b76867c93848eb48b9b0f0e7493b4c7c0f5ba67130bd |
| Initial visible state, count, null grid/undo | msw_init.json / ev_69453c16c2da764a7580587e737afb92a5369a4baf7b02217e565704d473531e |
| CLI dispatch, message lookup and post-action win check | run_game.json / ev_75763832989d0cc638f894079c0b5bdbecf4ab0f0576b2476963c1d984d34c15 |

Pseudocode is Ghidra output, not original source. Native snapshots corroborate the bounded state transitions. The symbol/debug types and prior source exposure assist interpretation; this is not a blind experiment.

Additional source inspection for harness construction/diagnosis: complete src/minesweeper.h, the MSW_MSG table, core indexing/getter/setter and initialization regions, flag/unflag implementations, and the CLI run_game loop. These are source-assisted inputs and are not passed off as REA-only discoveries. Probe dimensions, coherent setup and admission limits are test design decisions.

The CLI caller prints status messages and invokes msw_won after commands. Its pre-dig flag crash remains documented; this direct function contract excludes CLI win checking. Dig, reveal/chording, generated boards, win/loss, AI and undo execution have not been recovered by this milestone.

## Next gate

Milestone 6: pin DODGE draft v0.2.1 and audit this finite contract before modeling. No DODGE fields, resolver or Python reconstruction have been implemented in milestone 5.
