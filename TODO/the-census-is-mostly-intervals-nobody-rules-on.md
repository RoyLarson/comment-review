# The census is mostly intervals nobody rules on, and it is two thirds of the start cost

```
Status:   open
Progress: 2 of 13 tasks done
Owner:    session (Roy ruled the design 2026-08-18; the rest is build)
Requires-Roy: true
Raised:   2026-08-18, from measuring what a reviewer is handed before it works
Reopened: 2026-08-19 — --filtered stopped filtering when the margin kind arrived: only
          intervals collapse, so 1,627 bare margin rows now reach each reviewer. Its
          cost table is a rotted measurement
```

## Objective

Every interval between two lines of code is enumerated so that `add` and `move` have an index
to cite -- ruled 2026-08-17. **Measured 2026-08-18, that artifact is the largest single thing a
reviewer is handed.**

Roy, 2026-08-18: a tool retrieves the correct spot from the enumerated spots, the agents are
sent only the FILTERED places, and they call the tool when they need a place outside the
filter.

!! **THIS DOES NOT REVERSE THE 2026-08-17 RULING; IT DEPENDS ON IT.** Roy, 2026-08-18: *"We had
to enumerate everything first -- I was right about that. We had to get here before we could get
back to the cheaper answer."* Three things follow from that and they are the frame for
everything below:

- **`add` was not expressible before it.** The finding is about an EMPTY interval, and with no
  index for one, an `add` had to borrow a neighbouring block's. Enumeration is what made the
  verdict statable at all -- the record could not hold the finding until the gap had a name.
- **The filter is a PROJECTION of the full enumeration, not an alternative to it.** The lookup
  returns an index FROM the full census; the filtered view is citable only because the complete
  one exists underneath. Ship the cheap form without the expensive one and every citation
  resolves to nothing.
- **The measurement could only be taken here.** Which gaps actually get cited, by which role,
  and reasoned from what, is a fact about runs -- and there were no runs until the census could
  express the whole pipeline.

! So what changes is not the ARTIFACT but WHO CARRIES IT. The census on disk stays fully
enumerated; the copy pasted into a reviewer's prompt stops being the whole thing. The cost
ruled acceptable in 2026-08-17 is still paid -- once, on disk, by the tool -- rather than four
times, in four prompts.

## The design, as Roy stated it 2026-08-18

1. **The census is a HASHED STATIC TABLE** -- exact, constant, fully enumerated. It is computed
   once and addressed by index; nothing that follows edits it.
2. **The agents get a FILTERED VIEW of that table.**
3. **A destination outside their set comes from the TOOL.** They are told: if you need to move
   something to another spot in the code and it is not in your current set, use the tool to
   determine the values for the correct place.
4. !! **A RAW LINE NUMBER IS DISMISSED.** Any reference that says *put it here* by naming a
   line is not a destination and is not accepted.
   !! **A LINE NUMBER IS HOW YOU ASK; AN ADDRESS IS HOW YOU ANSWER.** The two rules only look
   contradictory: the tool TAKES a line of code, because that is what a reviewer has in hand
   after reading one, and RETURNS the address. What is refused is a line number written into a
   record as though it were a destination.
5. **After the first round, the spot joins the filtered table FOR EVERY AGENT.** A destination
   one role looked up is common ground in round 2, where a re-review rules on a joined block and
   has to see where its neighbours sent things.

### ! What rule 4 buys, beyond bytes

**`move`'s destination is the one payload in this system that NOTHING checks.** Its row requires
the `from` and `to` KEYS -- `claim_all=("from:", "to:")` -- and stops there: `quotes_original` is
empty, so `from` is not compared against the block, and no check resolves `to` at all. A `move`
can name a destination that does not exist and the join passes it.

! Making the destination a census index makes it resolvable exactly as an address already is:
the same lookup, the same failure message, the same refusal. **The cheapest form of the filter
is also the first time a relocation says somewhere real.**

! It also removes the ambiguity `LOCATION` was retired for. A line number can mean where the
prose SITS or where it SHOULD GO; an index into a table of intervals can only mean the second.

## What it costs, per reviewer, before any work is done

| | galley.py | verdicts.py + record.py |
| --- | --- | --- |
| blocks / of them prose | 110 / 11 | 1,120 / **154** |
| brief | 22,940 | 22,940 |
| vocabulary | 3,525 | 3,525 |
| packet | 3,906 | 3,964 |
| **census** | 12,193 | **131,353** |
| seeded record | 3,131 | 33,461 |
| **to start ONE reviewer** | **45,695** | **195,243** |

**966 of 1,120 blocks are intervals**, and a reviewer files a verdict on one only to place an
`add`. The census is 67% of the start cost on the larger target and every role receives an
identical copy.

## ! Why the filter is safe: intervals serve CITATION, not DISCOVERY

**An `add` is found by reading the CODE, not by reading the census.** Its finding is that a
constraint holds in code and appears in NO prose -- there is nothing in the census to notice,
because the entry is empty by definition. What the census supplies is the INDEX to cite once
the reviewer has already found the gap.

! Measured on the 2026-08-17 cycle run: `ownership-context` filed the run's only `add` on
interval block 103, and its reason is drawn entirely from the code -- two enforcement sites for
one constraint, prose at one of them. The census told it what to call the gap, not that the gap
was there.

!! **So filtering costs the CITATION and nothing else, and a lookup restores exactly that.**
That is the argument the ruling rests on; if it is wrong, the filter is wrong.

## ! Half the mechanism already exists

`record.py --seed` lays down slots for PROSE blocks only -- *"154 records seeded from 1120
blocks"* -- and `reviewer-brief.md` already tells a reviewer to APPEND a record carrying an
interval's index when it files an `add`. **The record file is already filtered; the census is
not.** The change is to filter the census the same way and give the reviewer something to ask.

