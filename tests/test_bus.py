"""The bus: one message in, the fold's events and what the stage saves out."""

from dataclasses import replace

import pytest
from helpers import (
    a_clean,
    a_correct,
    a_correct_citing,
    a_correct_setting,
    a_move,
    a_patch,
    a_query,
    a_real_binder_over,
    an_add,
    copies_over,
    returned,
)

from comment_review.desk.answers.answer import Question
from comment_review.desk.containers import Sheet
from comment_review.desk.evaluate.place import Place
from comment_review.desk.evaluate.state import State
from comment_review.desk.marks.mark import Mark, Shape
from comment_review.desk.stages import Dispatch, Kind, Role, Stage
from comment_review.desk.work import events
from comment_review.flows.bus import (
    AnswersReturned,
    CopiesReturned,
    DispositionsWritten,
    handle,
    turn_of,
)
from comment_review.flows.human import HumanAnswer
from comment_review.flows.transcribe import CannotTranscribe, docket_of_proof

BASE = "# one\n# two\n# three"
OTHER = "# four\n# five\n# six"
CORRECTED = "# one\n# TWO\n# three"


def _message(tmp_path, by_role):
    root = tmp_path / "repo"
    binder = a_real_binder_over(root, {"m.py@b1": BASE, "m.py@b2": OTHER})
    copies = [returned(wire) for wire in copies_over(binder, by_role)]
    return CopiesReturned("4c", copies, binder, root, None)


TWO_ROLES = {
    "block-context": {
        "m.py@b1": a_correct_setting("m.py@b1", "two", CORRECTED),
        "m.py@b2": a_clean("m.py@b2"),
    },
    "function-context": {
        "m.py@b1": a_clean("m.py@b1"),
        "m.py@b2": a_clean("m.py@b2"),
    },
}


def test_a_committed_fold_says_what_it_settled_and_what_it_carries(tmp_path):
    """`decision-log.md Process: #180`: the place the other role read but has
    not seen a text for is carried to it; the place they both cleaned settles
    on the paragraph as it stands."""
    out, result = handle(_message(tmp_path, TWO_ROLES))
    assert events.Settled("m.py@b2", None) in out
    assert (
        events.CarriedForward(
            "m.py@b1", State.COMPOSED, Question.COMPOSITION, ("function-context",)
        )
        in out
    )
    assert events.Committed(2) in out
    assert result is not None


def test_a_committed_fold_carries_its_places_on_the_proof(tmp_path):
    _out, result = handle(_message(tmp_path, TWO_ROLES))
    assert result is not None
    assert len(result.proof.places) == 2
    for entry in result.proof.places:
        place, why = Place.deserialize("a place", entry)
        assert place is not None, why
        assert place.serialize() == entry


def test_the_proof_holds_the_composed_places_text_the_chief_copy_does_not(tmp_path):
    """`m.py@b1` is `composed`, not settled -- block-context proposes
    `CORRECTED` and function-context, having only cleaned it, is still owed a
    say (`decision-log.md Process: #184`) -- so the chief's copy carries no
    mark there; its text is the closed proof's.

    SUPERSEDES `test_the_chief_copy_holds_one_mark_at_the_settled_place`,
    which asserted this composed place's mark on the chief's copy -- true
    before T10 filtered `chief_copy_of` to `SETTLED` places, and this
    place's own state was never one of them."""
    _out, result = handle(_message(tmp_path, TWO_ROLES))
    assert result is not None
    assert result.chief is not None
    marks = [mark for sheet in result.chief.sheets for mark in sheet.marks]
    assert marks == []
    place = next(p for p in result.proof.places if p["address"] == "m.py@b1")
    assert place["state"] == "composed"
    assert place["text"] == CORRECTED


COMPOSE_ROLES = {
    "block-context": {
        "m.py@b1": a_correct_setting("m.py@b1", "one", "# ONE\n# two\n# three"),
        "m.py@b2": a_clean("m.py@b2"),
    },
    "function-context": {
        "m.py@b1": a_correct_setting("m.py@b1", "three", "# one\n# two\n# THREE"),
        "m.py@b2": a_clean("m.py@b2"),
    },
}
COMPOSED = "# ONE\n# two\n# THREE"


def test_a_composed_place_carries_no_mark_on_the_chief_copy(tmp_path):
    """`decision-log.md Process: #184`: a composed place's working text is the
    closed proof's, not the chief's copy's -- the two roles here correct
    different sentences of the same paragraph, compose to one text, and are
    both still owed a say on it, so the place is `composed` rather than
    settled."""
    out, result = handle(_message(tmp_path, COMPOSE_ROLES))
    assert result is not None
    assert (
        events.CarriedForward(
            "m.py@b1",
            State.COMPOSED,
            Question.COMPOSITION,
            ("block-context", "function-context"),
        )
        in out
    )
    assert result.chief is not None
    marks = [mark for sheet in result.chief.sheets for mark in sheet.marks]
    assert [mark.address for mark in marks] == []
    place = next(p for p in result.proof.places if p["address"] == "m.py@b1")
    assert place["state"] == "composed"
    assert place["text"] == COMPOSED


def test_a_copy_from_another_tree_rolls_the_fold_back(tmp_path):
    """`decision-log.md Process: #178`: copies gathered from different trees
    share no address space, so there is no fold between them."""
    message = _message(
        tmp_path,
        {
            "block-context": {
                "m.py@b1": a_correct_setting("m.py@b1", "two", CORRECTED),
                "m.py@b2": a_clean("m.py@b2"),
            },
            "function-context": {
                "m.py@b1": a_clean("m.py@b1"),
                "m.py@b2": a_clean("m.py@b2"),
            },
        },
    )
    odd = message.copies[1]
    message.copies[1] = replace(odd, read_from={"root": "somewhere/else", "revise": 0})
    out, result = handle(message)
    assert result is None
    refused = [one for one in out if isinstance(one, events.Refused)]
    assert [one.role for one in refused] == ["function-context"]
    assert refused[0].address == ""
    assert "somewhere/else" in refused[0].reasons[0]
    assert any(isinstance(one, events.RolledBack) for one in out)
    assert not any(isinstance(one, events.Settled) for one in out)


