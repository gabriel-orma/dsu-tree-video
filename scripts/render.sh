#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
QUALITY="${QUALITY:-l}"

if [ -x "$ROOT/.venv/Scripts/python.exe" ]; then
    PY="$ROOT/.venv/Scripts/python.exe"
else
    PY="$ROOT/.venv/bin/python"
fi

bash "$ROOT/scripts/build.sh" test
bash "$ROOT/scripts/build.sh" trace

if [ "$#" -eq 0 ]; then
    set -- DemoUniones CasosBorde
fi

cd "$ROOT/anim"
for scene in "$@"; do
    DSU_TRACE_DIR="$ROOT/build/traces" "$PY" -m manim render -q"$QUALITY" --media_dir "$ROOT/media" scenes.py "$scene"
done
