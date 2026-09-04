"""`flows.turn` -- a PROTOTYPE. The loop `docs/the-turn.md` describes, run over
the real `collate()`: a batch answered, applied, folded again; the chief at
the cap.

! INPUTS ARE REAL -- binders from `a_binder_over`, copies from the real
`seed`, marks through `desk.mark.INSTRUCTIONS`. The answers are what a role
would hand back: the seeded slot with its fields filled.
"""

import pytest
from helpers import (
    _MARK_PY_CITE,
    _MARK_PY_LINE_1,
    REPO,
    a_binder_over,
    a_correct_setting,
    copies_over,
    entries_of,
)

from comment_review.desk.determined import CHIEF, ORIGINAL, Answer
from comment_review.desk.diff_mark import COMPOSITION, QUESTION, batch_of
from comment_review.desk.mark import Mark
from comment_review.flows.collate import collate
from comment_review.flows.turn import determined_chief, rule_at_cap, run_turn

BASE = "# one\n# two\n# three\n"
TWO = "# one\n# TWO\n# three\n"
DOS = "# one\n# dos\n# three\n"
ONE_ = "# ONE\n# two\n# three\n"
_THREE = "# one\n# two\n# THREE\n"
COMPOSED = "# ONE\n# two\n# THREE\n"


def _escalated():
    binder = a_binder_over({"m.py@b1": BASE})
    copies = copies_over(
        binder,
        {
            "block-context": {"m.py@b1": a_correct_setting("m.py@b1", "two", TWO)},
            "function-context": {"m.py@b1": a_correct_setting("m.py@b1", "two", DOS)},
        },
    )
    got = collate("4c", copies, binder, root=REPO)
    assert [e["address"] for e in got.escalations] == ["m.py@b1"]
    return binder, copies, got


def _composed():
    binder = a_binder_over({"m.py@b1": BASE})
    copies = copies_over(
        binder,
        {
            "block-context": {"m.py@b1": a_correct_setting("m.py@b1", 0, ONE_)},
            "function-context": {"m.py@b1": a_correct_setting("m.py@b1", 2, _THREE)},
        },
    )
    got = collate("4c", copies, binder, root=REPO)
    assert [e["address"] for e in got.rereads] == ["m.py@b1"]
    assert got.rereads[0]["composed"].change == COMPOSED
    return binder, copies, got


def _answered(batch: dict, role: str, **fields) -> dict:
    return {role: [{**batch[role][0], **fields}]}


class TestAnEscalation:
    def test_a_withdraw_leaves_the_other_roles_mark_standing(self):
        binder, copies, got = _escalated()
        batch = batch_of(got.escalations, got.rereads)
        answers = {
            **_answered(
                batch, "block-context", instruction="withdraw", reason="theirs"
            ),
            **_answered(batch, "function-context", instruction="hold", reason="stands"),
        }
        again, problems = run_turn("4c", copies, binder, REPO, answers, turn=1)
        assert problems == []
        assert again.escalations == []
        ruled = again.determined["m.py@b1"]
        assert ruled.answer is Answer.STET
        assert ruled.turn == 1
        assert ruled.side == "function-context"
        assert ruled.how == "one"
        assert [m.change for m in entries_of(again.chief)] == [DOS]

    def test_two_corrects_that_converge_are_a_stet(self):
        binder, copies, got = _escalated()
        batch = batch_of(got.escalations, got.rereads)
        answers = {
            **_answered(
                batch, "block-context", instruction="correct", reason="met", change=DOS
            ),
            **_answered(batch, "function-context", instruction="hold", reason="stands"),
        }
        again, problems = run_turn("4c", copies, binder, REPO, answers, turn=1)
        assert problems == []
        ruled = again.determined["m.py@b1"]
        assert ruled.answer is Answer.STET
        assert ruled.how == "identical"
        assert [m.change for m in entries_of(again.chief)] == [DOS]

    def test_two_holds_stay_escalated(self):
        binder, copies, got = _escalated()
        batch = batch_of(got.escalations, got.rereads)
        answers = {
            **_answered(batch, "block-context", instruction="hold", reason="mine"),
            **_answered(batch, "function-context", instruction="hold", reason="mine"),
        }
        again, problems = run_turn("4c", copies, binder, REPO, answers, turn=1)
        assert problems == []
        assert [e["address"] for e in again.escalations] == ["m.py@b1"]
        assert again.determined == {}

    def test_an_unanswered_slot_is_refused_and_the_place_stays(self):
        binder, copies, got = _escalated()
        batch = batch_of(got.escalations, got.rereads)
        answers = {
            "block-context": [batch["block-context"][0]],
            **_answered(batch, "function-context", instruction="hold", reason="mine"),
        }
        again, problems = run_turn("4c", copies, binder, REPO, answers, turn=1)
        assert any("unanswered" in p for p in problems)
        assert [e["address"] for e in again.escalations] == ["m.py@b1"]


