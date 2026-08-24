# Requires-Roy never goes back down, so 32 TODOs claim to be waiting on a ruling

```
Status:   deferred
Progress: 2 of 5 tasks done
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
should have a method of clearing my name already."* It does.

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
it.

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

- [x] T1 -- FINISHED. Cleared the flag on the FIVE whose own `Owner:` line records
      the ruling: `a-comment-inside-a-line-makes-the-file-unprovable`,
      `ownership-is-read-first-but-nothing-makes-it-so`, `the-census-is-mostly-
      intervals-nobody-rules-on`, `correct-against-patch-is-a-conflict-and-is-not-
      flagged`, `stage-5-is-the-only-stage-with-no-independent-reader`. VERIFIED
      2026-08-23: each header reads `Requires-Roy: false`.
- [x] T2 -- FINISHED. Cleared the two that went stale during 0.2.4 and did not say
      so: `docstrings-need-their-own-address-series` (the `a0..aN` numbering, ruled
      2026-08-19) and the interior-comment half of `a-comment-inside-a-line-makes-
      the-file-unprovable`. VERIFIED 2026-08-23: both read `Requires-Roy: false`.
- [ ] T3 -- Read each still-flagged file against the commits and transcripts that
      would carry its ruling, and clear the flag where one landed. This is the part
      that is work rather than cleanup: `Owner:` says `* 1 ruling` without saying
      whether it arrived. Verify: every file still reading `Requires-Roy: true`
      carries at least one `*` box naming the decision that is owed, so
      `list --requires-roy` and the `*` boxes agree; and the count from
      `grep -l "Requires-Roy: true" TODO/*.md | wc -l` is recorded here with its
      date.
- [ ] T4 -- * SUPERSEDED IN PART, and this is the remainder. `set-requires-roy`
      exists, so the box that said the flag has no way down was wrong; what is
      still missing is anything that PROMPTS or RECOMPUTES the clearing, since the
      only automatic lowering fires as a file leaves `TODO/`. Check the upstream
      vendor at `redacted_corpus` `todo-requires-roy` REDACTED_SHA_D FIRST -- the
      tool is re-grabbed, not maintained here. Verify: either `todo_tool.py` gains
      the recompute with a test that fails without it, or this file records the sha
      read and that upstream has none.
- [ ] T5 -- `.claude/skills/todo-tool/SKILL.md:309` calls `list --requires-roy`
      *"how Roy pulls his own queue: everything waiting on"* him. Correct it or make
      it true. Verify: either that line says the list is unfiltered by whether the
      ruling arrived, or the command grows a filter and the SKILL text names it.
