---
title: "Tasks: Bypass V-Johnny Merge [template:examples/level_1/tasks.md]"
description: "needed to locate the merge trigger and implement the bypass. Phase 1 is investigation"
trigger_phrases:
  - "tasks"
  - "cyberpunk"
  - "merge"
  - "johnny"
  - "bypass"
importance_tier: "normal"
contextType: "general"
_memory:
  continuity:
    packet_pointer: "specs/001-bypass-v-johnny-merge"
    last_updated_at: "2026-10-10T00:00:00Z"
    last_updated_by: "big-pickle"
    recent_action: "Nexus mod 25974 mapped; sickness facts (07), scene-actor Johnny (08)"
    next_safe_action: "get T049 and T050 decided, then apply the Design A patch"
    blockers:
      - "T049/T050 — scope and sickness-outcome decisions belong to the user, not derivable from the data"
      - "Tier 2 #bd_replacer (8 files) unresolved — symbol resolved by braindance scene, not the quest file"
      - "T006-T008 and T042 require the game to be running"
    key_files:
      - "$PROJECT/.opencode/specs/001-bypass-v-johnny-merge/plan.md"
      - "$PROJECT/.opencode/specs/001-bypass-v-johnny-merge/findings/01-savegame-survey.md"
      - "$PROJECT/.opencode/specs/001-bypass-v-johnny-merge/findings/06-relic-vs-johnny-separation.md"
      - "$PROJECT/.opencode/specs/001-bypass-v-johnny-merge/findings/07-relic-sickness-progression.md"
      - "$PROJECT/.opencode/specs/001-bypass-v-johnny-merge/findings/08-johnny-scene-actor-scope.md"
      - "$PROJECT/tools/scene-actor-scan.py"
    session_dedup:
      fingerprint: "sha256:2155813426844864c4947559018c4570aad6f32b524aa6ecd2dc595c0c325801"
      session_id: "001-bypass-v-johnny-merge"
      parent_session_id: null
    completion_pct: 72
---
# Tasks: Bypass V-Johnny Merge

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

- [x] T001 Create spec folder with spec/plan/tasks (`001-bypass-v-johnny-merge/`)
- [x] T002 Survey the cloned tooling repos (`findings/00-repo-scan.md`)
- [x] T003 Identify quest IDs and scene assets (`findings/trigger-research.md`)
- [x] T004 Survey all savegames and pick a pre-merge baseline (`findings/01-savegame-survey.md`)
- [x] T005 Scaffold the working project from the project template (`mod-prototype/`, since promoted to the repo root)
- [ ] T006 Confirm `ManualSave-5` loads in-game without a repair prompt
- [ ] T007 Take a timestamped backup of `ManualSave-5` before any test run
- [ ] T008 Confirm the baseline run: The Heist completes and the merge occurs (gate G2)
- [ ] T009 Install CET, Redscript and REDmod into the game install — **partly satisfiable by T019**:
      REDmod (appid 2060310) ships all three. Blocked on user installing the DLC
- [ ] T010 [P] Unpack game archives with WolvenKit (`~/projects/Cyberpunk-tooling/WolvenKit`)


<!-- /ANCHOR:phase-1 -->
---

<!-- ANCHOR:phase-2 -->
## Phase 2: Implementation

### Locate the merge trigger

- [x] T011 Diff the fact store between `ManualSave-5` and `ManualSave-6` — **superseded**. The trigger
      was found faster by scanning the compiled game data, which needs no save editing at all
- [x] T012 Inspect `q005_heist` quest phases for the merge code path — **done via `final.redscripts`**.
      Merge is not in a quest phase; it is the `gamedataPlayerPossesion` player state
      (`findings/02-merge-mechanic.md`)
- [x] T013 Search for the merge state in TweakDB and redscripts — **done**. Found the enum, the
      `Johnny` value, `PlayerPossesion_Record`, `OnLocalPlayerPossesionChanged`, `UsingJohnnyReplacer`,
      `IsPlayingAsReplacer`, `OnReplacerChanged`, and the four `JohnnySickness` tiers
- [x] T014 Write a re-runnable symbol scanner so this analysis survives game patches
      (`tools/merge-symbol-scan.py`)
- [x] T015 Record the intervention candidates now that the trigger is known
      (`findings/03-writability-evaluation.md`)
- [ ] T016 Trace what *sets* possession to `Johnny` — find the caller of `OnLocalPlayerPossesionChanged`
- [ ] T017 [P] Search existing mods for a Johnny-removal pattern to reuse
- [x] T018 **Find which quest phase contains `questReplacer_NodeType`** — **DONE, negative result.**
      Found in 26 phases, all braindances or NPC spawns. `q005_heist` has zero possession/replacer
      refs. No possession quest node exists. Merge is engine-side and fact-driven
      (`findings/04-quest-node-hunt-results.md`)