class TestAComposition:
    def test_the_composed_text_goes_back_as_a_marks_question(self):
        _, _, got = _composed()
        batch = batch_of(got.escalations, got.rereads)
        slot = batch["block-context"][0]
        assert slot[QUESTION] == COMPOSITION
        assert slot["raw_text"] == COMPOSED
        assert slot["composed"] is True
        assert slot["instruction"] is None
        assert entries_of(got.chief) == []

    def test_every_role_clean_on_it_is_a_stet_carrying_the_composition(self):
        binder, copies, got = _composed()
        batch = batch_of(got.escalations, got.rereads)
        answers = {
            **_answered(batch, "block-context", instruction="clean"),
            **_answered(batch, "function-context", instruction="clean"),
        }
        again, problems = run_turn("4c", copies, binder, REPO, answers, turn=1)
        assert problems == []
        assert again.rereads == []
        ruled = again.determined["m.py@b1"]
        assert ruled.answer is Answer.STET
        assert ruled.how == "identical"
        assert [m.change for m in entries_of(again.chief)] == [COMPOSED]

    def test_a_correct_over_it_folds_again_as_an_escalation(self):
        binder, copies, got = _composed()
        batch = batch_of(got.escalations, got.rereads)
        fixed = "# ONE\n# two\n# 3\n"
        answers = {
            **_answered(batch, "block-context", instruction="clean"),
            **_answered(
                batch,
                "function-context",
                instruction="correct",
                reason="the composition kept my wording and it reads wrong now",
                claim={"false": "# THREE", "true": "# 3"},
                sources=[{"cite": _MARK_PY_CITE, "verbatim": _MARK_PY_LINE_1}],
                change=fixed,
            ),
        }
        again, problems = run_turn("4c", copies, binder, REPO, answers, turn=1)
        assert problems == []
        assert [e["address"] for e in again.escalations] == ["m.py@b1"]
        assert again.determined == {}
        assert {p.mark.change for p in again.escalations[0]["marks"]} == {
            COMPOSED,
            fixed,
        }

    def test_a_drop_is_not_a_composition_answer(self):
        binder, copies, got = _composed()
        batch = batch_of(got.escalations, got.rereads)
        answers = {
            **_answered(
                batch,
                "block-context",
                instruction="drop",
                reason="none of it",
                claim={"drop": COMPOSED},
                sources=[{"cite": _MARK_PY_CITE, "verbatim": _MARK_PY_LINE_1}],
                change="",
            ),
            **_answered(batch, "function-context", instruction="clean"),
        }
        _, problems = run_turn("4c", copies, binder, REPO, answers, turn=1)
        assert any("not a composition answer" in p for p in problems)


class TestTheCap:
    def test_taken_in_of_the_original_leaves_no_entry_on_the_chief(self):
        _, _, got = _escalated()
        ruled = rule_at_cap(
            got, "m.py@b1", Answer.TAKEN_IN, ORIGINAL, "neither reading holds", turn=2
        )
        assert ruled.mark is None
        assert ruled.side == ORIGINAL
        assert ruled.how == "cap"
        every, chief = determined_chief(got, [ruled])
        assert every["m.py@b1"] is ruled
        assert entries_of(chief) == []

    def test_taken_in_of_a_role_carries_that_roles_text(self):
        _, _, got = _escalated()
        ruled = rule_at_cap(
            got, "m.py@b1", Answer.TAKEN_IN, "function-context", "dos is right", turn=2
        )
        _, chief = determined_chief(got, [ruled])
        assert [m.change for m in entries_of(chief)] == [DOS]

    def test_a_recast_carries_the_chiefs_own_prose_and_parses(self):
        _, _, got = _escalated()
        prose = "# one\n# 2\n# three\n"
        ruled = rule_at_cap(
            got, "m.py@b1", Answer.RECAST, "", "both sides miss it", turn=2, prose=prose
        )
        assert ruled.side == CHIEF
        _, chief = determined_chief(got, [ruled])
        entry = entries_of(chief)[0]
        assert entry.change == prose
        again, why = Mark.deserialize(entry.address, entry.serialize())
        assert why == []
        assert again == entry

    def test_stet_is_not_the_chiefs_to_rule(self):
        _, _, got = _escalated()
        with pytest.raises(ValueError):
            rule_at_cap(got, "m.py@b1", Answer.STET, "block-context", "x", turn=2)

    def test_a_side_with_no_mark_there_cannot_be_taken_in(self):
        _, _, got = _escalated()
        with pytest.raises(ValueError):
            rule_at_cap(got, "m.py@b1", Answer.TAKEN_IN, "module-context", "x", turn=2)
