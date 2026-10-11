---
title: "Implementation Summary: Publish the Cyberpunk 2077 mods to Nexus Mods as two separate mod pages [template:level_2/implementation-summary.md]"
description: "NoRelicSickness is now a packaged TweakXL drop-in with real release docs; NoJohnnyReplacer is honestly recorded as unbuildable until the WolvenKit round-trip and the keystone assumption are proven."
trigger_phrases:
  - "implementation"
  - "summary"
  - "nexus"
  - "tweakxl"
  - "release"
importance_tier: "normal"
contextType: "general"
_memory:
  continuity:
    packet_pointer: "specs/003-nexus-release"
    last_updated_at: "2026-10-11T09:00:00Z"
    last_updated_by: "big-pickle"
    recent_action: "Phases 1-2 executed; TweakXL overlay + release zip built; spec validator PASSED"
    next_safe_action: "Install RED4ext + TweakXL and close the Phase 3 in-game gates"
    blockers:
      - "In-game verification needs the game + RED4ext + TweakXL"
      - "Johnny archive needs a demonstrated WolvenKit serialize/pack round-trip"
    key_files:
      - "$PROJECT/tools/sickness-tweak.py"
      - "$PROJECT/tools/build-nexus-zips.sh"
      - "$PROJECT/src/no-relic-sickness/tweaks/NoRelicSickness.yaml"
    session_dedup:
      fingerprint: "sha256:5b8e0f9a3f7c4d21a6b3e8c0d9f2a1b4c7e6d5f8a9b0c1d2e3f4a5b6c7d8e9f0"
      session_id: "003-nexus-release"
      parent_session_id: null
    completion_pct: 56
    open_questions: []
    answered_questions: []
---
<!-- SPECKIT_TEMPLATE_SOURCE: impl-summary-core | v2.2 -->
# Implementation Summary

<!-- SPECKIT_LEVEL: 2 -->
<!-- HVR_REFERENCE: .opencode/skills/sk-doc/references/hvr_rules.md -->

---

<!-- ANCHOR:metadata -->
## Metadata

| Field | Value |
|-------|-------|
| **Spec Folder** | 003-nexus-release |
| **Delivered** | 2026-10-11 (Phases 1 and 2 complete; Phase 3 in-game gates open) |
| **Level** | 2 |
<!-- /ANCHOR:metadata -->

---

<!-- ANCHOR:what-built -->
## What Was Built

The Relic-sickness mod stopped being a patch script and became a release. It now ships as one
TweakXL file that overrides six game records and touches nothing else, so a player can install it by
copying a single folder and uninstall it by deleting a single file. At the same time, the Johnny mod
was left where it honestly belongs: designed, scoped, and unpublished, because its core assumption
has never been tested.

### NoRelicSickness as a TweakXL drop-in

You install it by dropping `r6/tweaks/NoRelicSickness.yaml` into the game directory. There is no
patch step, no backup to take and no REDmod deploy, because the mod never edits a shipped file. It
overrides six status-effect records through TweakXL and clears only their payload, so the Relic, its
quests and its scenes keep working exactly as vanilla.

The overlay is generated, never hand-written. `tools/sickness-tweak.py yaml` reads the shipped
vanilla sources and emits it; `verify-yaml` re-reads both and fails if a record is missing, a field
was renamed, or the `CameraAnimation` tag survived. That matters because a TweakXL file which
references a property the game no longer has is applied anyway, minus that property, with the
rejection written only to `red4ext/logs/tweakxl.log`. A generated-and-checked overlay cannot rot
into that silently.

### Release docs that match reality

`docs/Licence.md`, `docs/Version.md`, `docs/Changelog.md` and `docs/INSTALL.md` no longer carry
project-template filler. The licence states the real holder and permissions; the version file states
plainly that the mod is packaged but not yet run in game; the install guide covers the drop-in, the
repo-only patch variant, and the fact that the Johnny mod has no download.

### A build script and an honest refusal

