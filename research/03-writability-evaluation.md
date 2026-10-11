# How to settle whether Redscript can write `gamedataPlayerPossesion`

Task T018. The answer decides Path A vs Path B. Four tests, cheapest first.

## What the offline evidence already says

### Evidence FOR script involvement

`questReplacer_NodeType` exists in WolvenKit's 15,830 generated RED4 class definitions:

```csharp
public partial class questReplacer_NodeType : questIGameManagerNonSignalStoppingNodeType
{
    CBool   enable;
    gameEntityReference objectRef;
    CName   audioOverrideAppearanceName;
}
```

This is a **quest node**. It is authored into a quest phase, and it has an `enable` flag. So the
game already drives replacer changes from quest data, and that data is editable. **This is a
candidate layer that does not depend on the setter existing at all** — flipping `enable = false`,
or repointing `objectRef`, may be the whole fix.

### Evidence AGAINST a script-callable setter

Searched `final.redscripts` for `Set*Possesion`, `Set*Replacer`, and any `Possesion*` suffix.
Result — only these five, none of which is a setter:

```
gamedataPlayerPossesion
GetPlayerPossesionRecord
OnLocalPlayerPossesionChanged
playerPossesion
PlayerPossesion_Record
```

### Why that is suggestive but NOT conclusive

I checked whether the string table is a complete list of script-callable natives. It is not:

| Name | Script-callable? | In table? |
| --- | --- | --- |
| `SetFact` / `GetFact` | yes | yes |
| `AddTarget` | yes | yes |
| `EntityExists` | yes | **no** |
| `AddStateModifier` | yes | **no** |
| `GetQuestFact` | yes | **no** |

**`final.redscripts` only contains names the base-game scripts reference.** A native that exists
but that no shipped script calls will not appear. So "no setter in the table" does not prove "no
setter exists". This invalidates the naive inference and is why the compile probe below is needed.

### Which classes are native vs TweakDB

WolvenKit's class definitions are generated from TweakDB. Checking what is and isn't there:

| Present in WolvenKit class defs (TweakDB/script side) | Absent (native/engine side) |
| --- | --- |
| `questReplacer_NodeType` | `gamedataPlayerPossesion` |
| `NotJohnnyReplacerPrereq`, `NotReplacerPrereq`, `NotVRReplacerPrereq` | `PlayerPossesion_Record` |
| `scannerDetailsGameController.PossessedByJohnnyFactListenerId` | `BaseStatusEffect.JohnnySickness*` |
| `DialogHubLogicController.PossessedDialogFluff` | the possession system class itself |

The possession system, its enum, its record and its status effects are all engine-side. That is
consistent with the setter being engine-only — but `questReplacer_NodeType` proves the engine
exposes *a* control path to quest data, which is enough to keep Path A alive.

---

## The tests

### Test 1 — Compile probe. Decisive, and does NOT need the game running.

Redscript is compiled ahead of launch, and the compiler typechecks method calls against the game's
native function database. Calling a native that does not exist is a **compile error**, not a
runtime one. So the question "does this setter exist?" is answerable statically.

Procedure:

1. Get a redscript compiler. It ships in **Cyberpunk 2077 REDmod** — Steam appid **2060310**, free
   DLC, requires owning Cyberpunk 2077 (appid 1091500). Not installed on this machine as of
   2026-10-04: `r6/` contains only `cache`, `config` and `publishing`, with no `red4ext/` and no
   `redscripts/`.
   **WolvenKit cannot substitute.** Current WolvenKit has no redscript decompilation or validation;
   the only repo-wide match for "redscript" is `WolvenKit/Helpers/RedscriptLanguage.cs`, which is
   syntax highlighting for the editor.
2. Drop a throwaway override in `r6/redscripts/`:
   ```
   // probe.reds
   @addMethod(PlayerPuppet)
   protected cb ProbeSetPossesion(CName v) {
       wrappedMethod(SetPlayerPossesion, v);
   }
   ```
3. Compile. `Unknown method` ⇒ the native does not exist ⇒ engine-only.
   Compiles ⇒ it exists ⇒ Path A is viable.

Probe every plausible spelling, because the game misspells this one:

- `SetPlayerPossesion` / `SetPlayerPossession`
- `SetLocalPlayerPossesion` / `SetLocalPlayerPossession`
- `SetPlayerPossessionRecord`

Also probe the known-good readers to confirm the compiler is actually validating:
`GetPlayerPossesionRecord`, `UsingJohnnyReplacer`.

**Cost:** needs .NET SDK install. **Game must not be running, but does not need to ever launch.**

### Test 2 — Find the quest node. Decisive, no game, needs unpacking. **DONE — negative result.**

Executed; see `04-quest-node-hunt-results.md`. `questReplacer_NodeType` is a braindance/NPC-spawn
node, absent from The Heist, and no quest node sets possession.

1. Unpack `basegame_3_nightcity.archive` / `basegame_4_gamedata.archive` with WolvenKit.
2. Search quest phases for `questReplacer_NodeType`.
3. Identify which quest and phase contains it.

If a quest node drives the merge, then Path A does **not** need a setter at all: set
`enable = false` on that node, or repoint `objectRef` away from `Character.johnny_replacer`.
This is the most promising path, because it acts on the game's own control point rather than
fighting the engine.

### Test 3 — Runtime method enumeration. Needs the game.

If Test 1 and 2 both come back negative, enumerate methods on the live possession-system object via
CET. Find the owner by hooking `OnLocalPlayerPossesionChanged` and reading its `this`. This gives
the definitive method list rather than inferring it from static data.

### Test 4 — Hook the setter. Needs the game, needs a setter to exist.

If Test 1 shows a setter exists but is engine-owned, hook it to refuse the `Johnny` value, or
re-force the state on `OnReplacerChanged` via the game's own `m_OnReplacerChangedCallback` hook.

---

## Recommendation

Run **Test 2 first**. It needs no compiler and no game, it targets the game's own control point,
and if it succeeds it makes Test 1 largely moot. Run Test 1 in parallel since the .NET SDK install
is independent and slow.

## Traps

- **Do not infer "engine-only" from the string table.** Proven wrong above: `EntityExists` and
  `AddStateMachine` are script-callable and absent.
- **Watch the spelling.** The game writes `Possesion` (one trailing `s`) in
  `gamedataPlayerPossesion`, `GetPlayerPossesionRecord`, `OnLocalPlayerPossesionChanged` and
  `playerPossesion`, but `JohnnyReplacer` and `IsJohnnyReplacer` are spelled correctly. A probe
  using the correct spelling will find nothing.
- **`Character.kurt_replacer` shares the mechanic.** Any fix scoped to "replacer" breaks Kurt's
  quest. Scope to Johnny explicitly.
- **`mq304` (Phantom Liberty) uses `JohnnyReplacerSequence`.** Most likely regression site.