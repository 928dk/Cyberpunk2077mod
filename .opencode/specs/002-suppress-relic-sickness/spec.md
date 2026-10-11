---
title: "Spec: Suppress Relic Sickness [template:examples/level_1/spec.md]"
description: "required for NoRelicSickness. Level 1 because the edit is two TweakDB files and"
trigger_phrases:
  - "relic"
  - "sickness"
  - "tweakdb"
  - "cyberpunk"
  - "mod"
  - "neutralise"
importance_tier: "normal"
contextType: "general"
_memory:
  continuity:
    packet_pointer: "specs/002-suppress-relic-sickness"
    last_updated_at: "2026-10-10T00:00:00Z"
    last_updated_by: "big-pickle"
    recent_action: "deployed and verified: Relic VFX/SFX gone from compiled tweakdb"
    next_safe_action: "confirm in game that no overlay or camera breathing appears"
    blockers:
      - "Phantom Liberty is not installed, so the q304_songbird_relic_shock half is compile-verified only"
      - "no in-game confirmation yet that the effect is gone at runtime"
    key_files:
      - "$PROJECT/src/no-relic-sickness/README.md"
      - "$PROJECT/src/no-relic-sickness/payload/base/gameplay/static_data/database/status_effect/johnny_sickness.tweak"
      - "$PROJECT/tools/sickness-tweak.py"
      - "$PROJECT/.opencode/specs/001-bypass-v-johnny-merge/findings/07-relic-sickness-progression.md"
    session_dedup:
      fingerprint: "sha256:9287db1d04302dca8e097c52b5eb4d57b3793480469da10c49193521fc403e92"
      session_id: "002-suppress-relic-sickness"
      parent_session_id: null
    completion_pct: 80
---
# Spec: Suppress Relic Sickness

<!-- SPECKIT_LEVEL: 1 -->
<!-- SPECKIT_TEMPLATE_SOURCE: spec-core | v2.2 -->

---

<!-- ANCHOR:metadata -->
## 1. METADATA

| Field | Value |
|-------|-------|
| **Level** | 1 |
| **Priority** | P2 |
| **Status** | In Progress |
| **Created** | 2026-10-10 |
| **Branch** | `feature/suppress-relic-sickness` |


<!-- /ANCHOR:metadata -->
---

<!-- ANCHOR:problem -->
## 2. PROBLEM & PURPOSE

### Problem Statement

With the Relic installed, V suffers the Relic sickness: a fullscreen glitch overlay, a camera that
breathes, fullscreen SFX, and a stamina-regeneration penalty of −2.5% to −15% depending on stage.
All of it comes from four TweakDB status-effect records,
`BaseStatusEffect.JohnnySickness{Low,Medium,Heavy}`, plus one Phantom Liberty record that inherits
the same base and redefines the payload itself.

A useful clarification, arrived at by reading the shipped TweakDB rather than assuming:
**vanilla cannot kill V with the Relic.** The countdown ladder
(5d → 3d → 2d12h → 2d → 1d12h → 1d) is entirely Nexus mod 25974's addition, keyed off the
`sickness_on` fact. What vanilla ships is presentation and a small stat penalty.

### Purpose

Remove the sickness effect while keeping the Relic, its storyline, its scenes and every quest call
site intact. Branched separately from spec 001 (`NoJohnnyReplacer`) because the two touch disjoint
files: 16 quest files there, two TweakDB sources here.


<!-- /ANCHOR:problem -->
---

<!-- ANCHOR:scope -->
## 3. SCOPE

### In Scope
- The `VFX[]` and `packages[]` payload of `JohnnySicknessLow`, `JohnnySicknessMedium`,
  `JohnnySicknessMediumQuest` and `JohnnySicknessHeavy`
- The `CameraAnimation` gameplay tag on `JohnnySicknessAbstract`
- `q304_songbird_relic_shock` in the Phantom Liberty tree, which inherits the same abstract
- Regenerating the override after a game patch, with a failing check rather than a silent one
- Install and uninstall that restore the shipped sources byte-for-byte

### Out of Scope
- The scripted beats: `sq032.quest` plays the sickness scene ten times and
  `sq032_sickness.questphase` once, so V still visibly glitches and hears voicesets. That is a
  quest-graph edit, not a TweakDB one
- Any death countdown. This patch does not touch `sickness_on`, so Nexus mod 25974 still kills V
  on schedule. The two are otherwise compatible — 25974 ships no TweakDB
- Johnny in any form (spec 001)
- Phantom Liberty's Relic *story*, only its one status-effect record


<!-- /ANCHOR:scope -->
---

<!-- ANCHOR:requirements -->
## 4. REQUIREMENTS

### Functional Requirements

- **FR-001**: The Relic sickness must produce no fullscreen overlay, no camera-breathing animation
  and no fullscreen SFX at any stage.
- **FR-002**: The stamina-regeneration penalty must not apply.
- **FR-003**: All affected TweakDB records must still exist, with their inheritance edges intact, so
  the 11 quest call sites continue to resolve. Removing a record is a failure, not a shortcut.
