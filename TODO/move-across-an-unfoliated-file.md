# A move to a file the run never foliated is refused as though it were malformed

```
Status:   open
Progress: 0 of 5 tasks done
Owner:    session
Requires-Roy: true
Raised:   2026-08-20 (Roy, 2026-08-20: 'we have an addresser back, but that is because
          we need a way to state any file in the project -- except we currently do not
          foliate every file')
```

## Objective

A move to a file the run never foliated is refused as though it were malformed.

## Tasks

- [ ] !! THE ADDRESS FORM SURVIVES FOR EXACTLY ONE REASON -- a `move` may name
      ANOTHER FILE. `reviewer-brief.md`: *'down, another file, or out of the code
      entirely -- all move'*. A page envelope makes a record's OWN place a bare
      folio, but a cross-page destination cannot be one.
- [ ] !! AND THE RUN ONLY FOLIATES WHAT IS IN SCOPE. `census.py` is handed the
      files a change touched; everything else has no places at all. So a correct
      address for a real file is unresolvable whenever that file was not in the
      same diff.
- [ ] `desk.py:476` returns `move's destination {addr} is not a place in the
      census` for BOTH causes -- a wrong address, and a right address for a file
      nobody censused. A reviewer reading that about a correct citation goes
      looking for an error that is not there. ! The plausible case is ordinary
      ownership-context work: *this comment belongs in the module docstring of
      `other.py`*.
- [ ] * RULING WANTED: what a `move` to an unfoliated file MEANS. Three shapes --
      (a) refuse, but say WHY, so the reviewer knows the citation was right and
      the scope was short; (b) widen the run's scope to foliate any file a
      destination names, which makes scope depend on findings; (c) treat it as
      `unavailable`, the shape already used for a destination outside the code,
      and let the human place it.
- [ ] ! Do NOT over-build the address form for this yet. Roy, same day: *'galley
      is still up in the air on how it is going to work, so that may lose the
      address again.'* `galley.py --edits` is keyed by address today and is the
      other cross-page consumer; if the galley stops taking addresses, one of the
      two reasons the form exists goes with it.
