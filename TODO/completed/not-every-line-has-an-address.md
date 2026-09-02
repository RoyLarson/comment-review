# The addressing docstring states a universal that leading refutes

```
Status:   open
Progress: 8 of 8 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-23 (Roy, 2026-08-23: "Every line is a place" -- measured false by 595
          lines, all leading, on the day leading was ruled a symbol rather than a place)
Ruled:    2026-08-23 — leading does not get a place -- tried several ways and refused;
          the sentence is narrowed, and cue still needs its word
TRIAGED:  2026-08-23 — 2026-08-23. Seven of eight are records: the measurement, why only
          the UNIVERSAL is wrong and not the second clause, that it was true when
          written and a later ruling broke it, that owes_address already exists because
          of this gap, the cost either way, and the ruling itself -- which task 7 says
          CLOSES the starred task 5, so that one is ticked as answered rather than
          outstanding. ! The narrowing has LANDED: the old universal is gone from
          addresser.py and line 30 states the d-series exception immediately after,
          pointing at owes_address.
CLOSED:   2026-08-23 — TASK 8 IS DONE, AND THE FILE IS 8 OF 8. Verified by reading the
          module: `addresser.py:18-19` now reads *"AN ADDRESS IS NOT A SPAN OF LINES. NO
          LINE HAS MORE THAN ONE, AND A PARAGRAPH IS JUST THE LINES THAT SHARE ONE"* --
          the universal is gone and the surviving clause is the one doing the work.
          `addresser.py:30` points from there to `owes_address`, whose docstring at
          :1361-1377 carries Roy's closing quotation AND BOTH downstream reasons the
          task asked for: *"Two things stop being determinable the moment the slack is
          addressable: WHERE everything below an edit shifted to, and HOW MUCH blank
          belongs where afterwards -- the second being a typographic judgement no rule
          computes"*, followed by *"WHICH IS WHY THE EDGE SHAPE HOLDS: this system never
          chooses an amount of blank, it replays what it read."* ! It also carries the
          fence answer and the three refused attempts. ! Requires-Roy drops to false:
          the ruling landed and nothing further is owed. ! Ready for
          `todo_tool.py close`.
CORRECTED: 2026-08-23 — the Objective said [[leaf-means-two-things]] *"stays live"*.
           MEASURED: it is `TODO/completed/leaf-means-two-things.md`, 19 of 19, settled
           2026-08-23 by the binder model. The clause is corrected below rather than
           deleted, so the reasoning stays legible.
```

## Objective

**595 real lines carry no address, every one of them `leading`, under a docstring stating that
every line has exactly one.** MEASURED 2026-08-23 on the 19 shipped scripts: 8,746 paragraphs
over 11,009 lines, 401 with no address. So `addresser.py:28` -- *"EVERY LINE HAS EXACTLY ONE
ADDRESS, AND A PARAGRAPH IS JUST THE LINES THAT SHARE ONE"* -- was false in its own directory.

!! **RULED 2026-08-23: THE SENTENCE IS NARROWED. LEADING DOES NOT GET A PLACE.** Roy, closing it:
*"We tried leading getting a place. We tried several different ways. The constraints of coding AND
editing do not allow it. It makes the shifting impossible to correctly determine and lay the prose
back in."*

! **THAT IS THE OPERATIVE REASON AND IT WAS NOT IN THE RECORD.** `c27ea1d` already carries three
others -- a `d` has no anchor so it fails the substitution, `""` being the ABSENCE of an answer
rather than one; every other place exists because the walk reached a trigger and THE TRIGGER IS
THE ANCHOR, while a `d` exists only because the lexer found blank lines; and publishing agreeing
independently, since leading is a MEASUREMENT of the type it accompanies ("10 on 12") and a
measurement cannot be anchored, only the thing measured can. **What none of them said is what
breaks downstream**, and it is two failures rather than one. Roy: *"It makes the shifting
impossible to correctly determine and lay the prose back in ... or deterministically put the
leading back in where people would expect it."*

| | what cannot be determined |
| --- | --- |
| **position** | where everything below an edit has shifted to, once the slack between places is itself editable |
| **amount** | how much blank belongs where afterwards -- a comment growing from two lines to six, a paragraph dropped between two blanks. *"Where people would expect it"* is a typographic judgement, and no rule computes it |

!! **THE SECOND IS WHY THE EDGE SHAPE IS THE ONLY ONE THAT WORKS.** Keyed on the place it FOLLOWS
-- `f0 -> d0` -- the system never decides an amount; it replays what it read. Make leading a place
and an edit can target it, and then something has to CHOOSE the right blank. Nothing can.

!! **SO THE OPPOSITE FIX IS CLOSED, AND THIS FILE HELD IT OPEN FOR THREE HOURS.** It was filed
with *"do not correct the sentence before ruling"*, on the reading that if leading took a place the
universal would become true and `path@cue` would become PAGE AND LINE, the way a proof is cited.
**It cannot.** ! The trade shape was real and the constraint beats it: this system cannot cite by
line, because a prose edit moves every line below it, and it cannot make the slack citable either.
**Both halves of the trade's own address are unavailable here**, which is why the `@` half is a
coinage and not a borrowing.

