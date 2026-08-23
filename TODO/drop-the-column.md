# original_column is redundant and can be dropped entirely

```
Status:   blocked
Progress: 0 of 6 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-20 (Roy, 2026-08-20: 'the edit_column is an idea that can be dropped
          entirely. It was there because we did not have a way to identify the above
          line-of-code comments from the beside line-of-code comment. That is now
          resolved fully by the address system')
Updated:  2026-08-20 — waiting on the galley rewrite: dropping the field changes
          splice's tuple
```

## Objective

original_column is redundant and can be dropped entirely.

## Tasks

- [ ] !! MEASURED, 9,281 of 9,281: `original_column == len(anchor) + 1` for every
      paragraph carrying one, and `line[: column - 1] == anchor` exactly. Re-
      measured across python, toml-ini, go, ruby and rust (3,693 paragraphs, 0
      disagreeing) and on the c-family path the field was BUILT for -- a block
      comment opened after a statement. The field carries nothing the anchor does
      not.
- [ ] !! AND KIND NOW ANSWERS WHAT IT WAS FOR. A `c` is exactly {trailing-comment,
      margin} and an `a` is {docstring, undocumented}; everything else is a `b`.
      Verified with zero exceptions after the 2026-08-20 kind fix. So 16 of the 18
      shipped sites, which use the column only as a BOOLEAN, become a membership
      test.
- [ ] `addresser._series_of` argues *'NOT from the kind, which would need a case
      per kind and a new one for every kind added'*. That was written when kind
      and series disagreed. It is now ONE membership test, and the docstring's
      reasoning is stale.
- [ ] The two numeric uses both reduce to the anchor: `galley.paragraph_matches`
      splits the stored halves at `column - 1`, and `splice` keeps `line[: column
      - 1]` as the head. Both become the anchor itself, which is what makes the
      galley simpler -- Roy, 2026-08-20: *'I think the galley work becomes simpler
      because of this.'*
- [ ] `galley.unanswerable` requires `original_column` present and refuses a
      census without it. That requirement goes with the field.
- [ ] DEFERRED: the change touches `splice`'s tuple, and Roy ruled the galley work
      waits -- *'the decision on ordering is all galley work coming up on how it
      resets the paragraphs ... it can wait'*. Land it with that work, not before.
