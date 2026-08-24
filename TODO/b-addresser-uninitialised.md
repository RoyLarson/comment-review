# The b addresser is never initialised at the module trigger, and computes its cue from line numbers

```
Status:   in-progress
Progress: 13 of 17 tasks done
Owner:    backend
Requires-Roy: true
Raised:   2026-08-19 (the python_edge_cases.md run, 2026-08-19 -- b1 unresolvable on the
          finished file)
Ruled:    2026-08-19 — the cues -- not the census -- makes the full address. Roy:
          'this is because the census is doing the cues's job.'
Framing:  2026-08-19 — an ADDRESS is not an EDIT RANGE. Two places sharing an insertion
          point is not a collision -- edit ranges expand and contract, the address does
          not. Roy: 'by the way you read it those have overlapping edit ranges - and
          they do but that doesn't mean in the end they collide because there is a
          defined order.'
Renumbered: 2026-08-20 — every series starts at 0 and a skipped trigger takes no number,
            so the b and c cues all shifted down by one.
Ruled:    2026-08-21 — the CLOSING TRIGGER is EOF. triggers() returns [MODULE, *code,
          EOF]; b emits there and a, c and f skip, exactly as each decides at the
          MODULE. Roy rejected the cheaper N+1 rule because f will almost certainly want
          the same trigger for tail matter.
TRIAGED:  2026-08-23 — four of the eight open boxes are RULINGS ALREADY MADE, and three
          of those four have since been IMPLEMENTED, so they are ticked with the
          evidence. Four boxes remain, all verified live today. ! `Requires-Roy` is set
          TRUE, from `false`: T15 is a change to Roy's own marks document and the box
          says so -- *"shifting them is his call, not a mechanical fix."*
```

## Objective

!! **`b0` AND `b1` WERE MUTUALLY EXCLUSIVE, AND WHICH ONE EXISTED DEPENDED ON WHETHER THE FILE
HAD A LICENCE.** Measured 2026-08-19 over five file shapes:

| file | `b0` | `b1` |
| --- | --- | --- |
| no front matter, no module docstring | -- | `b1` |
| module docstring only | -- | `b1` |
| licence + module docstring | `b0` | **--** |
| shebang, no module docstring | `b0` | **--** |
| plain comment above code | -- | `b1` |

So the gap above the first line of code was called `b1` on one file and `b0` on another, and
**adding a module docstring flipped it mid-run**. ! That is fixed -- see T1 to T7 -- and what is
left is the wake: Roy's marks, and two tests that survived the renumbering.

## What it cost, end to end

Roy's `python_edge_cases.md` -- twelve `add` marks over every series at every nesting level. Run
through the census and the galley, eleven of twelve landed correctly and the result parsed. The
twelfth was `b0`, which did not exist on the original file. Then, on the FINISHED file:

```
$ addresser.py --census done.json --resolve 'done.py@b1'
done.py@b1 names no entry in this census        (rc=1)
```

! The prose the reviewer placed at `b1` to introduce `N = 0` was then at `b0`, stamped
`front-matter` -- so it was dropped from `--filtered`, no role saw it again, and any edit
proposed on it was auto-converted to a `query`. **A round-1 record citing `b1` resolved to
nothing, and the join reported it FATAL** -- the reviewer's correct finding refused as though
fabricated, which is the "blames the neighbour" class `verdicts.py` names as the most expensive
diagnostic there is.

## The cause -- both halves of `gap_step`

! **THE CODE BELOW IS DELETED** (T4: `grep -c 'def address\|def gap_step\|def on_step'
addresser.py` answers 0). It is quoted so the error stays legible.

```python
if FRONT_MATTER in (paragraph.get("annotations") or ()):
    return 0                                    # a BRANCH, not a step
at = paragraph.get("original_start")
return sum(1 for n in code if n < at) + 1       # LINE NUMBERS
```

!! **IT NEVER TOOK A STEP AT THE `<module>` TRIGGER.** The `+1` was a hardcoded offset standing
in for "the module already went past". The module's place was produced by a branch that fired
only when front-matter prose ALREADY EXISTED -- the opposite of an addresser.

!! **AND THE STEP WAS COMPUTED FROM LINE NUMBERS**, in the module whose whole purpose is to stop
line positions naming places. Roy, 2026-08-19: *"this system still uses line numbers implicitly
to determine what an address is. Even though line numbers shift and what goes between line
numbers shift which line number is what category of cues."*

