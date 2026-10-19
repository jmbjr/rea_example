# Milestone 7 complete — validated and resolved flag slice

## Hosted result

[Run 39197343541](https://github.com/jmbjr/rea_example/actions/runs/39197343541) completed successfully for source commit 17d5f18762ece31954d06600c00785967169ce6c.

The actual assembled six-scenario candidate passed:

- Exact DODGE pin integrity.
- G1: pinned JSON Schema.
- G2: applicable core semantic checks with explicit supported-subset admission.
- G3: required application source profile.
- G4: independent generic resolved checks and the required application resolved profile.

All **30 negative cases** were rejected at their expected gates, including a required resolved-stage validator failure and boolean/integer/float substitutions. Each rejection left no resolved artifact, even when a stale file was placed there first. Two complete resolutions produced identical canonical output.

## Accepted identities

| Artifact | Canonical SHA-256 |
| --- | --- |
| Candidate | 7edeed1f3ec4145a5a55c216be220e23fd6de23ac99d2c68001ece91cd32e1bd |
| Resolved model | 7d474846592d735385f4e041fb5eef423a274b278ced326d0c3082ac28caa5f9 |

Canonical hashing is UTF-8 JSON, sorted object keys, compact separators, no newline; arrays preserve order. Source hashes use original bytes.

The committed candidate and resolved snapshots were reproduced locally and their canonical hashes matched the actual hosted reports. They are derived historical evidence, not additional authored rule authorities. The acceptance and stage reports were retained from complete JSON records in the hosted job log. All newly uploaded implementation blobs were verified against local Git blob identities before the successful run; hosted toolchain hashes match those files.

[Download full hosted evidence](https://github.com/jmbjr/rea_example/actions/runs/39197343541/artifacts/12162830090) for the source map, dependency/Python versions, both positive builds, and each rejected candidate/report. Artifact ZIP digest: sha256:fe80cfccd187541aa33ab744c52296f851529ef72b0ddb505c350f8e56dfb133. Current expiry: 2026-11-18T04:00:39Z.

## What exists

- Authored reusable rules/composition in model/flag-rules.dodge.json.
- Hash-locked retained native observations in model/evidence-lock.json.
- Deterministic fixture-to-scene/scenario source assembly.
- Application profile rea-minesweeper-flags@0.1.0, loaded from its declared hashed source at both stages.
- One ordered neutral resolver retaining rule/object definitions, explicit scoped values, materialized cells, inherited invocations and provenance.
- Derived source-map locators from candidate fields to authored rules and raw native fixture observations.
- A separate GitHub Actions validation workflow and a fatal-gate acceptance suite.

The [pipeline guide](../../docs/DODGE_PIPELINE.md) defines invocation, artifact structure, supported features and limitations. The [milestone 6 audit](../../docs/DODGE_AUDIT.md) records the design decisions.

## Scope and limits

Maturity is **G4 for this bounded candidate**. The core validator explicitly rejects unsupported DODGE features; it is not a universal validator. Absent topology, AI, physical exports and other conditional features are identified as not applicable, never falsely reported as executed.

No game action is executed by this pipeline. There is no G5/G6 claim, Python transition interpreter, full Minesweeper reconstruction, Pages deployment or fix for the upstream CLI crash. Milestone 8 adds the readable executor, native equivalence and authority perturbation.

An initial hosted attempt failed because a source transfer truncated one file. That attempt is not accepted evidence; the corrected complete files and type-preserving checks passed the run linked above.
