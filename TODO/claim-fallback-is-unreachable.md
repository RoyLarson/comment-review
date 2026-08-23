# A non-object claim is silently emptied, and 60 lines of fallback say the opposite

```
Status:   deferred
Progress: 0 of 7 tasks done
Owner:    comment-review
Requires-Roy: true
Raised:   2026-08-22 (/simplify round 2, 2026-08-22, and Roy: probably (ii) but deferred
          because that whole system from census to findings to verdicts is something
          that needs to be determined now that the backend part of the system works)
```

## Objective

A non-object claim is silently emptied, and 60 lines of fallback say the opposite.

## Tasks

- [ ] MEASURED 2026-08-22, by construction and not by inspection: held.py:185 is
      the ONLY producer of claim_fields and it sets it from the same dict
      held.py:152 emptied. A dict claim gives filled fields plus a rendered marker
      string; a non-dict claim gives EMPTY fields and claim = claim_text(verdict,
      {}), which is the empty string for ALL SEVEN verdicts (ran it). So the pair
      -- empty claim_fields with a non-empty claim -- CANNOT BE PRODUCED
- [ ] AND A COMMENT 380 LINES AWAY SAYS THE OPPOSITE. record.py:538: *the word
      search STAYS for a record whose claim is MISSING or is not an object ... so
      a reviewer words are still read rather than the record failing every check
      at once*. They cannot be: held.py discarded them before any of that code
      runs. About 60 lines across record.py:492-552 and desk.py:100-123/187-203
      have a stated purpose that is false
- [ ] IT STAYS GREEN BECAUSE THE TESTS BUILD AN UNPRODUCIBLE SHAPE. The helper at
      tests/test_verdicts.py:79 defaults claim to the marker string and passes no
      claim_fields, so every test through it exercises a combination no producer
      can emit
- [ ] * THE RULING IS NOT *is the old format retired* -- it already is, record.py
      writes and validates an object and claim_text GENERATES the string. It is:
      when a claim is not an object, do we (i) PRESERVE the reviewer words so the
      fallbacks become live, or (ii) report it MALFORMED, which held.py already
      does two lines earlier for a bad place, and delete the 60 lines
- [ ] ROY LEANS (ii), 2026-08-22. (i) would have verdicts.py accept a record that
      record.py --check refuses -- two readers disagreeing about what is valid,
      which is the defect class this repo hunts
- [ ] THE COST OF (ii) IS SMALLER THAN THE REVIEW ESTIMATED. Of 80 claim= call
      sites in test_verdicts.py only SEVEN use the marker-string form and three
      already pass a dict; the other 70 take the helper default. So it is one
      helper plus seven sites, not ~150 -- the helper can build BOTH claim and
      claim_fields from the marker string and every call site stays as written
      while starting to test a producible shape
- [ ] DEFERRED, and this is what it waits on: the determination of the whole
      census -> findings -> verdicts path, now that the backend round-trips. Roy:
      *that whole system ... needs to be determined now that the backend part of
      the system works*. Deleting 60 lines of a layer whose replacement is about
      to be designed is work done twice
