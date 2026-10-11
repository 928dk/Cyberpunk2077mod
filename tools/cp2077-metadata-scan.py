#!/usr/bin/env python3
"""Survey Cyberpunk 2077 savegames from their metadata sidecars.

Answers: which playthroughs exist, where each one sits relative to The Heist
(q005) and Tapeworm (sq032), and which save is the best pre-merge baseline.

Usage:
    CP2077_SAVED_GAMES="/path/to/Saved Games/CD Projekt Red/Cyberpunk 2077" \
        python3 tools/cp2077-metadata-scan.py

If CP2077_SAVED_GAMES is unset, common Steam/Proton layouts are probed.
Save *contents* are never modified or read -- metadata sidecars only.

Three format traps, all documented in findings/01-savegame-survey.md, each of
which silently produced wrong results when this was first written naively:

1. The sidecar is `metadata.9.json`, NOT `metadata.json`. Testing for
   `metadata.json` matches nothing, so a naive scan reports "all saves
   identical" -- which is what happened.

2. The payload is nested three levels: RootType -> Data -> metadata. Reading
   `data.get('finishedQuests')` at the top level returns None every time.

3. `finishedQuests` is a SPACE-SEPARATED STRING, not a list, so `'q005' in
   finished` is a substring test that matches 'q0051' too. Must split() first.

`timestampString` is "HH:MM:SS, D.M.YYYY" -- no year-first prefix -- so
sorting it as a string sorts by time of day, not by date. Parsed here.
"""

import datetime
import json
import os
import sys
from pathlib import Path

# Quest completion markers used to locate a save on the story timeline.
HEIST = "q005"  # The Heist -- installs the Relic, where Johnny first appears
TAPEWORM = "sq032"  # Tapeworm -- the in-game quest that can banish Johnny

PROBE_PATHS = [
    "$HOME/.local/share/Steam/steamapps/compatdata/1091500/pfx/drive_c/users/steamuser/"
    "Saved Games/CD Projekt Red/Cyberpunk 2077",
    "$HOME/.local/share/Steam/steamapps/common/Cyberpunk 2077/saved/game saves",
    "$HOME/saved games/CD Projekt Red/Cyberpunk 2077",
]


def resolve_base():
    """Locate the save directory: env var first, then known layouts."""
    env = os.environ.get("CP2077_SAVED_GAMES")
    if env:
        base = Path(env).expanduser()
        if not base.is_dir():
            sys.exit(f"CP2077_SAVED_GAMES does not exist: {base}")
        return base
    for raw in PROBE_PATHS:
        cand = Path(os.path.expandvars(raw)).expanduser()
        if cand.is_dir():
            return cand
    sys.exit(
        "Could not find the save directory. Set it explicitly:\n"
        "  CP2077_SAVED_GAMES='/path/to/CD Projekt Red/Cyberpunk 2077' \\\n"
        "      python3 tools/cp2077-metadata-scan.py"
    )


def parse_timestamp(raw):
    """'HH:MM:SS, D.M.YYYY' -> datetime. Month name is locale-dependent."""
    if not raw:
        return None
    for fmt in ("%H:%M:%S, %d.%m.%Y", "%H:%M:%S, %d.%b.%Y"):
        try:
            return datetime.datetime.strptime(raw.strip(), fmt)
        except ValueError:
            continue
    return None


def read_sidecar(save_dir):
    """Return (timestamp_raw, playthrough_id, finished_set) or None.

    Handles trap 1 by globbing for any metadata.*.json sidecar.
    """
    sidecars = sorted(save_dir.glob("metadata.*.json"))
    for path in sidecars:
        try:
            root = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        # trap 2: payload lives under Data -> metadata
        meta = root.get("Data", {}).get("metadata")
        if not isinstance(meta, dict):
            continue
        finished = meta.get("finishedQuests") or ""
        # trap 3: space-separated string, must split before membership testing
        finished_set = set(finished.split()) if isinstance(finished, str) else set(finished)
        return meta.get("timestampString", ""), meta.get("playthroughID", ""), finished_set
    return None


def main():
    base = resolve_base()
    print(f"Save directory: {base}\n")

    rows = []
    for save_dir in sorted(p for p in base.iterdir() if p.is_dir()):
        parsed = read_sidecar(save_dir)
        if parsed is None:
            continue
        ts_raw, pid, finished = parsed
        rows.append(
            {
                "name": save_dir.name,
                "ts_raw": ts_raw,
                "ts": parse_timestamp(ts_raw),
                "pid": pid,
                "finished": finished,
                "heist": HEIST in finished,
                "tapeworm": TAPEWORM in finished,
                "count": len(finished),
            }
        )

    if not rows:
        print("No save directory contained a readable metadata sidecar.")
        return 1

    # Sort by parsed date; fallback to name so ordering is at least stable.
    rows.sort(key=lambda r: (r["ts"] is None, r["ts"] or datetime.datetime.min, r["name"]))

    playthroughs = {}
    for r in rows:
        playthroughs.setdefault(r["pid"], []).append(r)

    print("=" * 78)
    print("PLAYTHROUGHS")
    print("=" * 78)
    for pid, saves in playthroughs.items():
        dates = [s["ts"] for s in saves if s["ts"]]
        span = f"{min(dates):%b %Y} - {max(dates):%b %Y}" if dates else "unknown dates"
        finished_any = set().union(*(s["finished"] for s in saves))
        print(f"  {pid or '(none)':10s} {len(saves):4d} saves   {span}")
        print(f"  {'':10s} reaches: q005={HEIST in finished_any} sq032={TAPEWORM in finished_any}")

    print()
    print("=" * 78)
    print(f"BASELINE CANDIDATES  (q004 done, {HEIST} NOT done, {TAPEWORM} not done)")
    print("=" * 78)
    baseline = [r for r in rows if r["heist"] is False and r["tapeworm"] is False and "q004" in r["finished"]]
    if not baseline:
        print("  none -- no save sits before The Heist.")
    for r in baseline:
        # Best baseline = pre-Heist AND earliest, i.e. furthest from any merge state.
        tag = "  <-- earliest pre-Heist, furthest from merge state" if r is baseline[0] else ""
        print(f"  {r['name']:26s} {r['ts_raw']:22s} pid={r['pid']:10s} n={r['count']}{tag}")

    print()
    print("=" * 78)
    print(f"MERGE-BOUNDARY CANDIDATES  ({HEIST} done)")
    print("=" * 78)
    boundary = [r for r in rows if r["heist"]]
    for r in boundary[:10]:
        print(f"  {r['name']:26s} {r['ts_raw']:22s} pid={r['pid']:10s} n={r['count']}")
    if len(boundary) > 10:
        print(f"  ... and {len(boundary) - 10} more")

    print()
    print("Note: finishedQuests records quest COMPLETION, not the merge itself.")
    print("      Finding the merge trigger needs the fact store in the save body,")
    print("      which this tool deliberately does not read.")
    return 0


if __name__ == "__main__":
    sys.exit(main())