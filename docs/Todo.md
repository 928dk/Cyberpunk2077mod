# Todo List

## In Progress

- [ ] Diff facts between `ManualSave-5` (pre-Heist) and `ManualSave-6` (post-Heist) to isolate what
      The Heist writes to the fact store. This is the concrete next action.

## Backlog

### Research
- [ ] Confirm whether the 2022 saves load under the current game version
- [ ] Unpack game archives with WolvenKit if quest-level detail is needed
- [ ] Locate the actual merge trigger — not the story beat, the code path that forces it
- [ ] Check whether the trigger is scriptable (Redscript override) or a TweakDB condition
- [ ] Check the CDPR modding docs for any existing "remove Johnny" pattern to reuse

### Implementation
- [ ] Decide the layer: CET (Lua) vs Redscript vs REDmod
- [ ] Write the first CET prototype
- [ ] Write the first Redscript prototype, only if needed
- [ ] Package as a REDmod modlet

### Verification
- [ ] Load `ManualSave-5`, run The Heist, confirm the merge does not occur
- [ ] Confirm Night City districts and side quests remain reachable after the intervention
- [ ] Check for softlocks in the Relic arc
- [ ] Confirm Phantom Liberty is unaffected (out of scope, but must not break)

## Completed

- [x] Gate 3 — spec folder decision (new project folder)
- [x] Create spec folder `001-bypass-v-johnny-merge` with spec/plan/tasks
- [x] Survey the five cloned tooling repos
- [x] Identify quest IDs: `q005_heist`, `sq032_tapeworm`, fact `q302_06_johnny_disappear`, scene `sb_johnny_disappear`
- [x] Survey all savegames and pick a pre-merge baseline (`ManualSave-5`)
- [x] Scaffold this project from the project template