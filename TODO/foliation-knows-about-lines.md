# The foliation carries line data for one consumer, and one field of it is read by nobody

```
Status:   decision-needed
Progress: 4 of 11 tasks done
Owner:    comment-review
Requires-Roy: true
Raised:   2026-08-21 (Roy, 2026-08-21: 'why does the foliation know about lines? I think
          I asked this question before ... it might need to so it can give that data to
          the record so the agents can rule on it but it makes me think it is suspect
          and becoming a property that it shouldn't be')
```

## Objective

The foliation carries line data for one consumer, and one field of it is read by nobody.

## Tasks

- [x] MEASURED 2026-08-21: Foliation.inserts is WRITTEN twice (foliator.py:577,
      :633) and READ NOWHERE -- delete it, or name its reader
- [ ] bounds and lines have ONE shipped reader each, both in page.py empty_places,
      to give an empty place a range the agents can see
- [ ] RULING: should page.py compute those bounds itself? It already reads the
      file, so the foliation would then hold no line data except the ruled
      anchor_line
- [ ] anchor_line is NOT suspect and stays -- Roy ruled 2026-08-20 that records
      sort by anchor line then series letter, because a foliation number would
      imply it does not change
- [ ] _above, _beside and _code are the walk's own line lookups behind
      above()/beside(); decide whether they are internal detail or the same smell
- [x] Re-run scripts/dead_sweep.py --names after any deletion; a module-level dict
      nobody reads is invisible to ruff, which is how inserts survived
- [ ] RULING/PROPOSAL, Roy 2026-08-21: replace anchor_line with anchor_num -- an
      ORDINAL over code lines -- carried ALONGSIDE the anchor text. MEASURED:
      anchor_line has exactly two consumers, record.py:854 (sort key) and
      foliator.py:846 (identity lookup), and NEITHER does arithmetic on the line,
      so an ordinal serves both
- [ ] The pair is what makes it work: an ordinal alone cannot see a rename in
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
- [ ] Roy's cut, 2026-08-21: _declared (a), leading (d), _front/_back (f) and
      _closing (ONE b) are the places that do NOT answer to a line -- by ordinal,
      by neighbour-pair, by the file, and by having no line below it. _above (b)
      and _beside (c) are the two that DO. If anchor_num lands, those two become
      ordinal-keyed and the whole set is uniform
