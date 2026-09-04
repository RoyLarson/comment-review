"""TRANSCRIBE -- one edit_copy, as the docket the write chain reads.

    docket_of(copy) -> Docket

!! ANY COPY, NOT ONLY THE COPY CHIEF'S. Roy, 2026-09-02: *"it could also be
ownership contexts edit-copy or any intermediate edit-copy which allows the stage
outputs to run."* A stage's own output therefore becomes a revise, which is the
mechanism `reads = "revise:N"` and stage `4b` both need. `decision-log.md
Process: #76`.

!! IT IS ITS OWN FLOW BECAUSE IT IS ITS OWN ACT. It lived in `flows/revise.py`
until `P55`+, whose docstring describes exactly one job -- *"Pull a revise: a
second proof of the whole tree"* -- which transcription is not: `pull` never
calls this, and `commands/proof.py` calls both. The cost of leaving it there was
that `revise.py` imported `EditCopy`, `Instruction`, `text_at`, `Alteration` and
`Schedule` for a function `pull` does not touch, so the module's import list
stopped describing what the module's stated job needs. Every other flow file
here -- `distribute.seed`, `fan_out.fan`, `mark_errors.mark_errors`,
`proof_setter.run` -- exposes one act.

!! AND IT IS A FLOW BECAUSE A FLOW MAY REACH BOTH ENDS AND NEITHER END MAY REACH
THE OTHER. Roy, 2026-08-31: *"No direct coupling inside of ends and middle, flows
are neither they run the steps."* This reads the MIDDLE's `EditCopy` and builds
the WRITE END's `Docket`; `Docket.of(edit_copy)` was offered and declined,
because it would put a middle type in `docket/docket.py`, which imports nothing
at all.
"""

from comment_review.desk.containers import EditCopy
from comment_review.desk.mark import Instruction, Mark, text_at
from comment_review.docket.docket import Alteration, Docket, Schedule
from comment_review.reading.addresser import cue_of


def _touched_by(mark: Mark) -> tuple[str, ...]:
    """Every address this one mark writes at, in the order the docket carries.

    !! A `move` IS ONE MARK AND TWO ADDRESSES. `INSTRUCTIONS[MOVE].claim_all` is
    `("from", "to")`, so the single entry a copy carries names both places -- the
    delete at its own `address`, the text at `claim.to`. **The copy does not have
    to carry a move twice**: `flows.collate._chief_copy` writes it once, and once
    is sufficient because the mark holds both ends.

    ! WHICH END GETS WHICH TEXT IS `desk.mark.text_at`'s, not this function's.
    This says WHERE a mark writes; that says WHAT.

    ! WHEN `move-is-a-composite-mark` LANDS this returns one address for every
    instruction: a `drop` at the origin and an `add` at the destination are two
    marks with two addresses, and the branch below has nothing left to decide.
    """
    if mark.instruction is Instruction.MOVE:
        return (mark.address, mark.claim["to"])
    return (mark.address,)


def docket_of(copy: EditCopy) -> Docket:
    """One edit_copy, transcribed into the docket the write chain reads.

    Args:
        copy: a returned edit_copy, already through `EditCopy.deserialize`.

    Returns:
        A `Docket` -- one `Schedule` per sheet that carries at least one mark,
        each naming that sheet's own path and sha and the COPY's role.

    ! A SHEET WITH NO MARKS GETS NO SCHEDULE. A seeded copy holds a slot for
    every place; only the ones a role filled are edits, and an empty schedule
    would tell the write end to set a page from nothing.
    """
    schedules = []
    for sheet in copy.sheets:
        alterations = tuple(
            Alteration(cue=cue_of(address).cue, text=text_at(address, mark))
            for mark in sheet.marks
            for address in _touched_by(mark)
        )
        if alterations:
            schedules.append(
                Schedule(
                    path=sheet.path,
                    sha=sheet.sha,
                    alterations=alterations,
                    role=copy.role,
                )
            )
    return Docket(schedules=tuple(schedules))
