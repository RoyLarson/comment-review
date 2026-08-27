"""The copy desk: what a role's marks become on the way to the galley.

    notations          the shape a role's marks take before the galley reads
                        them -- set this place to this text, or delete it
    external_address    a SKETCH, not in service -- a coordinate into a file
                         this system does not set

!! `run_context`, `vocabulary`, `desk` and `verdicts` -- the four modules this
package held before -- moved to `prototype/original/` and are reference only;
nothing under `src/` imports them.

!! WHAT CARRIES A ROLE'S ANSWER TO THE PAGE WAS NOT HERE AND WAS NOT NAMED.
Roy, 2026-08-24: *"we have a missing piece in the chain."* `notations.py` is
that piece -- the galley needs only *this address gets this paragraph*, and
`notations.read` / `notations.by_page` produce exactly that shape from a
role's marks.

! THE NAME IS PROVISIONAL. `notations` sits one letter from the `annotations`
that `binder/annotate.py` already owns for candidate flags on a paragraph --
see `notations.py`'s own header and
`TODO/notations-collides-with-annotations.md`.
"""
