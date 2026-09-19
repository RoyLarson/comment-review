"""The bus: one message in, the fold's events and what the stage saves out."""

from dataclasses import replace

from helpers import (
    a_clean,
    a_correct_citing,
    a_correct_setting,
    a_move,
    a_patch,
    a_query,
    a_real_binder_over,
    copies_over,
    returned,
)

from comment_review.desk.answers.answer import Question
from comment_review.desk.evaluate.place import Place
from comment_review.desk.evaluate.state import State
from comment_review.desk.marks.mark import Shape
from comment_review.desk.stages import Dispatch, Kind, Role, Stage
from comment_review.desk.work import events
from comment_review.flows.bus import (
    AnswersReturned,
    CopiesReturned,
    DispositionsWritten,
    handle,
)

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


def test_the_chief_copy_holds_one_mark_at_the_settled_place(tmp_path):
    _out, result = handle(_message(tmp_path, TWO_ROLES))
    assert result is not None
    assert result.chief is not None
    marks = [mark for sheet in result.chief.sheets for mark in sheet.marks]
    assert [mark.address for mark in marks] == ["m.py@b1"]
    assert marks[0].change == CORRECTED


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

#: One role's human-review query and nothing else: the fold settles `b1` and
#: leaves `b2` for the human, carrying neither forward.
A_QUERY_FOR_THE_HUMAN = {
    "block-context": {
        PLACE: a_clean(PLACE),
        "m.py@b2": a_query("m.py@b2", Shape.HUMAN_REVIEW_NECESSARY),
    },
    "function-context": {
        PLACE: a_clean(PLACE),
        "m.py@b2": a_clean("m.py@b2"),
    },
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
#: function-context corrects b2, contesting the destination and pairing the
#: origin to it. Both ends are carried forward and the chief rules them.
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


def test_the_chief_closes_a_contested_move_at_each_of_its_ends(tmp_path):
    """!! THE ORIGIN IS THE CASE. Nobody marked it but the mover, so it
    reaches `stands` alone and is carried forward only because its partner
    is. The dispositions pass read that un-paired state until 2026-09-18 and
    refused every ruling the chief made with *"cannot close a place that is
    agreed"* -- at a place this same handler had just reported contested.
    """
    collated = _collated(tmp_path, A_CONTESTED_MOVE)
    assert _state_at(collated.proof, PLACE) == "contested"
    assert _state_at(collated.proof, "m.py@b2") == "contested"
    out, closed = handle(
        DispositionsWritten(
            collated.proof,
            [
                _ruling(PLACE, "taken_in", side="block-context"),
                _ruling("m.py@b2", "taken_in", side="block-context"),
            ],
        )
    )
    assert closed is not None, out
    assert events.Settled(PLACE, REMAINDER) in out
    assert events.Settled("m.py@b2", MOVED_TO) in out
    assert _state_at(closed.proof, PLACE) == "stands"
    assert _state_at(closed.proof, "m.py@b2") == "stands"


def test_the_chief_may_take_a_moves_origin_in_and_recast_its_destination(tmp_path):
    collated = _collated(tmp_path, A_CONTESTED_MOVE)
    out, closed = handle(
        DispositionsWritten(
            collated.proof,
            [
                _ruling(PLACE, "taken_in", side="block-context"),
                _ruling("m.py@b2", "recast", prose=CHIEFS_OWN),
            ],
        )
    )
    assert closed is not None, out
    assert closed.chief is not None
    assert events.Settled(PLACE, REMAINDER) in out
    assert events.Settled("m.py@b2", CHIEFS_OWN) in out
    # The chief's copy writes the pair as the two rulings decided it, and the
    # move is not taken in: its destination closed on the chief's own prose
    # rather than on what the move sets there, so writing the move would land
    # a paragraph the chief ruled against.
    placed = [
        (mark.address, str(mark.instruction), mark.change)
        for sheet in closed.chief.sheets
        for mark in sheet.marks
    ]
    assert placed == [
        (PLACE, "correct", REMAINDER),
        ("m.py@b2", "correct", CHIEFS_OWN),
    ]


def test_a_move_ruled_at_one_end_only_is_refused_for_the_other(tmp_path):
    collated = _collated(tmp_path, A_CONTESTED_MOVE)
    out, closed = handle(
        DispositionsWritten(
            collated.proof, [_ruling(PLACE, "taken_in", side="block-context")]
        )
    )
    assert closed is None
    assert (
        "copy-chief",
        "m.py@b2",
        "carried forward and not ruled on -- it was put to block-context,"
        " function-context",
    ) in _refusals(out)
    assert any(isinstance(one, events.RolledBack) for one in out)


#: block-context moves b1's middle line to b2; function-context rewrites that
#: same line where it stands. The origin is an escalation put to both roles,
#: and the destination a composition put to the role that did not move it --
#: so the origin is the only place the mover can answer.
A_MOVE_ITS_ORIGIN_CONTESTS = {
    "block-context": {
        PLACE: a_move(PLACE, "m.py@b2", change="# two\n", reads=OTHER + "# two\n"),
        "m.py@b2": a_clean("m.py@b2"),
    },
    "function-context": {
        PLACE: a_correct_setting(PLACE, "two", CORRECTED),
        "m.py@b2": a_clean("m.py@b2"),
    },
}


def test_a_mover_withdrawing_at_its_origin_takes_the_move_off_the_destination(tmp_path):
    """`decision-log.md Process: #129`: an answer at either end reaches the
    move whole. Two turns, because the destination settles on the moved text
    in the first and the mover withdraws in the second -- and the sentence
    must then be on the page once, in the wording the other role gave it,
    where it already was.
    """
    collated = _collated(tmp_path, A_MOVE_ITS_ORIGIN_CONTESTS)
    assert _state_at(collated.proof, PLACE) == "contested"
    assert _state_at(collated.proof, "m.py@b2") == "contested"
    assert collated.batch is not None
    assert sorted(one["address"] for one in collated.batch["block-context"]) == [PLACE]
    out, first = handle(
        AnswersReturned(
            collated.proof,
            {
                "block-context": [_answer(PLACE, "hold", "it belongs at b2")],
                "function-context": [
                    _answer(PLACE, "hold", "it belongs here, reworded"),
                    _answer("m.py@b2", "clean", "it reads with the line in"),
                ],
            },
            tmp_path / "repo",
        )
    )
    assert first is not None, out
    assert first.batch is not None
    out, second = handle(
        AnswersReturned(
            first.proof,
            {
                # The destination settled in the first turn and is carried
                # forward by its partner alone, which is why its slots ask
                # an escalation and why neither answer there decides
                # anything: what takes the move off it is the withdrawal
                # written at the origin.
                "block-context": [
                    _answer(PLACE, "withdraw", "reworded where it stands, it reads"),
                    _answer("m.py@b2", "hold", "nothing of mine to change here"),
                ],
                "function-context": [
                    _answer(PLACE, "hold", "mine stands"),
                    _answer("m.py@b2", "hold", "as before"),
                ],
            },
            tmp_path / "repo",
        )
    )
    assert second is not None, out
    assert events.Settled(PLACE, CORRECTED) in out
    assert events.Settled("m.py@b2", None) in out
    assert second.batch is None
    assert second.chief is not None
    assert _changes_on(second.chief) == [CORRECTED]


def test_a_disposition_at_an_unsettlable_place_is_refused(tmp_path):
    collated = _collated(tmp_path, A_QUERY_FOR_THE_HUMAN)
    out, result = handle(
        DispositionsWritten(
            collated.proof,
            [
                {
                    "address": "m.py@b2",
                    "answer": "taken_in",
                    "side": "block-context",
                    "reason": "ruling on it anyway",
                }
            ],
        )
    )
    assert result is None
    assert ("copy-chief", "m.py@b2", "not carried forward") in _refusals(out)
    assert any(isinstance(one, events.RolledBack) for one in out)


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


def test_a_place_an_answer_holds_for_the_human_is_named_for_the_asking(tmp_path):
    """`decision-log.md Process: #90`: a human-review query rides to the end
    of the review to be asked. A role may raise one in a turn as well as on
    its first reading, and the place it holds is named either way."""
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
    assert result is not None, out
    assert _state_at(result.proof, PLACE) == "unsettlable"
    assert (
        events.Unsettlable(
            PLACE,
            "block-context",
            "which of the two the author meant is theirs to say",
        )
        in out
    )


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
