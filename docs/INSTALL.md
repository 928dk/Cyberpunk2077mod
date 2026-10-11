# Installation

For players. If you are changing the mods rather than installing them, start at the repository
`README.md` and the spec folders instead.

There are two mods. **NoRelicSickness is available; NoJohnnyReplacer is an untested release
candidate** — see the last section.

---

## NoRelicSickness

Stops the Relic from hurting V. The Relic, its storyline and its scenes are unchanged.

### Requirements

| Requirement | Why |
| --- | --- |
| Cyberpunk 2077 | base game. The Phantom Liberty record is included and simply unused if you do not own the expansion |
| **RED4ext** | the mod-loader framework that lets the game read files from `r6/tweaks/` |
| **TweakXL** | the core mod that reads `r6/tweaks/*.yaml` and merges it into the game's TweakDB |

RED4ext and TweakXL are the two standard core mods for this kind of change. Install them first, using
their own instructions:

- RED4ext — https://github.com/WopsS/RED4ext
- TweakXL — https://github.com/psiberx/cp2077-tweak-xl

Install each one into the Cyberpunk 2077 directory exactly as its own readme says, and launch the
game once so that `red4ext/` and `red4ext/plugins/` are created.

### Install

Unzip the release into your Cyberpunk 2077 directory. You should end up with:

```
<Cyberpunk 2077>/r6/tweaks/NoRelicSickness.yaml
```

That is the entire mod. No game file is modified, so there is nothing to back up and no deploy step
to run. Vortex can install the archive directly; it deploys the same `r6/tweaks/` file.

### First launch — check that it loaded

TweakXL applies a file even when it rejects one property inside it, and it reports the rejection only
in its log. So the first launch is worth 30 seconds of checking. After launching the game once, open:

```
<Cyberpunk 2077>/red4ext/logs/tweakxl.log
```

and look for `NoRelicSickness.yaml`. If a line says a property was not applied, the mod is only
partly working — report it. If the game also has no `red4ext/` directory at all, RED4ext is not
installed and the mod will do nothing.

### Uninstall

Delete the file:

```
<Cyberpunk 2077>/r6/tweaks/NoRelicSickness.yaml
```

Nothing else was written, so nothing else has to be undone. Existing saves are unaffected either
way — this is a data overlay, not a save edit.

---

## NoRelicSickness — source-patch variant (repo only)

Not shipped as a release. It exists for users who cannot run TweakXL, and it is the only reason the
`payload/` and `install.sh` files are still in the tree. It edits two of the game's own shipped
TweakDB sources and then recompiles them.

```bash
src/no-relic-sickness/install.sh "/path/to/Cyberpunk 2077"    # backs up, patches, deploys
src/no-relic-sickness/uninstall.sh "/path/to/Cyberpunk 2077"  # restores the originals
```

Requirements: **REDmod** (Steam app 2060310) and, on Linux, `wine` — `redMod.exe` is a Windows binary
and the game runs through Proton. Use this variant **or** the TweakXL drop-in, not both.

---

## NoJohnnyReplacer

Experimental. An archive exists (`dist/NoJohnnyReplacer-1.0.0-rc1.archive`), but nothing has been
**run in game** — treat it as a release candidate, not a release.

Install (for testing):

1. Copy `dist/NoJohnnyReplacer-1.0.0-rc1.archive` into `<Cyberpunk 2077>/archive/pc/mod/`.
2. Launch the game, load a save that reaches the Relic arc, and check whether Johnny still appears
   in his braindance scenes (q101 / q108 / q116 / q204).
3. To uninstall, remove the file — nothing else is touched.

The archive disables 27 `questReplacer_NodeType` nodes across 16 quest files.

Still missing:

1. **In-game proof.** That flipping `enable` to `false` is honoured at runtime has never been
   checked by a real launch — the keystone assumption of the whole design.
2. **Oodle-verified packaging.** The build packs with WolvenKit's Kraken fallback (no Oodle lib is
   installed locally); the game must accept the buffers.

Honest limits: disabling replacer nodes does not remove Johnny from the 195 scripted scenes that
spawn him by scene-actor record, and it does not remove the Relic sickness. Track its state in
`.opencode/specs/001-bypass-v-johnny-merge/`.
