---
title: "Verification Checklist: Publish the Cyberpunk 2077 mods to Nexus Mods as two separate mod pages [template:level_2/checklist.md]"
description: "Verification Date: 2026-10-11"
trigger_phrases:
  - "verification"
  - "checklist"
  - "nexus"
  - "release"
importance_tier: "normal"
contextType: "general"
_memory:
  continuity:
    packet_pointer: "specs/003-nexus-release"
    last_updated_at: "2026-10-10T12:00:00Z"
    last_updated_by: "big-pickle"
    recent_action: "Checklist filled with evidence after the Phase 1/2 work; validate.sh PASSED"
    next_safe_action: "Close the in-game gates once RED4ext + TweakXL are installed"
    blockers:
      - "In-game testing needs the game + RED4ext + TweakXL"
      - "replacer-scope verify needs an extracted vanilla quest tree"
    key_files:
      - "$PROJECT/tools/sickness-tweak.py"
      - "$PROJECT/tools/build-nexus-zips.sh"
    session_dedup:
      fingerprint: "sha256:5b8e0f9a3f7c4d21a6b3e8c0d9f2a1b4c7e6d5f8a9b0c1d2e3f4a5b6c7d8e9f0"
      session_id: "003-nexus-release"
      parent_session_id: null
    completion_pct: 56
    open_questions: []
    answered_questions: []
---
<!-- SPECKIT_TEMPLATE_SOURCE: checklist | v2.2 -->
# Verification Checklist: Publish the Cyberpunk 2077 mods to Nexus Mods as two separate mod pages

<!-- SPECKIT_LEVEL: 2 -->

---

<!-- ANCHOR:protocol -->
## Verification Protocol

| Priority | Handling | Completion Impact |
|----------|----------|-------------------|
| **[P0]** | HARD BLOCKER | Cannot claim done until complete |
| **[P1]** | Required | Must complete OR get user approval |
| **[P2]** | Optional | Can defer with documented reason |
<!-- /ANCHOR:protocol -->

---

<!-- ANCHOR:pre-impl -->
## Pre-Implementation

- [x] CHK-001 [P0] Requirements documented in spec.md — evidence: spec.md §4 REQ-001…REQ-008.
- [x] CHK-002 [P0] Technical approach defined in plan.md — evidence: plan.md §3 Architecture and §4 Implementation Phases.
- [ ] CHK-003 [P1] Dependencies identified and available (RED4ext, TweakXL, REDmod, WolvenKit) — REDmod present; **RED4ext and TweakXL are not installed**, so TweakXL application cannot be exercised here; WolvenKit is a source checkout only. All four are named in docs/INSTALL.md.
<!-- /ANCHOR:pre-impl -->

---

<!-- ANCHOR:code-quality -->
## Code Quality

- [ ] CHK-010 [P0] `sickness-tweak.py verify` and `replacer-scope.py verify` pass (exit 0) — `sickness-tweak.py verify` and `verify-yaml` both exit 0. `replacer-scope.py verify` is not runnable here: it needs an extracted vanilla quest tree, which is not on this machine. Deferred with T020–T025.
- [x] CHK-011 [P0] Build scripts fail loudly on a missing/renamed record (no silent no-op) — evidence: pointing `yaml` at an already-patched source raised `tag 'CameraAnimation' absent ... review before shipping` and exited 1; `verify-yaml` fails on a missing record or a surviving tag.
- [x] CHK-012 [P1] TweakXL YAML and archive contents match the verified payload exactly — evidence: `./tools/build-nexus-zips.sh --check` regenerates the overlay from the vanilla sources, re-runs `verify-yaml`, parses the YAML with PyYAML, then packages that exact file.
- [x] CHK-013 [P1] Release archives contain only changed resources (no base game data) — evidence: `unzip -l` shows only `r6/tweaks/NoRelicSickness.yaml` and `README.txt`.
<!-- /ANCHOR:code-quality -->

---

<!-- ANCHOR:testing -->
## Testing

