# NoRelicSickness

Stops the Relic from hurting V. The Relic, its storyline and its scenes all stay
exactly as they are — only the sickness *effect* is removed.

| | vanilla | with this |
|---|---|---|
| fullscreen yellow/glitch overlay | yes | no |
| camera breathing animation | yes | no |
| fullscreen SFX | yes | no |
| stamina regen penalty | −2.5% / −5% / −10% / −15% | none |
| the Relic, its quests, its scenes | yes | yes |
| scripted beats where V visibly collapses | yes | yes (see Scope) |

**Not yet verified in game.** The overlay is generated and structurally checked
but has never been loaded by the game. See *First launch* below for what must be
confirmed.

## Release format: TweakXL drop-in

The release ships one file:

```
r6/tweaks/NoRelicSickness.yaml
```

Unzip it into the Cyberpunk 2077 directory and you are done. Nothing is patched,
so there is no backup and no deploy step. Uninstalling means deleting the file.

Requires **RED4ext** and **TweakXL**. They are what read `r6/tweaks/*.yaml` and
merge it into the game's TweakDB. Without them the file is inert.

### First launch

TweakXL applies a file even when it rejects one property inside it, and it only
says so in its log. After the first launch, check:

```
<Cyberpunk 2077>/red4ext/logs/tweakxl.log
```

Every property in `NoRelicSickness.yaml` must have been applied. A rejected
property means the mod is only partly working.

## What it changes

Six status-effect records are overridden. `VFX[]` and `packages[]` are cleared on
each concrete record, and the `CameraAnimation` tag is dropped from the shared
abstract:

| Record | Override |
|---|---|
| `BaseStatusEffect.JohnnySicknessAbstract` | `gameplayTags` without `CameraAnimation` |
| `BaseStatusEffect.JohnnySicknessLow` | `VFX: []`, `packages: []` |
| `BaseStatusEffect.JohnnySicknessMedium` | `VFX: []`, `packages: []` |
| `BaseStatusEffect.JohnnySicknessMediumQuest` | `VFX: []`, `packages: []` |
| `BaseStatusEffect.JohnnySicknessHeavy` | `VFX: []`, `packages: []` |
| `BaseStatusEffect.q304_songbird_relic_shock` | `VFX: []`, `packages: []` (Phantom Liberty) |

**Every record and every inheritance edge is kept**, so all 11 quest call
sites — ten scene nodes in `sq032.quest` plus one in `sq032_sickness.questphase`
— still resolve. They apply a status effect that now does nothing.

A TweakXL array value *replaces* the vanilla array; `!append` and `!remove` are
the mutation forms. `[]` therefore clears an array, and the `gameplayTags` list
is the vanilla list with one entry removed.

## Source-patch variant

The older approach edits the game's own shipped TweakDB sources under
`tools/redmod/tweaks/`, then runs a REDmod deploy. It is kept for users who
cannot run TweakXL and is not the release:

```bash
./install.sh "/path/to/Cyberpunk 2077"     # back up, patch, add a marker mod, deploy
./uninstall.sh "/path/to/Cyberpunk 2077"   # restore the originals
```

Requires REDmod (Steam app 2060310) and, on Linux, `wine` — `redMod.exe` is a
Windows binary.

It exists because REDmod's tweak compiler merges the base tree and every mod's
`tweaks/` tree into one flat compile and **rejects a redeclared record**:

```
Line 27: Duplicated group 'JohnnySicknessLow' in package 'BaseStatusEffect'
```

So a REDmod can *add* TweakDB records but cannot *override* an existing one.
TweakXL has no such restriction, which is why the drop-in is the primary form.
Use one variant or the other, not both.

## Regenerating after a game patch

Both forms are generated from the shipped vanilla sources, never hand-written —
a hand-written copy silently rots the first time CDPR edits a record:

```bash
GAME="/path/to/Cyberpunk 2077"

# TweakXL drop-in (the release)
python3 tools/sickness-tweak.py yaml \
  --vanilla-root "$GAME/tools/redmod/tweaks" \
  --out src/no-relic-sickness/tweaks/NoRelicSickness.yaml
python3 tools/sickness-tweak.py verify-yaml \
  --vanilla-root "$GAME/tools/redmod/tweaks" \
  --yaml src/no-relic-sickness/tweaks/NoRelicSickness.yaml

# source patch
python3 tools/sickness-tweak.py build \
  --vanilla-root "$GAME/tools/redmod/tweaks" \
  --out-root src/no-relic-sickness/payload --diff
python3 tools/sickness-tweak.py verify \
  --vanilla-root "$GAME/tools/redmod/tweaks" \
  --override-root src/no-relic-sickness/payload
```

Every mode fails loudly if a field it means to change is not there — a CDPR
rename must not quietly become a no-op that still claims success.

> If the game install has already been patched by `install.sh`, its
> `tools/redmod/tweaks/` sources are the patched ones. `install.sh` keeps the
> pristine originals in `src/no-relic-sickness/.backup/`; point `--vanilla-root`
> there instead.

## Scope

Deliberately **not** included:

- **The scripted beats.** `sq032.quest` plays the sickness scene ten times and
  `sq032_sickness.questphase` once; V still visibly glitches and hears the
  voicesets. Removing those is a quest-graph edit, not a TweakDB one.
- **The death countdown.** Vanilla cannot kill V with the Relic — the
  5d→3d→2d12h→2d→1d12h→1d ladder is entirely Nexus mod 25974's addition, keyed
  off the `sickness_on` fact. This mod does not touch that fact, so **installing
  mod 25974 will still kill V on schedule.** The two are otherwise compatible:
  mod 25974 ships quest and scene overrides and no TweakDB, so there is no
  collision.
- **Johnny.** That is the separate `NoJohnnyReplacer` work in spec 001.

Phantom Liberty was not installed on the machine this was developed on, so the
`q304_songbird_relic_shock` override compiles but is unverified in play. The
`ep1` records are absent from a base-only install, where TweakXL simply has
nothing to override for that one record.
