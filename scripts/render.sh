#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
QUALITY="${QUALITY:-l}"
ALL_SCENES=(Gancho Titulo Pregunta TDA PasoAPaso Grande Complejidad Creditos)

if [ -x "$ROOT/.venv/Scripts/python.exe" ]; then
    PY="$ROOT/.venv/Scripts/python.exe"
else
    PY="$ROOT/.venv/bin/python"
fi

find_ffmpeg() {
    if command -v ffmpeg >/dev/null 2>&1; then
        command -v ffmpeg
        return
    fi
    local candidate
    for candidate in "$LOCALAPPDATA"/Microsoft/WinGet/Packages/Gyan.FFmpeg*/ffmpeg-*/bin/ffmpeg.exe; do
        if [ -x "$candidate" ]; then
            echo "$candidate"
            return
        fi
    done
}

native_path() {
    if command -v cygpath >/dev/null 2>&1; then
        cygpath -m "$1"
    else
        echo "$1"
    fi
}

bash "$ROOT/scripts/build.sh" test
bash "$ROOT/scripts/build.sh" trace

if [ "$#" -eq 0 ]; then
    set -- "${ALL_SCENES[@]}"
    JOIN=1
else
    JOIN=0
fi

cd "$ROOT/anim"
for scene in "$@"; do
    DSU_TRACE_DIR="$ROOT/build/traces" "$PY" -m manim render -q"$QUALITY" --media_dir "$ROOT/media" scenes.py "$scene"
done

if [ "$JOIN" -eq 1 ]; then
    case "$QUALITY" in
        l) FOLDER=480p15 ;;
        m) FOLDER=720p30 ;;
        h) FOLDER=1080p60 ;;
        p) FOLDER=1440p60 ;;
        k) FOLDER=2160p60 ;;
    esac
    FFMPEG="$(find_ffmpeg)"
    if [ -z "$FFMPEG" ]; then
        echo "ffmpeg no encontrado: no se unieron las escenas" >&2
        exit 1
    fi
    LIST="$ROOT/build/scenes_$FOLDER.txt"
    : > "$LIST"
    for scene in "${ALL_SCENES[@]}"; do
        echo "file '$(native_path "$ROOT/media/videos/scenes/$FOLDER/$scene.mp4")'" >> "$LIST"
    done
    OUT="$ROOT/media/dsu_tree_$FOLDER.mp4"
    "$FFMPEG" -v error -y -f concat -safe 0 -i "$(native_path "$LIST")" -c copy "$(native_path "$OUT")"
    echo "video completo: $OUT"

    MUSIC=""
    for candidate in "$ROOT"/assets/musica.{mp3,m4a,wav,ogg,flac,opus}; do
        if [ -f "$candidate" ]; then
            MUSIC="$candidate"
            break
        fi
    done
    if [ -n "$MUSIC" ]; then
        FFPROBE="$(dirname "$FFMPEG")/ffprobe"
        DURATION="$("$FFPROBE" -v error -show_entries format=duration -of csv=p=0 "$(native_path "$OUT")")"
        FADE_START="$(awk -v d="$DURATION" 'BEGIN { printf "%.2f", (d > 4 ? d - 4 : 0) }')"
        WITH_MUSIC="$ROOT/media/dsu_tree_${FOLDER}_musica.mp4"
        "$FFMPEG" -v error -y \
            -i "$(native_path "$OUT")" \
            -stream_loop -1 -i "$(native_path "$MUSIC")" \
            -filter_complex "[1:a]volume=${MUSIC_VOLUME:-0.25},afade=t=in:st=0:d=2,afade=t=out:st=${FADE_START}:d=4[a]" \
            -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -shortest \
            "$(native_path "$WITH_MUSIC")"
        echo "video con música: $WITH_MUSIC"
    fi
fi
