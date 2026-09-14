"""The marks table: what each row sets, refuses and pairs as."""

from comment_review.desk.marks.mark import Instruction, Mark
from comment_review.desk.marks.table import INSTRUCTIONS, Stance, Touch


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
    human = _mark(Instruction.QUERY, claim={"shape": str(Shape.HUMAN_REVIEW_NECESSARY)})
    assert INSTRUCTIONS[Instruction.QUERY].pairs(deferring) is Stance.ABSTAINS
    assert INSTRUCTIONS[Instruction.QUERY].pairs(human) is Stance.UNSETTLABLE


def test_every_row_names_the_answers_a_turn_may_give_on_it():
    for instruction, row in INSTRUCTIONS.items():
        if row.pairs(_mark(instruction)) is Stance.PROPOSES:
            assert set(row.answers) == {"hold", "withdraw", "correct", "patch"}, (
                instruction
            )


def test_add_rereads_and_only_add_rereads():
    """Ruling R4 (decision-log.md Process #116 and #121): an add is carried
    forward for every role that read its page."""
    for instruction, row in INSTRUCTIONS.items():
        assert row.rereads == (instruction is Instruction.ADD), instruction
