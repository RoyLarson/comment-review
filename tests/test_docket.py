"""The DOCKET: pages, each with its path, its sha and its schedule of alterations.

!! EVERY DOCKET HERE IS HAND-WRITTEN JSON EXCEPT THE `role` TESTS BELOW, and
that is deliberate for the rest. A docket arrives from OUTSIDE this system --
the desk makes it -- so its FORMAT is a file format, not a value the code
produces. Building one with a helper and reading it back would be the code
agreeing with itself, which is the shape `docs/gates.md` records the round
trip scoring 699 of 699 on.

! `conftest.docket_from` exists for the CHAIN's cases, which assert things about
drafting rather than about the format. Most of this file does not use it.

!! `desk.collator.docket_from` IS GONE, since `P55`. It was the desk's own
production code and it built the WRITE END's artifact from inside the MIDDLE --
the only such import in the tree. What replaces it is
`flows/revise.py::docket_of`, which takes an `EditCopy`, and its cases live in
`tests/test_revise.py::TestDocketOf` beside it.

! SO THE CASES THAT USED IT SPLIT IN TWO, and neither claim was dropped. What
each was really asking is either RECONCILIATION -- what survives to be settled
at all, which now asks `reconcile()` directly instead of routing through a
transcription step to observe it -- or TRANSCRIPTION, which `TestDocketOf`
asserts over the copy the production path actually carries.

!! ONE CLAIM IS SUPERSEDED RATHER THAN MOVED, and it is the `role` of a page two
roles settled. `docket_from` read a per-place `roles` off `Reconciled`; an
`edit_copy` has one role for the whole copy, so `docket_of` writes that.
**The per-role fact is lost at the FOLD, not at the docket** -- Roy, 2026-09-02:
*"by the time the copy-chiefs edit-copy becomes the sole edit-copy in the master
proof the per role piece is lost. If we are pulling from the individual roles
already then we know the answer."* Pull a role's own copy and every schedule
names that role; pull the chief's and `copy-chief` is the true answer, because
the fold is what set it.

! THE NAME IS SETTLED, 2026-08-26 -- `decision-log.md Vocabulary: #14`. It was
`notations`, one letter from the `annotations` that `concordance/annotate.py` owns.
"""

import json

import pytest
from helpers import a_correct, a_drop, a_master_proof, a_move

from comment_review.desk.collator import reconcile
from comment_review.desk.containers import MasterProof
from comment_review.docket.docket import Alteration, Docket, Schedule
from comment_review.flows.revise import _set_by
from comment_review.machine.json_object import object_of

#: One ordinary alteration, for the cases whose subject is a SCHEDULE's own
#: fields rather than what any particular mark transcribes to.
A_ROW = Alteration(cue="b1", text="# new")


def _refused_reasons(proof) -> list[str]:
    """Every reason the parse gave for an entry it would not read as a mark.

    ! IT IS WHAT A RAISE USED TO BE. `places` raised `MalformedMark` on the
    first unreadable entry; `Sheet.refused` carries every one of them with the
    address that owns it, so a test asks what was refused rather than that
    something was.
    """
    return [
        reason
        for copy in proof.edit_copies
        for sheet in copy.sheets
        for one in sheet.refused
        for reason in one.reasons
    ]


def read(text: str):
    """The load and the deserialize, as `commands/proof.py` performs them.

    ! A TEST HELPER, NOT AN API. `docket.read` was one function and is now
    two steps in the FLOW -- `decision-log.md Process: #67` -- so a test
    that wants the pair spells the pair. ! What it must not do is hide the
    split: the `not JSON` and `not a docket` cases below are the two halves,
    and they are what used to come back from one call.
    """
    loaded, why = object_of(text, "docket")
    if why:
        return None, why
    got, problems = Docket.deserialize("d.json", loaded)
    return got, "; ".join(problems)


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
    assert got is not None
    assert got.schedules[0].path == "m.py"


def test_None_is_the_delete():
    got, why = read(a_docket([("m.py", "abc123", [("b1", None)])]))
    assert why == ""
    assert got is not None
    assert got.schedules[0].alterations[0].text is None


