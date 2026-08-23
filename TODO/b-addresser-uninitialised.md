# The b addresser is never initialised at the module trigger, and computes its cue from line numbers

```
Status:   open
Progress: 9 of 17 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-19 (the python_edge_cases.md run, 2026-08-19 -- b1 unresolvable on the
          finished file)
Ruled:    2026-08-19 — the cues -- not the census -- makes the full address. Roy:
          'this is because the census is doing the cues's job.'
Framing:  2026-08-19 — an ADDRESS is not an EDIT RANGE. Two places sharing an insertion
          point is not a collision -- edit ranges expand and contract, the address does
          not. Roy: 'by the way you read it those have overlapping edit ranges - and
          they do but that doesn't mean in the end they collide because there is a
          defined order.'
Renumbered: 2026-08-20 — 2026-08-20 -- every series starts at 0 and a skipped trigger
            takes no number, so the b and c cues all shifted down by one. Eight tasks
            close: four DONE, four SUPERSEDED and checked per CLAUDE.md's marks table.
            Three new tasks at the bottom cover what the shift left behind in the edge-
            case fixture.
Ruled:    2026-08-21 — 2026-08-21 -- the CLOSING TRIGGER is EOF, task 7 closed.
          triggers() returns [MODULE, *code, EOF]; b emits there and a, c and f skip,
          exactly as each decides at the MODULE. Roy rejected the cheaper N+1 rule
          because f will almost certainly want the same trigger for tail matter: 'that
          makes two conditions where you would have to understand to keep the code
          consistent, and why 1 gets a +1 and the other gets some other treatment --
          which is the reason each addresser owns its own rules.' !! AND IT EXPOSED THAT
          triggers() WAS NOT THE WALK: one caller, a test asserting its shape, while
          cue wrote the walk by hand -- so the function claiming 'ONE LIST, SO THE
          THREE SERIES CANNOT DRIFT APART' was not the list any series walked. cue
          reads it now; behaviour verified unchanged place-for-place.
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
at = paragraph.get("original_start")
return sum(1 for n in code if n < at) + 1       # LINE NUMBERS
```

!! **IT NEVER TAKES A STEP AT THE `<module>` TRIGGER.** The `+1` is a hardcoded offset standing
in for "the module already went past". The module's place is produced by a branch that fires
only when front-matter prose ALREADY EXISTS -- the opposite of a addresser. `margins()` emits a
`c` for a bare code line and `_undocumented()` an `a` for a bare declaration; nothing emits `b0`
for the module unless prose is already sitting there to be labelled.

!! **AND THE STEP IS COMPUTED FROM LINE NUMBERS**, in the module whose whole purpose is to stop
line positions naming places. Roy, 2026-08-19: *"this system still uses line numbers implicitly
to determine what an address is. Even though line numbers shift and what goes between line
numbers shift which line number is what category of cues."*

! **`a` is the only series initialised correctly**, which is why `a0`/`a1`/`a2` came out right on
the edge case: `declares` is a real enumeration -- `0` for the module, then `enumerate(declared,
1)`. Module first, then roll forward. `b` was never given that walk. Roy: *"the addresser for the
a's and b's were supposed to get the `__module__` or `<module>` as their first call and then
rolled forward on appropriate lines. The other session hacked its way past that part and didn't
initialize the addresser correctly and got the counts out of order."*

## The shape it should have

The addresser walks ANCHORS and emits an address at every trigger, recording `address -> anchor`
as it goes. The census then ties those addresses to prose, and a record is one per accountable
address:

| layer | owns | knows nothing about |
| --- | --- | --- |
| addresser | walks anchors, emits every address, records `address -> anchor` | prose |
| census / page | which prose occupies which address | how addresses are numbered |
| record | one per accountable address | line positions |

! Today it runs the other way -- `census.py` builds a paragraph, calls `cues.address()` on
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

- [x] DONE. `Addresser.emit` takes the anchor, records `places[cue] = anchor`
      and returns the cue -- one step states both facts, so they cannot
      disagree. ! It emits at every trigger THAT IS ITS OWN: each series owns its
      skip rule, ruled 2026-08-20.
- [x] !! SUPERSEDED 2026-08-20 -- FRONT MATTER GOT ITS OWN SERIES. Roy: 'we
      should have just made the frontmatter its own cues, then the rule that
      b owns all the lines that are not another cues's lines would explicitly
      stay true.' So the file's own matter is `f0`, `b` skips the module entirely,
      and nothing is emitted at that trigger for `b` at all. ! What this task
      WANTED still holds: the place exists whether or not prose sits in it, which
      is what `f0` on a file with no licence header now proves.
- [x] !! SUPERSEDED 2026-08-20 BY THE NAME, NOT THE PROPERTY. The gap above the
      first line of code is `b0`, since every series was ruled to start at 0 and a
      skipped trigger takes no number. ! It can no longer be swallowed by anything
      -- the thing that used to swallow it is in another series.
