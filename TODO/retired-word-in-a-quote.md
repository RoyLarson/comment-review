# A retired word inside a quoted ruling forces a whole-file exemption

```
Status:   open
Progress: 0 of 5 tasks done
Owner:    comment-review
Requires-Roy: true
Raised:   2026-08-23 (2026-08-23, restoring six quotations a mechanical rename had
          rewritten)
```

## Objective

A retired word inside a quoted ruling forces a whole-file exemption.

## Tasks

- [ ] !! TWO RULES COLLIDE AND BOTH ARE ROY'S. CLAUDE.md: *"When a ruling is
      quoted here, quote all of it"* -- and changing a word inside a quotation is
      worse than shortening one, because nothing marks the edit. Roy, 2026-08-19,
      on the vocabulary gate: a file carrying the marker is *"EXEMPT WHOLE"*,
      because exempting a LINE would let a retired word creep back into a file
      about the current representation *"one suppression at a time."*
- [ ] ! SO `folio` CANNOT JOIN `RETIRED` AS THINGS STAND. Six quoted rulings
      across five shipped modules -- `addresser.py`, `lexer.py`, `page.py`,
      `galley.py`, `compositor.py` -- say `folio` or `foliation` because they were
      made before 2026-08-23. Adding the word would exempt those five files WHOLE,
      which is every module the gate most needs to cover.
- [ ] * THE RULING WANTED: whether a QUOTED SPAN is exempt. ! It is not the same
      as a line exemption -- a line marker says *this line is special*, where a
      quotation says *these are someone else's words, and the rule about our prose
      does not reach them*. The repo already marks quotes one way, `*"..."*`, so
      the checker could recognise them. ! Roy's creep argument still applies and
      has to be answered: a quote is easy to fabricate around a word you want to
      keep.
- [ ] ! WHAT WAS DONE INSTEAD, 2026-08-23: `RETIRED` is UNCHANGED, so the gate
      still passes and nothing is weakened. The cost is that `folio` is unpoliced
      -- `docs/vocabulary.md` records it as retired and no command enforces it. !
      That is the state to fix, in whichever direction is ruled.
- [ ] ! MEASURED: the rename rewrote SIX quotations across five files and every
      gate stayed green. Only reading them caught it -- and the sharpest was a
      SUPERSEDED ruling quoted as saying `path@cue`, a word ruled three days after
      the ruling was made.
