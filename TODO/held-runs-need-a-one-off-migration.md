# The held runs can be migrated one-off from the source at the recorded hash

```
Status:   open
Progress: 0 of 5 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-19 (B4, after `convert` was made to refuse a 0.2.x report, 2026-08-19)
Deferred: 2026-08-19 — Not worth doing now -- Roy, 2026-08-19: 'a one-off script thing
          and not worth doing right now.' Nothing depends on it: 0.2.4 onward holds
          addressed reports, so replay is cheap again without this. It buys back only
          the runs already in evidence/.
```

## Objective

!! **THE SHIPPED CONVERTER CANNOT DO IT, AND A ONE-OFF SCRIPT CAN.** Roy, 2026-08-19: *"because
we have recorded the hash and because we can clone the data we can eventually one-off move the old
records into the new format -- but that is definitely a one-off script thing and not worth doing
'right' now."*

`record.convert` refuses a 0.2.x report because nothing IN the report names a place: `BLOCK
<index>` is a position in a census that carries no addresses and that today's `census.py` does not
reproduce, and `LOCATION path:start-end` is thrown away by `parse_report`. **What closes the gap
is the SOURCE**, and every held run records the hash to get it.

| held run | subject, as its own README states |
| --- | --- |
| `evidence/cycle-0.2.3/` | **this repo**, `feat/0.2.3-cycle-and-record` @ `882635b` |
| `evidence/todo-tool-full-run/` | `redacted_corpus`, `todo-requires-roy` @ `REDACTED_SHA_D` |
| `evidence/redacted-corpus-full-v0_2/` | `redacted-branch-b` @ `REDACTED_SHA_F`, base `REDACTED_SHA_E` |

! **`cycle-0.2.3` is the cheap first case**: `882635b` is in this repo's own history, so it needs
no clone and the answer can be checked by reading.

**The recipe, which is why this is a script and not a feature:**

1. Worktree the subject at the recorded hash.
2. `census.py --json` over the paths in scope -- a census that carries addresses.
3. Read the held report's RAW text, not `parse_report`, which discards `LOCATION`.
4. For each `--- RECORD`, take `LOCATION path:start` and ask the locator for the address there.
5. Emit the record with that address; run the shipped shape check over the result.

! **Step 4 needs a stated rule and does not have one.** Block boundaries moved between census
versions -- the held census has no `margin` and no `undocumented` -- so a held range need not
correspond to one of today's blocks. The obvious rule is *the block whose EDIT range contains the
held start line*, and it is a guess until something checks it against a run whose answer is known.

!! **NOT WORTH DOING NOW, AND THE REASON IS THAT NOTHING DEPENDS ON IT.** Replay was the cheap way
to validate a change; 0.2.4 onward holds addressed reports, so the cheapness returns without this.
This buys back the runs already in `evidence/`, and only those.

## Tasks

- [ ] !! RULE STEP 4 FIRST: which of today's blocks a held `LOCATION path:start-
      end` maps to. The obvious rule is the block whose EDIT range contains the
      held start line, and it is a guess until it is checked against a run whose
      answer is known. Block boundaries moved between census versions -- the held
      census has no `margin` and no `undocumented`.
- [ ] Start with `evidence/cycle-0.2.3/` -- its subject is THIS repo at `882635b`,
      so it needs no clone and the result can be checked by reading.
- [ ] The script reads the held report's RAW text. `record.parse_report` discards
      `LOCATION`, which is the only field that can place a record once the source
      is in hand.
- [ ] Run the shipped shape check over whatever it emits --
      `record.record_problems` and the join -- so a migrated report is held to the
      same contract as a fresh one.
- [ ] It lives in `scripts/`, not `plugins/`. Nothing a user installs should carry
      it, and it runs once per held run rather than once per review.
