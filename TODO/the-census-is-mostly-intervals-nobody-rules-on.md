# The census is mostly intervals nobody rules on, and it is two thirds of the start cost

```
Status:   in-progress
Progress: 13 of 25 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-18, from measuring what a reviewer is handed before it works
Triaged:  2026-08-23 -- the filter SHIPPED and is what stage 4 hands a reviewer. Eleven
          of the twenty boxes were rulings, measurements or reasoning, or had landed;
          the destination check and the operation question were both settled, the second
          the opposite way from the box that proposed it
Split:    2026-08-23 -- boxes cut to two lines. The round-1 grow held one place and every
          role, the census-reader box held a survey and its cross-check, and the
          placeholder box held one placeholder and all of them; 22 boxes became 25
Measured: 2026-08-24 — the two-artifact design ruled here on 2026-08-18
          was already BUILT BY HAND once. A full v0.2 dogfooding run produced a full
          census for the machine and a prose-only one for the reviewer, 171 of 3333
          blocks -- 5.1 percent -- and split the dispatch packet the same way. ! It
          never reached the tool. ! And the cost of not having it, measured today on the
          JSON: one page of page.py is 429,239 bytes, 1,716,956 across four roles; prose
          rows carrying only the fields that carry information is 2 percent of that. !
          T19 is now a plan box, sequenced AFTER the field cut on Roys ruling: deciding
          the form while the content is still wrong would rule on fields the cut
          removes.
Re-asked: 2026-08-24 — the 2026-08-18 filtered-view ruling is RE-OPENED
          rather than carried forward. Roy: this was ruled when I could not trust the
          system to work period. It may not be necessary now, because page loading and
          address querying should be able to return the record correctly without messing
          up the rest of the system. ! A pre-filtered file is what you build when you
          CANNOT ASK -- a binder that answers give me this page, or what is the address
          of this line, makes the copy unnecessary rather than smaller. See decision-log
          Addressing 9. ! And the field cut may answer it on its own: prose rows
          carrying only the fields that carry information are 2 percent of the full
          census, and a view exists to make a large thing small.
```

## Objective

Every place between two lines of code is enumerated so that `add` and `move` have an index to
cite -- ruled 2026-08-17. **Measured 2026-08-18, that artifact was the largest single thing a
reviewer was handed.**

Roy, 2026-08-18: a tool retrieves the correct spot from the enumerated spots, the agents are
sent only the FILTERED places, and they call the tool when they need a place outside the filter.

!! **THIS DOES NOT REVERSE THE 2026-08-17 RULING; IT DEPENDS ON IT.** Roy, 2026-08-18: *"We had
to enumerate everything first -- I was right about that. We had to get here before we could get
back to the cheaper answer."* Three things follow, and they are the frame for everything below:

- **`add` was not expressible before it.** The finding is about an EMPTY place, and with no index
  for one, an `add` had to borrow a neighbouring paragraph's. Enumeration is what made the verdict
  statable at all.
- **The filter is a PROJECTION of the full enumeration, not an alternative to it.** The lookup
  returns an address FROM the full census; the filtered view is citable only because the complete
  one exists underneath.
- **The measurement could only be taken here.** Which gaps get cited, by which role, is a fact
  about runs -- and there were no runs until the census could express the whole pipeline.

! So what changed is not the ARTIFACT but WHO CARRIES IT. The census on disk stays fully
enumerated; the copy pasted into a reviewer's prompt is not the whole thing.

## What has SHIPPED, verified 2026-08-23

**Stage 3 writes three files and the reviewer gets the third.** `SKILL.md:338-348`:
`census.txt`, `census.json`, and `dispatch.txt` from `census.py --filtered`. Re-measured
2026-08-19 over 6,828 paragraphs: **397,685 bytes to 159,316**, and every reviewer gets an
identical copy, so a four-role run saves 953,476.

**The collapse is on the KIND CLASS, not on one kind.** `census.py:576` collapses every
`Kind.holds_no_prose(b.kind)` place into one run row. Verified over `census.py` and `desk.py`:
642 filtered rows against 1,766 full, **0 bare `margin` rows**, 62,127 bytes against 146,078.
! The 2026-08-19 reopening -- `--filtered` collapsing only `interval`, so 1,627 bare `margin`
rows reached each reviewer -- is closed.

