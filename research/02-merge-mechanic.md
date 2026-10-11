# The merge mechanic is script-visible (2026-10-04)

Investigated **without launching the game**, by reading the compiled game data shipped in the
install. This answers the plan's biggest open question.

## Source data used

| File | Size | What it is |
| --- | --- | --- |
| `~/.../Cyberpunk 2077/r6/cache/final.redscripts` | 16 MB | Compiled Redscript bytecode. String table is plaintext, so function names, TweakDB record names and argument names are all readable. |
| `~/.../Cyberpunk 2077/r6/cache/tweakdb.bin` | 42 MB | Optimized TweakDB. Record *names* are hashed, but loc strings are plaintext. |
| `~/.../Cyberpunk 2077/bin/x64/cyberpunk2077_addresses.json` | 132 MB | Linker map of `Cyberpunk2077.exe`. 987,479 entries, but **only 83 carry a symbol name** — the rest are hash-only. Dead end for name lookup. |
| `CyberpunkSaveEditor/assets/CFacts.json` | 19,428 lines | The game's fact-name registry. |

Paths under `~/projects/Client/Cyberpunk2077mod/` are the research repos; the paths above are the
Steam install at `~/.local/share/Steam/steamapps/common/Cyberpunk 2077/`.

## The core mechanism: `PlayerPossesion`

The merge is not a narrative flag. It is a **player possession state**.

```
gamedataPlayerPossesion        <- TweakDB enum, has a value named `Johnny`
GetPlayerPossesionRecord       -> PlayerPossesion_Record
OnLocalPlayerPossesionChanged  |playerPossesion|uiSystem
```

All four strings appear in the Redscript string table. `gamedataPlayerPossesion` is listed
immediately alongside `gamedataConsumableType`, `gamedataTraitType` and `gamedataCrowdTrait` — i.e.
it is an ordinary gameplay enum, not internal plumbing.

**Consequence:** when the merge happens, the game flips the player's possession from V to Johnny.
That is the trigger, and it is script-visible.

## Script-callable predicates

```
UsingJohnnyReplacer;StateGameScriptInterface
IsPlayingAsReplacer;StateGameScriptInterface
```

These are callable from Redscript. So quest logic can already ask "is the player playing as the
Johnny replacer?" — the game provides the predicate.

## The replacer character record

```
Character.johnny_replacer      <- confirmed present in BOTH final.redscripts and tweakdb.bin
Character.kurt_replacer        <- also exists
```

`kurt_replacer` matters: "replacer" is a **general game mechanic**, not a one-off for Johnny.
Kurt is a replacer in the Badlands/DLC content. Any intervention has to account for that, or it
will break Kurt's quest too.

## The merge symptoms are status effects

```
BaseStatusEffect.JohnnySicknessLow
BaseStatusEffect.JohnnySicknessMedium
BaseStatusEffect.JohnnySicknessHeavy
BaseStatusEffect.JohnnySicknessMediumQuest
IsJohnnySicknessBreathingEffectActive;PlayerPuppet
```

Four escalating severity tiers plus a quest-specific variant. The breathing effect is what the
player sees. These are ordinary status effects, which means they are suppressible.

## Supporting state

| Symbol | Meaning |
| --- | --- |
| `isPlayerPossessedByJohnny` | GameSessionData variable |
| `m_possessedByJohnnyFactListenerId` | fact listener already wired to the possession state |
| `GetPossessedByJohnnyFactName;` | returns the fact name |
| `GetPlayAsJohnnyFactName;` | returns the fact name |
| `SetWasEverJohnny;GameObjectBool` | sticky "was ever Johnny" flag |
| `m_usingJhonnyReplacer` | PlayerCombatController blackboard field (note: the game misspells it "Jhonny") |
| `m_OnReplacerChangedCallback`, `OnReplacerChanged` | change callback already exists |
| `EvaluateApplyingReplacerGameplayRestrictions;` | with args `mainObj`, `controlledObj` |
| `NotJohnnyReplacerPrereq`, `NotReplacerPrereq` | prereqs that gate on *not* being the replacer |
| `Possessed`, `isPossessed`, `PossessedDialog` | the dialogue UI treatment |

Two of these are the strongest leads: **`m_OnReplacerChangedCallback` / `OnReplacerChanged`** is the
hook the game itself uses, and **`NotJohnnyReplacerPrereq`** proves the game already has machinery
for "content that must not run while Johnny is in control".

## The Heist facts

From `CFacts.json`, all 92 `q005_*` facts, notable ones:

```
q005_johnny_chip_acquired     <- the chip is acquired at the END of The Heist
q005_lie_relic
q005_done
q005_start
```

`CheckJohnnyFact` sits in the attribute menu code next to `q005_johnny_chip_acquired` — the
"Escalation"-style attribute unlock is keyed off that fact.

## Correction: there are no `q006` facts

`CFacts.json` has zero entries for `q006`. The quest after The Heist therefore does not use the
`qNNN_factname` naming convention, or its facts live under a different prefix. Anyone assuming
"the merge happens in q006" is guessing. The merge is **not** in a quest's fact namespace — it is
in `PlayerPossesion`.

## What this answers

**Open question from `plan.md`: "Is the merge enforced in compiled engine code with no script hook?"**

Answer: **Partly no.** The possession state, its change event, its predicates and its symptoms are
all script-visible. That does *not* prove the state is script-*writable* — the engine may only
expose a setter internally. That remains the open question.

## What remains open

1. **Is `PlayerPossesion` writable from Redscript?** Readable is proven; writable is not. This is
   the make-or-break question for Path A.
2. **What sets it?** A quest node in The Heist, or an engine tick? Need the caller.
3. **Does V survive without Johnny?** Lore and the Johnny-alt-app progression suggest some Relic
   functions may hard-require him. `JohnnySilverhandAltApp` exists as a parallel content path.
4. **What breaks if possession never flips?** `EvaluateApplyingReplacerGameplayRestrictions`
   implies gameplay is gated on it.

## Method notes

Two dead ends worth recording so nobody repeats them:

- `cyberpunk2077_addresses.json` looks like a jackpot (132 MB of symbols) but only 83 of 987,479
  entries have names. It is a hash table, not a symbol dump.
- `tweakdb.bin` does **not** contain plaintext record names like `PlayerPossesion`. The record
  names are hashed in the optimized format. Loc strings are plaintext, which is why
  `johnny_replacer` is findable (it appears via a loc/reference) but the enum is not.