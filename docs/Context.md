# Project Context

## Overview

Cyberpunk 2077 mod that aims to prevent V and Johnny Silverhand from merging during the Relic
storyline, while keeping the rest of Night City's areas and quests reachable.

Two paths are being evaluated:

- **Path A — prevent the merge.** Block or skip whatever the game uses to force the merge. Preferred,
  because it is the least invasive: nothing else in the story changes.
- **Path B — alternative resolution.** If the merge cannot be blocked cleanly, inject or repurpose a
  quest beat that removes Johnny (the game already has a "Johnny disappears" scene) or author an
  alternate story branch.

Phantom Liberty is explicitly out of scope.

## Architecture

### High-Level Design

The mod lives in the Cyberpunk 2077 modding layers, not in the game archives:

```
┌─────────────────────────────────────────────────────────┐
│ Game install                                           │
│  └─ mods/                                              │
│     ├─ red4ext/  ← CET (Lua)      runtime hooks         │
│     └─ redscripts/ ← Redscript    script overrides      │
├─────────────────────────────────────────────────────────┤
│ Research layer (this repo)                              │
│  ├─ Cyberpunk-Modding-Docs/   CDPR modding reference    │
│  ├─ WolvenKit/                archive + quest editing   │
│  ├─ CyberpunkSaveEditor/      save fact inspection      │
│  └─ CyberEngineTweaks/        CET source + API          │
└─────────────────────────────────────────────────────────┘
```

### Components

| Component | Purpose | Status |
| --- | --- | --- |
| `src/` | The actual mod: Lua for CET, `.reds` for Redscript | Empty — placeholder only |
| `research/` | Notes and extracts from the cloned tooling | Populated via spec `findings/` |
| `analysis/` | Fact diffs, quest maps, data dumps | Not started |
| `tools/` | Helper scripts (save scanning, etc.) | Not started |
| `tests/` | Verification runs | Not started |
| `docs/` | Project documentation | Scaffolded |

## Dependencies

Runtime, inside the game:
- **Cyber Engine Tweaks** (CET) — Lua runtime, hot-reloadable, no archive edits. Preferred prototyping surface.
- **Redscript** — replaces vanilla `.reds` scripts. Needed if the trigger lives in scripted quest logic.
- **REDmod** — modlet packaging so the mod loads as one unit.
- **TweakDB** — only if the trigger turns out to be a TweakDB-driven condition.

Research, on this machine:
- Python 3.14.7 at `/usr/bin/python3`
- The five cloned repos under `~/projects/Client/Cyberpunk2077mod/`

Game assets are **not** unpacked on this machine yet. WolvenKit can unpack
`~/projects/../Steam/steamapps/common/Cyberpunk 2077` if quest-level detail is needed.

## Related Projects

- Spec folder `001-bypass-v-johnny-merge` in the parent directory — the research record for this work.
- Cyberpunk-Modding-Docs — upstream CDPR documentation, the canonical quest/scene reference.
- WolvenKit — the tool for actually editing quests and scenes if the merge is scripted there.