#!/usr/bin/env bash
#
# build-johnny-archive.sh — build the NoJohnnyReplacer .archive reproducibly.
#
# Design A (see research/replacer-manifest.txt): disable the Tier-1
# #johnny_replacer questReplacer_NodeType nodes so the quest system stops
# spawning Johnny while the Relic storyline stays intact. The keystone
# assumption — that the engine honours enable=false — is documented but
# UNVERIFIED in-game: this script produces a build, not a proof.
#
# Pipeline:  extract -> serialize -> patch -> verify -> deserialize -> pack
#   extract     : WolvenKit.CLI unbundle *.questphase from the game archives
#   serialize   : WolvenKit.CLI convert serialize   (CR2W -> JSON)
#   patch       : tools/replacer-scope.py patch     (flip Tier-1 enable to 0)
#   verify      : tools/replacer-scope.py verify    (tier2/3 untouched)
#   deserialize : WolvenKit.CLI convert deserialize (JSON -> CR2W)
#   pack        : WolvenKit.CLI pack (.archive for <CP2077>/archive/pc/mod/)
#
# Requires:
#   - a WolvenKit.CLI net10.0 build and a dotnet 10 SDK (WOLVENKIT_CLI,
#     DOTNET_BIN; defaults below)
#   - the vanilla game archives (CP2077_GAME, default Steam path)
#
# Environment:
#   CP2077_GAME   path to the Cyberpunk 2077 install (default: Steam path)
#   WOLVENKIT_CLI path to WolvenKit.CLI.dll          (default: known build)
#   DOTNET_BIN    dotnet host binary                 (default: ~/.dotnet/dotnet)
#   KEEP=1        keep the work dir on exit
#
# Usage: build-johnny-archive.sh [VERSION]   (default version: 1.0.0-rc1)
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="${1:-1.0.0-rc1}"

GAME="${CP2077_GAME:-$HOME/.steam/steam/steamapps/common/Cyberpunk 2077}"
CLI="${WOLVENKIT_CLI:-$HOME/projects/Cyberpunk-tooling/WolvenKit/WolvenKit.CLI/bin/Release/net10.0/WolvenKit.CLI.dll}"
if command -v dotnet >/dev/null 2>&1; then
    DOTNET="$(command -v dotnet)"
elif [ -x "$HOME/.dotnet/dotnet" ]; then
    DOTNET="$HOME/.dotnet/dotnet"
else
    DOTNET="${DOTNET_BIN:-}"
fi

WORK="${TMPDIR:-/tmp}/johnny-build-$$"
RAW="$WORK/raw"; STAGE="$WORK/stage"; PATCHED="$WORK/patched"
VERIF="$WORK/verif"; UNPACK="$WORK/unpack"; OUTDIR="$REPO/dist"
OUT="$OUTDIR/NoJohnnyReplacer-$VERSION.archive"

# The 16 Tier-1 ship-set files, relative to the archive root. Keep in sync with
# research/replacer-manifest.txt (the manifest is the authority; re-run it after
# any game patch and diff).
SHIPSET=(
  base/quest/main_quests/epilogue/q204/phases/q204_02_corridor.questphase
  base/quest/main_quests/part1/q101/phases/q101_j_01_concert.questphase
  base/quest/main_quests/part1/q101/phases/q101_j_02_kerry.questphase
  base/quest/main_quests/part1/q101/phases/q101_j_03_hallway.questphase
  base/quest/main_quests/part1/q101/phases/q101_j_04_smasher.questphase
  base/quest/main_quests/part1/q101/phases/q101_j_04a_evac.questphase
  base/quest/main_quests/part1/q101/phases/q101_j_05_soulkiller.questphase
  base/quest/main_quests/part1/q108/phases/q108_01_concert.questphase
  base/quest/main_quests/part1/q108/phases/q108_02_backalley.questphase
  base/quest/main_quests/part1/q108/phases/q108_03_ripperdoc.questphase
  base/quest/main_quests/part1/q108/phases/q108_04_atlantis.questphase
  base/quest/main_quests/part1/q108/phases/q108_05_escape.questphase
  base/quest/main_quests/part1/q108/phases/q108_06_tower.questphase
  base/quest/main_quests/part1/q108/phases/q108_06a_tower_server.questphase
  base/quest/main_quests/part1/q108/phases/q108_riots.questphase
  base/quest/main_quests/part1/q116/phases/q116_cyberspace.questphase
)

die() { echo "error: $*" >&2; exit 1; }

