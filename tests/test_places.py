"""Build places from reviewer copies and fold their decisions."""

from helpers import (
    a_binder_over,
    a_clean,
    a_correct,
    a_correct_setting,
    a_move,
    a_real_binder_over,
    a_typed_ruling,
    an_add,
    copies_over,
    returned,
    seed,
)

from comment_review.desk import report as events
from comment_review.desk.evaluate.move import _is_this_move, moves_in
from comment_review.desk.marks.table import Row
from comment_review.desk.proof.mark import (
    Touch,
)
from comment_review.desk.proof.state import State
from comment_review.desk.work.fold import Fold
from comment_review.flows.fill import composition_problems, fill, row_problems
from comment_review.flows.on_the_page import Held
from comment_review.flows.places import bases_and_anchors, places_of
from comment_review.flows.transcribe import _touched_by_page
from comment_review.flows.verify import resolution_problems
from comment_review.reading.diagnostics import ReadFailure

BASE = "# one\n# two\n# three\n"


def _binder_bases(binder) -> dict[str, str]:
    """The binder's paragraph at each address it carries.

    These binders are built over no real page, so the text they seeded is the
    only base there is; the flow reads the page (`decision-log.md Process:
    #187`), which is `tests/test_bus.py`'s subject rather than this file's.
    """
    return {b.address: b.raw_text for b in binder.paragraphs if b.address}


def test_a_move_is_filed_at_its_origin_and_at_its_destination():
    binder = a_binder_over({"m.py@b1": BASE, "m.py@b5": BASE})
    wire = copies_over(
        binder, {"block-context": {"m.py@b1": a_move("m.py@b1", "m.py@b5")}}
    )
    copies = [returned(w) for w in wire]
    places = places_of(copies, _binder_bases(binder), {})
    assert set(places) == {"m.py@b1", "m.py@b5"}
    assert [f.touch for f in places["m.py@b1"].filed] == [Touch.ORIGIN]
    assert [f.touch for f in places["m.py@b5"].filed] == [Touch.DESTINATION]


def test_a_clean_and_a_correct_on_one_address_land_as_two_filed_on_one_place():
    binder = a_binder_over({"m.py@b1": BASE})
    wire = copies_over(
        binder,
        {
            "block-context": {"m.py@b1": a_clean("m.py@b1")},
            "function-context": {"m.py@b1": a_correct("m.py@b1")},
        },
    )
    copies = [returned(w) for w in wire]
    places = places_of(copies, _binder_bases(binder), {})
    assert set(places) == {"m.py@b1"}
    place = places["m.py@b1"]
    assert {f.role for f in place.filed} == {"block-context", "function-context"}
    assert all(f.touch is Touch.OWN for f in place.filed)


def test_readers_are_every_role_whose_copy_holds_a_sheet_for_the_page():
    binder = a_binder_over({"m.py@b1": BASE, "m.py@b5": BASE})
    wire = copies_over(
        binder,
        {
            "block-context": {"m.py@b1": a_clean("m.py@b1")},
            "function-context": {},
        },
    )
    copies = [returned(w) for w in wire]
    places = places_of(copies, _binder_bases(binder), {})
    assert places["m.py@b1"].readers == ("block-context", "function-context")


def _folded_with_anchors(anchors: dict[str, str], order: list[str]) -> Fold:
    """Two roles' differing corrects at `m.py@b1`, each carrying `anchors[role]`,
    handed to the places in `order` and folded."""
    binder = a_binder_over({"m.py@b1": BASE})
    marks = {
        "block-context": a_correct_setting("m.py@b1", "two", "# one\n# 2\n# three\n"),
        "function-context": a_correct_setting("m.py@b1", "three", "# one\n# 3\n"),
    }
    wire = copies_over(
        binder,
        {role: {"m.py@b1": {**marks[role], "anchor": anchors[role]}} for role in order},
    )
    copies = [returned(w) for w in wire]
    held = bases_and_anchors(copies, lambda address: Held(BASE, "x = 1"))
    assert not isinstance(held, ReadFailure), held
    bases, anchors_held = held
    return Fold(places_of(copies, bases, anchors_held)).run()


ROLES = ["block-context", "function-context"]


def test_differing_anchors_at_one_place_are_refused_by_role_and_address():
    anchors = {"block-context": "x = 1", "function-context": "y = 2"}
    for order in (ROLES, ROLES[::-1]):
        fold = _folded_with_anchors(anchors, order)
        assert not fold.committed
        refused = [one for one in fold.events if isinstance(one, events.Refused)]
        assert [(one.role, one.address) for one in refused] == [
            ("block-context", "m.py@b1"),
            ("function-context", "m.py@b1"),
        ]
        for one in refused:
            assert "'x = 1'" in one.reasons[0] and "'y = 2'" in one.reasons[0]