- [x] T019 **Determine whether Redscript can WRITE `gamedataPlayerPossesion`** — **ANSWERED: NO.**
      REDmod's `metadata.json` is the compiler's own reflection DB (11,246 classes / 657 global
      functions). Only one possession method exists game-wide and it is a getter,
      `gamedataTweakDBInterface.GetPlayerPossesionRecord`. No setter exists
      (`findings/05-redmod-metadata-answer.md`)
- [x] T019b **Locate the data path that sets possession.** `questSetPossesion_NodeType` carries a
      single `gamedataPlayerPossesion playerPossesion` property, used in 5 phases (q115, q203, q204,
      sq031). Enum is `{ Default: 0, Johnny: 1 }`. Editable as quest data — see T022
- [x] T019a Runtime enumeration is **unnecessary for the write question** — `metadata.json` gave the
      complete method list statically. Still needed to find the *hookable* native that SETS
      possession at runtime, the only remaining lever for the progressive takeover
- [ ] T020 Check what `EvaluateApplyingReplacerGameplayRestrictions` gates, since holding possession
      at V may *remove* access rather than preserve it
- [ ] T021 Check whether `Character.kurt_replacer` shares the path, so the fix does not break Kurt's quest
- [ ] T022 [P] **Flip `questSetPossesion_NodeType.playerPossesion` to `Default`** in
      `q115_03_afterlife`, `q204_00_setup` and `sq031` — 5 sites all set `Johnny`; `q203_penthouse`
      already uses `Default`, proving the game flips this itself. Prevents "V permanently becomes
      Johnny at the ending". Cheap, reversible data edit. Does NOT stop the progressive takeover
      (`findings/05-redmod-metadata-answer.md`)

### Design A — suppress Johnny, keep the Relic

Selected 2026-10-04 over "discard the Relic": the Relic is the story engine for Act 2, Phantom
Liberty and all four endings (`ep1_relic_intro_button` proves PL runs its own Relic intro), so
discarding it deletes most of the game. Johnny is the engram, not the device.

- [x] T023 Write the rollback procedure before making any change — **DONE**, `docs/Rollback.md`.
      Override-directory only, so uninstall is `rm -rf`. Mod writes no facts and no save state, so
      one save works with and without it
- [x] T038 Discover the mechanism: `questReplacer_NodeType.enable` is a serialised `Bool`. Disabling
      the node stops the braindance spawning Johnny. No CET, no redscript, no runtime hook
- [x] T039 Scope all 49 replacer nodes across 27 files into three tiers — **DONE**, see below
- [x] T040 Build `tools/replacer-scope.py` with manifest/patch/verify modes — **DONE**, compiles and
      round-trips clean
- [ ] T041 **Resolve the 8 Tier-2 `#bd_replacer` files.** The symbol is resolved by the braindance
      scene at load time, not by the quest file, so the quest data cannot say who fills it. Only
      `q105_judys_braindance` is confirmed Johnny (CDPR's `q105_replacer_disabled` gates exactly
      that node). Hold the other 7 until checked
- [ ] T042 Verify `enable = false` is honoured at runtime — **the project's keystone assumption.**
      Everything rests on it and only a game launch settles it
- [ ] T043 Check whether braindance staging breaks with an empty replacer slot — **SCOPE WIDENED
      2026-10-10 (T048).** `q110_13_alt_intro.scene` and `q116_05_mikoshi.scene` also bind actors to
      `#johnny_replacer`, and `q116_cyberspace.questphase` carries two Tier-1 nodes Design A will
      disable. This is now about the Alt/Relic scenes, not only braindances
- [ ] T044 Check whether ambient Johnny (`johnny_default_on`) survives Design A

### Findings from an external mod (2026-10-10)

Triggered by the user supplying Nexus mod **25974** (*The Downward Spiral — Relic Sickness Death
Timer*), downloaded to `$PROJECT/archives/` and extracted. Reverse-engineered rather than installed.

- [x] T047 Map the vanilla Relic-sickness progression and the mod's death timer over it
      (`findings/07-relic-sickness-progression.md`). Facts: `sickness_on`, `sq032_tapeworm_stage`
      (story stage 1-6, advanced at q104/q105/q110/q112), `sq032_sickness_stage` (affliction stage),
      status effects `BaseStatusEffect.JohnnySickness{Low,Medium,Heavy}` applied to the player.
      No replacer, no possession. **Closes the open question in finding 06**
