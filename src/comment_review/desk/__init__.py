"""The copy desk: what a role's marks become.

    marks               the shape a role writes, and the rules a mark can be
                         judged by ON ITS OWN -- no binder, no page -- with
                         the table of rows every reader asks
    answers             what a role hands back in a turn, and its own table
    dispositions        what the chief rules on a place the roles never
                         settled, and its own table
    evaluate            a place, its six states, and the passes that take one
                         from the marks filed on it to the state it comes to
    work                the Unit of Work: a fold over the places, which
                         commits or rolls back whole, and the events it emits
    collator            `decision-log.md Vocabulary: #19`'s first named step:
                         SOURCE-VERIFICATION, per mark, against the page it
                         rules on
    proof               the roles level: every `edit_copy` of one stage
                         held in one `master_proof`
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

!! RECONCILIATION LEFT `collator` ENTIRELY, and the row above says so. It was
built there in 2026-08-29 as a grouping step and a ruling step, and the rebuild
replaced both: a place is built from the marks filed on it
(`flows.places.places_of`) and ruled from its own record (`evaluate`), inside a
fold that commits or rolls back whole (`work`). ! `collator.docket_from` was
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

!! `marks` IS THE FIRST PIECE BACK, ported 2026-08-27 at Roy's direction --
*"You can copy it from there and update the rules/requirements from there but it
doesn't belong in the new records.py. It belongs in the desk/ i think."*

! **`marks` IS THE HALF THAT NEEDS NOTHING LOADED.** Whether `claim.false` is a
key is answerable from the mark alone, and `proof.mark.read_mark` settles it
the moment a mark comes back, reading the entry into its instruction's type or
into named problems, with no third outcome. Whether that
sentence is really IN the paragraph needs the text at the place, which the flow
reads off the page, and the file a `source` cites -- that is
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