@pytest.mark.parametrize(
    "text,fragment",
    [
        ("{not json", "not JSON"),
        ("[]", "not a docket"),
        ('"a string"', "not a docket"),
        ("{}", "no `pages` key"),
        (json.dumps({"pages": []}), "non-empty list"),
        (json.dumps({"pages": "oops"}), "non-empty list"),
        (json.dumps({"pages": [1]}), "not a page"),
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
    assert got is None
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
    assert got is None
    assert "needs `text`" in why


def test_a_refusal_is_never_an_empty_result():
    """!! THE DEFECT THIS EXISTS FOR. A guess that is wrong reads as an EMPTY
    input, which downstream is indistinguishable from a run with nothing to do."""
    got, why = read("[]")
    assert got is None and why != ""


def test_an_EMPTY_DOCKET_IS_REFUSED_BY_NAME():
    """IMPORTANT, measured 2026-08-25 on the flat form: `read("{}")` answered
    `({}, "")`, so `proof_setter.run` drafted nothing and `commands/proof.py`
    printed `0 page(s) drafted for review` at exit 0 -- the
    empty-reads-as-success shape this module exists to prevent, and the one
    `binder.read` already refuses on a missing `pages` key."""
    got, why = read("{}")
    assert got is None
    assert "no `pages` key" in why


def test_TWO_SCHEDULES_FOR_ONE_PAGE_are_refused():
    """!! ONE SCHEDULE PER PAGE. Two would let a later one silently win, and
    which applied would depend on iteration order -- the same class of defect
    as two paragraphs sharing an address, which `galley.reset` refuses by
    name."""
    got, why = read(
        a_docket([("m.py", "a", [("b1", "# one")]), ("m.py", "a", [("b2", "# two")])])
    )
    assert got is None
    assert "two schedules for one page" in why


def test_TWO_ALTERATIONS_FOR_ONE_PLACE_are_refused():
    got, why = read(a_docket([("m.py", "a", [("b1", "# one"), ("b1", "# two")])]))
    assert got is None
    assert "two alterations for one place" in why


class TestTheDocketsOwnPages:
    """!! NOTHING UNWINDS A DOCKET ANY MORE, and that is what the containers
    bought. The flat form returned `(grouped, refusals)` because it had to
    SPLIT an address to find the path, and a malformed one could not be
    split; `schedules_of` then unwound the nested dict into `Schedule`s.
    `Docket.deserialize` builds them, so `docket.schedules` IS the answer --
    `decision-log.md Process: #67`."""

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
        assert docket is not None
        schedules = docket.schedules
        assert [s.path for s in schedules] == ["pkg/a/util.py", "top.py"]
        assert [s.sha for s in schedules] == ["sha1", "sha2"]

    def test_the_path_is_the_REPO_S_and_is_not_flattened(self):
        """!! THE WHOLE POINT OF THE NESTING. An ADDRESS carries `pkg:a:util.py`
        and needed `unflatten` plus the binder's page paths to recover a real
        one -- and MEASURED 2026-08-25, using the flattened key as a path meant
        every file below the repo root refused. A schedule states the path."""
        docket, _ = read(a_docket([("pkg/a/util.py", "sha", [("b0", "# x")])]))
        assert docket is not None
        assert docket.schedules[0].path == "pkg/a/util.py"

    def test_the_alterations_are_ALTERATIONS_in_docket_order(self):
        docket, _ = read(a_docket([("m.py", "sha", [("b1", "# new"), ("c0", None)])]))
        assert docket is not None
        alterations = docket.schedules[0].alterations
        assert [one.cue for one in alterations] == ["b1", "c0"]
        assert [one.text for one in alterations] == ["# new", None]

    def test_edits_is_the_cue_to_text_map_the_setter_consumes(self):
        """! `flows.proof_setter._one` sets places by cue and never asks about
        order, so the mapping is built once on the schedule. It was the
        `alterations` FIELD until 2026-08-31, which is why the third
        container level did not exist -- `Process: #67`."""
        docket, _ = read(a_docket([("m.py", "sha", [("b1", "# new"), ("c0", None)])]))
        assert docket is not None
        assert docket.schedules[0].edits == {"b1": "# new", "c0": None}


#: TRANSCRIPTION, moved: `test_the_docket_names_the_role_that_set_each_alteration`
#: is `TestDocketOf::test_the_schedule_carries_the_copys_own_role`, which runs an
#: `ownership-context` copy through and asserts the role that comes out.


def test_a_null_sha_reads_as_ABSENT_not_the_word_None():
    """!! `.get("sha", "")` DEFAULTS ONLY WHEN THE KEY IS ABSENT. A sheet
    carrying `"sha": null` arrives with the key PRESENT and holding None, so
    `.get` returns None and `str(None)` is the four-character word "None" --
    the same class of defect `results/verdicts.py` had over a null `verbatim`,
    which happened to render as text a cited line really held. Nothing
    downstream would catch it: the docket's own `sha` check refuses an EMPTY
    string, so "None" would pass through as a plausible-looking sha.

    !! THE FOLD MOVED AND THE END-TO-END CLAIM DID NOT, `P42`.
    `desk.collator._real_pages` carried its own copy of it and now reads
    `Sheet.sha`, which `Sheet.deserialize` already folded -- so the null goes
    into the WIRE here and the assertion still lands on the docket. That is the
    whole route a role's `"sha": null` travels, with one spelling of the rule in
    it instead of two.
    """
    wire = a_master_proof(
        {"block-context": {"m.py@b1": a_correct("m.py@b1")}}
    ).serialize()
    wire["edit_copies"][0]["sheets"][0]["sha"] = None
    proof, why = MasterProof.deserialize("4c", wire)
    assert proof is not None, why
    #: ! ASSERTED ON THE SHEET, NOT ON A DOCKET, since `P55`. The fold is
    #: `Sheet.deserialize`'s and always was -- `_real_pages` merely read the
    #: folded value back out. Asking the parse directly removes a transcription
    #: step from a claim that was never about transcription.
    assert proof.edit_copies[0].sheets[0].sha == ""


#: TRANSCRIPTION, moved: `test_set_by_stops_mapping_everything_to_empty` is
#: `TestDocketOf::test_set_by_names_the_role_whose_copy_was_pulled`, where the
#: copy that produces the docket is the thing being varied.


def test_an_EMPTY_role_is_OMITTED_from_the_wire_and_reads_back_as_empty():
    """An absent `role` and an empty one stay ONE thing rather than two.

    !! IT IS A FORMAT FACT AND IS ASSERTED AS ONE, since `P55`. It used to ride
    on `test_a_page_two_roles_settled_names_NEITHER_of_them`, which built a page
    two roles had settled and checked that `docket_from` named neither. That
    SCENARIO is gone -- an `edit_copy` carries one role for the whole copy, so
    `docket_of` writes that role and never has two to choose between. The
    omission rule survives it, because a `Schedule` can still be built with an
    empty `role` and the wire must not grow a key for it.

    ! WHY THE SCENARIO WENT RATHER THAN BEING PRESERVED. Roy, 2026-09-02: *"by
    the time the copy-chiefs edit-copy becomes the sole edit-copy in the master
    proof the per role piece is lost. If we are pulling from the individual roles
    already then we know the answer."* The fold is where per-role attribution
    ends, not the docket -- so `copy-chief` on a folded page is the true answer
    and not the false one the old test guarded against.
    """
    page = Schedule(path="m.py", sha="0" * 40, alterations=(A_ROW,), role="")
    assert "role" not in page.serialize()
    docket = Docket(schedules=(page,))
    assert set(_set_by(docket).values()) == {""}
    assert read(json.dumps(docket.serialize()))[1] == ""


def test_a_settled_move_DELETES_its_origin_and_writes_its_destination():
    """!! A `move` IS A DELETE AT ONE END AND AN ADD AT THE OTHER
    (`docs/the-mark.md`): *"a move = a delete at the origin + an add at the
    destination"*. Writing `change` at both ends is the duplication the one
    instruction exists to prevent.

    !! ASSERTED ON RECONCILIATION HERE, AND ON TRANSCRIPTION IN
    `TestDocketOf::test_one_move_mark_yields_two_alterations`. What this file
    says is the shape the other test depends on: `settled` carries the move at
    BOTH addresses, and both entries hold the SAME `Mark` -- `_join_moves`
    keying one mark twice so neither end can settle without the other.

    ! WHICH IS WHY ONE COPY ENTRY IS ENOUGH DOWNSTREAM. The mark carries
    `claim.to`, so a transcription reading a single entry can still write both
    ends; it does not need reconciliation's two keys.
    """
    proof = a_master_proof({"block-context": {"m.py@a0": a_move("m.py@a0", "m.py@a8")}})
    settled = reconcile(proof).settled
    assert sorted(one["address"] for one in settled) == ["m.py@a0", "m.py@a8"]
    marks = {id(one["marks"][0].mark) for one in settled}
    assert len(marks) == 1, "both ends must hold one mark, not two"
    assert settled[0]["marks"][0].mark.claim["to"] == "m.py@a8"


def test_a_change_in_the_RETIRED_ARRAY_FORM_never_reaches_the_docket():
    """!! `None` IS THE DELETE SIGNAL, so a `change` that has no text to set
    must not reach it -- `docket/docket.py`'s own header: *"a key whose value
    failed to serialise arrives looking exactly like a deliberate deletion."*
    MEASURED 2026-08-29: `_alteration_text` joined `change if isinstance(change,
    list) else []`, so a raw-text `change` produced `None`, `docket.read`
    accepted it, and the paragraph was EMPTIED.

    !! THE MECHANISM MOVED TWICE AND THE CLAIM HAS NOT. It was
    `UnusableChange`, raised inside the docket step; then `MalformedMark`, from
    `places`; and since `P51` the entry never becomes a `Mark` at all --
    `Sheet.deserialize` sorts it into `refused`, so nothing downstream can build
    an alteration from it. **What this asserts is the outcome rather than
    whichever exception is current**: the bad `change` reaches no docket, and
    the reason is routable back to the role that wrote it.
    """
    mark = a_correct("m.py@b1")
    mark["change"] = [mark["change"]]
    proof = a_master_proof({"block-context": {"m.py@b1": mark}})
    assert _refused_reasons(proof), "the array form must not read as a mark"
    #: ! ASKED OF RECONCILIATION SINCE `P55`. A refused entry never becomes a
    #: `Mark`, so nothing settles and no copy can carry it forward -- which is
    #: the same claim the docket assertion made, one step earlier and with no
    #: transcription in between.
    assert reconcile(proof).settled == []


def test_an_EMPTY_change_refuses_where_the_instruction_may_not_empty():
    mark = a_correct("m.py@b1")
    mark["change"] = ""
    proof = a_master_proof({"block-context": {"m.py@b1": mark}})
    assert _refused_reasons(proof)
    assert reconcile(proof).settled == []


def test_an_EMPTY_change_IS_the_delete_where_the_row_may_empty():
    """`drop` is the one row `INSTRUCTIONS[...].may_empty` is True for, which
    is what the refusal above is read from rather than from a named
    instruction.

    !! THE OTHER HALF IS `TestDocketOf::test_a_drop_is_written_as_a_delete`,
    which asserts the `Alteration(cue, text=None)` this used to. What stays here
    is that the empty change SETTLES rather than being refused -- the pair the
    test above it makes sense against.
    """
    mark = a_drop("m.py@b1")
    mark["change"] = ""
    proof = a_master_proof({"block-context": {"m.py@b1": mark}})
    assert not _refused_reasons(proof)
    assert [one["address"] for one in reconcile(proof).settled] == ["m.py@b1"]


def test_NO_DOCKET_CARRIES_ONE_END_OF_A_MOVE():
    """The design's own sentence, section 3: a `move` settles or escalates
    WHOLE, so **no docket ever carries one end of one**. Half-applied, it is
    invisible downstream -- both dockets read, both set, and `prove_unchanged`
    passes either way because only prose moved."""
    proof = a_master_proof(
        {
            "block-context": {"m.py@a0": a_move("m.py@a0", "m.py@a8")},
            "module-context": {"m.py@a8": a_correct("m.py@a8", "a different sentence")},
        }
    )
    #: ! ASKED OF RECONCILIATION SINCE `P55`. `_join_moves` gives both ends the
    #: STRONGEST outcome either reached, so a collision at the destination pulls
    #: the origin out of `settled` with it. Nothing settles, so no copy carries
    #: the move and no docket can be built holding one end -- the claim is the
    #: same, asked of the step that decides it.
    assert reconcile(proof).settled == []
