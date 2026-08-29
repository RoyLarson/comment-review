"""`desk/collator.py`'s `places` and `reconcile` -- T4.1 and T4.2,
reconciliation's grouping and its settle/escalate/reread rule.

! INPUTS FROM REALITY, `decision-log.md Vocabulary: #23`: every mark below is
built through `desk.mark.INSTRUCTIONS` by `tests/helpers.py`'s `a_correct`,
`a_move`, `a_clean` and `a_query`, and every `master_proof` is composed
through the real `seed()` and `gather()` by `a_master_proof` -- never a
hand-authored container literal.

!! `reconcile`'s expectation is `Process: #49`, NOT `reconcile` ITSELF --
`CLAUDE.md`'s rule that no test takes its expectation from the code under
test. Settle/escalate/reread come from Roy's own ruling, quoted on
`reconcile`'s docstring; the tests below check the outcomes that ruling
names, not whatever the function happens to return.
"""

from helpers import a_clean, a_correct, a_master_proof, a_move, a_query

from comment_review.desk.collator import places, reconcile


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


def test_one_change_settles_because_nobody_composed_anything():
    proof = a_master_proof({"block-context": {"m.py@b1": a_correct("m.py@b1")}})
    out = reconcile(proof)
    assert [s["address"] for s in out.settled] == ["m.py@b1"]
    assert out.escalations == [] and out.rereads == []


def test_two_changes_on_different_sentences_are_RE_READ_not_merged():
    proof = a_master_proof({
        "block-context": {"m.py@b1": a_correct("m.py@b1", sentence=0)},
        "module-context": {"m.py@b1": a_correct("m.py@b1", sentence=2)},
    })
    out = reconcile(proof)
    assert out.settled == []
    assert [r["address"] for r in out.rereads] == ["m.py@b1"]
    assert sorted(out.rereads[0]["roles"]) == ["block-context", "module-context"]


def test_two_changes_on_the_SAME_sentence_escalate():
    proof = a_master_proof({
        "block-context": {"m.py@b1": a_correct("m.py@b1", sentence=0)},
        "module-context": {"m.py@b1": a_correct("m.py@b1", sentence=0)},
    })
    out = reconcile(proof)
    assert [e["address"] for e in out.escalations] == ["m.py@b1"]


def test_clean_and_query_owe_no_change_so_they_compose_nothing():
    proof = a_master_proof({
        "block-context": {"m.py@b1": a_clean("m.py@b1")},
        "module-context": {"m.py@b1": a_query("m.py@b1")},
    })
    out = reconcile(proof)
    assert out.rereads == [] and out.escalations == []
