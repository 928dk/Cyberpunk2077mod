# Trigger research (initial)

Key findings from repo search:

1. **The Heist quest**: `q005_heist` (quest path `quests/main_quest/prologue/q005_heist`)
- Journal entries around line ~22072 in `journal-quest-data (1).json` (Modding-Docs).
- "The Heist" is heavily involved; merge occurs in Relic arc after/around this sequence.

2. **Tapeworm quest** (sq032_tapeworm) relates to Relic/Johnny integration
- `q302_06_johnny_disappear` fact appears in `CyberpunkSaveEditor/assets/CFacts.json`
- Scene asset: `sb_johnny_disappear` (prefab/scnlocjson/scenesolution) in WolvenKit test resources

3. **Johnny appearance/disappearance**
- Scene block `sb_johnny_disappear` exists — suggests scripted points where Johnny disappears. This might be relevant to Path B (getting rid of JSH).
- Modding-Docs has guide "Johnny glitching and talking with V" — useful for understanding how Johnny is controlled.

4. **Merge trigger is not obviously named in docs**
- No obvious "merge" keyword string in text we scanned. The merge is likely controlled via quest conditions/facts, flags, or Redscript logic (not just a named string in docs).
- Need to inspect actual quest scripts or savegame facts near the merge point.

## Next steps (recommended)
- Inspect saves with CyberpunkSaveEditor: find which save is closest before The Heist/Relic merge; look for quest facts set around that point.
- If you have game unpacked (WolvenKit project), search quest files (.quest, .scene, .reds) for terms like "merge", "chip", "Relic", "overwrite", "takeover".
- For Path B (inject new quest to get rid of JSH), look at how `sb_johnny_disappear` is used — possibly trigger similar disappearance/resolution.
- For Path A (prevent merge entirely), likely need to identify the specific quest phase/node that forces merge and either skip it or change its conditions. That will probably require looking at quest files/reds rather than docs alone.
