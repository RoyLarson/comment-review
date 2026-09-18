"""The bus: one message in, the fold's events and what the stage saves out."""

from dataclasses import replace

from helpers import (
    a_clean,
    a_correct_citing,
    a_correct_setting,
    a_query,
    a_real_binder_over,
    copies_over,
    returned,
)

from comment_review.desk.answers.answer import Question
from comment_review.desk.evaluate.place import Place
from comment_review.desk.evaluate.state import State
from comment_review.desk.mark import Shape
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
