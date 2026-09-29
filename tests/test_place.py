"""Place: the serialize round trip.

Which marks propose, and what each sets where it is filed, is
`desk.evaluate.passes.sides_of`'s -- `tests/test_passes.py`. It lived on
`Place.proposals` until `decision-log.md Process: #179` gave a role's several
marks at one place one side between them, which is a composition that can
refuse and so belongs where the reasons are read.
"""

from helpers import a_typed_answer, a_typed_mark, a_typed_ruling

from comment_review.desk.proof.answer import Question
from comment_review.desk.proof.disposition import ORIGINAL
from comment_review.desk.proof.mark import Instruction, Touch
from comment_review.desk.proof.place import Filed, Place
from comment_review.desk.proof.state import State

BASE = "# one\n# two\n# three\n"


def _mark(
    instruction, change="", raw_text=BASE, claim=None, address="m.py@b1", sources=()
):
    return a_typed_mark(
        instruction,
        address=address,
        anchor="x = 1",
        raw_text=raw_text,
        claim=claim or {},
        reason="r",
        sources=sources,
        change=change,
    )


def test_a_place_round_trips_through_serialize():
    corr = _mark(
        Instruction.CORRECT,
        change="# one\n# 2\n# three\n",
        claim={"false": "two", "true": "2"},
        sources=({"cite": "m.py:1", "verbatim": "two"},),
    )
    answer = a_typed_answer(
        address="m.py@b1",
        anchor="x = 1",
        question=Question.ESCALATION,
        name="hold",
        reason="the prose is right as it stands",
    )
    disposition = a_typed_ruling(
        address="m.py@b1",
        name="taken_in",
        side=ORIGINAL,
        prose="",
        reason="the base already says this",
    )
    place = Place(
        address="m.py@b1",
        anchor="x = 1",
        base=BASE,
        readers=("a", "b"),
        filed=[
            Filed("a", corr, Touch.OWN),
            # A half of a split move keeps the move it came from across a save,
            # so a later turn's refusal still names the move the role filed.
            Filed(
                "b",
                _mark(
                    Instruction.DROP,
                    claim={"drop": "# three"},
                    sources=({"cite": "m.py:1", "verbatim": "x = 1"},),
                ),
                Touch.OWN,
                "m.py@b1",
            ),
        ],
        answers={1: {"a": answer}},
        disposition=disposition,
        state=State.STANDS,
        text="# one\n# 2\n# three\n",
        sides={"a": "# one\n# 2\n# three\n"},
        reasons=(),
        question=None,
    )
    got, problems = Place.deserialize("m.py@b1", place.serialize())
    assert problems == []
    assert got == place


def test_deserialize_refuses_a_place_that_is_not_an_object():
    got, problems = Place.deserialize("m.py@b1", "not a place")
    assert got is None
    assert problems == ["m.py@b1: a place must be an object"]


def test_a_state_or_question_outside_its_set_is_named():
    got, problems = Place.deserialize(
        "m.py@b1", {"address": "m.py@b1", "state": "limbo", "question": "why"}
    )
    assert got is None
    assert problems == [
        "m.py@b1: `state` 'limbo' is not one of stands, agreed, composed,"
        " contested, unsettlable, refused, to-come",
        "m.py@b1: `question` 'why' is not one of escalation, composition, placement",
    ]


def test_an_answer_at_a_turn_that_is_not_a_number_is_named():
    """A turn key is read as an integer; one that is not is a problem named at
    the place, not a `ValueError` out of the read."""
    got, problems = Place.deserialize(
        "m.py@b1",
        {
            "address": "m.py@b1",
            "answers": {
                "first": {
                    "block-context": {
                        "address": "m.py@b1",
                        "question": "composition",
                        "instruction": "clean",
                        "reason": "r",
                    }
                }
            },
        },
    )
    assert got is None
    assert problems == ["m.py@b1: answers at turn 'first' -- a turn is a number"]
