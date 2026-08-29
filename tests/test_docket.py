"""The DOCKET: pages, each with its path, its sha and its schedule of alterations.

!! EVERY DOCKET HERE IS HAND-WRITTEN JSON EXCEPT THE `role` TESTS BELOW, and
that is deliberate for the rest. A docket arrives from OUTSIDE this system --
the desk makes it -- so its FORMAT is a file format, not a value the code
produces. Building one with a helper and reading it back would be the code
agreeing with itself, which is the shape `docs/gates.md` records the round
trip scoring 699 of 699 on.

! `conftest.docket_from` exists for the CHAIN's cases, which assert things about
drafting rather than about the format. Most of this file does not use it.

!! `desk.collator.docket_from` IS DIFFERENT: it is the desk's own production
code, T4.5's answer to "the desk is not built" -- so the two `role` tests
below assert what THAT function produces, the one case in this file where
building a docket and reading it back is the actual thing under test rather
than the format's own witness.

! THE NAME IS SETTLED, 2026-08-26 -- `decision-log.md Vocabulary: #14`. It was
`notations`, one letter from the `annotations` that `binder/annotate.py` owns.
"""

import json

import pytest
from helpers import a_correct, a_drop, a_master_proof, a_move

from comment_review.desk.collator import MalformedMark, docket_from, reconcile
from comment_review.docket.docket import read, schedules_of
from comment_review.flows.revise import _set_by


def a_docket(pages) -> str:
    """The JSON text of a docket over `[(path, sha, [(cue, text), ...]), ...]`."""
    return json.dumps(
        {
            "pages": [
                {
                    "path": path,
                    "sha": sha,
                    "alterations": [{"cue": c, "text": t} for c, t in alterations],
                }
                for path, sha, alterations in pages
            ]
        }
    )


def test_a_well_formed_docket_reads():
    got, why = read(a_docket([("m.py", "abc123", [("b1", "# new"), ("c0", None)])]))
    assert why == ""
    assert got["pages"][0]["path"] == "m.py"


def test_None_is_the_delete():
    got, why = read(a_docket([("m.py", "abc123", [("b1", None)])]))
    assert why == ""
    assert got["pages"][0]["alterations"][0]["text"] is None


@pytest.mark.parametrize(
    "text,fragment",
    [
        ("{not json", "not JSON"),
        ("[]", "not a docket"),
        ('"a string"', "not a docket"),
        ("{}", "no `pages` key"),
        (json.dumps({"pages": []}), "non-empty list"),
        (json.dumps({"pages": "oops"}), "non-empty list"),
        (json.dumps({"pages": [1]}), "must be an object"),
        (json.dumps({"pages": [{"sha": "a", "alterations": []}]}), "needs a `path`"),
        (json.dumps({"pages": [{"path": "", "sha": "a"}]}), "needs a `path`"),
        (
            json.dumps({"pages": [{"path": "m.py", "alterations": []}]}),
            "needs the `sha`",
        ),
        (json.dumps({"pages": [{"path": "m.py", "sha": ""}]}), "needs the `sha`"),
        (json.dumps({"pages": [{"path": "m.py", "sha": "a"}]}), "non-empty list"),
        (
            json.dumps({"pages": [{"path": "m.py", "sha": "a", "alterations": []}]}),
            "non-empty list",
        ),
        (
            json.dumps({"pages": [{"path": "m.py", "sha": "a", "alterations": [1]}]}),
            "must be an object",
        ),
        (a_docket([("m.py", "a", [("", "# x")])]), "needs a `cue`"),
        (a_docket([("m.py", "a", [("b1", 123)])]), "must be text or null"),
        (a_docket([("m.py", "a", [("b1", ["a"])])]), "must be text or null"),
        (a_docket([("m.py", "a", [("b1", "")])]), "empty string"),
    ],
)
def test_what_is_refused(text, fragment):
    got, why = read(text)
    assert got == {}
    assert fragment in why


def test_an_alteration_with_NO_text_key_is_refused():
    """!! ABSENT IS NOT null. A key that failed to serialise disappears rather
    than arriving as null, and reading a missing `text` as a delete is how a
    bug upstream becomes a deletion downstream at exit 0."""
    got, why = read(
        json.dumps(
            {"pages": [{"path": "m.py", "sha": "a", "alterations": [{"cue": "b1"}]}]}
        )
    )
    assert got == {}
    assert "needs `text`" in why


