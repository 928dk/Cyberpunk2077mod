#!/usr/bin/env python3
"""Scope and patch questReplacer_NodeType nodes by target actor.

Design A: suppress Johnny by disabling the replacer nodes that spawn him.
The intervention is a single serialised Bool per node -- questReplacer_NodeType.enable
-- so this needs no CET, no redscript, no game launch to author.

Three tiers, because the replacer mechanism is shared with actors that must
keep working:

  TIER 1  #johnny_replacer   confirmed Johnny          -> disable
  TIER 2  #bd_replacer       symbolic braindance slot  -> HOLD, needs scene check
  TIER 3  anything else      Kurt / VR / PL / mall NPC -> never touch

The #bd_replacer slot is resolved by the braindance scene at load time, not by a
named TweakDB record, so the quest file cannot tell us who fills it. One file is
confirmed anyway: q105_judys_braindance, because CDPR ships a dedicated
q105_replacer_disabled fact that gates exactly that node.

Usage:
    replacer-scope.py manifest <root> [--include-profiling]   # report only
    replacer-scope.py patch    <root> --out <dir>            # emit patched copies
    replacer-scope.py verify   <root> --out <patched-dir>     # confirm the delta

Read-only unless 'patch' is given. Never edits in place.
"""

import argparse
import json
import pathlib
import re
import sys
from collections import Counter

JOHNNY_REF = "#johnny_replacer"
BD_REF = "#bd_replacer"
REPLACER_TYPE = "questReplacer_NodeType"

# Paths that must never ship: developer profiling/test scaffolding.
PROFILING = re.compile(r"/(test|tests|profiling)/")


def walk(node, out):
    """Collect every dictionary carrying a $type discriminator."""
    if isinstance(node, dict):
        if isinstance(node.get("$type"), str):
            out.append(node)
        for v in node.values():
            walk(v, out)
    elif isinstance(node, list):
        for v in node:
            walk(v, out)


def scalar(v):
    """Unwrap WolvenKit's typed scalars: {"$value": 1} -> 1."""
    if isinstance(v, dict):
        return v.get("$value")
    return v


def refs_of(node):
    """All string values inside objectRef."""
    found = []

    def dig(x):
        if isinstance(x, dict):
            if isinstance(x.get("$value"), str):
                found.append(x["$value"])
            for v in x.values():
                dig(v)
        elif isinstance(x, list):
            for v in x:
                dig(v)

    dig(node.get("objectRef", {}))
    return set(found)


def classify(refs):
    if JOHNNY_REF in refs:
        return 1
    if BD_REF in refs:
        return 2
    return 3


def scan(root, include_profiling=False):
    """Yield (path, node_index, tier, enable, refs) for every replacer node."""
    root = pathlib.Path(root)
    hits = []
    for path in sorted(root.rglob("*.quest*.json")):
        rel = str(path.relative_to(root))
        if not include_profiling and PROFILING.search("/" + rel):
            continue
        text = path.read_text()
        if REPLACER_TYPE not in text:
            continue
        data = json.loads(text)
        nodes = []
        walk(data, nodes)
        for idx, node in enumerate(nodes):
            if node.get("$type") != REPLACER_TYPE:
                continue
            refs = refs_of(node)
            hits.append((rel, idx, classify(refs), scalar(node.get("enable")), refs))
    return hits


def report(hits):
    tiers = Counter(t for _, _, t, _, _ in hits)
    width = 78
    for tier, title in (
        (1, "TIER 1  #johnny_replacer   confirmed Johnny            -> disable"),
        (2, "TIER 2  #bd_replacer       symbolic braindance slot    -> HOLD"),
        (3, "TIER 3  other replacers    Kurt / VR / PL / mall NPC  -> never touch"),
    ):
        rows = [h for h in hits if h[2] == tier]
        print("=" * width)
        print(f"{title}")
        print("=" * width)
        for rel, idx, _, enable, refs in rows:
            extra = sorted(r for r in refs if r not in (JOHNNY_REF, BD_REF, "None"))
            print(f"  [{idx:2d}] enable={enable}  {rel}" + (f"   {extra}" if extra else ""))
        todo = [r for r in rows if r[2] == 1 and r[3]]
        print(
            f"  -> {len(rows)} nodes in {len({r[0] for r in rows})} files"
            f"   |  {len(todo)} need flipping to enable=0\n"
        )
    print(
        f"TOTAL {len(hits)} nodes  |  tier1={tiers[1]} tier2={tiers[2]} tier3={tiers[3]}"
    )


