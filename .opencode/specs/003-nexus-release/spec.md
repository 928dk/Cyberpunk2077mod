---
title: "Feature Specification: Publish the Cyberpunk 2077 mods to Nexus Mods as two separate mod pages [template:level_2/spec.md]"
description: "Two Cyberpunk 2077 mods exist in this repo as research plus tooling, but neither is installable by a mod manager or verified in game. This spec packages each as a Nexus-ready release and creates two public mod pages."
trigger_phrases:
  - "nexus"
  - "publish"
  - "release"
  - "mod page"
  - "tweakxl"
  - "cyberpunk"
  - "relic sickness"
  - "johnny replacer"
importance_tier: "normal"
contextType: "general"
_memory:
  continuity:
    packet_pointer: "specs/003-nexus-release"
    last_updated_at: "2026-10-11T09:00:00Z"
    last_updated_by: "big-pickle"
    recent_action: "Phases 1-2 executed: docs, licence, TweakXL overlay, release zip; spec validator PASSED"
    next_safe_action: "Install RED4ext + TweakXL and close the Phase 3 in-game gates before publishing"
    blockers:
      - "NoJohnnyReplacer core assumption (enable=false honoured at runtime) is still unverified"
      - "WolvenKit CLI serialize/pack path for quest resources is undemonstrated under Linux"
      - "In-game verification needs a save reaching the Relic arc, plus RED4ext + TweakXL installed"
    key_files:
      - "$PROJECT/src/no-relic-sickness/tweaks/NoRelicSickness.yaml"
      - "$PROJECT/src/no-relic-sickness/README.md"
      - "$PROJECT/tools/sickness-tweak.py"
      - "$PROJECT/tools/build-nexus-zips.sh"
      - "$PROJECT/tools/replacer-scope.py"
      - "$PROJECT/docs/Licence.md"
      - "$PROJECT/docs/INSTALL.md"
      - "$PROJECT/README.md"
    session_dedup:
      fingerprint: "sha256:5b8e0f9a3f7c4d21a6b3e8c0d9f2a1b4c7e6d5f8a9b0c1d2e3f4a5b6c7d8e9f0"
      session_id: "003-nexus-release"
      parent_session_id: null
    completion_pct: 56
    open_questions:
      - "Publish the Johnny mod as the honest partial now, or attempt scene-actor removal (T049) first?"
      - "Does TweakXL cleanly drop the CameraAnimation tag, or only empty arrays?"
    answered_questions:
      - "Publish both mods as separate Nexus pages (not one combined page)."
      - "Relic-sickness mod ships as a TweakXL YAML drop-in, not a patch installer."
---
<!-- SPECKIT_TEMPLATE_SOURCE: spec-core | v2.2 -->
# Feature Specification: Publish the Cyberpunk 2077 mods to Nexus Mods as two separate mod pages

<!-- SPECKIT_LEVEL: 2 -->

---

<!-- ANCHOR:metadata -->
## 1. METADATA

| Field | Value |
|-------|-------|
| **Level** | 2 |
| **Priority** | P1 |
| **Status** | In Progress |
| **Created** | 2026-10-10 |
| **Branch** | `003-nexus-release` |
<!-- /ANCHOR:metadata -->

---

<!-- ANCHOR:problem -->
## 2. PROBLEM & PURPOSE

### Problem Statement
The repo holds two distinct Cyberpunk 2077 mods. `NoRelicSickness` (spec 002) is implemented but ships as a shell-script patch that edits the game's own shipped TweakDB sources, which no mod manager can install. `NoJohnnyReplacer` (spec 001) has no build artifact at all: it is a Python generator that emits patched quest JSON from an extracted corpus. Neither is verified in game, neither has a downloadable archive, and the licensing and release docs are still unedited templates.

### Purpose
Produce two installable, verified, correctly licensed mod archives and publish each as its own Nexus Mods page, so a stranger can install either one with Vortex and know exactly what it does and does not change.
<!-- /ANCHOR:problem -->

---

<!-- ANCHOR:scope -->
## 3. SCOPE

### In Scope
- Repackage `NoRelicSickness` as a **TweakXL** YAML overlay (drop-in `r6/tweaks`), replacing the patch-script approach of spec 002.
- Build `NoJohnnyReplacer` into a real artifact: patched `.quest`/`.questphase` resources packed into a REDmod archive.
- In-game verification of both mods on a save that reaches the Relic arc.
- Release prep: real licence/permissions, version/changelog/install docs, Nexus descriptions with honest limitations, header images.
- Create two Nexus mod pages manually and upload the first files.
- Post-release: capture `mod_id`/`file_id`, wire the Nexus upload API/GitHub Action for later versions.

