# Milestone 3: repeatable observations

Completed 2026-10-18 UTC. No REA analysis performed.

## Runtime observations first

Four uncontrolled runs used the unchanged milestone 2 executable, arguments cli 6 6 5, and stdin d 0,0 followed by q. Consecutive output comparisons were equal, unequal, equal; the middle pair crossed a clock-second boundary. See uncontrolled.json for timestamps, outputs, and return codes. All exited 0. This suggests clock-dependent generation; by itself it does not prove the implementation.

Milestone 2 source diagnosis had already exposed srand(time(NULL)) and lazy grid allocation. That source-assisted knowledge informed the fixed-clock harness choice. No additional gameplay source was read for milestone 3.

## Harness and identity

target/fixed-time.c interposes only the C time() function, returning epoch 1700000000 and writing the same value through a non-null output pointer. LD_PRELOAD loads it into the existing dynamically linked executable. The target file and its gameplay code are unchanged; this is explicitly an instrumented execution environment, not an unmodified runtime observation or a custom PRNG implementation.

- Target SHA-256, rechecked: 466db863eeee26f39edebc2d7c6181257fc91c2b2373dc9598429f0353ed2905
- Harness .so SHA-256: 31fa8b83c9eec29866ed978cc1c10b7d9249ab880351edf63c5bc6ec07c5a171
- Linux x86_64, GCC 13.3.0, glibc 2.39 (same environment as milestone 2).
- Compiler: gcc -std=c99 -Wall -Wextra -shared -fPIC experiment-step3/fixed-time.c -o experiment-step3/fixed-time.so
- No compiler diagnostics, exit 0. Runtime subprocesses used an absolute LD_PRELOAD path.
- Source and build recipe are committed; the .so is reproducible by recipe but is not committed. File paths/toolchain can affect hashes.

## Fixtures and verification

Each controlled case uses cli 6 6 5 and the fixed clock. It was captured three times with identical stdout/stderr/return code. A separate later verification invocation then matched each fixture three more times (24 successful controlled sessions total):

| Fixture | Commands | Result |
| --- | --- | --- |
| dig-quit.json | dig 0,0; quit | Revealed board and clean exit |
| flag-unflag.json | dig 0,0; flag 5,5; unflag 5,5; quit | Flag appeared and was removed |
| repeat-dig.json | dig 0,0 twice; quit | Visible board remained the same on second dig |
| out-of-bounds.json | dig 0,0; dig 6,6; quit | Cell out of bounds message; clean exit |

All controlled runs exited 0 with empty stderr. Fixtures retain raw ANSI escapes; the replay verifier compares output exactly. No win/loss coverage or hidden-grid equality is claimed. All controlled commands dig before flagging because the pre-dig flag crash remains unfixed.

## Reproduce

From the experiment repo root, after building the CLI baseline using target/build-cli.sh:

```sh
mkdir -p build
gcc -std=c99 -Wall -Wextra -shared -fPIC target/fixed-time.c -o build/fixed-time.so
python3 tools/verify_step3.py build/minesweeper-cli build/fixed-time.so evidence/step3
```

The verifier runs every controlled JSON fixture three times and compares return code, stdout, and stderr. It skips uncontrolled.json. Paths to the binary and harness may differ from capture paths; commands do not print the executable path during these sessions.

## Comparison strategy and limits

Use these fixed-clock sessions as the first behavioral oracle for the Python reconstruction. Represent or capture an equivalent initial board before comparing game semantics. Python's random module is not assumed to reproduce C rand(); the exact hidden board has not been extracted. The fixture observes only visible state and messages.

Repeatability is established in this Linux/glibc environment, not across platforms/libc versions. Keep the first dig coordinate, dimensions, mine count, clock epoch, executable identity, and libc environment associated with every fixture. The clock override affects time() throughout the process and would not cover other entropy sources if the target changed.

Step 3 is complete: a repeatable runtime observation strategy exists without target gameplay changes. Next is step 4: pin REA and a provider, verify actual REA operations, and capture substantive binary evidence. No user assistance is needed at this gate.
