# A non-object claim is silently emptied, and 60 lines of fallback say the opposite

```
Status:   deferred
Progress: 6 of 8 tasks closed
Owner:    backend
Requires-Roy: true
Raised:   2026-08-22 (/simplify round 2, 2026-08-22, and Roy: probably (ii) but deferred
          because that whole system from census to findings to verdicts is something
          that needs to be determined now that the backend part of the system works)
TRIAGED:  2026-08-23 — 2026-08-23. Six of the seven boxes are RECORDS -- a measurement,
          a contradicting comment, why the suite stays green, which way Roy leans, what
          (ii) costs, and what the deferral waits on. None can be ticked by an
          observation, so all six are ticked as records and left in place. ONE LIVE
          ITEM: the * ruling.
RE-VERIFIED: 2026-08-23 — 2026-08-23, read against the tree. STILL LIVE and citations
             corrected: held.py:152 empties a non-dict claim (`if not isinstance(claim,
             dict): claim = {}`), held.py:161 then renders `claim_text(verdict, claim)`
             and held.py:187 sets `claim_fields=claim` from the SAME emptied dict, so
             the producer-by-construction argument holds. The contradicting comment is
             record.py:541-544, not :538. The fallback readers are record.py:525-544
             (`_answered`) and desk.py:171-172, :218 and :511, each branching on
             `if f.claim_fields ... else f.claim`.
Split:    2026-08-23 -- the six record boxes are cut to one line each and their content
             reads from the Objective, which already carried all of it verbatim
```

## Objective

A non-object claim is silently emptied, and 60 lines of fallback say the opposite.

**MEASURED 2026-08-22, by construction and not by inspection**: held.py:187 is the ONLY
producer of `claim_fields` and it sets it from the same dict held.py:152 emptied. A dict
claim gives filled fields plus a rendered marker string; a non-dict claim gives EMPTY
fields and `claim = claim_text(verdict, {})`, which is the empty string for ALL SEVEN
verdicts (ran it). So the pair -- empty `claim_fields` with a non-empty `claim` -- CANNOT
BE PRODUCED.

**AND A COMMENT 380 LINES AWAY SAYS THE OPPOSITE.** record.py:541-544: *"The word search
STAYS for a record whose `claim` is MISSING or is not an object: `claim_fields` is empty
there and this falls through to `pattern`, so a reviewer's words are still read rather than
the record failing every check at once."* They cannot be: held.py:152 discarded them
before any of that code runs. About 60 lines across record.py:525-544 and desk.py:171-172,
:218 and :511 have a stated purpose that is false.

**IT STAYS GREEN BECAUSE THE TESTS BUILD AN UNPRODUCIBLE SHAPE.** The helper at
tests/test_verdicts.py:79 defaults `claim` to the marker string and passes no
`claim_fields`, so every test through it exercises a combination no producer can emit.

**ROY LEANS (ii), 2026-08-22.** (i) would have verdicts.py accept a record that
`record.py --check` refuses -- two readers disagreeing about what is valid, which is the
defect class this repo hunts.

**THE COST OF (ii) IS SMALLER THAN THE REVIEW ESTIMATED.** Of 80 `claim=` call sites in
test_verdicts.py only SEVEN use the marker-string form and three already pass a dict; the
other 70 take the helper default. So it is one helper plus seven sites, not ~150 -- the
helper can build BOTH `claim` and `claim_fields` from the marker string and every call
site stays as written while starting to test a producible shape.

!! **THE QUESTION IS NOT *"is the old format retired"*.** It already is: record.py writes and
validates an object, and `claim_text` GENERATES the string. The question is what happens when a
claim is not an object.

!! **AND THE TWO SHAPES THE RULING PICKS BETWEEN.** Under **(ii)**: held.py reports a non-dict
claim MALFORMED -- which held.py:142-145 already does two lines earlier for a bad place -- and
record.py:525-544 plus desk.py:171-172, :218 and :511 lose the fallback and the sentences that
describe it. Under **(i)**: held.py:152 stops emptying the claim, and a test builds the
preserved-words shape so the fallback has a caller.

!! **WHY IT IS DEFERRED, and what it waits on**: the determination of the whole census ->
findings -> verdicts path, now that the backend round-trips. Roy: *"that whole system ...
needs to be determined now that the backend part of the system works"*. Deleting 60 lines
of a layer whose replacement is about to be designed is work done twice. ! T8 is deferred with
T4 -- it waits on the same determination.

## Tasks

- [x] T1 | FINISHED | unknown | T1 -- RECORD, not a task. The by-construction
      measurement, restated in the Objective: the pair `claim_fields` empty with
      `claim` non-empty CANNOT BE PRODUCED.
- [x] T2 | FINISHED | unknown | T2 -- RECORD, not a task. The contradicting
      comment at record.py:541-544 and the ~60 lines whose stated purpose is
      false, restated in the Objective.
- [x] T3 | FINISHED | unknown | T3 -- RECORD, not a task. The suite stays green
      because tests/test_verdicts.py:79 builds an unproducible shape. Restated
      in the Objective.
- [?] T4 | T4 -- * Rule whether a non-object `claim` (i) preserves the reviewer
      words or (ii) is reported MALFORMED. Verify: `docs/decision-log.md`
      records the ruling.
- [x] T5 | FINISHED | unknown | T5 -- RECORD, not a task. ROY LEANS (ii),
      2026-08-22. Restated in the Objective.
- [x] T6 | FINISHED | unknown | T6 -- RECORD, not a task. The cost of (ii) is
      one helper plus seven sites, not ~150. Restated in the Objective.
- [x] T7 | FINISHED | unknown | T7 -- RECORD, not a task. What the deferral
      waits on -- the determination of the whole census -> findings -> verdicts
      path. Restated in the Objective.
- [ ] T8 | T8 -- Make code and prose agree in the shape T4 rules. Verify: no
      shipped comment describes an unreachable branch, and `uv run pytest -q` is
      green.
