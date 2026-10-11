---
title: "Implementation Summary [template:examples/level_1/implementation-summary.md]"
description: "the merge bypass work. NOT YET WRITTEN - this document is a placeholder until"
trigger_phrases:
  - "implementation"
  - "summary"
  - "merge"
  - "bypass"
  - "cyberpunk"
importance_tier: "normal"
contextType: "general"
_memory:
  continuity:
    packet_pointer: "specs/001-bypass-v-johnny-merge"
    last_updated_at: "2026-10-03T00:00:00Z"
    last_updated_by: "big-pickle"
    recent_action: "still not implemented, but the merge trigger is now identified offline"
    next_safe_action: "replace this document with real content once Phase 3 produces a working mod"
    blockers:
      - "nothing implemented; document exists only to satisfy the level_1 file contract"
    key_files:
      - "$PROJECT/.opencode/specs/001-bypass-v-johnny-merge/tasks.md"
      - "$PROJECT/docs/Todo.md"
    session_dedup:
      fingerprint: "sha256:40d853f17c5be9d7cb76c8b70185da230e0e73e551213051492f3c17a97241dc"
      session_id: "001-bypass-v-johnny-merge"
      parent_session_id: null
    completion_pct: 70
---
# Implementation Summary

<!-- SPECKIT_LEVEL: 1 -->
<!-- SPECKIT_TEMPLATE_SOURCE: impl-summary-core | v2.2 -->

<!-- STATUS: IMPLEMENTED AS BUILD-ONLY. The Design A toolchain is complete and the archive
builds from the vanilla game archives (2026-10-11). Nothing has been installed or run in game:
the keystone assumption and the packed-archive load are unverified. -->

---

<!-- ANCHOR:metadata -->
## Metadata

| Field | Value |
|-------|-------|
| **Spec Folder** | 001-bypass-v-johnny-merge |
| **Completed** | — |
| **Level** | 1 |


<!-- /ANCHOR:metadata -->
---

<!-- ANCHOR:what-built -->
## What Was Built

The research record (`findings/` + `research/`) and the Design A toolchain are complete; the release
candidate archive builds from the vanilla game archives. Nothing has been installed or run in game.

| File | Action | Purpose |
|------|--------|---------|
| `spec.md`, `plan.md`, `tasks.md` | Created | Requirements, gates, T001-T033 |
| `findings/00-08-*.md`, `research/` | Created | Repo survey, merge mechanic, node hunt, scene-actor scope, relic split |
| `research/replacer-manifest.txt` | Created | Frozen ship set: 16 files, 27 nodes to disable |
| `tools/replacer-scope.py` | Created | manifest / patch / verify over quest JSON |
| `tools/build-johnny-archive.sh` | Created | extract → serialize → patch → verify → deserialize → pack |
| `src/cp2077-merge-bypass/README.txt` | Created | Source note for the mod |

### Files Changed (mod code)

No game files are patched in-repo; the intervention is produced at build time from the vanilla
archives into `dist/NoJohnnyReplacer-<version>.archive` (2026-10-11: `1.0.0-rc1`, 16 questphases,
28 `questReplacer_NodeType` nodes disabled).


<!-- /ANCHOR:what-built -->
---

<!-- ANCHOR:how-delivered -->
## How It Was Delivered

Design A was delivered as a **build pipeline, not an installed mod**, because nothing on this
machine may be shipped as "done" before it has been run. The chain:

1. The decisive finding landed 2026-10-04: `findings/04-quest-node-hunt-results.md` located the
   actual trigger — `questReplacer_NodeType` nodes with a `#johnny_replacer` cutscene target. The
   systemic setter hunt (`merge-symbol-scan.py`, 11,246 classes) had already shown there is no
   script setter for possession, so the quest-graph edit became the only buildable path.
2. The recorded claim "WolvenKit is source-only with no proven CLI round-trip" was wrong. A
   complete `WolvenKit.CLI` `net10.0` build exists on this machine (2026-10-04) and runs under
   `~/.dotnet/dotnet` once `DOTNET_ROOT` is set. It provides `unbundle`, `convert
   serialize/deserialize` and `pack`.
