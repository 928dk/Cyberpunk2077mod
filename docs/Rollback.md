# Rollback procedure

Written before the first edit, as spec FR-005 requires. Everything here must be true before the
mod is applied, and must remain true for the life of the mod.

## Principle

**The mod never modifies the game install.** All modified quest phases are *overrides* loaded by
REDmod from a directory REDmod owns. Un-installing the mod is deleting that directory. There is no
archive to repack, no repair pass, and no way for the mod to corrupt base game data.

This is why Design A chose quest-data overrides over the alternatives:

| Rejected approach | Why not |
| --- | --- |
| CET runtime hook | Needs the game running to iterate; opaque; survives patches unpredictably |
| Redscript override | Adds a compile step for no gain — no setter exists (finding 05) |
| Direct archive edit | Irreversible, breaks on patch, violates FR-006 |

## Pre-flight checks

Run these before the first apply. If any fails, stop.

```bash
MOD_DIR="$HOME/.local/share/Steam/steamapps/common/Cyberpunk 2077/mods/NoJohnnyReplacer"
GAME_DIR="$HOME/.local/share/Steam/steamapps/common/Cyberpunk 2077"

# 1. REDmod is present and the mod dir is ours, not someone else's
test -d "$GAME_DIR/tools/redmod" && echo "REDmod OK"
ls -d "$MOD_DIR" 2>/dev/null && echo "WARN: mod dir already exists — inspect before overwriting"

# 2. No other mod is also editing these quest phases
#    (conflict resolution in REDmod is last-wins; silent double-override is a real risk)
grep -rl "questReplacer" "$GAME_DIR/mods" 2>/dev/null | grep -v NoJohnnyReplacer

# 3. Baseline save exists and is untouched
ls -la "$HOME/.local/share/Steam/steamapps/common/Cyberpunk 2077/saved/game saves/"*.sav
```

## Apply

The mod ships as an override directory. From the project root:

```bash
cd ~/projects/Client/Cyberpunk2077mod

# regenerate the patch from the extracted quest corpus
python3 tools/replacer-scope.py patch $SCRATCH/cp-unpack \
        --out "$HOME/.local/share/Steam/steamapps/common/Cyberpunk 2077/mods/NoJohnnyReplacer"

# prove the delta before trusting it
python3 tools/replacer-scope.py verify $SCRATCH/cp-unpack \
        --out "$HOME/.local/share/Steam/steamapps/common/Cyberpunk 2077/mods/NoJohnnyReplacer"
echo "verify exit=$?"
```

`verify` must print `tier1 still enabled : 0  OK`, `tier2/3 files patched : 0  OK` and exit 0.
**Do not launch the game until it does.**

## Rollback

```bash
rm -rf "$HOME/.local/share/Steam/steamapps/common/Cyberpunk 2077/mods/NoJohnnyReplacer"
```

That is the whole procedure. Then load the same save. Expected: vanilla behaviour, no repair
prompt, no crash.

## Save handling

The mod touches **quest data only**. It does not write to the save, does not add facts, and does
not change player state. Therefore:

- A save played with the mod can be loaded without it.
- A save played without the mod can be loaded with it.
- **One save file is sufficient — no separate "modded" save is needed.**

Keep `ManualSave-5` (pre-Heist, 2022) untouched as the rollback baseline. Confirm it still loads
under the current patch before relying on it; if it does not, take a fresh pre-Heist save.

## Post-patch maintenance

If a game update lands, the mod may need regenerating because the extracted corpus in
`$SCRATCH/cp-unpack` is a snapshot. Procedure:

1. Re-extract the quest corpus (see `findings/04` for the WolvenKit commands).
2. Re-run `tools/replacer-scope.py manifest` and diff against the recorded manifest.
3. New tier-1 files must be added to the patch set. Tier 2/3 stay held.

The recorded baseline manifest is in `research/replacer-manifest.txt`.