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
    a_clean,
    a_correct_setting,
    an_add,
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
        again, problems = run_turn("4c", copies, binder, REPO, batch, answers, turn=1)
        assert problems == []
        assert again.escalations == []
        # ! NOT A STET YET, since `Process: #89`: the surviving mark is a lone
        # one and block-context, now clean, marked the place -- so it goes back
        # to block-context carrying function-context's text.
        assert [e["address"] for e in again.rereads] == ["m.py@b1"]
        assert again.rereads[0]["roles"] == ["block-context", "function-context"]
        assert again.rereads[0]["composed"].change == DOS
        batch2 = batch_of(again.escalations, again.rereads)
        answers2 = {r: [{**batch2[r][0], "instruction": "clean"}] for r in batch2}
        final, problems = run_turn("4c", copies, binder, REPO, batch2, answers2, turn=2)
        assert problems == []
        ruled = final.determined["m.py@b1"]
        assert ruled.answer is Answer.STET
        assert ruled.turn == 2
        assert ruled.how == "identical"
        assert [m.change for m in entries_of(final.chief)] == [DOS]

    def test_two_corrects_that_converge_are_a_stet(self):
        binder, copies, got = _escalated()
        batch = batch_of(got.escalations, got.rereads)
        answers = {
            **_answered(
                batch, "block-context", instruction="correct", reason="met", change=DOS
            ),
            **_answered(batch, "function-context", instruction="hold", reason="stands"),
        }
        again, problems = run_turn("4c", copies, binder, REPO, batch, answers, turn=1)
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
        again, problems = run_turn("4c", copies, binder, REPO, batch, answers, turn=1)
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
        again, problems = run_turn("4c", copies, binder, REPO, batch, answers, turn=1)
        assert any("unanswered" in p for p in problems)
        assert [e["address"] for e in again.escalations] == ["m.py@b1"]


class TestTheSentBatchPairsTheAnswer:
    """T27, MEASURED in the game's hand 1: a role rewrote its slot without the
    `question` key and the fold refused it. The flow SENT the slot; the answer
    pairs to it by address, and nothing on the returned slot is trusted."""

    def test_a_stripped_slot_still_parses_against_what_was_sent(self):
        binder, copies, got = _escalated()
        batch = batch_of(got.escalations, got.rereads)
        bare = {"address": "m.py@b1", "instruction": "withdraw", "reason": "theirs"}
        answers = {
            "block-context": [bare],
            **_answered(batch, "function-context", instruction="hold", reason="stands"),
        }
        again, problems = run_turn("4c", copies, binder, REPO, batch, answers, turn=1)
        assert problems == []
        # The withdrawal applied: function-context's mark is the lone one, and
        # it goes back to block-context (`#89`).
        assert again.rereads[0]["composed"].change == DOS

    def test_an_answer_at_an_address_never_sent_is_refused_by_name(self):
        binder, copies, got = _escalated()
        batch = batch_of(got.escalations, got.rereads)
        stray = {"address": "m.py@b9", "instruction": "hold", "reason": "?"}
        answers = {
            "block-context": [stray],
            **_answered(batch, "function-context", instruction="hold", reason="stands"),
        }
        _, problems = run_turn("4c", copies, binder, REPO, batch, answers, turn=1)
        assert any("m.py@b9" in p and "never sent" in p for p in problems)

    def test_a_sent_slot_left_out_of_the_answer_is_unanswered(self):
        binder, copies, got = _escalated()
        batch = batch_of(got.escalations, got.rereads)
        answers = {
            "block-context": [],
            **_answered(batch, "function-context", instruction="hold", reason="stands"),
        }
        _, problems = run_turn("4c", copies, binder, REPO, batch, answers, turn=1)
        assert any("m.py@b1" in p and "unanswered" in p for p in problems)


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
        again, problems = run_turn("4c", copies, binder, REPO, batch, answers, turn=1)
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
        again, problems = run_turn("4c", copies, binder, REPO, batch, answers, turn=1)
        assert problems == []
        assert [e["address"] for e in again.escalations] == ["m.py@b1"]
        assert again.determined == {}
        assert {p.mark.change for p in again.escalations[0]["marks"]} == {
            COMPOSED,
            fixed,
        }

    def test_a_patch_over_it_stays_a_patch_and_the_role_stays_in_the_fold(self):
        """MEASURED in the game's hand 2: a patch answer was rewritten as a
        `correct`, which owes sources a patch never carried, and the role's
        entry was refused at the fold -- the role vanished from the escalation."""
        binder, copies, got = _composed()
        batch = batch_of(got.escalations, got.rereads)
        worded = "# ONE\n# two\n# three!\n"
        answers = {
            **_answered(batch, "block-context", instruction="clean"),
            **_answered(
                batch,
                "function-context",
                instruction="patch",
                reason="wording only",
                claim={"from": "# THREE", "to": "# three!"},
                change=worded,
            ),
        }
        again, problems = run_turn("4c", copies, binder, REPO, batch, answers, turn=1)
        assert problems == []
        assert again.revisit == []
        assert [e["address"] for e in again.escalations] == ["m.py@b1"]
        roles = {p.role for p in again.escalations[0]["marks"]}
        assert roles == {"block-context", "function-context"}

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
        _, problems = run_turn("4c", copies, binder, REPO, batch, answers, turn=1)
        assert any("not a composition answer" in p for p in problems)


