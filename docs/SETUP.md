# Setup

Everything needed to reproduce the findings in this repository, from a clean machine.

## 1. Prerequisites

| Need | Why | Notes |
| --- | --- | --- |
| Cyberpunk 2077 (Steam, appid `1091500`) | the game data being analysed | any recent patch |
| **Cyberpunk 2077 REDmod** (Steam appid `2060310`) | ships `metadata.json`, the reflection database | free DLC, requires owning the game |
| .NET 10 SDK | WolvenKit.CLI builds against it | see §2 |
| Python 3.11+ | the tools in `tools/` | standard library only — no pip installs |

`REDmod` is not optional. It installs `tools/redmod/metadata.json`, which is the redscript
compiler's own reflection database (11,246 classes, 1,233 enums, 657 global functions). That file is
what settled the "can Redscript write player possession?" question statically, with no compiler and
no game launch. Inferring it from the `final.redscripts` string table instead would have been wrong —
that table only contains names the base-game scripts reference.

## 2. .NET 10

```bash
curl -fsSL https://dot.net/v1/dotnet-install.sh | bash -s -- --channel 10.0
export PATH="$HOME/.dotnet:$PATH"
dotnet --version    # expect 10.0.x
```

## 3. Third-party tooling

Not vendored in this repo. Clone into one directory:

```bash
mkdir -p ~/projects/Cyberpunk-tooling && cd ~/projects/Cyberpunk-tooling

git clone https://github.com/WolvenKit/WolvenKit.git
git clone https://github.com/CDPR-Modding-Documentation/Cyberpunk-Modding-Docs.git
git clone https://github.com/PixelRick/CyberpunkSaveEditor.git
git clone https://github.com/maximegmd/CyberEngineTweaks.git
```

| Clone | Used for | Optional? |
| --- | --- | --- |
| **WolvenKit** | archive extraction, `convert serialize` to JSON | **required** |
| **Cyberpunk-Modding-Docs** | `journal-quest-data.json` — quest ID → title map | required for the quest map |
| **CyberpunkSaveEditor** | `assets/CFacts.json` — the fact-name registry | required for fact searches |
| **CyberEngineTweaks** | reference for the CET layer | not needed; Design A is pure quest data |

`Cyberpunk-Modding-Docs` is large. If disk is tight, a sparse checkout of `.gitbook/assets` is enough:

```bash
git clone --filter=blob:none --sparse https://github.com/CDPR-Modding-Documentation/Cyberpunk-Modding-Docs.git
cd Cyberpunk-Modding-Docs && git sparse-checkout set .gitbook/assets
```

Build the CLI once:

```bash
cd ~/projects/Cyberpunk-tooling/WolvenKit
dotnet build WolvenKit.CLI/WolvenKit.CLI.csproj -c Release
```

## 4. Extract the quest corpus

The quest graph is only readable as JSON. **Do not grep the binary files** — node type names live in
a lookup table at the head of each file, so raw byte matches misattribute which node is which. This
produced a wrong conclusion early in the project.

The CLI's verb is **`extract`** (alias `unbundle`), not `unpack`. Flags are `-o/--outpath`,
`-gp/--gamepath`, `-r/--regex`:

```bash
export PATH="$HOME/.dotnet:$PATH"
export WK=~/projects/Cyberpunk-tooling/WolvenKit/WolvenKit.CLI
export GAME_DIR="$HOME/.local/share/Steam/steamapps/common/Cyberpunk 2077"
export OUT=/tmp/cp-unpack

# extract only the quest trees
dotnet run --project "$WK" -c Release --no-build -- \
    extract --gamepath "$GAME_DIR" --outpath "$OUT" --regex '\.quest(phase)?$'

# convert the phases containing replacer nodes to JSON, one at a time
for f in $(grep -rl 'questReplacer' "$OUT/base"); do
  dotnet run --project "$WK" -c Release --no-build -- convert serialize "$f" -v Quiet
done
```

`convert serialize` is slow — roughly 20–60 s per phase, and there are ~1,354 quest files. Extract
once, then convert only what you need. Run the commands from the `WolvenKit` directory or pass
`--project` an absolute path; the relative form used earlier in this project assumed that directory.

Known traps, all recorded in `findings/04-quest-node-hunt-results.md`:

- Node type names come from a lookup table at the file head. Binary greps attribute nodes to the
  wrong owners. Always serialise to JSON first.
- The game spells it **`Possesion`** with one trailing `s` in `gamedataPlayerPossesion`,
  `GetPlayerPossesionRecord`, `OnLocalPlayerPossesionChanged` — but spells `JohnnyReplacer` and
  `IsJohnnyReplacer` correctly. A regex written for the correct spelling silently reports "no match".
- `*.tweakdb` is **not** in the archives; TweakDB ships compiled only. `extract -r '\.tweakdb$'`
  matches 0 of 56,574.
- `final.redscripts` is plaintext, but its string table is **incomplete** — it holds only names the
  base-game scripts reference. `EntityExists` and `AddStateModifier` are script-callable and absent.
  Absence in that table is not proof of nonexistence.

## 5. Run the tools

```bash
# where is Johnny spawned, and what may we safely disable?
python3 tools/replacer-scope.py manifest /tmp/cp-unpack

# survey savegames (read-only; never writes save data)
export CP2077_SAVED_GAMES="$HOME/.local/share/Steam/steamapps/compatdata/1091500/pfx/drive_c/users/steamuser/Saved Games/CD Projekt Red/Cyberpunk 2077"
python3 tools/cp2077-metadata-scan.py
```

All tools use the standard library only.

## 6. Applying the mod

Read `docs/Rollback.md` first — it was written before the first edit, as the spec requires.

```bash
export GAME_DIR="$HOME/.local/share/Steam/steamapps/common/Cyberpunk 2077"

python3 tools/replacer-scope.py patch /tmp/cp-unpack --out "$GAME_DIR/mods/NoJohnnyReplacer"
python3 tools/replacer-scope.py verify /tmp/cp-unpack --out "$GAME_DIR/mods/NoJohnnyReplacer"
```

See `docs/Rollback.md` for pre-flight checks and the uninstall procedure.

`verify` must exit 0. It passes only if every tier-1 node is disabled **and** no tier-2/3 file was
touched.

To roll back:

```bash
rm -rf "$GAME_DIR/mods/NoJohnnyReplacer"
```

The mod writes no facts and no save state, so a save played with it loads fine without it, and
vice versa. One save is enough — no separate "modded" save is required.

## 7. After a game patch

Re-extract the corpus (§4) and diff the node manifest against the recorded baseline:

```bash
python3 tools/replacer-scope.py manifest /tmp/cp-unpack > /tmp/manifest-new.txt
diff research/replacer-manifest.txt /tmp/manifest-new.txt
```

New tier-1 files must be added to the patch set. Tier 2 and 3 stay held.

## Not yet verified

**`enable = false` has never been confirmed to suppress the replacer at runtime.** It is a populated
serialised field and the node system's parent type is `questDisableableNodeDefinition`, which is
strong circumstantial evidence — but only a game launch settles it. See T042 in the task list.