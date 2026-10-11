#!/usr/bin/env python3
"""Find which scene resources spawn an actor by TweakDB character record.

Why this tool exists
--------------------
`replacer-scope.py` answers "which quest files carry questReplacer_NodeType".
This answers the other half: "which scene files put Johnny on screen WITHOUT a
replacer". Finding 06 assumed the replacer was the whole mechanism. It is not.

The trap that makes this non-obvious: CR2W stores a TweakDBID as a 64-bit
*hash*, not as a string. `grep -r Character.Silverhand` over extracted .scene
files returns ZERO hits -- the name only reappears after WolvenKit serialises the
resource against TweakDB. A first pass at this analysis therefore "proved" that
no scene referenced Silverhand, and that conclusion was wrong.

So we scan for the hash instead:

    TweakDBID(name) = crc32(name) | (len(name) << 32)        little-endian uint64

NodeRefs are stored as plain strings, so `#johnny_replacer` is greppable and the
two mechanisms need different lookups. Both are reported side by side on purpose:
the ratio between them is the finding.

Usage:
    scene-actor-scan.py scan <root> [--manifest PATH] [--include-versions]
    scene-actor-scan.py verify <root> <serialized-scene.json>

`verify` is the self-check: it resolves TweakDBIDs out of a WolvenKit-serialised
JSON, computes their hashes, and confirms each hash is present in the matching
binary .scene. If it passes, the hash scan is sound for this file; if the file
has zero records it is vacuous. Run it on any extracted scene before trusting a
count from a game patch.

Read-only. Never edits anything.
"""

import argparse
import json
import pathlib
import re
import sys
import zlib

# Johnny, by the two mechanisms that can put him on screen.
DEFAULT_TARGETS = ("Character.Silverhand", "Character.johnny_replacer")

# Historical patch variants live under .../versions/<patch>/ and would double-count.
VERSIONS = re.compile(r"/versions/")

# Nodes that reference the replacer slot by name (stored as strings, so greppable).
NODE_REF_RE = re.compile(rb"#johnny_replacer")


def tweakdbid(name: str) -> int:
    """CR2W TweakDBID: crc32 of the ASCII name, with the length in the high 32 bits."""
    crc = zlib.crc32(name.encode("ascii")) & 0xFFFFFFFF
    return crc | (len(name) << 32)


def hash_le(name: str) -> bytes:
    return tweakdbid(name).to_bytes(8, "little")


def scene_files(root: pathlib.Path, include_versions: bool):
    for path in root.rglob("*.scene"):
        rel = "/" + path.relative_to(root).as_posix()
        if not include_versions and VERSIONS.search(rel):
            continue
        yield path


def scan(root: pathlib.Path, targets, include_versions: bool):
    targets = list(targets)
    patterns = {t: hash_le(t) for t in targets}
    refs = {t: NODE_REF_RE for t in targets}

    by_target = {t: [] for t in targets}
    ref_hits = {t: [] for t in targets}
    total = 0
    total_bytes = 0

    for path in scene_files(root, include_versions):
        total += 1
        try:
            data = path.read_bytes()
        except OSError:
            continue
        total_bytes += len(data)
        for t in targets:
            if patterns[t] in data:
                by_target[t].append(path.relative_to(root).as_posix())
            if t == "Character.Silverhand" and refs[t].search(data):
                ref_hits[t].append(path.relative_to(root).as_posix())

    return {
        "root": str(root),
        "scene_count": total,
        "bytes_read": total_bytes,
        "targets": targets,
        "by_tweakdbid": by_target,
        "by_node_ref": ref_hits,
        "hashes": {t: f"0x{tweakdbid(t):016x}" for t in targets},
    }


def render(result) -> str:
    out = []
    out.append("=" * 78)
    out.append("SCENE ACTOR SCAN -- how each target actor reaches a scene")
    out.append("=" * 78)
    out.append(f"root        : {result['root']}")
    out.append(f"scenes read : {result['scene_count']}")
    out.append("variants    : " + ("INCLUDED (/versions/)" if result.get("include_versions")
                                 else "excluded (/versions/, historical patch copies)"))
    out.append("")
    out.append("TweakDBID hashes (why plain grep finds nothing):")
    for t, h in result["hashes"].items():
        out.append(f"  {t:32s} {h}")
    out.append("")
    out.append("-" * 78)
    out.append("RESULT -- by TweakDB record (actor is named by character record)")
    out.append("-" * 78)
    for t in result["targets"]:
        out.append(f"  {t:32s} {len(result['by_tweakdbid'][t]):5d} scenes")
    out.append("")
    out.append("-" * 78)
    out.append("RESULT -- by NodeRef string (actor is named by slot)")
    out.append("-" * 78)
    out.append(f"  {'#johnny_replacer':32s} {sum(len(v) for v in result['by_node_ref'].values()):5d} scenes")
    out.append("")
    out.append("Interpretation:")
    out.append("  A TweakDBID hit means the scene names the CHARACTER RECORD. It does not by")
    out.append("  itself prove the actor is spawned -- it is also the record selector used by")
    out.append("  questCharacterManagerParameters_SetStatusEffect. Serialise a sample before")
    out.append("  quoting a file as a spawn site; `verify` below automates that check.")
    return "\n".join(out)