**A run NAMES ITS ADDRESSED ENDS and everything between is still citable.** `SKILL.md:357-361`:
*"DO NOT SHIP THE FILTER WITHOUT A WAY TO NAME WHAT IT COLLAPSED ... A run NAMES ITS ENDS --
`@b7..b12` -- and `addresser.py --anchor` resolves any place in between."* The collapsed row also
counts what it swallowed (`47-intervals`, `3-leadings, 3-margins`), so a reviewer can still see
that a gap exists. A collapsed row reads
`227-234  @c1..b7  122-129  no-prose  0L  2-intervals, 6-margins`, and `SKILL.md:357-361` states
why the naming is not optional: without it a reviewer cannot cite what was collapsed, and
*"filtering without that is worse than not filtering."*

**The projection is documented and the citation is the ADDRESS, not the index.**
`SKILL.md:350-355`: *"Every paragraph keeps the ADDRESS it holds in the FULL census ... The index
in the first column is a READING AID for a human scanning the listing, and nothing cites it."*
! That is a stronger property than the box asked for, and nothing tests it.

## What the finished boxes settled

**The lookup is `scripts/addresser.py`.** In goes a line, out comes the address of the place
there: `addresser.py --census <CENSUS> --anchor LINE --series a|b|c`. ! It stayed narrow, which
was the instruction -- every extra question is a second way to name a place, and one way to name
a place is the property this design buys.

**A destination that is not an address is refused, which is rule 4.** `desk.py:508-553`: a `move`
naming a LINE inside a file this run cued is refused with *"that form was retired: ask
`addresser.py --anchor LINE --series a|b|c` for the address"*; a `move` naming an address
resolves through `entry_for` and is refused by name when the census has no such place. ! It also
distinguishes a wrong address from a right address for an uncued file, which two causes used to
share one message.

**The record carries NO `side`, which is the OPPOSITE of what the box proposed.** The box wanted
`{"op": "insert", "anchor": ..., "side": "above"}`. `record.py:327-332` refuses that and says
why: *"NO `side`. The ADDRESS carries it: an `a` is a declaration's documentation, a `b` is a
gap, a `c` is the room beside a line of code ... A second statement of one fact can disagree with
the first, and this one did -- measured 2026-08-19, an `add` on a `c` address passed the gate
carrying `side: above`, and there was no `beside` to write instead."* ! The consumers stopped
inferring too: `galley.reset` works by CUE (`galley.py:141-153`), not by branching on
`kind == "interval"`.

## ! Why the filter is safe: empty places serve CITATION, not DISCOVERY

**An `add` is found by reading the CODE, not by reading the census.** Its finding is that a
constraint holds in code and appears in NO prose -- there is nothing in the census to notice,
because the entry is empty by definition. What the census supplies is the ADDRESS to cite once
the reviewer has already found the gap.

! Measured on the 2026-08-17 cycle run: `ownership-context` filed the run's only `add` on an
empty place, and its reason is drawn entirely from the code -- two enforcement sites for one
constraint, prose at one of them.

!! **So filtering costs the CITATION and nothing else, and a lookup restores exactly that.**
That is the argument the ruling rests on; if it is wrong, the filter is wrong. **T11 is what tests
it**, and the cycle run on disk in `evidence/cycle-0.2.3/` carries the record files that are its
answer key.

## What else reads the census, and where the four readers disagree

`verdicts.py`, `galley.py`, `record.py` and `addresser.py` all take the census, and only the
REVIEWER's copy is filtered: the filter is a view for dispatch, not a change to the artifact on
disk. ! Measured 2026-08-23, this is not only a survey -- three of the four unwrap a dict census
with their own copy of the same expression and `verdicts.py:332` does not, so the same file loads
in three readers and gives an `AttributeError` in the fourth.
[`the-bridge-landed-and-the-rewrite-did-not`](the-bridge-landed-and-the-rewrite-did-not.md) owns
that seam.

## What a reviewer is told to run, and cannot resolve

`reviewer-brief.md:210` tells a reviewer to run
`python <skill>/scripts/addresser.py --census <FULL CENSUS> --anchor LINE --series a|b|c`.
`run_context.PATH_SECTIONS` is `("REPO ROOT", "CENSUS", "LOOKUP CENSUS", "REVIEWER FILES")`, and
`REVIEWER FILES` -- the only section holding plugin paths -- is in `TASK_AGENT_ONLY` and withheld
from reviewers, while `SKILL.md` insists *"An agent is GIVEN what it needs, and is never sent
looking."* ! `<FULL CENSUS>` names no section either; the field is `LOOKUP CENSUS`.

**And the `kind` column has no legend anywhere a reviewer reads.** Measured 2026-08-23, the
listing prints `docstring`, `comment`, `trailing-comment`, `margin`, `interval`, `leading`,
`dark-matter`, `undocumented` and `no-prose` (the collapsed run). `reviewer-brief.md` names
`interval`, `undocumented` and `margin` and never names `leading`, `dark-matter` or `no-prose` --
which between them are most of the rows. ! The only legend in the tree is in `SKILL.md`, which
reviewers never see.

