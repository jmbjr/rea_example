#!/bin/sh
set -eu
# Usage: sh target/build-cli.sh /path/to/minesweeper-upstream /path/to/output
src_dir=$(cd "$1" && pwd)
out_dir=$2
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
test "$(git -C "$src_dir" rev-parse HEAD)" = c7cadf1f7ed57d950b400d965a7d3bbab5e50bed
test -z "$(git -C "$src_dir" status --porcelain)"
mkdir -p "$out_dir"
out_dir=$(cd "$out_dir" && pwd)
gcc -std=c99 -g -Wall -I"$src_dir/src" "$src_dir/src/minesweeper.c" "$src_dir/src/cli.c" "$src_dir/src/main.c" "$script_dir/cli-only-stubs.c" -o "$out_dir/minesweeper-cli"
sha256sum "$out_dir/minesweeper-cli"
