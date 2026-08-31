# The ported mark refuses marks the shipped brief tells a role to write

```
Status:   open
Progress: 5 of 5 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-28, reviewing `desk/mark.py` against the role's needs before building
          the collator. Roy asked for the review: "I know we moved the mark already and
          it looks correct but we should review it and make certain it still fully fits
          the role for the initial round."
Superseded: 2026-08-28 — 2026-08-28, Roy, on T4: *"It should not have been added to this
            todo."* This file's Objective is that A MARK WRITTEN FROM THE BRIEF VERBATIM
            IS REFUSED BY THE GATE -- the gate and the instruction disagreeing about
            what a valid mark is. Giving the SHEET a new `code_concerns` container is a
            different subject, and it was already tracked: `code-concerns-cannot-carry-
            a-proposed-change.md` carries it in nine tasks, T1 defining the shape and T3
            publishing it in the brief. So T4 was BOTH misfiled AND a duplicate. ! IT IS
            CHECKED AS SUPERSEDED, NOT DONE -- `CLAUDE.md`'s table: superseded work
            carries `[x]` so the record of it stays legible, and the work itself remains
            OPEN where it belongs, on a file whose Status already reads `blocked` on the
            `*` ruling in `a-role-with-no-code-out-damages-the-prose`. ! IT WAS ALSO
            `T1.6` OF `docs/plans/0.2.4-the-mark-and-the-collator.md` until the same
            day, when Roy ruled it *"indefinitely deferred"* and it left that plan's
            task list -- a plan is one release's scope and closes, so an indefinitely
            deferred box in it would have made 0.2.4 unreleasable by arithmetic nobody
            chose.
```

## Objective

**A mark written from `reviewer-brief.md` VERBATIM is refused by `desk/mark.py` in two places**,
and the code was written the night before. This is the defect class the rewrite exists to end --
the gate and the instruction disagreeing about what a valid mark is, with the gate being the one
that certifies a review.

    an `add`   carrying `claim.anchor`   REFUSED -- the gate reads `claim.missing`
    a `query`  carrying `claim.shape`    REFUSED -- the gate looks for a key named
                                         `outside-my-role`

!! **ONE ROOT CAUSE.** `prototype/original/record.py:306` derives EXTRA claim keys from the row's
traits -- `claim_any` -> `shape`, `needs_attempted` -> `attempted`, `needs_settles` -> `settles`,
`needs_anchor` -> `anchor` -- and the port dropped it. `allowed()` then published `query`'s three
SHAPE VALUES as though they were claim KEYS.

! **THE PROTOTYPE'S OWN DOCSTRING PREDICTED IT**: *"ONE ROW, which is the promise the table makes
and which four sites had taken back ... A new trait had to be added in four places and nothing
failed if one was missed."*

!! **AND THE TESTS PASSED**, because the fixture built its claim from the same table the gate
reads. Six of seven mutations were caught, so the suite looked sound. `decision-log.md
Process: #23` is the rule that came out of it.

### Two more gaps from the same review

**`code_concerns` IS INSTRUCTED AND HAS NO SLOT.** The brief names it twice and
`function-context` twice; every role produced one in every round of the 2026-08-27 experiment;
`flows.marks.seed` emits `{role, marks}` and nowhere to put it.

**THE GENERATOR IS GONE.** `reviewer-brief.md:278` carries
`<!-- BEGIN GENERATED: verdict table -- prototype/render_brief.py -->` and **that script exists
nowhere in the tree.** So the table announces it is generated while being hand-maintained -- which
is what let `add` drift in the first place, and is a claim about the code that is not true.

! **MEASURED: six of the seven rows still agree exactly**, so the table had not broadly drifted.
Only `add` disagreed, and the port is what moved.

## Tasks

- [x] T1 | FINISHED | unknown | T1 -- Restore the extras derivation, so one row
      states every key a `claim` owes. Verify: `allowed()['claim']` matches the
      brief's published table for all seven, checked against the brief and not
      against `INSTRUCTIONS`.
- [x] T2 | FINISHED | unknown | T2 -- Make the gate read those keys. Verify: the
      two brief-compliant marks above are accepted, and a `query` naming a shape
      outside the three is refused.
- [x] T3 | FINISHED | unknown | T3 -- Rebuild `tests/test_mark.py` so no case is
      built from the table it checks. Verify: the suite FAILS before T1 and
      passes after -- one that passes both ways is testing itself.
- [x] T4 | FINISHED | unknown | T4 -- Give the sheet a `code_concerns` list, and
      say so in the brief. Verify: a sheet carrying one validates, and the brief
      names the key.
- [x] T5 | FINISHED | unknown | T5 -- Rebuild the generator and gate it. Verify:
      it writes the block from `INSTRUCTIONS`, and a test fails when the
      committed block and a fresh render disagree.
