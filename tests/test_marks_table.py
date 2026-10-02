"""The marks table: what each row sets, refuses and pairs as."""

from typing import Any, ClassVar

import pytest
from helpers import a_real_binder_over, a_typed_mark, returned, seed

from comment_review.desk.marks.table import INSTRUCTIONS, Stance, chief_mark
from comment_review.desk.proof.mark import (
    AddMark,
    Amendment,
    CorrectMark,
    DropMark,
    Instruction,
    Mark,
    Touch,
    mark_type,
    read_mark,
)
from comment_review.desk.proof.place import Filed, Place
from comment_review.flows.verify import resolution_problems


def _mark(instruction: Instruction, **fields) -> Mark:
    base: dict[str, Any] = {"raw_text": "# one\n# two\n# three\n", "reason": "a reason"}
    base.update(fields)
    return a_typed_mark(instruction, **base)


BASE = "# one\n# two\n# three\n"


def test_the_rows_that_carry_their_own_raw_text_are_add_and_move():
    """Process #175 and #176: for these two the role writes the paragraph as
    it will read; for every other row `raw_text` is the seeded paragraph."""
    carried = {name for name, row in INSTRUCTIONS.items() if row.carries_raw_text}
    assert carried == {Instruction.ADD, Instruction.MOVE}


def test_a_clean_and_a_query_set_nothing_anywhere():
    for instruction in (Instruction.CLEAN, Instruction.QUERY):
        row = INSTRUCTIONS[instruction]
        assert row.touches == (Touch.OWN,)
        assert row.sets(_mark(instruction), Touch.OWN, BASE) is None


def test_a_correct_sets_its_derived_change():
    row = INSTRUCTIONS[Instruction.CORRECT]
    mark = _mark(Instruction.CORRECT, change="# one\n# 2\n# three\n")
    assert row.sets(mark, Touch.OWN, BASE) == "# one\n# 2\n# three\n"


def test_a_drop_of_the_whole_paragraph_sets_a_delete():
    row = INSTRUCTIONS[Instruction.DROP]
    assert row.sets(_mark(Instruction.DROP, change=""), Touch.OWN, BASE) == ""


def test_a_move_sets_the_remainder_at_the_origin_and_raw_text_at_the_destination():
    """Process #172 and #175: change is the snippet, raw_text the destination
    paragraph as it will read."""
    row = INSTRUCTIONS[Instruction.MOVE]
    mark = _mark(
        Instruction.MOVE,
        claim={"from": "m.py@b1", "to": "m.py@b5"},
        change="# two\n",
        raw_text="# four\n# two\n# five\n",
    )
    assert row.touches == (Touch.ORIGIN, Touch.DESTINATION)
    assert row.sets(mark, Touch.ORIGIN, BASE) == "# one\n# three\n"
    assert (
        row.sets(mark, Touch.DESTINATION, "# four\n# five\n")
        == "# four\n# two\n# five\n"
    )


def test_a_move_whose_snippet_is_not_in_the_origin_once_is_refused_by_reads():
    row = INSTRUCTIONS[Instruction.MOVE]
    mark = _mark(
        Instruction.MOVE, claim={"from": "m.py@b1", "to": "m.py@b5"}, change="# six\n"
    )
    assert row.reads(mark, Touch.ORIGIN, BASE) == [
        "the snippet is not in the origin's paragraph: '# six\\n'"
    ]


def test_a_moves_destination_text_must_keep_every_word_of_the_snippet_and_the_base():
    row = INSTRUCTIONS[Instruction.MOVE]
    mark = _mark(
        Instruction.MOVE,
        claim={"from": "m.py@b1", "to": "m.py@b5"},
        change="# two\n",
        raw_text="# four\n# five\n",
    )
    assert row.reads(mark, Touch.DESTINATION, "# four\n# five\n") == [
        "the destination text does not keep 'two'"
    ]


def test_an_add_sets_its_raw_text_and_keeps_the_prose_already_there():
    """Process #176 and #132."""
    row = INSTRUCTIONS[Instruction.ADD]
    mark = _mark(
        Instruction.ADD,
        claim={"missing": "why", "anchor": "`x`"},
        change="# why\n",
        raw_text="# one\n# why\n# two\n# three\n",
    )
    assert row.sets(mark, Touch.OWN, BASE) == mark.raw_text
    assert row.reads(mark, Touch.OWN, BASE) == []
    dropping = _mark(
        Instruction.ADD,
        claim={"missing": "why", "anchor": "`x`"},
        change="# why\n",
        raw_text="# why\n# one\n",
    )
    assert row.reads(dropping, Touch.OWN, BASE) == ["the text does not keep 'two'"]


