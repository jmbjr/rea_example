# Milestone 10 hosted acceptance

[Run 40577377787](https://github.com/jmbjr/rea_example/actions/runs/40577377787)
passed for source commit `f52332950b61b095acf2fbc4308542ce16127694` in PR #2.
Implementation is verified on the review branch; merge is pending.

- Three fixed 4x4 boards; 13 historical and 108 freshly captured native cases.
- 1,974 direct-core comparisons over three deterministic Python replays.
- 286 terminal-session prefix comparisons, blocked post-terminal moves and reset.
- G1–G4 passed; all 13 playable rejection/stale-output cases rejected.
- Original 30 flag negatives and bounded runtime/CLI comparisons passed.
- Same-click layout perturbation passed with unchanged template/interpreter.
- Actual CLI, bundle identity rejection, and extracted application smoke test passed.

Candidate canonical hash:
`cdf9f67362734a02e2bfe1ab34a5c2cf5e464aeb2d95403f992b41f1b02e38ed`.
Resolved canonical hash:
`804a3917218929bdbab3939dc08c66986e1a7c88e4f4aa434aa9c92e4af57247`.
The hosted native probe hash is in `acceptance.json`; it differs from the local
build hash. The observed states/results and candidate/resolved hashes agreed.

The candidate, resolved model, source map and raw fresh native fixtures are gzip
compressed solely for storage. Decompress with Python's `gzip.decompress` before
JSON parsing. Each fixture retains all three native process outputs. Reports,
negative-case diagnostics, perturbation and CLI records remain plain JSON.
`artifact.json` binds retained files, original artifact identity and source tree.
Runtime, compiler and dependency identities are retained. Evidence-only additions
do not alter the admitted model or executable source.

[Download the hosted artifact](https://github.com/jmbjr/rea_example/actions/runs/40577377787/artifacts/12767693170),
then extract the inner `minesweeper-python.zip` to play. It expires November 26;
all essential observations and models are retained here. Recreate the application
with the documented workflow or `tools/package_playable.py` from the retained
bundle after decompression. See [usage and boundaries](../../docs/PLAYABLE_PYTHON.md).

Maturity: bounded G5 on the exercised fixed boards; no whole-game or browser/G6
claim. First clicks are unprotected. Source/debug assistance and native quirks
are preserved. Browser delivery remains milestones 11–12.