[ -n "$DOTNET" ] || die "no dotnet found (set DOTNET_BIN)"
[ -f "$CLI" ]    || die "WolvenKit.CLI not found at $CLI (set WOLVENKIT_CLI)"
[ -d "$GAME/archive/pc/content" ] || die "game archives not found at $GAME (set CP2077_GAME)"
export DOTNET_ROOT="$(dirname "$DOTNET")"
export DOTNET_CLI_TELEMETRY_OPTOUT=1

trap '[ "${KEEP:-0}" = 1 ] || rm -rf "$WORK"' EXIT

mkdir -p "$WORK" "$RAW" "$STAGE" "$PATCHED" "$VERIF" "$UNPACK" "$OUTDIR"

say() { printf '\n\033[1m=== %s ===\033[0m\n' "$*"; }

say "1/7 extract *.questphase from $GAME"
"$DOTNET" "$CLI" extract "$GAME/archive/pc/content" -o "$RAW" -gp "$GAME" -w "*.questphase" \
    >/dev/null 2>&1 || die "extract failed (see WolvenKit output with --verbose)"
echo "  extracted questphase files: $(find "$RAW" -name '*.questphase' | wc -l)"

say "2/7 stage the $(( ${#SHIPSET[@]} )) ship-set files"
missing=0
for f in "${SHIPSET[@]}"; do
    [ -f "$RAW/$f" ] || { echo "  MISSING FROM VANILLA: $f"; missing=1; continue; }
    mkdir -p "$STAGE/$(dirname "$f")"
    cp "$RAW/$f" "$STAGE/$f"
done
[ "$missing" = 0 ] || die "vanilla corpus is missing ship-set files (game patched?)"

say "3/7 serialize CR2W -> JSON"
if ! "$DOTNET" "$CLI" convert serialize "$STAGE" >/dev/null 2>&1; then
    die "serialize failed"
fi
echo "  json files: $(find "$STAGE" -name '*.json' | wc -l)"

say "4/7 patch + verify (replacer-scope.py)"
python3 "$REPO/tools/replacer-scope.py" patch "$STAGE" --out "$PATCHED" | tail -3
python3 "$REPO/tools/replacer-scope.py" verify "$STAGE" --out "$PATCHED" \
    || die "verify rejected the patch"

say "5/7 overlay patched JSON, deserialize JSON -> CR2W"
(cd "$PATCHED" && find . -name '*.json' -print0 |
    while IFS= read -r -d '' p; do cp "$p" "$STAGE/${p#./}"; done)
"$DOTNET" "$CLI" convert deserialize "$STAGE" >/dev/null 2>&1 || die "deserialize failed"
echo "  rebuilt questphase files: $(find "$STAGE" -name '*.questphase' | wc -l)"

say "6/7 verify the rebuilt binaries (re-serialize + manifest)"
cp -r "$STAGE" "$VERIF/"
find "$VERIF" -name '*.json' -delete
"$DOTNET" "$CLI" convert serialize "$VERIF" >/dev/null 2>&1 || die "re-serialize failed"
python3 "$REPO/tools/replacer-scope.py" manifest "$VERIF" | sed -n '1,6p'

say "7/7 pack $OUT"
find "$STAGE" -name '*.json' -delete        # the archive ships binaries only
"$DOTNET" "$CLI" pack "$STAGE" -o "$WORK/packed" 2>&1 | grep -viE '^\s*[0-9]+%' | tail -2
mv "$WORK/packed/stage.archive" "$OUT"       # pack names archives after the input dir
[ -f "$OUT" ] || die "pack produced no archive"

say "round-trip check: unpack $OUT and re-scan one ship-set file"
EXTRACT_LOG="$WORK/extract-out.log"
"$DOTNET" "$CLI" extract "$OUT" -o "$UNPACK" -gp "$GAME" -w "*.questphase" >"$EXTRACT_LOG" 2>&1 \
    || { tail -20 "$EXTRACT_LOG" >&2; die "unpack of the built archive failed — the game will not load it either"; }
echo "  $(grep -oE 'Unbundled [0-9]+/[0-9]+ entries' "$EXTRACT_LOG" | tail -1)"

printf '\n\033[32mdone:\033[0m %s (%d bytes)\n' "$OUT" "$(stat -c%s "$OUT")"
echo "  install: copy into <Cyberpunk 2077>/archive/pc/mod/"
echo "  status : UNVERIFIED IN GAME — launch a Johnny scene before shipping (see README.txt)"