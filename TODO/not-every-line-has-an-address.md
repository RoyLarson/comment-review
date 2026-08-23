# The addressing docstring states a universal that leading refutes

```
Status:   open
Progress: 0 of 8 tasks done
Owner:    backend
Requires-Roy: true
Raised:   2026-08-23 (Roy, 2026-08-23: "Every line is a place" -- measured false by 595
          lines, all leading, on the day leading was ruled a symbol rather than a place)
Ruled:    2026-08-23 — leading does not get a place -- tried several ways and refused;
          the sentence is narrowed, and cue still needs its word
```

## Objective

**595 real lines carry no address, every one of them `leading`, under a docstring stating that
every line has exactly one.** MEASURED 2026-08-23 on the 19 shipped scripts: 8,746 paragraphs
over 11,009 lines, 401 with no address. So `addresser.py:28` -- *"EVERY LINE HAS EXACTLY ONE
ADDRESS, AND A PARAGRAPH IS JUST THE LINES THAT SHARE ONE"* -- is false in its own directory.

!! **RULED 2026-08-23: THE SENTENCE IS NARROWED. LEADING DOES NOT GET A PLACE.** Roy, closing it:
*"We tried leading getting a place. We tried several different ways. The constraints of coding AND
editing do not allow it. It makes the shifting impossible to correctly determine and lay the prose
back in."*

! **THAT IS THE OPERATIVE REASON AND IT WAS NOT IN THE RECORD.** `1728d8a` already carries three
others -- a `d` has no anchor so it fails the substitution, `""` being the ABSENCE of an answer
rather than one; every other place exists because the walk reached a trigger and THE TRIGGER IS
THE ANCHOR, while a `d` exists only because the lexer found blank lines; and publishing agreeing
independently, since leading is a MEASUREMENT of the type it accompanies ("10 on 12") and a
measurement cannot be anchored, only the thing measured can. **What none of them says is what
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

! **WHAT IS LEFT IS ONE CORRECTION, AND IT IS NARROW.** The second clause -- *"a paragraph is just
the lines that share one"* -- is TRUE and is the clause doing the work, refusing the range reading
that three sessions in one day reached for. Only the universal is wrong. This is a `correct`, not
a `drop`.

! **AND `cue` STILL NEEDS ITS WORD**, so [[leaf-means-two-things]] stays live rather than
dissolving. A cue numbers a page or a leaf; the `@` half numbers a place on a page, which the
trade never needed a word for.

## Tasks

- [ ] MEASURED 2026-08-23 ON THE 19 SHIPPED SCRIPTS: 8,746 paragraphs over 11,009
      lines; 401 carry NO address, and 595 REAL LINES sit under them. Every one is
      `leading`. ! So `addresser.py:28` -- *"EVERY LINE HAS EXACTLY ONE ADDRESS,
      AND A PARAGRAPH IS JUST THE LINES THAT SHARE ONE"* -- is false by 595 lines
      in its own directory.
- [ ] ! THE SECOND CLAUSE IS STILL TRUE AND IS THE ONE DOING THE WORK. *"A
      paragraph is just the lines that share one"* refuses the range reading,
      which is what the paragraph exists to refuse -- three sessions in one day
      reached for a range after it was settled. ! Only the UNIVERSAL is wrong, so
      this is a `correct`, not a `drop`.
- [ ] ! IT WAS TRUE WHEN WRITTEN AND A LATER RULING BROKE IT. Roy, 2026-08-22:
      *"LEADING TAKES A SYMBOL AND NOT A PLACE"* -- `emit` is what MAKES a place
      and a blank run is not one. ! Nothing re-read the addressing docstring
      afterward, which is the shape this whole repo exists to catch: a ruling
      lands in one module and the sentence stating the invariant sits in another.
- [ ] ! `owes_address` ALREADY EXISTS BECAUSE OF THIS EXACT GAP, and its docstring
      carries the measurement: two callers disagreed, and a census printed *"8542
      of 8542 paragraphs addressed"* while 392 carried none. ! So the CODE was
      reconciled 2026-08-22 and the PROSE forty lines up was not.
- [ ] * AND THE OPPOSITE FIX IS ON THE TABLE, so do not correct the sentence
      before ruling. Roy, 2026-08-23: *"Every line is a place."* ! If leading
      takes a place, the universal becomes true rather than needing narrowing --
      and `path@cue` becomes PAGE AND LINE, which is how a proof is cited in the
      trade (*"p. 12, l. 7"*), the only difference being that the second half is a
      stable name instead of a counted position. ! That would dissolve `leaf-
      means-two-things` instead of settling it: there would be no cue in the
      system at all.
- [ ] ! WHAT IT COSTS EITHER WAY. Narrow the sentence and leading stays a symbol,
      the 2026-08-22 ruling stands, and `cue` still needs a word. Give leading a
      place and the ruling reverses, `emit` has to make something for a blank run,
      and `Kind.holds_no_prose` / `Kind.occupies_no_lines` -- which part on
      exactly leading -- stop differing.
- [ ] RULED 2026-08-23, AND IT CLOSES THE STARRED TASK ABOVE: leading does not get
      a place, so the sentence is NARROWED rather than made true. Roy: *"We tried
      leading getting a place. We tried several different ways. The constraints of
      coding AND editing do not allow it."* ! It was ATTEMPTED, which the git
      history shows in three commits -- `b8e3348` a fifth series, `bb2be6c` the
      edge repair, `1728d8a` the retreat to a symbol. Recorded so a fourth attempt
      is not made.
- [ ] ! PUT ROY'S TWO REASONS INTO `addresser.py` BESIDE THE NARROWED SENTENCE.
      `1728d8a` already carries the substitution argument, the trigger-is-the-
      anchor cause and the measurement analogy; none of them says what breaks
      DOWNSTREAM. ! Make the slack addressable and neither the SHIFTING nor the
      AMOUNT can be determined -- and the amount is a typographic judgement, not a
      computation. The edge shape works because it replays what it read instead of
      choosing.
