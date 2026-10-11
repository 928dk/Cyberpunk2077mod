---
title: "Implementation Plan: Publish the Cyberpunk 2077 mods to Nexus Mods as two separate mod pages [template:level_2/plan.md]"
description: "Repackage NoRelicSickness as a TweakXL drop-in, build NoJohnnyReplacer into a REDmod archive, verify both in game, then publish two Nexus pages with real licences, descriptions and images."
trigger_phrases:
  - "implementation"
  - "plan"
  - "nexus"
  - "tweakxl"
  - "redmod"
  - "release"
importance_tier: "normal"
contextType: "general"
_memory:
  continuity:
    packet_pointer: "specs/003-nexus-release"
    last_updated_at: "2026-10-11T09:00:00Z"
    last_updated_by: "big-pickle"
    recent_action: "Phases 1-2 executed: TweakXL overlay + release zip built and verified"
    next_safe_action: "Close the Phase 3 in-game gates (RED4ext + TweakXL) before publishing"
    blockers:
      - "Johnny keystone assumption unverified"
      - "WolvenKit CLI pack path undemonstrated"
    key_files:
      - "$PROJECT/tools/sickness-tweak.py"
      - "$PROJECT/tools/build-nexus-zips.sh"
      - "$PROJECT/src/no-relic-sickness/tweaks/NoRelicSickness.yaml"
      - "$PROJECT/tools/replacer-scope.py"
    session_dedup:
      fingerprint: "sha256:5b8e0f9a3f7c4d21a6b3e8c0d9f2a1b4c7e6d5f8a9b0c1d2e3f4a5b6c7d8e9f0"
      session_id: "003-nexus-release"
      parent_session_id: null
    completion_pct: 56
    open_questions: []
    answered_questions: []
---
<!-- SPECKIT_TEMPLATE_SOURCE: plan-core | v2.2 -->
# Implementation Plan: Publish the Cyberpunk 2077 mods to Nexus Mods as two separate mod pages

<!-- SPECKIT_LEVEL: 2 -->

---

<!-- ANCHOR:summary -->
## 1. SUMMARY

### Technical Context

| Aspect | Value |
|--------|-------|
| **Language/Stack** | Python 3 tooling; Cyberpunk 2077 REDengine mod formats |
| **Framework** | TweakXL (YAML), REDmod (archives), WolvenKit CLI |
| **Storage** | Game archives on local NVMe; release archives under `dist/` |
| **Testing** | `replacer-scope.py verify`, `sickness-tweak.py verify`, in-game playtest |

### Overview
The sickness mod moves from a source patch to a TweakXL YAML overlay so it installs like any other mod. The Johnny mod gains a build script that extracts the 16 targeted quest resources, flips `enable` to false, and packs a REDmod archive. Both are verified in game before any page is created, then published as two separate Nexus pages with honest descriptions and declared dependencies.
<!-- /ANCHOR:summary -->

---

<!-- ANCHOR:quality-gates -->
## 2. QUALITY GATES

### Definition of Ready
- [x] Problem statement clear and scope documented
- [x] Success criteria measurable
- [x] Dependencies identified (RED4ext, TweakXL, REDmod, WolvenKit, Nexus account)

### Definition of Done
- [ ] All P0 and P1 requirements met or approved for deferral
- [ ] In-game verification recorded in `implementation-summary.md`
- [ ] `validate.sh --strict` passes on this spec folder
- [ ] Both Nexus pages live with a downloadable archive
<!-- /ANCHOR:quality-gates -->

---

<!-- ANCHOR:architecture -->
## 3. ARCHITECTURE

### Pattern
Data-overlay mods (no runtime hooks). Each mod ships only the changed data as an overlay the engine merges at load.

### Key Components
- **NoRelicSickness (TweakXL)**: `r6/tweaks/*.yaml` overriding existing status-effect records; loaded by TweakXL/RED4ext.
- **NoJohnnyReplacer (REDmod)**: `mods/NoJohnnyReplacer/info.json` + `archives/*.archive` holding patched `.quest`/`.questphase` resources.
- **Build tooling**: `tools/sickness-tweak.py` (already exists), a new `tools/build-nexus-zips.sh`, and WolvenKit CLI for the quest pack step.

### Data Flow
Authoring: game `.tweak` sources / extracted quest corpus → patch → release archive under `dist/`. Install: user unzips into the game folder (or Vortex does it) → engine loads the overlay instead of the base data.

<!-- /ANCHOR:architecture -->

---

<!-- ANCHOR:affected-surfaces -->
## FIX ADDENDUM: AFFECTED SURFACES

| Surface | Current Role | Action | Verification |
|---------|--------------|--------|--------------|
| `tools/sickness-tweak.py` | Builds the source-patch payload | Add a YAML-emit mode | `verify` still passes; YAML matches the payload fields |
| `tools/replacer-scope.py` | Emits patched quest JSON | Feed the pack step | `verify` exits 0 |
| `src/no-relic-sickness/install.sh` | Patches shipped sources | Keep for reference; no longer the release path | README updated to lead with TweakXL |
| `README.md` | Project status | Update to reflect release state | Manual read |

