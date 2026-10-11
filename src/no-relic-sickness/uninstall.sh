#!/usr/bin/env bash
# NoRelicSickness uninstaller. Restores the shipped TweakDB sources from the
# backup install.sh took, removes the marker mod, and recompiles.
#
# Usage:   ./uninstall.sh [game-dir]
#
# If the backup is missing the script refuses to guess and exits non-zero,
# because writing a "restored" file that is really a generated override would
# leave the game permanently patched with no record of how.

set -euo pipefail

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
GAME="${1:-${CP2077_DIR:-}}"
BACKUP="$DIR/.backup"

if [ -z "$GAME" ]; then
  echo "error: no game directory given." >&2
  echo "  usage: $0 \"/path/to/Cyberpunk 2077\"" >&2
  exit 2
fi
if [ ! -d "$BACKUP" ]; then
  echo "error: no backup at $BACKUP -- cannot restore safely." >&2
  echo "       Re-download REDmod, or copy these two files from a clean install:" >&2
  echo "         base/gameplay/static_data/database/status_effect/johnny_sickness.tweak" >&2
  echo "         ep1/gameplay/static_data/database/status_effect/quest_custom.tweak" >&2
  exit 1
fi

TWEAKS="$GAME/tools/redmod/tweaks"

for rel in base/gameplay/static_data/database/status_effect/johnny_sickness.tweak \
           ep1/gameplay/static_data/database/status_effect/quest_custom.tweak; do
  if [ ! -f "$BACKUP/$rel" ]; then
    echo "error: backup incomplete, missing $rel" >&2
    exit 1
  fi
  cp "$BACKUP/$rel" "$TWEAKS/$rel"
  echo "    restored $rel"
done

rm -rf "$GAME/mods/NoRelicSickness"
echo "    removed marker mod"

if command -v wine >/dev/null 2>&1; then
  echo "==> running REDmod deploy to recompile"
  ( cd "$GAME/tools/redmod/bin" && WINEDEBUG=-all wine ./redMod.exe deploy -f ) \
      > "$DIR/.deploy-uninstall.log" 2>&1 || {
        echo "error: deploy FAILED -- full log:" >&2
        cat "$DIR/.deploy-uninstall.log" >&2
        exit 1
      }
  grep -E 'Commandlet|ERROR' "$DIR/.deploy-uninstall.log" || true
else
  echo "note: wine not found, skipping deploy."
fi

echo "==> done. The Relic sickness is back to vanilla."