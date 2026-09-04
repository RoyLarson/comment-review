# Requires-Roy never goes back down, so 32 TODOs claim to be waiting on a ruling

```
Status:   deferred
Progress: 2 of 7 tasks closed
Owner:    systems
Requires-Roy: false
Raised:   2026-08-19 (asking what was waiting on Roy for 0.2.4, 2026-08-19)
Updated:  2026-08-19 -- deferred until 0.2.4 closes -- Roy, 2026-08-19: 'this is work
          waiting on this release of this project to finish'. Nothing in the 0.2.4 plan
          is blocked on it.
Narrowed: 2026-08-19 -- Six cleared from evidence in their own files, 32 -> 26.
          SUPERSEDED: this file first said the flag has no way down; 'set-requires-roy
          false' exists and is documented. The defect is that nothing recomputes it or
          prompts the clearing -- check the upstream vendor at redacted_corpus todo-
          requires-roy REDACTED_SHA_D before building one.
Re-measured: 2026-08-23 -- 47 of the 101 files in TODO/ carry 'Requires-Roy: true',
          against 26 after the 2026-08-19 clearing. The count rose by 21 in four days
          and nothing lowered one, which is this file's claim measured again.
Split:    2026-08-23 -- 5 boxes became 7. The audit box held the clearing and the count
          it produces; the recompute box held an upstream read and the build after it
```

## Objective

!! **THE FLAG GOES UP AND NOTHING BRINGS IT DOWN.** MEASURED 2026-08-19: 32 of the open TODOs
carried `Requires-Roy: true`, and six cleared by hand the same day took it to 26. RE-MEASURED
2026-08-23: **47 of 101** -- `grep -l "Requires-Roy: true" TODO/*.md | wc -l`.

! **SUPERSEDED, 2026-08-19: `set-requires-roy <file> false` EXISTS.** It is a subcommand
(`scripts/todo_tool.py:1522`, dispatched at `:1616`) and is documented at
`.claude/skills/todo-tool/SKILL.md:55` and `:132`. This file first said the flag "has no way
down" and named only `complete` and `reopen` -- wrong, and the skill's own instruction is the
opposite: *"set it as soon as you hit one ... and clear it when he answers."* Roy: *"the tool
should have a method of clearing my name already."* It does. **What is still missing is anything
that PROMPTS or RECOMPUTES the clearing**, which is the remainder that box left behind.

!! **SO THE DEFECT IS THE DISCIPLINE, NOT THE COMMAND.** The flag is set when a wall is hit and
nobody runs the clearing command when the ruling arrives, because nothing prompts it and nothing
recomputes it. The one automatic lowering is inside `complete`: `todo_tool.py:1012-1013` clears
the field as the file is renamed into `completed/`, so a file stops demanding a decision only by
leaving the backlog.

!! **THAT DEFEATS THE FIELD.** `.claude/skills/todo-tool/SKILL.md:309` says `--requires-roy` is
*"how Roy pulls his own queue: everything waiting on"* him. At 47 entries it is a wall rather
than a queue, and Roy, 2026-08-19: *"pulling it tells you nothing you can act on."*

! **It is the same failure the tool exists to prevent, one field over.** `Progress:` is a derived
fact, so the tool recomputes it on every write rather than trusting a hand edit. `Requires-Roy`
is a derived fact too -- *is a decision still owed* -- and nothing recomputes it.

**SIX WERE CLEARED 2026-08-19, EACH FROM EVIDENCE IN ITS OWN FILE**, and all six still read
`Requires-Roy: false` -- verified 2026-08-23 by reading each header:

| TODO | its Owner field said |
| --- | --- |
| `a-comment-inside-a-line-makes-the-file-unprovable` | `* 1 ruling, MADE` |
| `ownership-is-read-first-but-nothing-makes-it-so` | `ruled 2026-08-17; the rest is build` |
| `the-census-is-mostly-intervals-nobody-rules-on` | `Roy ruled the design 2026-08-18; the rest is build` |
| `correct-against-patch-is-a-conflict-and-is-not-flagged` | `already ruled on once` |
| `stage-5-is-the-only-stage-with-no-independent-reader` | `* 3 rulings, 2 made` |
| `docstrings-need-their-own-address-series` | the `a0..aN` numbering, ruled 2026-08-19 |

! **The rest cannot be classified from the file alone.** Several say `* 1 ruling` in `Owner:`
without saying whether it arrived; settling each needs the commit or the transcript that carries
it. **That is the part that is work rather than cleanup.**

!! **DEFERRED UNTIL 0.2.4 CLOSES.** Roy, 2026-08-19: *"I think this is work waiting on this
release of this project to finish."* Nothing in the 0.2.4 plan is blocked on it.

! **Roy, 2026-08-19, on where this came from**: *"that was what the todo-tool session was
working on when we copied this over and maybe lost some work in the process."* The tool is
VENDORED from `redacted_corpus` at `todo-requires-roy` REDACTED_SHA_D and is re-grabbed rather
than maintained here, so a recompute may exist upstream. **Check there before building one.**

! **This file is NOT flagged `Requires-Roy`.** Clearing a flag whose own file records the ruling
is an audit, not a decision, and flagging it would add one more entry to the queue it exists to
shorten.

## Tasks

- [x] T1 | FINISHED | unknown | T1 -- FINISHED. Cleared the flag on the five
      whose own `Owner:` line records the ruling; the five are named in the
      Objective.
- [x] T2 | FINISHED | unknown | T2 -- FINISHED. Cleared the two that went stale
      during 0.2.4 and did not say so; both now read `Requires-Roy: false`.
- [ ] T3 | T3 -- Clear the flag on each still-flagged file whose ruling has
      landed, read from the commits. Verify: `list --requires-roy` and the `*`
      boxes agree.
- [ ] T4 | T4 -- Record the count that clearing leaves. Verify: `grep -l
      "Requires-Roy: true" TODO/*.md \| wc -l` is written into this file with
      its date.
- [ ] T5 | T5 -- Read the upstream vendor at `redacted_corpus`
      `todo-requires-roy` for an existing recompute. Verify: this file records
      the sha and the answer.
- [ ] T6 | T6 -- If upstream has none, give `todo_tool.py` the recompute or the
      prompt to clear. Verify: a test fails without it and passes with it.
- [ ] T7 | T7 -- Correct `.claude/skills/todo-tool/SKILL.md:309` or make it
      true. Verify: the line says the list is unfiltered, or a filter exists and
      it names it.
