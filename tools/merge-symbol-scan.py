#!/usr/bin/env python3
"""
Search the compiled Cyberpunk 2077 game data for symbols relating to the
V/Johnny merge mechanic.

Reads only files that ship in the Steam install -- does NOT launch the game.

Usage:
    python3 tools/merge-symbol-scan.py [pattern ...]

With no arguments, runs a built-in set of patterns aimed at the merge mechanic.
With arguments, treats each argument as a case-insensitive literal to search for.

Why this exists
---------------
`final.redscripts` is compiled Redscript bytecode, but its string table is
plaintext. That makes every script-visible function name, TweakDB record name
and argument name greppable -- which is how the merge mechanic was located
without ever running the game.

Two files that LOOK promising and are not:

  * bin/x64/cyberpunk2077_addresses.json (132 MB) is a linker map, but only
    83 of its 987,479 entries carry a symbol name. The rest are hash-only.
  * r6/cache/tweakdb.bin (42 MB) hashes its record names. Loc strings are
    plaintext, so some names are findable, but most are not.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

GAME_ROOT = Path(
    "$GAME_DIR"
)

TARGETS = [
    GAME_ROOT / "r6/cache/final.redscripts",
    GAME_ROOT / "r6/cache/tweakdb.bin",
]

# Patterns aimed at the merge mechanic. Each is (label, compiled-regex).
DEFAULT_PATTERNS: list[tuple[str, str]] = [
    # NOTE: the game consistently misspells this as "Possesion" (one trailing s).
    # The pattern must match both spellings or it silently reports "no match".
    ("possession state", r"Possesion|Possession"),
    ("possessed-by-johnny", r"possessedByJohnny"),
    ("johnny facts", r"GetPossessedByJohnnyFactName|GetPlayAsJohnnyFactName"),
    ("replacer predicates", r"UsingJohnnyReplacer|IsPlayingAsReplacer|IsJohnnyReplacer"),
    ("replacer records", r"Character\.\w*replacer"),
    ("replacer hooks", r"OnReplacerChanged|ReplacerChangedCallback|ApplyingReplacer"),
    ("merge symptoms", r"JohnnySickness"),
    ("johnny flags", r"hasJohnny|isJohnnyUnlocked|SetWasEverJohnny|usingJhonnyReplacer"),
    ("relic facts", r"q005_lie_relic|q005_johnny_chip_acquired|q302_06_johnny_disappear"),
]

CONTEXT = 110
MAX_PER_PATTERN = 8


def search(data: bytes, pattern: re.Pattern[str], limit: int) -> list[str]:
    """Return up to `limit` unique context windows around pattern matches."""
    out: list[str] = []
    seen: set[str] = set()
    for match in pattern.finditer(data):
        start = max(0, match.start() - CONTEXT)
        end = match.start() + CONTEXT
        ctx = data[start:end].decode("latin-1").replace("\x00", "|")
        if ctx in seen:
            continue
        seen.add(ctx)
        out.append(ctx)
        if len(out) >= limit:
            break
    return out


def main() -> int:
    args = sys.argv[1:]
    if args:
        patterns = [(a, re.escape(a)) for a in args]
    else:
        patterns = DEFAULT_PATTERNS

    missing = [p for p in TARGETS if not p.exists()]
    if missing:
        print("ERROR: game data not found:", file=sys.stderr)
        for p in missing:
            print(f"  {p}", file=sys.stderr)
        print("Is Cyberpunk 2077 installed at the expected path?", file=sys.stderr)
        return 1

    total_hits = 0
    for path in TARGETS:
        data = path.read_bytes()
        print(f"\n{'=' * 78}\n{path}  ({len(data) / 1e6:.1f} MB)\n{'=' * 78}")
        for label, pattern in patterns:
            rx = re.compile(pattern.encode("latin-1"))
            hits = search(data, rx, MAX_PER_PATTERN)
            if not hits:
                print(f"\n  [no match] {label}")
                continue
            total_hits += len(hits)
            print(f"\n  [{len(hits)} hit(s)] {label}")
            for ctx in hits:
                print(f"    {ctx}")

    print(f"\n\n{total_hits} context window(s) matched.")
    return 0 if total_hits else 1


if __name__ == "__main__":
    raise SystemExit(main())