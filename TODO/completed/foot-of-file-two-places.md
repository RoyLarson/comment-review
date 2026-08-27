# Two places name the foot of a file, and only one of them can hold prose

```
Status:   decision-needed
Progress: 3 of 3 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-25 (xhigh wave C on feat/the-write-chain-of-command, finding 5)
Updated:  2026-08-26 — RULED and CLOSED. Roy, 2026-08-26: "still the same rule as the
          frontmatter in reverse." Matter is the run that STARTS on line 1 or ENDS on
          the last line, so the blank that pushes a gap clear of it goes BEFORE at the
          head and AFTER at the foot. The compositor sets a trailing leading below a
          closing gap it is filling, and the two places separate: the back matter keeps
          the foot, the gap sits above the blank. THE QUESTION WAS MIS-FRAMED -- it
          asked which of the two owns prose at the foot and assumed one had to lose. The
          answer is both, so task 2 is SUPERSEDED rather than done: there is no losing
          place to unemit or refuse. MEASURED: "...return y\n# ADDED\n" and "...return
          y\n\n# ADDED\n" both re-read at f1; "...return y\n# ADDED\n\n" re-reads at the
          closing gap. A leading BEFORE the closing gap was the mirror image of the fix
          and moved nothing -- an earlier attempt exempted the foot on that measurement
          and called the collision unsolvable. Pinned by
          test_an_ADD_at_b4_NOW_REACHES_A_DRAFT_AT_ITS_OWN_PLACE and
          test_b4_AND_f1_NO_LONGER_COMPOSE_THE_SAME_BYTES, and b4 is back in the every-
          absent-place matrix it had been excluded from. decision-log.md Addressing:
          #19.
```

## Objective

`addresser.cue` emits the closing gap and the file's back matter at the SAME
`<eof>` trigger, and its own comment says so: *"both sentinels are shared --
`a0` with `f0` at the head, the closing gap with `f1` at the foot."* Which of
the two a paragraph attaches to is the LEXER's `matter` rule, not the walk's.

**MEASURED 2026-08-25 on `tests/conftest.SAMPLE`**, through
`flows/proof_setter.run`:

| notation | composed draft | outcome |
| --- | --- | --- |
| `{"m.py@b4": "# ADDED"}` | `...return y\n# ADDED\n` | REFUSED at `reread` |
| `{"m.py@f1": "# ADDED"}` | `...return y\n# ADDED\n` | drafted |

The two compose **the same bytes** -- `test_b4_AND_f1_COMPOSE_THE_SAME_BYTES`
pins it -- so neither the galley nor the compositor is what refuses. The
re-read gives the prose to `f1` and leaves `b4` empty, and `_reread` compares
against the cue it was given.

! **IT IS NOT ALWAYS `f1` THAT WINS.** Measured over 3,293 pages in this
checkout's `corpora/`: **9** have a closing `b` holding prose -- doc-comment
runs (`--- @class`, `/* ... */`) that the lexer does not stamp `matter`. So
which place holds prose at the foot depends on the KIND of the prose being
added, which nothing at the address level can state.

! **THIS IS THE BACK HALF OF A CATEGORY ERROR ALREADY RULED AT THE FRONT.**
`CLAUDE.md`: *"`b0` held the file's own matter as well as the first gap"* --
resolved by giving matter its own `f` series. The head's residual collision
(`f0` grabbing `b0`'s lines when front matter is not on line 1) is a **ruled
sacrifice**, Roy 2026-08-21: *"I know f0 is going to grab b0 lines. It is a
sacrifice I am willing to make."* The foot has had no such ruling.

**WHAT THIS WAVE DID AND DID NOT DO.** `_reread` still refuses, and now names
the place that does hold the text -- `b4: holds [], was given ['# ADDED'] --
f1 holds it`. That makes the refusal actionable and nothing more. Reading the
notation as satisfied because the text is SOMEWHERE would be the verification
step agreeing with the edit step instead of checking it, which is the shape
`docs/gates.md` records the round trip scoring 699 of 699 on.

! **A DECISION IS OWED BEFORE ANY CODE MOVES.** Roy ruled the closing `b` into
existence, 2026-08-22: *"the last `b` triggers on EOF and records either
`<eof>` or `<module>`, and its anchor and where it is placed becomes a
determined fact by the compositor."* Deleting it is not this lane's to choose,
and neither is demoting `f1`.

## Tasks

- [x] Rule which of the closing gap and the back matter owns prose at the foot of
      a file, and record it in docs/decision-log.md
- [x] Make the losing place either unemitted or refusable at the EDIT step, so an
      add there does not reach reread
- [x] Pin the ruling with a test: an add at the foot reaches a draft, and the
      address it must be cited at is the one the ruling names