def collect_tweakdbids(node, out):
    """Collect TweakDBID values out of a WolvenKit-serialised CR2W JSON."""
    if isinstance(node, dict):
        if node.get("$type") == "TweakDBID":
            value = node.get("$value")
            if isinstance(value, str) and value and value != "0":
                out.add(value)
        for v in node.values():
            collect_tweakdbids(v, out)
    elif isinstance(node, list):
        for v in node:
            collect_tweakdbids(v, out)


def verify(root: pathlib.Path, json_path: pathlib.Path) -> int:
    doc = json.loads(json_path.read_text(encoding="utf-8"))
    names = set()
    collect_tweakdbids(doc, names)

    binary = json_path.with_suffix("")
    if not binary.exists():
        print(f"FAIL  no matching .scene next to {json_path}", file=sys.stderr)
        return 2

    data = binary.read_bytes()
    missing = sorted(n for n in names if hash_le(n) not in data)

    print(f"scene            : {binary.name}")
    print(f"TweakDBID records: {len(names)}")
    for n in sorted(names):
        state = "FOUND" if hash_le(n) in data else "MISSING"
        print(f"  {n:44s} 0x{tweakdbid(n):016x}  {state}")

    if not names:
        print("FAIL  no TweakDBIDs in the file -- the check would be vacuous", file=sys.stderr)
        return 2
    if missing:
        print(f"FAIL  {len(missing)} record(s) unresolved in the binary: {missing}",
              file=sys.stderr)
        return 1
    print("OK    every record resolves: the hash scan is sound for this file")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("scan", help="count scenes referencing each target record")
    s.add_argument("root", type=pathlib.Path, help="directory of extracted .scene files")
    s.add_argument("--target", action="append", dest="targets",
                   help="override the default TweakDB targets (repeatable)")
    s.add_argument("--include-versions", action="store_true",
                   help="also count /versions/ historical patch copies")
    s.add_argument("--manifest", type=pathlib.Path,
                   help="also write the per-file manifest here")

    v = sub.add_parser("verify", help="self-check: hash-scan soundness against one scene")
    v.add_argument("root", type=pathlib.Path)
    v.add_argument("scene_json", type=pathlib.Path)

    args = p.parse_args()

    if args.cmd == "verify":
        return verify(args.root, args.scene_json)

    if not args.root.is_dir():
        print(f"error: not a directory: {args.root}", file=sys.stderr)
        return 2

    result = scan(args.root, args.targets or DEFAULT_TARGETS, args.include_versions)
    result["include_versions"] = args.include_versions
    print(render(result))

    if args.manifest:
        lines = [
            "=" * 78,
            "SCENE ACTOR MANIFEST",
            "=" * 78,
            f"root        : {result['root']}",
            f"scenes read : {result['scene_count']}",
            f"variants    : {'INCLUDED' if args.include_versions else 'excluded (/versions/)'}",
            "",
        ]
        for t in result["targets"]:
            lines += ["=" * 78,
                      f"TARGET {t}   tweakdbid=0x{tweakdbid(t):016x}   "
                      f"scenes={len(result['by_tweakdbid'][t])}",
                      "=" * 78]
            lines += sorted(result["by_tweakdbid"][t])
            lines.append("")
        lines += ["=" * 78,
                  "TOTAL",
                  "=" * 78]
        for t in result["targets"]:
            lines.append(f"  {t:32s} {len(result['by_tweakdbid'][t])} scenes "
                         f"(TweakDBID record)")
        lines.append(f"  {'#johnny_replacer':32s} "
                     f"{sum(len(v) for v in result['by_node_ref'].values())} scenes "
                     f"(NodeRef string)")
        args.manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"\nmanifest written: {args.manifest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())