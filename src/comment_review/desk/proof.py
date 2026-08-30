"""The roles level: every `edit_copy` of one stage, gathered into one `master_proof`.

    gather(stage, edit_copies)   {"stage": ..., "read_from": ..., "edit_copies": [...]}

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


class MismatchedRoot(Exception):
    """Two `edit_copies` handed to `gather` were censused from different roots.

    !! THE ONLY RULE WITH A NAMED EXCEPTION HERE, and it has to be one that can
    fail: two edit_copies censused from different revises cannot be
    reconciled, because their addresses answer to different trees -- an `a0`
    from one tells nothing about the `a0` in the other.

    ! IT COULD NOT FIRE FOR AN ABSENT FIELD, WHICH IS WHY `gather` SUBSCRIPTS.
    Reading `copy.get("read_from", {})` made every copy that carried none agree
    on `{}`, so a set of edit_copies that could not say which tree they were
    censused from compared EQUAL and gathered without complaint. The absence is
    now `flows.distribute.seed`'s own `KeyError`, one level further along.
    """


def gather(stage: str, edit_copies: list[dict]) -> dict:
    """Every `edit_copy` of one stage, as the master_proof that holds them.

    Args:
        stage: the stage label these edit_copies were dispatched under, e.g.
            `SKILL.md`'s `"4a"` or `"4c"`.
        edit_copies: as `flows.distribute.seed` returns one -- one per role, or
            one per shard under fan-out. Held in the order given: nothing is
            sorted and nothing is dropped.

    Returns:
        `{"stage": stage, "read_from": ..., "edit_copies": [...]}`.
        `read_from` is taken from the first edit_copy, copied rather than
        aliased -- matching `binder.bind`'s own rule for the same field, so a
        caller mutating its own dict afterward cannot change what the
        master_proof already holds. An empty `edit_copies` gathers to `{}`,
        since there is no first copy to take it from.

    Raises:
        MismatchedRoot: a later edit_copy's `read_from` disagrees with the
            first's -- naming both values.
        KeyError: an edit_copy carries no `read_from` at all. `seed` writes the
            field onto every copy it hands out and refuses a binder without
            one, so a copy reaching here without it was not seeded or was
            stripped after it was.
    """
    read_from: dict = {}
    for i, copy in enumerate(edit_copies):
        this = copy["read_from"]
        if i == 0:
            read_from = {**this}
        elif this != read_from:
            raise MismatchedRoot(
                f"edit_copy {i} ({copy.get('role', '?')!r}) was censused from "
                f"{this!r}, disagreeing with the master_proof's {read_from!r}"
            )
    return {
        "stage": stage,
        "read_from": read_from,
        "edit_copies": list(edit_copies),
    }
