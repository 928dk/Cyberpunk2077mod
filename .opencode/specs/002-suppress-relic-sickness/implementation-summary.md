---
title: "Implementation Summary [template:examples/level_1/implementation-summary.md]"
description: "NoRelicSickness is built and verified against the compiled database. Only the in-game"
trigger_phrases:
  - "implementation"
  - "summary"
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
    recent_action: "verified against the compiled tweakdb; awaiting in-game confirmation"
    next_safe_action: "T023 -- load a Relic-stage save and confirm no overlay"
    blockers:
      - "in-game check not yet run"
      - "Phantom Liberty not installed"
    key_files:
      - "$PROJECT/src/no-relic-sickness/README.md"
      - "$PROJECT/tools/sickness-tweak.py"
    session_dedup:
      fingerprint: "sha256:4e7b1c9a2d80f635a1b8e4c7d29f6013a5c8b2e74d190f36a2c5b8e7d4019f63"
      session_id: "002-suppress-relic-sickness"
      parent_session_id: null
    completion_pct: 92
---
# Implementation Summary: Suppress Relic Sickness

<!-- SPECKIT_LEVEL: 1 -->
<!-- SPECKIT_TEMPLATE_SOURCE: implementation-summary-core | v2.2 -->

---

<!-- ANCHOR:metadata -->
## 1. METADATA

| Field | Value |
|-------|-------|
| **Level** | 1 |
| **Status** | Built and verified offline; awaiting in-game confirmation |
| **Branch** | `feature/suppress-relic-sickness` |
| **Spec** | `002-suppress-relic-sickness` |
| **Mod** | `src/no-relic-sickness/` |
| **Verified** | 2026-10-10 |


<!-- /ANCHOR:metadata -->
---

<!-- ANCHOR:what-built -->
## 2. WHAT WAS BUILT

`NoRelicSickness` — the Relic stops hurting V. Two shipped TweakDB sources are patched so the
sickness records keep their identity and inheritance but lose their effect payload. An install script
backs up, applies and recompiles; an uninstall script reverses it exactly.

| | vanilla | with this |
|---|---|---|
| fullscreen glitch overlay | yes | no |
| camera breathing | yes | no |
| fullscreen SFX | yes | no |
| stamina regen penalty | −2.5% / −5% / −10% / −15% | none |
| the Relic, its quests, its scenes | yes | yes |


<!-- /ANCHOR:what-built -->
---

<!-- ANCHOR:how-delivered -->
## 3. HOW IT WAS DELIVERED

`redMod.exe deploy`, run under wine, compiles TweakDB natively — no TweakXL, no redscript, no CET.
Three things had to be true first, each established by running the deploy rather than by reading
about it:

**The override had to go onto the shipped sources.** REDmod merges the base tweak tree and every
mod's `tweaks/` tree into one flat compile and rejects a redeclared group:

```
Line 27: Duplicated group 'JohnnySicknessLow' in package 'BaseStatusEffect'
```

A REDmod can add TweakDB records but cannot override an existing one. Hence `install.sh` rather than
a drop-in folder.

**A marker mod had to exist.** `redMod.exe deploy` reports `No mods found, no deployment is needed!`
and does nothing, so without at least one deployed mod there would be no recompile and no
`r6/cache/modded/tweakdb.bin`. `mods/NoRelicSickness/info.json` is otherwise empty and exists purely
to make the deploy run.

**The payload is generated, not hand-written.** `tools/sickness-tweak.py` reads the shipped sources,
removes exactly the intended fields, and prints the diff. Every rule fails loudly — a missing field,
tag, record or parent is an error, never a silent pass.


<!-- /ANCHOR:how-delivered -->
---

<!-- ANCHOR:decisions -->
## 4. KEY DECISIONS

### Keep the records, empty the payload

Removing a record would break every `fk<>` link to it. Emptying `VFX[]` and `packages[]` keeps all 11
quest call sites resolving while making the effect a no-op — one edit instead of eleven, and no
quest graph is touched, so no phase can be left stranded.

### Patch two files, not one

