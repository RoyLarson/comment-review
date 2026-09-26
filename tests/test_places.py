"""places_of derives places from the roles' copies; chief_copy_of derives the
copy chief's own copy from what the fold decided at each place."""

from helpers import a_binder_over, a_clean, a_correct, a_move, copies_over, returned

from comment_review.desk.containers import Sheet
from comment_review.desk.evaluate.place import Place
from comment_review.desk.marks.mark import Instruction
from comment_review.desk.marks.table import INSTRUCTIONS, Touch
from comment_review.flows.places import chief_copy_of, places_of

BASE = "# one\n# two\n# three\n"


def _binder_bases(binder) -> dict[str, str]:
    """The binder's paragraph at each address it carries.

    These binders are built over no real page, so the text they seeded is the
    only base there is; the flow reads the page (`decision-log.md Process:
    #187`), which is `tests/test_bus.py`'s subject rather than this file's.
    """
    return {b.address: b.raw_text for b in binder.paragraphs if b.address}


def test_a_move_yields_two_places_that_partner_each_other():
    binder = a_binder_over({"m.py@b1": BASE, "m.py@b5": BASE})
    wire = copies_over(
        binder, {"block-context": {"m.py@b1": a_move("m.py@b1", "m.py@b5")}}
    )
    copies = [returned(w) for w in wire]
    places = places_of(copies, _binder_bases(binder), {})
    assert set(places) == {"m.py@b1", "m.py@b5"}
    assert places["m.py@b1"].partner == "m.py@b5"
    assert places["m.py@b5"].partner == "m.py@b1"
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


def test_a_taken_in_move_writes_one_mark_at_its_origin_and_none_at_its_destination():
    binder = a_binder_over({"one.py@b1": BASE, "two.py@b1": "# four\n# five\n"})
    move = a_move("one.py@b1", "two.py@b1")
    move["change"] = "# two\n"
    wire = copies_over(binder, {"block-context": {"one.py@b1": move}})
    copies = [returned(w) for w in wire]
    places = places_of(copies, _binder_bases(binder), {})

    origin, destination = places["one.py@b1"], places["two.py@b1"]
    move_mark = origin.filed[0].mark
    row = INSTRUCTIONS[Instruction.MOVE]
    origin.text = row.sets(move_mark, Touch.ORIGIN, origin.base)
    destination.text = row.sets(move_mark, Touch.DESTINATION, destination.base)

    sheets = [
        Sheet(path="one.py", sha="0" * 40, marks=()),
        Sheet(path="two.py", sha="0" * 40, marks=()),
    ]
    copy = chief_copy_of(places, "copy-chief", {"root": ".", "revise": 0}, sheets)

    by_path = {sheet.path: sheet.marks for sheet in copy.sheets}
    assert len(by_path.get("one.py", ())) == 1
    assert "two.py" not in by_path


def test_chief_copy_of_synthesizes_a_correct_for_a_decided_place():
    place = Place(address="m.py@b1", anchor="x = 1", base=BASE, text="# x\n")
    sheets = [Sheet(path="m.py", sha="0" * 40, marks=())]
    copy = chief_copy_of(
        {"m.py@b1": place}, "copy-chief", {"root": ".", "revise": 0}, sheets
    )
    marks = [m for sheet in copy.sheets for m in sheet.marks]
    assert len(marks) == 1
    assert marks[0].instruction is Instruction.CORRECT
    assert marks[0].change == "# x\n"
    assert marks[0].claim["false"] == BASE


def test_chief_copy_of_writes_no_mark_for_a_place_whose_text_is_none():
    place = Place(address="m.py@b1", anchor="x = 1", base=BASE, text=None)
    sheets = [Sheet(path="m.py", sha="0" * 40, marks=())]
    copy = chief_copy_of(
        {"m.py@b1": place}, "copy-chief", {"root": ".", "revise": 0}, sheets
    )
    assert copy.sheets == ()


def test_chief_copy_of_synthesizes_a_drop_for_an_empty_decided_text():
    place = Place(address="m.py@b1", anchor="x = 1", base=BASE, text="")
    sheets = [Sheet(path="m.py", sha="0" * 40, marks=())]
    copy = chief_copy_of(
        {"m.py@b1": place}, "copy-chief", {"root": ".", "revise": 0}, sheets
    )
    marks = [m for sheet in copy.sheets for m in sheet.marks]
    assert len(marks) == 1
    assert marks[0].instruction is Instruction.DROP
    assert marks[0].change == ""
