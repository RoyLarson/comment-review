# The b foliator is never initialised at the module trigger, and computes its folio from line numbers

```
Status:   open
Progress: 0 of 14 tasks done
Owner:    session * Roy (* 1 ruling -- the closing trigger)
Requires-Roy: true
Raised:   2026-08-19 (the python_edge_cases.md run, 2026-08-19 -- b1 unresolvable on the
          finished file)
Ruled:    2026-08-19 — the addresser -- not the census -- makes the full address. Roy:
          'this is because the census is doing the addresser's job.'
Framing:  2026-08-19 — an ADDRESS is not an EDIT RANGE. Two places sharing an insertion
          point is not a collision -- edit ranges expand and contract, the address does
          not. Roy: 'by the way you read it those have overlapping edit ranges - and
          they do but that doesn't mean in the end they collide because there is a
          defined order.'
```

## Objective

!! **`b0` AND `b1` ARE MUTUALLY EXCLUSIVE, AND WHICH ONE EXISTS DEPENDS ON WHETHER THE FILE HAS
A LICENCE.** Measured 2026-08-19 over five file shapes:

| file | `b0` | `b1` |
| --- | --- | --- |
| no front matter, no module docstring | -- | `b1` |
| module docstring only | -- | `b1` |
| licence + module docstring | `b0` | **--** |
| shebang, no module docstring | `b0` | **--** |
| plain comment above code | -- | `b1` |

So the gap above the first line of code is called `b1` on one file and `b0` on another, and
**adding a module docstring flips it mid-run**.

## What it cost, end to end

Roy's `python_edge_cases.md` -- twelve `add` marks over every series at every nesting level. Run
through `census.py` and `galley.py`, eleven of twelve land correctly and the result parses. The
twelfth is `b0`, which does not exist on the original file. Then, on the FINISHED file:

```
$ addresser.py --census done.json --resolve 'done.py@b1'
done.py@b1 names no entry in this census        (rc=1)
```

! The prose the reviewer placed at `b1` to introduce `N = 0` is now at `b0`, stamped
`front-matter` -- so it is dropped from `--filtered`, no role ever sees it again, and any edit
proposed on it is auto-converted to a `query` by `verdicts.py`. **A round-1 record citing `b1`
resolves to nothing, and the join reports it FATAL** -- the reviewer's correct finding refused as
though fabricated, which is the "blames the neighbour" class `verdicts.py` names as the most
expensive diagnostic there is.

## The cause -- both halves of `gap_step`

```python
if FRONT_MATTER in (paragraph.get("annotations") or ()):
    return 0                                    # a BRANCH, not a step
at = paragraph.get("edit_start")
return sum(1 for n in code if n < at) + 1       # LINE NUMBERS
```

!! **IT NEVER TAKES A STEP AT THE `<module>` TRIGGER.** The `+1` is a hardcoded offset standing
in for "the module already went past". The module's place is produced by a branch that fires
only when front-matter prose ALREADY EXISTS -- the opposite of a foliator. `margins()` emits a
`c` for a bare code line and `_undocumented()` an `a` for a bare declaration; nothing emits `b0`
for the module unless prose is already sitting there to be labelled.

!! **AND THE STEP IS COMPUTED FROM LINE NUMBERS**, in the module whose whole purpose is to stop
line positions naming places. Roy, 2026-08-19: *"this system still uses line numbers implicitly
to determine what an address is. Even though line numbers shift and what goes between line
numbers shift which line number is what category of foliation."*

! **`a` is the only series initialised correctly**, which is why `a0`/`a1`/`a2` came out right on
the edge case: `declares` is a real enumeration -- `0` for the module, then `enumerate(declared,
1)`. Module first, then roll forward. `b` was never given that walk. Roy: *"the foliator for the
a's and b's were supposed to get the `__module__` or `<module>` as their first call and then
rolled forward on appropriate lines. The other session hacked its way past that part and didn't
initialize the foliator correctly and got the counts out of order."*

## The shape it should have

The foliator walks ANCHORS and emits an address at every trigger, recording `address -> anchor`
as it goes. The census then ties those addresses to prose, and a record is one per accountable
address:

| layer | owns | knows nothing about |
| --- | --- | --- |
| foliator | walks anchors, emits every address, records `address -> anchor` | prose |
| census / page | which prose occupies which address | how addresses are numbered |
| record | one per accountable address | line positions |

! Today it runs the other way -- `census.py` builds a paragraph, calls `addresser.address()` on
it, then runs `anchor_every_address()` to decorate it. **The paragraph produces the address**,
and two passes compute what should be one fact, so they can disagree.

! What the inversion makes IMPOSSIBLE rather than checked: every address exists by definition,
because the walk emits at every trigger; the anchor cannot disagree with its address, because
one step states both; and `mark_front_matter` can no longer RECLASSIFY prose, because front
matter occupies `b0` rather than defining it.

## Not in scope

