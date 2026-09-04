"""`desk.determined` -- a PROTOTYPE. `decision-log.md Process: #87`.

Mirrors `test_diff_mark.py`'s shape tests, over the chief's own object, and
proves the master proof carries the turn record and the rulings across a
round trip.
"""

from dataclasses import replace

import pytest
from helpers import a_correct, a_master_proof

from comment_review.desk.containers import MasterProof
from comment_review.desk.determined import (
    CHIEF,
    HOW,
    ORIGINAL,
    Answer,
    Determined,
)
from comment_review.desk.diff_mark import DiffInstruction
from comment_review.desk.mark import INSTRUCTIONS, Instruction, Mark


def _a_mark(address: str = "m.py@b1") -> Mark:
    return Mark(
        address=address,
        anchor="def f(x):",
        raw_text="# as it stands\n",
        instruction=Instruction.CORRECT,
        claim={"false": "as it stands", "true": "as it should read"},
        reason="the paragraph is stale",
        # ! A `correct` OWES A SOURCE, and `Mark.deserialize` refuses one
        # without; the round trips below go through that boundary.
        sources=({"cite": "m.py:1", "verbatim": "def f(x):"},),
        change="# as it should read\n",
    )


def _a_ruling(**over) -> dict:
    entry = {
        "address": "m.py@b1",
        "answer": "taken_in",
        "turn": 2,
        "side": "block-context",
        "how": "cap",
        "reason": "block-context's reading is the one the code supports",
        "mark": _a_mark().serialize(),
    }
    entry.update(over)
    return entry


def test_the_closed_set_is_exactly_three():
    assert set(Answer) == {"stet", "taken_in", "recast"}
    assert HOW == ("one", "identical", "withdrawn", "cap")


@pytest.mark.parametrize("named", sorted(INSTRUCTIONS))
def test_a_marks_instruction_is_refused_by_name(named):
    got, why = Determined.deserialize("x", _a_ruling(answer=named))
    assert got is None
    assert any("a role's answer" in w for w in why)


@pytest.mark.parametrize("named", sorted(DiffInstruction))
def test_a_diff_marks_instruction_is_refused_by_name(named):
    got, why = Determined.deserialize("x", _a_ruling(answer=named))
    assert got is None
    assert any("a role's answer" in w for w in why)


def test_serialize_round_trips_through_deserialize():
    got, why = Determined.deserialize("x", _a_ruling())
    assert why == []
    assert got is not None
    again, why = Determined.deserialize("x", got.serialize())
    assert why == []
    assert again == got


def test_the_original_standing_carries_no_mark():
    got, why = Determined.deserialize("x", _a_ruling(side=ORIGINAL, mark=None))
    assert why == []
    assert got is not None
    assert got.mark is None
    again, why = Determined.deserialize("x", got.serialize())
    assert again == got


def test_a_stet_owes_no_reason():
    got, why = Determined.deserialize(
        "x", _a_ruling(answer="stet", how="identical", turn=0, reason="")
    )
    assert why == []
    assert got is not None and got.answer is Answer.STET


@pytest.mark.parametrize("answer", ["taken_in", "recast"])
def test_the_chiefs_own_answers_owe_a_reason(answer):
    got, why = Determined.deserialize(
        "x", _a_ruling(answer=answer, side=CHIEF, reason="")
    )
    assert got is None
    assert any("reason" in w for w in why)


def test_a_recast_needs_the_chiefs_mark():
    got, why = Determined.deserialize(
        "x", _a_ruling(answer="recast", side=CHIEF, mark=None)
    )
    assert got is None
    assert any("mark" in w for w in why)


def test_how_is_closed():
    got, why = Determined.deserialize("x", _a_ruling(how="composed"))
    assert got is None
    assert any("how" in w for w in why)


def test_a_master_proof_round_trips_turns_and_rulings():
    proof = a_master_proof({"block-context": {"m.py@b1": a_correct("m.py@b1")}})
    ruled = Determined("m.py@b1", Answer.STET, 0, "block-context", "one", "", _a_mark())
    proof = replace(
        proof,
        turns=({"turn": 1, "sent": {}, "returned": {}},),
        determined=(ruled,),
    )
    again, why = MasterProof.deserialize("p", proof.serialize())
    assert why == []
    assert again is not None
    assert again.turns == proof.turns
    assert again.determined == proof.determined


def test_a_master_proof_without_them_still_parses():
    """The wire `gather` wrote before Process 87 carried neither key."""
    proof = a_master_proof({"block-context": {"m.py@b1": a_correct("m.py@b1")}})
    wire = proof.serialize()
    del wire["turns"]
    del wire["determined"]
    again, why = MasterProof.deserialize("p", wire)
    assert why == []
    assert again is not None
    assert again.turns == ()
    assert again.determined == ()


def test_a_master_proof_round_trips_the_unsettlable_places():
    """`Process: #90`: the human's query rides on the proof to the end."""
    proof = a_master_proof({"block-context": {"m.py@b1": a_correct("m.py@b1")}})
    riding = {
        "address": "m.py@b1",
        "roles": ["block-context", "module-context"],
        "query": {"role": "module-context", "reason": "needs a human"},
    }
    proof = replace(proof, unsettlable=(riding,))
    again, why = MasterProof.deserialize("p", proof.serialize())
    assert why == []
    assert again is not None
    assert again.unsettlable == (riding,)