def _lone(mark: dict):
    """One owing mark from block-context, three cleans -- `#89`'s case."""
    binder = a_binder_over({"m.py@b1": BASE})
    copies = copies_over(
        binder,
        {
            "block-context": {"m.py@b1": mark},
            "function-context": {"m.py@b1": a_clean("m.py@b1")},
            "module-context": {"m.py@b1": a_clean("m.py@b1")},
            "ownership-context": {"m.py@b1": a_clean("m.py@b1")},
        },
    )
    got = collate("4c", copies, binder, root=REPO)
    return binder, copies, got


class TestALoneOwingMark:
    """`Process: #89`, MEASURED in the game's hand 3: a lone patch against three
    cleans landed as a stet at turn 0, and the cleans had never seen the text.
    A lone mark is a composition of one side: it goes back to every role that
    marked the place but a query, carrying its own text."""

    def test_it_goes_back_to_every_role_that_marked_carrying_its_text(self):
        _, _, got = _lone(a_correct_setting("m.py@b1", "two", TWO))
        assert got.determined == {}
        assert entries_of(got.chief) == []
        assert [e["address"] for e in got.rereads] == ["m.py@b1"]
        assert got.rereads[0]["roles"] == [
            "block-context",
            "function-context",
            "module-context",
            "ownership-context",
        ]
        batch = batch_of(got.escalations, got.rereads)
        assert all(batch[r][0]["raw_text"] == TWO for r in batch)
        assert all(batch[r][0]["composed"] is True for r in batch)

    def test_every_clean_over_its_text_is_a_stet_carrying_it(self):
        binder, copies, got = _lone(a_correct_setting("m.py@b1", "two", TWO))
        batch = batch_of(got.escalations, got.rereads)
        answers = {r: [{**batch[r][0], "instruction": "clean"}] for r in batch}
        again, problems = run_turn("4c", copies, binder, REPO, batch, answers, turn=1)
        assert problems == []
        assert again.rereads == [] and again.escalations == []
        ruled = again.determined["m.py@b1"]
        assert ruled.answer is Answer.STET
        assert ruled.how == "identical"
        assert [m.change for m in entries_of(again.chief)] == [TWO]

    def test_a_lone_add_lands_the_same_way(self):
        """T13's own verify: a lone surviving add, all others holding, lands."""
        added = an_add("m.py@b1")
        added["change"] = BASE + "# and the sentence that was missing\n"
        binder, copies, got = _lone(added)
        batch = batch_of(got.escalations, got.rereads)
        assert all(batch[r][0]["raw_text"] == added["change"] for r in batch)
        answers = {r: [{**batch[r][0], "instruction": "clean"}] for r in batch}
        again, problems = run_turn("4c", copies, binder, REPO, batch, answers, turn=1)
        assert problems == []
        assert [m.change for m in entries_of(again.chief)] == [added["change"]]

    def test_a_clean_over_the_base_from_the_author_withdraws_it(self):
        """A `clean` adopts the slot's text; where a role owed the only change
        and the slot carries its own text, clean is agreement, not withdrawal.
        Withdrawal is a `correct` back to the base, or a DiffMark withdraw on an
        escalation."""
        binder, copies, got = _lone(a_correct_setting("m.py@b1", "two", TWO))
        batch = batch_of(got.escalations, got.rereads)
        answers = {r: [{**batch[r][0], "instruction": "clean"}] for r in batch}
        again, _ = run_turn("4c", copies, binder, REPO, batch, answers, turn=1)
        assert "m.py@b1" in again.determined


