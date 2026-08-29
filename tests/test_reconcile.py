"""`desk/collator.py`'s `places` -- T4.1, reconciliation's first step.

! INPUTS FROM REALITY, `decision-log.md Vocabulary: #23`: every mark below is
built through `desk.mark.INSTRUCTIONS` by `tests/helpers.py`'s `a_correct`
and `a_move`, and every `master_proof` is composed through the real `seed()`
and `gather()` by `a_master_proof` -- never a hand-authored container literal.
"""

from helpers import a_correct, a_master_proof, a_move

from comment_review.desk.collator import places


def test_a_move_lands_in_both_the_origin_and_the_destination():
    # T1's failing case: a move a0 -> a8 against another role's correct on a8.
    proof = a_master_proof({
        "block-context": {"m.py@a0": a_move("m.py@a0", "m.py@a8")},
        "module-context": {"m.py@a8": a_correct("m.py@a8")},
    })
    grouped = places(proof)
    assert "m.py@a0" in grouped and "m.py@a8" in grouped
    assert len(grouped["m.py@a8"]) == 2, "the move must reach its destination"


def test_every_mark_carries_the_role_that_made_it():
    proof = a_master_proof({"block-context": {"m.py@b1": a_correct("m.py@b1")}})
    assert places(proof)["m.py@b1"][0]["role"] == "block-context"
