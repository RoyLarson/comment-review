# The census is mostly intervals nobody rules on, and it is two thirds of the start cost

```
Status:   open
Progress: 0 of 7 tasks done
Owner:    session * Roy (* 1 ruling -- whether the filter ships, given it revisits
          a cost he accepted on 2026-08-17)
Raised:   2026-08-18, from measuring what a reviewer is handed before it works
```

## Objective

Every interval between two lines of code is enumerated so that `add` and `move` have an index
to cite -- ruled 2026-08-17, and the cost was named and accepted then:
*"I don't see a way around this pseudo-concrete syntax tree and I don't think it matters."*
**Measured 2026-08-18, it is the largest single thing a reviewer is handed.**

Roy, 2026-08-18, naming the way around it: a tool retrieves the correct spot from the
enumerated spots, the agents are sent only the FILTERED places, and they call the tool when
they need a place outside the filter.

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

- [ ] * **Rule whether the filter ships.** It revisits a cost ruled acceptable on 2026-08-17,
      with a measurement that did not exist then. ! The counter-argument to weigh: a reviewer
      holding the whole census can see that a gap is BETWEEN two named declarations without
      asking anything, and a filtered census plus a tool call is two steps where there was one.

- [ ] **Write the lookup, and decide what it answers.** At least: which interval lies between
      two given lines, and which interval sits above or below a named declaration -- the
      `add`'s anchor question, in the reviewer's own terms. ! It answers with the index from
      the FULL census, which is the only thing that makes the filtered one citable.

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

## Related

- [`an-empty-interval-has-no-census-index`](completed/an-empty-interval-has-no-census-index.md)
  -- why every interval is enumerated, and the cost accepted at the time
- [`the-harness-cannot-run-the-system-it-grades`](the-harness-cannot-run-the-system-it-grades.md)
  -- the same start-cost question from the test side, where one role on one file is the unit
- [`a-scope-declaration-costs-as-much-as-a-finding`](a-scope-declaration-costs-as-much-as-a-finding.md)
  -- the other place a reviewer spends output on blocks it does not rule on
