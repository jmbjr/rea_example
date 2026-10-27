# Playable assessment contract and compatibility audit

Milestone 9 extends the evidence boundary, not the implemented Python gameplay boundary. Existing G5 remains flag/unflag only until the new candidate passes its own gates and comparisons.

## Scope and authority

Upstream is unchanged `brenns10/minesweeper@c7cadf1f7ed57d950b400d965a7d3bbab5e50bed`. Investigation is source/debug-assisted: `src/minesweeper.c`, `src/minesweeper.h` and `src/cli.c` were read to identify dependencies and construct the probe. REA/Ghidra then inspects the compiled target; this is not blind reconstruction.

The observation scope is an explicitly initialized 4x4 grid, two mines at opposite corners, initially all-hidden visible cells, and undo disabled. Setup derives the eight-neighbor counts from explicit mine positions and supplies complete grid bytes to the native game. This is experimental setup, not evidence that Python reproduces native random generation. The probe calls unchanged `msw_dig`, `msw_flag`, `msw_unflag` and `msw_won`.

The assessment delivery should use several curated fixed boards with concealed mines, including a less trivial board than this flood-focused fixture. Each additional layout/size must receive native comparisons before it is claimed. These 4x4 examples do not establish useful puzzle difficulty, every mine arrangement, every adjacent count, every possible state or browser usability.

## Native contract and evidence matrix

Each named fixture is under `evidence/step9/oracle/`. REA function evidence is under `evidence/step9/rea/`. Probe input letters and JSON serialization are experiment interfaces, not the upstream CLI syntax.

| Behavior | Native contract | Evidence |
| --- | --- | --- |
| Coordinates | Dig returns 1 before mutation when outside the board. Flag/unflag have no equivalent guard; adapter/probe must admit only valid coordinates. | `msw_dig`, `msw_in_bounds`; `dig-bounds` |
| Initialized setup | A non-null grid bypasses initial random generation. Flag/unflag followed by win checking is safe in the observed initialized fixture. | `msw_dig`, `msw_won`, `msw_initial_grid`; `flag-before-dig-initialized` |
| Numbered-cell dig | Copy the underlying digit to visible; return 0. Repeating the call on a revealed numbered cell also returns 0. | `msw_dig`, `msw_get_grid`; `numbered-cell`, `repeated-number` |
| Empty-area reveal | If underlying cell is `0` and visible cell is not `0`, write `0`, recursively dig in-bounds neighbors in the native offset order, ignore their return values, then return 0. | `msw_dig`; `empty-expansion` |
| Flagged number/mine | Once the empty-cell branch does not match, a visible flag causes result 5 with no mutation. | `msw_dig`; `flagged-number` (number case directly observed) |
| Flagged empty cell | Empty-cell branch precedes the flag guard: overwrite the flag with `0`, expand, return 0. Do not decrement flag counter. | `msw_dig`; `flagged-zero`, `expansion-flagged-zero` |
| Flagged expansion boundary | Numbered flagged cells remain flagged when encountered during expansion. | `msw_dig`; `expansion-flagged-number` |
| Mine hit | If not blocked by a flag, write `!` to visible and return 7. No all-mine reveal or persistent native loss field is created. | `msw_dig`; `mine-and-raw-post-loss` |
| Flag bookkeeping | Flag increments counter, unflag decrements it. Digging a flagged zero can make counter differ from actual visible flags; do not enforce equality after every action or silently repair it. | Earlier flag evidence plus `flagged-zero` |
| Victory | Every safe cell's visible value equals its underlying value; mine cells remain `#` or `F`. No flag requirement or counter equality is imposed. | `msw_won`; `win-without-flags`, `win-with-flags` |
| Caller result/outcome | Native core dig returns 0 even on the winning move. CLI checks victory after the operation and maps it to status 9; otherwise result 7 ends the loop. | `run_game`, `msw_won`; win/mine fixtures |
| Terminal boundary | Core functions accept further calls after a win/loss observation; CLI stops accepting moves. Browser session must model the caller's stop rule, not claim core rejects those calls. | `run_game`; `raw-post-win`, `mine-and-raw-post-loss` |
| Unchanged state | Grid, dimensions, mine count, generation and undo fields stay unchanged across these direct calls. No `msw_end_turn` call is made. | All fixture before/after records |

The probe intentionally continues after terminal observations, including remaining commands in the long win sequences. `cli_would_stop` is a probe-derived observation of the source-reviewed CLI condition; it is not a native game field. Session comparisons must stop at the **first** such observation. Remaining records test the lower-level core only. `won` is a fresh call to native `msw_won`, not a latched session outcome.

### Dependencies and boundaries

- Dig depends on bounds, underlying/visible access, visible mutation and recursive neighbor traversal. Undo-disabled mutation dependencies are already retained in milestone 5; new captures include direct dig, grid access, bounds and win routines.
- Neighbor offsets are `(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)`. They are game/setup semantics with source provenance, not renderer geometry.
- Native `msw_generate_grid` computes adjacent counts after shuffling mines. Fixed setup supplies the resulting facts independently and bypasses both shuffle and first-dig rejection sampling. First-click safety is therefore not promised for arbitrary clicks on a fixed board.
- The pre-dig CLI crash is consistent with `run_game` calling `msw_won` while `grid` remains null after flag/unflag. Initializing the fixture avoids that path; it does not fix or change upstream.
- `msw_end_turn` assumes undo storage. It is not required by `run_game` and must not be introduced into this undo-disabled slice.
- Restart is an assessment session reset to validated initial state. Changing board is a new selected validated scenario. Neither is claimed as a recovered upstream core action.
- Out-of-scope commands, malformed input and flag/unflag coordinates remain adapter admission errors. Chording (`msw_reveal`), AI, undo, random generation and upstream bug fixes are deferred.

