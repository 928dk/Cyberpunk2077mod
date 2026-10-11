#!/usr/bin/env bash
# NoRelicSickness installer.
#
# Neutralises the Relic-sickness status effect by editing two shipped TweakDB
# sources and running the REDmod deploy so the change reaches the compiled
# database. See README.md for why this is a patch rather than a drop-in mod.
#
# Usage:   ./install.sh [game-dir]
#          CP2077_DIR=/path/to/'Cyberpunk 2077' ./install.sh
#
# Nothing outside the game directory is modified. The two shipped .tweak files
# are backed up first and uninstall.sh restores them verbatim.

set -euo pipefail

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
GAME="${1:-${CP2077_DIR:-}}"

if [ -z "$GAME" ]; then
  echo "error: no game directory given." >&2
  echo "  usage: $0 \"/path/to/Cyberpunk 2077\"" >&2
  exit 2
fi
if [ ! -d "$GAME/tools/redmod/tweaks" ]; then
  echo "error: $GAME does not look like a Cyberpunk 2077 install" >&2
  echo "  (expected tools/redmod/tweaks -- is REDmod installed?)" >&2
  exit 2
fi

TWEAKS="$GAME/tools/redmod/tweaks"
BACKUP="$DIR/.backup"
MOD="$GAME/mods/NoRelicSickness"

FILES=(
  "base/gameplay/static_data/database/status_effect/johnny_sickness.tweak"
  "ep1/gameplay/static_data/database/status_effect/quest_custom.tweak"
)

echo "==> game: $GAME"

# ---- back up, only once -------------------------------------------------
for rel in "${FILES[@]}"; do
  mkdir -p "$BACKUP/$(dirname "$rel")"
  if [ ! -f "$BACKUP/$rel" ]; then
    cp "$TWEAKS/$rel" "$BACKUP/$rel"
    echo "    backed up $rel"
  else
    echo "    backup already present, keeping it: $rel"
  fi
done

# ---- apply --------------------------------------------------------------
for rel in "${FILES[@]}"; do
  if [ ! -f "$DIR/payload/$rel" ]; then
    echo "error: payload missing: payload/$rel" >&2
    exit 1
  fi
  cp "$DIR/payload/$rel" "$TWEAKS/$rel"
  echo "    patched  $rel"
done

# ---- marker mod ---------------------------------------------------------
# redMod.exe deploy is a no-op unless at least one mod is deployed, so an
# otherwise empty marker mod is what makes the recompile happen at all.
mkdir -p "$MOD"
cp "$DIR/mods/NoRelicSickness/info.json" "$MOD/info.json"
echo "    installed marker mod $MOD"

# ---- deploy -------------------------------------------------------------
REDMOD="$GAME/tools/redmod/bin/redMod.exe"
if command -v wine >/dev/null 2>&1; then
  echo "==> running REDmod deploy (a minute or two)"
  ( cd "$GAME/tools/redmod/bin" && WINEDEBUG=-all wine ./redMod.exe deploy -f ) \
      > "$DIR/.deploy.log" 2>&1 || {
        echo "error: deploy FAILED -- full log:" >&2
        cat "$DIR/.deploy.log" >&2
        echo "run uninstall.sh to put the game back" >&2
        exit 1
      }
  grep -E 'Commandlet|Validation errors|ERROR' "$DIR/.deploy.log" || true
else
  echo "note: wine not found, skipping deploy."
  echo "      Start the game via REDmod once, or run:"
  echo "      cd '$GAME/tools/redmod/bin' && wine ./redMod.exe deploy -f"
fi

echo "==> done. Undo with: $DIR/uninstall.sh"