`BaseStatusEffect.q304_songbird_relic_shock` — Phantom Liberty's relic shock — *inherits*
`JohnnySicknessAbstract` but redefines the entire payload itself, in a different file. Stripping only
`johnny_sickness.tweak` left it producing overlay, SFX and a −10% stamina penalty. It was visible
only in the compiled-database delta, never in the source. Six records across two files.

### Carry every record through verbatim

`SFXEffector` and `JohnnySicknessUI` live in the same file and are linked from
`tech_new_perks.tweak` and ep1 `quest_custom.tweak`. An earlier version of the generator emitted only
the five targeted records and compilation failed on both.

### Vanilla cannot kill V with the Relic

Reading the shipped TweakDB rather than the modding wikis: the records carry a VFX, a breathing
animation, an SFX and a stamina penalty. No health drain, no damage. The 5d→3d→2d12h→2d→1d12h→1d
ladder is entirely Nexus mod 25974's addition, keyed off `sickness_on`. This changed what the branch
was for.


<!-- /ANCHOR:decisions -->
---

<!-- ANCHOR:verification -->
## 5. VERIFICATION

| Gate | Result |
|---|---|
| `verify` on generated payload | pass |
| `verify` on pristine sources as its own override | fails (correct) |
| `verify` with a dropped record | fails (correct) |
| `verify` with a changed parent | fails (correct) |
| `deploy` exit code | 0, no validation errors |
| Relic VFX/SFX tokens, patched vs vanilla deploy | 0, vs 1–2 each |
| `CameraBreathing*` references | Low −1, Medium −2, Sick −1, Heavy 0 |
| Records present after patch | yes, all six |
| `uninstall.sh` round trip | original md5 restored |
| In-game | **not run** |

### The first check was vacuous, and the control caught it

Checking the compiled `tweakdb.str` for the effect strings returned zero — for the patched *and* the
unpatched deploy, because those strings are not present in that file form at all. A clean result from
a bad method is worse than an error.

The real proof came from deploying twice and diffing the compiled `.bin`. All ten
`vfx_fullscreen_johnny_sickness_*` tokens drop to 0, and each `CameraBreathing*` reference drops by
exactly the number of records that referenced it — `CameraBreathingHeavy` by 0, because these records
never used it. That accounting is what distinguishes a real delta from noise.

### Two bugs the gates caught

- The generator dropped `SFXEffector` and `JohnnySicknessUI`, breaking compilation in two unrelated
  files. It now carries every record through verbatim and `verify` fails on any dropped record.
- The `package`/`using` prologue was emitted twice: `Expected end of file but got: 'package'`.


<!-- /ANCHOR:verification -->
---

<!-- ANCHOR:limitations -->
## 6. KNOWN LIMITATIONS

- **No in-game confirmation.** Everything above is offline verification against the compiled
  database. T023–T026 remain.
- **Phantom Liberty is untested in play.** The DLC is not installed, so the `q304_songbird_relic_shock`
  half is compile-verified only.
- **The scripted beats remain.** `sq032.quest` plays the sickness scene ten times and
  `sq032_sickness.questphase` once, so V still visibly glitches and hears voicesets. That is a
  quest-graph edit, and the user scoped it out of this branch.
- **Nexus mod 25974 still kills V on schedule.** This patch does not touch `sickness_on`. The two are
  otherwise compatible — 25974 ships quest and scene overrides and no TweakDB, so there is no
  collision.
- **Johnny is untouched.** That is spec 001's `NoJohnnyReplacer`, on `master`.
- **Not a distributable mod.** Patching the shipped sources is the only route REDmod offers without
  adding a redscript dependency. A TweakXL build would be a true drop-in, at the cost spec 001
  explicitly avoids.
- **Load order.** Another TweakDB mod re-adding these records wins or loses by load order.


<!-- /ANCHOR:limitations -->

## 7. BRANCH LAYOUT

`master` is spec 001, unchanged. This branch is spec 002. The two touch disjoint files — 16 quest
files versus 2 TweakDB sources — so they merge without conflict. A third direction,
`feature/scene-actor-johnny` (spec 001, T049), would touch ~195 `.scene` files and is also disjoint.