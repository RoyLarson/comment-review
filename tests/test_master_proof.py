"""`desk/proof.py`: the roles level that `binder` and `docket` lack.

! Every `edit_copy` comes from the real `seed()` over a real binder, through
`binder_of` -- `CLAUDE.md`'s rule for this suite: no hand-authored container
literal where a real one can be built.
"""

from pathlib import Path

import pytest
from helpers import binder_of, returned

from comment_review.desk.proof import MismatchedRoot, gather
from comment_review.flows.distribute import seed

DESK = Path(__file__).resolve().parents[1] / "src" / "comment_review" / "desk"


def test_a_master_proof_holds_every_edit_copy_of_one_stage():
    binder = binder_of(DESK, 0)
    copies = [
        returned(seed(binder, role)) for role in ("block-context", "module-context")
    ]
    proof = gather("4c", copies)
    assert [c.role for c in proof.edit_copies] == ["block-context", "module-context"]
    assert proof.read_from == binder.read_from


def test_one_role_and_seven_shards_both_assemble():
    binder = binder_of(DESK, 0)
    one = gather("4a", [returned(seed(binder, "ownership-context"))])
    assert len(one.edit_copies) == 1
    shards = [returned(seed(binder, "block-context")) for _ in range(7)]
    assert len(gather("4c", shards).edit_copies) == 7


def test_an_edit_copy_from_another_root_is_refused():
    # ! THE CHECK THAT CAN FAIL: two copies censused from different revises
    # cannot be reconciled -- their addresses answer to different trees.
    a = returned(seed(binder_of(DESK, 0), "block-context"))
    wire = seed(binder_of(DESK, 0), "module-context")
    wire["read_from"] = {**wire["read_from"], "revise": 1}
    with pytest.raises(MismatchedRoot):
        gather("4c", [a, returned(wire)])


#: !! `test_edit_copies_that_cannot_say_which_tree_they_read_are_refused` WENT
#: WITH `P42`, and what it measured is now unreachable rather than untested. It
#: deleted `read_from` from two seeded copies and asserted `gather` raised
#: `KeyError` -- the subscript that existed because a `{}` default had made two
#: copies which could not say which tree they read compare EQUAL. `gather` takes
#: `EditCopy`s now, and `EditCopy.deserialize` refuses a copy with no
#: `read_from` before one can be built, so the stripped shape cannot be
#: assembled to hand in. The refusal is
#: `tests/test_containers.py::TestWhatItRefuses::
#: test_an_edit_copy_whose_read_from_is_the_wrong_SHAPE`.
