# T048: Johnny reaches the screen by TWO mechanisms. The replacer is only one of them. (2026-10-10)

Found while reverse-engineering Nexus mod 25974 (see finding 07), which shipped an unmodified copy of
a vanilla Relic-sickness scene. That scene puts Johnny on screen with **zero replacer nodes**.

## The claim

| Mechanism | Where it lives | Reached by | Count in base game |
| --- | --- | --- | --- |
| **A — replacer** | quest graph, `questReplacer_NodeType` | `#johnny_replacer` NodeRef | 28 nodes / 16 quest files (finding 06) |
| **B — scene actor** | `.scene` resource, `scnActorDef` | `Character.Silverhand` TweakDB record | **195 scenes** |
| A+B — both | `.scene` resource, `acquisitionPlan = spawnSet` | actor named `johnny_replacer`, bound to NodeRef `#johnny_replacer` | **12 scenes** |
| A as a record | `.scene` resource | `Character.johnny_replacer` TweakDB record | 26 scenes (5× q101, 19× q108, 2× q116) |

Design A disables mechanism A. **Mechanism B is untouched by it.**

## Evidence

`sq032_00_sickness.scene`, the Relic-sickness scene, actor list:

```
actor "Johnny"   acquisitionPlan=spawnDespawn   spawnDespawnParams.specRecordId=Character.Silverhand
```

Its replacer-reference count is **0**. Same shape in three more quest scenes, all serialised and
checked:

| Scene | Actor bound to `Character.Silverhand` | Also names `#johnny_replacer` |
| --- | --- | --- |
| `sq032_00_sickness.scene` | `Johnny`, spawnDespawn | no |
| `johnny_default.scene` | `Johnny`, spawnDespawn | no |
| `sq031_05_grave.scene` | `Johnny`, spawnDespawn | no |
| `sq023_07_restaurant.scene` | `Johnny`, spawnDespawn | no |
| `q110_13_alt_intro.scene` | `Johnny`, spawnDespawn | **yes** (actor `johnny_replacer`, spawnSet) |
| `q116_05_mikoshi.scene` | `Johnny`, spawnDespawn | **yes** |
| `q115_03a_alt.scene` | — (`johnny`, spawnSet, record 0) | **yes** |

The full per-file listing is `research/scene-actor-manifest.txt`.

## The measurement trap — worth its own note

CR2W stores a TweakDBID as a **64-bit hash, not a string**:

```
TweakDBID(name) = crc32(name) | (len(name) << 32)
Character.Silverhand -> 0x000000140044e64c
```

So this, run over 2,642 extracted scenes:

```bash
grep -rl 'Character.Silverhand' .          # 0 hits. Correct answer: 195.
```

WolvenKit only resolves the hash back to the name when it serialises against TweakDB, which is why
the record is visible in a `.scene.json` and invisible in the `.scene`. The first pass of this
analysis "proved" that no scene referenced Silverhand, and that conclusion was wrong. A wrong result
that comes out clean is worse than an error.

`tools/scene-actor-scan.py` scans for the hash instead, and its `verify` subcommand is the
self-check — it resolves the records out of a serialised JSON and confirms each hash is present in
the matching binary:

```bash
$ python3 tools/scene-actor-scan.py verify "$SCRATCH/scenes" \
      "$SCRATCH/scenes/base/quest/side_quests/sq032/scenes/sq032_00_sickness.scene.json"
scene            : sq032_00_sickness.scene
TweakDBID records: 6
  BaseStatusEffect.JohnnySicknessHeavy         0x00000024f823d80e  FOUND
  BaseStatusEffect.JohnnySicknessLow           0x000000221ecc53b5  FOUND
  BaseStatusEffect.JohnnySicknessMedium        0x00000025da9d3677  FOUND
  Character.AldecaldosFemale                   0x0000001a1bb289cd  FOUND
  Character.Player_Puppet_Base                 0x0000001c15982adf  FOUND
  Character.Silverhand                         0x000000140044e64c  FOUND
OK    every record resolves: the hash scan is sound for this file
```

Run `verify` before trusting any count taken after a game patch.

## Why this matters now: the Relic-adjacent scenes use mechanism A

`q110_13_alt_intro.scene`, `q115_03a_alt.scene` and `q116_05_mikoshi.scene` all bind actors to
`#johnny_replacer` — and two of the three *also* spawn `Character.Silverhand` directly. Two
consequences:

1. **T043 is wider than "braindance staging".** It asked whether braindance staging breaks when the
   replacer slot is empty. It now also covers the Alt/Relic scenes. `q116_cyberspace.questphase`
   carries **two Tier-1 nodes** that Design A will disable, and `q116_05_mikoshi.scene` binds actors
   to the slot those nodes control.
2. **A scene actor bound to `#johnny_replacer` is the replacer *entity*.** Disabling the node removes
   the appearance swap; it does not obviously remove the actor. Whether the staging still reads as
   "Johnny is standing there" with a default body is exactly T043.

## What this does **not** prove

- **195 is a reference count, not a spawn count.** A TweakDBID hit means the scene names the
  *character record*; the same record is also the selector used by
  `questCharacterManagerParameters_SetStatusEffect`. `vset_johnny.scene` and several loading screens
  and marketing GIFs reference Silverhand without rendering him. Four quest scenes were serialised
  and confirmed as spawns; the other 191 were not individually checked.
- **This does not show the mod is broken.** Mechanism B may be a bug rather than a design, and CDPR
  may already gate those scenes on something else.
- **It does not change the tiering.** `#johnny_replacer` → disable, `#bd_replacer` → hold, all else →
  never touch. That classification is unaffected.

## The scope question this raises — T049

Finding 06 and the spec both describe Design A as removing Johnny from the Relic storyline. On the
evidence above, Design A removes the **body-swap** Johnny and leaves the **scene-actor** Johnny.
Those are different outcomes and the user has not chosen between them. Recorded as a decision, not
resolved here.

Options, for whoever picks it up:

| Option | Work | Result |
| --- | --- | --- |
| A — replacer layer only | as scoped today | body-swap Johnny gone; Johnny still appears in scenes. Limitation documented. |
| B — also strip scene actors | edit or redirect ~195 scenes, or blank `Character.Silverhand` centrally | Johnny gone everywhere. Much larger, far more patch-fragile. |
| C — staged | ship A, then open a follow-up spec for B | A verified in game before committing to B |

## Reproducing

```bash
export PATH="$DOTNET:$PATH"
WK=$TOOLING/WolvenKit/WolvenKit.CLI

dotnet run --project "$WK" -c Release --no-build -- \
  extract "$GAME_DIR/archive/pc/content/basegame_4_gamedata.archive" \
  -o "$SCRATCH/scenes" -r "\.scene$"          # 7,067 entries, 2,642 after dropping /versions/

python3 tools/scene-actor-scan.py scan "$SCRATCH/scenes" \
  --manifest research/scene-actor-manifest.txt
```

`/versions/` holds historical patch copies (`patch0`, `patch1_2` … `gold`). Excluding them is
default: including them double-counts and reports the same scene many times.