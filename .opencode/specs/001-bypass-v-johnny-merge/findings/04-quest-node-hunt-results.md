# Result of T018 (quest node hunt) and T019 status (2026-10-04)

Both offline tests attempted. T018 produced a firm **negative** result. T019 is blocked on tooling.

## What was done

- Installed .NET SDK 10.0.401 to `~/.dotnet` (user-local, no sudo). WolvenKit's `global.json` pins
  10.0.302 with `rollForward: latestFeature`, so 10.0.401 satisfies it.
- Built `WolvenKit.CLI` (Release, 0 errors, 394 warnings).
- Extracted **1,354 quest files** (`.questphase` / `.quest`) from `basegame_4_gamedata.archive`.
- Enumerated **221 distinct quest node types** across the corpus.
- Serialised individual phases to JSON with `convert serialize` to read node structures properly.

## T018: `questReplacer_NodeType` is NOT the merge

`questReplacer_NodeType` appears in **26 quest phases**, but reading the nodes shows it is a
**braindance / NPC-spawn node**, not a possession control:

```json
{
  "$type": "questReplacer_NodeType",
  "enable": 1,
  "audioOverrideAppearanceName": "None",
  "objectRef": { "names": ["johnny"], "reference": "#johnny_replacer" }
}
```

In `q116_cyberspace.questphase` it appears alongside `questSpawnSet_NodeType` actions
(`action: "Reactivate"`, `entryName: "johnny"`) and `questCharacterSpawned_ConditionType` checks —
i.e. it spawns Johnny as a scene actor. The 26 phases are almost entirely braindances
(`q101_j_*`, `q004_*`, `q105_*`, `q108_*`) plus `mq060_yaiba_showroom`.

**It is absent from The Heist entirely.**

### The Heist does not trigger the merge

`q005_heist.questphase` contains **zero** references to possession, replacer, Johnny, Silverhand or
engram. One incidental `chip` string. The merge is not in the Heist.

### No possession quest node exists

Of the 221 node types, the only replacer/possession candidates are
`questReplacer_NodeType` (braindance, ruled out) and `questGameplayRestrictions_NodeType` (269 uses,
which matches `EvaluateApplyingReplacerGameplayRestrictions`). **There is no quest node that sets
player possession.**

### What the merge actually is, then

Not quest-node driven. The corpus does contain:

| Name | Where | What it is |
| --- | --- | --- |
| `johnny_sickness_lvl1`, `lvl2`, `lvl3` | `q113_10_jungle.questphase` | Used as `effectName` in `questPlayFX_NodeType` with `isPlayer` — **visual FX**, not state |
| `sq031_johnny_assumed_control` | `sq031_afterlife.questphase` | A `questCheckpointNodeDefinition.debugString` — a **checkpoint label**, not a fact |

`sq031` is **"Chippin' In"**, the Akira side-quest ending where Johnny takes the Relic. That is a
real possession event, but it is opt-in and late, not the main Relic merge.

Critically, the fact that drives possession is **not hardcoded in any quest**. It is resolved at
runtime by the native `GetPossessedByJohnnyFactName`, whose implementation is in the executable.
That is why the quest corpus contains no candidate fact name — the engine computes it.

**Conclusion: the merge is engine-side and fact-driven, with the fact name computed in C++ and not
present in any editable game data.** This is a materially harder target than the plan assumed.

## T019: blocked

The compile probe needs a **redscript compiler**. WolvenKit cannot help: the current version has no
redscript decompilation or validation — only syntax highlighting
(`WolvenKit/Helpers/RedscriptLanguage.cs` is the only match repo-wide).

The compiler ships in **Cyberpunk 2077 REDmod** — Steam appid **2060310**, `type: dlc`,
`is_free: true`, requires owning Cyberpunk 2077 (appid 1091500). Verified against the Steam store
API, not from memory.

> **Correction.** An earlier revision of this document claimed the modkit was appid **2694490**.
> That is wrong — 2694490 is **Path of Exile 2**. The correct id is **2060310**, and the product was
> rebranded from "Cyberpunk Modkit" to "Cyberpunk 2077 REDmod". The id was asserted without being
> looked up, and it was the user who caught it, not me.

**REDmod is not installed on this machine.** `~/.../Cyberpunk 2077/r6/` contains only `cache`,
`config` and `publishing` — no `red4ext/`, no `redscripts/`. There is no `appmanifest_2060310.acf`,
while `appmanifest_1091500.acf` (the base game) is present.

So the probe needs the user to install it from Steam: Library -> Cyberpunk 2077 -> DLC ->
Cyberpunk 2077 REDmod -> Install. It cannot be done unattended: `steamcmd` neither authenticates nor
fetches DLC for a title the account does not own.

### Options

1. **You install the Cyberpunk Modkit** via Steam, then I run the probe. Cleanest and authoritative.
2. **Skip the static probe** and go straight to a runtime CET enumeration of the possession
   system's methods. Needs the game running, but gives the definitive method list instead of
   inferring it.
3. **Treat T018's negative result as sufficient** and move to Path B, since the trigger now looks
   engine-only.

## Revised assessment

The plan's fallback (Path B) is now the more likely path. Evidence that Path A is hard:

- Possession is set by engine code, not quest data.
- The driving fact's name is computed in C++ and is not in any file we can edit.
- The possession system class, its enum, its record and its status effects are all absent from
  WolvenKit's 15,830 TweakDB class definitions.
- Only the *read* side is script-visible (`UsingJohnnyReplacer`, `IsPlayingAsReplacer`,
  `GetPlayerPossesionRecord`).

This does not rule out Path A — CET can hook native functions directly, bypassing the redscript
layer entirely. But it does mean the intervention is a runtime hook, not a data edit.

## Reusable setup left behind

```
~/.dotnet/                                  # .NET 10.0.401, user-local
~/projects/Cyberpunk-tooling/WolvenKit/WolvenKit.CLI/   # built, Release
```

Build command:

```bash
export PATH="$HOME/.dotnet:$PATH"
dotnet build WolvenKit.CLI/WolvenKit.CLI.csproj -c Release
```

Extract quests (1,354 files, ~4 min):

```bash
dotnet run --project WolvenKit.CLI/WolvenKit.CLI.csproj -c Release --no-build -- \
  extract "<game>/archive/pc/content/basegame_4_gamedata.archive" -o <out> \
  -r "quests.*\.(questphase|quest)$" -v Minimal
```

Read one phase properly (this is the step that mattered — raw binary greps give misleading
node attribution because type names live in a lookup table at the head of the file):

```bash
dotnet run --project WolvenKit.CLI/WolvenKit.CLI.csproj -c Release --no-build -- \
  convert serialize <file>.questphase -v Quiet
```

## Traps hit

- **`.tweakdb` source files do not exist in the archive.** `extract -r "\.tweakdb$"` matched 0 of
  56,574 entries. The TweakDB ships only compiled, as `r6/cache/tweakdb.bin`, which hashes its
  record names. So TweakDB record-level queries are not available offline without WolvenKit's
  in-memory TweakDB reader.
- **Quest node type names are a lookup table, not inline.** Grepping the raw binary and attributing
  the nearest preceding node name gives wrong answers — every node type string sits in a block at
  the start of the file. Serialise to JSON first.
- **Name matching is not evidence.** `questReplacer_NodeType` matched on name and looked exactly
  like a possession control. It is a braindance spawner. Reading the node was the only way to know.
- **WolvenKit is 3.5 GB+ of sources and needs .NET 10**, not 9. Installing 9 first was wasted motion.