# Savegame survey (2026-10-03)

> **Redacted for public release, 2026-10-04.** Absolute paths, the Linux username and the raw
> 16-hex-character playthrough IDs were replaced with placeholders (`$GAME_SAVED_GAMES`, `PT-A`…`PT-C`)
> before this was published. Save *names* are kept because the spec, the plan and the test gates all
> reference them as identifiers — without them the document stops being usable. Set
> `CP2077_SAVED_GAMES` and run `tools/cp2077-metadata-scan.py` to reproduce this survey against a
> real install.

## Save location
```
$GAME_SAVED_GAMES/
```

## Metadata format correction

Metadata files are named **`metadata.9.json`** (not `metadata.json`), and the payload is **nested three levels deep**:

```
RootType
└── Data
    └── metadata
        ├── finishedQuests   # space-separated string, NOT a list
        ├── playthroughID    # 16 hex chars
        └── timestampString  # "HH:MM:SS, D.M.YYYY" — NOT ISO, so string-sort is wrong
```

Consequences:
- `data.get('finishedQuests')` at top level silently returns `None` — every save looks identical. This is what produced a first scan of "all saves identical".
- `finishedQuests` is a **space-separated string**, so `'q005' in finished` substring-tests true for `q0051` etc. Must `.split()` first. Confirmed the bug: a substring scan reported `q005=True` for saves that had not finished it, and `sq032=False` for a save that had.
- `timestampString` has no year-first prefix, so sorting it as a string sorts by time-of-day, not date. Sorting needs parsing: `D.M.YYYY` with a locale-dependent month abbreviation.

## Playthroughs present

| playthroughID | Save dates | Notes |
| --- | --- | --- |
| `PT-A` | Oct 2022 – Dec 2022 | Oldest. Progresses through The Heist and past Tapeworm. |
| `PT-B` | Jan 2023 | New game, restarted. |
| `PT-C` | Oct 2026 | The current new game (started yesterday). |

## Candidate baseline saves

Filter used: `q004` finished, `q005` **not** finished, `sq032` not finished → sits immediately before The Heist.

| Save | timestampString | playthrough | finishedQuests |
| --- | --- | --- | --- |
| **ManualSave-5** | 14:20:21, 29.10.2022 | `PT-A` | `q004 q000 q001 q003 ma_wat_kab_08` |
| ManualSave-1 | 19:23:34, 26.10.2022 | `PT-A` | same as above |
| ManualSave-2 | 19:53:48, 26.10.2022 | `PT-A` | same as above |
| ManualSave-3 | 21:05:57, 26.10.2022 | `PT-A` | same as above |
| ManualSave-4 | 21:37:51, 26.10.2022 | `PT-A` | same as above |
| ManualSave-146 | 20:57:50, 6.01.2023 | `PT-B` | + `ma_wat_kab_05 ma_wat_lch_04` |
| ManualSave-147 | 21:00:45, 6.01.2023 | `PT-B` | same as 146 |

**Chosen: `ManualSave-5`.** Pre-Heist, fewest side gigs, oldest, so furthest from any merge state.

## Merge-boundary saves (for diffing later)

These are the earliest `q005`-finished saves in playthrough `PT-A` — the other end of the boundary:

| Save | timestampString | finishedQuests |
| --- | --- | --- |
| ManualSave-29 | 00:07:00, 7.11.2022 | 9 entries incl. `q005` |
| ManualSave-30 | 00:18:54, 7.11.2022 | `q005` present |
| ManualSave-6 | 20:17:12, 29.10.2022 | `q005` present |

`ManualSave-6` (29.10.2022, same day as ManualSave-5) is the tightest pre/post pair available — same playthrough, same day, one before The Heist and one after.

`ManualSave-124` (15:24:16, 4.12.2022) is the earliest save with **both** `q005` and `sq032` finished, i.e. past Tapeworm.

## What this does and does not tell us

- `finishedQuests` marks quest *completion*, not the merge itself. There is no merge flag here.
- To find the actual merge trigger we need the **fact store**, which lives in the save body (`ManualSave-5/*.bin` etc.), not in metadata. CyberpunkSaveEditor reads that.
- Unknown yet: whether the 2022 saves load under the current game version. Old saves usually do, but the Relic-sequence code has been touched by patches 2.0/2.1/2.2/2.3.

## Next step

Diff facts between `ManualSave-5` (pre-Heist) and `ManualSave-6` (post-Heist, same day, same playthrough) to see which facts the Heist sets. That isolates the candidates for the merge trigger without guessing quest IDs.