### Out of Scope
- Removing Johnny from scripted scenes (`Character.Silverhand` spawnDespawn, 195 scenes) — tracked as T049, deferred to a later update.
- Phantom Liberty verification beyond a successful compile — PL not owned on this machine.
- New meshes/textures/voice work — not this project.
- The parked replacement-quest project (`~/projects/Client/Cyberpunk2077suppressJohnny/`).

### Files to Change

| File Path | Change Type | Description |
|-----------|-------------|-------------|
| `docs/Licence.md` | Modify | Replace MIT template with a mod licence + Nexus-style permissions block |
| `docs/Version.md` | Modify | Real versioning for both mods; drop "no code exists" text |
| `docs/Changelog.md` | Modify | Real release entries |
| `docs/INSTALL.md` | Modify | Real install/uninstall for both formats |
| `README.md` | Modify | State current release status honestly |
| `src/no-relic-sickness/tweaks/NoRelicSickness.yaml` | Create | TweakXL overlay records |
| `src/no-relic-sickness/README.md` | Modify | Document the TweakXL path and its dependencies |
| `dist/` | Create | Zip-ready trees per mod (git-ignored) |
| `tools/build-nexus-zips.sh` | Create | Build script producing both release archives |
| `src/no-relic-sickness/RELEASE.txt` | Create | Readme shipped inside the release archive |
| `PRIVACY.md` | Modify | Update the sweep expectations for the spec-003 files |
| `.opencode/specs/003-nexus-release/scratch/nexus-sickness.txt` | Create | Nexus page copy (BBCode) with honest limitations |
| `.opencode/specs/003-nexus-release/scratch/nexus-header-sickness.png` | Create | 1920x1080 page header image |
| `.opencode/specs/003-nexus-release/scratch/make-nexus-header.py` | Create | Draws the header image; reproduces it from source |
| `.opencode/specs/001-.../README` | Modify | Link the Johnny mod to its Nexus page once published |
<!-- /ANCHOR:scope -->

---

<!-- ANCHOR:requirements -->
## 4. REQUIREMENTS

### P0 - Blockers (MUST complete)

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| REQ-001 | `NoRelicSickness` installs as a drop-in mod via TweakXL | `r6/tweaks/NoRelicSickness.yaml` present in the archive; no game file patched; TweakXL applies every property with none rejected in `red4ext/logs/tweakxl.log` |
| REQ-002 | `NoJohnnyReplacer` has a reproducible build artifact | Build script emits an archive containing exactly the 16 tier-1 quest resources, all with `enable=0` |
| REQ-003 | Both mods verified in game | Sickness: no overlay/breathing/SFX/stamina penalty, quest call sites resolve. Johnny: no merge, districts reachable, no softlock, clean uninstall |
| REQ-004 | No personal identifiers in released artifacts or page text | Privacy sweep over `dist/` and page copy returns only documented false positives |

### P1 - Required (complete OR user-approved deferral)

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| REQ-005 | Real licence/permissions published | `docs/Licence.md` and the Nexus permissions block both set, no `YYYY/Your Name` placeholder |
| REQ-006 | Both Nexus pages created and files uploaded | Two public pages reachable under `nexusmods.com/profile/928dk/mods` |
| REQ-007 | Descriptions state honest limitations | Johnny page notes scripted-scene Johnny; sickness page notes mod 25974 interaction |
| REQ-008 | Requirements/dependencies declared on both pages | RED4ext + TweakXL for the sickness mod; REDmod for the Johnny mod |
<!-- /ANCHOR:requirements -->

---

<!-- ANCHOR:success-criteria -->
## 5. SUCCESS CRITERIA

- **SC-001**: A fresh install of `NoRelicSickness` (RED4ext + TweakXL only) removes the Relic-sickness presentation in game with no game-file patching and no deploy step.
- **SC-002**: `NoJohnnyReplacer` archive applies cleanly; on a save through the Relic arc, V does not merge and the six districts plus a side gig remain reachable.
- **SC-003**: Removing either mod returns the save and game to vanilla behaviour with no archive repair.
- **SC-004**: Both mod pages are live, each with a downloadable archive, declared dependencies, and a description matching the tested behaviour.
- **SC-005**: A later version can be uploaded without the website form, using a stored API key and the Nexus upload action.
<!-- /ANCHOR:success-criteria -->

---

<!-- ANCHOR:risks -->
## 6. RISKS & DEPENDENCIES

