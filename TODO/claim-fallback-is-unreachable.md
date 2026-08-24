# A non-object claim is silently emptied, and 60 lines of fallback say the opposite

```
Status:   deferred
Progress: 6 of 8 tasks done
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

!! **WHY IT IS DEFERRED, and what it waits on**: the determination of the whole census ->
findings -> verdicts path, now that the backend round-trips. Roy: *"that whole system ...
needs to be determined now that the backend part of the system works"*. Deleting 60 lines
of a layer whose replacement is about to be designed is work done twice.

## Tasks

- [x] T1 -- RECORD, not a task. MEASURED 2026-08-22, by construction and not by
      inspection: held.py:187 is the ONLY producer of claim_fields and it sets it
      from the same dict held.py:152 emptied. The pair -- empty claim_fields with a
      non-empty claim -- CANNOT BE PRODUCED. Re-verified in place 2026-08-23.
- [x] T2 -- RECORD, not a task. AND A COMMENT 380 LINES AWAY SAYS THE OPPOSITE,
      at record.py:541-544. About 60 lines across record.py:525-544 and
      desk.py:171-172, :218 and :511 have a stated purpose that is false.
- [x] T3 -- RECORD, not a task. IT STAYS GREEN BECAUSE THE TESTS BUILD AN
      UNPRODUCIBLE SHAPE -- tests/test_verdicts.py:79.
- [ ] T4 -- * THE RULING. It is NOT *"is the old format retired"* -- it already is,
      record.py writes and validates an object and claim_text GENERATES the string.
      It is: when a claim is not an object, do we (i) PRESERVE the reviewer words so
      the fallbacks become live, or (ii) report it MALFORMED, which held.py already
      does two lines earlier (held.py:142-145) for a bad place, and delete the 60
      lines.
- [x] T5 -- RECORD, not a task. ROY LEANS (ii), 2026-08-22.
- [x] T6 -- RECORD, not a task. THE COST OF (ii) IS SMALLER THAN THE REVIEW
      ESTIMATED -- one helper plus seven sites, not ~150.
- [x] T7 -- RECORD, not a task. DEFERRED, and this is what it waits on: the
      determination of the whole census -> findings -> verdicts path.
- [ ] T8 -- WHEN T4 IS RULED, MAKE THE CODE AND THE PROSE AGREE. Under (ii):
      held.py reports a non-dict claim MALFORMED, and record.py:525-544 plus
      desk.py:171-172, :218 and :511 lose the fallback and the sentences that
      describe it. Under (i): held.py:152 stops emptying the claim, and a test
      builds the preserved-words shape so the fallback has a caller. Verify: no
      shipped comment describes a branch nothing can reach, and the test suite is
      green. ! DEFERRED with T4 -- it waits on the same determination.