def _two_places():
    """b1 will converge on turn 1; b5 stays contested -- so turn 2 has a batch."""
    binder = a_binder_over({"m.py@b1": BASE, "m.py@b5": BASE})
    copies = copies_over(
        binder,
        {
            "block-context": {
                "m.py@b1": a_correct_setting("m.py@b1", "two", TWO),
                "m.py@b5": a_correct_setting("m.py@b5", "two", TWO),
            },
            "function-context": {
                "m.py@b1": a_correct_setting("m.py@b1", "two", DOS),
                "m.py@b5": a_correct_setting("m.py@b5", "two", DOS),
            },
        },
    )
    got = collate("4c", copies, binder, root=REPO)
    assert sorted(e["address"] for e in got.escalations) == ["m.py@b1", "m.py@b5"]
    return binder, copies, got


def _slot(batch: dict, role: str, address: str) -> dict:
    return next(s for s in batch[role] if s["address"] == address)


class TestOnceStetAlwaysStet:
    """`Process: #91`. MEASURED in the game, hands 1 and 4: the fold re-recorded
    every place at the current turn, so a stet at turn 1 read turn 2 after
    the next fold; and nothing kept a determined place out of later batches."""

    def _turn_one(self):
        binder, copies, got = _two_places()
        batch = batch_of(got.escalations, got.rereads)
        answers = {
            "block-context": [
                {
                    **_slot(batch, "block-context", "m.py@b1"),
                    "instruction": "correct",
                    "reason": "met",
                    "change": DOS,
                },
                {
                    **_slot(batch, "block-context", "m.py@b5"),
                    "instruction": "hold",
                    "reason": "mine",
                },
            ],
            "function-context": [
                {
                    **_slot(batch, "function-context", "m.py@b1"),
                    "instruction": "hold",
                    "reason": "stands",
                },
                {
                    **_slot(batch, "function-context", "m.py@b5"),
                    "instruction": "hold",
                    "reason": "mine",
                },
            ],
        }
        again, problems = run_turn("4c", copies, binder, REPO, batch, answers, turn=1)
        assert problems == []
        assert again.determined["m.py@b1"].turn == 1
        assert [e["address"] for e in again.escalations] == ["m.py@b5"]
        return binder, copies, again

    def test_a_stet_place_keeps_its_turn_and_leaves_every_later_batch(self):
        binder, copies, one = self._turn_one()
        batch2 = batch_of(one.escalations, one.rereads)
        assert all(s["address"] == "m.py@b5" for r in batch2 for s in batch2[r])
        answers2 = {
            r: [{**batch2[r][0], "instruction": "hold", "reason": "still"}]
            for r in batch2
        }
        two, problems = run_turn(
            "4c", copies, binder, REPO, batch2, answers2, turn=2, earlier=one.determined
        )
        assert problems == []
        assert two.determined["m.py@b1"].turn == 1
        assert [e["address"] for e in two.escalations] == ["m.py@b5"]

    def test_a_role_changing_its_entry_at_a_stet_place_changes_nothing(self):
        binder, copies, one = self._turn_one()
        # block-context rewrites its b1 entry behind the fold's back.
        for copy in copies:
            if copy["role"] == "block-context":
                for sheet in copy["sheets"]:
                    for entry in sheet["marks"]:
                        if entry["address"] == "m.py@b1":
                            entry["change"] = "# one\n# something else\n# three\n"
        batch2 = batch_of(one.escalations, one.rereads)
        answers2 = {
            r: [{**batch2[r][0], "instruction": "hold", "reason": "still"}]
            for r in batch2
        }
        two, _ = run_turn(
            "4c", copies, binder, REPO, batch2, answers2, turn=2, earlier=one.determined
        )
        assert two.determined["m.py@b1"].turn == 1
        assert two.determined["m.py@b1"].mark is not None
        assert two.determined["m.py@b1"].mark.change == DOS
        assert [e["address"] for e in two.escalations] == ["m.py@b5"]
        assert [m.change for m in entries_of(two.chief)] == [DOS]


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