Required inventories:
- Consumers of `NoRelicSickness`: `rg -n 'NoRelicSickness' src docs README.md`.
- Same-class records: `rg -n 'JohnnySickness|q304_songbird_relic_shock' src/no-relic-sickness/payload`.
<!-- /ANCHOR:affected-surfaces -->

---

<!-- ANCHOR:phases -->
## 4. IMPLEMENTATION PHASES

Phase names match `tasks.md`.

### Phase 1: Setup (docs + licence)
- [x] Lock names/versions for both mods
- [x] Replace `docs/Licence.md` template with a real mod licence + permissions block
- [x] Rewrite `docs/Version.md`, `docs/Changelog.md`, `docs/INSTALL.md`
- [x] Draft the sickness Nexus description (BBCode) with honest limitations
- [x] Produce the header image (1920x1080)

### Phase 2: Implementation (build both releases)
- [x] Sickness: map the exact records/fields to override
- [x] Sickness: emit `tweaks/NoRelicSickness.yaml`
- [x] Sickness: build `dist/NoRelicSickness-1.0.0.zip` (r6/tweaks layout)
- [ ] Johnny: extract the 16 tier-1 quest resources
- [ ] Johnny: patch `enable=false`, serialize, pack a REDmod archive
- [ ] Johnny: build `dist/NoJohnnyReplacer/`

### Phase 3: Verification
- [x] `validate.sh --strict` passes; privacy sweep clean
- [ ] Sickness: verify in game (presentation gone, call sites resolve); read `tweakxl.log`
- [ ] Johnny: verify the keystone assumption and SC-002/SC-003 in game

### Phase 4: Publish
- [ ] Create page 1 (sickness) and upload
- [ ] Create page 2 (Johnny) and upload
- [ ] Capture `mod_id`/`file_id`; store API key; add upload workflow
- [ ] Cross-link GitHub and Nexus
<!-- /ANCHOR:phases -->

---

<!-- ANCHOR:testing -->
## 5. TESTING STRATEGY

| Test Type | Scope | Tools |
|-----------|-------|-------|
| Unit | TweakDB/quest patch generation | `sickness-tweak.py verify`, `replacer-scope.py verify` |
| Integration | Archive contents and layout | unzip/`tar -t`, REDmod deploy log |
| Manual | In-game Relic arc | Cyberpunk 2077 on this machine |
| Privacy | Released trees + page copy | grep sweeps from `PRIVACY.md` |
<!-- /ANCHOR:testing -->

---

<!-- ANCHOR:dependencies -->
## 6. DEPENDENCIES

| Dependency | Type | Status | Impact if Blocked |
|------------|------|--------|-------------------|
| RED4ext + TweakXL | External (users) | Green | Sickness drop-in unusable |
| REDmod | External (game DLC) | Green (installed) | Johnny archive will not load |
| WolvenKit CLI | External tool | Yellow | No Johnny artifact |
| Nexus account | External | Green | No page |
<!-- /ANCHOR:dependencies -->

---

<!-- ANCHOR:rollback -->
## 7. ROLLBACK PLAN

- **Trigger**: a mod breaks saves, causes crashes, or fails verification.
- **Procedure**: delete the mod folder / remove the archive, reload the save, confirm vanilla behaviour; on Nexus, archive or hide the file and post a note.
<!-- /ANCHOR:rollback -->

---

<!-- ANCHOR:phase-deps -->
## L2: PHASE DEPENDENCIES

```
Phase 1 (setup) ──► Phase 2 (build) ──► Phase 3 (verify) ──► Phase 4 (publish)
```

| Phase | Depends On | Blocks |
|-------|------------|--------|
| 1 | None | 2 |
| 2 | 1 | 3 |
| 3 | 2 | 4 |
| 4 | 3 | None |
<!-- /ANCHOR:phase-deps -->

---

<!-- ANCHOR:effort -->
## L2: EFFORT ESTIMATION

| Phase | Complexity | Estimated Effort |
|-------|------------|------------------|
| A: Release prep | Low | 2-3 hours |
| B: Sickness -> TweakXL | Med | 3-5 hours |
| C: Johnny archive | High | 6-12 hours |
| D: Publish | Low | 1-2 hours |
| **Total** | | **12-22 hours** |
<!-- /ANCHOR:effort -->

---

<!-- ANCHOR:enhanced-rollback -->
## L2: ENHANCED ROLLBACK

### Pre-deployment Checklist
- [ ] Baseline save backed up before testing
- [ ] Original game resource backed up (if any patch path is used)
- [ ] Both mods confirmed removable by folder delete

### Rollback Procedure
1. Remove the mod folder (`mods/NoRelicSickness`, `mods/NoJohnnyReplacer`) or the `r6/tweaks` file.
2. Delete the compiled `r6/cache/modded/tweakdb.bin` if a patch path was used.
3. Reload the save; confirm no repair prompt.
4. On Nexus, archive the file and post a note.

### Data Reversal
- **Has data migrations?** No — data overlays only; nothing outside the mod folder is written.
- **Reversal procedure**: delete the mod directory.
<!-- /ANCHOR:enhanced-rollback -->
