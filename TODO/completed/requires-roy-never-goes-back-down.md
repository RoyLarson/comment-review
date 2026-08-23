# Requires-Roy never goes back down, so 32 TODOs claim to be waiting on a ruling

```
Status:   blocked
Progress: 2 of 5 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-19 (asking what was waiting on Roy for 0.2.4, 2026-08-19)
Updated:  2026-08-19 — deferred until 0.2.4 closes -- Roy, 2026-08-19: 'this is work
          waiting on this release of this project to finish'. Nothing in the 0.2.4 plan
          is blocked on it.
Narrowed: 2026-08-19 — Six cleared from evidence in their own files, 32 -> 26.
          SUPERSEDED: this file first said the flag has no way down; 'set-requires-roy
          false' exists and is documented. The defect is that nothing recomputes it or
          prompts the clearing -- check the upstream vendor at redacted_corpus todo-
          requires-roy REDACTED_SHA_D before building one.
Moved:    2026-08-23 — the TOOL half moved to job_board as `requires-roy-never-clears`,
          2026-08-23 -- job_board owns todo_tool now and this repo only vendors it. !
          What did NOT move is task 3: the audit of the remaining ~25 flags here against
          the commits that would carry their rulings. That is this project own backlog
          hygiene, and it needs a home if it is still wanted separately from the read-
          through.
```

## Objective

!! **32 TODOs CARRIED `Requires-Roy: true`, AND NOTHING EVER LOWERED ONE.** Measured
2026-08-19.

! **SUPERSEDED, same day: `set-requires-roy <file> false` EXISTS** and is documented in
`.claude/skills/todo-tool/SKILL.md`. This file first said the flag "has no way down" and named
only `complete` and `reopen` -- wrong, and the skill's own instruction is the opposite: *"set it
as soon as you hit one ... and clear it when he answers."* Roy: *"the tool should have a method of
clearing my name already."* It does.

!! **SO THE DEFECT IS THE DISCIPLINE, NOT THE COMMAND.** The flag is set when a wall is hit and
nobody runs the clearing command when the ruling arrives, because nothing prompts it and nothing
recomputes it. **Six were cleared 2026-08-19 from evidence already inside their own files** --
32 down to 26 -- and none of the six needed a ruling to clear.

!! **THAT DEFEATS THE FIELD.** `.claude/skills/todo-tool/SKILL.md` says `list --requires-roy` is
*"how Roy pulls his own queue: everything waiting on him."* At 32 entries it is a wall rather than
a queue, and Roy, 2026-08-19: *"pulling it tells you nothing you can act on."*

! **It is the same failure the tool exists to prevent, one field over.** `Progress:` is a derived
fact, so the tool recomputes it on every write rather than trusting a hand edit. `Requires-Roy` is
a derived fact too -- *is a decision still owed* -- and nothing recomputes it.

**SIX WERE CLEARED 2026-08-19, EACH FROM EVIDENCE IN ITS OWN FILE:**

| TODO | its Owner field says |
| --- | --- |
| `a-comment-inside-a-line-makes-the-file-unprovable` | `* 1 ruling, MADE` |
| `ownership-is-read-first-but-nothing-makes-it-so` | `ruled 2026-08-17; the rest is build` |
| `the-census-is-mostly-intervals-nobody-rules-on` | `Roy ruled the design 2026-08-18; the rest is build` |
| `correct-against-patch-is-a-conflict-and-is-not-flagged` | `already ruled on once` |
| `stage-5-is-the-only-stage-with-no-independent-reader` | `* 3 rulings, 2 made` |
| `docstrings-need-their-own-address-series` | the `a0..aN` numbering, ruled 2026-08-19 |

! The remaining **26** cannot be classified from the file alone. Several say `* 1 ruling` in `Owner:`
without saying whether it arrived; settling each needs the commit or the transcript that carries
it.

!! **DEFERRED UNTIL 0.2.4 CLOSES.** Roy, 2026-08-19: *"I think this is work waiting on this
release of this project to finish."* Nothing in the 0.2.4 plan is blocked on it -- the plan's one
`*` box is itself one of the stale five.

! **Roy, 2026-08-19, on where this came from**: *"that was what the todo-tool session was
working on when we copied this over and maybe lost some work in the process."* The tool is
VENDORED from `redacted_corpus` at `todo-requires-roy` REDACTED_SHA_D and is re-grabbed rather than
maintained here, so a recompute may exist upstream. **Check there before building one.**

! **This file is NOT flagged `Requires-Roy`.** Clearing a flag whose own file records the ruling
is an audit, not a decision, and flagging it would add a thirty-third entry to the queue it exists
to shorten.

## Tasks

- [x] Clear the flag on the FIVE whose own `Owner:` line records the ruling:
      `a-comment-inside-a-line-makes-the-file-unprovable`, `ownership-is-read-
      first-but-nothing-makes-it-so`, `the-census-is-mostly-intervals-nobody-
      rules-on`, `correct-against-patch-is-a-conflict-and-is-not-flagged`,
      `stage-5-is-the-only-stage-with-no-independent-reader`. No ruling needed --
      the files say it was made.
- [x] Clear the two that went stale during 0.2.4 and do not say so: `docstrings-
      need-their-own-address-series` (the `a0..aN` numbering, ruled 2026-08-19)
      and the interior-comment half of `a-comment-inside-a-line-makes-the-file-
      unprovable`.
- [ ] Read the remaining ~25 against the commits and transcripts that would carry
      their rulings, and clear each flag where one landed. This is the part that
      is real work rather than cleanup: the `Owner:` field says `* 1 ruling`
      without saying whether it arrived.
- [ ] !! THE FLAG NEEDS A WAY DOWN THAT IS NOT `complete`. Today only closing a
      file or reopening one lowers it, so it accumulates. Decide what recomputes
      it -- the tool has no notion of a ruling landing, and `Progress:` is
      recomputed on every write precisely because a derived fact nobody recomputes
      goes wrong.
- [ ] `.claude/skills/todo-tool/SKILL.md` calls `list --requires-roy` "how Roy
      pulls his own queue". Correct it or make it true -- at 32 entries it is a
      wall, and the skill's own warning about `--status` drifting from a file's
      `Status:` is the same shape.
