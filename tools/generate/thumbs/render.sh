#!/usr/bin/env bash
# Render one collection's thumbnail through chiitiler, then run Gate 1.
#
# Gate 1 compares three renders: the image, a 256px probe of the collection's
# own layers on white with no basemap, and a blank white reference. Identical
# hashes mean nothing landed in the frame. A probe within 15% of the blank's
# size means almost nothing did. This replaces a file-size check, which passes
# any image chiitiler manages to encode, including a uniformly blank one.
set -uo pipefail

COLL="$1"
PORT="${PORT:-13579}"
SIZE="${SIZE:-1024}"
WORK="${WORK:-/tmp/portolan-thumbs}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

SLUG=$(echo "$COLL" | tr '/' '_')
OUT="$WORK/$SLUG"
mkdir -p "$OUT"

# A window from windows.json, keyed by collection id, unless FRAME_BBOX is set.
ID="${COLL#catalog/}"
if [ -z "${FRAME_BBOX:-}" ]; then
  FRAME_BBOX=$(python3 -c "import json,sys;w=json.load(open(sys.argv[1])).get(sys.argv[2]);print(','.join(map(str,w)) if w else '')" \
    "$SCRIPT_DIR/windows.json" "$ID")
fi
export FRAME_BBOX

INFO=$(python3 "$SCRIPT_DIR/frame.py" "$COLL" "$OUT" 2>/dev/null)
if [ -z "$INFO" ] || [ "$INFO" = "NO_PMTILES" ]; then
  echo -e "$COLL\tSKIP\tno-pmtiles\t\t"
  exit 0
fi
BBOX=$(python3 -c "import json,sys;print(json.loads(sys.argv[1])['bbox'])" "$INFO")
FILL=$(python3 -c "import json,sys;print(json.loads(sys.argv[1])['fill'])" "$INFO")
ASPECT=$(python3 -c "import json,sys;print(json.loads(sys.argv[1])['aspect'])" "$INFO")

render() {  # style_file  size  out_file
  local code
  code=$(curl -s -w '%{http_code}' -X POST \
    "http://localhost:$PORT/clip.png?bbox=${BBOX}&size=${2}" \
    -H 'Content-Type: application/json' \
    -d "{\"style\": $(cat "$1")}" \
    -o "$3")
  echo "$code"
}

C1=$(render "$OUT/full.json"  "$SIZE" "$OUT/full.png")
C2=$(render "$OUT/probe.json" 256     "$OUT/probe.png")
C3=$(render "$OUT/blank.json" 256     "$OUT/blank.png")

if [ "$C1" != "200" ]; then
  echo -e "$COLL\tFAIL\thttp-$C1\t$FILL\t$ASPECT"
  exit 0
fi

PH=$(sha256sum "$OUT/probe.png" 2>/dev/null | cut -c1-16)
BH=$(sha256sum "$OUT/blank.png" 2>/dev/null | cut -c1-16)
PS=$(stat -c%s "$OUT/probe.png" 2>/dev/null || echo 0)
BS=$(stat -c%s "$OUT/blank.png" 2>/dev/null || echo 1)

if   [ "$PH" = "$BH" ];                   then GATE=FAIL-empty
elif [ "$PS" -lt $(( BS * 115 / 100 )) ]; then GATE=WARN-sparse
else                                           GATE=PASS; fi

# write to the path the existing thumbnail asset already points at
EXISTING=$(ls "$COLL"/*.thumb.* 2>/dev/null | head -1)
if [ -n "$EXISTING" ]; then
  case "$EXISTING" in
    *.png) cp "$OUT/full.png" "$EXISTING" ;;
    *) convert "$OUT/full.png" -quality 90 "$EXISTING" 2>/dev/null \
         || cp "$OUT/full.png" "${EXISTING%.*}.png" ;;
  esac
  FINAL="$EXISTING"
else
  PM=$(ls "$COLL"/*.pmtiles 2>/dev/null | head -1)
  FINAL="$COLL/$(basename "${PM%.pmtiles}").thumb.jpg"
  convert "$OUT/full.png" -quality 90 "$FINAL"
fi

echo -e "$COLL\t$GATE\t$(stat -c%s "$FINAL")\t$FILL\t$ASPECT"
