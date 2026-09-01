"""The roles level: every `edit_copy` of one stage, gathered into one `master_proof`.

    gather(stage, edit_copies)   the `MasterProof` holding them

!! THE LEVEL `binder` AND `docket` LACK, RULED 2026-08-29 (`decision-log.md
Vocabulary: #28`):

    master_proof
      +-- edit_copy        one per role; one per SHARD under fan-out
            +-- sheet      one per page
                  +-- mark one per place

Roy: *"The got the binder - they copied the pages from the binder and built
their own binder to make up ... this is their edit_copy ... the master proof
holds the edit_copies."* `binder` and `docket` have no roles level -- one goes
out, one comes back, and in between there are N marked copies with no
container. This module is that container.

! `master_proof` HOLDS `edit_copies`, NOT SHEETS DIRECTLY -- a sheet belongs
to the `edit_copy` that seeded it, one level down.
"""

from comment_review.desk.containers import EditCopy, MasterProof


class MismatchedRoot(Exception):
    """Two `edit_copies` handed to `gather` were censused from different roots.

    !! THE ONLY RULE WITH A NAMED EXCEPTION HERE, and it has to be one that can
    fail: two edit_copies censused from different revises cannot be
    reconciled, because their addresses answer to different trees -- an `a0`
    from one tells nothing about the `a0` in the other.

    ! AN ABSENT `read_from` IS NO LONGER THIS MODULE'S CASE AT ALL, since
    2026-08-31. `gather` subscripted the key so an absence raised `KeyError`
    rather than comparing every copy that carried none EQUAL on `{}`; taking an
    `EditCopy` retires the question, because `EditCopy.deserialize` refuses a
    copy whose `read_from` fails `_read_from_problem` before one can be built.
    """


def gather(stage: str, edit_copies: list[EditCopy]) -> MasterProof:
    """Every `edit_copy` of one stage, as the master_proof that holds them.

    Args:
        stage: the stage label these edit_copies were dispatched under, e.g.
            `SKILL.md`'s `"4a"` or `"4c"`.
        edit_copies: one per role, or one per shard under fan-out. Held in the
            order given: nothing is sorted and nothing is dropped.

    Returns:
        The `MasterProof`. `read_from` is taken from the first edit_copy,
        copied rather than aliased -- matching `binder.bind`'s own rule for the
        same field, so a caller mutating its own dict afterward cannot change
        what the master_proof already holds. An empty `edit_copies` gathers to
        `{}`, since there is no first copy to take it from.

    Raises:
        MismatchedRoot: a later edit_copy's `read_from` disagrees with the
            first's -- naming both values.
    """
    read_from: dict = {}
    for i, copy in enumerate(edit_copies):
        if i == 0:
            read_from = {**copy.read_from}
        elif copy.read_from != read_from:
            raise MismatchedRoot(
                f"edit_copy {i} ({copy.role!r}) was censused from "
                f"{copy.read_from!r}, disagreeing with the master_proof's "
                f"{read_from!r}"
            )
    return MasterProof(
        stage=stage,
        # ! COPIED TWICE, AND EACH COPY ANSWERS A DIFFERENT CALLER. The
        # `{**copy.read_from}` above keeps the LOOP from comparing a value it
        # has aliased to the first copy's own dict; this one keeps the proof
        # from being changed through whatever the caller still holds.
        read_from={**read_from},
        edit_copies=tuple(edit_copies),
    )