def test_a_refusal_is_never_an_empty_result():
    """!! THE DEFECT THIS EXISTS FOR. A guess that is wrong reads as an EMPTY
    input, which downstream is indistinguishable from a run with nothing to do."""
    got, why = read("[]")
    assert got == {} and why != ""


def test_an_EMPTY_DOCKET_IS_REFUSED_BY_NAME():
    """IMPORTANT, measured 2026-08-25 on the flat form: `read("{}")` answered
    `({}, "")`, so `proof_setter.run` drafted nothing and `commands/proof.py`
    printed `0 page(s) drafted for review` at exit 0 -- the
    empty-reads-as-success shape this module exists to prevent, and the one
    `binder.read` already refuses on a missing `pages` key."""
    got, why = read("{}")
    assert got == {}
    assert "no `pages` key" in why


def test_TWO_SCHEDULES_FOR_ONE_PAGE_are_refused():
    """!! ONE SCHEDULE PER PAGE. Two would let a later one silently win, and
    which applied would depend on iteration order -- the same class of defect
    as two paragraphs sharing an address, which `galley.reset` refuses by
    name."""
    got, why = read(
        a_docket([("m.py", "a", [("b1", "# one")]), ("m.py", "a", [("b2", "# two")])])
    )
    assert got == {}
    assert "two schedules for one page" in why


def test_TWO_ALTERATIONS_FOR_ONE_PLACE_are_refused():
    got, why = read(a_docket([("m.py", "a", [("b1", "# one"), ("b1", "# two")])]))
    assert got == {}
    assert "two alterations for one place" in why


class TestSchedulesOf:
    """!! IT REFUSES NOTHING, and that is what the nesting bought. The flat form
    returned `(grouped, refusals)` because it had to SPLIT an address to find
    the path, and a malformed one could not be split. `read` rules on the shape
    now, so this only unwinds."""

    def test_one_schedule_per_page_in_docket_order(self):
        docket, why = read(
            a_docket(
                [
                    ("pkg/a/util.py", "sha1", [("b0", "# first")]),
                    ("top.py", "sha2", [("c0", None)]),
                ]
            )
        )
        assert why == ""
        schedules = schedules_of(docket)
        assert [s.path for s in schedules] == ["pkg/a/util.py", "top.py"]
        assert [s.sha for s in schedules] == ["sha1", "sha2"]

    def test_the_path_is_the_REPO_S_and_is_not_flattened(self):
        """!! THE WHOLE POINT OF THE NESTING. An ADDRESS carries `pkg:a:util.py`
        and needed `unflatten` plus the binder's page paths to recover a real
        one -- and MEASURED 2026-08-25, using the flattened key as a path meant
        every file below the repo root refused. A schedule states the path."""
        docket, _ = read(a_docket([("pkg/a/util.py", "sha", [("b0", "# x")])]))
        assert schedules_of(docket)[0].path == "pkg/a/util.py"

    def test_the_alterations_are_cue_to_text(self):
        docket, _ = read(a_docket([("m.py", "sha", [("b1", "# new"), ("c0", None)])]))
        assert schedules_of(docket)[0].alterations == {"b1": "# new", "c0": None}


def test_the_docket_names_the_role_that_set_each_alteration():
    proof = a_master_proof({"block-context": {"m.py@b1": a_correct("m.py@b1")}})
    docket = docket_from(reconcile(proof), proof)
    assert docket["pages"][0]["role"] == "block-context"


def test_set_by_stops_mapping_everything_to_empty():
    # `revise.pull._set_by` reads an optional `role` per page and used to map
    # every address to "" because nothing wrote it -- see `_set_by`'s own
    # docstring. `docket_from` is what writes it now.
    proof = a_master_proof({"block-context": {"m.py@b1": a_correct("m.py@b1")}})
    docket = docket_from(reconcile(proof), proof)
    assert set(_set_by(docket).values()) == {"block-context"}