#: A stage dealt the `b` places over a cap of two lines, admitting the edit
#: instructions -- `decision-log.md Process: #193`. Its dispatch is the one
#: role these cases return a copy for.
COMPACTING = Stage(
    name="6",
    kind=Kind.EDITORIAL,
    reads="revise:4",
    dispatches=(Dispatch(Role.BLOCK_CONTEXT, ()),),
    cap=2,
    series=("b",),
    admits=("patch", "drop", "add", "clean"),
)


def _dealt(tmp_path, by_role, admits=("patch", "drop", "add", "clean"), stage="6"):
    """One copy of a compacting stage, as a role hand-edits it before returning.

    The copy is seeded for real and its `admits` is then written over, which
    is the whole subject: a role that widens or clears its own copy's field
    has changed the only thing `mark` and `check` read.
    """
    message = _message(tmp_path, by_role)
    message.copies[0] = replace(message.copies[0], stage=stage, admits=admits)
    # `_replace` rather than `dataclasses.replace`: a message is a NamedTuple.
    return message._replace(topology=COMPACTING)


#: One role's marks over a page of two places, one of them an instruction the
#: compacting stage does not admit.
A_CORRECT = {
    "block-context": {
        "m.py@b1": a_correct_setting("m.py@b1", "two", CORRECTED),
        "m.py@b2": a_clean("m.py@b2"),
    }
}


def test_a_copy_that_widened_its_own_admits_is_refused_at_the_fold(tmp_path):
    """`decision-log.md Process: #193`. What a stage admits is the topology's
    row, and a copy is not where it is decided: a role that added `correct`
    to its own copy's `admits` passes `mark` and `check`, which read that
    field, and is refused here -- twice, once for the field and once for the
    mark it let through."""
    out, result = handle(_dealt(tmp_path, A_CORRECT, admits=("patch", "correct")))
    assert result is None
    refused = [one for one in out if isinstance(one, events.Refused)]
    assert [one.address for one in refused] == ["", "m.py@b1"]
    assert all(one.role == "block-context" for one in refused)
    assert "correct" in refused[0].reasons[0] and "6" in refused[0].reasons[0]
    assert "and not correct" in refused[1].reasons[0]
    assert any(isinstance(one, events.RolledBack) for one in out)


def test_a_copy_that_cleared_its_own_admits_is_refused_at_the_fold(tmp_path):
    """An empty `admits` reads as *every instruction* wherever it is asked, so
    clearing the field is how a copy escapes the rule. The row is what it is
    held to."""
    out, result = handle(_dealt(tmp_path, A_CORRECT, admits=()))
    assert result is None
    refused = [one for one in out if isinstance(one, events.Refused)]
    assert [one.address for one in refused] == ["", "m.py@b1"]


def test_a_copy_that_agrees_with_the_row_folds(tmp_path):
    """The control: the same hand, with the marks the row admits, commits --
    so what the two cases above refuse is the instruction and the field, not
    the stage."""
    hand = {
        "block-context": {
            "m.py@b1": a_patch("m.py@b1", "two", "2", "# one\n# 2\n# three"),
            "m.py@b2": a_clean("m.py@b2"),
        }
    }
    out, result = handle(_dealt(tmp_path, hand))
    assert result is not None, [one for one in out if isinstance(one, events.Refused)]


def test_without_a_topology_the_copys_own_admits_still_binds(tmp_path):
    """`collate` is never weaker than `check`: without a row there is nothing
    else to hold a mark to, and the copy's own field is what `check` would
    have used."""
    message = _message(tmp_path, A_CORRECT)
    message.copies[0] = replace(
        message.copies[0], stage="6", admits=("patch", "drop", "add", "clean")
    )
    out, result = handle(message)
    assert result is None
    refused = [one for one in out if isinstance(one, events.Refused)]
    assert [one.address for one in refused] == ["m.py@b1"]
    assert "and not correct" in refused[0].reasons[0]


def test_an_ordinary_stage_admits_every_instruction(tmp_path):
    """A copy carrying no `admits`, under a row carrying none, is every stage
    that ran before the ruling."""
    ordinary = COMPACTING._replace(
        cap=0, series=(), admits=(), name="4", reads="original"
    )
    message = _message(tmp_path, A_CORRECT)._replace(topology=ordinary)
    _out, result = handle(message)
    assert result is not None


def test_a_correct_that_drops_an_unnamed_word_is_advised_and_the_fold_commits(tmp_path):
    """`decision-log.md Process: #177`, through the handler."""
    out, result = handle(
        _message(
            tmp_path,
            {
                "block-context": {
                    "m.py@b1": a_correct_setting("m.py@b1", "two", "# one\n# TWO"),
                    "m.py@b2": a_clean("m.py@b2"),
                }
            },
        )
    )
    assert result is not None
    advised = [one for one in out if isinstance(one, events.Advised)]
    assert [(one.role, one.address) for one in advised] == [
        ("block-context", "m.py@b1")
    ]
    assert advised[0].notes == (
        "its change drops 'three', which its claim never names",
    )
    assert events.Settled("m.py@b1", "# one\n# TWO") in out


def test_a_cite_that_resolves_against_nothing_rolls_the_fold_back(tmp_path):
    out, result = handle(
        _message(
            tmp_path,
            {
                "block-context": {
                    "m.py@b1": a_correct_citing("m.py@b1", "nowhere.py:1"),
                    "m.py@b2": a_clean("m.py@b2"),
                }
            },
        )
    )
    assert result is None
    refused = [one for one in out if isinstance(one, events.Refused)]
    assert refused
    assert refused[0].role == "block-context"
    assert refused[0].address == "m.py@b1"
    assert any(isinstance(one, events.RolledBack) for one in out)


# -- the turn and the chief's rulings, over what a committed collate left -------

DOS = "# one\n# dos\n# three"
DROPPING = "# one\n# TWO"
RECAST = "# one\n# both ways\n# three"
PLACE = "m.py@b1"

