"""The dispositions table: what the chief may close, and what text it sets."""

from comment_review.desk.dispositions.disposition import CHIEF, Disposition
from comment_review.desk.dispositions.table import DISPOSITIONS
from comment_review.desk.proof.state import State


def test_taken_in_closes_a_carried_place_with_one_sides_text_or_the_original():
    row = DISPOSITIONS["taken_in"]
    assert row.closes == frozenset({State.COMPOSED, State.CONTESTED})
    sides = {"block-context": "# theirs\n", "module-context": "# ours\n"}
    ours = Disposition(
        address="m.py@b1", name="taken_in", side="module-context", prose="", reason="r"
    )
    assert row.sets(ours, "# base\n", sides) == "# ours\n"
    original = Disposition(
        address="m.py@b1", name="taken_in", side="original", prose="", reason="r"
    )
    assert row.sets(original, "# base\n", sides) is None


def test_recast_sets_the_chiefs_prose():
    row = DISPOSITIONS["recast"]
    recast = Disposition(
        address="m.py@b1",
        name="recast",
        side="copy-chief",
        prose="# mine\n",
        reason="r",
    )
    assert row.sets(recast, "# base\n", {}) == "# mine\n"
    assert row.owes == ("prose",)


def test_no_disposition_closes_an_unsettlable_place():
    for row in DISPOSITIONS.values():
        assert State.UNSETTLABLE not in row.closes


def test_a_disposition_is_read_by_name():
    got, why = Disposition.deserialize(
        "m.py@b1",
        {"address": "m.py@b1", "answer": "taken_in", "side": "original", "reason": "r"},
    )
    assert why == [] and got is not None
    got, why = Disposition.deserialize(
        "m.py@b1", {"address": "m.py@b1", "answer": "recast", "reason": "r"}
    )
    assert got is None and "needs `prose`" in why[0]
    got, why = Disposition.deserialize(
        "m.py@b1", {"address": "m.py@b1", "answer": "correct", "reason": "r"}
    )
    assert got is None and "a role's answer" in why[0]


def test_a_recast_with_no_side_takes_the_rows_own():
    got, why = Disposition.deserialize(
        "m.py@b1",
        {"address": "m.py@b1", "answer": "recast", "prose": "# mine\n", "reason": "r"},
    )
    assert why == [] and got is not None and got.side == CHIEF


def test_a_taken_in_with_no_side_is_refused():
    got, why = Disposition.deserialize(
        "m.py@b1", {"address": "m.py@b1", "answer": "taken_in", "reason": "r"}
    )
    assert got is None and "needs `side`" in why[0]
