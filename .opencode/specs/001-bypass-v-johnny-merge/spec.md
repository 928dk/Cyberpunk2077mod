---
title: "Spec: Bypass V-Johnny Merge [template:examples/level_1/spec.md]"
description: "required for the Cyberpunk 2077 Relic storyline merge bypass. Level 1 because the"
trigger_phrases:
  - "cyberpunk"
  - "merge"
  - "johnny"
  - "silverhand"
  - "relic"
  - "mod"
  - "bypass"
importance_tier: "normal"
contextType: "general"
_memory:
  continuity:
    packet_pointer: "specs/001-bypass-v-johnny-merge"
    last_updated_at: "2026-10-10T00:00:00Z"
    last_updated_by: "big-pickle"
    recent_action: "sickness facts mapped (07); scene-actor Johnny found (08); scope clarified"
    next_safe_action: "get T049 and T050 decided, then apply the Design A patch"
    blockers:
      - "enable=false is NOT confirmed honoured at runtime -- the keystone assumption of Design A (T042)"
      - "8 Tier-2 #bd_replacer files unresolved: the symbol is resolved by the braindance scene at load time, not by the quest file (T041)"
      - "whether ambient Johnny (johnny_default_on) survives Design A is unknown (T044)"
      - "whether staging breaks with an empty replacer slot is unknown, and now includes the Alt/Relic scenes (T043)"
      - "2022 baseline saves not yet confirmed loadable under current patch -- required for the first play test"
    key_files:
      - "$PROJECT/.opencode/specs/001-bypass-v-johnny-merge/findings/06-relic-vs-johnny-separation.md"
      - "$PROJECT/.opencode/specs/001-bypass-v-johnny-merge/findings/07-relic-sickness-progression.md"
      - "$PROJECT/.opencode/specs/001-bypass-v-johnny-merge/findings/08-johnny-scene-actor-scope.md"
      - "$PROJECT/.opencode/specs/001-bypass-v-johnny-merge/findings/05-redmod-metadata-answer.md"
      - "$PROJECT/.opencode/specs/001-bypass-v-johnny-merge/findings/04-quest-node-hunt-results.md"
      - "$PROJECT/tools/replacer-scope.py"
      - "$PROJECT/tools/scene-actor-scan.py"
      - "$PROJECT/docs/Rollback.md"
      - "$PROJECT/research/replacer-manifest.txt"
    session_dedup:
      fingerprint: "sha256:4d0542883f3184803dfba855135ca54bb2c0f2b9bce7dea853dae42cbe941fe0"
      session_id: "001-bypass-v-johnny-merge"
      parent_session_id: null
    completion_pct: 70
---
# Spec: Bypass V-Johnny Merge

<!-- SPECKIT_LEVEL: 1 -->
<!-- SPECKIT_TEMPLATE_SOURCE: spec-core | v2.2 -->

---

<!-- ANCHOR:metadata -->
## 1. METADATA

| Field | Value |
|-------|-------|
| **Level** | 1 |
| **Priority** | P1 |
| **Status** | In Progress |
| **Created** | 2026-10-03 |
| **Branch** | `001-bypass-v-johnny-merge` |


<!-- /ANCHOR:metadata -->
---

<!-- ANCHOR:problem -->
## 2. PROBLEM & PURPOSE

### Problem Statement
In Cyberpunk 2077's main Relic storyline, V and Johnny Silverhand are forced to merge, where
Johnny's engram overwrites V's personality. This is not a dialogue choice and cannot be declined.
Once merged, V's own identity is gone, which removes the point of playing the character as V.

### Purpose
Keep the Relic, remove the engram. The Relic is the story engine for Act 2, Phantom Liberty and all
four endings, so it must stay. Johnny is a passenger on it and that is what gets suppressed, so V
remains V while every district, side quest and Phantom Liberty stays reachable.

**Superseded framing (2026-10-04).** The original purpose was "prevent the merge at its trigger",
and an intermediate reading was "discard the Relic". Both were wrong about *where* the problem lives.
`findings/06` establishes the Relic and Johnny as separate systems joined at exactly one moment; the
intervention targets the engram, not the device.

