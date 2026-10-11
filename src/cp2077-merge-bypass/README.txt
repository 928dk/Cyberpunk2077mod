NoJohnnyReplacer
===============

Design A: keep the Relic and its story, stop the quest system from spawning
Johnny. The intervention disables the Tier-1 `#johnny_replacer`
`questReplacer_NodeType` nodes -- 28 nodes in 16 questphase files (27 enabled,
one already off) -- so the braindance slots stay wired but never fill.

The release artifact is a single .archive built from the vanilla game archives
by `tools/build-johnny-archive.sh`, which runs the full round-trip:

    extract (WolvenKit.CLI unbundle) -> serialize (CR2W -> json) ->
    replacer-scope.py patch -> replacer-scope.py verify ->
    deserialize (json -> CR2W) -> pack (.archive)

Output: `dist/NoJohnnyReplacer-<version>.archive`, installed by copying into
`<Cyberpunk 2077>/archive/pc/mod/`. Uninstall = delete the file.

STATUS: UNVERIFIED IN GAME. Two open risks, both recorded in
`.opencode/specs/001-bypass-v-johnny-merge/`:

  1. that the engine honours `enable = false` on these nodes at runtime
     (the keystone assumption of the whole design);
  2. that WolvenKit's Kraken-fallback packing (no Oodle lib installed
     locally) is accepted by the game's archive reader.

Known limits: disabling replacer nodes does not remove Johnny from the 195
scripted scenes that spawn him by scene-actor record, and it does not touch
the Relic sickness (that is NoRelicSickness' job).

The ship set (16 files) is frozen in `research/replacer-manifest.txt`; re-run
the manifest after any game patch and diff against it.