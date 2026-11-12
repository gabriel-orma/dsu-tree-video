#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CXX="${CXX:-g++}"
FLAGS="-std=c++17 -O2 -Wall -Wextra -Wpedantic -static"
mkdir -p "$ROOT/build"

"$CXX" $FLAGS "$ROOT/src/dsu_tree.cpp" "$ROOT/tests/test_dsu_tree.cpp" -o "$ROOT/build/test_dsu_tree"
"$CXX" $FLAGS "$ROOT/src/dsu_tree.cpp" "$ROOT/src/trace_main.cpp" -o "$ROOT/build/dsu_trace"

case "${1:-}" in
    test)
        "$ROOT/build/test_dsu_tree"
        ;;
    trace)
        rm -rf "$ROOT/build/traces"
        mkdir -p "$ROOT/build/traces"
        for scenario in "$ROOT"/scenarios/*.txt; do
            name="$(basename "$scenario" .txt)"
            "$ROOT/build/dsu_trace" "$scenario" "$ROOT/build/traces/$name.json"
            echo "traza: build/traces/$name.json"
        done
        ;;
esac