#: Two roles correcting one sentence two ways, a third reading the page and
#: marking it clean: the fold contests the place and asks the two sides.
TWO_SIDES = {
    "block-context": {
        PLACE: a_correct_setting(PLACE, "two", CORRECTED),
        "m.py@b2": a_clean("m.py@b2"),
    },
    "function-context": {
        PLACE: a_correct_setting(PLACE, "two", DOS),
        "m.py@b2": a_clean("m.py@b2"),
    },
    "module-context": {
        PLACE: a_clean(PLACE),
        "m.py@b2": a_clean("m.py@b2"),
    },
}

#: The two sides alone, with no third role reading the page: what the two
#: settle between them settles, since nobody else is owed a say (`#180`).
JUST_THE_TWO = {
    role: marks for role, marks in TWO_SIDES.items() if role != "module-context"
}


def _collated(tmp_path, by_role=None):
    """What a committed `CopiesReturned` left, which a turn reads."""
    out, result = handle(_message(tmp_path, by_role or TWO_SIDES))
    assert result is not None, out
    return result


def _answer(address, instruction, reason, **fields):
    """One role's answer entry, as a role writes one: no `question` on it."""
    return {"address": address, "instruction": instruction, "reason": reason, **fields}


def _both_hold(address=PLACE):
    return {
        "block-context": [_answer(address, "hold", "mine reads correctly")],
        "function-context": [_answer(address, "hold", "so does mine")],
    }


def _state_at(proof, address):
    """The state the proof records for one place."""
    for entry in proof.places:
        if entry["address"] == address:
            return entry["state"]
    raise AssertionError(f"{address} is not on the proof")


def _answers_at(proof, address):
    """The turns the proof records answers at, for one place."""
    for entry in proof.places:
        if entry["address"] == address:
            return entry["answers"]
    raise AssertionError(f"{address} is not on the proof")


def _changes_on(copy):
    return [mark.change for sheet in copy.sheets for mark in sheet.marks]


def _refusals(out):
    return [
        (one.role, one.address, reason)
        for one in out
        if isinstance(one, events.Refused)
        for reason in one.reasons
    ]


def _held_and_withdrawn():
    return {
        "block-context": [_answer(PLACE, "hold", "mine reads correctly")],
        "function-context": [_answer(PLACE, "withdraw", "theirs is better")],
    }


def test_a_hold_and_a_withdraw_leave_one_side_and_it_goes_to_the_role_that_cleaned(
    tmp_path,
):
    """`decision-log.md Process: #180`: the role that withdrew has had its
    say; the role that was clean at the first fold has seen no text, and the
    one side left is put to it."""
    collated = _collated(tmp_path)
    out, result = handle(
        AnswersReturned(collated.proof, _held_and_withdrawn(), tmp_path / "repo")
    )
    assert result is not None, out
    assert _state_at(result.proof, PLACE) == "composed"
    assert result.batch is not None
    assert sorted(result.batch) == ["module-context"]
    assert result.batch["module-context"][0]["raw_text"] == CORRECTED


def test_a_hold_and_a_withdraw_settle_the_place_where_nobody_else_read_it(tmp_path):
    collated = _collated(tmp_path, JUST_THE_TWO)
    out, result = handle(
        AnswersReturned(collated.proof, _held_and_withdrawn(), tmp_path / "repo")
    )
    assert result is not None, out
    assert events.Settled(PLACE, CORRECTED) in out
    assert _state_at(result.proof, PLACE) == "stands"
    assert result.batch is None


def test_a_recast_at_a_still_contested_place_puts_the_chiefs_prose_on_its_copy(
    tmp_path,
):
    collated = _collated(tmp_path)
    out, held = handle(AnswersReturned(collated.proof, _both_hold(), tmp_path / "repo"))
    assert held is not None, out
    assert _state_at(held.proof, PLACE) == "contested"
    out, closed = handle(
        DispositionsWritten(
            held.proof,
            [
                {
                    "address": PLACE,
                    "answer": "recast",
                    "prose": RECAST,
                    "reason": "neither side says what the code does",
                }
            ],
        )
    )
    assert closed is not None, out
    assert closed.chief is not None
    assert _changes_on(closed.chief) == [RECAST]
    assert _state_at(closed.proof, PLACE) == "stands"


#: block-context moves b1's middle line to b2, which reads with it at the end;
#: function-context corrects b2, contesting the destination's words, and is
#: owed a say on the move's placement.
A_CONTESTED_MOVE = {
    "block-context": {
        PLACE: a_move(PLACE, "m.py@b2", change="# two\n", reads=OTHER + "# two\n"),
        "m.py@b2": a_clean("m.py@b2"),
    },
    "function-context": {
        PLACE: a_clean(PLACE),
        "m.py@b2": a_correct_setting("m.py@b2", "five", "# four\n# 5\n# six"),
    },
}
#: The origin's paragraph with the moved line taken out of it.
REMAINDER = "# one\n# three"
MOVED_TO = OTHER + "# two\n"
CHIEFS_OWN = OTHER + "# two, as the chief words it\n"


def _ruling(address, name, **fields):
    return {"address": address, "answer": name, "reason": "the chief's", **fields}


def _stetted(tmp_path):
    """`A_CONTESTED_MOVE` after one turn: function-context stets the move's
    placement and takes the origin's remainder, and both roles hold at the
    destination. The move is contested, so the chief rules its two ends."""
    collated = _collated(tmp_path, A_CONTESTED_MOVE)
    answers = {
        role: [
            _answer(
                slot["address"],
                {"placement": "stet", "composition": "clean"}.get(
                    slot["question"], "hold"
                ),
                "r",
                **({"to": slot["to"]} if "to" in slot else {}),
            )
            for slot in slots
        ]
        for role, slots in collated.batch.items()
    }
    out, turned = handle(AnswersReturned(collated.proof, answers, tmp_path / "repo"))
    assert turned is not None, out
    assert [m["placement"] for m in turned.proof.moves] == ["contested"]
    return turned


