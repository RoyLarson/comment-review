"""`galley` is the OLD NAME for `proof`. It runs the proof chain.

!! IT IS A NAME, NOT A COMMAND. Roy, 2026-08-26: *"Create the galley
entry_point function that points to proof_setter and delete the unused
command."* Everything this module held -- its own argument parsing, its own
address-to-path resolution through `rows_of(census)`, its own staleness
comparison, its own overlap guard, its own draft loop -- was a second spelling
of what `flows/proof_setter.py` does, and Roy ruled on the reason: *"there is no
reason to go to the galley for something that proof-setter is supposed to do."*
The removal is recorded in `docs/history.md`.

!! IT SURVIVES BECAUSE `SKILL.md` STILL INVOKES IT at stage 7a, and that file is
`agents` lane. Deleting the name would break the shipped skill from this side.

!! AND THE NAME IS ALL THAT CARRIES OVER -- THE FLAGS DIFFER. This command took
`--census` and `--edits`; `proof` takes `--binder` and `--notations`, so
`galley --census ... --edits ...` reaches `proof`'s parser and is refused as an
unrecognised argument. A skill run is NOT rewired by this file existing; that
is `TODO/the-skill-names-commands-that-moved-to-prototype.md`.

! `__main__.py` DISPATCHES ON THE NAME, so `galley` stays in `COMMANDS` and
`python -m comment_review galley` still resolves.
"""

from comment_review.commands import proof


def main() -> int:
    """Run the proof chain under the older name.

    ! It calls `proof.main()` rather than `proof_setter.run` so there is one
    place that parses these arguments, reads the two files and chooses the exit
    code. A second console face for one flow is what this module used to be.

    Returns:
        `proof.main()`'s exit code, unchanged.
    """
    return proof.main()