def test_stances():
    from comment_review.desk.proof.mark import Shape

    assert (
        INSTRUCTIONS[Instruction.CLEAN].pairs(_mark(Instruction.CLEAN))
        is Stance.ABSTAINS
    )
    assert (
        INSTRUCTIONS[Instruction.CORRECT].pairs(_mark(Instruction.CORRECT))
        is Stance.PROPOSES
    )
    deferring = _mark(Instruction.QUERY, claim={"shape": str(Shape.OUTSIDE_MY_ROLE)})
    unable = _mark(Instruction.QUERY, claim={"shape": str(Shape.UNABLE_TO_DETERMINE)})
    human = _mark(Instruction.QUERY, claim={"shape": str(Shape.HUMAN_REVIEW_NECESSARY)})
    assert INSTRUCTIONS[Instruction.QUERY].pairs(deferring) is Stance.DEFERS
    assert INSTRUCTIONS[Instruction.QUERY].pairs(unable) is Stance.DEFERS
    assert INSTRUCTIONS[Instruction.QUERY].pairs(human) is Stance.UNSETTLABLE


def test_only_a_deferring_query_defers():
    """`decision-log.md Process: #121` and `#180`: a role that defers is not
    waited on, and a `clean` is -- so no other row may take that stance."""
    from comment_review.desk.proof.mark import Shape

    deferring = [
        instruction
        for instruction, row in INSTRUCTIONS.items()
        if row.pairs(_mark(instruction, claim={"shape": str(Shape.OUTSIDE_MY_ROLE)}))
        is Stance.DEFERS
    ]
    assert deferring == [Instruction.QUERY]
    assert (
        INSTRUCTIONS[Instruction.CLEAN].pairs(_mark(Instruction.CLEAN))
        is Stance.ABSTAINS
    )


def test_a_destination_touch_is_on_exactly_the_rows_whose_type_names_one():
    """`places` writes at the destination a row's touches name, and the type's
    read checks a destination only where its type names one -- so the two
    disagreeing would write a destination nothing checks, or check one
    nothing writes."""
    for instruction, row in INSTRUCTIONS.items():
        kind = mark_type(instruction)
        assert (Touch.DESTINATION in row.touches) is kind.owes_destination, instruction
        assert bool(kind.names_destination) is kind.owes_destination, instruction


def test_owes_destination_is_derived_from_the_destination_key():
    """A type states its destination key, never `owes_destination` beside it."""

    class Elsewhere(Amendment):
        claim_all: ClassVar[tuple[str, ...]] = ("from", "there")
        names_destination: ClassVar[str] = "there"

    class Nowhere(Amendment):
        owes_destination: ClassVar[bool] = True

    assert Elsewhere.owes_destination is True
    assert Nowhere.owes_destination is False


def test_a_type_naming_a_key_its_claim_does_not_carry_is_refused():
    with pytest.raises(TypeError, match="`to`, which its claim keys do not carry"):

        class Stray(Amendment):
            claim_all: ClassVar[tuple[str, ...]] = ("from",)
            names_destination: ClassVar[str] = "to"


def test_a_move_writes_at_its_origin_and_at_its_destination():
    """The destination is the claim key the type names -- `to`."""
    assert mark_type(Instruction.MOVE).names_destination == "to"
    mark = _mark(Instruction.MOVE, claim={"from": "m.py@b1", "to": "m.py@b5"})
    assert INSTRUCTIONS[Instruction.MOVE].places(mark) == (
        ("m.py@b1", Touch.ORIGIN),
        ("m.py@b5", Touch.DESTINATION),
    )


def test_a_refusal_about_the_destination_names_the_types_own_key(tmp_path):
    """The read's two destination refusals and resolution's spell the key the
    type names, as `derived_change` spells `quotes_original`."""
    entry = {
        "address": "m.py@b1",
        "instruction": "move",
        "claim": {"from": "m.py@b1", "to": "m.py@b1"},
        "reason": "a reason",
        "sources": [{"cite": "m.py:1", "verbatim": "x = 1"}],
        "change": "# two",
        "raw_text": BASE,
    }
    _, onto_itself = read_mark("w", entry)
    _, not_a_place = read_mark("w", {**entry, "claim": {"from": "m.py@b1", "to": "b9"}})
    assert [*onto_itself, *not_a_place] == [
        "w: `claim.to` is this mark's own `address` -- a move to where the"
        " paragraph already is deletes it and writes nothing back",
        "w: `claim.to` 'b9' is not a `path@cue` place -- a destination on a"
        " gathered page is its full address, as the addresser prints it, and one"
        " outside the code is not carried yet (`decision-log.md Process: #173`):"
        " file a `human-review-necessary` query here naming it instead",
    ]

    binder = a_real_binder_over(tmp_path, {"m.py@b1": BASE})
    wire = seed(binder, "block-context")
    wire["sheets"][0]["marks"][0].update(
        {**entry, "claim": {"from": "m.py@b1", "to": "m.py@b9"}}
    )
    problems = resolution_problems(returned(wire), ["m.py"], tmp_path, {})
    assert [p.message for p in problems] == [
        "`claim.to` 'm.py@b9' resolves against no page -- m.py carries no place 'b9'"
    ]