def test_an_undecided_moves_ends_are_to_come_and_ask_nothing(tmp_path):
    """A move's placement is settled before the marks around it, so neither
    end of an undecided move is asked about its words: the one question put
    to the roles is the placement."""
    collated = _collated(tmp_path, A_CONTESTED_MOVE)
    assert _state_at(collated.proof, PLACE) == "to-come"
    assert _state_at(collated.proof, "m.py@b2") == "to-come"
    assert collated.batch is not None
    slots = [slot for slots in collated.batch.values() for slot in slots]
    assert {slot["question"] for slot in slots} == {"placement"}


#: block-context moves b1's middle line to b2; function-context corrects b1's
#: last line, which reads differently with the move taken out.
A_MOVE_BESIDE_A_CORRECTION = {
    "block-context": {
        PLACE: a_move(PLACE, "m.py@b2", change="# two\n", reads=OTHER + "# two\n"),
        "m.py@b2": a_clean("m.py@b2"),
    },
    "function-context": {
        PLACE: a_correct_setting(PLACE, "three", "# one\n# two\n# 3"),
        "m.py@b2": a_clean("m.py@b2"),
    },
}


def _turn(result, root, answer_for):
    """One turn: every slot the batch holds answered by `answer_for(role, slot)`."""
    assert result.batch is not None
    answers = {
        role: [
            _answer(
                slot["address"],
                answer_for(role, slot),
                "r",
                **({"to": slot["to"]} if "to" in slot else {}),
            )
            for slot in slots
        ]
        for role, slots in result.batch.items()
    }
    out, turned = handle(AnswersReturned(result.proof, answers, root))
    assert turned is not None, out
    return turned


def test_a_withdrawn_moves_origin_is_put_to_the_role_that_has_not_seen_it(tmp_path):
    """While the move is open its origin asks nothing, so no role accepts a
    text the move's outcome may change. Once the mover withdraws, the origin
    holds the correction alone, and the mover has never been shown it: the
    place is carried to that role, not settled on an answer to another text."""
    root = tmp_path / "repo"
    collated = _collated(tmp_path, A_MOVE_BESIDE_A_CORRECTION)
    words = {"composition": "clean", "escalation": "hold"}
    stetted = _turn(
        collated,
        root,
        lambda role, slot: words.get(slot["question"], "stet"),
    )
    withdrawn = _turn(
        stetted,
        root,
        lambda role, slot: words.get(
            slot["question"], "withdraw" if role == "block-context" else "stet"
        ),
    )
    assert [m["placement"] for m in withdrawn.proof.moves] == ["withdrawn"]
    assert _state_at(withdrawn.proof, PLACE) == "composed"
    (origin,) = [p for p in withdrawn.proof.places if p["address"] == PLACE]
    assert origin["owed"] == ["block-context"]


def test_the_chief_rules_a_moves_placement_then_its_ends(tmp_path):
    """The chief rules an undecided move once, for the pair; the move splits,
    and an end that then needs words is carried back to the chief, who rules
    it on the proof the placement ruling wrote. The snippet lands once."""
    turned = _stetted(tmp_path)
    out, placed = handle(
        DispositionsWritten(
            turned.proof,
            [_ruling(PLACE, "taken_in", to="m.py@b2", side="block-context")],
        )
    )
    assert placed is not None, out
    assert [m["placement"] for m in placed.proof.moves] == ["agreed"]
    carried = sorted(
        one.address for one in out if isinstance(one, events.CarriedForward)
    )
    # Both ends now hold the split's halves, which function-context has not
    # seen, so each is carried back to the chief for its words.
    assert carried == [PLACE, "m.py@b2"]
    out, closed = handle(
        DispositionsWritten(
            placed.proof,
            [
                _ruling(PLACE, "taken_in", side="block-context"),
                _ruling("m.py@b2", "recast", prose=CHIEFS_OWN),
            ],
        )
    )
    assert closed is not None, out
    assert events.Settled(PLACE, REMAINDER) in out
    assert events.Settled("m.py@b2", CHIEFS_OWN) in out
    texts = [p["text"] for p in closed.proof.places]
    assert sum(text.count("# two") for text in texts if text) == 1


def test_a_ruling_at_an_end_of_an_undecided_move_is_refused(tmp_path):
    """An end's words are ruled against its move's outcome, so a ruling at an
    end whose move is still undecided has nothing to close."""
    turned = _stetted(tmp_path)
    out, closed = handle(
        DispositionsWritten(
            turned.proof,
            [
                _ruling(PLACE, "taken_in", to="m.py@b2", side="block-context"),
                _ruling("m.py@b2", "taken_in", side="block-context"),
            ],
        )
    )
    assert closed is None
    assert (
        "copy-chief",
        "m.py@b2",
        "an end of an undecided move -- rule the move's placement,"
        " and this end's words once it is split",
    ) in _refusals(out)


def test_an_undecided_move_with_no_placement_ruling_is_refused_by_name(tmp_path):
    turned = _stetted(tmp_path)
    out, closed = handle(DispositionsWritten(turned.proof, []))
    assert closed is None
    assert (
        "copy-chief",
        f"{PLACE} -> m.py@b2",
        "the placement of this move is contested and not ruled on",
    ) in _refusals(out)


def test_a_placement_ruling_of_original_keeps_the_paragraph_where_it_is(tmp_path):
    turned = _stetted(tmp_path)
    out, placed = handle(
        DispositionsWritten(
            turned.proof,
            [_ruling(PLACE, "taken_in", to="m.py@b2", side="original")],
        )
    )
    assert placed is not None, out
    assert [m["placement"] for m in placed.proof.moves] == ["withdrawn"]


def test_an_answer_at_a_place_no_turn_carried_is_refused(tmp_path):
    collated = _collated(tmp_path)
    answers = _both_hold()
    answers["block-context"].append(_answer("m.py@b2", "hold", "and this one"))
    out, result = handle(AnswersReturned(collated.proof, answers, tmp_path / "repo"))
    assert result is None
    assert ("block-context", "m.py@b2", "not carried forward") in _refusals(out)


