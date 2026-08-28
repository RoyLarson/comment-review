"""The copy desk: what a role's marks become. THE COLLATE HALF IS NOT BUILT.

    mark                the shape a role writes, and the rules a mark can be
                         judged by ON ITS OWN -- no binder, no page
    external_address    a SKETCH, not in service -- a coordinate into a file
                         this system does not set

!! THE MIDDLE IS THE HALF THAT IS NOT DESIGNED, and this package is where it
goes: marks in from the roles, a DOCKET out. Roy, 2026-08-25, on why the former
contents left: *"There is code there none of it is correct so testing it is
solidifying wrong."* `run_context`, `vocabulary`, `desk` and the module the
collator replaces are in `prototype/original/`, reference only; nothing under
`src/` imports them.

! THAT FOURTH ITEM IS NOT NAMED, and the omission is deliberate. It is a list of
FILES, and the file still carries the retired word -- `prototype/` is exempt from
the rename by `decision-log.md Vocabulary: #19`, since renaming inside a captured
record makes it describe something that never happened. Writing the basename here
would put the retired word in a shipped file; writing `collator` would name a
file that does not exist there.

!! `mark` IS THE FIRST PIECE BACK, ported 2026-08-27 at Roy's direction --
*"You can copy it from there and update the rules/requirements from there but it
doesn't belong in the new records.py. It belongs in the desk/ i think."*

! **IT IS THE HALF THAT NEEDS NOTHING LOADED.** Whether `claim.false` is a key
is answerable from the mark alone; whether that sentence is really IN the
paragraph needs the page the role read. The second is SOURCE-VERIFICATION, and
it is what is still missing -- so a mark can be checked the moment it comes
back, and not yet checked against the file it rules on.

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