3. 2026-10-11 the full round-trip was proven end to end: extract → serialize → patch → verify →
   deserialize → pack, with two real bugs found and fixed on the way:
   - `replacer-scope.py` emitted CBool as `{"$type":"Bool","$value":…}`; WolvenKit's deserializer
     requires the bare integer it itself emits (`Cannot get the value of a token type
     'StartObject' as a number`). Fixed to emit `0`.
   - `verify` demanded a non-empty tier-2/3 set even when the scanned corpus has none; made the
     intact check vacuous-pass for ship-set-only corpora.
4. The result is `dist/NoJohnnyReplacer-1.0.0-rc1.archive` (144 KB, 16 entries), which round-trips
   (unpack → 16/16). Install = copy to `<CP2077>/archive/pc/mod/`. **It has not been run in
   game.**


<!-- /ANCHOR:how-delivered -->
---

<!-- ANCHOR:decisions -->
## Key Decisions

| Decision | Rationale |
|----------|-----------|
| Research-first, no mod code until the trigger is located | The merge may be enforced in compiled engine code with no script hook. Writing a prototype before knowing this risks building on an unusable layer. **Paid off**: the trigger was found by scanning compiled game data, which needed no game launch and no save editing. |
| Prefer CET (Lua) over Redscript over archive edits | No archive repacking, instant reload, easy to bisect which intervention actually mattered |
| Path B (alternative resolution) kept as a first-class path, not a consolation prize | The user raised it explicitly. The game already ships `sb_johnny_disappear` and a `q302_06_johnny_disappear` fact, so a "remove Johnny instead of merging him" resolution may reuse existing machinery |
| Phantom Liberty excluded from scope | Explicit user decision. Recorded as a constraint: PL must not *break*, but must not be worked on |
| Baseline saves chosen from 2022 rather than the current playthrough | The Oct 2026 playthrough has not reached the merge. The Oct 2022 playthrough has both pre-Heist and post-Heist saves from the same playthrough, same day — the tightest available diff pair |


<!-- /ANCHOR:decisions -->
---

<!-- ANCHOR:verification -->
## Verification

| Test Type | Status | Notes |
|-----------|--------|-------|
| Manual | Not started | Gate G1 (save load) and G2 (baseline run) pending — the game has never loaded this mod |
| Syntax | Pass | `bash -n` clean on every tool script; `py_compile` clean on `replacer-scope.py` |
| JSON round-trip | Pass | serialize → patch → verify → deserialize → re-serialize reproduces the patched nodes (`enable=0` on all 28) |
| Archive round-trip | Pass | `pack` produces a 16-entry archive; `unbundle` reads it back 16/16 |
| Keystone (runtime) | **Not started** | `enable=false` honoured at runtime is untested — everything rests on this |
| Spec validation | Pass | `validate.sh --strict` on the spec folder |


<!-- /ANCHOR:verification -->
---

<!-- ANCHOR:limitations -->
## Known Limitations

1. **The archive is built but unverified in game** — `tools/build-johnny-archive.sh` produces
   `dist/NoJohnnyReplacer-1.0.0-rc1.archive` from the vanilla archives (built 2026-10-11), but the
   keystone assumption (`enable=false` honoured at runtime) and the Kraken-packed buffers
   (no local Oodle lib, so WolvenKit packed with its fallback) have never been checked by a real
   launch
2. **Possession is proven script-readable, not script-writable** — the whole Path A design depends on
   this and it is unverified (task T018)
3. **Blocking possession may *remove* content** — `EvaluateApplyingReplacerGameplayRestrictions` and
   `GameplayRestriction.BlockAllHubMenu` / `BlockFastTravel` suggest gameplay is gated on it, so the
   fix could invert the user's original problem
4. **`Character.kurt_replacer` shares the mechanic** — a "replacer"-scoped fix would break Kurt's
   quest. Any intervention must be Johnny-specific
5. **`mq304` (Phantom Liberty) uses `JohnnyReplacerSequence`** — PL is explicitly out of scope but is
   the most likely regression site
6. **CET, Redscript and REDmod not installed in the game** — no prototyping surface yet
7. **Game archives not unpacked** — the caller that *sets* possession is still unknown
8. **Baseline saves are from Oct 2022** — unverified whether they load under the current patch

<!-- /ANCHOR:limitations -->

---