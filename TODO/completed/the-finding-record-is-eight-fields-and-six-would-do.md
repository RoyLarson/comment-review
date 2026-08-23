# The finding record is eight fields, six would do, and one of them is checked by nothing

```
Status:   done
Progress: 8 of 8 tasks done
Owner:    session * Roy (* 1 ruling)
Raised:   2026-08-15 (Roy: "It looks like another session got convinced by other
          sessions that they didn't have everything they needed to state what
          they wanted to do")
```

## Objective

! **Group A landed the six-field record and all four checks.** What is left is a
BUDGET decision -- which worked examples ship -- and `query` and `add` are now
ruled, so the reason they were held back is gone.

**The record shipped with five fields and now has eight, and every field added since exists to
serve the GATE, not the reviewer.** `BLOCK` and `EVIDENCE` came in with `5f14da7` (parse the
findings and gate stage 5), `QUOTE` with `cb7e361` (split QUOTE from SUMMARY). Roy's memory of
the original -- *"Line | summary | reason | and something else"* -- is `LOCATION`, `SUMMARY`,
`FINDING`, `VERDICT`, `CHANGE`, exactly as imported at `9932c3f`.

Six fields carry it, and the shape is ruled: **`BLOCK`, `VERDICT`, `CLAIM`, `SOURCE`, `REASON`,
`CHANGE`**, with the record opener `--- RECORD` so the record and its own field stop sharing a
name. Roy ruled `SOURCE` over `PROOF`, which would have collided with the `proof` level and
`prove_unchanged.py`'s AST proof.

! **The cut is not the point; the check is.** `REASON` is the field Roy's `move` ruling rests
on -- *"this comment belongs to that line there"* -- and **nothing checks it**. `LOCATION` was
checked, but only for resolvability, never against the block it claims to describe. The gate
loads the census and takes only `len(blocks)` from it.

## Tasks

- [x] Implement the six-field record in `references/reviewer-brief.md` and
      `scripts/verdicts.py`: `LOCATION` goes (derivable from `BLOCK`, which the census resolves
      to path/start/end); `EVIDENCE` + `QUOTE` merge into `SOURCE` as `file:line | verbatim`,
      split on `|` and each half checked exactly as now; `SUMMARY` splits, its left half
      becoming `CLAIM` and its derived right half folding into `REASON`; `FINDING` becomes
      `REASON`. ! **The opener is ALREADY `--- RECORD`, done 2026-08-16** -- Roy found the
      ambiguity in the brief's own example (*"is it the emitted full table or is it the row
      in the table?"*) and it was split out because it is independent of the field cut.
      ! **DONE 2026-08-17, group A tasks 4-6.** `BLOCK VERDICT SOURCE CLAIM REASON CHANGE`.
      LOCATION retired, EVIDENCE+QUOTE merged as `file:line | verbatim`, SUMMARY split with its
      derived half folding into REASON. ! A SOURCE line REPEATS rather than comma-separating,
      because verbatim text can contain a comma.

- [x] Keep `SOURCE` merged, not re-split. `EVIDENCE` and `QUOTE` were ONE field until
      `cb7e361` split them, because the old `SUMMARY` mixed verbatim with derived text and a
      checker cannot verify both in one field. `SOURCE`'s two halves are both verbatim, so the
      merge does not recreate that. ! Do not merge anything DERIVED into it.
      ! **HELD.** One field, and both halves verbatim -- which is why the merge does not
      recreate the defect that split them. Nothing DERIVED went into it: the derived side is
      REASON, and it is checked by nothing.

- [x] Add the cross-check the record never had: **does `CLAIM` appear in the census text for
      `BLOCK`?** The census carries each block's joined text and the gate already loads it. This
      catches a finding attached to the wrong block, which nothing catches today, and it is
      strictly stronger than the `LOCATION` check being removed.
      ! **DONE, task 6.** `claim_problem` matches CLAIM against the census text for its BLOCK. !
      Exempt: `clean` cites no claim, and `add` is a finding about prose that is MISSING, so its
      block is an empty interval with no sentence to quote.

- [x] Check `REASON`. Minimum: non-empty, and not merely a restatement of `CLAIM`. Today
      `Finding.finding` is read at exactly one site (`verdicts.py:539`) and only to print the
      reason a record was MALFORMED -- so for a real finding the field is decoration.
      ! `Finding.finding` is overloaded: reviewer clause, or diagnostic string when
      `block == -1`. One attribute, two meanings -- fix with it.
      ! **DONE, tasks 4 and 7.** Required non-empty, and refused when it merely restates CLAIM
      -- equality only, because a REASON that quotes the claim and then explains it is doing its
      job. ! The overload is gone too: `parse_report` returns malformed records separately, so
      the field holds one thing.

- [x] `query` DOES carry `SOURCE`. **Roy, 2026-08-15:** *"EVIDENCE + QUOTE for query means I
      looked here, and here, and here and I couldn't determine what this means."* The exemption
      rests on a conflation -- "no line SETTLES it" is not "no line to CITE" -- and
      `reviewer-brief.md` contradicts itself on it fifteen lines apart: *"You are still required
      to open the code that would settle it; on every other verdict your QUOTE proves you did"*,
      then *"A query carries no EVIDENCE and no QUOTE, by construction."* The one verdict that
      most needs proof the reviewer looked is the only one exempted from giving it. So:
      `SOURCE` goes PLURAL for a query, one entry per place examined; `evidence_problem()` stops
      exempting it and checks each the same way as every other verdict; what stays unenforceable
      is whether those were the right places, which is judgment and always was.
      ! Residual, small: `QUERY_ATTEMPTED` exists to refuse "a query naming no attempted check",
      but the attempted check IS the `SOURCE` list once it is carried -- so that regex becomes
      redundant. Decide whether `QUERY_SETTLES` stays as a shape check on `REASON` or "what
      would settle it" becomes prose the gate does not police.
      ! **DONE 2026-08-16 and 08-17.** `source_problem` exempts `clean` alone, and SOURCE goes
      plural by repeating the line.

