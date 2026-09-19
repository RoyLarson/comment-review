"""Which decided places may take a compacted text, and the message that writes one.

`decision-log.md Process: #191`: stage 6 condenses text the fold already
decided, so the compacted text is written onto the place that holds it.
"""

from helpers import (
    BASE,
    TWO,
    a_clean,
    a_correct_setting,
    a_real_binder_over,
    copies_over,
    returned,
)

from comment_review.desk.evaluate.compaction import compacted
from comment_review.desk.evaluate.place import Place
from comment_review.desk.evaluate.state import SETTLED, State
from comment_review.desk.work import events
from comment_review.flows.bus import CompactionsReturned, CopiesReturned, handle

#: The decided text these cases condense, and the condensed text itself. The
#: second is shorter than the first, which is the whole subject of the pass.
DECIDED = "# the count of the items, and the sum\n# of everything the store holds\n"
CONDENSED = "# the count of the items and their sum\n"


def _place(state: State | None, text: str | None, address: str = "m.py@b1") -> Place:
    """One place as a fold left it -- its state and its decided text."""
    return Place(address=address, anchor="x = 1", base=BASE, state=state, text=text)


def _row(address: str, change: str) -> dict:
    """One compaction as stage 6 hands it back."""
    return {"address": address, "change": change}


def test_a_settled_place_takes_the_condensed_text():
    places = {"m.py@b1": _place(State.AGREED, DECIDED)}
    texts, problems = compacted(places, [_row("m.py@b1", CONDENSED)])
    assert (texts, problems) == ({"m.py@b1": CONDENSED}, [])


def test_every_settled_state_takes_one():
    """! BOTH OF THEM, not the one the case above happens to build. A place
    settles as `stands` where one side proposed the text and as `agreed`
    where several proposed it, and stage 6 reads them the same way."""
    for state in SETTLED:
        places = {"m.py@b1": _place(state, DECIDED)}
        texts, problems = compacted(places, [_row("m.py@b1", CONDENSED)])
        assert (texts, problems) == ({"m.py@b1": CONDENSED}, []), state


def test_a_place_standing_on_its_base_is_refused():
    """It settled on no text: every role read it and none proposed one, so
    there is nothing there to condense and the page is not this pass's to
    edit."""
    places = {"m.py@b1": _place(State.STANDS, None)}
    texts, problems = compacted(places, [_row("m.py@b1", CONDENSED)])
    assert texts == {}
    (where, why) = problems[0]
    assert where == "m.py@b1" and "no text" in why


def test_a_place_held_for_the_human_is_refused():
    """An unsettlable place rides to the author with its question, and it
    carries no text at all."""
    places = {"m.py@b1": _place(State.UNSETTLABLE, None)}
    _texts, problems = compacted(places, [_row("m.py@b1", CONDENSED)])
    assert problems and problems[0][0] == "m.py@b1"


def test_a_place_still_carried_forward_is_refused():
    """A carried-forward text has not settled (`Process: #180`), so what
    stage 6 would be condensing is a proposal the roles are still ruling
    on."""
    for state in (State.COMPOSED, State.CONTESTED):
        places = {"m.py@b1": _place(state, DECIDED)}
        _texts, problems = compacted(places, [_row("m.py@b1", CONDENSED)])
        assert problems and str(state) in problems[0][1], state


def test_a_refused_place_is_refused():
    places = {"m.py@b1": _place(State.REFUSED, DECIDED)}
    _texts, problems = compacted(places, [_row("m.py@b1", CONDENSED)])
    assert problems and problems[0][0] == "m.py@b1"


def test_an_address_the_proof_does_not_carry_is_refused():
    places = {"m.py@b1": _place(State.AGREED, DECIDED)}
    _texts, problems = compacted(places, [_row("m.py@b9", CONDENSED)])
    assert problems and problems[0][0] == "m.py@b9"


def test_an_empty_compacted_text_is_refused():
    """Compaction condenses; it does not delete. An empty change at a place
    that decided a text is a deletion nobody ruled on, and stage 6 is told to
    report a paragraph it cannot bring under the cap rather than cut it
    away."""
    places = {"m.py@b1": _place(State.AGREED, DECIDED)}
    texts, problems = compacted(places, [_row("m.py@b1", "")])
    assert texts == {}
    (where, why) = problems[0]
    assert where == "m.py@b1" and "empty" in why


