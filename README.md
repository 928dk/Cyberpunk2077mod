# Cyberpunk2077mod

Two independent Cyberpunk 2077 mods, plus the research and tooling behind them.

| Mod | What it does | State |
|---|---|---|
| **NoRelicSickness** | stops the Relic-sickness effect hurting V — no fullscreen overlay, no breathing camera, no SFX, no stamina penalty | packaged as a TweakXL drop-in; **not yet run in game** |
| **NoJohnnyReplacer** | keeps the Relic but disables the quest nodes that spawn Johnny | buildable archive (experimental); keystone assumption unverified |

**Nothing here has been verified in game yet.** Both mods are designed and one is packaged, but
neither has been loaded by the game. Read the status sections below before trusting a claim about
behaviour.

## Releases

| File | Contents |
|---|---|
| `dist/NoRelicSickness-1.0.0.zip` | `r6/tweaks/NoRelicSickness.yaml` + a readme. Requires RED4ext + TweakXL |
| `dist/NoJohnnyReplacer-1.0.0-rc1.archive` | 16 patched questphases for `archive/pc/mod/`. **Unverified in game** |

Built by `tools/build-nexus-zips.sh` (sickness) and `tools/build-johnny-archive.sh` (Johnny).
Install instructions for players are in `docs/INSTALL.md`; licence and permissions are in
`docs/Licence.md`.

---

## The idea

The obvious approach — discard the Relic — is wrong. The Relic is the story engine for everything
after Act 1: Takemura's job, Hanako, Arasaka Tower, Mr. Hands and all four endings.
`ep1_relic_intro_button` proves Phantom Liberty runs its own Relic intro, so a Relic-less path would
break PL.

The Relic and Johnny are **separate systems** joined at exactly one moment:

| | The Relic | Johnny |
|---|---|---|
| What | A device: perk trees, level, access | An engram riding it |
| Introduced by | `base_relic_intro_button` — a *scene* | `questReplacer_NodeType` — the *quest graph* |

So the requirement is: **keep the Relic, load no engram.**

See `.opencode/specs/001-bypass-v-johnny-merge/findings/06-relic-vs-johnny-separation.md`.

## The mechanism

```csharp
questReplacer_NodeType {
    Bool enable;      // set to false — that is the entire mod
    gameEntityReference objectRef;
    CName audioOverrideAppearanceName;
}
```

Disabling the node stops a braindance spawning Johnny. This means:

- no CET, no redscript, no runtime hook
- no game launch required to author it
- plain CR2W quest data, loaded as a REDmod override
- uninstall is `rm -rf` — nothing outside the mod directory is ever touched

## Scope

49 replacer nodes exist across 27 quest files. They are **not all Johnny**, and the mechanism is
shared with unrelated content, so the edit is classified into three tiers:

| Tier | Ref | Nodes | Files | Action |
|---|---|---|---|---|
| 1 | `#johnny_replacer` | 28 (27 enabled) | 16 | **disable** |
| 2 | `#bd_replacer` | 18 | 8 | **held** — symbol resolved by the braindance scene at load time, so the quest file cannot identify it |
| 3 | other | 2 | 2 | **never touch** — a mall NPC and an android display |

Tier 2 and 3 exist to stop a blanket edit from breaking Kurt's quest, V's VR intro, two Phantom
Liberty bosses and two side-quest braindances.

### What this does *not* remove

Johnny reaches the screen by two mechanisms, not one. This mod disables the first:

| | Mechanism | Count |
|---|---|---|
| A | quest-graph replacer (`#johnny_replacer`) | 28 nodes / 16 quest files |
| B | scene actor record `Character.Silverhand`, `acquisitionPlan = spawnDespawn` | **195 scenes** |
| A+B | scene actor bound to NodeRef `#johnny_replacer` | 12 scenes |

**Johnny still appears in scripted scenes after this mod is applied.** `sq032_00_sickness.scene`,
`johnny_default.scene`, `sq031_05_grave.scene` and `q110_13_alt_intro.scene` all spawn him
independently of any replacer node. That is a presentation layer, not a merge vector — V does not
merge because of it — but it is the honest boundary of the intervention, and removing it is a
separate job (`findings/08`, task T049).

The Relic sickness is likewise untouched by *this* mod: it is `sickness_on` + `sq032_tapeworm_stage` +
`sq032_sickness_stage` plus a status effect on the player, none of which involve a replacer. **V
still gets sick on the Relic timer.** `findings/07`, task T050.

That is deliberate, and it is a separate branch: `feature/suppress-relic-sickness`
(spec `002-suppress-relic-sickness`) removes the sickness by emptying the payload of the four
`BaseStatusEffect.JohnnySickness*` records at the TweakDB layer. Worth knowing: **vanilla cannot kill
V with the Relic** — the records carry a fullscreen VFX, a breathing camera, an SFX and a −2.5% to
−15% stamina penalty, and nothing else. The 5d→3d→2d12h→2d→1d12h→1d countdown is entirely Nexus mod
25974's addition, keyed off the `sickness_on` fact.

## Layout

