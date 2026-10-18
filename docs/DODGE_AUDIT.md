# Milestone 6: DODGE compatibility and authority audit

Status: audit complete; pre-model design only. No candidate document or executable reconstruction exists. This is G0 planning evidence, not G1–G4 conformance.

## Exact baseline and source

DODGE repository: https://github.com/jmbjr/DODGE  
Commit: 9af5804719bc4dc421d1cd76d3587f5b678d3f81  
Selected path: draft/v0.2.1  
Status: working draft, not an official 0.2.1 release.

[spec/dodge-pin.json](../spec/dodge-pin.json) records SHA-256, Git blob IDs and lengths for the normative spec, implementation guide, draft README and all three schemas. Normative authority remains the spec and schemas; the implementation guide supplies adoption guidance.

The audit read the pinned spec, schema definitions and relevant invocation example. The implementation guide bytes match the guide already read for the roadmap (Git blob 15ecf6f876e78053e4972894af685403347adbe1). No fields from another revision are assumed. This commit was selected independently of TheFountain's CI; no claim of matching its pin is made.

Acquisition:

~~~sh
git clone https://github.com/jmbjr/DODGE.git dodge-spec
git -C dodge-spec checkout --detach 9af5804719bc4dc421d1cd76d3587f5b678d3f81
python3 tools/verify_dodge_pin.py dodge-spec
~~~

Verification requires the exact commit and a clean checkout, checks all six pinned files, and parses the schemas as JSON. It passed locally. This verifies identity only; it does not validate any game. No source vendoring or target deployment is required.

Mechanics authority: [milestone 5 contract](../evidence/step5/CONTRACT.md), [eight REA records](../evidence/step5/rea/), and [six native oracle fixtures](../evidence/step5/oracle/). Source/debug assistance remains explicit.

## Compatibility decisions

| Contract fact | Classification | Planned neutral representation |
| --- | --- | --- |
| Six visible cells | Existing DODGE composition + scenario facts | One logical cell token archetype/object and six quantity-one scene instances; no physical dimensions required |
| Per-cell visible character | Existing DODGE state | Object-owned enum value; admitted #, F and 0–8 come from the slice contract; scenario persistence |
| Cell row/column | Canonical scenario facts | Object-owned integer coordinate bindings, derived from ordered fixture layout |
| Rows, columns, mines | Canonical scenario facts | Scenario-owned integer bindings; current fixture values 2, 3, 1 |
| Flag count | Existing DODGE state | Scenario-owned integer value; coherent with initial F count; no maximum derived from mines |
| Flag/unflag checks | Existing DODGE predicates/procedures | eq conditions and a branch step with explicit success and else paths |
| Cell write and counter delta | Existing DODGE effects | Ordered set plus add/subtract effects; all facts declared in data |
| Numeric native result | Existing value/effect semantics + output projection | Scenario-owned result binding set in every branch; it is an execution output, not a recovered native persistent field |
| Input action invocation | Existing invocation semantics | Two explicit cell invocations; target slot bound from using-object; selected scenario context supplied explicitly |
| Initialization bookkeeping | Canonical observed setup | Scenario bindings for generation=1, undo_index=0, undo_enabled=false, grid_initialized=false; no effects change them |
| Coordinate lookup and row-major output | Legitimate implementation algorithms | Select exactly one cell from declared coordinates; serialize in row-major order using declared dimensions |
| Native message text | Presentation/reference fact | Derive a consistent code-to-message view from oracle observations; adapter formats it; text never controls rules |
| C pointers, malloc and struct offsets | Implementation details | Preserve in evidence where relevant; do not turn them into neutral gameplay state |
| Invalid-coordinate probe guard | Experiment admission policy | Reject outside the declared comparison domain; do not invent an upstream bounds-result branch |
| Undo enabled, mine generation, dig, win/loss | Outside scope | Preserve exclusions; do not add guessed behavior |

**No essential executable semantic is unsupported in this finite slice. No executable sidecar, namespaced extension, custom condition opcode or array-indexing expression is needed.** The choice to model cells individually avoids pretending the scalar operand schema supports indexed array writes.

The cell token describes a logical game object, not a physical export design. Scene quantity is six; a later UI may render those objects without adding rules.

## Exact execution design to implement next

