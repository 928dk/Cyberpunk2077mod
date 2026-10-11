---
title: "Tasks: Publish the Cyberpunk 2077 mods to Nexus Mods as two separate mod pages [template:level_2/tasks.md]"
description: "Task Format: T### [P?] Description (file path)"
trigger_phrases:
  - "tasks"
  - "nexus"
  - "tweakxl"
  - "redmod"
  - "release"
importance_tier: "normal"
contextType: "general"
_memory:
  continuity:
    packet_pointer: "specs/003-nexus-release"
    last_updated_at: "2026-10-10T12:00:00Z"
    last_updated_by: "big-pickle"
    recent_action: "Phase 1 + Phase 2 (except in-game) executed: docs, licence, TweakXL overlay, release zip"
    next_safe_action: "Run the Phase 3 objective gates, then the in-game checks once RED4ext+TweakXL are installed"
    blockers:
      - "Johnny keystone assumption unverified (T024)"
      - "WolvenKit serialize/pack round-trip not demonstrated (T021/T022)"
      - "TweakXL application unverified in game (T012/T015)"
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
<!-- SPECKIT_TEMPLATE_SOURCE: tasks-core | v2.2 -->
# Tasks: Publish the Cyberpunk 2077 mods to Nexus Mods as two separate mod pages

<!-- SPECKIT_LEVEL: 2 -->

---

<!-- ANCHOR:notation -->
## Task Notation

| Prefix | Meaning |
|--------|---------|
| `[ ]` | Pending |
| `[x]` | Completed |
| `[P]` | Parallelizable |
| `[B]` | Blocked |

**Task Format**: `T### [P?] Description (file path)`
<!-- /ANCHOR:notation -->

---

<!-- ANCHOR:phase-1 -->
## Phase 1: Setup

Release preparation: names, licence, versions, install docs and page copy.

- [x] T001 Lock display names and version strings for both mods (README.md, docs/Version.md) — evidence: `docs/Version.md` pins NoRelicSickness 1.0.0 and records NoJohnnyReplacer as unbuilt; root `README.md` leads with both.
- [x] T002 Replace the MIT template with a mod licence + permissions block (docs/Licence.md) — evidence: real holder, permissions table, MIT terms, game-data carve-out.
- [x] T003 Rewrite version history for both mods (docs/Version.md) — evidence: per-mod state plus the two unverified items.
- [x] T004 Add real release entries (docs/Changelog.md) — evidence: dated entries 2026-10-03/04, 2026-10-09/10, 2026-10-10.
- [x] T005 Rewrite install/uninstall for both formats (docs/INSTALL.md) — evidence: TweakXL drop-in, source-patch variant, Johnny marked unavailable.
- [x] T006 [P] Draft the NoRelicSickness Nexus description (scratch/nexus-sickness.txt) — evidence: BBCode draft with a TESTED-ON marker to fill.
- [x] T007 [P] NoJohnnyReplacer page copy deferred (scratch/nexus-johnny.txt) — evidence: file records why no page may be drafted until the artifact exists and the assumption is tested.
- [x] T008 Produce the 1920x1080 header image for the sickness page (scratch/) — evidence: `scratch/nexus-header-sickness.png` (1920x1080) drawn by `scratch/make-nexus-header.py`; a plain Pillow text banner, no AI-generated art and no CDPR artwork. Johnny needs one only if it is ever published.
- [x] T009 Fix the GitHub repo description to describe the mods (GitHub settings) — evidence: `gh repo view 928dk/Cyberpunk2077mod --json description` returns the approved two-mod text.
<!-- /ANCHOR:phase-1 -->

---

<!-- ANCHOR:phase-2 -->
## Phase 2: Implementation

Build both releases. The sickness overlay is generated and packaged; the Johnny archive cannot be
built until a WolvenKit serialize/pack round-trip is demonstrated.

- [x] T010 Enumerate the exact records and fields to override (src/no-relic-sickness/) — evidence: `TARGETS` names 6 records across 2 files.
- [x] T011 Emit the TweakXL overlay (src/no-relic-sickness/tweaks/NoRelicSickness.yaml) — evidence: `yaml` and `verify-yaml` both report OK; 6 record overrides.
- [x] T013 Build the release archive (tools/build-nexus-zips.sh) — evidence: `dist/NoRelicSickness-1.0.0.zip` holds `r6/tweaks/NoRelicSickness.yaml` + `README.txt`.
- [x] T014 Update the sickness README to lead with TweakXL (src/no-relic-sickness/README.md) — evidence: release-format section plus the first-launch `tweakxl.log` check.
- [ ] T020 [B] Extract the 16 tier-1 quest resources (scratch/) — WolvenKit round-trip missing.
- [ ] T021 [B] Flip enable=false and serialize the resources (tools/replacer-scope.py + WolvenKit) — round-trip missing.
- [ ] T022 [B] Pack the REDmod archive (src/cp2077-merge-bypass/) — no archive exists.
- [ ] T023 [B] Add info.json and dist layout for Johnny (tools/build-nexus-zips.sh) — blocked on T022.
<!-- /ANCHOR:phase-2 -->

---

<!-- ANCHOR:phase-3 -->
## Phase 3: Verification

Objective gates run without a game; the `[B]` items need the game plus RED4ext + TweakXL.

- [x] T035 Run validate.sh --strict on this spec folder — evidence: PASSED, 0 errors / 0 warnings (2026-10-11).
- [x] T030 Privacy sweep of dist/ and the page copy (see PRIVACY.md) — evidence: 13 identifier hits all sha256 fingerprints; 0 absolute home paths; 0 tracked save files; `dist/` and `.backup/` git-ignored.
- [ ] T012 [B] Confirm TweakXL applies the array clears and the dropped tag (game) — read `red4ext/logs/tweakxl.log`.
- [ ] T015 [B] Verify in game: presentation gone, all 11 call sites resolve.
- [ ] T024 [B] Verify the Johnny keystone assumption in game.
- [ ] T025 [B] Verify SC-002/SC-003: no merge, districts reachable, no softlock.
<!-- /ANCHOR:phase-3 -->

---

<!-- ANCHOR:phase-4 -->
## Phase 4: Publish

- [ ] T031 Create the NoRelicSickness page and upload file 1 (Nexus web).
- [ ] T032 [B] Create the NoJohnnyReplacer page and upload file 1 (Nexus web) — blocked until Phase 3 passes for Johnny.
- [ ] T033 Capture mod_id/file_id; store the API key; add the upload workflow (.github/workflows/).
- [ ] T034 Cross-link the GitHub README and both Nexus pages.
<!-- /ANCHOR:phase-4 -->

---

<!-- ANCHOR:completion -->
## Completion Criteria

- [ ] All tasks marked `[x]`
- [ ] No `[B]` blocked tasks remaining
- [ ] Manual verification passed
<!-- /ANCHOR:completion -->

---

<!-- ANCHOR:cross-refs -->
## Cross-References

- **Specification**: See `spec.md`
- **Plan**: See `plan.md`
- **Sibling specs**: `001-bypass-v-johnny-merge`, `002-suppress-relic-sickness`
<!-- /ANCHOR:cross-refs -->
