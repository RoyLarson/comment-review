"""The marks table: what each row sets, refuses and pairs as."""

from typing import Any, ClassVar

import pytest
from helpers import a_real_binder_over, a_typed_mark, returned, seed

from comment_review.desk.marks.table import INSTRUCTIONS, Stance
from comment_review.desk.proof.mark import (
    Amendment,
    Instruction,
    Mark,
    Touch,
    mark_type,
    read_mark,
)
from comment_review.flows.verify import admit


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
        " gathered page is its full address, as `addresses find` prints it, and"
        " one outside the code is not carried yet (`decision-log.md Process: #173`):"
        " file a `human-review-necessary` query here naming it instead",
    ]

    binder = a_real_binder_over(tmp_path, {"m.py@b1": BASE})
    wire = seed(binder, "block-context")
    wire["sheets"][0]["marks"][0].update(
        {**entry, "claim": {"from": "m.py@b1", "to": "m.py@b9"}}
    )
    problems = admit([returned(wire)], tmp_path, binder=binder).problems
    assert [p.message for p in problems if "resolves" in p.message] == [
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