def test_identical_anchors_with_differing_edits_still_fold():
    anchors = {"block-context": "x = 1", "function-context": "x = 1"}
    for order in (ROLES, ROLES[::-1]):
        fold = _folded_with_anchors(anchors, order)
        assert fold.committed, fold.events
        assert fold.decided["m.py@b1"].anchor == "x = 1"


def _ruled(anchor: str, **ruling) -> dict:
    """Two roles' adds at an empty place whose marks carry `anchor`, contested,
    then ruled by the chief: the places, ready to fold again."""
    binder = a_binder_over({"m.py@b1": ""})
    wire = copies_over(
        binder,
        {
            role: {
                "m.py@b1": {**an_add("m.py@b1", text), "change": text, "anchor": anchor}
            }
            for role, text in (("block-context", "# a"), ("function-context", "# b"))
        },
    )
    places = places_of(
        [returned(w) for w in wire], {"m.py@b1": ""}, {"m.py@b1": anchor}
    )
    first = Fold(places).run()
    assert first.committed, first.events
    assert places["m.py@b1"].state is State.CONTESTED
    places["m.py@b1"].disposition = a_typed_ruling(address="m.py@b1", **ruling)
    return places


def test_a_recast_commits_without_synthesizing_an_add_mark():
    fold = Fold(_ruled("", name="recast", prose="# c\n", reason="neither")).run()
    assert fold.committed, fold.events
    place = fold.decided["m.py@b1"]
    assert place.text == "# c\n"
    assert place.disposition is not None
    assert place.disposition.reason == "neither"


def test_every_reader_of_where_a_mark_writes_asks_the_row(monkeypatch, tmp_path):
    """The row is the one definition of which places a mark writes at.

    With `Row.places` sending a move's destination somewhere its claim does
    not name, every flow that walks a mark's places follows the row: a reader
    that still decided the places for itself would land at `m.py@b5`.
    """
    binder = a_binder_over({"m.py@b1": BASE, "m.py@b5": BASE, "m.py@b7": BASE})
    wire = copies_over(
        binder, {"block-context": {"m.py@b1": a_move("m.py@b1", "m.py@b5")}}
    )
    copies = [returned(w) for w in wire]
    mark = copies[0].sheets[0].marks[0]
    elsewhere = (("m.py@b1", Touch.ORIGIN), ("m.py@b7", Touch.DESTINATION))
    monkeypatch.setattr(Row, "places", lambda self, mark: elsewhere)

    result = bases_and_anchors(copies, lambda address: Held(BASE, "x = 1"))
    from comment_review.reading.diagnostics import ReadFailure

    assert not isinstance(result, ReadFailure)
    bases, _anchors = result
    assert set(bases) == {"m.py@b1", "m.py@b7"}
    places = places_of(copies, _binder_bases(binder), {})
    assert set(places) == {"m.py@b1", "m.py@b7"}

    asked: list[str] = []
    row_problems(mark, lambda address: asked.append(address) or BASE)
    assert asked == ["m.py@b1", "m.py@b7"]
    asked.clear()
    composition_problems("r", [mark, mark], lambda a: asked.append(a) or BASE)
    assert asked == ["m.py@b1", "m.py@b7"]
    assert _touched_by_page(copies[0]) == {"m.py": ["m.py@b1", "m.py@b7"]}

    resolved: list[str] = []
    monkeypatch.setattr(
        "comment_review.flows.verify._unresolved",
        lambda address, *_: resolved.append(address) or "",
    )
    assert resolution_problems(copies[0], [], tmp_path, {}) == []
    assert resolved == ["m.py@b1", "m.py@b7"]

    # `fill` refuses a composition only at the places the row says this mark
    # writes, so a refusal at the destination the claim names is not its.
    monkeypatch.setattr(
        "comment_review.flows.fill.composition_problems",
        lambda role, marks, base_at: [("m.py@b5", "at b5"), ("m.py@b7", "at b7")],
    )
    real = a_real_binder_over(
        tmp_path / "repo", {"m.py@b1": BASE, "m.py@b5": BASE, "m.py@b7": "# seven\n"}
    )
    entry = a_move("m.py@b1", "m.py@b5", change="# two", reads="# seven\n# two")
    placed, why = fill(seed(real, "block-context"), entry, tmp_path / "repo")
    assert placed is None
    assert why == ["m.py@b7: at b7"]

    # The move aggregate is keyed by the destination the row names, and knows
    # the filing as that move; a reader of the claim would key it at b5.
    moves = moves_in(places)
    assert set(moves) == {"m.py@b1 -> m.py@b7"}
    assert _is_this_move(places["m.py@b1"].filed[0], moves["m.py@b1 -> m.py@b7"])