def test_an_answer_from_a_role_the_place_was_not_put_to_is_refused(tmp_path):
    collated = _collated(tmp_path)
    answers = _both_hold()
    answers["module-context"] = [_answer(PLACE, "hold", "reading over their shoulder")]
    out, result = handle(AnswersReturned(collated.proof, answers, tmp_path / "repo"))
    assert result is None
    refused = [one for one in _refusals(out) if one[0] == "module-context"]
    assert [(role, address) for role, address, _why in refused] == [
        ("module-context", PLACE)
    ]
    assert "not put to" in refused[0][2]


def test_a_role_that_was_asked_and_answered_nothing_is_refused(tmp_path):
    collated = _collated(tmp_path)
    out, result = handle(
        AnswersReturned(
            collated.proof,
            {"block-context": [_answer(PLACE, "hold", "mine reads correctly")]},
            tmp_path / "repo",
        )
    )
    assert result is None
    assert ("function-context", PLACE, "unanswered") in _refusals(out)


def test_an_answer_whose_cite_does_not_resolve_is_refused(tmp_path):
    """`decision-log.md Process: #181`: an answer's evidence is verified as a
    mark's is, before the fold, so a turn never folds over a citation that
    resolves against nothing."""
    collated = _collated(tmp_path)
    answers = _both_hold()
    answers["block-context"] = [
        _answer(
            PLACE,
            "correct",
            "the line I read says so",
            change=CORRECTED,
            sources=[{"cite": "nowhere.py:1", "verbatim": "x = 1"}],
        )
    ]
    out, result = handle(AnswersReturned(collated.proof, answers, tmp_path / "repo"))
    assert result is None
    refused = [one for one in _refusals(out) if one[0] == "block-context"]
    assert [(role, address) for role, address, _why in refused] == [
        ("block-context", PLACE)
    ]
    assert "does not resolve" in refused[0][2]


def test_an_answer_whose_cite_resolves_is_taken(tmp_path):
    collated = _collated(tmp_path)
    answers = _both_hold()
    answers["block-context"] = [
        _answer(
            PLACE,
            "correct",
            "the line I read says so",
            change=CORRECTED,
            sources=[{"cite": "m.py:2", "verbatim": "# one"}],
        )
    ]
    out, result = handle(AnswersReturned(collated.proof, answers, tmp_path / "repo"))
    assert result is not None, out


def test_a_role_this_turn_asked_nothing_of_is_refused_by_name(tmp_path):
    collated = _collated(tmp_path)
    answers = _both_hold()
    answers["module-context"] = []
    out, result = handle(AnswersReturned(collated.proof, answers, tmp_path / "repo"))
    assert result is None
    assert ("module-context", "", "no slots were sent to this role") in _refusals(out)


def test_a_second_turn_reads_the_first_turns_answers_and_its_own(tmp_path):
    collated = _collated(tmp_path, JUST_THE_TWO)
    _out, held = handle(
        AnswersReturned(collated.proof, _both_hold(), tmp_path / "repo")
    )
    assert held is not None
    out, result = handle(
        AnswersReturned(
            held.proof,
            {
                "block-context": [_answer(PLACE, "withdraw", "theirs reads better")],
                "function-context": [_answer(PLACE, "hold", "mine stands")],
            },
            tmp_path / "repo",
        )
    )
    assert result is not None, out
    assert events.Settled(PLACE, DOS) in out
    assert sorted(_answers_at(result.proof, PLACE)) == ["1", "2"]


def test_a_disposition_at_a_place_the_answers_settled_is_refused(tmp_path):
    collated = _collated(tmp_path, JUST_THE_TWO)
    _out, settled = handle(
        AnswersReturned(collated.proof, _held_and_withdrawn(), tmp_path / "repo")
    )
    assert settled is not None
    out, result = handle(
        DispositionsWritten(
            settled.proof,
            [
                {
                    "address": PLACE,
                    "answer": "taken_in",
                    "side": "block-context",
                    "reason": "ruling on a place the roles closed",
                }
            ],
        )
    )
    assert result is None
    assert ("copy-chief", PLACE, "not carried forward") in _refusals(out)


def test_a_human_question_answered_at_a_place_rolls_the_turn_back(tmp_path):
    """`decision-log.md Process: #197`: a human-review query is asked before
    the fold, whether a role raises it on its first reading or in a turn. The
    turn rolls back naming the role, the place and the question."""
    collated = _collated(
        tmp_path,
        {
            "block-context": {
                PLACE: a_correct_setting(PLACE, "one", "# ONE\n# two\n# three"),
                "m.py@b2": a_clean("m.py@b2"),
            },
            "function-context": {
                PLACE: a_correct_setting(PLACE, "three", "# one\n# two\n# THREE"),
                "m.py@b2": a_clean("m.py@b2"),
            },
        },
    )
    assert _state_at(collated.proof, PLACE) == "composed"
    out, result = handle(
        AnswersReturned(
            collated.proof,
            {
                "block-context": [
                    _answer(
                        PLACE,
                        "query",
                        "which of the two the author meant is theirs to say",
                        claim={
                            "shape": "human-review-necessary",
                            "attempted": "read both texts against the code",
                            "settles": "human",
                        },
                    )
                ],
                "function-context": [
                    _answer(PLACE, "clean", "the two read as one paragraph")
                ],
            },
            tmp_path / "repo",
        )
    )
    assert result is None
    assert [e for e in out if isinstance(e, events.AsksTheHuman)] == [
        events.AsksTheHuman(
            "block-context",
            PLACE,
            "which of the two the author meant is theirs to say",
        )
    ]
    assert out[-1] == events.RolledBack(1)


def test_an_advisory_note_is_reported_again_after_a_turn(tmp_path):
    """`decision-log.md Process: #177`: a note is a fact about a mark, so a
    fold that re-derives the place from its record derives the note with it."""
    collated = _collated(
        tmp_path,
        {
            "block-context": {
                PLACE: a_correct_setting(PLACE, "two", DROPPING),
                "m.py@b2": a_clean("m.py@b2"),
            },
            "function-context": {
                PLACE: a_correct_setting(PLACE, "two", DOS),
                "m.py@b2": a_clean("m.py@b2"),
            },
        },
    )
    out, result = handle(
        AnswersReturned(collated.proof, _both_hold(), tmp_path / "repo")
    )
    assert result is not None, out
    advised = [one for one in out if isinstance(one, events.Advised)]
    assert [(one.role, one.address) for one in advised] == [("block-context", PLACE)]
    assert advised[0].notes == (
        "its change drops 'three', which its claim never names",
    )


