"""What the agents hand the write chain -- an address, and the text for it.

! A STAND-IN. The middle piece is not designed; this is the SHAPE so the write
chain has something to build to. See TODO/notations-collides-with-annotations.md
-- the NAME is deferred, not settled.
"""

import json

import pytest

from comment_review.desk.notations import read


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
