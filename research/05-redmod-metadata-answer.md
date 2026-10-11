# T019 ANSWERED: no setter exists. The merge is a quest data node. (2026-10-04)

The install of **Cyberpunk 2077 REDmod** (appid 2060310) produced a better oracle than the
compile probe I had planned.

## The oracle: `tools/redmod/metadata.json`

6.5 MB of the redscript reflection database that ships with REDmod:

| Section | Count |
| --- | --- |
| `classes` | 11,246 |
| `enums` | 1,233 |
| `global_functions` | 657 |
| `bitfields` | 26 |
| `aliases` | — |
| `simple_types` | 18 |

This is the complete set of types and functions the redscript compiler validates against. It answers
"does this exist?" **without** needing to compile anything. The compile probe is now unnecessary.

## Answer: there is no setter. At all.

Searching every class, every member function, every static function and every global function for
`osses` / `ossession` / `eplacer`:

```
gamedataTweakDBInterface.GetPlayerPossesionRecord     <- GETTER
gamedataUIIconCensorship_Record.Replacer              <- unrelated (censorship icon)
gamedataUIIconCensorship_Record.ReplacerHandle        <- unrelated (censorship icon)
```

**Three hits, and only one is real. It is a getter.** There is no `SetPlayerPossesion`, no
`SetLocalPlayerPossesion`, no setter of any kind, and no global function.

Searching for writable fields of type `gamedataPlayerPossesion` returns exactly one:

```
questSetPossesion_NodeType.playerPossesion
```

**So: Redscript cannot write player possession. That question is settled.**

## But there is a data node that does

```csharp
questSetPossesion_NodeType : questISceneManagerNodeType   // size 64
{
    gamedataPlayerPossesion playerPossesion;   // the only property
}
```

And the enum is confirmed exactly as the string table suggested:

```
gamedataPlayerPossesion -> { Default: 0, Johnny: 1, Count: 2, Invalid: 3 }
```

## Where it is used — all 5 sites, read from the serialised JSON

| File | Quest | `playerPossesion` |
| --- | --- | --- |
| `q115_03_afterlife.questphase` | **For Whom the Bell Tolls** (main, part 1) | `Johnny` |
| `q204_00_setup.questphase` | **New Dawn Fades** (epilogue) | `Johnny` |
| `q203_penthouse.questphase` | **Path of Glory** (epilogue) | `Default` |
| `sq031.questphase` | **Chippin' In** (side quest) | `Johnny` ×3 |
| `q115_afterlife.quest` | For Whom the Bell Tolls (quest root) | — |

`q203` already uses `Default`. That is the proof-of-concept that the game itself keeps V as V on one
ending path — the node is meant to be flipped, and CDPR flips it.

## The critical distinction

**This node governs the ending, not the progressive takeover.**

All five sites are endings or epilogues:
- *For Whom the Bell Tolls* — V takes the Relic and inherits Johnny's body
- *New Dawn Fades* — Johnny-takes-over epilogue
- *Chippin' In* — the Akira side-quest where Johnny takes the body

None of them is in the Relic arc proper. The **progressive** merge during the Relic run — Johnny
glitching in at the Afterlife, the chip percentage climbing, the escalating
`johnny_sickness_lvl1/2/3`, the `JohnnySickness` breathing effect — is a **different system** and is
not driven by `questSetPossesion`.

So fixing this node prevents *"V permanently becomes Johnny at the ending."* It does **not** prevent
*"Johnny progressively overwrites V across the Relic arc."* Those are two problems, and the user's
original request is about the second one.

## Where this leaves the project

| Question | Status |
| --- | --- |
| Can Redscript write possession? | **No.** Settled from `metadata.json`. |
| Is the final merge editable? | **Yes** — flip `playerPossesion` to `Default` in q115/q204/sq031 |
| Is the progressive takeover editable via quest data? | **Not via this node.** Need a different lever. |
| Is the progressive takeover CET-hookable? | **Likely yes** — the possession state, its change event (`OnLocalPlayerPossesionChanged`) and the `m_OnReplacerChangedCallback` hook are all visible to a runtime hook, even though none is script-writable |

The honest read: the ending is a five-minute data edit. The progressive takeover — the thing actually
being asked about — is engine-side and, on current evidence, only reachable by a runtime CET hook or
by suppressing the symptoms (`JohnnySickness` status effects, the Johnny quest sequences).

That is a meaningful narrowing, and it points at **T019a (runtime CET enumeration)** as the next
real step, not at more offline archaeology.

## Method note

This is the payoff from actually looking things up. Two earlier claims in this project were wrong
because they were asserted rather than queried:

- the modkit appid (2694490 → actually 2060310, Path of Exile 2)
- "no setter exists", inferred from the `final.redscripts` string table

The second was *nearly* right for the wrong reason, and the string table could not have established
it — that table only holds names the base-game scripts reference, so `EntityExists` and
`AddStateModifier` are missing from it despite being script-callable. The `metadata.json` reflection
database is the correct oracle because it is what the compiler itself validates against.

## Reusable

```python
# Query REDmod's reflection DB instead of guessing
import json, pathlib
db = json.loads(pathlib.Path(
    "~/.local/share/Steam/steamapps/common/Cyberpunk 2077/tools/redmod/metadata.json"
).expanduser().read_text())
db["classes"]      # 11246, each with .functions / .static_functions / .properties
db["enums"]        # 1233
db["global_functions"]  # 657
```

Class properties carry `name`, `type`, `offset` and `flags`. A property's `type` is the type name, so
cross-referencing `type == "<enum>"` finds every field that stores that enum — which is how
`questSetPossesion_NodeType.playerPossesion` was isolated.