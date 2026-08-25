"""What the agents hand the write chain -- an address, and the text for it.

! A STAND-IN. The middle piece is not designed; this is the SHAPE so the write
chain has something to build to. See TODO/notations-collides-with-annotations.md
-- the NAME is deferred, not settled.
"""

import json

import pytest
from conftest import SAMPLE, build, by_cue

from comment_review.binder.binder import bind
from comment_review.desk.notations import by_page, read


def test_a_well_formed_notations_file_reads():
    got, why = read(json.dumps({"m.py@b1": "# new", "m.py@c0": None}))
    assert why == ""
    assert got == {"m.py@b1": "# new", "m.py@c0": None}


def test_None_is_the_delete():
    got, why = read(json.dumps({"m.py@b1": None}))
    assert why == "" and got["m.py@b1"] is None


@pytest.mark.parametrize(
    "text,fragment",
    [
        ("{not json", "not JSON"),
        ("[]", "not a notations"),
        ('"a string"', "not a notations"),
        (json.dumps({"m.py@b1": 123}), "must be text"),
        (json.dumps({"m.py@b1": ["a", "b"]}), "must be text"),
        (json.dumps({"m.py@b1": ""}), "empty string"),
    ],
)
def test_what_is_refused(text, fragment):
    got, why = read(text)
    assert got == {}
    assert fragment in why


def test_a_refusal_is_never_an_empty_result():
    """!! THE DEFECT THIS EXISTS FOR. A guess that is wrong reads as an EMPTY
    input, which downstream is indistinguishable from a run with nothing to do."""
    got, why = read("[]")
    assert got == {} and why != ""


def _binder():
    return bind([build(SAMPLE)], absent=True)


def test_an_address_the_binder_carries_resolves_to_its_page_and_cue():
    page = build(SAMPLE)
    cue = next(c for c in by_cue(page) if c.startswith("b"))
    grouped, refused = by_page({f"m.py@{cue}": "# new"}, bind([page], absent=True))
    assert refused == []
    assert grouped == {"m.py": {cue: "# new"}}


def test_an_address_no_binder_row_names_is_REFUSED_and_named():
    grouped, refused = by_page({"m.py@b99": "# new"}, _binder())
    assert grouped == {}
    assert any("m.py@b99" in r for r in refused)


def test_a_file_the_binder_never_saw_is_REFUSED():
    grouped, refused = by_page({"other.py@b1": "# new"}, _binder())
    assert grouped == {}
    assert any("other.py@b1" in r for r in refused)


def test_ONE_bad_address_refuses_the_WHOLE_set():
    """!! ABORT-WHOLE. Roy, 2026-08-25: *"fails loud amd stops is the right
    answer for now."* A partial group is a state no page describes."""
    page = build(SAMPLE)
    cue = next(c for c in by_cue(page) if c.startswith("b"))
    grouped, refused = by_page(
        {f"m.py@{cue}": "# good", "m.py@b99": "# bad"}, bind([page], absent=True)
    )
    assert grouped == {}
    assert len(refused) == 1