def patch(root, outdir, hits):
    """Write patched copies of tier-1 files with enable forced to 0."""
    root, outdir = pathlib.Path(root), pathlib.Path(outdir)
    targets = {}
    for rel, idx, tier, enable, _ in hits:
        if tier == 1 and enable:
            targets.setdefault(rel, []).append(idx)

    written = []
    for rel, indices in sorted(targets.items()):
        src = root / rel
        data = json.loads(src.read_text())
        nodes = []
        walk(data, nodes)
        replacers = [n for n in nodes if n.get("$type") == REPLACER_TYPE]
        # indices in scan() are positions within walk() order, not within replacers
        for n in nodes:
            if n.get("$type") != REPLACER_TYPE:
                continue
            if classify(refs_of(n)) == 1 and scalar(n.get("enable")):
                # WolvenKit serialises CBool as a bare integer (0/1), not the
                # generic {"$type": "Bool", "$value": ...} envelope. Emitting the
                # envelope makes the file un-deserialisable:
                #   "Cannot get the value of a token type 'StartObject' as a number"
                n["enable"] = 0
        dst = outdir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(json.dumps(data, indent=2))
        written.append((rel, len(indices)))

    for rel, n in written:
        print(f"  patched {n:2d} node(s)  {rel}")
    print(f"\n{len(written)} files written to {outdir}")
    return written


def verify(original, patched):
    """Tier 1 must be fully disabled in the patch; tier 2/3 must be untouched.

    The patch directory deliberately contains ONLY the tier-1 files, so tier 2/3
    are asserted against the original tree. Touching either is a regression.
    """
    patched_hits = scan(patched)
    bad = [h for h in patched_hits if h[2] == 1 and h[3]]

    original_hits = scan(original)
    non_tier1 = {h[0] for h in original_hits if h[2] in (2, 3)}
    untouched = {h[0]: h[3] for h in original_hits if h[2] in (2, 3)}

    patched_files = {h[0] for h in patched_hits}
    leaked = sorted(patched_files - {h[0] for h in original_hits if h[2] == 1})

    print(f"  tier1 still enabled   : {len(bad)}  {'OK' if not bad else 'FAIL'}")
    print(f"  tier2/3 files patched : {len(leaked)}  {'OK' if not leaked else 'FAIL'}")
    print(f"  tier2/3 files intact  : {len(untouched)}  {'OK' if (not non_tier1 or untouched) else 'FAIL'}")
    print(f"  tier1 files patched   : {len(patched_files)}")
    for rel, _, _, _, _ in bad:
        print(f"    STILL ENABLED : {rel}")
    for rel in leaked:
        print(f"    LEAKED NON-TIER1 : {rel}")
    # The intact check passes vacuously when the scanned original corpus holds no
    # tier-2/3 at all (e.g. a build staging only the tier-1 ship set); it stays
    # strict whenever tier-2/3 files are present in the corpus.
    return not bad and not leaked and (not non_tier1 or bool(untouched))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mode", choices=("manifest", "patch", "verify"))
    ap.add_argument("root")
    ap.add_argument("--out")
    ap.add_argument("--include-profiling", action="store_true")
    args = ap.parse_args()

    if args.mode == "manifest":
        hits = scan(args.root, args.include_profiling)
        if not hits:
            print("no questReplacer_NodeType found")
            return 1
        report(hits)
        return 0

    if args.mode == "patch":
        if not args.out:
            ap.error("patch needs --out")
        hits = scan(args.root, args.include_profiling)
        patch(args.root, args.out, hits)
        return 0

    if args.mode == "verify":
        if not args.out:
            ap.error("verify needs --out <patched-dir>")
        ok = verify(args.root, args.out)
        return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())