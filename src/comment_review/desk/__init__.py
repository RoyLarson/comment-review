"""The copy desk: what a role's marks become. NOT BUILT.

    external_address    a SKETCH, not in service -- a coordinate into a file
                         this system does not set

!! THE MIDDLE IS THE HALF THAT IS NOT DESIGNED, and this package is where it
will go: marks in from the roles, a DOCKET out. Roy, 2026-08-25, on why the
former contents left: *"There is code there none of it is correct so testing it
is solidifying wrong."* `run_context`, `vocabulary`, `desk` and `verdicts` are
in `prototype/original/`, reference only; nothing under `src/` imports them.

!! AND THE INTERFACE IT PRODUCES IS NO LONGER HERE. `notations.py` moved to
`docket/docket.py` on 2026-08-26 and was renamed with it. Roy: *"this is solid
write-side separate module stuff like binder is a separate module from the
middle and the io stuff. It defines an interface between the middle and the
first write-to-disk."*

! PARKED HERE, THE INTERFACE LOOKED LIKE PART OF THE MIDDLE -- and the middle is
the half that may be rebuilt entirely, while the docket is what the write chain
is already proven against. `decision-log.md Vocabulary: #14`.
"""