- [ ] CHK-020 [P0] In-game: NoRelicSickness removes overlay/breathing/SFX/stamina penalty
- [ ] CHK-021 [P0] In-game: NoJohnnyReplacer prevents the merge and does not softlock the arc
- [ ] CHK-022 [P1] Uninstall both: vanilla behaviour, no archive repair
- [ ] CHK-023 [P1] Load-order conflict with another quest mod documented
<!-- /ANCHOR:testing -->

---

<!-- ANCHOR:fix-completeness -->
## Fix Completeness

- [x] CHK-FIX-001 [P0] Each finding classified (instance-only / class-of-bug / cross-consumer) — evidence: the finding is a class, not an instance — every status effect in the `JohnnySickness*` family carries the same payload shape, so the fix covers the family rather than one record.
- [x] CHK-FIX-002 [P0] Same-class producer inventory done for the changed records — evidence: all 6 producers enumerated (the shared abstract plus 5 concrete records) across both the base and `ep1` files; listed in src/no-relic-sickness/README.md.
- [x] CHK-FIX-003 [P0] Consumer inventory done for the affected quest call sites — evidence: 11 consumers identified — ten scene nodes in `sq032.quest` plus one in `sq032_sickness.questphase` — and each still resolves because every record and inheritance edge is kept.
- [x] CHK-FIX-004 [P0] Adversarial cases covered: missing record, renamed field, absent DLC — evidence: a missing/renamed field raises `SystemExit` in `build_yaml`; the absent-DLC case is documented (the `ep1` record is simply not present on a base-only install).
- [x] CHK-FIX-005 [P1] Matrix axes (base/ep1 × record × field) listed before completion — evidence: the base/ep1 source split is `TARGETS`'s two keys and the record × field product is the README table.
<!-- /ANCHOR:fix-completeness -->

---

<!-- ANCHOR:security -->
## Security

- [x] CHK-030 [P0] No secrets/tokens in the repo or release archives — evidence: privacy sweep 2026-10-11 found no credentials; the archive holds only the YAML and a readme.
- [x] CHK-031 [P0] No personal identifiers in dist/ or page copy (privacy sweep clean) — evidence: 13 identifier hits, all spec-kit `sha256` fingerprints; 0 absolute home paths; 0 save files.
- [ ] CHK-032 [P1] Nexus API key stored outside the repo — no key exists yet; must be captured at T033 and kept out of the tree.
<!-- /ANCHOR:security -->

---

<!-- ANCHOR:docs -->
## Documentation

- [x] CHK-040 [P1] spec/plan/tasks synchronized — evidence: `validate.sh --strict` PASSED, 0 errors / 0 warnings; tasks.md phases renamed to the template's Setup/Implementation/Verification names.
- [x] CHK-041 [P1] README and INSTALL describe the shipped formats, not the old ones — evidence: both lead with the TweakXL drop-in and mark the source-patch variant as repo-only.
- [x] CHK-042 [P2] Nexus page descriptions list honest limitations — evidence: scratch/nexus-sickness.txt has a "Known limitations" block (scripted beats, untested PL) and a compatibility block naming mod 25974.
<!-- /ANCHOR:docs -->

---

<!-- ANCHOR:file-org -->
## File Organization

- [x] CHK-050 [P1] Temp files live in scratch/ only — evidence: the two page drafts and the regenerated scratch output live in `.opencode/specs/003-nexus-release/scratch/`.
- [x] CHK-051 [P1] dist/ is git-ignored and cleaned before completion — evidence: `git check-ignore -v dist/…zip` resolves to `.gitignore:13:dist/`; nothing under dist/ is tracked.
<!-- /ANCHOR:file-org -->

---

<!-- ANCHOR:summary -->
## Verification Summary

| Category | Total | Verified |
|----------|-------|----------|
| P0 Items | 12 | 9/12 |
| P1 Items | 11 | 7/11 |
| P2 Items | 1 | 1/1 |

Open: CHK-010 (replacer-scope verify unrunnable here), CHK-003/032 (deps, API key), and the four
in-game testing items — all gated on RED4ext + TweakXL and a playthrough that reaches the Relic arc.

**Verification Date**: 2026-10-11
<!-- /ANCHOR:summary -->
