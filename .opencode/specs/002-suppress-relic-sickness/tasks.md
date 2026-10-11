---
title: "Tasks: Suppress Relic Sickness [template:examples/level_1/tasks.md]"
description: "T001-T029. Everything except the in-game check is done and verified against the"
trigger_phrases:
  - "tasks"
  - "relic"
  - "sickness"
  - "tweakdb"
importance_tier: "normal"
contextType: "general"
_memory:
  continuity:
    packet_pointer: "specs/002-suppress-relic-sickness"
    last_updated_at: "2026-10-10T00:00:00Z"
    last_updated_by: "big-pickle"
    recent_action: "branch complete; only the in-game check remains"
    next_safe_action: "load a Relic-stage save and confirm no overlay"
    blockers:
      - "Phantom Liberty not installed: q304_songbird_relic_shock is compile-verified only"
      - "T022-T025 need the game running"
    key_files:
      - "$PROJECT/.opencode/specs/002-suppress-relic-sickness/spec.md"
      - "$PROJECT/.opencode/specs/002-suppress-relic-sickness/plan.md"
      - "$PROJECT/src/no-relic-sickness/README.md"
    session_dedup:
      fingerprint: "sha256:9c1d4f0a7b2e6835d41c9a7e0b5f83d2c6a19e47fb0d3851c7a2e9b64f10d8a3"
      session_id: "002-suppress-relic-sickness"
      parent_session_id: null
    completion_pct: 92
---
# Tasks: Suppress Relic Sickness

<!-- SPECKIT_LEVEL: 1 -->
<!-- SPECKIT_TEMPLATE_SOURCE: tasks-core | v2.2 -->

---

<!-- ANCHOR:notation -->
## Task Notation

| Prefix | Meaning |
|--------|---------|
| `[ ]` | Pending |
| `[x]` | Completed |
| `[P]` | Parallelizable |
| `[B]` | Blocked |

**Task Format**: `T### [P?] Description (file path)`


<!-- /ANCHOR:notation -->
---

<!-- ANCHOR:phase-1 -->
## Phase 1: Setup

- [x] T001 Read the shipped `johnny_sickness.tweak` and establish what the four records actually
      carry — VFX, breathing animation, SFX, stamina modifier, nothing else
- [x] T002 Establish that vanilla cannot kill V with the Relic, and that the 5d→1d ladder is
      Nexus mod 25974's addition keyed off `sickness_on`
- [x] T003 Count the quest call sites: ten scene nodes in `sq032.quest` plus one in
      `sq032_sickness.questphase`
- [x] T004 [P] Open a branch per direction so this never touches `master` or spec 001


<!-- /ANCHOR:phase-1 -->
---

<!-- ANCHOR:phase-2 -->
## Phase 2: Implementation

### Probe the deployment route

- [x] T005 Run `redMod.exe` under wine and confirm TweakDB compilation is a native deploy stage, so
      no TweakXL and no redscript are needed
- [x] T006 Confirm a mod needs an `info.json`, and that `tweaks/` is discovered automatically
- [x] T007 **NEGATIVE:** attempt the override as a mod. Result: `Duplicated group
      'JohnnySicknessLow' in package 'BaseStatusEffect'`. REDmod cannot override an existing
      TweakDB record — the patch has to go onto the shipped sources
- [x] T008 Discover that `redMod.exe deploy` is a no-op with zero mods deployed, and add a marker
      mod so the recompile happens at all

### Generate and gate

- [x] T009 Write `tools/sickness-tweak.py` with `build` (regenerate + diff) and `verify` (invariants)
- [x] T010 **BUG caught by the gate:** the first version emitted only the five targeted records and
      dropped `SFXEffector` and `JohnnySicknessUI`. Compilation failed on `tech_new_perks.tweak`
      and ep1 `quest_custom.tweak`, which link to them. The generator now carries every record
      through verbatim
- [x] T011 **BUG caught by the gate:** the `package`/`using` prologue was emitted twice. Header is
      now comments only and the prologue comes from vanilla
- [x] T012 Make every rule fail loudly — a missing field, tag, record or parent is an error, never a
      silent pass
- [x] T013 Negative controls: pristine-as-override fails, dropped record fails, changed parent fails

### Package

- [x] T014 `install.sh` — back up, patch, install marker mod, run the deploy, surface stderr on
      failure
- [x] T015 `uninstall.sh` — restore from backup, remove marker mod, recompile; refuse to guess if the
      backup is missing
- [x] T016 `src/no-relic-sickness/README.md`, including why this is a patch and not a drop-in mod
- [x] T017 Keep `.backup/` and deploy logs out of git


<!-- /ANCHOR:phase-2 -->
---

<!-- ANCHOR:phase-3 -->
## Phase 3: Verification

### Against the compiled database

- [x] T018 Deploy from unmodified sources as a **control** — necessary because the first check
      looked like a pass but was vacuous: the payload tokens are absent from the `.str` form either
      way
- [x] T019 Deploy patched and diff the compiled binaries. All ten `vfx_fullscreen_johnny_sickness_*`
      tokens drop to 0; `CameraBreathing` references drop by exactly the number of records that
      referenced them (Low −1, Medium −2, Sick −1, Heavy 0); all four records survive
- [x] T020 **Gap found by the diff:** `q304_songbird_relic_shock` in the Phantom Liberty tree inherits
      `JohnnySicknessAbstract` but redefines the whole payload itself. Stripping only the first file
      left it fully intact. Generator now handles both files; six records across two files
- [x] T021 Confirm the tool's determinism: a deploy with sources unmodified by accident reproduced
      the vanilla output exactly (delta 0 everywhere)
- [x] T022 Round-trip test: install → uninstall restores both files to their original md5 and the
      Relic VFX tokens return to the compiled database

### In game

- [ ] T023 Load a save at `sq032_tapeworm_stage` ≥ 3 and let a sickness beat trigger. Confirm: no
      fullscreen overlay, no camera breathing, no fullscreen SFX
- [ ] T024 Confirm stamina regeneration is unaffected at a heavy stage
- [ ] T025 Confirm the scripted beats still play (V glitching on screen) — they should, this patch
      does not touch them
- [ ] T026 Confirm nothing regressed in the Relic arc itself, and that the 11 call sites did not
      error

### Follow-ups, not in this branch

- [ ] T027 Decide whether the scripted sickness beats are worth removing too. Quest-graph edit, and
      the user declined it for this branch
- [ ] T028 If distribution matters more than staying redscript-free, rebuild on TweakXL so this
      becomes a true drop-in mod
- [ ] T029 Re-run `sickness-tweak.py build --diff` after the next game patch and review the diff


<!-- /ANCHOR:phase-3 -->
---

<!-- ANCHOR:completion -->
## Completion Criteria

- [x] Every Relic VFX/SFX token is absent from the compiled database, proven against a vanilla deploy
- [x] All six records survive with inheritance intact, so all 11 quest call sites still resolve
- [x] The negative controls fail correctly, so the pass means something
- [x] `uninstall.sh` restores the shipped sources byte-for-byte
- [ ] Confirmed in game (T023–T026)


<!-- /ANCHOR:completion -->
---

<!-- ANCHOR:cross-refs -->
## Cross-References

- **Specification**: See `spec.md`
- **Plan**: See `plan.md`
- **Evidence**: `../001-bypass-v-johnny-merge/findings/07-relic-sickness-progression.md`
- **Mod**: `src/no-relic-sickness/README.md`
- **Sibling direction**: `feature/scene-actor-johnny` (spec 001, task T049) touches ~195 `.scene`
  files and never collides with this one


<!-- /ANCHOR:cross-refs -->