## What it cost, per reviewer, before any work is done

| | galley.py | verdicts.py + record.py |
| --- | --- | --- |
| paragraphs / of them prose | 110 / 11 | 1,120 / **154** |
| brief | 22,940 | 22,940 |
| vocabulary | 3,525 | 3,525 |
| packet | 3,906 | 3,964 |
| **census** | 12,193 | **131,353** |
| seeded record | 3,131 | 33,461 |
| **to start ONE reviewer** | **45,695** | **195,243** |

!! **THIS TABLE IS A ROTTED MEASUREMENT and is kept as the baseline the filter is scored
against, not as a current fact.** It was taken 2026-08-18, before `margin` and `leading` existed
and before the filter shipped; the same two files census to 3,359 paragraphs today. Re-take it
with a successor measurement rather than quoting it.

## ! The page rendering -- PROPOSED 2026-08-21, DEFERRED, not ruled

Roy, 2026-08-21: *"I might be convinced that the addressing per anchor/line would be useful for
the agents ... I think this is a valuable concept."* He also deferred it: *"this doesn't need my
attention just yet"*, so `Requires-Roy` stays FALSE -- it was cleared 2026-08-19 for a stated
reason, and a proposal awaiting a look is not a decision owed today.

**The renderer is in the tree as `scripts/render_page.py`** so nobody re-derives the numbers.
MEASURED 2026-08-21 over 26 files -- every shipped script, this repo's `scripts/`, plus
`corpora/cpython/Objects/listobject.c` and `corpora/sentry/eslint.config.ts`: rows 1,635,544
bytes, margin 1,088,304 (-33%, smaller on 23 of 26), prose-only 1,029,443 (-37%).

!! **THE TWO FORMATS COST DIFFERENT THINGS and that predicts where each wins:** ROWS pays per
PLACE, MARGIN pays per LINE. Code-heavy files have an empty place between every pair of
statements, each a row with its anchor repeated -- `listobject.c` -50%, `eslint.config.ts` -51%.
The three files the margin LOSES on are prose-dense with little code: `addresser.py` +7%,
`desk.py` +9%, `page.py` level. ! **The ratio tracks CODE DENSITY, not language**, which is what
a one-Python-file measurement could not have shown. ! This supersedes the single-file number
(`scripts/check_vocabulary.py`: 25,950 bytes of rows, 21,535 of margin, 19,242 prose-only,
15,076 the file itself), which was one Python file that is 40% docstring.

**It composes with the filtered handout rather than replacing it.** Roy, 2026-08-18: *"a tool
retrieves the correct spot from the enumerated spots ... and they call the tool when they need a
place outside the filter."* The margin rendering is a candidate for what that TOOL RETURNS -- a
display a reviewer calls up, which is the tool this TODO already ruled.

**And the records belong on it.** Roy, 2026-08-21: *"the records though also need to be
potentially explicitly shown or retrievable. Because they are supposed to mark on the records
what is supposed to happen."* A reviewer MARKS a manuscript; a page showing addresses but not the
marks against them is a proof with no editorial marks on it. That half does not exist, and it is
a requirement ON the deferred proposal rather than work today.

**What is still open in the proposal, none of it ruled:** whether an EMPTY place gets a row in
position (its value is entirely positional -- an `add` cites it) or is listed under the page;
whether the page is text or structured; and the margin's own format, which was invented for the
mock-up and matches nothing in the tree.

## Tasks

- [x] T1 | FINISHED | unknown | T1 -- RULED 2026-08-18: the filter ships and the
      reviewer is handed the TOOL, not the whole census. The ruling and what
      follows from it are in the Objective.
- [x] T2 | FINISHED | unknown | T2 -- FINISHED. The lookup is
      `scripts/addresser.py --census <CENSUS> --anchor LINE --series a\|b\|c`.
      Why it stayed that narrow is in the Objective.
- [x] T3 | FINISHED | unknown | T3 -- FINISHED. A `move` destination that is not
      an address is refused, which is rule 4. The two refusal messages are
      quoted in the Objective.
- [ ] T4 | T4 -- Grow the filtered table between rounds so rule 5 holds at 5b.
      Verify: a place cited in round 1 appears in the round-2 handout.
- [ ] T5 | T5 -- Grow it for EVERY role, not only the role that cited. Verify:
      all four round-2 handouts carry that place.
- [ ] T6 | T6 -- Test that a filtered census carries every prose paragraph's
      ADDRESS unchanged from the full one. Verify: a multi-file census test
      fails if any address differs.
