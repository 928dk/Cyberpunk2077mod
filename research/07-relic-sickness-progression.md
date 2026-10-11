# T047: the Relic sickness is facts + a scene + a status effect. It does not need Johnny. (2026-10-10)

Triggered by the user supplying Nexus mod **25974**, *The Downward Spiral — Relic Sickness Death
Timer (On Borrowed Time)*, downloaded to `$PROJECT/archives/` and extracted. The mod is a working
implementation of a Relic-sickness death timer, so it is a readable answer to a question this project
had already written down as unanswered.

## The open question it answers

`findings/06-relic-vs-johnny-separation.md` listed, under "The other Johnny layers":

> **Chip percentage / `JohnnySickness`.** Driver still unidentified. Possibly moot if Johnny never
> loads.

It is **not moot**. The sickness subsystem is independent of the replacer subsystem, and this mod
names every part of it. Corrected line is in finding 06.

## What the mod ships

One archive plus its load manifest:

```
archive/pc/mod/the_downward_spiral.archive
archive/pc/mod/the_downward_spiral.archive.xl
```

Version 3.1.3. Five CR2W resources inside — four overrides of vanilla files and one new phase:

| Resource | Kind |
| --- | --- |
| `mod/the_downward_spiral/quest/phases/tds_sickness_loop.questphase` | **new** — the entire mod |
| `base/quest/side_quests/sq032/scenes/sq032_00_sickness.scene` | override |
| `base/quest/main_quests/part1/q115/phases/q115_death.questphase` | override |
| `base/quest/main_quests/part1/q115/phases/q115_solo_lobby.questphase` | override |
| `base/quest/main_quests/epilogue/final_boards.questphase` | override |

Across all five: **0 `questReplacer_NodeType`, 0 `possesion` references.** It is a facts-and-timers
mod, nothing else.

## The vanilla sickness architecture

Extracted and serialised from `$GAME_DIR/archive/pc/content/basegame_4_gamedata.archive`.

### Stage counters

| Fact | Written by | Read by | Meaning |
| --- | --- | --- | --- |
| `sq032_tapeworm_stage` | `sq032_tapeworm_setup.questphase` (`ADD 1` ×4) and `sq032.questphase` (`SET 2`) | `sq032_episode_3/4/5/6.questphase` (`GreaterOrEqual 3/4/5/6`), `sq032_sickness.questphase` | **Story stage 1–6.** Advanced at the four Relic gates `q104` / `q105` / `q110` / `q112`. |
| `sq032_sickness_stage` | **no base-game quest writes it** | `sq032_00_sickness.scene` (9×: `LessOrEqual 2`, `Equal 3`, `Equal 4`, `Equal 5`, `Equal 6`) | **Affliction stage.** A CDPR fact, advanced outside quest data. |
| `sickness_on` | `sq032_sickness.questphase` (`SET 1`) | `sq032_sickness.questphase`, the scene | Master switch |
| `sq032_sickness_{glitch,headache,heavy_headache,nausea,nosebleed,echo,warning}` | the scene itself (6 `questSetVar_NodeType`) | `sq032_sickness.questphase` | Symptom variants |

`sq032_sickness.questphase` is 6 nodes: an input, two pause conditions, one scene node, one fact
write, one phase node. It gates on `sq032_tapeworm_stage Greater 0`, sets `sickness_on = 1`, and
plays `sq032_00_sickness.scene`.

### What the scene actually does

`sq032_00_sickness.scene` (`base/quest/side_quests/sq032/scenes/`):

- 37 pause conditions, 26 `questCharacterManagerNodeDefinition`, 26 `questPlayVoiceset_NodeType`,
  13 game managers, 10 conditions.
- **26** `questCharacterManagerParameters_SetStatusEffect` nodes applying
  `BaseStatusEffect.JohnnySickness{Low,Medium,Heavy}`. Each has `isPlayer = 1` — the affliction is
  applied to **the player**. The `questRecordSelector` names `Character.Silverhand`, which reads as
  the lore *source* of the affliction rather than its target. *(Interpretation, not proven.)*
- Actor `Johnny`, `acquisitionPlan = spawnDespawn`,
  `spawnDespawnParams.specRecordId = Character.Silverhand`. See finding 08.
- Symptom flags are set and cleared *inside* the scene, which is how the same scene renders
  different variants.

**The sickness is a status effect on V plus a scene. It is not a replacer, it is not possession, and
it does not require Johnny to be loaded.**

## How the mod uses it

`tds_sickness_loop.questphase`, 55 nodes: 19 pause conditions, 15 conditions, 7 fact writes, 5
randomizers, 3 hubs, 2 game managers, 2 phase calls, 1 input, 1 scene.

The loop:

