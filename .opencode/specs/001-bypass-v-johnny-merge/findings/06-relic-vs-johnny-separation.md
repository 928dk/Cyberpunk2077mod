# The Relic and Johnny are separate systems. Keep the Relic, drop the engram. (2026-10-04)

The user reframed the project mid-session: *"stop the start of Johnny taking over = discarding the
relic, and make another storyline."* That framing is wrong in one specific and important way, and
this document records why, plus the mechanism that replaced it.

## The Relic is the content. Johnny is the passenger.

| | The Relic | Johnny |
| --- | --- | --- |
| What it is | A device: perk trees, level, access to content | An engram riding it |
| Data | `RelicPerkSystem`, `RelicTree_Meleeware_*`, `Relic_Up`, `RelicGoldenNumbers`, `isRelicMilestone`, `SetLastRelicLevel` | `Character.johnny_replacer`, `johnny_default_on`, `q105_replacer_disabled` |
| Introduced by | `base_relic_intro_button` — a **scene**, not a quest node | `questReplacer_NodeType` — the **quest graph** |

They are welded together at exactly one moment, the Relic intro, and nowhere else.

**Discarding the Relic would delete most of the game.** The Relic is the story engine for
everything after Act 1 — Takemura's job, Hanako, Arasaka Tower, Mr. Hands, and all four endings.
Worse, `ep1_relic_intro_button` is a *separate* trigger, so Phantom Liberty runs its own Relic
intro. A Relic-less path would very likely break PL, which is explicitly out of scope and must not
break.

The requirement is not "discard the Relic". It is "keep the Relic, load no engram".

## Design A: disable the Johnny replacer nodes

`questReplacer_NodeType`, from REDmod's `metadata.json`:

```csharp
questReplacer_NodeType : questIGameManagerNonSignalStoppingNodeType   // size 128
{
    Bool enable;                          // <-- the entire mod
    gameEntityReference   objectRef;
    CName                 audioOverrideAppearanceName;
}
```

**One serialised Bool per node.** Set `enable = false` and the braindance plays without Johnny. No
CET, no redscript, no facts, no runtime hook, and no game launch to author it. Pure CR2W quest data,
overridable by WolvenKit/REDmod, and reversible by deleting the override.

`enable` is a real populated field, not vestigial — 39 of the 49 shipped nodes have it set. And the
node system has a first-class "disableable" concept: `questFactsDBManagerNodeDefinition`'s parent is
literally `questDisableableNodeDefinition`.

*Unverified:* that the engine honours `enable` at runtime for this node type. Only a game launch
settles it. This is the single largest remaining assumption in the project.

## The game already contains this pattern

`q105_judys_braindance.questphase` — Johnny's **first** appearance ("Disasterpiece") — ships a
CDPR-authored kill switch:

```
questFactsDBManagerNodeDefinition
  └ questSetVar_NodeType { factName: "q105_replacer_disabled", value: 1 }
questConditionNodeDefinition
  └ questFactsDBCondition
      └ questVarComparison_ConditionType { comparisonType: "Greater",
                                          factName: "q105_replacer_disabled", value: 0 }
```

CDPR set a fact and branched on it to decide whether to run the replacer. That is direct evidence the
replacer is fact-gated data rather than engine-hardcoded, and it is the shape this mod imitates —
except Design A uses the simpler mechanism (`enable = false`) instead of a fact round-trip.

## Scope: three tiers, because the replacer is shared

Walking all 27 quest files that contain `questReplacer_NodeType` yields **49 nodes**. They are not
all Johnny, and a blanket edit would break unrelated content.

| Tier | Ref | Nodes | Files | Action |
| --- | --- | --- | --- | --- |
| **1** | `#johnny_replacer` | 28 (27 enabled) | 16 | **disable** |
| **2** | `#bd_replacer` | 18 | 8 | **hold** — needs scene check |
| **3** | other | 2 | 2 | **never touch** |

### Tier 1 — confirmed Johnny

`q101_j_01..j_05` (Playing for Time), `q108_01..06a + riots` (Never Fade Away),
`q116_cyberspace` (Changes), `q204_02_corridor` (New Dawn Fades).

### Tier 2 — ambiguous, deliberately held

`#bd_replacer` is a **symbolic braindance slot**, not a named TweakDB record:

```json
"objectRef": { "$type": "gameEntityReference",
               "reference": { "$type": "NodeRef", "$value": "#bd_replacer" },
               "type": "EntityRef" }
```

