# Minesweeper target provenance

## Pinned source

- Upstream: https://github.com/brenns10/minesweeper
- Commit: `c7cadf1f7ed57d950b400d965a7d3bbab5e50bed`
- Tree: `b96d7df554a745dfbb22e0c523d85d083ae42c74`
- Commit date: 2021-02-02T07:09:42Z
- Commit subject: Show flags vs count
- Pin resolved from upstream master on 2026-10-18 UTC.
- License: BSD-3-Clause; copyright (c) 2015 Stephen Brennan.
- Exact upstream license is retained in `LICENSE.minesweeper.txt`.

We use a pinned source reference, not a fork or vendored source tree. No upstream source has been modified. Future build or instrumentation patches must be stored separately and associated with their own executable hashes.

## Source acquisition

On a host with GitHub network access:

```sh
git clone https://github.com/brenns10/minesweeper.git minesweeper-upstream
cd minesweeper-upstream
git checkout --detach c7cadf1f7ed57d950b400d965a7d3bbab5e50bed
git rev-parse HEAD
git status --porcelain
```

Require the printed HEAD to match the pin above and a clean working tree. This recipe has not yet been executed in this workspace. The GitHub connector successfully fetched metadata and the four files listed below at the exact pin. Full source acquisition and the build belong to milestone 2.

## Intended build context

- Target platform: Linux x86_64, native executable.
- Observed workspace compiler: GCC 13.3.0 (Ubuntu 13.3.0-6ubuntu2~24.04).
- Observed build utility: GNU Make 4.3.
- `pkg-config`: unavailable in the current workspace.
- Upstream Makefile uses C99, `-g -Wall`, GTK 3 via pkg-config, and ncurses; it builds the core, CLI, GUI, entry point, and curses sources together.
- Intended first attempt: unmodified `make`; output expected at `bin/release/main`.
- CLI launch from inspected entry point: `bin/release/main cli`.
- GTK/ncurses headers and libraries have not been checked.
- No build, executable hash, runtime trace, or REA result exists yet.

The missing pkg-config is a known dependency gap, not an attempted-build result. Milestone 2 must record the real upstream build attempt before choosing a minimal CLI-only build adjustment.

## Inspection and source-exposure ledger

The experiment repository root contained only README.md when checked on 2026-10-18 UTC; no repository process or AGENTS.md file was present.

Before analysis, the following upstream files were inspected for target suitability, build setup, attribution, and launch syntax; each was re-fetched at the pin:

| File | Git blob SHA | Purpose |
| --- | --- | --- |
| README.md | 841a42c3a83fe7d9752c8923974204971030523b | Documented commands and build instructions |
| Makefile | 06fa6d0c05970f09de692be18e768a94d3fda113 | Compiler, source list, dependencies |
| src/main.c | 9c0d08848c79ec84543ef865c2931c4bab9a6f40 | CLI mode dispatch |
| LICENSE.txt | bce5d471c5f9a5e06e867d037f066a2175e56889 | Redistribution terms |

Fetching the commit endpoint to resolve the pin also returned diffs for src/curses.c, src/minesweeper.c, and src/minesweeper.h. Those diffs exposed a flag counter initialization/update, a status display, and structure field changes. This is additional source exposure, not REA evidence. No full gameplay source file was intentionally read during milestone 1.

This is therefore a partially source-informed experiment. Later claims must distinguish runtime observations, REA findings, and source-assisted interpretations. Do not claim a pristine blind reconstruction.

## Next gate

Follow issue #1 milestone 2: acquire the pinned source, attempt the upstream build, resolve build issues transparently, exercise the CLI, and record commands/toolchain/executable hash. Deterministic boards and REA compatibility remain unverified.

## Milestone 2 update

Pinned source checkout and CLI-only build completed. See [build results, hashes, runtime captures, and additional source exposure](../evidence/step2/README.md). Earlier statements above about unattempted acquisition/build describe milestone 1. Next gate is issue #1 milestone 3. The upstream full build failed on missing GTK dependencies; no gameplay fix was applied.