- [x] T7 | FINISHED | unknown | T7 -- FINISHED, and neither "drop them" nor
      "keep them": a run of prose-less places collapses to ONE row that names
      its ends. Example in the Objective.
- [x] T8 | FINISHED | unknown | T8 -- FINISHED for the byte half, re-measured
      2026-08-19 (`SKILL.md:346-348`). ! The other half of the claim -- *without
      a verdict changing* -- is T11's.
- [ ] T9 | T9 -- Record which of `verdicts.py`, `galley.py`, `record.py` and
      `addresser.py` read the census in full. Verify: each of the four is named
      here as full or filtered.
- [ ] T10 | T10 -- Check that survey against T8 of
      `the-bridge-landed-and-the-rewrite-did-not`. Verify: both name the same
      set of full-census readers.
- [ ] T11 | T11 -- Re-run `evidence/cycle-0.2.3/` filtered and full and diff the
      verdicts. Verify: the mix differs only in which places were cited, or the
      filter is wrong.
- [x] T12 | FINISHED | unknown | T12 -- FINISHED, and the OPPOSITE of what the
      box proposed: the record carries no `side`, because the address carries
      it. `record.py:327-332`, in the Objective.
- [x] T13 | FINISHED | unknown | T13 -- FINISHED. `--filtered` collapses on
      `Kind.holds_no_prose` (`census.py:576`), not on one kind. Verified
      2026-08-23: 0 bare `margin` rows over two shipped scripts.
- [ ] T14 | T14 -- Resolve `<skill>` in `reviewer-brief.md:210` to a path a
      reviewer is given. Verify: it comes from a packet section not in
      `TASK_AGENT_ONLY`.
- [ ] T15 | T15 -- Resolve `<FULL CENSUS>` in `reviewer-brief.md:210`; the
      packet field is `LOOKUP CENSUS`. Verify: the file names that field
      instead.
- [ ] T16 | T16 -- Check every other placeholder in `reviewer-brief.md`. Verify:
      each names a packet section a reviewer is given.
- [ ] T17 | T17 -- Define every `kind` the census listing can print where a
      reviewer reads it. Verify: each of the nine kinds measured 2026-08-23 is
      in `reviewer-brief.md`.
- [ ] T18 | T18 -- Ship a column legend with the census listing itself. Verify:
      a filtered listing handed to a reviewer carries a legend, without reading
      `SKILL.md`.
- [ ] T19 | T19 -- * Rule the page rendering, deferred by Roy 2026-08-21; the
      open questions are in the Objective. Verify: the ruling is in
      `docs/decision-log.md`.
- [x] T20 | FINISHED | unknown | T20 -- Not a task. The single-file rendering
      number was a MEASUREMENT and is superseded by the 26-file run. Both are in
      the Objective.
- [x] T21 | FINISHED | unknown | T21 -- FINISHED. "Re-measure across languages"
      was done 2026-08-21: the 26-file run includes a `.c` and a `.ts`, and
      those are where the margin wins hardest.
- [x] T22 | FINISHED | unknown | T22 -- Not a task. "THE RECORDS BELONG ON THE
      PAGE" is a requirement ON the deferred proposal and is in the Objective.
      It becomes work the day T19 is ruled.
- [x] T23 | FINISHED | unknown | T23 -- Not a task. "IT IS A DISPLAY THEY CALL
      UP" is the argument that the rendering composes with the filtered handout
      rather than replacing it. Kept in the Objective.
- [x] T24 | FINISHED | unknown | T24 -- Not a task. "WHAT IS STILL OPEN in the
      proposal" enumerates three unruled questions; they are what T19 rules on,
      and they are listed in the Objective.
- [x] T25 | FINISHED | unknown | T25 -- Not a task. The 26-file measurement is a
      MEASUREMENT, and `scripts/render_page.py` is in the tree so it can be
      re-taken. In the Objective.
## Related

- [`verdicts-py-announces-one-subject-and-holds-four`](completed/verdicts-py-announces-one-subject-and-holds-four.md)
  -- COMPLETED. The split that moved the checks to `desk.py` and the reader to `held.py`, which
  is why the lookup and the verdict table are no longer in one 2,000-line file
- [`an-empty-interval-has-no-census-index`](completed/an-empty-interval-has-no-census-index.md)
  -- why every place is enumerated, and the cost accepted at the time
- [`the-harness-cannot-run-the-system-it-grades`](the-harness-cannot-run-the-system-it-grades.md)
  -- the same start-cost question from the test side, where one role on one file is the unit
- [`a-scope-declaration-costs-as-much-as-a-finding`](a-scope-declaration-costs-as-much-as-a-finding.md)
  -- the other place a reviewer spends output on paragraphs it does not rule on
