# The foliation carries line data for one consumer, and one field of it is read by nobody

```
Status:   in-flight
Progress: 18 of 18 tasks done
Owner:    comment-review
Requires-Roy: true
Raised:   2026-08-21 (Roy, 2026-08-21: 'why does the foliation know about lines? I think
          I asked this question before ... it might need to so it can give that data to
          the record so the agents can rule on it but it makes me think it is suspect
          and becoming a property that it shouldn't be')
Updated:  2026-08-21 — anchor_num started 2026-08-21; the field collapse it enables is a
          separate step
Narrowed: 2026-08-22 — the walkers survive the walk (6912fbe); Foliation is 4 fields --
          walk, reading, lines, _code
```

## Objective

The foliation carries line data for one consumer, and one field of it is read by nobody.

## Tasks

- [x] MEASURED 2026-08-21: Foliation.inserts is WRITTEN twice (foliator.py:577,
      :633) and READ NOWHERE -- delete it, or name its reader
- [x] bounds and lines have ONE shipped reader each, both in page.py empty_places,
      to give an empty place a range the agents can see
- [x] RULING: should page.py compute those bounds itself? It already reads the
      file, so the foliation would then hold no line data except the ruled
      anchor_line
- [x] anchor_line is NOT suspect and stays -- Roy ruled 2026-08-20 that records
      sort by anchor line then series letter, because a foliation number would
      imply it does not change
- [x] _above, _beside and _code are the walk's own line lookups behind
      above()/beside(); decide whether they are internal detail or the same smell
- [x] Re-run scripts/dead_sweep.py --names after any deletion; a module-level dict
      nobody reads is invisible to ruff, which is how inserts survived
- [x] RULING/PROPOSAL, Roy 2026-08-21: replace anchor_line with anchor_num -- an
      ORDINAL over code lines -- carried ALONGSIDE the anchor text. MEASURED:
      anchor_line has exactly two consumers, record.py:854 (sort key) and
      foliator.py:846 (identity lookup), and NEITHER does arithmetic on the line,
      so an ordinal serves both
- [x] The pair is what makes it work: an ordinal alone cannot see a rename in
      place (def f -> def RENAMED shifts no ordinal), and the anchor text alone
      cannot cheaply see an insertion. Roy: 'a single shift on anchor_num and you
      know it is all trash after rereading' -- the file-wide drift ruling in one
      integer
- [x] DONE 2026-08-21: inserts DELETED (dead, 0 readers) and bounds DELETED,
      replaced by Foliation.gap_bounds() computed from the walk's own code lines.
      Round-trip held at 3,068 of 3,073, 0 collisions
- [x] MEASURED 2026-08-21: Foliation.leading is declared in foliator.py and NEVER
      touched by the walk -- page.py:611 (tie_leading) fills it, compositor.py:158
      reads it, and the only mention in foliator.py is the field declaration. It
      is the PAGE's data parked on the foliation because that is what gets passed
      around. Move it or say why it stays
- [x] Roy's cut, 2026-08-21: _declared (a), leading (d), _front/_back (f) and
      _closing (ONE b) are the places that do NOT answer to a line -- by ordinal,
      by neighbour-pair, by the file, and by having no line below it. _above (b)
      and _beside (c) are the two that DO. If anchor_num lands, those two become
      ordinal-keyed and the whole set is uniform
- [x] Roy's three questions, 2026-08-21, all one answer: the b's ARE tabled
      (_above, keyed by the code line BELOW the gap); _front/_back need not be
      fields at all since places holds f0/f1 in order; and _closing is special
      ONLY because there are N+1 b's for N code lines, so a table keyed by the
      line below cannot hold the one with no line below it
- [x] SO anchor_num IS THE ENABLING CHANGE, not a field swap: key by ordinal and
      b_N is just the index past the end, f is series-letter-plus-position, and
      SIX fields become derivable -- _above, _beside, _code, _closing, _front,
      _back. What is left is places + _declared + reading
- [x] Roy, 2026-08-21, the sharpest form: '_above, _beside, _declared, _front,
      _back, _closing are 1 object type flattened into a special case with
      different names.' A PLACE is (folio, series, anchor, anchor_num). Six
      collections of one type, each keyed differently and named separately -- so
      every accessor becomes a QUERY over one collection: above(n) is the b at
      ordinal n, matter() is the first f, the closing gap is the b with the
      highest ordinal
- [x] THE FLATTENING IS ONE COMPREHENSION, foliator.py:686. walkers = {name:
      Foliator(name) for name in SERIES} creates five per-series collections of
      (folio -> anchor) IN EMISSION ORDER; the walk uses them; then out.places
      flattens all five into one dict and the walkers are DISCARDED at return.
      Every projection rebuilt during the walk --
      documents/matter/back_matter/_closing/above/beside -- is an index into a
      walker that was just thrown away. Keep the walkers, delete six fields, add
      no data
- [x] Roy 2026-08-21: 'the foliator needs to key off of the anchor_num and the
      line doesn't matter, because the compositor can only put it near the
      anchor_num and by its own rules will have to put it at the end of the file.'
      Placement consults NO line -- the foot lands last because it holds the
      highest ordinal. The last line-shaped consumer is for_anchor, which matches
      by RANGE to answer which places belong to an anchor: a reviewer lookup, not
      a placement
- [x] Roy 2026-08-21: 'leading is better in the page and it is a paragraph type,
      but it really fits the spanning of paragraphs better than a foliation.' It
      is an EDGE keyed by a folio pair, has no anchor, is not citable and no
      verdict names it -- so being a SERIES in foliator.SERIES may be the wrong
      category. Decide whether d stops being a series and the leading paragraph is
      referenced directly instead of through a folio
- [x] CORRECTION 2026-08-22, to the task above it: the collapse landed and
      predicted the WRONG two fields. It said six become derivable -- _above,
      _beside, _code, _closing, _front, _back -- leaving places + _declared +
      reading. What actually happened: _code STAYED and _declared WENT. _code is
      the ordinal-to-line map, which is the one line fact the walk genuinely owns
      and every accessor taking a LINE uses to find a POSITION; _declared was an
      ordinal-keyed table of a places, which is exactly what the a foliator
      already is. ! The count was right and the membership was not, which is why
      the box names both.
