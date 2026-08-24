# The census owns addressing, and four modules share one subject between them

```
Status:   in-progress
Progress: 4 of 5 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-19 (Roy, 2026-08-19: 'this is because the census is doing the
          cues's job')
Narrowed: 2026-08-23 — the census owns no addressing; what remained was that an address
          was COMPOSED in page.py and record.py, not in the addresser
Closed:   2026-08-23 — that residual has LANDED. `addresser.address_for` is the only
          site that joins the two halves, and `page.py:792`, `page.py:804`,
          `record.py:1085` and `held.py:63` all call it. `grep -rn 'f"{flatten' scripts/`
          returns nothing outside `addresser.py:895`.
TRIAGED:  2026-08-23 — four boxes were already ticked and stay ticked. One box remains,
          and it is a real task: nothing has run `module-context` over the four modules.
```

## Objective

!! **THE TITLE IS FALSE AS OF 2026-08-23, AND SO IS THE RESIDUAL THAT REPLACED IT.** The census
owns no addressing at all. Roy, correcting a session that quoted this file's own title back as
though it were a design fact: *"that is false, it clearly owns none of the addressing. It asks the
page to supply the address for itself ... the page knows its path and the cues. Something else
owns addressing -- the Addresser."*

! **MEASURED 2026-08-23.** `census.py` sets no anchor -- the five sites named below are gone,
`paragraphs_lexical` and `paragraphs_stdlib` moved to the lexer, and the one surviving `anchor =`
is a render for printing. It calls no `cues.address(...)`. Every `@` in that file is
`b.address.split("@")[-1]`, printing an address it was handed.

!! **AND THE PUT-TOGETHER CAME HOME.** Roy's ruling on this file, 2026-08-19, was that *"the
foliation is the only and official spot that converts the galley artifact into an address."* The
addresser owns every PART of an address, the whole TAKE-APART -- `flatten`, `emit`, `cue_of`,
`unflatten` -- and now the JOIN as well:

| site | what it does |
| --- | --- |
| `addresser.py:870` | `address_for(path, cue)` -- *"THE ONLY PLACE THEY ARE JOINED"* |
| `page.py:792`, `:804` | call it |
| `record.py:1085`, `held.py:63` | call it |

! Its own docstring records what this file was about: *"IT LEAKED TO TWO MODULES, and
`record.address_for` -- which this is -- carried the claim 'the only place the two halves are put
back together' while `page.py` composed its own with an f-string at two sites. Ruled by Roy,
2026-08-23."*

! **What is left is the module-subject task, and it is unfinished for a plain reason**: the four
modules were separated and each announces one subject, but `module-context` has never been run
over them to verify it, which is what the task asks for.

## Tasks

- [x] T1 -- !! THE ADDRESSER IS THE ONLY OFFICIAL PLACE AN ADDRESS IS MADE. Roy: 'make
      certain that the cues is the only and official spot that converts the
      galley artifact into an address through the addresser assigning the
      cues, and the cues being able to take the cues and convert
      those into which address does this line belong to right now.'
      ! COMPLETE as of 2026-08-23: the JOIN was the last half outside, and
      `addresser.address_for` holds it.
- [x] T2 -- `census.py` set an anchor in FIVE places -- `paragraphs_lexical`:522,
      `paragraphs_stdlib`:747, and :851/:906 which wrote `getattr(node, 'name',
      '<module>')`, the NAME, later overwritten by `anchor_every_address`. The census
      produced a wrong value and a second pass corrected it. All five are gone.
- [x] T3 -- `census.py`'s run loop called `cues.address(vars(b), lines)` per
      paragraph, so the PARAGRAPH produced the address. Inverted: the addresser
      emits the address and the census ties prose to it.
- [x] T4 -- BOTH DIRECTIONS LIVE IN THE ADDRESSER: cues out (walk anchors, emit
      addresses) and lookup back (which address does THIS line belong to right
      now). ! The second is what an agent needs while reading code it must search
      anyway.
- [ ] T5 -- State each module's ONE subject, now that they are separated -- `cues` names
      places, `page` says what a page and a paragraph are, `census` says which prose
      occupies which address, `galley` sets the proposed text -- and verify with
      `module-context` over all four. Verify: a `module-context` report on
      `addresser.py`, `page.py`, `census.py` and `galley.py` that returns no
      more-than-one-subject finding. ! It is the verification that is missing, not the
      docstrings: each of the four announces one subject today and nothing has checked
      that claim from outside.
