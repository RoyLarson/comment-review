# Requires-Roy never goes back down, so 32 TODOs claim to be waiting on a ruling

```
Status:   blocked
Progress: 0 of 5 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-19 (asking what was waiting on Roy for 0.2.4, 2026-08-19)
Updated:  2026-08-19 — deferred until 0.2.4 closes -- Roy, 2026-08-19: 'this is work
          waiting on this release of this project to finish'. Nothing in the 0.2.4 plan
          is blocked on it.
```

## Objective

!! **32 TODOs CARRY `Requires-Roy: true`, AND THE FLAG HAS NO WAY DOWN.** Measured 2026-08-19.
`complete` clears it and `reopen` resets it to false, so the only paths that lower it are closing
a file and reopening one. **Nothing clears it when a ruling actually lands**, which is the case it
was built for -- so it only ever accumulates.

!! **THAT DEFEATS THE FIELD.** `.claude/skills/todo-tool/SKILL.md` says `list --requires-roy` is
*"how Roy pulls his own queue: everything waiting on him."* At 32 entries it is a wall rather than
a queue, and Roy, 2026-08-19: *"pulling it tells you nothing you can act on."*

! **It is the same failure the tool exists to prevent, one field over.** `Progress:` is a derived
fact, so the tool recomputes it on every write rather than trusting a hand edit. `Requires-Roy` is
a derived fact too -- *is a decision still owed* -- and nothing recomputes it.

**FIVE ARE PROVABLY STALE FROM THEIR OWN `Owner:` LINE:**

| TODO | its Owner field says |
| --- | --- |
| `a-comment-inside-a-line-makes-the-file-unprovable` | `* 1 ruling, MADE` |
| `ownership-is-read-first-but-nothing-makes-it-so` | `ruled 2026-08-17; the rest is build` |
| `the-census-is-mostly-intervals-nobody-rules-on` | `Roy ruled the design 2026-08-18; the rest is build` |
| `correct-against-patch-is-a-conflict-and-is-not-flagged` | `already ruled on once` |
| `stage-5-is-the-only-stage-with-no-independent-reader` | `* 3 rulings, 2 made` |

! **Two more went stale during 0.2.4 and their files do not say so**:
`docstrings-need-their-own-address-series` (the `a0..aN` numbering was ruled 2026-08-19) and the
interior-comment half of `a-comment-inside-a-line-makes-the-file-unprovable`.

! The remaining ~25 cannot be classified from the file alone. Several say `* 1 ruling` in `Owner:`
without saying whether it arrived; settling each needs the commit or the transcript that carries
it.

!! **DEFERRED UNTIL 0.2.4 CLOSES.** Roy, 2026-08-19: *"I think this is work waiting on this
release of this project to finish."* Nothing in the 0.2.4 plan is blocked on it -- the plan's one
`*` box is itself one of the stale five.

! **This file is NOT flagged `Requires-Roy`.** Clearing a flag whose own file records the ruling
is an audit, not a decision, and flagging it would add a thirty-third entry to the queue it exists
to shorten.

## Tasks

- [ ] Clear the flag on the FIVE whose own `Owner:` line records the ruling:
      `a-comment-inside-a-line-makes-the-file-unprovable`, `ownership-is-read-
      first-but-nothing-makes-it-so`, `the-census-is-mostly-intervals-nobody-
      rules-on`, `correct-against-patch-is-a-conflict-and-is-not-flagged`,
      `stage-5-is-the-only-stage-with-no-independent-reader`. No ruling needed --
      the files say it was made.
- [ ] Clear the two that went stale during 0.2.4 and do not say so: `docstrings-
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