1. wait until `sickness_on Greater 0`
2. seed `sq032_sickness_stage` from `sq032_tapeworm_stage` (`Equal 1/2/3/4/5`, `GreaterOrEqual 6`)
3. set stage to 1..5, wait, increment, while `sq032_sickness_stage Less 6`
4. at `GreaterOrEqual 6`, call `q115_death.questphase` and `final_boards.questphase` — **it routes
   death through vanilla machinery**
5. play `sq032_00_sickness.scene`, branched per stage and per symptom

The countdown ladder it installs, in game time:

```
5d -> 3d -> 2d12h -> 2d -> 1d12h -> 1d, then death
```

Two `questGameplayRestrictions_NodeType` nodes gate gameplay during an attack.

### Two techniques worth stealing

**Game time, not real time.** `q115_death.questphase` is overridden to replace
**152 `questRealtimeDelay_ConditionType`** with **74 `questGameTimeDelay_ConditionType`**. Real-time
delays keep running in menus; game-time delays only advance when the world clock does. Verified by
node-type count diff against the vanilla file — the only large structural change the mod makes.

**Facts, not conditions, for endings.** `final_boards.questphase` gains exactly 3
`questVarComparison_ConditionType` + 3 `questFactsDBCondition`; `q115_solo_lobby` gains 2. Small,
targeted, no new systems.

### The hook: phase attachment, not override

The `.xl` attaches `tds_sickness_loop.questphase` as a child phase of:

```
cyberpunk2077.quest
ep1\quest\cyberpunk2077_ep1_standalone.quest
mod\quest\newgameplus.quest
mod\quest\newgameplus_q001.quest
mod\quest\newgameplus_standalone.quest
```

i.e. a new phase bolted onto the root quest **without editing it**. That is a third implementation
route for this project and it is cheaper than a 16-file override.

**It cannot perform Design A.** A new phase can set facts; it cannot flip a `Bool` inside an
existing vanilla node. Disabling the replacer nodes still requires overriding those files. Recorded
so this is not re-investigated.

*(Phantom Liberty is not installed on the analysis machine — no `ep1` archive, only an
`ep1.addcont_keystone` marker — so the ep1 parent is inert locally and unverified in play.)*

## What this changes for spec 001

1. **Confirms and sharpens finding 06.** The Relic and the sickness are facts, a scene and a status
   effect. Johnny is the replacer layer. They touch at the Relic intro and nowhere else. Disabling
   the replacer does not weaken the Relic.
2. **Design A keeps the Relic lethal.** V still gets sick and still dies on the Relic timer, because
   nothing in Design A touches `sickness_on`, `sq032_sickness_stage` or `sq032_tapeworm_stage`. If
   "V stays V" is meant to include "V survives", that is a *separate* facts-based patch and the
   facts are now known. **The spec does not currently say which outcome is wanted — see T049.**
3. **`sq032_tapeworm_stage` is a runtime verification lever.** T042 (does `enable = false` work?)
   currently has no observable. Reading `sq032_tapeworm_stage` and `sq032_sickness_stage` at runtime
   gives one, and is independent of the replacer.
4. **Conflict surface.** Mod 25974 overrides `sq032_00_sickness.scene` and `final_boards.questphase`.
   `final_boards` is the ending/merge file finding 06 already flags. If a player installs both, the
   last-loaded mod wins. See T046.

## Reproducing

```bash
export PATH="$DOTNET:$PATH"
WK=$TOOLING/WolvenKit/WolvenKit.CLI

# the mod's own questphase
dotnet run --project "$WK" -c Release --no-build -- \
  extract "$PROJECT/archives/.../the_downward_spiral.archive" -o "$SCRATCH/tds"
dotnet run --project "$WK" -c Release --no-build -- \
  convert serialize "$SCRATCH/tds/mod/the_downward_spiral/quest/phases/tds_sickness_loop.questphase"

# the vanilla sickness quest + scene
dotnet run --project "$WK" -c Release --no-build -- \
  extract "$GAME_DIR/archive/pc/content/basegame_4_gamedata.archive" -o "$SCRATCH/sq032" \
  -r "sq032.*\.(questphase|quest)$"
dotnet run --project "$WK" -c Release --no-build -- \
  extract "$GAME_DIR/archive/pc/content/basegame_4_gamedata.archive" -o "$SCRATCH/vanilla-scene" \
  -r "sq032_00_sickness\.scene$"
```

## What is still unknown

- **Who writes `sq032_sickness_stage` in vanilla.** Every `.quest` and `.questphase` in
  `basegame_4_gamedata` was scanned (3,496 files) and none sets it. It is read by the vanilla scene,
  so it must be written outside quest data — engine, TweakDB, or Phantom Liberty (not installed here,
  so not checked). Consequence: the mod is, in vanilla terms, the writer.
- **Whether mod 25974 has been play-tested against the current patch.** Its four overrides are
  surgical, but a quest-graph override is patch-fragile in the same way Design A is.
- **Whether 195 scene references (finding 08) is the real count of scenes that render Johnny.** Only
  sampled, not enumerated per scene.