! **`a` was the only series initialised correctly**, which is why `a0`/`a1`/`a2` came out right
on the edge case: `declares` is a real enumeration -- `0` for the module, then `enumerate(
declared, 1)`. Module first, then roll forward. Roy: *"the addresser for the a's and b's were
supposed to get the `__module__` or `<module>` as their first call and then rolled forward on
appropriate lines."*

## The shape it should have, and now does

| layer | owns | knows nothing about |
| --- | --- | --- |
| addresser | walks anchors, emits every address, records `address -> anchor` | prose |
| census / page | which prose occupies which address | how addresses are numbered |
| record | one per accountable address | line positions |

! What the inversion made IMPOSSIBLE rather than checked: every address exists by definition,
because the walk emits at every trigger; the anchor cannot disagree with its address, because
one step states both; and nothing can RECLASSIFY prose, because front matter occupies `f0`
rather than defining it.

## The rulings on ORDER, all made and all implemented

- **THE TOP-OF-FILE ORDER IS f0, a0, b0.** Roy, 2026-08-19: *"we can accept that the system
  reads b0 first if available then a0 then b1. It gets written in that order. Those addresses
  always exist and can be queried and stated."* ! What he called `b0` there is `f0` now -- the
  FILE'S OWN MATTER, a licence agreement, a shebang, a coding line. ! An agent that pushes an
  edit into `b0` raises it to the HUMAN for a yes/no -- *"not supposed to happen but it is
  possible and legaleze has its holes as well"*.
- **WRITE BY SERIES, NEVER BY LINE NUMBER.** Roy, 2026-08-19: *"apply all edits to all
  docstrings, then apply the b comments on the appropriate side of the docstring edits, then
  apply the c comments"*. ! IMPLEMENTED: `galley.py`'s own docstring reads *"NO LINE NUMBER
  APPEARS IN THIS FILE"*, `reset` is an assignment to a paragraph, and `compositor.set_page`
  walks the reading order and asks each place what it holds.
- **THE APPLICATION ORDER IS f0, a0, THEN a -> b -> c.** `compositor.set_page`'s docstring
  quotes the ruling it implements -- Roy, 2026-08-21: *"f0 always first, then a0, then b0, then
  c0. I know f0 is going to grab b0 lines. It is a sacrifice I am willing to make."* !!
  WELL-FOUNDED, NOT ARBITRARY: only `a` and `b` ever want one insertion point, and a `c` carries
  a COLUMN on a line that already exists, so it can contend with nothing.

## Not in scope

The front-matter misclassification itself -- adding a module docstring below an existing comment
run restamps that run as a licence header -- is the same run's second defect and is filed apart.

## Tasks

- [x] T1 -- DONE. `Addresser.emit` takes the anchor, records `places[cue] = anchor`
      and returns the cue -- one step states both facts, so they cannot
      disagree. ! It emits at every trigger THAT IS ITS OWN: each series owns its
      skip rule, ruled 2026-08-20.
- [x] T2 -- !! SUPERSEDED 2026-08-20 -- FRONT MATTER GOT ITS OWN SERIES. Roy: 'we
      should have just made the frontmatter its own cues, then the rule that
      b owns all the lines that are not another cues's lines would explicitly
      stay true.' So the file's own matter is `f0`, `b` skips the module entirely,
      and nothing is emitted at that trigger for `b` at all. ! What this task
      WANTED still holds: the place exists whether or not prose sits in it, which
      is what `f0` on a file with no licence header now proves.
- [x] T3 -- !! SUPERSEDED 2026-08-20 BY THE NAME, NOT THE PROPERTY. The gap above the
      first line of code is `b0`, since every series was ruled to start at 0 and a
      skipped trigger takes no number.
- [x] T4 -- DONE 2026-08-20. `gap_step`, `on_step` and `address` are DELETED --
      `grep -c 'def address\|def gap_step\|def on_step' addresser.py` answers 0.
      Every cue comes from `Addresser.emit`.
- [x] T5 -- DONE. `anchor_every_address` is deleted -- `grep -c` answers 0 in
      `census.py`. `Addresser.emit` records `places[cue] = anchor` in the step
      that issues the cue.
- [x] T6 -- DONE. `page.attach` says which place a paragraph sits in and `record.seed`
      lays one slot per accountable address, grouped under the page that names
      the file once.
- [x] T7 -- RULED 2026-08-21: the CLOSING trigger is EOF, and `triggers()` is the walk
      every series reads. ! MEASURED 2026-08-23 on the edge-case original: 7 code lines,
      `b0..b7`, the last anchored `<eof>`.