```
.opencode/specs/001-bypass-v-johnny-merge/   spec, plan, tasks, findings/ (NoJohnnyReplacer)
.opencode/specs/002-suppress-relic-sickness/ spec for NoRelicSickness
.opencode/specs/003-nexus-release/           packaging + publishing for both
docs/       project docs, incl. Licence.md, Version.md, Changelog.md, INSTALL.md, Rollback.md
tools/      replacer-scope.py — manifest / patch / verify (Johnny)
            sickness-tweak.py — build / verify the TweakDB overrides (patch + TweakXL forms)
            build-nexus-zips.sh — build the NoRelicSickness release archives under dist/
            build-johnny-archive.sh — extract -> patch -> pack the NoJohnnyReplacer .archive
            cp2077-metadata-scan.py — savegame survey (read-only)
            merge-symbol-scan.py — engine symbol scan
            scene-actor-scan.py — which scenes put Johnny on screen
src/no-relic-sickness/  tweaks/NoRelicSickness.yaml (release), payload/ + install.sh (patch variant)
src/cp2077-merge-bypass/  NoJohnnyReplacer source (README.txt; artifact built to dist/ by tools/build-johnny-archive.sh)
research/   findings mirrored here, plus the baseline node manifests
PRIVACY.md  what was redacted before publication, and the checks that keep it clean
```

`src/no-relic-sickness/` ships as a **TweakXL drop-in** — the release is a single
`r6/tweaks/NoRelicSickness.yaml` and patches no game file. A source-patch variant (edit the shipped
TweakDB sources then REDmod-deploy) is kept for users without TweakXL; it exists because REDmod's
tweak compiler rejects a redeclared record while TweakXL overrides one cleanly. See its
[README](src/no-relic-sickness/README.md).

Third-party tooling (WolvenKit, modding docs, save editor) is **not** in this repo — upstream URLs
and re-clone commands are listed in `docs/SETUP.md`.

Game saves, extracted game archives and playthrough IDs are never committed. See `PRIVACY.md`.

## Usage

```bash
# build the NoJohnnyReplacer .archive from the vanilla game archives
# (extract -> serialize -> patch -> verify -> deserialize -> pack)
tools/build-johnny-archive.sh 1.0.0-rc1
#   -> dist/NoJohnnyReplacer-1.0.0-rc1.archive  (copy into <CP2077>/archive/pc/mod/)

# the JSON-level steps are also available individually:
python3 tools/replacer-scope.py manifest /path/to/extracted/quests        # report
python3 tools/replacer-scope.py patch  /path/to/extracted/quests --out DIR # patch
python3 tools/replacer-scope.py verify /path/to/extracted/quests --out DIR # prove delta
```

`verify` exits 0 only if every tier-1 node is disabled **and** no tier-2/3 file was touched.
The archive build needs `dotnet` + a WolvenKit.CLI `net10.0` build — see `docs/SETUP.md`.

NoRelicSickness is built the same way — both of its forms are generated, never hand-edited:

```bash
GAME="/path/to/Cyberpunk 2077"

# the release: TweakXL drop-in
python3 tools/sickness-tweak.py yaml \
  --vanilla-root "$GAME/tools/redmod/tweaks" \
  --out src/no-relic-sickness/tweaks/NoRelicSickness.yaml

# the source-patch variant
python3 tools/sickness-tweak.py build \
  --vanilla-root "$GAME/tools/redmod/tweaks" \
  --out-root src/no-relic-sickness/payload --diff

# package the release archives
tools/build-nexus-zips.sh --version 1.0.0
```

See `docs/Rollback.md` before applying anything. It was written before the first edit, as the spec
requires.

## Status

### NoRelicSickness

Generated from the shipped vanilla sources and structurally verified: `verify-yaml` confirms the
overlay covers exactly the six intended records, and the file parses as YAML.

| | |
|---|---|
| ✅ Built | `r6/tweaks/NoRelicSickness.yaml` — six record overrides |
| ✅ Built | `dist/NoRelicSickness-1.0.0.zip` |
| ⚠️ **Unverified** | **That the game loads it and the sickness presentation is actually gone** |
| ⚠️ **Unverified** | **That TweakXL does not silently reject a property** — check `red4ext/logs/tweakxl.log` |

### NoJohnnyReplacer

`validate.sh --strict` passes on the spec folder. Task state: **19 done / 29 open**.

| | |
|---|---|
| ✅ Settled | No redscript setter for possession exists (11,246 classes checked) |
| ✅ Settled | The Relic/Johnny split, and that discarding the Relic is not viable |
| ✅ Settled | Tier 1 scope: 27 nodes across 16 files |
| ✅ Built | `replacer-scope.py` — full CR2W round-trip proven (extract → serialize → patch → deserialize → pack) |
| ✅ Built | `dist/NoJohnnyReplacer-1.0.0-rc1.archive` — 16 questphases, 28 nodes disabled |
| ⚠️ **Unverified** | **That `enable = false` is honoured at runtime.** Everything rests on this. |
| ⚠️ **Unverified** | **That the packed archive loads in game** (WolvenKit packed with its Kraken fallback; no local Oodle lib) |

Two further unknowns are recorded in the spec's blocker list: whether braindance staging breaks
with an empty replacer slot, and whether ambient Johnny (`johnny_default_on`) survives.

Nothing here has been tested in game yet, and the mod has never been applied to a game install.

## Related

`~/projects/Client/Cyberpunk2077suppressJohnny/` — parked research for a follow-on project:
authoring a replacement quest for the plot threads Johnny was carrying. Start from its README; it
states what it inherits and what it must not assume.