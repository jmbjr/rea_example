# Milestone 2 — CLI build and smoke evidence

Completed 2026-10-18 UTC for issue #1.

## Source and environment

Cloned upstream using git, checked out detached commit c7cadf1f7ed57d950b400d965a7d3bbab5e50bed, and verified git status --porcelain was empty before and after builds. No upstream file was changed.

Linux x86_64; GCC 13.3.0 (Ubuntu 13.3.0-6ubuntu2~24.04); GNU Make 4.3; glibc 2.39 (Ubuntu 2.39-0ubuntu8.6). pkg-config is absent.

## Upstream attempt

Ran `make` in the pinned checkout. Exit 2. It compiled src/minesweeper.c and src/cli.c, then failed compiling src/gui.c:

```text
make: pkg-config: No such file or directory
gcc  -c -g -Wall --std=c99  -Isrc/  src/minesweeper.c -o obj/release/minesweeper.o
make: pkg-config: No such file or directory
gcc  -c -g -Wall --std=c99  -Isrc/  src/cli.c -o obj/release/cli.o
make: pkg-config: No such file or directory
gcc  -c -g -Wall --std=c99  -Isrc/  src/gui.c -o obj/release/gui.o
src/gui.c:16:10: fatal error: gtk/gtk.h: No such file or directory
make: *** [Makefile:80: obj/release/gui.o] Error 1
```

## Working CLI-only build

Compiled the unchanged upstream core, CLI, and main with experiment-owned stubs for gui_main/curses_main. The stubs print an unavailable message and return failure; they do not implement GUI behavior. This is an adapted CLI baseline, not the upstream all-interface binary.

Actual command, from minesweeper-upstream, with sibling experiment-step2 containing the committed stub:

```sh
gcc -std=c99 -g -Wall -Isrc src/minesweeper.c src/cli.c src/main.c ../experiment-step2/cli-only-stubs.c -o ../experiment-step2/minesweeper-cli
```

Exit 0; no compiler diagnostics. See target/build-cli.sh for the portable invocation using repository files.

Observed executable SHA-256:
`466db863eeee26f39edebc2d7c6181257fc91c2b2373dc9598429f0353ed2905`

ELF 64-bit LSB PIE, x86-64, dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, debug info retained, not stripped. Build ID c1aa1e6291ebfeec5a5483d50b837a9078e16ad4.

This hash identifies this workspace build. Debug paths/toolchain can change hashes on other hosts; byte-for-byte reproducibility is not claimed. The binary remains in the current workspace at experiment-step2/minesweeper-cli; it is not committed. Rebuild and record a fresh hash if that workspace is unavailable.

## Runtime results

JSON files preserve argv, stdin, stdout (including terminal escapes), stderr, and return code.

- launch.json: no mode → usage and exit 1, as expected.
- help.json: cli -h → commands and exit 0.
- dig-quit.json: cli 4 4 2; help, dig 0,0, quit → board changed, goodbye, exit 0.
- quit.json: immediate quit → goodbye and exit 0.
- commands.json: help, flag 0,0, unflag 0,0, quit → SIGSEGV (-11). Buffered stdout was lost. Do not count this as a successful command sequence.

A separate diagnostic build added -fsanitize=address,undefined. The flag-first case reported a null pointer load at src/minesweeper.h:137 and AddressSanitizer SEGV. Diagnostic executable SHA-256: 9ca4576e7745b1b73b7ec5e15e1b37c8b84ac123de4c9adc7e14c555438c2700. Sanitizer symbolization was limited by unavailable /proc/self/exe. This diagnostic binary is not the baseline.

No gameplay fix was made. The successful dig-first trace satisfies the accepted-command smoke check; the pre-dig flag crash remains a known upstream CLI limitation.

## Additional source exposure

For CLI integration and crash diagnosis, inspected src/cli.c (including command loop and argument parsing), declarations/constants/helpers in src/minesweeper.h, and portions of src/minesweeper.c around initialization, allocation, printing, and destruction. Also searched those files for relevant symbols. This revealed lazy grid initialization and source-level command/argument behavior. These are source-assisted observations, not REA findings.

## Next

Milestone 3: establish repeatable board/state observations. The 4x4 trace is one observed random board, not a deterministic fixture. REA has not run. No user intervention is currently required.