- [x] T048 Determine whether Johnny reaches the screen outside the replacer
      (`findings/08-johnny-scene-actor-scope.md`). **YES** — `Character.Silverhand` is a
      `spawnDespawn` actor record in 195 scenes; 12 more bind an actor to `#johnny_replacer`. Built
      `tools/scene-actor-scan.py` with a `verify` self-check, and
      `research/scene-actor-manifest.txt` as the per-file baseline. Note the trap: CR2W stores
      TweakDBIDs as hashes, so `grep 'Character.Silverhand'` returns 0 over the same corpus
- [ ] T049 **Decide the Johnny scope**: replacer layer only (design A as written, scene-actor Johnny
      documented as a limitation) / also strip scene actors (~195 scenes) / stage it. Blocks final
      scope and the wording of the README
- [x] T050 **Decide the sickness outcome** — **DECIDED 2026-10-10: suppress the VFX and stamina
      penalty, keep the Relic itself.** Delivered on branch `feature/suppress-relic-sickness` under
      its own spec, `002-suppress-relic-sickness`. Two TweakDB sources, six records; the scripted
      beats were declined for that branch. Note for whoever picks this up: vanilla **cannot kill V**
      with the Relic — the 5d→1d ladder is Nexus mod 25974's addition, keyed off `sickness_on`
- [ ] T051 Record mod 25974's conflict surface — it overrides `sq032_00_sickness.scene`,
      `q115_death.questphase`, `q115_solo_lobby.questphase` and `epilogue/final_boards.questphase`.
      The last is the ending/merge file finding 06 already flags. Feeds T046
- [ ] T052 Give T042 a runtime observable: read `sq032_tapeworm_stage` / `sq032_sickness_stage` in
      game to confirm quest state independently of the replacer. Today T042 has no way to be
      checked but by eye

### Ship and verify Design A

- [ ] T045 Apply to `mods/NoJohnnyReplacer` and confirm REDmod loads it
- [ ] T046 Confirm no other mod edits the same quest phases (last-wins conflict risk)
- [x] T024 Choose the intervention layer — **CHOSEN: quest data override via REDmod.** Rejected CET
      (needs the game running to iterate, opaque), redscript (no setter exists, finding 05), direct
      archive edit (irreversible, violates FR-006)
- [ ] T025 Implement the smallest viable intervention (`src/`)
- [ ] T026 Add a config flag so the mod can be toggled without deletion
- [ ] T027 Verify the mod loads clean: CET log and redscript compile output both free of errors
- [ ] T028 Run gate G4: merge does not occur on `ManualSave-5`


<!-- /ANCHOR:phase-2 -->
---

<!-- ANCHOR:phase-3 -->
## Phase 3: Verification

- [ ] T029 Run gate G5: all districts traversable on the modded save
- [ ] T030 Complete one side gig on the modded save
- [ ] T031 Complete one NCPD/cyberpsycho activity on the modded save
- [ ] T032 Run gate G6: confirm the next Relic quest is still issued (no softlock)
- [ ] T033 Run gate G7: remove the mod, reload, confirm vanilla behaviour restored
- [ ] T034 Confirm Phantom Liberty is unaffected — note `mq304` uses `JohnnyReplacerSequence`, so PL is
      the most likely place for a regression
- [ ] T035 Record actual test results, including any failures, in `findings/test-results.md`
- [ ] T036 Package as a REDmod modlet with install instructions (`docs/INSTALL.md`)
- [ ] T037 Write `implementation-summary.md` with what worked, what failed, and the patch-fragility notes


<!-- /ANCHOR:phase-3 -->
---

<!-- ANCHOR:completion -->
## Completion Criteria

- [ ] All tasks marked `[x]`
- [ ] No `[B]` blocked tasks remaining
- [ ] Gates G1-G7 all pass, with evidence recorded
- [ ] SC-001 through SC-005 satisfied, or SC-005 documented as the fallback outcome
- [ ] Rollback verified on a real save, not just asserted


<!-- /ANCHOR:completion -->
---

<!-- ANCHOR:cross-refs -->
## Cross-References

- **Specification**: See `spec.md`
- **Plan**: See `plan.md`
- **Savegame survey**: See `findings/01-savegame-survey.md`
- **Trigger research**: See `findings/trigger-research.md`
- **Relic vs Johnny separation (the architectural result)**: See `findings/06-relic-vs-johnny-separation.md`
- **Relic sickness progression + Nexus mod 25974**: See `findings/07-relic-sickness-progression.md`
- **Scene-actor Johnny (replacer-free path)**: See `findings/08-johnny-scene-actor-scope.md`
- **Working project**: `~/projects/Client/Cyberpunk2077mod/`

<!-- /ANCHOR:cross-refs -->