- [x] * Rule on `add` -- ! **RULED 2026-08-17: it carries a BLOCK, and the block is the empty
      INTERVAL.** Neither of the two options this task named: the borrowing was not stated as
      intended and no anchor field was added. The census now enumerates every gap between two
      lines of code, so the finding is about a real numbered block that holds nothing, which is
      what an `add` was always claiming. Closed by
      [`an-empty-interval-has-no-census-index`](an-empty-interval-has-no-census-index.md).
      ! The `add` PAYLOAD gained its own rule the same day -- a side, and the anchor named in
      backticks -- under `the-gate-and-the-brief-disagree`.

- [x] **Reversed by a later ruling, 2026-08-16.** Was: *"say once that `clean` produces NO
      record -- it is the `CLEAN` range line."* Roy ruled the opposite the same day: *"every block
      gets a FINDING including CLEAN, that was a stated mechanism and needs to be consistent."*
      Every block is now a record, `clean` included, and the range line, `CLEAN_LINE` and
      `_expand` are deleted from `verdicts.py`. ! That closed the fabrication this file's own
      objective describes: a range covered N blocks in one line and cited nothing.

- [x] **RULED 2026-08-18 by Roy: the payload prose SHIPS, all seven, and it is generated.**
      The budget objection is answered by the branch that raised it. Roy: *"The total number of
      tokens necessary to get the agents to start their work is significantly down ... what we
      cut out of the records, the raw block content, is probably going to more than pay off the
      extra tokens written into the brief."*

      !! **MEASURED, and the two costs scale differently.** The brief is FIXED per reviewer; the
      record is PER BLOCK. Dropping the block text from records saves 332,828 bytes per run at
      four reviewers against a brief of 87,284 -- and the +1,109 the payload prose actually cost
      breaks even at about two prose blocks. On `galley.py`, 11 prose blocks and the smallest
      real target measured, the cut removed 4,045 against 1,109 spent.

      ! **The recommendation this task carried was stale in three ways** and none of them was
      the budget: it named `split`, a verdict collapsed into `move` on 2026-08-16; its examples
      were in the 0.2.x text format this branch replaced; and its 18 KB was 21,467 by the time
      anyone read it again.

      !! **AND THE HAND COPY HAD DRIFTED, which is why the answer is a GENERATOR and not a
      choice.** The brief's verdict table taught the retired marker form -- `false: "..." /
      true: "..."` -- forty lines under a JSON worked example using JSON keys; `query`'s row
      never named `settles`; and ten of the eleven keys a reviewer must type appeared nowhere
      in the brief AS KEYS. Four reviewers read that table, so it was not a documentation
      defect but an instruction to write the wrong thing. `VERDICTS` now owns the keys and the
      prose, `scripts/render_brief.py` writes the table, and `tests/test_brief_table.py`
      refuses a brief that has drifted from the row.

## Worked examples -- kept at Roy's request, all INVENTED

Not shipped unless the task above says so. `correct` is the outlier: it is the only verdict
whose `CHANGE` is a mechanical false/true pair. For every other one `CHANGE` is a different kind
of thing, which is why the gate can check only its SHAPE per verdict.

```
--- RECORD                             --- RECORD
BLOCK     17                           BLOCK     8
VERDICT   correct                      VERDICT   drop
CLAIM     "kept because twenty call    CLAIM     "added 2024-03 after the incident"
          sites want this"             SOURCE    docs/decisions/2024-03-cache.md:1 |
SOURCE    redacted_pkg/billing/rates.py:355 |           # Cache stampede -- mitigation
          def compute_rates(plan,      REASON    the postmortem it points at is tracked
          week, *, clamp=True):                  and current, so this is not the only
REASON    31 callers, all under                  record of the fact
          tests/ -- the count is        CHANGE    delete the sentence
          stale and every caller
          is a test
CHANGE    false: "twenty call sites
          want this" / true: "31
          callers, all in tests/"

--- RECORD                             --- RECORD
BLOCK     23                           BLOCK     31
VERDICT   patch                        VERDICT   move
CLAIM     "basically the same as the   CLAIM     "every entry must be declared before
          other one but not really"              the walk starts"
SOURCE    redacted_pkg/billing/period.py:88 SOURCE    redacted_pkg/catalog/index.py:12 |
          | def next_period(start, *,            class Index:
          inclusive=False):            REASON    it constrains the class, not the
REASON    true -- the two differ only             helper it sits above; someone
          at the boundary -- but it               editing `Index.__init__` never
          names neither function and             sees it there
          states no difference, so     CHANGE    to index.py:12, above `class
          nothing checks it                      Index` -- verbatim, unchanged
CHANGE    "Like `prev_period`, except
          the end date is exclusive."

--- RECORD
BLOCK     5
VERDICT   split
CLAIM     "returns UTC; callers in the scheduler assume local and convert on the way out"
SOURCE    redacted_pkg/billing/clock.py:40 | def now() -> datetime:
REASON    two propositions with different owners, and the second is false of the two
          callers that do not convert
CHANGE    "Returns UTC." above `def now` / "Converts to local on the way out." above
          `Scheduler.emit`
```

`query` and `add` are deliberately absent -- they WERE the two * rulings above, and an example
written before the ruling would have fixed the answer by illustrating it. ! Both are ruled as
of 2026-08-17, so the reason for their absence is gone and writing them is now in scope for the
worked-examples task below.