# -- the fold's base is the page's text (`decision-log.md Process: #187`) ------

#: The paragraph at `n.py@b1`, a file the run did not gather: the binder holds
#: no row for it, so the page is the only thing that knows what is there.
UNGATHERED = "# seven\n# eight"


def _ungathered_page(tmp_path, text=UNGATHERED):
    """`n.py`, written beside the binder's pages and not gathered.

    Laid out the way `a_real_binder_over` lays a page, so its one comment is
    at `b1` and sits above `v1 = 1`.
    """
    root = tmp_path / "repo"
    root.mkdir(parents=True, exist_ok=True)
    (root / "n.py").write_text(
        f"v0 = 0\n{text}\nv1 = 1\n", encoding="utf-8", newline="\n"
    )


def _moved_into_n(tmp_path, reads):
    """block-context moves b1's middle line into `n.py@b1`, reading `reads`."""
    message = _message(
        tmp_path,
        {
            "block-context": {
                PLACE: a_move(PLACE, "n.py@b1", change="# two\n", reads=reads),
                "m.py@b2": a_clean("m.py@b2"),
            }
        },
    )
    _ungathered_page(tmp_path)
    return message


def test_a_move_into_an_ungathered_file_that_drops_a_word_is_refused(tmp_path):
    """The destination text is measured against the page's paragraph there,
    not against the empty string a binder without that file would give."""
    out, result = handle(_moved_into_n(tmp_path, "# seven\n# two\n"))
    assert result is None
    assert (
        "block-context",
        "n.py@b1",
        "the text does not keep 'eight'",
    ) in _refusals(out)
    assert any(isinstance(one, events.RolledBack) for one in out)


def test_a_move_into_an_ungathered_file_that_keeps_every_word_folds(tmp_path):
    """The control: the same move, keeping the paragraph already there. The
    destination carries the page's anchor, which no mark there supplies."""
    out, result = handle(_moved_into_n(tmp_path, "# seven\n# eight\n# two"))
    assert result is not None, _refusals(out)
    place = next(one for one in result.proof.places if one["address"] == "n.py@b1")
    assert place["base"] == UNGATHERED
    assert place["anchor"] == "v1 = 1"


def test_an_add_over_prose_in_an_ungathered_file_that_drops_a_word_is_refused(
    tmp_path,
):
    """An `add` at a place the binder does not hold, on a sheet the copy
    carries for that page, is held to the prose the page has there."""
    message = _message(
        tmp_path,
        {
            "block-context": {
                PLACE: a_clean(PLACE),
                "m.py@b2": a_clean("m.py@b2"),
            }
        },
    )
    _ungathered_page(tmp_path)
    add = {
        **Mark.seed("n.py@b1", "v1 = 1", ""),
        **an_add("n.py@b1", reads="# seven\n# a new line"),
        "change": "# a new line",
    }
    copy = message.copies[0]
    sheet, why = Sheet.deserialize("n.py", {"path": "n.py", "sha": "", "marks": [add]})
    assert sheet is not None, why
    message.copies[0] = replace(copy, sheets=(*copy.sheets, sheet))
    out, result = handle(message)
    assert result is None
    assert (
        "block-context",
        "n.py@b1",
        "the text does not keep 'eight'",
    ) in _refusals(out)


def test_a_move_and_an_add_into_one_ungathered_place_compose_on_different_sentences(
    tmp_path,
):
    """Each role's text keeps the paragraph there and adds a different line,
    so the two compose against the page's paragraph. Measured against
    nothing, every line of each would be new and the two would contest."""
    message = _message(
        tmp_path,
        {
            "block-context": {
                PLACE: a_move(
                    PLACE, "n.py@b1", change="# two\n", reads="# two\n" + UNGATHERED
                ),
                "m.py@b2": a_clean("m.py@b2"),
            },
            "function-context": {
                PLACE: a_clean(PLACE),
                "m.py@b2": a_clean("m.py@b2"),
            },
        },
    )
    _ungathered_page(tmp_path)
    add = {
        **Mark.seed("n.py@b1", "v1 = 1", ""),
        **an_add("n.py@b1", reads=UNGATHERED + "\n# six"),
        "change": "# six",
    }
    sheet, why = Sheet.deserialize("n.py", {"path": "n.py", "sha": "", "marks": [add]})
    assert sheet is not None, why
    copy = message.copies[1]
    message.copies[1] = replace(copy, sheets=(*copy.sheets, sheet))
    out, result = handle(message)
    assert result is not None, _refusals(out)
    assert _state_at(result.proof, "n.py@b1") != "contested"


def test_a_move_into_a_file_this_checkout_does_not_hold_is_refused_by_name(
    tmp_path,
):
    """A page a mark touches that cannot be read is refused before the fold
    opens, naming the page, in the one wording every reader of a page uses."""
    message = _message(
        tmp_path,
        {
            "block-context": {
                PLACE: a_move(PLACE, "gone.py@b1", change="# two\n", reads="# two"),
                "m.py@b2": a_clean("m.py@b2"),
            }
        },
    )
    out, result = handle(message)
    assert result is None
    reasons = [reason for _role, address, reason in _refusals(out) if address == PLACE]
    assert any("no page can be read at gone.py" in reason for reason in reasons), (
        reasons
    )


# -- a move's placement, asked once for its pair (`Process: #195`) ------------

MOVED_FROM = "# one\n# two\n# three"
ARRIVAL = "# four\n# two\n# five\n# six"


