# Versions

Two independent mods live in this repository. They have separate release lines and are published as
separate Nexus Mods pages.

| Mod | Version | State |
| --- | --- | --- |
| **NoRelicSickness** | 1.0.0 | Packaged and structurally verified. **Not yet run in game.** |
| **NoJohnnyReplacer** | — | Not built. No archive exists. |
| repo tooling (`tools/`) | — | Unversioned scripts, tracked on `master`. |

---

## NoRelicSickness 1.0.0

| | |
| --- | --- |
| Release date | pending the first Nexus upload |
| Format | TweakXL drop-in — `r6/tweaks/NoRelicSickness.yaml` |
| Requires | RED4ext and TweakXL |
| Archive | `dist/NoRelicSickness-1.0.0.zip` (built by `tools/build-nexus-zips.sh`) |
| Spec | `.opencode/specs/002-suppress-relic-sickness/` |

What it does: overrides six shipped status-effect records so the Relic stops hurting V — no
fullscreen overlay, no camera-breathing animation, no fullscreen SFX, no stamina-regen penalty. The
Relic, its quests and its scenes are untouched.

### Not verified

The overlay has passed generation and structural checks and parses as YAML. It has never been loaded
by the game. Two things are therefore still unproven:

1. That TweakXL applies all three overridden properties and does not silently reject one. TweakXL
   drops a property it cannot bind **without an in-game warning**, so the first launch must be
   checked against `red4ext/logs/tweakxl.log`.
2. That the in-game result matches the table in the mod README.

Until both are recorded in `implementation-summary.md`, this is *release-ready* but not *released*.

---

## NoJohnnyReplacer

No build artifact exists. The intervention is designed and its scope is fixed (27 `enable` flips
across 16 `#johnny_replacer` quest files), and `tools/replacer-scope.py` emits and verifies the
patched quest JSON — but nothing has serialized that JSON back into `.quest`/`.questphase` resources,
and the keystone assumption (that `questReplacer_NodeType.enable = false` is honoured at runtime) has
never been tested. See `.opencode/specs/001-bypass-v-johnny-merge/`.

It will not get a public page until the assumption is tested in game.

---

## Repository tooling

| Script | Role |
| --- | --- |
| `tools/sickness-tweak.py` | Builds and verifies the Relic-sickness overrides; emits both the patch and TweakXL forms |
| `tools/replacer-scope.py` | Manifest / patch / verify for the Johnny quest nodes |
| `tools/scene-actor-scan.py` | Finds which scenes put Johnny on screen independently of a replacer |
| `tools/cp2077-metadata-scan.py` | Read-only savegame survey |
| `tools/merge-symbol-scan.py` | Engine symbol scan |
| `tools/build-nexus-zips.sh` | Builds the release archives under `dist/` |

See [Changelog.md](Changelog.md) for the history of each.