def test_every_other_row_writes_at_its_own_address_alone():
    for instruction, row in INSTRUCTIONS.items():
        if instruction is Instruction.MOVE:
            continue
        assert row.places(_mark(instruction)) == (("m.py@b1", Touch.OWN),), instruction


def test_a_mark_with_no_address_writes_nowhere():
    """`clean` is the one row a mark may carry no address for."""
    mark = _mark(Instruction.CLEAN, address="")
    assert INSTRUCTIONS[Instruction.CLEAN].places(mark) == ()


def test_chief_mark_returns_the_filed_mark_that_set_the_decided_text():
    """Ruling R5: the side taken in is returned as-is, not resynthesized."""
    mark = _mark(
        Instruction.CORRECT,
        claim={"false": "two", "true": "2"},
        change="# one\n# 2\n# three\n",
    )
    place = Place(
        address="m.py@b1",
        anchor="x = 1",
        base=BASE,
        filed=[Filed("a", mark, Touch.OWN)],
        text="# one\n# 2\n# three\n",
    )
    assert chief_mark(place) is mark


def test_chief_mark_synthesizes_a_correct_when_no_filed_mark_set_the_text():
    mark = _mark(
        Instruction.CORRECT,
        claim={"false": "two", "true": "2"},
        change="# one\n# 2\n# three\n",
    )
    place = Place(
        address="m.py@b1",
        anchor="x = 1",
        base=BASE,
        filed=[Filed("a", mark, Touch.OWN)],
        text="# different\n",
    )
    got = chief_mark(place)
    assert isinstance(got, CorrectMark)
    assert got.serialize()["claim"] == {"false": BASE, "true": "# different\n"}
    assert got.change == "# different\n"
    assert got.raw_text == BASE


def test_chief_mark_synthesizes_over_a_side_composed_from_two_marks():
    """`decision-log.md Process: #179`: where a role's two marks composed into
    its side, no filed mark set the decided text by itself, so there is no
    side to take in and the chief's own mark carries the composition."""
    cited = ({"cite": "m.py:1", "verbatim": "x = 1"},)
    correct = _mark(
        Instruction.CORRECT,
        claim={"false": "two", "true": "2"},
        change="# one\n# 2\n# three\n",
        sources=cited,
    )
    moved = _mark(
        Instruction.MOVE,
        address="m.py@b5",
        claim={"from": "m.py@b5", "to": "m.py@b1"},
        change="# five\n",
        raw_text="# five\n" + BASE,
        sources=cited,
    )
    composed = "# five\n# one\n# 2\n# three\n"
    place = Place(
        address="m.py@b1",
        anchor="x = 1",
        base=BASE,
        filed=[Filed("a", correct, Touch.OWN), Filed("a", moved, Touch.DESTINATION)],
        text=composed,
    )
    assert all(
        INSTRUCTIONS[one.mark.instruction].sets(one.mark, one.touch, place.base)
        != composed
        for one in place.filed
    )
    got = chief_mark(place)
    assert isinstance(got, CorrectMark)
    assert got.change == composed
    assert got.raw_text == BASE
    # The filed marks' evidence, deduped: what the chief read to decide the
    # text, and what the parse demands of the row it synthesized.
    assert got.sources == cited
    again, why = read_mark(got.address, got.serialize())
    assert why == [] and again == got


def test_chief_mark_synthesizes_an_add_over_an_empty_base():
    place = Place(address="m.py@b1", anchor="x = 1", base="", filed=[], text="# new\n")
    got = chief_mark(place)
    assert isinstance(got, AddMark)
    assert got.serialize()["claim"] == {"missing": "# new", "anchor": "`x = 1`"}
    assert got.change == "# new\n"
    # Process #176: an add's `raw_text` is the paragraph as it will read, and
    # its row sets that text at the place. The base is empty here, so the two
    # are the same text.
    assert got.raw_text == "# new\n"
    assert INSTRUCTIONS[got.instruction].sets(got, Touch.OWN, place.base) == place.text


