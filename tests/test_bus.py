"""The bus: one message in, the fold's events and what the stage saves out."""

from helpers import (
    a_clean,
    a_correct_citing,
    a_correct_setting,
    a_real_binder_over,
    copies_over,
    returned,
)

from comment_review.desk.evaluate.place import Place
from comment_review.desk.work import events
from comment_review.flows.bus import CopiesReturned, handle

BASE = "# one\n# two\n# three"
OTHER = "# four\n# five\n# six"
CORRECTED = "# one\n# TWO\n# three"


def _message(tmp_path, by_role):
    root = tmp_path / "repo"
    binder = a_real_binder_over(root, {"m.py@b1": BASE, "m.py@b2": OTHER})
    copies = [returned(wire) for wire in copies_over(binder, by_role)]
    return CopiesReturned("4c", copies, binder, root, None)


TWO_ROLES = {
    "block-context": {
        "m.py@b1": a_correct_setting("m.py@b1", "two", CORRECTED),
        "m.py@b2": a_clean("m.py@b2"),
    },
    "function-context": {
        "m.py@b1": a_clean("m.py@b1"),
        "m.py@b2": a_clean("m.py@b2"),
    },
}


def test_a_committed_fold_says_what_it_settled(tmp_path):
    out, result = handle(_message(tmp_path, TWO_ROLES))
    assert events.Settled("m.py@b1", CORRECTED) in out
    assert events.Settled("m.py@b2", None) in out
    assert events.Committed(2) in out
    assert result is not None


def test_a_committed_fold_carries_its_places_on_the_proof(tmp_path):
    _out, result = handle(_message(tmp_path, TWO_ROLES))
    assert result is not None
    assert len(result.proof.places) == 2
    for entry in result.proof.places:
        place, why = Place.deserialize("a place", entry)
        assert place is not None, why
        assert place.serialize() == entry


def test_the_chief_copy_holds_one_mark_at_the_settled_place(tmp_path):
    _out, result = handle(_message(tmp_path, TWO_ROLES))
    assert result is not None
    assert result.chief is not None
    marks = [mark for sheet in result.chief.sheets for mark in sheet.marks]
    assert [mark.address for mark in marks] == ["m.py@b1"]
    assert marks[0].change == CORRECTED


def test_a_cite_that_resolves_against_nothing_rolls_the_fold_back(tmp_path):
    out, result = handle(
        _message(
            tmp_path,
            {
                "block-context": {
                    "m.py@b1": a_correct_citing("m.py@b1", "nowhere.py:1"),
                    "m.py@b2": a_clean("m.py@b2"),
                }
            },
        )
    )
    assert result is None
    refused = [one for one in out if isinstance(one, events.Refused)]
    assert refused
    assert refused[0].role == "block-context"
    assert refused[0].address == "m.py@b1"
    assert any(isinstance(one, events.RolledBack) for one in out)