- [ ] T8 -- Every `b` cue in `evidence/` names the pre-2026-08-20 numbering. State which
      scheme the held runs use, in `evidence/README.md`, and whether they are migrated or
      pinned. Verify: `evidence/README.md` says which. ! Related but not the same work:
      [`held-runs-need-a-one-off-migration`](held-runs-need-a-one-off-migration.md) is
      about the retired REPORT FORMAT and is deferred; this is one sentence about
      numbering, and a reader of `evidence/` has nothing today.
- [x] T9 -- DONE. One list, one walker per name. ! `SERIES` reads
      `(COVERS, DECLARED, GAP, ON)` today -- `FRONT` was renamed `COVERS` -- and
      `addresser.py:230` is the only place the four letters are spelled.
      ! SUPERSEDED IN ITS COUNT, not its point. Roy, 2026-08-19: 'a b and
      c all get addressers - the other session decided a short-cut was okay even
      though I had just told it that it was not okay.'
- [x] T10 -- !! THE TEST THAT CLAIMED TO HOLD THIS ASSERTED THE F-STRING PACKAGING, NOT
      THE MECHANISM. `test_a_cue_is_never_DERIVED_from_another` forbade
      `f"{path}@c{code.index(start)}"` and `sum(1 for n in code if n < at)}"` --
      both ending in the f-string closer. The expressions survived VERBATIM, lifted
      out of the f-string with `+ 1` appended, so all three assertions passed.
      Measured 2026-08-19. ! DONE: it now reads `addresser.py`'s CODE lines, skipping
      prose, so the three retired expressions stay quoted in the docstrings where they
      keep the error legible and cannot pass the assertion.
- [x] T11 -- RULING, MADE 2026-08-19 and renamed 2026-08-20: the top-of-file order is
      f0, a0, b0, and all three are emitted on every file. Kept in the Objective, under
      *The rulings on ORDER*. Not a checkpoint -- there is no state in which someone
      ticks a ruling.
- [x] T12 -- RULING, MADE 2026-08-19 -- write by series, never by line number -- and
      IMPLEMENTED. `galley.py` contains no line arithmetic and no `splice`; `reset` is
      an assignment to a paragraph and `compositor.set_page` walks the reading order.
      Quoted in the Objective.
- [x] T13 -- RULING, MADE 2026-08-19 -- the application order is f0, a0, then a -> b ->
      c -- and IMPLEMENTED: `compositor.set_page`'s docstring quotes it and the walk
      follows `addresser.SERIES`. Quoted in the Objective.
- [x] T14 -- DONE, by deletion. `galley.overlaps()` could not see two edits at one
      insertion point -- for two empty ranges the test was `b_start <= a_end`, `4 <= 3`,
      False. The box asked for the check to be deleted or for what it still guards to be
      stated once write-by-series landed. It landed, and the check is gone: `grep -n
      overlaps galley.py` finds only the `--out`/`--repo` path check.
- [ ] T15 -- * ROY'S MARKS ON `tests/fixtures/python_edge_cases.md` NAME THE OLD
      NUMBERING, and shifting them is his call. VERIFIED 2026-08-23 by censusing the
      fixture's own `## Original` block: `b0` anchors `N = 0` and `c0` is the room beside
      it, so the marks reading `b1` ... `b4` and `c1` ... `c4` are each one too high --
      `b1` now anchors `def wrapper(fn):`. `a0`, `a1`, `a2` and `f0` are unchanged. ! It
      is Roy's document -- each mark says what he wants said at that place -- so it is a
      ruling, not a mechanical fix.
- [ ] T16 -- `test_every_b_the_marks_name_exists` and
      `test_every_a_and_c_the_marks_name_exists` (`tests/test_edge_cases.py:81`, `:106`)
      ask only that the cue EXISTS, and `b1`..`b4` all still do -- they name different
      places now. ! An existence check cannot catch a renumbering, which is the one thing
      it is there to catch: assert the ANCHOR instead, since a mark names a place and a
      place is a line of code. Verify: shift every mark by one and the class must go red;
      today it stays green.
- [ ] T17 -- `test_b1_is_the_gap_above_the_first_line_of_code`
      (`tests/test_edge_cases.py:86`) is FALSE OF ITS OWN NAME -- it asserts `b1` is in
      the cues, and the gap above the first line of code is `b0`. MEASURED 2026-08-23: on
      that fixture `b1`'s anchor is `def wrapper(fn):`, the SECOND line of code. Verify:
      the test asserts the anchor of the cue it names.
