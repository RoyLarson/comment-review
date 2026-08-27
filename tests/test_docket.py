"""The DOCKET: what the desk hands the write chain -- an address, and its text.

! THE SHAPE IS STILL A STAND-IN. The middle is not designed, so what is on disk
is one flat map and `schedules_of` derives the per-page grouping. The nested
form -- pages, each with its path, sha and schedule -- is task 4 of
`TODO/notations-collides-with-annotations.md`.

! THE NAME IS SETTLED, 2026-08-26 -- `decision-log.md Vocabulary: #14`. It was
`notations`, one letter from the `annotations` that `binder/annotate.py` owns.
"""

import json

import pytest
from conftest import SAMPLE, build, by_cue

from comment_review.docket.docket import read, schedules_of


def test_a_well_formed_alterations_file_reads():
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
        ("[]", "not a docket"),
        ('"a string"', "not a docket"),
        (json.dumps({"m.py@b1": 123}), "must be text"),
        (json.dumps({"m.py@b1": ["a", "b"]}), "must be text"),
        (json.dumps({"m.py@b1": ""}), "empty string"),
        ("{}", "no alterations"),
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


def test_an_EMPTY_DOCKET_FILE_is_refused_by_name():
    """IMPORTANT, measured 2026-08-25: `read("{}")` answered `({}, "")`, so
    `proof_setter.run` drafted nothing and `commands/proof.py` printed
    `0 page(s) drafted for review` at exit 0 -- the empty-reads-as-success
    shape this module's own docstring says it exists to prevent, and the one
    `binder.read` already refuses on a missing `pages` key."""
    got, why = read("{}")
    assert got == {}
    assert "no alterations" in why


def test_an_address_the_address_itself_resolves():
    page = build(SAMPLE)
    # Pick a cue that holds prose.
    cue = next(
        c
        for c, b in by_cue(page).items()
        if c.startswith("b") and any(x.strip() for x in b.raw_lines)
    )
    grouped, refused = schedules_of({f"m.py@{cue}": "# new"})
    assert refused == []
    assert grouped == {"m.py": {cue: "# new"}}


def test_a_malformed_address_is_REFUSED_and_named():
    grouped, refused = schedules_of({"malformed": "# new"})
    assert grouped == {}
    assert any("malformed" in r for r in refused)


def test_ONE_bad_address_refuses_the_WHOLE_set():
    """!! ABORT-WHOLE. Roy, 2026-08-25: *"fails loud amd stops is the right
    answer for now."* A partial group is a state no page describes."""
    page = build(SAMPLE)
    # Pick a cue that holds prose.
    cue = next(
        c
        for c, b in by_cue(page).items()
        if c.startswith("b") and any(x.strip() for x in b.raw_lines)
    )
    grouped, refused = schedules_of({f"m.py@{cue}": "# good", "malformed": "# bad"})
    assert grouped == {}
    assert len(refused) == 1