## Exact DODGE compatibility audit

Pin remains `jmbjr/DODGE@9af5804719bc4dc421d1cd76d3587f5b678d3f81`, draft 0.2.1. All six manifest hashes were reverified. Normative sections 7.3–7.6, 9, 11 and 15, schema definitions `subject`, `operand`, `condition`, `effect`, `step`, `scenario`/`endCondition`, and the implementation guide were inspected. No new spec field or pin change is needed for the bounded approach below.

| Need | Authoritative home and representation | Current implementation gap |
| --- | --- | --- |
| Board dimensions, mine layout, counts, initial visible state | Versioned canonical scenario source; derive/check counts; resolve typed cell bindings | Current profile admits only historical 2x3 flag fixtures |
| Dig branch precedence/results | One source-backed rule template compiled into ordinary ordered branches/effects | No dig template, source profile or comparison executor binding |
| Cross-cell traversal | Fixed-board specialization into finite acyclic procedures using concrete `instance_ref` subjects | Core currently rejects static rule subjects even though the schema/spec allow them; add checked binding coverage |
| Empty-region expansion | Bounded depth-indexed procedure DAG derived from board size and native neighbor order | Not implemented or equivalence-proven; must not bypass cycle checks |
| Win predicate | Per-cell comparisons composed by `all`/`any`; safe cells match underlying values, mines remain hidden/flagged | Validator/runtime only support `eq`; no composite-condition cycle/reference validation |
| Terminal session | Ordered scenario end conditions evaluated after an action; preserve core result separately from session status/outcome | Resolver currently omits/rejects end conditions; runtime has no terminal boundary |
| Python/browser parity | Same Python interpreter and session code, same resolved model bytes | No browser loader, target capability check or browser parity evidence |
| Clicks, keyboard/touch, display and hosting | Browser adapter and target-owned build/deployment configuration | No playable UI/Pages deployment |

### Finite traversal strategy for the next implementation

Use fixed layouts and specialize reusable dig semantics into existing DODGE primitives rather than hard-code a Minesweeper flood algorithm in the renderer or interpreter. For a board of N cells, derive per-cell, depth-indexed procedures with calls only to the next depth. The native recursive branch marks a newly expanded zero before visiting neighbors, so a recursive path can expand at most N distinct zeros. Preserve the final non-expanding neighbor calls at the depth boundary; never silently drop them. A source/resolved semantic profile must verify this construction and its bound, ordered neighbors, grid-derived literal reveal values, root result handling and unchanged flag counter.

This gives a finite acyclic graph rather than a recursive reference cycle. Nested dig return values are ignored by native expansion; the root action's result must not be replaced by a nested result. Prove this with native comparisons before claiming it executable. Model size grows with board size and depth; measure generation time, execution depth and browser load cost before enlarging boards. The existing runtime's fixed depth guard may need a validated, bounded adjustment.

This is a selected implementation approach, **not** a new conformance result. If the bounded graph cannot preserve native behavior within reasonable size/depth, stop and reassess a declared alternative instead of slipping executable semantics into a UI or inventing repeat semantics. The pinned schema includes `repeat`, but it does not by itself establish the collection/context behavior needed for a new generic flood executor.

### Browser delivery boundary

The preferred route is the same Python code under Pyodide, with a thin JS event/rendering adapter. Official documentation establishes browser initialization and loading custom Python code into its virtual filesystem:

- https://pyodide.org/en/stable/usage/index.html
- https://pyodide.org/en/stable/usage/loading-custom-python-code.html

This is feasibility guidance, not a tested browser integration or version pin. Select and pin the runtime at implementation. Validate/resolve in Actions; package the exact admitted model, runtime and receipt together. Browser startup verifies packaged identity and loads shared Python session code. It must not call the Git-based build CLI, subprocess or native REA in the browser, and it must not recover transition rules from expected-output fixtures. Keep DOM messages to coordinates/action/reset requests and presentation snapshots. Concealed local mine data is inspectable by a determined player; no anti-cheat promise is made.

## Next finite delivery sequence

1. **Milestone 10 — playable neutral model and Python session.** Add curated boards with native observations, implement bounded dig compilation, checked static subjects/composite predicates and ordered end conditions; extend source/resolved profiles and provenance. Compare direct-core traces and terminal session prefixes, preserve flag regressions, add missing-semantics/changed-neighbor/outcome negatives and layout perturbations. Stop if the graph strategy fails.
2. **Milestone 11 — assessable browser build.** Load the same Python runtime/session and validated model through a pinned browser Python runtime; add dig/flag controls, numbers, terminal outcome and restart/board selection. Prove native/Python/browser parity on selected sequences and check first load/input/reset in a real browser. Show fixed-board and first-click assumptions clearly.
3. **Milestone 12 — Actions/Pages delivery and user assessment.** Package only passing artifacts, deploy the tested build through Actions, verify the live URL, then ask the user to play and assess. Record observations before planning random generation, additional mechanics or visual polish.

No automatic binary-to-DODGE compiler, full-game equivalence, expanded G5 or browser/G6 claim is established by this contract alone.
