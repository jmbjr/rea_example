# Bounded validation and resolution

This pipeline implements milestone 7 for the direct flag/unflag comparison slice. It is not a general DODGE implementation. The required application profile is `rea-minesweeper-flags@0.1.0` at both source and resolved-game stages.

## Run

Use the **DODGE flags validation** GitHub Actions workflow. It installs the locked dependencies, checks out the exact DODGE revision from milestone 6, verifies its hashes, and runs:

```sh
python3 tools/check_flag_gates.py /path/to/pinned-dodge build/dodge
```

For one build without the negative acceptance suite:

```sh
python3 -m pip install -r requirements-dodge.txt
python3 tools/build_flags.py /path/to/pinned-dodge build/flags
```

An optional `--candidate` file exercises the same validation pipeline on an assembled candidate. It does not bypass schema, source or resolved gates. A failed invocation exits nonzero. The workflow publishes diagnostics even on ordinary step failure.

## Authority and stage ownership

| Stage | Implementation | Evidence |
| --- | --- | --- |
| Source identity | `verify_dodge_pin.py`, source byte hashes, historical evidence lock | Exact spec revision and file identities |
| Source assembly | `assemble_flags.py` | Candidate with six derived fixture scenarios |
| G1 | Pinned Draft 2020-12 schema through jsonschema | Actual candidate validation result |
| G2 | `dodge_core.py` | Named coverage for all 12 section 15.3 requirements and invocation checks |
| G3 | Declared `flag_profile.py` | Native scope/contract, complete fixture projection and evidence identity |
| Resolution | `resolve_flags.py` | Ordered materialized inventory, explicit bindings, inherited invocations |
| G4 generic | `validate_resolved_core` | Exact rule/object/source preservation, complete ordered scopes and bindings |
| G4 application | Required `validate_resolved` | Domain constraints on the exact downstream model |

Reusable rules have one authored home in `model/flag-rules.dodge.json`. Historical observations are immutable references. Scenario state is derived from the native fixture sources and independently checked by the application profile. Profile assertions enforce the recovered contract; they are not another transition executor.

The profile is loaded only from the selected local, hashed validator source. Missing/incorrect profile requirements, missing implementation, mismatched versions or either stage failing are fatal. Unknown normalized features and unknown executable fields fail admission rather than being ignored.

## Supported core subset and scope

The core validator admits scalar typed values with object/scenario ownership and scenario persistence, equality predicates with explicit subjects, literal set/add/subtract effects, action/procedure references, ordered conditional branches with else paths, direct token instances and explicit using-object target invocations. Procedure/action references are checked for cycles. Sources are local, versioned, byte-hashed files.

All applicable core semantic requirements are checked for this candidate. Physical components/faces, collections, resources, topology, phases, AI, representation/export configuration, equipment, modifiers and other unsupported features are rejected if supplied. Their conditional checks are not falsely reported as executed. There is no target export in this milestone; target capability and manifest checks remain outside this build.

This is a strict subset validator, not a claim that every valid DODGE document is accepted. The pinned schema's permissive optional executable shapes do not waive additional core or domain checks. The validation report states applicability for absent features.

## Resolved format

`rea-flags-resolved/1` is a project-owned neutral format, not a new DODGE schema. It retains:

- Document identity and canonical JSON hash, source definitions/hashes, rule definitions and logical object/archetype definitions.
- Scenarios in source declaration order, their source scene/fixture locators and available actions.
- Scenario-owned initial values and ordered materialized cell inventory, including cell values, inherited explicit invocations and provenance.

The scene reference is a locator into the identified candidate; each scenario's concrete inventory is materialized in the output. Object/archetype and executable references remain resolvable from retained definitions. Coordinates are declared state; IDs do not select action behavior. Result is deliberately unset initially. No gameplay default fills a missing binding.

The resolver is not its own acceptance oracle: independent resolved checks compare all source rules/objects, selected inventory, order, bindings, inherited invocations and identity; negative cases tamper with each boundary. The required application profile reruns on the resulting model.

`source-map.json` is derived diagnostic provenance linking candidate JSON pointers to authored rule pointers and native fixture observations (source hash, raw stdout pointer, decoded JSON Lines location, cell position). It supplies no executable semantics.

## Failure and acceptance evidence

`resolved-game.json` is written atomically only after all required stages pass. A rejected rebuild removes any stale resolved output in that output directory. Candidate source and failed-stage diagnostics can still be retained. No runtime or target-generation entry point is invoked by this pipeline.

Acceptance builds twice and compares canonical resolved bytes. The 28 negative cases cover schema errors, missing/wrong-kind references, cycles, duplicate identity/coordinates, source hashes, scalar types/defaults, invalid counters/undo state, missing context, missing rejection/result paths, changed deltas, invented flag caps, missing/version-mismatched/unavailable validators, unsupported topology, lost bindings, tampered resolved state/inventory/invocations/order, and a required resolved-stage validator that raises after earlier gates passed. Every negative verifies that no resolved artifact survives.

Hashes use UTF-8 JSON with sorted object keys, compact separators and no newline. Arrays retain semantic order. Source file hashes use original bytes. The hosted artifact includes the actual candidate, resolved model, stage coverage, source map, dependency versions, and each negative case's report. Only a successful hosted run for this candidate can establish milestone completion.

The next milestone adds a generic Python executor and native equivalence checks. This milestone does not claim G5/G6, playable Minesweeper, whole-game conformance, or a fix for the upstream CLI crash.
