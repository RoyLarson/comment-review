"""`desk/proof.py`: the roles level that `binder` and `docket` lack.

! Every `edit_copy` comes from the real `seed()` over a real binder, through
`binder_of` -- `CLAUDE.md`'s rule for this suite: no hand-authored container
literal where a real one can be built.
"""

from pathlib import Path

import pytest
from helpers import binder_of

from comment_review.desk.proof import MismatchedRoot, gather
from comment_review.flows.marks import seed

DESK = Path(__file__).resolve().parents[1] / "src" / "comment_review" / "desk"


def test_a_master_proof_holds_every_edit_copy_of_one_stage():
    binder = binder_of(DESK, 0)
    copies = [seed(binder, role) for role in ("block-context", "module-context")]
    proof = gather("4c", copies)
    assert [c["role"] for c in proof["edit_copies"]] == [
        "block-context",
        "module-context",
    ]
    assert proof["read_from"] == binder["read_from"]


def test_one_role_and_seven_shards_both_assemble():
    binder = binder_of(DESK, 0)
    assert len(gather("4a", [seed(binder, "ownership-context")])["edit_copies"]) == 1
    shards = [seed(binder, "block-context") for _ in range(7)]
    assert len(gather("4c", shards)["edit_copies"]) == 7


def test_an_edit_copy_from_another_root_is_refused():
    # ! THE CHECK THAT CAN FAIL: two copies censused from different revises
    # cannot be reconciled -- their addresses answer to different trees.
    a = seed(binder_of(DESK, 0), "block-context")
    b = seed(binder_of(DESK, 0), "module-context")
    b["read_from"] = {**b["read_from"], "revise": 1}
    with pytest.raises(MismatchedRoot):
        gather("4c", [a, b])


def test_edit_copies_that_cannot_say_which_tree_they_read_are_refused():
    """Copies with the field STRIPPED compared equal under a `{}` default, so
    the one rule this module enforces could not fire on them -- two copies that
    cannot say which tree they were censused from agreed with each other."""
    roles = ("block-context", "module-context")
    copies = [seed(binder_of(DESK, 0), role) for role in roles]
    for copy in copies:
        del copy["read_from"]
    with pytest.raises(KeyError):
        gather("4c", copies)