def test_chief_mark_synthesizes_a_drop_when_the_decided_text_is_empty():
    place = Place(address="m.py@b1", anchor="x = 1", base=BASE, filed=[], text="")
    got = chief_mark(place)
    assert isinstance(got, DropMark)
    assert got.serialize()["claim"] == {"drop": BASE}
    assert got.change == ""
    assert got.raw_text == BASE


def test_chief_mark_does_not_turn_on_the_order_the_copies_were_handed_over():
    """The same place, built from the same two copies dispatched two ways.

    !! `places_of` APPENDS IN THE ORDER THE COPIES CAME, which is the order a
    command's `--edit-copy` flags happened to be typed in. Both of this
    function's answers used to ride on that: which of two marks setting one
    text is returned, and the order the sources stand in on a synthesized
    mark. It reads the filed marks in role order instead, so one hand of
    copies gives one mark however it was dealt.

    ! IT IS `tests/test_collate.py::TestTheChiefsCopy::
    test_sources_and_reason_AGREE_on_the_roles_ORDER` ASKED OF THE NEW PATH.
    That case measured the old fold's composed mark against "the order
    `edit_copies` happened to be handed in, which is not a property of the
    data"; it went with the fold, and this is the claim it was making.
    """
    zebra = _mark(
        Instruction.CORRECT,
        claim={"false": "two", "true": "2"},
        change="# one\n# 2\n# three\n",
        sources=({"cite": "zebra.py:1", "verbatim": "x = 1"},),
    )
    apple = _mark(
        Instruction.CORRECT,
        claim={"false": "three", "true": "3"},
        change="# one\n# two\n# 3\n",
        sources=({"cite": "apple.py:1", "verbatim": "y = 2"},),
    )
    composed = "# one\n# 2\n# 3\n"

    def at(filed: list) -> Mark:
        return chief_mark(
            Place(
                address="m.py@b1",
                anchor="x = 1",
                base=BASE,
                filed=filed,
                text=composed,
            )
        )

    dealt = [
        Filed("zebra-context", zebra, Touch.OWN),
        Filed("apple-context", apple, Touch.OWN),
    ]
    assert at(dealt) == at(list(reversed(dealt)))
    # `Mark.sources` is `tuple[object, ...]` deliberately -- a source that is
    # not an object is carried so `source_problems` can refuse it by name -- so
    # a test reading `cite` off one says it is reading a well-formed source.
    cites = []
    for source in at(dealt).sources:
        assert isinstance(source, dict), source
        # Declared, not narrowed -- `ty` loses an isinstance narrow at the
        # subscript, the same reason `EditCopy.deserialize` gives.
        held: dict = source
        cites.append(held["cite"])
    assert cites == ["apple.py:1", "zebra.py:1"]


def test_chief_mark_takes_in_the_first_side_by_role_where_two_set_one_text():
    """The other half: two roles whose marks both set the decided text. The
    one returned is the first by role, not the first dealt."""
    text = "# one\n# 2\n# three\n"
    fields = {"claim": {"false": "two", "true": "2"}, "change": text}
    zebra = _mark(Instruction.CORRECT, reason="zebra's", **fields)
    apple = _mark(Instruction.CORRECT, reason="apple's", **fields)
    dealt = [
        Filed("zebra-context", zebra, Touch.OWN),
        Filed("apple-context", apple, Touch.OWN),
    ]

    def at(filed: list) -> Mark:
        return chief_mark(
            Place(address="m.py@b1", anchor="x = 1", base=BASE, filed=filed, text=text)
        )

    assert at(dealt).reason == "apple's"
    assert at(list(reversed(dealt))).reason == "apple's"


def test_a_mark_writing_two_places_is_never_the_chiefs_mark_whole():
    """Before P3 the chief rules a move's ends one at a time, so each end is
    written from its own decided text -- a move taken whole at one end would
    land at an end the chief may have recast."""
    move = a_typed_mark(
        Instruction.MOVE,
        address="m.py@b1",
        anchor="x = 1",
        raw_text="# four\n# two\n# five\n",
        claim={"from": "m.py@b1", "to": "m.py@b5"},
        reason="r",
        sources=({"cite": "m.py:1", "verbatim": "v0 = 0"},),
        change="# two\n",
    )
    place = Place(
        address="m.py@b1",
        anchor="x = 1",
        base="# one\n# two\n# three\n",
        filed=[Filed("a", move, Touch.ORIGIN)],
        text="# one\n# three\n",
    )
    got = chief_mark(place)
    assert isinstance(got, Amendment) and got.instruction is not Instruction.MOVE
    assert got.change == "# one\n# three\n"
