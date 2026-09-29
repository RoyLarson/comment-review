"""The dispositions table: what the chief may close, and what text it sets --
and the ruling types it is keyed by."""

import pytest
from helpers import a_typed_ruling

from comment_review.desk.dispositions.table import DISPOSITIONS
from comment_review.desk.proof.disposition import (
    CHIEF,
    RULINGS,
    RecastRuling,
    TakenInRuling,
    disposition_type,
    read_disposition,
)
from comment_review.desk.proof.state import State


def test_every_row_of_the_table_is_a_ruling_type():
    """The table's keys, the one `match` and `RULINGS` state one set three
    ways, so the three are held equal."""
    assert {one.name for one in RULINGS} == set(DISPOSITIONS)
    for name in DISPOSITIONS:
        kind = disposition_type(name)
        assert kind is not None and kind.name == name
    assert disposition_type("stet") is None


@pytest.mark.parametrize(
    "entry",
    [
        {
            "address": "m.py@b1",
            "side": "module-context",
            "prose": "",
            "reason": "r",
            "to": "",
            "answer": "taken_in",
        },
        {
            "address": "m.py@b1",
            "side": "",
            "prose": "# mine\n",
            "reason": "r",
            "to": "",
            "answer": "recast",
        },
        {
            "address": "m.py@b1",
            "side": "original",
            "prose": "",
            "reason": "r",
            "to": "m.py@b5",
            "answer": "taken_in",
        },
    ],
    ids=["taken-in", "recast", "placement"],
)
def test_each_ruling_writes_the_wire_entry_it_read(entry):
    """The wire is unchanged by the types; compared as entries, not key order."""
    got, why = read_disposition("m.py@b1", entry)
    assert why == [] and got is not None
    assert got.serialize() == entry
    again, why = read_disposition("m.py@b1", got.serialize())
    assert why == [] and again == got


def test_taken_in_closes_a_carried_place_with_one_sides_text_or_the_original():
    row = DISPOSITIONS["taken_in"]
    assert row.closes == frozenset({State.COMPOSED, State.CONTESTED})
    sides = {"block-context": "# theirs\n", "module-context": "# ours\n"}
    ours = a_typed_ruling(
        address="m.py@b1", name="taken_in", side="module-context", prose="", reason="r"
    )
    assert row.sets(ours, "# base\n", sides) == "# ours\n"
    original = a_typed_ruling(
        address="m.py@b1", name="taken_in", side="original", prose="", reason="r"
    )
    assert row.sets(original, "# base\n", sides) is None


def test_recast_sets_the_chiefs_prose():
    row = DISPOSITIONS["recast"]
    recast = a_typed_ruling(
        address="m.py@b1",
        name="recast",
        side="copy-chief",
        prose="# mine\n",
        reason="r",
    )
    assert row.sets(recast, "# base\n", {}) == "# mine\n"
    assert RecastRuling.owes == ("prose",)
    assert TakenInRuling.owes == ("side",)


def test_no_disposition_closes_an_unsettlable_place():
    for row in DISPOSITIONS.values():
        assert State.UNSETTLABLE not in row.closes


def test_a_disposition_is_read_by_name():
    got, why = read_disposition(
        "m.py@b1",
        {"address": "m.py@b1", "answer": "taken_in", "side": "original", "reason": "r"},
    )
    assert why == [] and got is not None
    got, why = read_disposition(
        "m.py@b1", {"address": "m.py@b1", "answer": "recast", "reason": "r"}
    )
    assert got is None and "needs `prose`" in why[0]
    got, why = read_disposition(
        "m.py@b1", {"address": "m.py@b1", "answer": "correct", "reason": "r"}
    )
    assert got is None and "a role's answer" in why[0]


def test_a_recast_with_no_side_takes_the_rows_own():
    got, why = read_disposition(
        "m.py@b1",
        {"address": "m.py@b1", "answer": "recast", "prose": "# mine\n", "reason": "r"},
    )
    assert why == [] and got is not None and got.taken_side == CHIEF
    assert isinstance(got, RecastRuling)


def test_a_taken_in_with_no_side_is_refused():
    got, why = read_disposition(
        "m.py@b1", {"address": "m.py@b1", "answer": "taken_in", "reason": "r"}
    )
    assert got is None and "needs `side`" in why[0]