def test_a_page_two_roles_settled_names_NEITHER_of_them():
    """!! A FALSE ATTRIBUTION IS WORSE THAN AN ABSENT ONE. `role` is one per
    page, so a page holding two roles' settled places can only name one of
    them -- and `set_by` is what a later phase ROUTES a reversal on
    (`flows.revise.Pulled`), which would send it to a role that never touched
    the place. The docket omits the field instead, and `_set_by` says `""`."""
    proof = a_master_proof({
        "block-context": {"m.py@b1": a_correct("m.py@b1")},
        "module-context": {"m.py@b3": a_correct("m.py@b3")},
    })
    docket = docket_from(reconcile(proof), proof)
    page = docket["pages"][0]
    assert sorted(one["cue"] for one in page["alterations"]) == ["b1", "b3"]
    assert "role" not in page
    assert set(_set_by(docket).values()) == {""}
    assert read(json.dumps(docket))[1] == ""


def test_a_settled_move_DELETES_its_origin_and_writes_its_destination():
    """!! A `move` IS A DELETE AT ONE END AND AN ADD AT THE OTHER
    (`docs/the-mark.md`): *"a move = a delete at the origin + an add at the
    destination"*. Writing `change` at both ends is the duplication the one
    instruction exists to prevent."""
    proof = a_master_proof({"block-context": {"m.py@a0": a_move("m.py@a0", "m.py@a8")}})
    docket = docket_from(reconcile(proof), proof)
    alterations = {one["cue"]: one["text"] for one in docket["pages"][0]["alterations"]}
    assert alterations["a0"] is None
    assert isinstance(alterations["a8"], str) and alterations["a8"]


def test_a_change_in_the_RETIRED_ARRAY_FORM_never_reaches_the_docket():
    """!! `None` IS THE DELETE SIGNAL, so a `change` that has no text to set
    must not reach it -- `docket/docket.py`'s own header: *"a key whose value
    failed to serialise arrives looking exactly like a deliberate deletion."*
    MEASURED 2026-08-29: `_alteration_text` joined `change if isinstance(change,
    list) else []`, so a raw-text `change` produced `None`, `docket.read`
    accepted it, and the paragraph was EMPTIED.

    ! IT IS THE PARSE THAT REFUSES IT NOW, at `places`, not a check inside the
    docket step -- `desk.mark.parse` rules `change` raw text
    (`TODO/change-is-raw-text-not-lines.md`), so `MalformedMark` is raised
    before any alteration is built. The `UnusableChange` exception this case
    used to assert is gone with the shape that could reach it."""
    mark = a_correct("m.py@b1")
    mark["change"] = [mark["change"]]
    proof = a_master_proof({"block-context": {"m.py@b1": mark}})
    with pytest.raises(MalformedMark):
        docket_from(reconcile(proof), proof)


def test_an_EMPTY_change_refuses_where_the_instruction_may_not_empty():
    mark = a_correct("m.py@b1")
    mark["change"] = ""
    proof = a_master_proof({"block-context": {"m.py@b1": mark}})
    with pytest.raises(MalformedMark):
        docket_from(reconcile(proof), proof)


def test_an_EMPTY_change_IS_the_delete_where_the_row_may_empty():
    """`drop` is the one row `INSTRUCTIONS[...].may_empty` is True for, which
    is what the refusal above is read from rather than from a named
    instruction."""
    mark = a_drop("m.py@b1")
    mark["change"] = ""
    proof = a_master_proof({"block-context": {"m.py@b1": mark}})
    docket = docket_from(reconcile(proof), proof)
    assert docket["pages"][0]["alterations"] == [{"cue": "b1", "text": None}]


def test_NO_DOCKET_CARRIES_ONE_END_OF_A_MOVE():
    """The design's own sentence, section 3: a `move` settles or escalates
    WHOLE, so **no docket ever carries one end of one**. Half-applied, it is
    invisible downstream -- both dockets read, both set, and `prove_unchanged`
    passes either way because only prose moved."""
    proof = a_master_proof({
        "block-context": {"m.py@a0": a_move("m.py@a0", "m.py@a8")},
        "module-context": {"m.py@a8": a_correct("m.py@a8", "a different sentence")},
    })
    assert docket_from(reconcile(proof), proof) == {"pages": []}