The actor is resolved by the braindance scene at load time, so the quest file cannot say who it is.
Affects `q004` (braindance tutorial), `q105_blackmarket`, `sq012`, `sq021`.

Only `q105_judys_braindance` is confirmed Johnny, because `q105_replacer_disabled` gates exactly
that node. The other seven files could be Johnny or could be a recorded NPC; guessing would risk
silently deleting an NPC from a braindance. **Held until the braindance scenes are resolved.**

### Tier 3 — must not be touched

| File | Ref | Why |
| --- | --- | --- |
| `q110_demo_playstyle_selection` | `#q110_com_mall_v_solo_female_replacer` | A shopping-mall NPC, not Johnny |
| `mq060_yaiba_showroom` | `#mq060_communityArea` / `android_replacer` | Android display in the Yaiba showroom |

Also excluded from all tiers: any path under `test/` or `profiling/`. `q101_hammer_club_concert.quest`
carries a Johnny replacer but is developer profiling scaffolding and must never ship.

## The other Johnny layers — Design A does not cover them

- **Ambient presence.** `johnny_default_on` / `johnny_off` control Johnny's mirror, phone and bar
  scenes. Set by `sq032_finale.questphase` (Tapeworm). Disabling replacer nodes likely does not touch
  this. **Untested.**
- **Ending merge.** `questSetPossesion_NodeType` in q115 / q203 / q204 / sq031. Under Design A this
  becomes *optional* — V never becomes Johnny because Johnny was never there — rather than
  load-bearing.
- **Chip percentage / `JohnnySickness`.** **ANSWERED 2026-10-10** — see `07-relic-sickness-progression.md`.
  Not moot. The sickness is `sickness_on` + `sq032_tapeworm_stage` (story stage 1-6) +
  `sq032_sickness_stage` (affliction stage) + a status effect on the player
  (`BaseStatusEffect.JohnnySickness{Low,Medium,Heavy}`) applied by `sq032_00_sickness.scene`. No
  replacer, no possession, no Johnny required. Design A therefore does not weaken it: V still gets
  sick and still dies on the Relic.
- **Scene-actor Johnny.** `Character.Silverhand` is referenced by **195 scenes** as a
  `spawnDespawn` actor record — a second, replacer-free way Johnny reaches the screen. See
  `08-johnny-scene-actor-scope.md`. Design A does not touch it.

## Note on `NotJohnnyReplacerPrereq`

`NotJohnnyReplacerPrereq`, `NotReplacerPrereq` and `NotVRReplacerPrereq` exist and looked like a
single global TweakDB lever — the "one edit instead of 27" candidate. **Not needed.** The `enable`
Bool is simpler, is per-node so it can be scoped exactly, and needs no prereq-graph archaeology.
No call site was ever located, so this route remains untested and now unnecessary.

## The quest map, for future reference

Derived from the modkit's `journal-quest-data` (416 quests, 65 base-game):

| Quest | Title | Role |
| --- | --- | --- |
| q005 | The Heist | Chip. **No Johnny yet.** |
| q101 | Playing for Time | Braindances — 8 Johnny replacers |
| q105 | Automatic Love | **Johnny's first appearance** (`q105_judys_braindance`) |
| q108 | Never Fade Away | 13 Johnny replacers |
| q112 | Play It Safe | Hanako, parade, safe house, implantation |
| q113–q116 | | Arasaka Tower, Changes, braindances |
| q204 | New Dawn Fades | Ending — replacer + possession |
| q300–q307 | Phantom Liberty | **Has its own Relic intro** |

## What remains unverified

1. **Does `enable = false` actually suppress the replacer at runtime?** Everything rests on this.
2. **Do the Tier-2 braindances break without their replacer actor?** Some braindance staging may be
   directed at the actor, in which case disabling empties or breaks the scene rather than
   cleanly removing Johnny.
3. **Does ambient Johnny (`johnny_default_on`) persist after Design A?** If so it is a follow-up.
4. **Does the Relic intro scene itself hard-require Johnny to be loadable?** — **PARTLY ANSWERED
   2026-10-10.** `q110_13_alt_intro.scene` and `q116_05_mikoshi.scene` each spawn Johnny **twice**:
   once as `Character.Silverhand` and once as a `johnny_replacer` actor bound to `#johnny_replacer`.
   `q115_03a_alt.scene` binds its `johnny` actor to `#johnny_replacer` only. So the Alt/Relic scenes
   do reference Johnny, through both mechanisms. Whether the scene *breaks* is T043. See
   `08-johnny-scene-actor-scope.md`.