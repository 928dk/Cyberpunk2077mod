---
title: "Implementation Plan: Bypass V-Johnny Merge [template:examples/level_1/plan.md]"
description: "planning required for the Cyberpunk 2077 merge bypass. The plan is research-first"
trigger_phrases:
  - "implementation"
  - "plan"
  - "cyberpunk"
  - "merge"
  - "johnny"
  - "bypass"
importance_tier: "normal"
contextType: "general"
_memory:
  continuity:
    packet_pointer: "specs/001-bypass-v-johnny-merge"
    last_updated_at: "2026-10-03T00:00:00Z"
    last_updated_by: "big-pickle"
    recent_action: "Design A chosen: disable questReplacer nodes; tooling built and round-trip verified"
    next_safe_action: "apply Design A patch, then verify enable=false at runtime (T042)"
    blockers:
      - "modding layers not installed in the game"
      - "layer choice still unresolved: state is readable, writability unknown"
    key_files:
      - "$PROJECT/.opencode/specs/001-bypass-v-johnny-merge/spec.md"
      - "$PROJECT/.opencode/specs/001-bypass-v-johnny-merge/tasks.md"
    session_dedup:
      fingerprint: "sha256:c56986f341d4975219e4f4e62ff5f59c1147b3ff5887382f6694bc5deea4510f"
      session_id: "001-bypass-v-johnny-merge"
      parent_session_id: null
    completion_pct: 70
---
# Implementation Plan: Bypass V-Johnny Merge

<!-- SPECKIT_LEVEL: 1 -->
<!-- SPECKIT_TEMPLATE_SOURCE: plan-core | v2.2 -->

---

<!-- ANCHOR:summary -->
## 1. SUMMARY

### Technical Context

| Aspect | Value |
|--------|-------|
| **Language** | Lua (CET), Redscript (`.reds`), possibly TweakDB |
| **Target** | Cyberpunk 2077, main Relic storyline |
| **Platform** | Windows (via Proton/Steam Deck compat prefix on this machine) |
| **Mod layer** | CET → Redscript → REDmod, in that order of preference |
| **Performance** | Must be negligible; a per-frame hook is acceptable, per-tick allocation is not |
| **Tooling** | WolvenKit, CyberpunkSaveEditor, Cyber Engine Tweaks |
| **Baseline saves** | `ManualSave-5` (pre-Heist), `ManualSave-6` (post-Heist) |

### Approach

Research-first. The merge trigger is not yet identified, and every implementation choice depends on
whether that trigger is scriptable. Therefore Phase 1 is investigation, not coding.

Matrix axes — the decision surface:

| Axis | Options |
|------|---------|
| Trigger location | scripted quest phase / engine engram system / TweakDB condition |
| Intervention | skip the phase / invert a condition / replace the resolution scene |
| Layer | CET Lua / Redscript override / TweakDB edit / WolvenKit quest edit |
| Path | A: block merge / B: alternative removal resolution |

Required rows before implementation is attempted: at least one confirmed trigger location, and at
least one confirmed intervention point per viable layer.


<!-- /ANCHOR:summary -->
---

<!-- ANCHOR:quality-gates -->
## 2. QUALITY GATES

These must pass before any claim of success. No gate may be skipped or self-certified by reading code.

| Gate | Check | Pass condition |
|------|-------|----------------|
| G1 | Save load | `ManualSave-5` loads without a repair prompt |
| G2 | Baseline run | The Heist completes unmodified, merge occurs (confirms the baseline) |
| G3 | Mod load | CET reports the mod loaded; no errors in `Cyber Engine Tweaks\red4ext\cet.log` or the redscript output |
| G4 | Merge blocked | Relic arc completes with V intact, no merge |
| G5 | World intact | All districts traversable; ≥1 side gig and ≥1 NCPD/cyberpsycho activity complete |
| G6 | No softlock | The next Relic quest is issued after the intervention point |
| G7 | Rollback | Removing the mod and reloading the save restores vanilla behaviour |


<!-- /ANCHOR:quality-gates -->
---

<!-- ANCHOR:architecture -->
## 3. ARCHITECTURE

### High-Level Design

```
┌──────────────────────────────────────────────────────────┐
│ Game install                                            │
│                                                          │
│  Relic quest phase ──► merge trigger ──► V+Johnny merged │
│         │                    │                           │
│         │                    └── where? (Phase 1 answers)│
│         │                                                │
│  mod layers (in order of preference)                     │
│    1. CET       red4ext/<mod>/  Lua, hot-reload         │
│    2. Redscript redscripts/<mod>/ script override        │
│    3. REDmod    red4ext/r6/scripts/mod/  pack + install  │
│    4. TweakDB   mods/<mod>/  condition edits             │
└──────────────────────────────────────────────────────────┘
```

