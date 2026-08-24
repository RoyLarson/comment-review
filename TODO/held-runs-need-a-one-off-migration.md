# The held runs can be migrated one-off from the source at the recorded hash

```
Status:   deferred (waits on someone needing a held run replayed -- nothing depends on it)
Progress: 2 of 5 tasks done
Owner:    testing
Requires-Roy: false
Raised:   2026-08-19 (B4, after `convert` was made to refuse a 0.2.x report, 2026-08-19)
Deferred: 2026-08-19 — Not worth doing now -- Roy, 2026-08-19: 'a one-off script thing
          and not worth doing right now.' Nothing depends on it: 0.2.4 onward holds
          addressed reports, so replay is cheap again without this. It buys back only
          the runs already in evidence/.
Triaged:  2026-08-23 — THREE CLAIMS IN THIS FILE ARE NOW FALSE, and the shape of the gap
          moved with them. (1) `record.convert` and `record.parse_report` NO LONGER
          EXIST -- `grep -rn "parse_report\|def convert" plugins/ scripts/ tests/`
          matches only `__pycache__`, and `record.py` holds `every_record` (`:816`) and
          `record_problems` (`:1033`). (2) Of the three held runs listed, only
          `evidence/cycle-0.2.3/` is in this tree; `evidence/todo-tool-full-run/` and
          `evidence/redacted-corpus-full-v0_2/` are not. (3) The held records are NOT
          `--- RECORD` / `LOCATION` text: `evidence/cycle-0.2.3/records/*.json` carry
          `record_version "1"` and a FLAT `records` list whose `address` is
          `path:start-end`, a LINE RANGE. ! Status moved `blocked` -> `deferred`: a
          `deferred` Status line names what it waits on, so the reason the old note gave
          for filing it blocked no longer holds.
```

## Objective

!! **THE SHIPPED CONVERTER CANNOT DO IT, AND A ONE-OFF SCRIPT CAN.** Roy, 2026-08-19: *"because
we have recorded the hash and because we can clone the data we can eventually one-off move the old
records into the new format -- but that is definitely a one-off script thing and not worth doing
'right' now."*

!! **THE GAP IS AN ADDRESS, AND THAT HAS NOT CHANGED -- WHAT CHANGED IS BOTH ENDS OF IT.**
A held report names a place by LINE RANGE and today's reader wants a CUE.

| | held, `evidence/cycle-0.2.3/records/*.json` | current, `record.py` |
| --- | --- | --- |
| envelope | flat `records` list on the report | `pages` -> each page's `records`, walked by `every_record` (`:816`) |
| the place | `"address": "path/to/file.py:1-33"` -- a line range | a cue on the page, put back together by `held.held_records` |
| the file | repeated on every record | named once, by the page |
| the reader that bridged them | `record.convert` / `record.parse_report` | **GONE** -- neither symbol exists in this tree |

**What closes the gap is the SOURCE**, and every held run records the hash to get it.

| held run | subject, as its own README states | in this tree |
| --- | --- | --- |
| `evidence/cycle-0.2.3/` | **this repo**, `feat/0.2.3-cycle-and-record` @ `1ad4ba7` | **yes** |
| `evidence/todo-tool-full-run/` | `redacted_corpus`, `todo-requires-roy` @ `REDACTED_SHA_D` | no |
| `evidence/redacted-corpus-full-v0_2/` | `redacted-branch-b` @ `REDACTED_SHA_F`, base `REDACTED_SHA_E` | no |

! **`cycle-0.2.3` is not merely the cheap first case, it is the only one here**: `1ad4ba7` is in
this repo's own history -- `git log --oneline -1 1ad4ba7` resolves -- so it needs no clone and the
answer can be checked by reading. MEASURED 2026-08-23: it holds four reports, one per role, in
`records/`. The other two rows are kept because a held run may be brought back; they are not work
this tree can start.

**The recipe, which is why this is a script and not a feature:**

1. Worktree the subject at the recorded hash.
2. `census.py --json` over the paths in scope -- a census that carries addresses.
3. Read the held report's JSON directly and walk its FLAT `records` list. ! It was `--- RECORD`
   text read past `parse_report` when this was filed; the format moved and the reader went.
4. For each record, take the `path:start-end` in its `address` and ask the locator for the cue
   at that start line.
5. Re-emit under a `pages` envelope with that cue, and run the shipped shape check over the
   result.

! **Step 4 needs a stated rule and does not have one.** Block boundaries moved between census
versions -- the held census has no `margin` and no `undocumented` -- so a held range need not
correspond to one of today's places. The obvious rule is *the place whose EDIT range contains the
held start line*, and it is a guess until something checks it against a run whose answer is known.

! **SUPERSEDED, and kept so the error stays legible.** This file used to say the script must read
the held report's RAW text because `record.parse_report` discards `LOCATION`. Neither half
survives: MEASURED 2026-08-23, `parse_report` and `convert` exist nowhere in `plugins/`,
`scripts/` or `tests/`, and the held reports are already JSON -- `records[*]` each carrying
`"address": "path:start-end"`. The reading problem is now the ENVELOPE and the address FORM.

!! **NOT WORTH DOING NOW, AND THE REASON IS THAT NOTHING DEPENDS ON IT.** Replay was the cheap way
to validate a change; 0.2.4 onward holds addressed reports, so the cheapness returns without this.
This buys back the runs already in `evidence/`, and only those.

! **IT LIVES IN `scripts/`, NOT `plugins/`.** Nothing a user installs should carry it, and it runs
once per held run rather than once per review. ! Stated here rather than carried as a box, because
it is a constraint on the work and not a checkpoint of its own.

## Tasks

- [ ] T1 -- !! RULE STEP 4 FIRST: which PLACE a held `path:start-end` maps to. Verify: the
      rule is written down, and a run whose answer is known agrees on every record.
- [ ] T2 -- Migrate `evidence/cycle-0.2.3/` first -- its subject is this repo at
      `1ad4ba7`. Verify: its four role reports re-emit under a `pages` envelope with cues.
- [x] T3 -- SUPERSEDED. The raw-text requirement and the `parse_report` claim it rested on
      are both false; the record of why is in the Objective.
- [ ] T4 -- Run the shipped shape check, `record.record_problems` (`record.py:1033`), over
      what T2 emits. Verify: `verdicts.py` joins it at `1ad4ba7`, all citations resolving.
- [x] T5 -- NOT A TASK. It lives in `scripts/`, not `plugins/` -- a constraint on the
      work, restated in the Objective.