def _a_move_two_roles_read(tmp_path):
    root = tmp_path / "repo"
    binder = a_real_binder_over(root, {"m.py@b1": MOVED_FROM, "m.py@b2": OTHER})
    by_role = {
        "block-context": {
            "m.py@b1": a_move("m.py@b1", "m.py@b2", change="# two\n", reads=ARRIVAL),
            "m.py@b2": a_clean("m.py@b2"),
        },
        "module-context": {
            "m.py@b1": a_clean("m.py@b1"),
            "m.py@b2": a_clean("m.py@b2"),
        },
    }
    copies = [returned(wire) for wire in copies_over(binder, by_role)]
    return CopiesReturned("4c", copies, binder, root, None), root


def _answering(batch_slots, answer_for):
    out = []
    for slot in batch_slots:
        name = answer_for(slot)
        out.append({**slot, "instruction": name, "reason": "r"})
    return out


def _slots_of(result):
    """A committed result's batch, which these cases expect to hold slots."""
    assert result is not None and result.batch is not None
    return result.batch


def _answered(result, answer_for):
    """Every slot of `result`'s batch, answered by `answer_for`."""
    return {
        role: _answering(slots, answer_for) for role, slots in _slots_of(result).items()
    }


def _placement_or_clean(placement):
    """An answer-for that answers each placement `placement` and the rest `clean`."""
    return lambda s: placement if s["question"] == "placement" else "clean"


class TestAMovesPlacementIsAskedOnce:
    """`decision-log.md Process: #195`, board P1."""

    def test_the_other_reader_is_sent_one_placement_slot(self, tmp_path):
        message, _root = _a_move_two_roles_read(tmp_path)
        _out, result = handle(message)
        assert result is not None
        batch = _slots_of(result)
        slots = [s for s in batch["module-context"] if s["question"] == "placement"]
        assert [(s["address"], s["to"]) for s in slots] == [("m.py@b1", "m.py@b2")]
        assert slots[0]["raw_text"] == ARRIVAL and slots[0]["snippet"] == "# two\n"
        assert "block-context" not in batch or not [
            s for s in batch["block-context"] if s["question"] == "placement"
        ]
        assert [m["placement"] for m in result.proof.moves] == ["open"]

    def test_agree_and_clean_land_the_paragraph_once(self, tmp_path):
        """The placement is agreed first; the split's two halves are then put
        to the reader that has not seen them, and its `clean` settles both."""
        message, root = _a_move_two_roles_read(tmp_path)
        _out, first = handle(message)
        assert first is not None
        answers = _answered(first, _placement_or_clean("agree"))
        out, agreed = handle(AnswersReturned(first.proof, answers, root))
        assert agreed is not None, out
        assert [m["placement"] for m in agreed.proof.moves] == ["agreed"]
        answers = _answered(agreed, _placement_or_clean("agree"))
        out, result = handle(AnswersReturned(agreed.proof, answers, root))
        assert result is not None, out
        assert result.chief is not None
        texts = {p["address"]: p["text"] for p in result.proof.places}
        assert texts["m.py@b1"] == "# one\n# three"
        assert texts["m.py@b2"] == ARRIVAL
        chief = [
            (m.instruction, m.address) for s in result.chief.sheets for m in s.marks
        ]
        assert sorted(chief) == [("add", "m.py@b2"), ("drop", "m.py@b1")]

    def test_a_stet_puts_it_to_the_mover_and_the_stetter(self, tmp_path):
        message, root = _a_move_two_roles_read(tmp_path)
        _out, first = handle(message)
        assert first is not None
        answers = _answered(first, _placement_or_clean("stet"))
        _out, result = handle(AnswersReturned(first.proof, answers, root))
        assert result is not None
        batch = _slots_of(result)
        assert [m["placement"] for m in result.proof.moves] == ["contested"]
        for role in ("block-context", "module-context"):
            assert [s["to"] for s in batch[role] if s["question"] == "placement"] == [
                "m.py@b2"
            ]

    def test_a_turn_that_asks_only_placements_is_counted(self, tmp_path):
        """The second turn's slots are the contested move's alone, so its
        answers are recorded on the move and on no place; the proof stands at
        that turn all the same."""
        message, root = _a_move_two_roles_read(tmp_path)
        _out, first = handle(message)
        assert first is not None
        answers = _answered(first, _placement_or_clean("stet"))
        _out, second = handle(AnswersReturned(first.proof, answers, root))
        batch = _slots_of(second)
        assert {s["question"] for slots in batch.values() for s in slots} == {
            "placement"
        }
        assert second is not None
        answers = _answered(second, lambda s: "stet")
        out, third = handle(AnswersReturned(second.proof, answers, root))
        assert third is not None, out
        assert turn_of(third.proof) == 2

    def test_a_placement_answer_from_a_role_not_asked_is_refused(self, tmp_path):
        """Review Focus 4."""
        message, root = _a_move_two_roles_read(tmp_path)
        _out, first = handle(message)
        assert first is not None
        answers = _answered(first, _placement_or_clean("agree"))
        stray = {
            "address": "m.py@b1",
            "to": "m.py@b2",
            "instruction": "agree",
            "reason": "r",
        }
        answers.setdefault("block-context", []).append(stray)
        out, result = handle(AnswersReturned(first.proof, answers, root))
        assert result is None
        assert (
            "block-context",
            "m.py@b1 -> m.py@b2",
            "not put to block-context -- this move is put to module-context",
        ) in _refusals(out)


def _taken_in(*addresses):
    """The chief's ruling at each of `addresses`, taking block-context's text."""
    return [
        {"address": a, "answer": "taken_in", "side": "block-context", "reason": "r"}
        for a in addresses
    ]


