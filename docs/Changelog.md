# Changelog

Newest first. Dates are the day the work landed on `master`, not the day it was planned.

## [Unreleased]

### Added
- Real mod licence and permissions (replaces the project-template MIT stub) — `docs/Licence.md`.
- Version and install documentation for both mods — `docs/Version.md`, `docs/INSTALL.md`.
- `tools/build-nexus-zips.sh` — builds the release archives under `dist/`.

## 2026-10-10 — Relic sickness as a TweakXL drop-in

Spec `.opencode/specs/003-nexus-release/`.

### Added
- `tools/sickness-tweak.py` gained a `yaml` mode and a `verify-yaml` mode. The overlay is generated
  from the shipped vanilla sources, so a CDPR rename fails the build instead of shipping a YAML that
  TweakXL would silently reject.
- `src/no-relic-sickness/tweaks/NoRelicSickness.yaml` — six record overrides: the `CameraAnimation`
  tag dropped from the shared abstract, and `VFX[]` / `packages[]` cleared on each concrete record.
- `src/no-relic-sickness/RELEASE.txt` — the readme shipped inside the archive.

### Changed
- The Nexus release path is now the TweakXL drop-in, which needs RED4ext + TweakXL and patches no
  game file. The 002 source-patch plus `install.sh` stays in the tree for users without TweakXL and
  is no longer the release artifact.

### Fixed
- `docs/Licence.md`, `docs/Version.md`, `docs/Changelog.md` and `docs/INSTALL.md` no longer carry
  project-template placeholder text (`YYYY Your Name`, `pip install -r requirements.txt`, and a
  version file that claimed no mod code existed).

## 2026-10-09/10 — Relic sickness implemented, Johnny scope closed

Spec `.opencode/specs/002-suppress-relic-sickness/`.

### Added
- `NoRelicSickness`: the Relic-sickness status effect is neutralised at the TweakDB layer by emptying
  the payload of `JohnnySicknessLow/Medium/MediumQuest/Heavy` and Phantom Liberty's
  `q304_songbird_relic_shock`, and dropping the `CameraAnimation` tag from `JohnnySicknessAbstract`.
  Every record and inheritance edge is kept, so all 11 quest call sites still resolve.
- `tools/sickness-tweak.py` — generates the payload and verifies the invariants; fails loudly if a
  targeted field is missing, a parent changed, or a record came out identical to vanilla.
- `tools/scene-actor-scan.py` plus `research/08-johnny-scene-actor-scope.md` — established that Johnny
  reaches the screen through 195 scripted scenes independently of any replacer node.

### Notes
- Filed the honest limits of `NoJohnnyReplacer`: disabling replacer nodes does not remove Johnny from
  scripted scenes, and does not remove the Relic sickness.
- REDmod's tweak compiler rejects a redeclared record, which is why 002 shipped as a patch. TweakXL
  has no such restriction; that is why 003 repackages it.

## 2026-10-03/04 — Project scaffold and first research

Spec `.opencode/specs/001-bypass-v-johnny-merge/`.

### Added
- Initial scaffold from `~/projects/project-template`.
- Trigger survey and savegame survey; baseline saves picked.
- The Relic/Johnny separation finding (`06-relic-vs-johnny-separation.md`) and the Relic-sickness
  progression finding (`07-relic-sickness-progression.md`).
- `tools/replacer-scope.py`, `tools/cp2077-metadata-scan.py`, `tools/merge-symbol-scan.py`.
- `PRIVACY.md` and the redaction pass over the tree ahead of making the repo public.

---

See [Version.md](Version.md) for the current state of each mod.