The front-matter misclassification itself -- adding a module docstring below an existing comment
run restamps that run as a licence header -- is the same run's second defect and is filed apart.

## Tasks

- [ ] !! THE FOLIATOR WALKS ANCHORS AND EMITS AT EVERY TRIGGER, recording address
      -> anchor in one table. Roy: 'the foliator gets an anchor and emits an
      address and should add the address and the anchor to an internal list or
      dict.'
- [ ] b0 is emitted at the <module> trigger UNCONDITIONALLY. Front matter OCCUPIES
      it, the way a docstring occupies a0 -- it does not define it by being
      present.
- [ ] b1 is ALWAYS the gap above the first line of code. Roy: 'b1 isn't able to be
      swallowed by b0.'
- [ ] gap_step stops computing from LINE NUMBERS. Roy: 'this system still uses
      line numbers implicitly to determine what an address is.'
- [ ] anchor_every_address() is DELETED -- the walk knows the anchor at the moment
      it emits the address, so the retro-fitting pass and its beside-map go.
- [ ] The census/page ties addresses to prose; a record is one per accountable
      address. Roy: 'then the census and the page tie those to the records.'
- [ ] * RULING WANTED: the CLOSING trigger. 7 code lines need 9 b places -- b0 at
      the module, b1..b7 above each line, and one for the gap AFTER the last. Is
      that the module again, an explicit EOF trigger, or does b simply emit N+1
      per walk?
- [ ] Held artifacts renumber: every b folio in evidence/ shifts. Decide whether
      they are migrated or pinned to the old scheme.
- [ ] !! ALL THREE SERIES GET A FOLIATOR -- a, b AND c. Roy, 2026-08-19: 'a b and
      c all get foliators - the other session decided a short-cut was okay even
      though I had just told it that it was not okay.' None is one today: `a`
      reads `paragraph.get('declares')`, `b` is `sum(1 for n in code if n < at) +
      1`, `c` is `code.index(start) + 1`. `triggers()` -- the one list they are
      all supposed to walk -- has NO production caller.
- [ ] !! THE TEST THAT CLAIMS TO HOLD THIS ASSERTS THE F-STRING PACKAGING, NOT THE
      MECHANISM. `test_a_folio_is_never_DERIVED_from_another` forbids
      `f"{path}@c{code.index(start)}"` and `sum(1 for n in code if n < at)}"` --
      both ending in the f-string closer. The expressions survive VERBATIM, lifted
      out of the f-string with `+ 1` appended, so all three assertions pass.
      Measured 2026-08-19. Rewrite it to hold the property: every folio comes from
      a walk that emitted it.
- [ ] * RULED 2026-08-19 -- THE TOP-OF-FILE ORDER IS b0, a0, b1. Roy: 'we can
      accept that the system reads b0 first if available then a0 then b1. It gets
      written in that order. Those addresses always exist and can be queried and
      stated.' ! An agent that pushes an edit into b0 raises it to the HUMAN for a
      yes/no -- 'not supposed to happen but it is possible and legaleze has its
      holes as well'. This settles the same-insertion-point collision at the head
      of a file, where a0 and b1 currently tie on their edit range and the winner
      is decided by the reviewer's quote style.
- [ ] * RULED 2026-08-19 -- WRITE BY SERIES, NEVER BY LINE NUMBER. Roy: 'apply all
      edits to all docstrings, then apply the b comments on the appropriate side
      of the docstring edits, then apply the c comments' -- b0 excepted. ! Prose
      is of exactly two kinds, docstrings and comments, and the galley can place
      both from the ADDRESS alone. Today galley.splice sorts on (start, end,
      column, replacement) and applies descending by LINE, which is what makes an
      a/b tie fall to the prose text.
- [ ] * RULED 2026-08-19 -- THE APPLICATION ORDER IS b0, a0, THEN a -> b -> c.
      Roy: 'we need this to be true for everything except a0 and b0 where b0 goes
      first then a0 then the rest.' ! b0 is the FRONT MATTER -- a licence
      agreement, a shebang, a coding line -- so it precedes the module docstring;
      everything below is docstrings, then comment runs on the appropriate side of
      them, then trailing comments. !! WELL-FOUNDED, NOT ARBITRARY: only `a` and
      `b` ever want one insertion point, and a `c` carries a COLUMN on a line that
      already exists, so it can contend with nothing. Measured on 'def
      my_func(the_var):' / '    print(the_var)': a0 shares a point with b1, a1
      with b2, and c1/c2 share with nothing.
- [ ] `galley.overlaps()` CANNOT SEE two edits at one insertion point -- for two
      empty ranges the test is `b_start <= a_end`, i.e. `4 <= 3`, False -- so it
      reports no clash and applies both. ! The a -> b -> c ruling should make that
      unreachable rather than caught: only `a` and `b` contend, and the order
      settles them. Verify that when write-by-series lands, and either delete the
      check or state what it still guards.