! **AND BOTH CORRECTIONS HAVE LANDED.** The narrowed sentence is at `addresser.py:18-19` and
Roy's two downstream reasons are at `addresser.py:1361-1377`, in `owes_address`, which
`addresser.py:30` points to from the sentence itself.

! **`cue` GOT ITS WORD ELSEWHERE.** This file said `leaf-means-two-things` *"stays live rather
than dissolving"*; MEASURED 2026-08-23, it is `TODO/completed/leaf-means-two-things.md` at 19 of
19 -- *"the binder model closes it -- no leaf in the picture, cue becomes cue, and Cues needs no
exotic noun because completeness is in the tabbing practice."* The reasoning is kept because it
was the live question when this file was written.

## Tasks

- [x] T1 | FINISHED | unknown | T1 -- MEASURED 2026-08-23 ON THE 19 SHIPPED
      SCRIPTS: 8,746 paragraphs over 11,009 lines; 401 carry NO address, and 595
      REAL LINES sit under them. Every one is `leading`. ! So `addresser.py:28`
      -- *"EVERY LINE HAS EXACTLY ONE ADDRESS, AND A PARAGRAPH IS JUST THE LINES
      THAT SHARE ONE"* -- was false by 595 lines in its own directory.
- [x] T2 | FINISHED | unknown | T2 -- ! THE SECOND CLAUSE IS STILL TRUE AND IS
      THE ONE DOING THE WORK. *"A paragraph is just the lines that share one"*
      refuses the range reading, which is what the paragraph exists to refuse --
      three sessions in one day reached for a range after it was settled. ! Only
      the UNIVERSAL was wrong, so this was a `correct`, not a `drop`.
- [x] T3 | FINISHED | unknown | T3 -- ! IT WAS TRUE WHEN WRITTEN AND A LATER
      RULING BROKE IT. Roy, 2026-08-22: *"LEADING TAKES A SYMBOL AND NOT A
      PLACE"* -- `emit` is what MAKES a place and a blank run is not one. !
      Nothing re-read the addressing docstring afterward, which is the shape
      this whole repo exists to catch: a ruling lands in one module and the
      sentence stating the invariant sits in another.
- [x] T4 | FINISHED | unknown | T4 -- ! `owes_address` ALREADY EXISTS BECAUSE OF
      THIS EXACT GAP, and its docstring carries the measurement: two callers
      disagreed, and a census printed *"8542 of 8542 paragraphs addressed"*
      while 392 carried none. ! So the CODE was reconciled 2026-08-22 and the
      PROSE forty lines up was not.
- [x] T5 | FINISHED | unknown | T5 -- * AND THE OPPOSITE FIX WAS ON THE TABLE,
      so the sentence was not corrected before the ruling. Roy, 2026-08-23:
      *"Every line is a place."* ! If leading took a place, the universal would
      become true rather than needing narrowing -- and `path@cue` would become
      PAGE AND LINE, which is how a proof is cited in the trade (*"p. 12, l.
      7"*), the only difference being that the second half is a stable name
      instead of a counted position. ! ANSWERED by T7: it does not.
- [x] T6 | FINISHED | unknown | T6 -- ! WHAT IT COSTS EITHER WAY. Narrow the
      sentence and leading stays a symbol, the 2026-08-22 ruling stands, and
      `cue` still needs a word. Give leading a place and the ruling reverses,
      `emit` has to make something for a blank run, and `Kind.holds_no_prose` /
      `Kind.occupies_no_lines` -- which part on exactly leading -- stop
      differing.
- [x] T7 | FINISHED | unknown | T7 -- RULED 2026-08-23, AND IT CLOSES THE
      STARRED TASK ABOVE: leading does not get a place, so the sentence is
      NARROWED rather than made true. Roy: *"We tried leading getting a place.
      We tried several different ways. The constraints of coding AND editing do
      not allow it."* ! It was ATTEMPTED, which the git history shows in three
      commits -- `875b0d4` a fifth series, `b998a60` the edge repair, `c27ea1d`
      the retreat to a symbol. Recorded so a fourth attempt is not made.
- [x] T8 | FINISHED | unknown | T8 -- DONE 2026-08-23. Roy's two reasons are in
      `addresser.py` beside the narrowed sentence: `addresser.py:18-19` carries
      *"NO LINE HAS MORE THAN ONE"*, `addresser.py:30` points from it to
      `owes_address`, and that docstring at :1361-1377 states both -- WHERE
      everything below an edit shifted to, and HOW MUCH blank belongs where
      afterwards, *"the second being a typographic judgement no rule computes"*
      -- followed by why the edge shape holds: *"this system never chooses an
      amount of blank, it replays what it read."*