### Component Strategy

| Component | Why | Risk |
|-----------|-----|------|
| **CET (Lua)** | No archive edits, instant reload, easy to bisect. Best for probing what is callable. | May have no hook into the merge system |
| **Redscript** | Correct layer if the trigger is in a `.reds` quest script | Requires exact vanilla source to override against; breaks on patch |
| **REDmod** | Packaging so the mod loads as one removable unit | Thin wrapper; adds no capability |
| **TweakDB** | Correct if the trigger is a quest/objective condition | Broad blast radius; easy to break unrelated content |
| **WolvenKit quest edit** | Last resort for trigger points with no script surface | Deep archive surgery; highest rollback cost |


<!-- /ANCHOR:architecture -->
---

<!-- ANCHOR:phases -->
## 4. IMPLEMENTATION PHASES

### Phase 1: Locate the trigger (no code)

- Diff the fact store between `ManualSave-5` (pre-Heist) and `ManualSave-6` (post-Heist, same
  playthrough, same day) to isolate what The Heist writes.
- Unpack game archives with WolvenKit; inspect `q005_heist` and the Relic arc scripts for the merge
  code path.
- Search for existing mods that reduce or gate Johnny — reuse before inventing.

**Exit criterion**: a named trigger with a file path and identifier, or a documented proof that no
script-level trigger exists.

### Phase 2: Choose the intervention

- Map the trigger to a hook point per viable layer.
- Pick the lowest-risk layer that can reach it.
- Write the rollback procedure first, before the change.

**Exit criterion**: one chosen layer, one hook point, one rollback command.

### Phase 3: Prototype

- Implement the smallest possible intervention.
- Prefer a reversible, toggleable mod with a config flag defaulting to on.

**Exit criterion**: the mod loads and changes the trigger, verified by observation, not by assumption.

### Phase 4: Verify against the gates

- Run G1 through G7 in order on the baseline save.
- Record actual results, including failures.

**Exit criterion**: all gates pass, or failures are documented with evidence.


<!-- /ANCHOR:phases -->
---

<!-- ANCHOR:testing -->
## 5. TESTING STRATEGY

### Test Matrix

| # | Save | Mod | Expectation |
|---|------|-----|--------------|
| T1 | ManualSave-5 | off | Merge occurs — baseline confirmation |
| T2 | ManualSave-5 | on | No merge; V intact through the Relic arc |
| T3 | ManualSave-6 | on | Relic arc resumes past The Heist without merge |
| T4 | T2 save | off again | Vanilla behaviour restored, no repair prompt |

### Manual Verification

Since this is a narrative mod, verification is play-based. Each test is a manual pass:

1. Load the save, confirm state.
2. Perform The Heist.
3. Continue the Relic arc, watching for the merge.
4. Walk through each district.
5. Complete one side gig and one NCPD/cyberpsycho activity.

Automated checks apply only to the mod's own syntax (`bash -n` on launchers, CET's Lua load, the
Redscript compile output) — not to game behaviour.


<!-- /ANCHOR:testing -->
---

<!-- ANCHOR:dependencies -->
## 6. DEPENDENCIES

### External

| Dependency | Purpose | Status |
|------------|---------|--------|
| Cyber Engine Tweaks | Lua runtime for the mod | Not installed in game |
| Redscript | Script overrides, if needed | Not installed in game |
| REDmod | Modlet packaging | Not installed in game |
| WolvenKit | Archive unpacking and quest editing | Cloned at `~/projects/Cyberpunk-tooling/WolvenKit` |
| CyberpunkSaveEditor | Save fact inspection | Cloned at `~/projects/Cyberpunk-tooling/CyberpunkSaveEditor` |
| Cyberpunk-Modding-Docs | Quest and scene reference | Cloned at `~/projects/Cyberpunk-tooling/Cyberpunk-Modding-Docs` |

### Internal

- Research record: `findings/trigger-research.md`, `findings/01-savegame-survey.md`
- Working project: `~/projects/Client/Cyberpunk2077mod/`


<!-- /ANCHOR:dependencies -->
---

<!-- ANCHOR:rollback -->
## 7. ROLLBACK PLAN

| Change | Rollback |
|--------|----------|
| CET mod | Delete the mod folder from `red4ext/`; CET hot-reloads without a restart |
| Redscript override | Delete the `.reds` override; vanilla script is restored on next load |
| REDmod modlet | Disable the modlet in the mod manager, or delete its folder |
| TweakDB edit | Remove the mod's TweakDB folder; vanilla TweakDB is restored |
| Any save-state change | Restore the save folder from a copy taken before the test run |

Before any test run, copy the save folder to a timestamped backup. Saves are the only irreplaceable
state here — the mod itself is always removable.


<!-- /ANCHOR:rollback -->