- [x] DONE 2026-08-20. `gap_step`, `on_step` and `address` are DELETED --
      `grep -c 'def address\|def gap_step\|def on_step' addresser.py` answers 0.
      Every cue comes from `Addresser.emit`.
- [x] DONE. `anchor_every_address` is deleted -- `grep -c` answers 0 in
      `census.py`. `Addresser.emit` records `places[cue] = anchor` in the step
      that issues the cue.
- [x] DONE. `page.attach` says which place a paragraph sits in and `record.seed`
      lays one slot per accountable address, grouped under the page that names
      the file once.
- [x] * RULING WANTED: the CLOSING trigger. ! ARITHMETIC SUPERSEDED 2026-08-20 --
      `b` skips the module, so 7 code lines need EIGHT `b` places, `b0..b6` above
      each line and `b7` for the gap AFTER the last. What is built today is an
      explicit emit after the loop (`out._closing`), which is one of the three
      answers rather than a ruling on them. The question stands: an EOF trigger
      in `triggers()`, or `b` emitting N+1 per walk by definition?
- [ ] Held artifacts renumber: every b cue in evidence/ shifts. Decide whether
      they are migrated or pinned to the old scheme.
- [x] DONE, and FOUR of them since 2026-08-20: `SERIES = (FRONT, DECLARED, GAP,
      ON)` is the only list, and `cue` builds one walker per name.
      ! SUPERSEDED IN ITS COUNT, not its point. Roy, 2026-08-19: 'a b and
      c all get addressers - the other session decided a short-cut was okay even
      though I had just told it that it was not okay.' None is one today: `a`
      reads `paragraph.get('declares')`, `b` is `sum(1 for n in code if n < at) +
      1`, `c` is `code.index(start) + 1`. `triggers()` -- the one list they are
      all supposed to walk -- has NO production caller.
- [x] !! THE TEST THAT CLAIMS TO HOLD THIS ASSERTS THE F-STRING PACKAGING, NOT THE
      MECHANISM. `test_a_cue_is_never_DERIVED_from_another` forbids
      `f"{path}@c{code.index(start)}"` and `sum(1 for n in code if n < at)}"` --
      both ending in the f-string closer. The expressions survive VERBATIM, lifted
      out of the f-string with `+ 1` appended, so all three assertions pass.
      Measured 2026-08-19. ! DONE: `test_a_cue_is_never_DERIVED_from_another`
      now reads `addresser.py`'s CODE lines, skipping prose, so the three retired
      expressions stay quoted in the docstrings where they keep the error legible
      and cannot pass the assertion.
- [ ] * RULED 2026-08-19, RENAMED 2026-08-20 -- THE TOP-OF-FILE ORDER IS f0, a0,
      b0. ! The ORDER is untouched; the file's own matter left the `b` series and
      the gap above the first line of code became `b0`. ! The half that says those
      addresses ALWAYS EXIST is done -- all three are emitted on every file. The
      half that says they are WRITTEN in that order is the galley's, below. Roy:
      'we can accept that the system reads b0 first if available then a0 then b1.
      It gets written in that order. Those addresses always exist and can be queried and
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
- [ ] * RULED 2026-08-19, RENAMED 2026-08-20 -- THE APPLICATION ORDER IS f0, a0,
      THEN a -> b -> c. Roy: 'we need this to be true for everything except a0 and
      b0 where b0 goes first then a0 then the rest.' ! What he called `b0` there is
      `f0` now -- the FILE'S OWN MATTER, a licence agreement, a shebang, a coding
      line -- so it precedes the module docstring;
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
- [ ] !! ROY'S MARKS ON `tests/fixtures/python_edge_cases.md` NAME THE OLD
      NUMBERING. Every `b` and `c` mark is one too high: `b1`/`c1` meant the gap
      above and the room beside `N = 0`, which are `b0`/`c0` since 2026-08-20.
      `a0`, `a1`, `a2` and `f0` are unchanged. ! It is Roy's document -- each mark
      says what he wants said at that place -- so shifting them is his call, not a
      mechanical fix.
- [ ] !! AND THE TESTS PASSED THROUGH THE SHIFT.
      `test_every_b_the_marks_name_exists` and
      `test_every_a_and_c_the_marks_name_exists` ask only that the cue EXISTS,
      and `b1`..`b4` all still do -- they name different places now. ! An
      existence check cannot catch a renumbering, which is the one thing it is
      there to catch: assert the ANCHOR instead, since a mark names a place and a
      place is a line of code.
- [ ] `test_b1_is_the_gap_above_the_first_line_of_code` is now FALSE OF ITS OWN
      NAME -- it asserts `b1` is in the cues, and the gap above the first line
      of code is `b0`. It passes because `b1` exists as the gap above the SECOND
      line.