`tools/build-nexus-zips.sh` produces `dist/NoRelicSickness-1.0.0.zip`, and with `--check` it
regenerates and re-verifies the overlay before packaging. Asked to build the Johnny archive, it
refuses and says why: no WolvenKit serialize/pack round-trip has been demonstrated, and the keystone
assumption is untested. Publishing a stub would be worse than publishing nothing.

### Files Changed

| File | Action | Purpose |
|------|--------|---------|
| `tools/sickness-tweak.py` | Modified | Added the `yaml` and `verify-yaml` modes and the two-form docstring |
| `tools/build-nexus-zips.sh` | Created | Builds the release archives under `dist/` |
| `src/no-relic-sickness/tweaks/NoRelicSickness.yaml` | Created | The TweakXL overlay — the actual release payload |
| `src/no-relic-sickness/RELEASE.txt` | Created | The readme shipped inside the archive |
| `src/no-relic-sickness/README.md` | Modified | Leads with the drop-in; keeps the patch variant as repo-only |
| `docs/Licence.md` | Modified | Real licence, permissions and game-data carve-out |
| `docs/Version.md` | Modified | Per-mod state and the two unverified items |
| `docs/Changelog.md` | Modified | Dated entries replacing the scaffold note |
| `docs/INSTALL.md` | Modified | Player-facing install for both mods and both formats |
| `README.md` | Modified | Two-mod framing, a Releases section, split status |
| `PRIVACY.md` | Modified | Privacy-sweep expectations corrected for spec 003 |
| `.opencode/specs/003-nexus-release/scratch/nexus-sickness.txt` | Created | The Nexus page copy, BBCode, with a limitations block |
| `.opencode/specs/003-nexus-release/scratch/nexus-johnny.txt` | Created | Why the Johnny page must not be written yet |
| `.opencode/specs/003-nexus-release/scratch/make-nexus-header.py` | Created | Draws the page header image with Pillow |
| `.opencode/specs/003-nexus-release/scratch/nexus-header-sickness.png` | Created | The 1920x1080 Nexus header for the sickness page |
<!-- /ANCHOR:what-built -->

---

<!-- ANCHOR:how-delivered -->
## How It Was Delivered

Everything objective was verified without the game, and everything that needs the game was left
open rather than assumed done. The overlay round-trips: `build` from the vanilla sources reproduces
the committed `payload/` byte-for-byte, `verify` confirms all six records are neutralised across both
files with inheritance intact, and `verify-yaml` confirms the drop-in covers exactly the same six.
The generator was proven to fail loudly by pointing it at an already-patched source, where it raised
`tag 'CameraAnimation' absent ... review before shipping` and exited 1. The release zip was built and
listed: it contains the overlay and a readme and no game data.

`validate.sh --strict` on the spec folder passes with 0 errors and 0 warnings, and a privacy sweep of
the working tree found 13 identifier hits, all of them spec-kit `sha256` fingerprints, plus zero
absolute home paths and zero tracked save files.

The Phase 3 gates are named and unclosed: install RED4ext and TweakXL, launch, read
`red4ext/logs/tweakxl.log` to confirm no property was rejected, then reach the Relic arc and confirm
the presentation is gone while the story continues.
<!-- /ANCHOR:how-delivered -->

---

<!-- ANCHOR:decisions -->
## Key Decisions

| Decision | Why |
|----------|-----|
| Ship the TweakXL drop-in as the release, keep the source patch as a repo-only variant | REDmod's tweak compiler rejects a redeclared record, so an existing TweakDB record cannot be overridden that way. TweakXL overrides it cleanly, and it patches no shipped file, so uninstalling is deleting one file. |
| Generate the overlay instead of hand-writing it | A hand-written copy silently rots the first time CDPR renames a field. Generating it from the shipped sources makes a rename a build failure instead of a quiet no-op. |
| Keep every record and inheritance edge, clear only the payload | All 11 quest call sites still resolve to a status effect that now does nothing. That avoids touching the quest graph entirely. |
| Leave `NoJohnnyReplacer` unpublished | It has a buildable but **unverified** artifact (`dist/NoJohnnyReplacer-1.0.0-rc1.archive`) and its keystone assumption (that `questReplacer_NodeType.enable = false` is honoured at runtime) is untested. A page would be a false claim. |
| MIT with the handle `928dk` for the licence and author | The repo already presented as MIT and the Nexus account is `928dk`; the maintainer confirmed both on 2026-10-11. |
| Keep `dist/` and `.backup/` git-ignored | The release archives are build output and the pristine sources are a machine-local backup of CDPR's data. Neither belongs in a public repository. |
<!-- /ANCHOR:decisions -->

