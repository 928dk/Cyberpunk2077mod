---
title: "Implementation Plan: Suppress Relic Sickness [template:examples/level_1/plan.md]"
description: "planning required for NoRelicSickness. The plan is one TweakDB edit plus a deploy"
trigger_phrases:
  - "implementation"
  - "plan"
  - "relic"
  - "sickness"
  - "tweakdb"
importance_tier: "normal"
contextType: "general"
_memory:
  continuity:
    packet_pointer: "specs/002-suppress-relic-sickness"
    last_updated_at: "2026-10-10T00:00:00Z"
    last_updated_by: "big-pickle"
    recent_action: "install/uninstall round-trip verified; plan written"
    next_safe_action: "in-game check at a Relic stage, then merge the branch"
    blockers:
      - "Phantom Liberty half unverifiable without the DLC"
    key_files:
      - "$PROJECT/.opencode/specs/002-suppress-relic-sickness/spec.md"
      - "$PROJECT/.opencode/specs/002-suppress-relic-sickness/tasks.md"
      - "$PROJECT/src/no-relic-sickness/README.md"
    session_dedup:
      fingerprint: "sha256:9287db1d04302dca8e097c52b5eb4d57b3793480469da10c49193521fc403e92"
      session_id: "002-suppress-relic-sickness"
      parent_session_id: null
    completion_pct: 80
---
# Implementation Plan: Suppress Relic Sickness

<!-- SPECKIT_LEVEL: 1 -->
<!-- SPECKIT_TEMPLATE_SOURCE: plan-core | v2.2 -->

---

<!-- ANCHOR:summary -->
## 1. SUMMARY

### Technical Context

The sickness lives in TweakDB, not in quest data. `BaseStatusEffect.JohnnySickness{Low,Medium,Heavy}`
each carry exactly four things: a `StatusEffectFX` entry, a `BreathingAnimationEffector`, an
`SFXEffector`, and one `ConstantStatModifier` on `BaseStats.StaminaRegenRate`. Nothing else. The
quest layer only ever does
`questCharacterManagerParameters_SetStatusEffect` with `isPlayer = 1`.

That shape is what makes this cheap: strip the payload at the record and all 11 call sites go quiet
at once, with no graph edits and no risk of stranding a phase.

### Approach

Empty `VFX[]` and `packages[]` on the four concrete records, drop the `CameraAnimation` tag from the
shared abstract, and do the same to `q304_songbird_relic_shock` in the Phantom Liberty tree. Keep
every record and every inheritance edge. Generate the result from the shipped sources rather than
hand-writing it.

The one genuinely hard-won fact: **REDmod cannot override an existing TweakDB record.** Its tweak
compiler merges the base tree and every mod's `tweaks/` tree into one flat compile and rejects a
redeclared group. So the patch goes onto the shipped sources under `tools/redmod/tweaks/`, with a
marker mod alongside purely because `redMod.exe deploy` refuses to run with zero mods deployed.


<!-- /ANCHOR:summary -->
---

<!-- ANCHOR:quality-gates -->
## 2. QUALITY GATES

1. `python3 -m py_compile tools/sickness-tweak.py`
2. `sickness-tweak.py verify` passes against the shipped sources
3. `verify` **fails** on a pristine tree, on a dropped record, and on a changed parent — the
   negative controls are part of the gate, not optional
4. `bash -n` on `install.sh` and `uninstall.sh`
5. `redMod.exe deploy` exits 0 with no validation errors
6. The compiled `tweakdb.bin` shows the ten Relic VFX/SFX tokens at 0, against a deploy made from
   unmodified sources where they are present
7. `uninstall.sh` restores both files to their original md5 and the database returns to vanilla


<!-- /ANCHOR:quality-gates -->
---

<!-- ANCHOR:architecture -->
## 3. ARCHITECTURE

### High-Level Design

```
CDPR's johnny_sickness.tweak  ──┐
CDPR's ep1 quest_custom.tweak ─┤──> redMod.exe deploy ──> r6/cache/modded/tweakdb.bin
                                │        (edited in place)
NoRelicSickness/info.json ─────┘        marker mod, keeps deploy from being a no-op
```

### Component Strategy

