"""The marks table: what each row sets, refuses and pairs as."""

from comment_review.desk.evaluate.place import Filed, Place
from comment_review.desk.marks.mark import Instruction, Mark
from comment_review.desk.marks.table import INSTRUCTIONS, Row, Stance, Touch, chief_mark


def _mark(instruction: Instruction, **fields) -> Mark:
    base = {
        "address": "m.py@b1",
        "anchor": "x = 1",
        "raw_text": "# one\n# two\n# three\n",
        "instruction": instruction,
        "claim": {},
        "reason": "a reason",
        "sources": (),
        "change": "",
    }
    base.update(fields)
    return Mark(**base)


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
        Instruction.ADD, claim=mark.claim, change="# why\n", raw_text="# why\n# one\n"
    )
    assert row.reads(dropping, Touch.OWN, BASE) == ["the text does not keep 'two'"]


def test_stances():
    from comment_review.desk.marks.mark import Shape

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
    from comment_review.desk.marks.mark import Shape

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


def test_every_row_names_the_answers_a_turn_may_give_on_it():
    for instruction, row in INSTRUCTIONS.items():
        if row.pairs(_mark(instruction)) is Stance.PROPOSES:
            assert set(row.answers) == {"hold", "withdraw", "correct", "patch"}, (
                instruction
            )


def test_owes_destination_is_derived_from_touches_not_set_beside_it():
    """A row cannot state `owes_destination` and `touches` in disagreement --
    `__post_init__` derives the first from the second every time, so passing
    a literal for it is overwritten rather than kept."""
    assert Row(touches=(Touch.ORIGIN, Touch.DESTINATION)).owes_destination is True
    assert Row().owes_destination is False
    assert Row(touches=(Touch.OWN,), owes_destination=True).owes_destination is False


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
    assert got.instruction is Instruction.CORRECT
    assert got.claim == {"false": BASE, "true": "# different\n"}
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
    assert got.change == composed
    assert got.raw_text == BASE
    # The filed marks' evidence, deduped: what the chief read to decide the
    # text, and what the parse demands of the row it synthesized.
    assert got.sources == cited
    again, why = Mark.deserialize(got.address, got.serialize())
    assert why == [] and again == got


def test_chief_mark_synthesizes_an_add_over_an_empty_base():
    place = Place(address="m.py@b1", anchor="x = 1", base="", filed=[], text="# new\n")
    got = chief_mark(place)
    assert got.instruction is Instruction.ADD
    assert got.claim == {"missing": "# new", "anchor": "`x = 1`"}
    assert got.change == "# new\n"
    # Process #176: an add's `raw_text` is the paragraph as it will read, and
    # its row sets that text at the place. The base is empty here, so the two
    # are the same text.
    assert got.raw_text == "# new\n"
    assert INSTRUCTIONS[got.instruction].sets(got, Touch.OWN, place.base) == place.text


def test_chief_mark_synthesizes_a_drop_when_the_decided_text_is_empty():
    place = Place(address="m.py@b1", anchor="x = 1", base=BASE, filed=[], text="")
    got = chief_mark(place)
    assert got.instruction is Instruction.DROP
    assert got.claim == {"drop": BASE}
    assert got.change == ""
    assert got.raw_text == BASE