1. Define a cell-visible enum with object ownership and scenario persistence. Define scenario-owned flags, dimensions, mines and unchanged bookkeeping values. Every value definition must include type, owner_scope and persistence_scope, as required by this exact schema.
2. Bind each concrete cell's coordinates and visible value exactly once. Bind the selected scenario explicitly so counter/result effects resolve unambiguously.
3. A cell's flag/unflag invocation binds relative target from using-object, then references the declared action. Do not dispatch gameplay on cell IDs or infer invocations from matching action names.
4. Each action references a procedure. Its ordered branch tests the bound target's visible value. Success changes the target cell, adjusts the scenario flag count, then sets the result output. Else sets only the rejection result. Preserve this ordering and the rejection state boundary.
5. Do not make visible-state checks action availability conditions or requirements: rejected native calls must still execute their result branch. Valid coordinates, valid state and disabled undo are admission/profile constraints, not native error codes.
6. Do not author an artificial action cost, turn progression, mine-count cap, topology, randomizer, hidden board, objective, victory or loss condition. Scenario action_refs can declare the two available actions without a turn loop.
7. The finite fixture command list supplies action order. Replay stops when that list ends; this is experiment orchestration, not a recovered game end condition.
8. Initial result is absent/unset until an action executes. The result output is excluded from before/after native game-state equality; the oracle's numeric result is compared separately. Captured native fields retain their exact meanings.

The schema supports object-owned state via concrete instance subjects and scenario-owned state via the scenario context. Each selector must resolve to exactly one binding. No target-owned state fallback is permitted.

## One authority path

| Fact | Sole authored/retained authority | Downstream treatment |
| --- | --- | --- |
| Recovered action semantics | Planned DODGE rule definitions, traceable to immutable REA evidence | Resolver/runtime consume conditions/effects; no second authored rule table in Python |
| Evidence truth and historical observations | Committed REA JSON and native raw fixture records | Immutable reference/baseline; not silently edited when model changes |
| Initial scenario state and commands | Committed oracle fixture setup and raw observations | Deterministic source projection assembles scene/scenario bindings before validation |
| Initial counter coherence | Fixture state validated against count of F cells | Derive convenience count where possible; compare with observed flags rather than author a competing default |
| Logical coordinates and serialization order | Fixture rows/columns plus row-major contract | Derive the six coordinate bindings; adapter consumes these bindings |
| Result and text association | Numeric effects in DODGE; observed text table derived from fixture observations | Compare codes independently; presentation maps codes without action semantics |
| Evidence locators | Project-owned provenance index using file SHA-256, evidence ID and JSON pointer | Use source_ref and traceability metadata allowed by schema; locators do not execute rules |
| Profile meaning/version | Declared project validator source | Run at both source and resolved-game stages; missing/failing profile is fatal |

Planned source assembly: author the reusable DODGE rules once; derive scenario setup from the committed fixture sources rather than manually copying six boards into another canonical catalog. The assembled candidate is the exact document validated and resolved. Sources identify the actual fixture/evidence files and hashes. The projection must be deterministic and retain which fixture/path supplied each binding.

If normalized initial bindings duplicate observed values in the assembled document, the domain profile must compare them to their declared source. The duplication is derived and checked, not independently authored. Runtime defaults must not mask a missing binding.

Command letters f/u belong to an input adapter mapping to explicit invocation triggers; they are not Python branches implementing game behavior. Physical layout, browser selection and Pages paths remain target-owned.

There is no conflict between the oracle's flags=2/mines=1 success and familiar Minesweeper conventions: the observed function has no cap. Preserve its actual behavior. Synthetic setup is not claimed to be a reachable full-game state.

## Planned semantic profile

Declare application profile **rea-minesweeper-flags**, version **0.1.0**, stages **source** and **resolved-game**, referencing a source with kind semantic_validator. These are project-owned planned identifiers, not new DODGE vocabulary. Implementation and declaration occur in milestone 7.

At source stage, the profile must enforce:

- Exact admitted scope: declared 2x3 dimensions, mines=1, six distinct quantity-one cells, complete unique coordinate coverage, valid visible enum, coherent flag count and disabled undo.
- Required flags/bookkeeping bindings; no generated hidden-grid behavior, bogus turn/win rules or unexplained default substitutions.
- Exact declared fixture projection and commands, hashes, three consistent oracle repetitions, initial setup and observed code/message consistency. Synthetic variants need their own declared source/provenance.
- Explicit invocation resolution, required target/scenario context, scenario action availability, correct predicate subjects and exactly one binding per lookup/mutation.
- Flag/unflag success and rejection branches structurally encode the evidence-backed cell write, delta, result and no-op-on-rejection contract. No requirement/cost turns a rejection into non-execution.
- Every claim binds to the native executable identity and retained evidence; source assistance is preserved.

