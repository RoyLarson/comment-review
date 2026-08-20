# The census owns addressing, and four modules share one subject between them

```
Status:   open
Progress: 0 of 5 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-19 (Roy, 2026-08-19: 'this is because the census is doing the
          addresser's job')
```

## Objective

The census owns addressing, and four modules share one subject between them.

## Tasks

- [ ] !! THE ADDRESSER IS THE ONLY OFFICIAL PLACE AN ADDRESS IS MADE. Roy: 'make
      certain that the addresser is the only and official spot that converts the
      galley artifact into an address through the foliator assigning the
      foliation, and the addresser being able to take the foliation and convert
      those into which address does this line belong to right now.'
- [ ] `census.py` sets an anchor in FIVE places -- `paragraphs_lexical`:522,
      `paragraphs_stdlib`:747, and :851/:906 which still write `getattr(node,
      'name', '<module>')`, the NAME, later overwritten by `anchor_every_address`.
      The census produces a wrong value and a second pass corrects it.
- [ ] `census.py`'s run loop calls `addresser.address(vars(b), lines)` per
      paragraph, so the PARAGRAPH produces the address. Inverted, the foliator
      emits the address and the census ties prose to it.
- [ ] BOTH DIRECTIONS LIVE IN THE ADDRESSER: foliation out (walk anchors, emit
      addresses) and lookup back (which address does THIS line belong to right
      now). ! The second is what an agent needs while reading code it must search
      anyway; `locator.py` answers it today from a separate module.
- [ ] State each module's ONE subject once they are separated -- `addresser` names
      places, `page` says what a page and a paragraph are, `census` says which
      prose occupies which address, `galley` sets the proposed text. Verify with
      `module-context` on all four.