---

<!-- ANCHOR:verification -->
## Verification

| Check | Result |
|-------|--------|
| `python3 -m py_compile tools/*.py` | PASS |
| `bash -n` on `tools/build-nexus-zips.sh`, `install.sh`, `uninstall.sh` | PASS |
| `sickness-tweak.py verify` (patch form, `.backup` vs `payload`) | PASS — 6 records across 2 files neutralised, inheritance intact |
| `sickness-tweak.py verify-yaml` | PASS — overlay covers exactly the intended 6 records |
| `sickness-tweak.py build` reproduces the committed payload | PASS — `diff -r` identical |
| `build-nexus-zips.sh --check` | PASS — regenerated, verified, parsed and packaged `dist/NoRelicSickness-1.0.0.zip` |
| PyYAML `safe_load` of the overlay | PASS — 6 top-level record overrides, expected shapes |
| Fail-loud behaviour on a renamed/absent field | PASS — raised and exited 1 against an already-patched source |
| `validate.sh --strict .opencode/specs/003-nexus-release` | PASS — 0 errors, 0 warnings |
| Privacy sweep (identifiers / home paths / save data) | PASS — 13 sha256 fingerprints only; 0 paths; 0 saves |
| Header image renders at the required size | PASS — `nexus-header-sickness.png` is 1920x1080; every text block measured to sit inside the frame |
| GitHub repo description applied | PASS — `gh repo view … --json description` returns the approved two-mod text |
| In-game: presentation gone, 11 call sites resolve | **NOT RUN** — needs the game plus RED4ext and TweakXL |
| In-game: `tweakxl.log` shows no rejected property | **NOT RUN** — same gate |
| TweakXL array-clear and tag-drop semantics | **NOT CONFIRMED IN GAME** — resolved from the modding docs and WolvenKit's record definition, but never observed at runtime |
<!-- /ANCHOR:verification -->

---

<!-- ANCHOR:limitations -->
## Known Limitations

1. **The mod is packaged but never run in game.** Generation and structure are verified; runtime
   behaviour is not. Do not publish the Nexus page until the Phase 3 gates close.
2. **TweakXL may silently reject a property.** It applies a file even when one property inside it
   fails to bind, and reports the rejection only in `red4ext/logs/tweakxl.log`. Check that log on the
   first launch; a rejected property means the mod is only partly working.
3. **The scripted sickness beats stay.** V still glitches and hears the voicesets during the story
   scenes, because those are scene animation, not the status effect. Removing them is a quest-graph
   edit this mod does not make.
4. **Phantom Liberty's record is unverified.** `q304_songbird_relic_shock` is overridden, but PL was
   not installed on the development machine. On a base-only install TweakXL simply has nothing to
   override for that one record.
5. **`NoJohnnyReplacer` has an unverified build artifact and no page.** The archive builds
   (`dist/NoJohnnyReplacer-1.0.0-rc1.archive`; extract → serialize → patch → deserialize → pack
   proven 2026-10-11) but the keystone assumption is untested, so a page would still be a false
   claim. See `scratch/nexus-johnny.txt`.
6. **The in-game keystone check cannot run here.** The `replacer-scope.py` JSON round-trip now runs
   against quests extracted from the vanilla archives (2026-10-11); what cannot run on this machine
   is the game itself loading the packed archive to a Johnny scene.
7. **Licence and author handle are confirmed.** MIT with the author handle `928dk`, confirmed by the
   maintainer on 2026-10-11.
8. **The header image is a plain text banner.** `scratch/nexus-header-sickness.png` is drawn
   programmatically by `scratch/make-nexus-header.py` — not AI-generated art and containing no CDPR
   artwork, so no AI-content disclosure is needed for it.
<!-- /ANCHOR:limitations -->