| Type | Item | Impact | Mitigation |
|------|------|--------|------------|
| Risk | TweakXL silently rejects a property (e.g. an array it will not bind) | Sickness mod partly applied, with no in-game warning | Read `red4ext/logs/tweakxl.log` on first launch; fall back to the spec-002 patch format and document it |
| Risk | `enable=false` is not honoured at runtime | **NoJohnnyReplacer is void as designed** | Verify first, before any page is created; if it fails, do not publish the Johnny mod |
| Risk | WolvenKit CLI cannot serialize/pack quest resources under Linux | No artifact | Test the CLI round-trip early; fall back to WolvenKit GUI on a Windows box |
| Risk | Quest override conflicts with other quest mods (load order) | Silent last-wins override | Ship only changed resources; document load order on the page |
| Risk | In-game verification requires reaching the Relic arc | Blocks SC-002/SC-003 | Use the baseline save; if the 2022 save will not load, take a fresh pre-Heist save |
| Dependency | RED4ext + TweakXL | Sickness drop-in path blocked | List as hard requirements on the Nexus page |
| Dependency | REDmod (Steam app 2060310) | Johnny archive load blocked | Already installed on this machine |
| Dependency | WolvenKit (`~/projects/Cyberpunk-tooling/WolvenKit`) | Build blocked | Present; confirm CLI works |
| Dependency | Nexus account (`928dk`) | Publish blocked | Account exists; first mod page is manual |
<!-- /ANCHOR:risks -->

---

<!-- ANCHOR:nfr -->
## L2: NON-FUNCTIONAL REQUIREMENTS

### Performance
- **NFR-P01**: Neither mod adds a measurable frame-time cost; both are data-only changes.
- **NFR-P02**: `NoRelicSickness` load adds no deploy step (no `redMod.exe` run required).

### Security
- **NFR-S01**: No personal identifiers (account name, home paths, playthrough IDs) in released archives or page text.
- **NFR-S02**: No secrets, tokens or API keys committed; the Nexus API key lives only in user secrets.

### Reliability
- **NFR-R01**: Uninstalling either mod restores vanilla behaviour with no archive repair.
- **NFR-R02**: Build scripts fail loudly if a targeted field/record is missing or renamed by a game patch.
<!-- /ANCHOR:nfr -->

---

<!-- ANCHOR:edge-cases -->
## L2: EDGE CASES

### Data Boundaries
- Game patch renames a record/field: `sickness-tweak.py build` and `replacer-scope.py verify` must fail, not silently no-op.
- Phantom Liberty not installed: base-only path must still produce a valid archive; the `ep1` record is skipped with a warning.

### Error Scenarios
- TweakXL/RED4ext absent: mod does nothing; the page lists them as required dependencies.
- Another mod overrides the same quest resources: document load-order expectation; do not attempt automatic conflict resolution.
- REDmod not installed: the Johnny archive will not load; listed as a requirement.

### State Transitions
- Partial install (sickness only, Johnny absent): both are independent; no cross-dependency.
- Version update: API upload adds a new file version; `archive_existing_version` set so the Files tab does not clutter.
<!-- /ANCHOR:edge-cases -->

---

<!-- ANCHOR:complexity -->
## L2: COMPLEXITY ASSESSMENT

| Dimension | Score | Notes |
|-----------|-------|-------|
| Scope | [16/25] | Two mods, docs, images, two pages, build tooling |
| Risk | [14/25] | Public release; keystone assumption unverified; one mod may be unpublishable |
| Research | [12/20] | TweakXL tag semantics, WolvenKit CLI, Nexus first-page flow |
| **Total** | **[42/70]** | **Level 2** |
<!-- /ANCHOR:complexity -->

---

<!-- ANCHOR:questions -->
## 10. OPEN QUESTIONS

Resolved:
- Author handle and licence on the page: `928dk` + MIT, confirmed by the maintainer on 2026-10-11.
- Does TweakXL drop a tag, or only clear arrays? A plain list assignment replaces the vanilla list,
  so the `CameraAnimation` tag is dropped by writing the two tags that remain. Settled against the
  local TweakXL docs and WolvenKit's record definition; not yet observed in game.
- Should the sickness mod also ship a REDmod-format variant for users without TweakXL? No. REDmod's
  tweak compiler rejects a redeclared record, so it cannot express this override. The TweakXL drop-in
  is the release; the in-repo patch variant covers users who will not install TweakXL.

Open:
- Publish the Johnny mod as the honest partial now, or attempt scene-actor removal (T049) first?
- Beyond the six records, does any other path re-apply the sickness? Only playing with the mod
  installed can rule that out.
<!-- /ANCHOR:questions -->