## Tasks

- [x] * **RULED 2026-08-18 by Roy: the filter ships, and the reviewer is handed the TOOL.**
      Not the whole census. The tool answers one question -- *what is the ADDRESS of this line
      of code* -- and that is the whole of what a reviewer needs to place prose it cannot
      already cite.

- [x] **Write the lookup. It answers ONE question: what is the ADDRESS of this line of
      code.** Roy, 2026-08-18. In goes a line; out comes the census index and address of the
      spot there. ! Resist widening it -- every extra question is a second way to name a place,
      and one way to name a place is the property this whole design is buying.

- [ ] **Refuse a destination that is not a census index**, which is rule 4 and is enforceable
      today: `move`'s `to` is free text no check resolves. Verify: a `move` naming a line
      number is refused with the message an unresolvable address already gets, and a `move`
      naming an index resolves through the same path.

- [ ] **Grow the filtered table between rounds, for every role.** Rule 5. A spot one role looked
      up is in everyone's view at 5b, because a re-review rules on the JOINED block and must be
      able to see where a neighbour sent something. ! Whatever is added is a projection of the
      same static table -- indices never change, the view widens.

- [ ] **Keep the indices STABLE -- a projection, never a renumbering.** The filtered census
      must carry the same block numbers as the full one, or every citation resolves to the
      wrong block and the join cannot tell. Verify: a filtered census and a full one agree on
      `block -> address` for every prose block.

- [ ] **Decide what the filtered census still SHOWS about intervals.** Dropping them entirely
      hides that a gap exists at all; a one-line summary per run of code (`lines 41-52: no
      prose`) may keep the discovery half at a fraction of the bytes. ! Measure before
      choosing -- the point of this file is that the full form was never measured.

- [ ] **Measure the result against these numbers**, per reviewer and for the set. The claim to
      test is that the start cost falls by most of the census's share without a verdict
      changing.

- [ ] **Check what else reads the census in full**, because `verdicts.py`, `galley.py` and
      `record.py` all take it and only the REVIEWER's copy is being filtered. The filter is a
      view for dispatch, not a change to the artifact on disk.

- [ ] **Re-run a known case both ways and diff the verdicts.** The cycle run is on disk in
      `evidence/cycle-0.2.3/` with its four record files, so the comparison has an answer key.

- [ ] !! **STATE THE OPERATION, because an interval's range does not mean what a block's means.**
      P7 of [`two-live-runs-proposed-fifteen-changes`](two-live-runs-proposed-fifteen-changes.md):
      an interval's `path:start-end` spans the two CODE LINES bounding the gap, so a range
      replace DELETES BOTH STATEMENTS. It was caught on that run by a guard rather than by
      design. Measured 2026-08-18: `galley.py:134` and `:332` still decide insert-against-replace
      by branching on `block.get("kind") == "interval"`, and `record.py:428` scrapes the side out
      of prose with `ANCHOR_SIDE.search(claim)`. ! **Both are consumers inferring what the
      producer knows**, which is the rule 0.2.3 settled when `whole_lines` became a stated fact.
      The record should carry `{"op": "insert", "anchor": ..., "side": "above"}`. Verify: the
      galley branches on the stated op, and an `add` with no op is refused rather than guessed.
- [ ] !! **REOPENED 2026-08-19: `--filtered` stopped filtering when `margin`
      arrived.** `census.py` collapses `kind == "interval"` only, so `margin` and
      `undocumented` -- both in `HOLDS_NO_PROSE` -- print one row each. Measured
      over three shipped scripts: 3,359 blocks, **1,627 of them bare `margin  0L
      -`**, one per code line, zero information, four times per run. ! The file's
      own cost table (1,120 blocks / 131,353 bytes) is a rotted measurement; re-
      measure with it. **Collapse on `HOLDS_NO_PROSE`, not on one kind.**
- [ ] **A reviewer is told to run `&lt;skill&gt;/scripts/addresser.py` and nothing
      resolves `&lt;skill&gt;`.** The packet carries REPO ROOT, CENSUS, LOOKUP
      CENSUS and REVIEWER FILES -- and REVIEWER FILES, the only section holding
      plugin paths, is explicitly withheld from reviewers. SKILL.md insists *"An
      agent is GIVEN what it needs, and is never sent looking."* ! Also `&lt;FULL
      CENSUS&gt;` names no packet section; the field is `LOOKUP CENSUS`, and it is
      the same file.
- [ ] **Nothing tells a reviewer what the census `kind` column means.** The
      listing prints `docstring`, `comment`, `trailing-comment`, `margin`, `no-
      prose`; the brief names `interval` and `undocumented` -- words the listing
      never prints -- and never names `margin`, which is most of the rows. ! The
      listing also ships no column legend; the only one is in SKILL.md, which
      reviewers never see, and it is stale.

## Related

- [`verdicts-py-announces-one-subject-and-holds-four`](verdicts-py-announces-one-subject-and-holds-four.md)
  -- **a dependency.** The lookup tool answers with an address, `census.address` owns
  `path:start-end`, and the verdict table is where that type belongs -- today it is 300 lines
  inside a 2,000-line file
- [`an-empty-interval-has-no-census-index`](completed/an-empty-interval-has-no-census-index.md)
  -- why every interval is enumerated, and the cost accepted at the time
- [`the-harness-cannot-run-the-system-it-grades`](the-harness-cannot-run-the-system-it-grades.md)
  -- the same start-cost question from the test side, where one role on one file is the unit
- [`a-scope-declaration-costs-as-much-as-a-finding`](a-scope-declaration-costs-as-much-as-a-finding.md)
  -- the other place a reviewer spends output on blocks it does not rule on
