# The finding record is eight fields, six would do, and one of them is checked by nothing

```
Status:   open
Progress: 0 of 8 tasks done
Owner:    session · Roy (⭐ 1 ruling)
Raised:   2026-08-15 (Roy: "It looks like another session got convinced by other
          sessions that they didn't have everything they needed to state what
          they wanted to do")
```

## Objective

**The record shipped with five fields and now has eight, and every field added since exists to
serve the GATE, not the reviewer.** `BLOCK` and `EVIDENCE` came in with `8a2a1bd` (parse the
findings and gate stage 5), `QUOTE` with `9f481c3` (split QUOTE from SUMMARY). Roy's memory of
the original — *"Line | summary | reason | and something else"* — is `LOCATION`, `SUMMARY`,
`FINDING`, `VERDICT`, `CHANGE`, exactly as imported at `7154b92`.

Six fields carry it, and the shape is ruled: **`BLOCK`, `VERDICT`, `CLAIM`, `SOURCE`, `REASON`,
`CHANGE`**, with the record opener `--- RECORD` so the record and its own field stop sharing a
name. Roy ruled `SOURCE` over `PROOF`, which would have collided with the `proof` level and
`prove_unchanged.py`'s AST proof.

⚠ **The cut is not the point; the check is.** `REASON` is the field Roy's `move` ruling rests
on — *"this comment belongs to that line there"* — and **nothing checks it**. `LOCATION` was
checked, but only for resolvability, never against the block it claims to describe. The gate
loads the census and takes only `len(blocks)` from it.

## Tasks

- [ ] Implement the six-field record in `references/reviewer-brief.md` and
      `scripts/verdicts.py`: `LOCATION` goes (derivable from `BLOCK`, which the census resolves
      to path/start/end); `EVIDENCE` + `QUOTE` merge into `SOURCE` as `file:line | verbatim`,
      split on `|` and each half checked exactly as now; `SUMMARY` splits, its left half
      becoming `CLAIM` and its derived right half folding into `REASON`; `FINDING` becomes
      `REASON`; the opener becomes `--- RECORD`. Update `tests/test_verdicts.py`.

- [ ] Keep `SOURCE` merged, not re-split. `EVIDENCE` and `QUOTE` were ONE field until
      `9f481c3` split them, because the old `SUMMARY` mixed verbatim with derived text and a
      checker cannot verify both in one field. `SOURCE`'s two halves are both verbatim, so the
      merge does not recreate that. ⚠ Do not merge anything DERIVED into it.

- [ ] Add the cross-check the record never had: **does `CLAIM` appear in the census text for
      `BLOCK`?** The census carries each block's joined text and the gate already loads it. This
      catches a finding attached to the wrong block, which nothing catches today, and it is
      strictly stronger than the `LOCATION` check being removed.

- [ ] Check `REASON`. Minimum: non-empty, and not merely a restatement of `CLAIM`. Today
      `Finding.finding` is read at exactly one site (`verdicts.py:539`) and only to print the
      reason a record was MALFORMED — so for a real finding the field is decoration.
      ⚠ `Finding.finding` is overloaded: reviewer clause, or diagnostic string when
      `block == -1`. One attribute, two meanings — fix with it.

- [ ] `query` DOES carry `SOURCE`. **Roy, 2026-08-15:** *"EVIDENCE + QUOTE for query means I
      looked here, and here, and here and I couldn't determine what this means."* The exemption
      rests on a conflation — "no line SETTLES it" is not "no line to CITE" — and
      `reviewer-brief.md` contradicts itself on it fifteen lines apart: *"You are still required
      to open the code that would settle it; on every other verdict your QUOTE proves you did"*,
      then *"A query carries no EVIDENCE and no QUOTE, by construction."* The one verdict that
      most needs proof the reviewer looked is the only one exempted from giving it. So:
      `SOURCE` goes PLURAL for a query, one entry per place examined; `evidence_problem()` stops
      exempting it and checks each the same way as every other verdict; what stays unenforceable
      is whether those were the right places, which is judgment and always was.
      ⚠ Residual, small: `QUERY_ATTEMPTED` exists to refuse "a query naming no attempted check",
      but the attempted check IS the `SOURCE` list once it is carried — so that regex becomes
      redundant. Decide whether `QUERY_SETTLES` stays as a shape check on `REASON` or "what
      would settle it" becomes prose the gate does not police.

- [ ] ⭐ Rule on `add`. It is the one verdict whose finding is not ABOUT an existing block — a
      constraint exists in code and nowhere in prose — yet `BLOCK` is required and coverage is
      computed from it, so it must borrow a neighbouring index. Either `add` carries an anchor
      instead of a block, or the borrowing is stated as intended.

- [ ] Say once that `clean` produces NO record. It is the `CLEAN 1-16,18,20-45` range line, and
      the verdict table lists it beside seven that do produce records without saying so.

- [ ] Decide which worked examples ship. ⚠ **This is a budget decision, not a completeness
      one.** `reviewer-brief.md` is 18 KB — the largest single thing a reviewer loads, and four
      parallel reviewers load four copies. Seven examples add ~2-3 KB to every one of them.
      Recommendation: ship **`move` and `split`** only, whose payload shape is least guessable,
      and keep the rest below as the record.

## Worked examples — kept at Roy's request, all INVENTED

Not shipped unless the task above says so. `correct` is the outlier: it is the only verdict
whose `CHANGE` is a mechanical false/true pair. For every other one `CHANGE` is a different kind
of thing, which is why the gate can check only its SHAPE per verdict.

```
--- RECORD                             --- RECORD
BLOCK     17                           BLOCK     8
VERDICT   correct                      VERDICT   drop
CLAIM     "kept because twenty call    CLAIM     "added 2024-03 after the incident"
          sites want this"             SOURCE    docs/decisions/2024-03-cache.md:1 |
SOURCE    redacted_pkg/billing/rates.py:355 |           # Cache stampede — mitigation
          def compute_rates(plan,      REASON    the postmortem it points at is tracked
          week, *, clamp=True):                  and current, so this is not the only
REASON    31 callers, all under                  record of the fact
          tests/ — the count is        CHANGE    delete the sentence
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
REASON    true — the two differ only             helper it sits above; someone
          at the boundary — but it               editing `Index.__init__` never
          names neither function and             sees it there
          states no difference, so     CHANGE    to index.py:12, above `class
          nothing checks it                      Index` — verbatim, unchanged
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

`query` and `add` are deliberately absent — they are the two ⭐ rulings above, and an example
written before the ruling would fix the answer by illustrating it.