### Chosen design: A — suppress the engram

| | |
| --- | --- |
| Mechanism | `questReplacer_NodeType.enable = false` on every `#johnny_replacer` node |
| Layer | Quest data override, loaded by REDmod |
| Scope | 27 nodes in 16 files |
| Cost | No CET, no redscript, no runtime hook, no game launch to author |
| Reversal | Delete the override directory |

Design C (author a replacement quest for Johnny's plot threads) is parked in
`~/projects/Client/Cyberpunk2077suppressJohnny/` as a future project.


<!-- /ANCHOR:problem -->
---

<!-- ANCHOR:scope -->
## 3. SCOPE

### In Scope
- The Relic storyline merge event and the code path that forces it
- Interventions at the modding layers: CET (Lua), Redscript, REDmod, TweakDB
- The alternate-resolution fallback, reusing the game's existing "Johnny disappears" scene block
  (`sb_johnny_disappear`) if blocking is not viable
- Verification that other areas, side quests and the open world remain reachable after the change

### Out of Scope
- Phantom Liberty (explicitly deferred by the user; must also not be broken by the change)
- Removing Johnny from non-merge contexts such as dialogue, his bar scene, or the-badge moments
- **Scene-actor Johnny.** Johnny reaches the screen two ways: the quest-graph replacer this spec
  disables, and `Character.Silverhand` as a `spawnDespawn` actor record in 195 scenes
  (`findings/08`). The second path is out of scope unless the user reopens it (T049). It is not a
  merge vector — it is a presentation layer — so it does not affect FR-001 or FR-002.
- **The Relic sickness.** With the Relic intact, V still gets sick and still dies on the Relic
  timer. Design A does not and is not intended to change that (`findings/07`). Suppressing it is a
  separate intervention (T050).
- Editing the base game archives directly beyond what REDmod/WolvenKit loading requires
- Console-quality assets, new voice acting, or writing an entirely new quest from scratch


<!-- /ANCHOR:scope -->
---

<!-- ANCHOR:requirements -->
## 4. REQUIREMENTS

### Functional Requirements

- **FR-001**: The mod must prevent V and Johnny from merging during the Relic storyline.
- **FR-002**: After the change, V must remain the player's own character, not a merged composite.
- **FR-003**: Districts, side quests, gigs and the open world must remain reachable after the change.
- **FR-004**: The Relic arc must not softlock. If a phase is skipped, the next available quest must
  still be issued by the quest system.
- **FR-005**: The mod must be reversible — removing it and reloading a save must restore vanilla
  behaviour with no archive repair.
- **FR-006**: The change must be expressible in a modding layer (CET / Redscript / REDmod / TweakDB),
  not as an irreversible base-game binary edit.

### Non-Functional Requirements

- **NFR-001**: Prototype iteration must not require unpacking and repacking the full game archives.
  CET hot-reload is the preferred prototyping surface for this reason.
- **NFR-002**: The mod must not degrade performance or frame rate measurably.
- **NFR-003**: Every intervention point must be recorded with file path and identifier so it can be
  reverted or re-applied after a game patch.

### Key Entities

| Entity | Identifiers |
|--------|-------------|
| **The possession state** | enum `gamedataPlayerPossesion` = `{ Default: 0, Johnny: 1, Count: 2, Invalid: 3 }`; record `gamedataPlayerPossesion_Record`; getter `gamedataTweakDBInterface.GetPlayerPossesionRecord` (**no setter exists**); event `OnLocalPlayerPossesionChanged` |
| **The possession data node** | `questSetPossesion_NodeType` (parent `questISceneManagerNodeType`), single property `playerPossesion`. Used in 5 phases: q115 (`Johnny`), q203 (`Default`), q204 (`Johnny`), sq031 (`Johnny` ×3) |
| **Replacer predicates** | `UsingJohnnyReplacer;StateGameScriptInterface`, `IsPlayingAsReplacer;StateGameScriptInterface`, `IsJohnnyReplacer` |
| **Replacer records** | `Character.johnny_replacer`, `Character.kurt_replacer`, `Character.q000_vr_replacer` |
| **Change hook (game's own)** | `m_OnReplacerChangedCallback`, `OnReplacerChanged` |
| **Merge symptoms** | `BaseStatusEffect.JohnnySicknessLow/Medium/Heavy/MediumQuest`, `IsJohnnySicknessBreathingEffectActive;PlayerPuppet` |
| **Supporting state** | `isPlayerPossessedByJohnny`, `GetPossessedByJohnnyFactName`, `GetPlayAsJohnnyFactName`, `SetWasEverJohnny`, `m_usingJhonnyReplacer` |
| **Existing prereqs to gate on** | `NotJohnnyReplacerPrereq`, `NotReplacerPrereq` |
| **Gameplay gating** | `EvaluateApplyingReplacerGameplayRestrictions;`, `GameplayRestriction.BlockAllHubMenu`, `GameplayRestriction.BlockFastTravel`, `JohnnyReplacerSequence` |
| The Heist | quest `q005_heist`, path `quests/main_quest/prologue/q005_heist`; facts `q005_johnny_chip_acquired`, `q005_lie_relic` |
| Tapeworm | quest `sq032_tapeworm`, path `quests/side_quest/sq032_tapeworm` |
| Johnny disappearance | fact `q302_06_johnny_disappear` |
| Johnny disappear scene | scene block `sb_johnny_disappear` (.prefab / .scenesolution / .scnlocjson) |
| Johnny as spawnable NPC | `Character.Silverhand`, appearance `silverhand_default` |


<!-- /ANCHOR:requirements -->
---

<!-- ANCHOR:success-criteria -->
## 5. SUCCESS CRITERIA

- **SC-001**: Loading the baseline save `ManualSave-5`, running The Heist, and continuing the Relic
  arc produces no merge. V's identity is intact at every point in the arc.
- **SC-002**: After reaching the end of the Relic arc on a modded save, all six districts are
  traversable and the side-quest journal is intact.
- **SC-003**: At least one side gig and one NCPD/cyberpsycho activity complete successfully on a
  modded save, proving the open world is not gated behind the merge.
- **SC-004**: Removing the mod folder and loading the same save restores vanilla progression with
  no crash and no repair prompt.
- **SC-005**: If Path A proves impossible, a documented Path B produces a scripted outcome where
  Johnny is removed from the story and V survives, without softlocking the Relic arc.


<!-- /ANCHOR:success-criteria -->
---

<!-- ANCHOR:risks -->
## 6. RISKS & DEPENDENCIES

| Type | Item | Impact | Mitigation |
|------|------|--------|------------|
| Risk | **`enable = false` is not honoured at runtime for this node type** | **THE keystone assumption.** It is a populated serialised field and the node system has a first-class disableable concept, but nothing has confirmed the engine reads it | Test on the baseline save before writing anything else. If it fails, fall back to the fact-based pattern CDPR already ships in `q105` |
| Risk | Conflating the **ending merge** with the **progressive takeover** | Would ship a "fix" that changes the ending while leaving the actual problem untouched | The two are tracked as separate problems throughout. Only the takeover is what the user asked for |
| Risk | **A blanket "disable all replacer nodes" edit** | The replacer is shared with Kurt's quest, V's VR intro, two PL bosses and a shopping-mall NPC | Three-tier classification is enforced in `tools/replacer-scope.py`; tier 3 files never written; `verify` fails if any leak |
| Risk | **The 18 `#bd_replacer` nodes are assumed to be generic braindance actors** | The symbol is resolved by the braindance scene at load time; if any is Johnny, it escapes suppression | Held as tier 2 rather than guessed. Seven files unresolved (T041) |
| Risk | **Discarding the Relic instead of the engram** | Would delete Act 2, Phantom Liberty and all endings | Rejected in favour of Design A. `ep1_relic_intro_button` shows PL runs its own Relic intro |
| Risk | Blocking the merge phase may strand the Relic arc with no next quest issued | Relic arc softlock | Always verify quest issuance after the intervention, not just the absence of the merge |
| Risk | Johnny's engram drives plot-critical UI (the mirror, the phone, the chip messages) | Removing him may break scenes that assume his presence | Treat `sb_johnny_disappear` and the existing Johnny-removal facts as the reference implementation |
| Risk | Possession is set by a fact whose **name is computed at runtime** in C++ | The trigger cannot be pre-empted by clearing a known fact name, which was the original assumption | If Path A is pursued, hook the engine function instead of trying to clear a fact |
| Risk | Baseline saves are from Oct 2022 and may not load under the current game version | Testing blocked | Verify save load first; fall back to the Oct 2026 playthrough with a fresh pre-Heist save if needed |
| Dependency | Game archives are not unpacked on this machine | Quest-level analysis blocked | WolvenKit can unpack the Steam install on demand |
| Dependency | CET / Redscript / REDmod not yet installed in the game | No prototype possible | Install before writing mod code |
| Dependency | Exact merge trigger not yet identified | All downstream work is speculative | Fact-diff `ManualSave-5` vs `ManualSave-6` is the next action |


<!-- /ANCHOR:risks -->
---

<!-- ANCHOR:questions -->
## 7. OPEN QUESTIONS

**Three answered 2026-10-04.** See `findings/02`, `04` and `05`.

- ~~Does the merge happen at a single scripted moment, or progressively?~~ **Two mechanisms, not
  one.** The *ending* merge is a single quest data node. The *progressive takeover* during the Relic
  arc is a separate engine-side system.
- ~~Is the trigger reachable from quest data?~~ **Partly.** `questReplacer_NodeType` (the obvious
  candidate) is braindance-only. But `questSetPossesion_NodeType` is the real data path.
- ~~Can Redscript write the possession state?~~ **No. Settled.** Across all 11,246 classes, 657
  global functions and 1,233 enums in REDmod's reflection database, exactly one possession method
  exists and it is a **getter**: `gamedataTweakDBInterface.GetPlayerPossesionRecord`. No setter, no
  global function. Redscript is a dead end; the lever is quest **data** or a runtime **hook**.

### The two mechanisms

| | Ending merge | Progressive takeover |
| --- | --- | --- |
| What | V permanently becomes Johnny | Johnny progressively overwrites V across the Relic arc |
| Where | `questSetPossesion_NodeType` (5 sites: q115, q203, q204, sq031) | Engine-side; not any quest node |
| Editable | **Yes** — flip `playerPossesion` to `Default` | **Not as data.** Only via CET runtime hook or symptom suppression |
| Effort | Trivial, reversible | Substantive |

The user's request is the **second** one. The first is a five-minute data edit that happens not to be
the one asked for.

Still open:

- **Which native function sets possession at runtime?** Not script-visible, so it must be found by
  CET runtime inspection (T019a). This is now the critical unknown.
- **What drives the progressive takeover?** Candidates: the `JohnnySickness` status effects
  (`Low`/`Medium`/`Heavy`/`MediumQuest`), the Johnny quest sequences in q101/q105/q108/q112/q113, and
  the chip percentage. None identified as the cause.
- **What breaks if possession never flips?** `EvaluateApplyingReplacerGameplayRestrictions` and
  `GameplayRestriction.BlockAllHubMenu` / `BlockFastTravel` imply gameplay is gated on it. This is
  the biggest risk in the project: prevention may be counterproductive.
- **Does V survive the Relic arc without Johnny?** `JohnnySilverhandAltApp` exists as a parallel
  content path, which suggests the game has a V-first variant worth studying.
- **How do we handle Kurt?** `Character.kurt_replacer` uses the same mechanic.
- **Are the 2022 baseline saves loadable under the current patch?**

<!-- /ANCHOR:questions -->

---

<!--
CORE TEMPLATE (~80 lines)
- Essential what/why/how only
-->