# Spec: Cyberpunk 2077 V–Johnny Merge Bypass

Full specification, plan and tasks live in the spec folder:
`~/projects/Client/Cyberpunk2077mod/.opencode/specs/001-bypass-v-johnny-merge/`

Goal: prevent V–Johnny merge in the Relic storyline; fallback: inject an alternative resolution that
removes Johnny instead of merging him, while keeping other areas and quests accessible.

## Key candidates
- Baseline save: `ManualSave-5` (pre-Heist, q004 done, q005 not done, 29.10.2022)
- Diff partner: `ManualSave-6` (post-Heist, same playthrough, same day)
- Quests: `q005_heist` (The Heist), `sq032_tapeworm` (Tapeworm)
- Fact: `q302_06_johnny_disappear`
- Scene asset: `sb_johnny_disappear` (the game's own Johnny-removal mechanism)

## Status
Nothing implemented. Phase 1 is investigation only — see the spec folder for gates G1–G7.