- **FR-004**: Helper records in the same files (`SFXEffector`, `JohnnySicknessUI`) must be carried
  through untouched, because `tech_new_perks.tweak` and `ep1 quest_custom.tweak` link against them.
- **FR-005**: Uninstall must restore the shipped sources byte-for-byte.
- **FR-006**: Nothing outside the game directory may be modified.

### Non-Functional Requirements

- No redscript, no CET, no TweakXL — REDmod's own deploy compiles TweakDB natively.
- Authorable without launching the game, like spec 001's Design A.
- The override must be regenerable from the shipped sources, not hand-maintained.

### Key Entities

| Entity | Role |
|---|---|
| `BaseStatusEffect.JohnnySicknessAbstract` | Shared base; carries the `CameraAnimation` tag |
| `BaseStatusEffect.JohnnySickness{Low,Medium,Heavy}` | The four records whose payload is emptied |
| `BaseStatusEffect.JohnnySicknessMediumQuest` | Inherits `Medium`; keeps its 5 s duration |
| `BaseStatusEffect.q304_songbird_relic_shock` | PL relic shock; inherits the abstract, redefines the payload |
| `BaseStatusEffect.SFXEffector`, `JohnnySicknessUI` | Helpers referenced from other files — must survive |
| `sq032_sickness.questphase`, `sq032.quest` | The 11 call sites that apply the effect. Untouched |


<!-- /ANCHOR:requirements -->
---

<!-- ANCHOR:success-criteria -->
## 5. SUCCESS CRITERIA

- **SC-001**: After `redMod.exe deploy`, the compiled `tweakdb.bin` contains zero occurrences of any
  `vfx_fullscreen_johnny_sickness_*` string, against a deploy made from unmodified sources where
  they are present. Confirmed: all ten tokens dropped to 0.
- **SC-002**: The four `JohnnySickness*` records still appear in the compiled database, so the 11
  call sites resolve. Confirmed: each collapses to its single declaration.
- **SC-003**: The camera-breathing references drop by exactly the number of records that referenced
  them — Low −1, Medium −2, Sick −1, Heavy 0 (never referenced by these records). Confirmed.
- **SC-004**: `uninstall.sh` restores both sources to their original md5 and the deployed database
  returns to vanilla. Confirmed.
- **SC-005**: In game, no overlay and no camera breathing occur at any Relic stage, and stamina
  regeneration is unaffected. **Not yet confirmed — needs a game launch.**
- **SC-006**: `sickness-tweak.py verify` fails on a pristine tree, on a dropped record, and on a
  changed parent. Confirmed with all three as controls.


<!-- /ANCHOR:success-criteria -->
---

<!-- ANCHOR:risks -->
## 6. RISKS & DEPENDENCIES

| Type | Item | Impact | Mitigation |
|------|------|--------|------------|
| Risk | **REDmod cannot override an existing TweakDB record** | The drop-in-`mods/` design does not exist; this must ship as a patch | Confirmed by deployment, not assumed. Hence `install.sh` |
| Risk | **`redMod.exe deploy` is a no-op with zero mods** | No recompile, no `r6/cache/modded/tweakdb.bin`, patch silently inert | A marker mod is installed alongside; `install.sh` runs the deploy itself |
| Risk | An effect record is defined in more than one file | A partial patch looks complete | `q304_songbird_relic_shock` was found exactly this way, by diffing the deployed database rather than trusting the first file |
| Risk | A removal rule silently matches nothing after a patch | Ships a no-op that reports success | `build` exits non-zero when an expected field or tag is absent |
| Risk | Dropping a helper record breaks unrelated records | `tech_new_perks.tweak` and ep1 `quest_custom.tweak` fail to compile | `verify` fails on any dropped record; the full-file rewrite is why the first attempt broke |
| Risk | Load order against another TweakDB mod | Last writer wins | Documented; nothing to do but say so |
| Risk | PL half is unverifiable here | `q304_songbird_relic_shock` is compile-verified only | Phantom Liberty is not installed on the development machine |
| Dependency | `wine` for `redMod.exe` | Deploy cannot run | Already required to play the game under Proton |
| Dependency | REDmod (Steam app 2060310) | Provides both the shipped tweak sources and the compiler | Installed |


<!-- /ANCHOR:risks -->
---

<!-- ANCHOR:questions -->
## 7. OPEN QUESTIONS

- Does the status effect still do anything observable now that its payload is empty — a buff icon,
  a gameplay tag match, a save-serialised entry? Unverified in game.
- Should the scripted beats also go? That is the quest-graph option the user declined; it is a
  coherent follow-up if the remaining V-glitch cutscenes prove irritating.
- Is a TweakXL-based build worth it for distribution? It would make this a true drop-in mod at the
  cost of a redscript dependency, which spec 001 explicitly avoids.


<!-- /ANCHOR:questions -->