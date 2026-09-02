"""The copy desk: what a role's marks become.

    mark                the shape a role writes, and the rules a mark can be
                         judged by ON ITS OWN -- no binder, no page
    collator            `decision-log.md Vocabulary: #19`'s two named steps.
                         SOURCE-VERIFICATION, per mark, against the page it
                         rules on; and RECONCILIATION -- per address, across
                         the marks of one stage -- ending in a DOCKET
    proof               the roles level: every `edit_copy` of one stage
                         gathered into one `master_proof`
    topology            a run's schedule, read from a TOML file -- which
                         stages run, in what order, and what each dispatches
    external_address    a SKETCH, not in service -- a coordinate into a file
                         this system does not set
    stages              the MARK sequence, as data -- `Kind`, `Role`, and a
                         stage's `dispatches`. `decision-log.md Process: #34`

!! THE MIDDLE IS THE HALF THAT WAS NOT DESIGNED, and this package is where it
goes: marks in from the roles, a DOCKET out. Roy, 2026-08-25, on why the former
contents left: *"There is code there none of it is correct so testing it is
solidifying wrong."*

!! TWO SENTENCES ABOVE ARE SUPERSEDED, 2026-08-29. The first line read
*"RECONCILIATION IS NOT BUILT"* and `collator`'s row read *"RECONCILIATION --
per place, across the marks of one stage -- is not built"*. It is built:
`collator.places` and `collator.reconcile` are what this branch added, and
`tests/test_reconcile.py` runs them. ! A third, `collator.docket_from`, was
added with them and left at `P55` -- the docket is transcribed by
`flows.revise.docket_of`, because building the WRITE END's artifact was never
the middle's to do. ! The `stages` row
credited that module with *"the roles it dispatches"* -- a `roles` FIELD this
branch deleted, so a reader following the row reached for `Stage.roles` and got
`AttributeError`. A stage's roles are `[d.role for d in stage.dispatches]`,
which `stages.py` says at its own `Stage`.

!! THIS DOCSTRING INVENTORIED `prototype/` UNTIL 2026-08-28, AND THE INVENTORY IS
CUT. Roy: *"Why are you talking about code in `prototype/original/`?"* A shipped
module has no business cataloguing what sits in a directory that nothing imports,
nothing ships and that does not run. ! What this package owes is stated by what
it exports and by the plan that builds the rest; a reader who wants the history
has `docs/history.md`, which is the file for it.

!! `mark` IS THE FIRST PIECE BACK, ported 2026-08-27 at Roy's direction --
*"You can copy it from there and update the rules/requirements from there but it
doesn't belong in the new records.py. It belongs in the desk/ i think."*

! **`mark` IS THE HALF THAT NEEDS NOTHING LOADED.** Whether `claim.false` is a
key is answerable from the mark alone, and `mark.parse` settles it the
moment a mark comes back -- turning the entry into a `mark.Mark` or into named
problems, with no third outcome. Whether that sentence is really IN the paragraph
needs the row's own `raw_text` or the page a `source` cites -- that is
`collator.source_verification`, which reads no page and at most one file per
citation, through a per-file cache.

! **AND THE WORD IS `instruction`, NOT THE STRUCK ONE.** A mark is the object;
its `instruction` is one of the seven -- the retired word read as judicial and
named the same thing twice, the object a *finding* and its type the struck
word. `decision-log.md Vocabulary: #17`.

!! AND THE INTERFACE IT PRODUCES IS NO LONGER HERE. `notations.py` moved to
`docket/docket.py` on 2026-08-26 and was renamed with it. Roy: *"this is solid
write-side separate module stuff like binder is a separate module from the
middle and the io stuff. It defines an interface between the middle and the
first write-to-disk."*

! PARKED HERE, THE INTERFACE LOOKED LIKE PART OF THE MIDDLE -- and the middle is
the half that may be rebuilt entirely, while the docket is what the write chain
is already proven against. `decision-log.md Vocabulary: #14`.
"""
