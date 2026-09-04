# The bridge landed and the rewrite did not

```
Status:   in-progress
Progress: 8 of 11 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-17, by /simplify over the 0.2.3 branch
Updated:  2026-08-18 -- the cycle is gone and the claim is typed at the seam
Triaged:  2026-08-23 -- the modules moved. `load_report` is now `held.py`, the checks
          are `desk.py`, and `ruled_text` reads the FIELD first with the string scan
          as fallback. Two boxes restated the same task; the census-reader count was
          re-taken and is four, not five
Split:    2026-08-23 -- the census-reader box held a mechanical change AND the
          behaviour it buys, and is now two; every finished box is cut to what it
          finished, with its evidence in the Objective
```

## Objective

`claim_text` renders a record's typed `claim` OBJECT back into the marker STRING the checks read,
and its own docstring calls that a bridge, kept *"before anything is rewritten to read the object
directly."* **The bridge shipped; the rewrite is half done.**

! **Generate-then-reparse is the defect class the record change exists to end** -- D7, D8 and D9,
all three of them a boundary guessed wrong. It happening inside one module instead of between a
reviewer and a parser is better, and is not the same as fixed.

**What has landed since this was filed.** The cycle is inverted: `record.py` imports from
`addresser` and `lexer` and NOTHING from `verdicts.py`, while `verdicts.py` imports from
`record`, `desk` and `held`. The reader moved out of the collator into `held.py`, whose own docstring
says why -- *"Reading a record file back -- the third verb on the noun `record.py` owns"*.
`ruled_text` (now `desk.py:721`) reads the field first: `desk.py:743-745`, *"THE FIELD FIRST, and
the scan below is now the FALLBACK."*

**What has not.** `held.py:161` still builds `Finding.claim` by calling `claim_text(verdict,
claim)` -- a rendered string -- and `desk.py:754-762` still marker-searches it when the field is
absent, feeding `block_problem`, `edit_problem`, `contradictions` and `unrecorded_findings`.
`held.py:172-176` still flattens `{cite, verbatim}` into `"cite | verbatim"` and `desk.py:326`
partitions it back.

!! **MEASURED 2026-08-23: FOUR READERS OF A CENSUS FILE, AND ONE CRASHES.** `addresser.py:1137`,
`galley.py:381` and `record.py:1121` each carry their own `census["paragraphs"] if
isinstance(census, dict) else census`; `verdicts.py:332` does not. Run against a
`{"paragraphs": [...]}` census, `verdicts.py` raises `AttributeError: 'str' object has no
attribute 'get'` from `addresser._by_path`. ! The key is `paragraphs`, not `blocks` -- the
2026-08-19 reading named five readers and the wrong key, and two of the modules it named
(`cues`, `locator`) no longer exist. `census.py:439` and `:290` emit a bare list unconditionally,
so nothing in this tree exercises the other branch either way.

! **`galley.unanswerable` is already half of the seam** the census reader wants.

## What the flattened `sources` cost, and what remains

!! **IT WAS A LIVE DEFECT.** A source carrying `"verbatim": null` rendered the word "None" and
PASSED, because the cited line contained it. Fixed 2026-08-18 by putting both halves through
`_half`, so what remains is the ROUND TRIP itself -- a cite containing `|` still splits wrong.
! Blast radius is ~20 test call sites that use the string form as a literal.

## What the finished boxes finished, kept as their evidence

- **T1/T2 (`3645aad`)** landed in the reader where the two formats met. Both formats arrived
  typed; a text record used to leave `claim_fields` empty and every check fell back to searching
  a rendered string. Verified on the case the task named:
  `false: "the cap is 5 / true: not really"` returns the whole value from the field and truncates
  to `the cap is 5` under the scan. ! `ruled_text` is what `block_problem`, `edit_problem` and
  `contradictions` compare on, so a truncated original is a finding checked against the wrong
  sentence.
- **T3 (RULED 2026-08-18)**: the verdict table lives in `record.py`, which already derived
  `allowed()` from it and imported six names back.
- **T4**: `held.py` holds `load_report` and `held_records` and imports `Finding`, `_half`,
  `address_for`, `claim_text` and `every_record` from `record.py`; `verdicts.py:103` now does
  `from held import load_report`. `record.SHAPES` (`record.py:890`) is the declaration of the
  field names and types.
- **T5 (`e32c12b`)**: all five `claim_help` rows name `claim.<key>` instead of the retired marker
  form, and four tests that asserted the old phrasing now assert the KEY.
- **T7 (`0599091`)**: `ANCHOR_EXAMPLE` is one string -- published in the form and run against the
  pattern -- and two tests hold them equal. ! Verified by MUTATION: loosening the pattern to `.*`
  fails three tests.
- **T11** was the measurement *"IT IS FIVE READERS, NOT THREE"*, and it was overtaken: the census
  key is `paragraphs`, two of the five modules it named are gone, and the count re-taken
  2026-08-23 is four. The crash it recorded is real and is what T8 and T9 close.

## Tasks

- [x] T1 | FINISHED | unknown | T1 -- FINISHED `3645aad`, in the reader where
      the two formats met. Evidence in the Objective.
- [x] T2 | FINISHED | unknown | T2 -- FINISHED `3645aad`, verified on the case
      the task named. Evidence in the Objective.
- [x] T3 | FINISHED | unknown | T3 -- * RULED 2026-08-18: the verdict table
      lives in `record.py`. The inversion holds, verified 2026-08-23.
- [x] T4 | FINISHED | unknown | T4 -- FINISHED. The reader left the module that
      does not own the format; it is `held.py` now. Evidence in the Objective.
- [x] T5 | FINISHED | unknown | T5 -- FINISHED `e32c12b`. All five `claim_help`
      rows name `claim.<key>`, and four tests assert the KEY.
- [x] T6 | FINISHED | unknown | T6 -- SUPERSEDED. This box and T10 were the same
      task filed twice, three lines apart. T10 carries the correction this one
      got wrong, so T10 is the copy that stays.
- [x] T7 | FINISHED | unknown | T7 -- FINISHED `0599091`. `ANCHOR_EXAMPLE` is
      one string, held equal by two tests and verified by mutation.
- [ ] T8 | T8 -- Move the census dict-unwrap into `census.py`, the module that
      owns the format. Verify: no module outside `census.py` spells
      `isinstance(..., dict)` on a census.
- [ ] T9 | T9 -- Make all four census readers agree on a `{"paragraphs": [...]}`
      census. Verify: all four load it, or all four refuse it with one message.
- [ ] T10 | T10 -- Make `Finding.sources` a typed pair instead of a flattened
      string. Verify: nothing splits on `\|`, and a cite containing `\|`
      round-trips.
- [x] T11 | FINISHED | unknown | T11 -- Not a task, and its content is now in
      the Objective above: "IT IS FIVE READERS, NOT THREE" was a MEASUREMENT,
      and it was overtaken by the count of four.
## Related

- [`the-parser-merges-across-boundaries-it-cannot-read`](the-parser-merges-across-boundaries-it-cannot-read.md)
  -- D7, D8 and D9, the three defects that made the record a value.
- [`the-record-is-a-parsed-template-and-should-be-a-value`](completed/the-record-is-a-parsed-template-and-should-be-a-value.md)
  -- the change that built the bridge, and the ruling that it was temporary.
