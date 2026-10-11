#!/usr/bin/env bash
# Build the Nexus release archives under dist/.
#
# NoRelicSickness ships as a TweakXL drop-in: one r6/tweaks/*.yaml overlay plus a
# README. No game file is patched and there is no deploy step.
#
# NoJohnnyReplacer needs WolvenKit to serialize patched .quest/.questphase
# resources into an archive. Until that round-trip is demonstrated this script
# reports the target as not built rather than shipping a stub.
#
# Usage:
#   ./tools/build-nexus-zips.sh [--version X.Y.Z] [--only NAME] [--check]
#
#   --version   release version stamped into the archive file name (default 1.0.0)
#   --only      build one target only: NoRelicSickness | NoJohnnyReplacer
#   --check     regenerate + verify the TweakXL overlay first. Needs a vanilla
#               tweaks tree in $CP2077_VANILLA_TWEAKS
#               (default: src/no-relic-sickness/.backup)
#
# dist/ is git-ignored.

set -euo pipefail

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
cd "$DIR"

VERSION="1.0.0"
ONLY=""
CHECK=0
while [ $# -gt 0 ]; do
  case "$1" in
    --version) VERSION="$2"; shift 2;;
    --only)    ONLY="$2";    shift 2;;
    --check)   CHECK=1;      shift;;
    -h|--help) sed -n '2,19p' "$0"; exit 0;;
    *)         echo "unknown argument: $1" >&2; exit 2;;
  esac
done

case "$ONLY" in
  ""|NoRelicSickness|NoJohnnyReplacer) ;;
  *) echo "unknown --only target: $ONLY" >&2; exit 2;;
esac

want() { [ -z "$ONLY" ] || [ "$ONLY" = "$1" ]; }

SICK_YAML="src/no-relic-sickness/tweaks/NoRelicSickness.yaml"
OUT="$DIR/dist"
mkdir -p "$OUT"

# ---- optional regenerate + verify ---------------------------------------
if [ "$CHECK" = 1 ]; then
  VANILLA="${CP2077_VANILLA_TWEAKS:-src/no-relic-sickness/.backup}"
  if [ ! -d "$VANILLA" ]; then
    echo "error: --check wants a vanilla tweaks tree; point" >&2
    echo "       CP2077_VANILLA_TWEAKS at <Cyberpunk 2077>/tools/redmod/tweaks" >&2
    exit 2
  fi
  echo "==> regenerating the TweakXL overlay from $VANILLA"
  python3 tools/sickness-tweak.py yaml        --vanilla-root "$VANILLA" --out "$SICK_YAML"
  python3 tools/sickness-tweak.py verify-yaml --vanilla-root "$VANILLA" --yaml "$SICK_YAML"
fi

# A real YAML parse, independent of the tool's own structural check.
python3 - "$SICK_YAML" <<'PY'
import sys, yaml
with open(sys.argv[1]) as fh:
    data = yaml.safe_load(fh)
assert isinstance(data, dict) and data, "overlay is empty or not a mapping"
print(f"YAML parses: {len(data)} record overrides")
PY

# ---- NoRelicSickness -----------------------------------------------------
build_sickness() {
  local stage="$OUT/NoRelicSickness"
  local zip="$OUT/NoRelicSickness-$VERSION.zip"
  rm -rf "$stage" "$zip"
  mkdir -p "$stage/r6/tweaks"
  cp "$SICK_YAML" "$stage/r6/tweaks/NoRelicSickness.yaml"
  cp "src/no-relic-sickness/RELEASE.txt" "$stage/README.txt"
  ( cd "$stage" && zip -q -r "$zip" r6 README.txt )
  echo "==> $zip"
  unzip -l "$zip"
}

# ---- NoJohnnyReplacer ----------------------------------------------------
build_johnny() {
  echo "==> NoJohnnyReplacer: NOT BUILT"
  echo "    The archive needs patched .quest/.questphase resources serialized and"
  echo "    packed by WolvenKit, which is still a source checkout with no proven"
  echo "    CLI round-trip on this machine. The keystone assumption (that"
  echo "    questReplacer_NodeType.enable=false is honoured at runtime) is also"
  echo "    unverified. Publishing a stub would be worse than publishing nothing."
  echo "    See .opencode/specs/003-nexus-release/plan.md (Phase 2)."
  return 1
}

if want NoRelicSickness; then build_sickness; fi

if want NoJohnnyReplacer; then
  if ! build_johnny; then
    [ -n "$ONLY" ] && exit 1   # asked for it explicitly -> hard fail
  fi
fi

echo "==> done"