| Component | Why this layer |
|-----------|----------------|
| TweakDB, not quest data | One edit reaches all 11 call sites; no graph surgery, no phase left stranded |
| Records kept, payload emptied | Removing a record breaks every `fk<>` link to it; emptying keeps resolution intact |
| Helper records carried through | `SFXEffector` and `JohnnySicknessUI` are linked from `tech_new_perks.tweak` and ep1 `quest_custom.tweak` |
| Generated, not hand-written | CDPR renames a field, the rule stops matching, and a hand-maintained copy ships a silent no-op |
| Two files, discovered by diffing | `q304_songbird_relic_shock` inherited the abstract but defined its own payload; only the deployed-database diff exposed it |


<!-- /ANCHOR:architecture -->
---

<!-- ANCHOR:phases -->
## 4. IMPLEMENTATION PHASES

### Phase 1: Establish the mechanism (done)
Read the shipped TweakDB sources. Established that the sickness is four records with a four-part
payload, that vanilla cannot kill V with it, and that the death ladder is mod 25974's.

### Phase 2: Probe the deployment route (done)
Ran `redMod.exe deploy` under wine. Confirmed TweakDB compilation is a native deploy stage, that
mod tweaks are discovered automatically, that a mod needs an `info.json`, and — by failure — that
a redeclared record is rejected.

### Phase 3: Generate and gate (done)
Wrote `sickness-tweak.py` with `build` and `verify`. Two bugs found by the gates rather than by
inspection: helper records were dropped on the first pass, and the `package`/`using` prologue was
duplicated on the second.

### Phase 4: Verify against the compiled database (done)
Deployed twice — once from unmodified sources as a control, once patched — and diffed the compiled
binaries. All ten Relic VFX/SFX tokens drop to zero; breathing references drop by exactly the
number of records that referenced them; every record survives.

### Phase 5: Package (done)
`install.sh` backs up, patches, installs the marker mod and deploys. `uninstall.sh` restores and
recompiles. Round-trip tested: original md5s restored.

### Phase 6: In-game confirmation (open)
Needs a launch. Provoke a Relic beat, confirm no overlay and no camera breathing, and check stamina
regeneration is unaffected.


<!-- /ANCHOR:phases -->
---

<!-- ANCHOR:testing -->
## 5. TESTING STRATEGY

### Test Matrix

| # | Check | Expected | Result |
|---|-------|----------|--------|
| 1 | `verify` on generated payload | pass | pass |
| 2 | `verify` on pristine sources as override | fail | pass (fails correctly) |
| 3 | `verify` with a record removed | fail | pass (fails correctly) |
| 4 | `verify` with a parent changed | fail | pass (fails correctly) |
| 5 | `deploy` from unmodified sources | success | success |
| 6 | `deploy` from patched sources | success | success |
| 7 | Relic VFX/SFX tokens in compiled db | 0 | 0 (were 1–2 each) |
| 8 | `CameraBreathing*` references | drop by record count | Low −1, Medium −2, Sick −1, Heavy 0 |
| 9 | Records still present | yes | yes |
| 10 | `uninstall.sh` round trip | original md5 | original md5 |
| 11 | In-game overlay absent | — | **not run** |

### Manual Verification
Load a save at tapeworm stage ≥ 3, let a sickness beat trigger, and confirm the screen is clean and
the camera does not breathe. Compare stamina regeneration before and after.


<!-- /ANCHOR:testing -->
---

<!-- ANCHOR:dependencies -->
## 6. DEPENDENCIES

### External
- Cyberpunk 2077 with REDmod (Steam app 2060310) — provides both the shipped tweak sources and the
  TweakDB compiler
- `wine` on Linux; Cyberpunk 2077 already runs under Proton
- Phantom Liberty for the `q304_songbird_relic_shock` half to be exercised in play

### Internal
- `tools/sickness-tweak.py` — build and verify
- `src/no-relic-sickness/payload/` — generated output, committed
- spec 001 `findings/07-relic-sickness-progression.md` — the evidence this rests on


<!-- /ANCHOR:dependencies -->
---

<!-- ANCHOR:rollback -->
## 7. ROLLBACK PLAN

`./uninstall.sh "<game dir>"` restores both shipped sources from the backup taken at install time and
recompiles. If the backup is missing the script refuses rather than writing a guessed "restored"
file. Verified by round trip: both files returned to their original md5 and the Relic VFX tokens
returned to the compiled database.

Worst case: the backup is gone and the sources are patched. Recovery is to re-download REDmod, or
copy the two files from a clean install — both paths are named verbatim in the uninstaller's error
message.


<!-- /ANCHOR:rollback -->