def test_one_refusal_keeps_every_other_text_out():
    """All or nothing, as every fold here is: a compaction that wrote the
    places it could would leave the proof holding some condensed paragraphs
    and some not, with nothing saying which."""
    places = {
        "m.py@b1": _place(State.AGREED, DECIDED),
        "m.py@b2": _place(State.STANDS, None, "m.py@b2"),
    }
    texts, problems = compacted(
        places, [_row("m.py@b1", CONDENSED), _row("m.py@b2", CONDENSED)]
    )
    assert texts == {} and len(problems) == 1


def test_a_row_that_is_not_a_compaction_is_refused_by_its_position():
    """A row with no address has no place to name, so the reason names where
    it sits in the file the pass handed back."""
    places = {"m.py@b1": _place(State.AGREED, DECIDED)}
    _texts, problems = compacted(places, ["not a compaction", {"change": CONDENSED}])
    assert len(problems) == 2
    assert all("compaction" in where for where, _why in problems)


def test_a_row_carrying_no_text_is_refused():
    places = {"m.py@b1": _place(State.AGREED, DECIDED)}
    _texts, problems = compacted(places, [{"address": "m.py@b1"}])
    assert problems and problems[0][0] == "m.py@b1"


def _closed(tmp_path):
    """A closed proof over one corrected place and one left standing."""
    root = tmp_path / "repo"
    binder = a_real_binder_over(root, {"m.py@b1": BASE, "m.py@b2": "# four\n"})
    copies = [
        returned(wire)
        for wire in copies_over(
            binder,
            {
                "block-context": {
                    "m.py@b1": a_correct_setting("m.py@b1", "two", TWO),
                    "m.py@b2": a_clean("m.py@b2"),
                }
            },
        )
    ]
    out, result = handle(CopiesReturned("4c", copies, binder, root, None))
    assert result is not None, out
    return result.proof


def test_the_message_writes_the_condensed_text_onto_the_place(tmp_path):
    proof = _closed(tmp_path)
    out, result = handle(CompactionsReturned(proof, [_row("m.py@b1", CONDENSED)]))
    assert result is not None, out
    by_address = {entry["address"]: entry for entry in result.proof.places}
    assert by_address["m.py@b1"]["text"] == CONDENSED
    assert by_address["m.py@b2"]["text"] is None
    assert [one for one in out if isinstance(one, events.Compacted)] == [
        events.Compacted("m.py@b1", CONDENSED)
    ]


def test_the_message_keeps_everything_else_the_place_holds(tmp_path):
    """Only the text moves: the state, the sides and the marks filed there
    are the record of how that text was decided, and a shorter wording of it
    does not re-decide anything."""
    proof = _closed(tmp_path)
    before = {entry["address"]: entry for entry in proof.places}["m.py@b1"]
    _out, result = handle(CompactionsReturned(proof, [_row("m.py@b1", CONDENSED)]))
    assert result is not None
    after = {entry["address"]: entry for entry in result.proof.places}["m.py@b1"]
    assert {k: v for k, v in after.items() if k != "text"} == {
        k: v for k, v in before.items() if k != "text"
    }


def test_the_message_carries_the_stage_and_the_copies_on(tmp_path):
    proof = _closed(tmp_path)
    _out, result = handle(CompactionsReturned(proof, [_row("m.py@b1", CONDENSED)]))
    assert result is not None
    assert result.proof.stage == proof.stage
    assert result.proof.edit_copies == proof.edit_copies
    assert (result.chief, result.batch) == (None, None)


def test_a_refused_compaction_rolls_the_round_back(tmp_path):
    proof = _closed(tmp_path)
    out, result = handle(CompactionsReturned(proof, [_row("m.py@b2", CONDENSED)]))
    assert result is None
    assert any(isinstance(one, events.RolledBack) for one in out)
    assert any(
        isinstance(one, events.Refused) and one.address == "m.py@b2" for one in out
    )
