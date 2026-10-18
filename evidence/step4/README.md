# Milestone 4: REA installed; native analysis blocked

Attempted 2026-10-18 UTC. Milestone 4 is **incomplete**. No binary-derived REA finding, pseudocode, or gameplay inference was produced.

## Installed identity

Official npm package rea-agents@6.5.0 installed locally using:

```sh
npm install --prefix rea-runtime --ignore-scripts --no-audit --no-fund rea-agents@6.5.0
```

173 packages added. Lifecycle scripts were intentionally disabled; the published CLI nevertheless ran. No MCP/client registration, global configuration, provider installation, or agent restart was performed.

Node v24.19.0; npm 11.9.0. CLI --version returned 6.5.0 (exit 0). package-identity.json retains the npm resolved URL and integrity:
sha512-C6BG7LyrAdR74mSjertM6PrxJkcNZ2bfQNOJornPo9erDEp2tyPRVYPnV5Yodr+1RqewCQla68WulXlVnveD+A==

The separate official REA source checkout resolved to commit 847472acf5cf4a28379e828dcd0fe55ac99d7c07 for documentation inspection. The executed tool was the published 6.5.0 package, not a build of that source checkout. Its server identity reports build_commit null; do not claim the checkout commit identifies the npm build.

Read bundled reverse-engineer-anything skill version 42 and connection-and-recovery guidance; used CLI directly.

## Captured commands

All captures preserve actual stdout, stderr, argv and return code, including full JSON output.

| Capture | Operation | Exit / result |
| --- | --- | --- |
| version.json | --version | 0; 6.5.0 |
| providers.json | providers --json | 0; all native session providers unavailable |
| doctor-ghidra.json | doctor --provider ghidra --json | 1; missing analysis engine |
| analyze-ghidra.json | analyze baseline --provider ghidra --json | 1; provider_unavailable during open_binary |
| process-prerequisite.json | ps -eo pid,args | 47; /proc unavailable |

Attempted target: milestone 2 CLI executable, SHA-256 rechecked as 466db863eeee26f39edebc2d7c6181257fc91c2b2373dc9598429f0353ed2905. No fixed-clock preload was supplied to REA. Provider selection failed before analysis opened; this hash is our separate target check, not a successful REA identity result.

## Blockers

1. Ghidra not installed/configured: GHIDRA_INSTALL_DIR is unset; no analyzeHeadless or matching native decompiler was found.
2. Hopper launcher /opt/hopper/bin/Hopper unavailable; IDA MCP configuration absent. Neither was used as a substitute.
3. Linux ps exits 47 with "Error, do this: mount -t proc proc /proc". REA documents procps-compatible process ownership checks as a prerequisite for supervised Linux native analysis. This is an independently observed prerequisite gap; the attempted analysis returned missing-provider diagnostics, not a process-check failure.
4. Default java launch fails loading libjli.so. Adding its existing library directories through LD_LIBRARY_PATH allowed Java to report OpenJDK 17.0.20. That is below the documented JDK 21 minimum for the supported Ghidra 12.1.x releases. No JDK upgrade was performed.

No /proc mount, sandbox change, process-check bypass, paid provider installation, or fake process inventory was attempted. Native compatibility is still unverified. Informational doctor registration/skill warnings do not block direct CLI use and were not treated as the main cause.

## Claims ledger

| Claim | Evidence | Type / boundary |
| --- | --- | --- |
| Pinned REA CLI executes here | version.json; providers.json | Actual REA diagnostics |
| No configured native engine is available | providers.json; doctor-ghidra.json | Current discovered configuration only |
| Requested native analysis failed | analyze-ghidra.json | Actual REA error, no completed analysis |
| Process inspection fails here | process-prerequisite.json | Shell diagnostic, not REA binary evidence |
| Minesweeper gameplay recovered by REA | None | Unresolved; no such claim |

## Resume on an analysis-capable host

Use a normal Linux x86_64 host/VM/container with a working /proc and procps ps. Install official Ghidra 12.1.x (REA docs verify 12.1.4), including its native decompiler, and a full compatible JDK (documented minimum 21; respect that installation's application.java.min/max). Set GHIDRA_INSTALL_DIR and JAVA_HOME to the actual absolute installation directories.

From this experiment repository, obtain the pinned Minesweeper source using target/README.md and build the baseline:

```sh
sh target/build-cli.sh /absolute/path/to/minesweeper-upstream build
ps -eo pid,args
java -version
npx -y rea-agents@6.5.0 doctor --provider ghidra --json > doctor-ghidra.json
npx -y rea-agents@6.5.0 analyze "$PWD/build/minesweeper-cli" --provider ghidra --json > analyze-ghidra.json
```

Also retain stderr, exit codes, provider version, and sha256sum of the newly built executable. Its hash may differ due to build paths/toolchain; associate all analysis with the actual bytes, not the previous workspace hash. On failure preserve diagnostics. On success choose a focused function inspection and retain substantive evidence before checking milestone 4 complete.

These commands are a handoff recipe, not results. A host with native analysis prerequisites is needed to resume; the user can run this there and return the captures, or continue this task in a suitably equipped execution environment.

## Roadmap status

Only milestone 4's package pin/setup item is complete. Provider verification, successful binary analysis, and a binary-findings table remain incomplete. This diagnostic claims ledger does not satisfy the substantive-finding gate. Do not advance to DODGE extraction or extend the roadmap yet.
