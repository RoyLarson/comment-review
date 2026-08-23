# The census owns addressing, and four modules share one subject between them

```
Status:   open
Progress: 4 of 5 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-19 (Roy, 2026-08-19: 'this is because the census is doing the
          cues's job')
Narrowed: 2026-08-23 — the census owns no addressing; what remains is that an address is
          COMPOSED in page.py and record.py, not in the addresser
```

## Objective

!! **THE TITLE IS FALSE AS OF 2026-08-23 AND THE RESIDUAL IS THE OPPOSITE DEFECT.** The census
owns no addressing at all. Roy, correcting a session that quoted this file's own title back as
though it were a design fact: *"that is false, it clearly owns none of the addressing. It asks the
page to supply the address for itself ... the page knows its path and the cues. Something else
owns addressing -- the Addresser."*

! **MEASURED the same day.** `census.py` sets no anchor -- the five sites named below are gone,
`paragraphs_lexical` and `paragraphs_stdlib` moved to the lexer, and the one surviving `anchor =`
is a render for printing. It calls no `cues.address(...)`. It composes nothing: every `@` in
that file is `b.address.split("@")[-1]`, printing an address it was handed.

!! **WHAT IS LEFT IS THE PUT-TOGETHER.** Roy's ruling on this file, 2026-08-19, was that *"the
cues is the only and official spot that converts the galley artifact into an address."* The
addresser owns every PART of an address and the whole TAKE-APART -- `flatten`, `emit`, `cue_of`,
`unflatten`, `Address` -- and does not own the join:

| site | what it does |
| --- | --- |
| `page.py:731` | `flat = flatten(...)`, then `f"{flat}@{place}"` at 796 and 808 |
| `record.py:823` | `f"{flatten(page)}@{place}"` |

! **So an address is MADE in two modules, neither of them the one that owns addressing** -- which
is the same shape this file was opened about, one level further in. ! It is two sites and one
f-string each, so the fix is small; what it is not is done.

! **The module-subject task is separately unfinished**: the four modules were separated and each
announces one subject, but `module-context` has never been run over them to verify it, which is
what that task asks for.

## Tasks

- [x] !! THE ADDRESSER IS THE ONLY OFFICIAL PLACE AN ADDRESS IS MADE. Roy: 'make
      certain that the cues is the only and official spot that converts the
      galley artifact into an address through the addresser assigning the
      cues, and the cues being able to take the cues and convert
      those into which address does this line belong to right now.'
- [x] `census.py` sets an anchor in FIVE places -- `paragraphs_lexical`:522,
      `paragraphs_stdlib`:747, and :851/:906 which still write `getattr(node,
      'name', '<module>')`, the NAME, later overwritten by `anchor_every_address`.
      The census produces a wrong value and a second pass corrects it.
- [x] `census.py`'s run loop calls `cues.address(vars(b), lines)` per
      paragraph, so the PARAGRAPH produces the address. Inverted, the addresser
      emits the address and the census ties prose to it.
- [x] BOTH DIRECTIONS LIVE IN THE ADDRESSER: cues out (walk anchors, emit
      addresses) and lookup back (which address does THIS line belong to right
      now). ! The second is what an agent needs while reading code it must search
      anyway; `locator.py` answers it today from a separate module.
- [ ] State each module's ONE subject once they are separated -- `cues` names
      places, `page` says what a page and a paragraph are, `census` says which
      prose occupies which address, `galley` sets the proposed text. Verify with
      `module-context` on all four.