At resolved-game stage, recheck domain invariants and prove that the exact downstream model preserves source definitions, order, invocation context, complete inventory and selected fixture state. Reject missing/extra branches, changed subjects/deltas/results, dropped bindings, duplicate cells or weakened admission constraints.

This profile validates the original recovered rule set. A later intentionally changed rule set would need an explicitly distinct policy; do not silently weaken this profile to allow variants. A milestone 8 authority perturbation can instead change a coherent synthetic initial cell state in a newly declared fixture source, proving the resolver/runtime follow setup without pretending it is an unchanged oracle case.

## Generic validation coverage for milestone 7

All normative section 15.3 checks need explicit coverage, not just the following domain profile:

| Core rule | Required treatment |
| --- | --- |
| 1. Local/external references | Resolve all selected sources, objects, subjects and rules; fail missing references |
| 2. Kind/face agreement | Validate cell token/archetype; check slots if present |
| 3. Cycles | Check procedure and collection graphs; no implicit recursion |
| 4. Quantities/dimensions | Validate six quantity-one instances; physical dimensions absent, but validate any supplied |
| 5. Source hashes | Match exact source bytes and DODGE pin before resolution |
| 6. Scoped ID uniqueness | Reject duplicate cell instance IDs; topology uniqueness if present |
| 7. Edge endpoints | No topology planned; reject unhandled topology rather than silently bypass checks |
| 8. Correct reference kinds | Conditions, actions, procedure/effect refs and subject inputs must resolve correctly |
| 9. Types/defaults/bounds | Check definitions and all initial bindings; omit competing defaults |
| 10. Deterministic order/end evaluation | Preserve branches/effect ordering; no phase/end loop planned |
| 11. AI executable/prose status | No AI planned; do not admit unsupported AI silently |
| 12. Target capability | No target export in milestone 7; any later target contract must support every required feature |

Invocation-specific checks in 15.3 apply: ID/slot uniqueness, precedence, reference kind, required context, action availability/cost semantics. Representations, modifiers, requirements, choices, equipment and target content overrides are not planned. If introduced, their conditional checks become mandatory; unsupported input must fail, not receive a false pass.

Section 15.4 additionally requires no dropped/duplicated/weakened/invented semantics, complete scene/scenario content and unambiguous bindings on the exact resolved model. Existing DODGE example validators may inform implementation, but their existence does not establish a ready-made complete validator for this candidate.

Required negative examples: missing effect/ref; wrong ref kind; procedure cycle; duplicate cell/coordinate; hash mismatch; wrong enum type; incoherent flags; undo enabled; missing target binding; dropped else/result; altered delta; and tampered resolved binding/order. Verify failure gates downstream execution, not merely that an error was logged.

## Finite next implementation checklist

Milestone 7 owns:

1. Acquire/verify pinned DODGE; record the input identity in Actions.
2. Create the reusable DODGE source and deterministic fixture-to-scene/scenario projection, provenance index and application profile declaration.
3. Validate the assembled candidate with the pinned schema (G1).
4. Implement/reuse and audit complete applicable core validation with coverage evidence (G2).
5. Run the required source profile (G3), including negative fixtures and fatal handling of missing/version-mismatched validators.
6. Resolve once, preserve order/authority, and run core resolved invariants plus the required resolved profile on the exact output (G4).
7. Publish stage-specific evidence through Actions; no runtime/target execution on failed gates.

Milestone 8 owns the generic Python interpreter for the supported neutral subset, native equivalence, deterministic replay, coherent scenario perturbation and minimal CLI projection. The interpreter handles operations and subject bindings, not named Minesweeper action IDs. No export contract/manifest is needed just to reach G4; if a packaged target is later emitted, the pinned contract/manifest schemas and validation evidence rules apply.

## Audit conclusion and limits

The essential representation choices are concrete enough for milestone 7. No candidate DODGE gap or upstream change is proposed. Failure to implement the required validators remains a blocker, not a conformance waiver.

Maturity remains pre-model/G0 planning: schema-valid game, core validation, required application profile, resolver and Python execution are all unimplemented. This audit does not claim the full game, invalid C memory behavior, enabled undo or the CLI crash is modeled.