class TestAnOpenMoveIsNotTranscribed:
    """A move whose placement is undecided closes only on the chief's
    placement ruling. The write end reads the proof's moves and refuses one
    that is still open, so the paragraph cannot land at one end while the
    other keeps it."""

    def _ruled(self, tmp_path):
        """A contested move the chief takes in, then its two ends' words."""
        message, root = _a_move_two_roles_read(tmp_path)
        _out, first = handle(message)
        assert first is not None
        answers = _answered(first, _placement_or_clean("stet"))
        out, second = handle(AnswersReturned(first.proof, answers, root))
        assert second is not None, out
        placement = {
            "address": "m.py@b1",
            "to": "m.py@b2",
            "answer": "taken_in",
            "side": "block-context",
            "reason": "r",
        }
        out, placed = handle(DispositionsWritten(second.proof, [placement]))
        assert placed is not None, out
        out, closed = handle(
            DispositionsWritten(placed.proof, _taken_in("m.py@b1", "m.py@b2"))
        )
        assert closed is not None, out
        return closed.proof, root

    def test_a_contested_move_the_chief_ruled_is_transcribed(self, tmp_path):
        proof, root = self._ruled(tmp_path)
        assert [m["placement"] for m in proof.moves] == ["agreed"]
        (schedule,) = docket_of_proof(proof, root).docket.schedules
        assert [(one.cue, one.text) for one in schedule.alterations] == [
            ("b1", "# one\n# three"),
            ("b2", ARRIVAL),
        ]

    def test_a_move_that_will_not_read_is_refused(self, tmp_path):
        proof, root = self._ruled(tmp_path)
        broken = replace(proof, moves=({"origin": "m.py@b1"},))
        with pytest.raises(CannotTranscribe) as raised:
            docket_of_proof(broken, root)
        assert any("destination" in why for why in raised.value.reasons), (
            raised.value.reasons
        )


# -- a human question is asked before the fold (`Process: #197`) -------------


def _with_a_human_query(tmp_path):
    root = tmp_path / "repo"
    binder = a_real_binder_over(root, {"m.py@b1": BASE, "m.py@b2": OTHER})
    by_role = {
        "block-context": {
            "m.py@b1": a_query("m.py@b1", Shape.HUMAN_REVIEW_NECESSARY),
            "m.py@b2": a_clean("m.py@b2"),
        },
        "module-context": {
            "m.py@b1": a_clean("m.py@b1"),
            "m.py@b2": a_clean("m.py@b2"),
        },
    }
    copies = [returned(wire) for wire in copies_over(binder, by_role)]
    return binder, root, copies


class TestAHumanQuestionIsAskedBeforeTheFold:
    """`decision-log.md Process: #197`: no human question reaches a fold."""

    def test_an_unanswered_human_query_rolls_the_stage_back_naming_it(self, tmp_path):
        binder, root, copies = _with_a_human_query(tmp_path)
        out, result = handle(CopiesReturned("4c", copies, binder, root, None))
        assert result is None
        asks = [e for e in out if isinstance(e, events.AsksTheHuman)]
        assert [(e.role, e.at, e.answer) for e in asks] == [
            ("block-context", "m.py@b1", "")
        ]
        assert isinstance(out[-1], events.RolledBack)
        assert not any(isinstance(e, events.Refused) for e in out)

    def test_an_answered_query_still_rolls_back_and_carries_the_answer(self, tmp_path):
        binder, root, copies = _with_a_human_query(tmp_path)
        human = (HumanAnswer("block-context", "m.py@b1", "q", "Keep it."),)
        out, result = handle(CopiesReturned("4c", copies, binder, root, None, human))
        assert result is None
        (ask,) = [e for e in out if isinstance(e, events.AsksTheHuman)]
        assert ask.answer == "Keep it."

    def test_once_the_role_replaces_its_query_the_stage_folds(self, tmp_path):
        root = tmp_path / "repo"
        binder = a_real_binder_over(root, {"m.py@b1": BASE, "m.py@b2": OTHER})
        by_role = {
            role: {"m.py@b1": a_clean("m.py@b1"), "m.py@b2": a_clean("m.py@b2")}
            for role in ("block-context", "module-context")
        }
        copies = [returned(wire) for wire in copies_over(binder, by_role)]
        human = (HumanAnswer("block-context", "m.py@b1", "q", "Keep it."),)
        _out, result = handle(CopiesReturned("4c", copies, binder, root, None, human))
        assert result is not None

    def test_a_human_answer_in_a_turn_rolls_the_turn_back_naming_its_move(
        self, tmp_path
    ):
        """Review Focus 1. A human question answered at a placement slot is
        named by the move's key, and one at a composition slot by the place's
        address -- the second asked once the move is agreed, since an end of
        an open move is `to-come` and asks nothing."""
        message, root = _a_move_two_roles_read(tmp_path)
        _out, first = handle(message)
        assert first is not None and first.batch is not None
        human_query = {
            "shape": "human-review-necessary",
            "attempted": "read both",
            "settles": "the author",
        }

        def asking(question):
            def answer_for(slot):
                if slot["question"] == question:
                    return {
                        **slot,
                        "instruction": "query",
                        "reason": "ask the author",
                        "claim": human_query,
                    }
                return {**slot, "instruction": "clean", "reason": "r"}

            return answer_for

        def asks_in(result, question):
            assert result.batch is not None
            answer_for = asking(question)
            answers = {
                role: [answer_for(s) for s in slots]
                for role, slots in result.batch.items()
            }
            out, turned = handle(AnswersReturned(result.proof, answers, root))
            assert turned is None
            return [(e.role, e.at) for e in out if isinstance(e, events.AsksTheHuman)]

        assert asks_in(first, "placement") == [("module-context", "m.py@b1 -> m.py@b2")]
        answers = _answered(first, _placement_or_clean("agree"))
        out, agreed = handle(AnswersReturned(first.proof, answers, root))
        assert agreed is not None, out
        assert asks_in(agreed, "composition") == [
            ("module-context", "m.py@b1"),
            ("module-context", "m.py@b2"),
        ]

    def test_a_human_query_beside_a_refusal_reports_both(self, tmp_path):
        """Review Focus 4."""
        binder, root, copies = _with_a_human_query(tmp_path)
        broken = [
            returned(w)
            for w in copies_over(
                binder,
                {
                    "module-context": {
                        "m.py@b1": a_correct("m.py@b1", "a sentence that is not there"),
                        "m.py@b2": a_clean("m.py@b2"),
                    }
                },
            )
        ]
        out, result = handle(
            CopiesReturned("4c", [copies[0], *broken], binder, root, None)
        )
        assert result is None
        assert any(isinstance(e, events.Refused) for e in out)
        assert any(isinstance(e, events.AsksTheHuman) for e in out)
