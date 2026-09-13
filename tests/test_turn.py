"""`flows.turn`. The loop `docs/the-turn.md` describes, run over
the real `collate()`: a batch answered, applied, folded again; the chief at
max turns.

! INPUTS ARE REAL -- binders from `a_binder_over`, copies from the real
`seed`, marks through `desk.mark.INSTRUCTIONS`. The answers are what a role
would hand back: the seeded slot with its fields filled.
"""

import pytest
from helpers import (
    _MARK_PY_CITE,
    _MARK_PY_LINE_1,
    ADDED_TEXT,
    EMPTY_PLACE,
    GAPPED_PAGE,
    REPO,
    a_binder_over,
    a_clean,
    a_correct_setting,
    a_drop,
    a_move,
    a_query,
    a_real_binder_over,
    an_add,
    an_add_at_an_empty_place,
    binder_of,
    copies_over,
    entries_of,
)

from comment_review.desk.containers import MasterProof
from comment_review.desk.determined import CHIEF, ORIGINAL, Answer
from comment_review.desk.diff_mark import COMPOSITION, QUESTION, batch_of
from comment_review.desk.mark import (
    INSTRUCTIONS,
    Instruction,
    Mark,
    Shape,
    derived_change,
)
from comment_review.flows.collate import collate
from comment_review.flows.distribute import seed
from comment_review.flows.fill import fill
from comment_review.flows.mark_errors import Revisit
from comment_review.flows.page_for import page_of
from comment_review.flows.turn import (
    batch_for,
    close,
    contracts,
    determined_chief,
    proof_after,
    refold,
    rule_at_max_turns,
    run_turn,
)

BASE = "# one\n# two\n# three\n"
TWO = "# one\n# TWO\n# three\n"
DOS = "# one\n# dos\n# three\n"
#: A composition's two sides and what they compose to, over `BASE` as a real
#: page holds it: `a_real_binder_over` strips the trailing newline.
ONE_ = "# ONE\n# two\n# three"
_THREE = "# one\n# two\n# THREE"
COMPOSED = "# ONE\n# two\n# THREE"


def _at(got, turns: int = 0) -> MasterProof:
    """The proof a fold left, standing at `turns` -- what `run_turn` reads.

    ! THE RECORD IS A PLACEHOLDER. The turn number is derived from its
    length (`MasterProof.turn`), and nothing here reads its contents.
    """
    return proof_after(got, tuple({"turn": i + 1} for i in range(turns)))


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


def _composed(root):
    """Two roles' disjoint corrects over a real page, folded into a composition."""
    binder = a_real_binder_over(root, {"m.py@b1": BASE})
    copies = copies_over(
        binder,
        {
            "block-context": {"m.py@b1": a_correct_setting("m.py@b1", 0, ONE_)},
            "function-context": {"m.py@b1": a_correct_setting("m.py@b1", 2, _THREE)},
        },
    )
    got = collate("4c", copies, binder, root=root)
    assert [e["address"] for e in got.rereads] == ["m.py@b1"]
    assert got.rereads[0]["composed"].change == COMPOSED
    return binder, copies, got


def _escalated_add():
    """Two roles' `add` marks at one EMPTY place -- `first.raw_text` is "",
    which is what leaves a `correct`-shaped recast with no false clause to
    quote."""
    binder = a_binder_over({"m.py@b1": ""})
    added_one = an_add("m.py@b1")
    added_one["change"] = "# one\n"
    added_two = an_add("m.py@b1")
    added_two["change"] = "# two\n"
    copies = copies_over(
        binder,
        {
            "block-context": {"m.py@b1": added_one},
            "function-context": {"m.py@b1": added_two},
        },
    )
    got = collate("4c", copies, binder, root=REPO)
    assert [e["address"] for e in got.rereads] == ["m.py@b1"]
    return binder, copies, got


def _patch(change: str) -> dict:
    """A `patch` mark quoting "two" -- real text in `BASE` -- with `change`
    the caller's own, so two calls can disagree on `to`."""
    return {
        "address": "m.py@b1",
        "instruction": Instruction.PATCH,
        "reason": "patch for the recast test",
        "claim": {"from": "two", "to": "TWO"},
        "change": change,
    }


def _escalated_patch():
    """Two roles' `patch` marks quoting the same sentence with different
    `change`, so the fold escalates rather than resolving to a stet."""
    binder = a_binder_over({"m.py@b1": BASE})
    copies = copies_over(
        binder,
        {
            "block-context": {"m.py@b1": _patch(TWO)},
            "function-context": {"m.py@b1": _patch(DOS)},
        },
    )
    got = collate("4c", copies, binder, root=REPO)
    assert [e["address"] for e in got.escalations] == ["m.py@b1"]
    return binder, copies, got


def _escalated_drop():
    """Two roles' `drop` marks quoting the same paragraph with different
    `change` -- one the empty edit `may_empty` allows, one not -- so the
    fold escalates rather than resolving to a stet."""
    binder = a_binder_over({"m.py@b1": BASE})
    copies = copies_over(
        binder,
        {
            "block-context": {"m.py@b1": {**a_drop("m.py@b1"), "change": ""}},
            "function-context": {
                "m.py@b1": {**a_drop("m.py@b1"), "change": "# leftover\n"}
            },
        },
    )
    got = collate("4c", copies, binder, root=REPO)
    assert [e["address"] for e in got.escalations] == ["m.py@b1"]
    return binder, copies, got


def _escalated_move():
    """Two roles' `move` marks off one origin to different destinations.
    `move` quotes no sentence, so `_outcome` sends it to a re-read rather
    than an escalation, and `_join_moves` carries every end of either move
    to that same outcome -- the origin is carried forward alongside both
    destinations."""
    binder = a_binder_over({"m.py@b1": BASE})
    copies = copies_over(
        binder,
        {
            "block-context": {
                "m.py@b1": {**a_move("m.py@b1", "n.py@c1"), "change": TWO}
            },
            "function-context": {
                "m.py@b1": {**a_move("m.py@b1", "o.py@c1"), "change": DOS}
            },
        },
    )
    got = collate("4c", copies, binder, root=REPO)
    assert "m.py@b1" in [e["address"] for e in got.rereads]
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
        again = run_turn(_at(got), binder, REPO, batch, answers)
        problems = again.revisit
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
        final = run_turn(_at(again, 1), binder, REPO, batch2, answers2)
        assert final.revisit == []
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
        again = run_turn(_at(got), binder, REPO, batch, answers)
        problems = again.revisit
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
        again = run_turn(_at(got), binder, REPO, batch, answers)
        problems = again.revisit
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
        again = run_turn(_at(got), binder, REPO, batch, answers)
        problems = again.revisit
        assert any("unanswered" in r for p in problems for r in p.reasons)
        assert [e["address"] for e in again.escalations] == ["m.py@b1"]


class TestAnEscalationAnswerDerivesItsChange:
    """`no-command-for-the-middle` T40: an escalation's `correct` or `patch`
    answer replaces the role's own proposal, so its claim quotes that proposal
    and derives the answer's `change` the way `desk.mark.derived_change`
    relates a claim to its change. The fold checks the quote against the
    proposal the batch sent the role (`Process: #119`)."""

    @pytest.mark.parametrize("instruction", [Instruction.CORRECT, Instruction.PATCH])
    def test_the_claim_quotes_the_roles_own_proposal(self, tmp_path, instruction):
        def filed(change: str) -> dict:
            if instruction is Instruction.CORRECT:
                return a_correct_setting("m.py@b1", "two", change)
            return _patch(change)

        binder = a_real_binder_over(tmp_path, {"m.py@b1": BASE})
        copies = copies_over(
            binder,
            {
                "block-context": {"m.py@b1": filed(TWO)},
                "function-context": {"m.py@b1": filed(DOS)},
            },
        )
        got = collate("4c", copies, binder, root=tmp_path)
        assert [e["address"] for e in got.escalations] == ["m.py@b1"]
        batch = batch_of(got.escalations, got.rereads)
        answers = {
            **_answered(
                batch,
                "block-context",
                instruction=str(instruction),
                reason="theirs reads better",
                change=DOS,
            ),
            **_answered(batch, "function-context", instruction="hold", reason="mine"),
        }
        again = run_turn(_at(got), binder, tmp_path, batch, answers)
        assert again.revisit == []
        assert [p for p in again.problems if p.address == "m.py@b1"] == []
        (held,) = _held_at(again, "block-context", "m.py@b1")
        assert held.claim[INSTRUCTIONS[instruction].quotes_original] == TWO
        assert derived_change(instruction, held.claim, TWO) == (DOS, [])


class TestAnAnswerThatStillDisagrees:
    """`no-command-for-the-middle` T54, `Process: #127`: after a turn, a place
    the turn asked about whose roles still hold different texts is an
    escalation."""

    def test_a_correct_to_a_new_text_beside_a_hold_stays_an_escalation(self, tmp_path):
        binder = a_real_binder_over(tmp_path, {"m.py@b1": BASE})
        copies = copies_over(
            binder,
            {
                "block-context": {"m.py@b1": a_correct_setting("m.py@b1", "two", TWO)},
                "function-context": {
                    "m.py@b1": a_correct_setting("m.py@b1", "two", DOS)
                },
            },
        )
        got = collate("4c", copies, binder, root=tmp_path)
        assert [e["address"] for e in got.escalations] == ["m.py@b1"]
        batch = batch_of(got.escalations, got.rereads)
        tres = "# one\n# tres\n# three\n"
        answers = {
            **_answered(
                batch,
                "block-context",
                instruction="correct",
                reason="neither reading holds",
                change=tres,
            ),
            **_answered(batch, "function-context", instruction="hold", reason="mine"),
        }
        again = run_turn(_at(got), binder, tmp_path, batch, answers)
        assert again.revisit == []
        assert [p for p in again.problems if p.address == "m.py@b1"] == []
        assert again.rereads == []
        assert [e["address"] for e in again.escalations] == ["m.py@b1"]
        assert {p.mark.change for p in again.escalations[0]["marks"]} == {tres, DOS}


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
        again = run_turn(_at(got), binder, REPO, batch, answers)
        problems = again.revisit
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
        problems = run_turn(_at(got), binder, REPO, batch, answers).revisit
        assert any(
            p.address == "m.py@b9" and "never sent" in r
            for p in problems
            for r in p.reasons
        )

    def test_a_sent_slot_left_out_of_the_answer_is_unanswered(self):
        binder, copies, got = _escalated()
        batch = batch_of(got.escalations, got.rereads)
        answers = {
            "block-context": [],
            **_answered(batch, "function-context", instruction="hold", reason="stands"),
        }
        problems = run_turn(_at(got), binder, REPO, batch, answers).revisit
        assert any(
            p.address == "m.py@b1" and "unanswered" in r
            for p in problems
            for r in p.reasons
        )


class TestAComposition:
    def test_the_composed_text_goes_back_as_a_marks_question(self, tmp_path):
        _, _, got = _composed(tmp_path)
        batch = batch_of(got.escalations, got.rereads)
        slot = batch["block-context"][0]
        assert slot[QUESTION] == COMPOSITION
        assert slot["raw_text"] == COMPOSED
        assert slot["composed"] is True
        assert slot["instruction"] is None
        assert entries_of(got.chief) == []

    def test_every_role_clean_on_it_is_a_stet_carrying_the_composition(self, tmp_path):
        binder, copies, got = _composed(tmp_path)
        batch = batch_of(got.escalations, got.rereads)
        answers = {
            **_answered(batch, "block-context", instruction="clean"),
            **_answered(batch, "function-context", instruction="clean"),
        }
        again = run_turn(_at(got), binder, tmp_path, batch, answers)
        problems = again.revisit
        assert problems == []
        assert again.rereads == []
        ruled = again.determined["m.py@b1"]
        assert ruled.answer is Answer.STET
        assert ruled.how == "identical"
        assert [m.change for m in entries_of(again.chief)] == [COMPOSED]

    def test_a_correct_over_it_beside_a_clean_adoption_is_an_escalation(self, tmp_path):
        """`Process: #124`: the adopting role holds the composed text and this
        role its own correct of it, so two roles hold different texts at one
        place, and the place is an escalation carrying both."""
        binder, copies, got = _composed(tmp_path)
        batch = batch_of(got.escalations, got.rereads)
        fixed = "# ONE\n# two\n# 3"
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
        again = run_turn(_at(got), binder, tmp_path, batch, answers)
        problems = again.revisit
        assert problems == []
        assert [e["address"] for e in again.escalations] == ["m.py@b1"]
        assert again.determined == {}
        assert {p.mark.change for p in again.escalations[0]["marks"]} == {
            COMPOSED,
            fixed,
        }

    def test_a_patch_over_it_stays_a_patch_and_the_role_stays_in_the_fold(
        self, tmp_path
    ):
        """MEASURED in the game's hand 2: a patch answer was rewritten as a
        `correct`, which owes sources a patch never carried, and the role's
        entry was refused at the fold -- the role vanished from the escalation."""
        binder, copies, got = _composed(tmp_path)
        batch = batch_of(got.escalations, got.rereads)
        worded = "# ONE\n# two\n# three!"
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
        again = run_turn(_at(got), binder, tmp_path, batch, answers)
        problems = again.revisit
        assert problems == []
        assert again.revisit == []
        assert [e["address"] for e in again.escalations] == ["m.py@b1"]
        roles = {p.role for p in again.escalations[0]["marks"]}
        assert roles == {"block-context", "function-context"}

    def test_a_drop_is_not_a_composition_answer(self, tmp_path):
        binder, copies, got = _composed(tmp_path)
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
        problems = run_turn(_at(got), binder, tmp_path, batch, answers).revisit
        assert any("not a composition answer" in r for p in problems for r in p.reasons)


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
        again = run_turn(_at(got), binder, REPO, batch, answers)
        problems = again.revisit
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
        again = run_turn(_at(got), binder, REPO, batch, answers)
        problems = again.revisit
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
        again = run_turn(_at(got), binder, REPO, batch, answers)
        assert "m.py@b1" in again.determined


#: A composition `query`, citing a line `GAPPED_PAGE` holds.
_A_QUERY = {
    "instruction": "query",
    "reason": "the added sentence names a value this role does not rule on",
    "claim": {
        "shape": Shape.UNABLE_TO_DETERMINE,
        "attempted": "read the added sentence against the line below it",
        "settles": "block-context, which made the add",
    },
    "sources": [{"cite": "m.py:7", "verbatim": "w = 4"}],
}


def _held_at(got, role: str, address: str) -> list[Mark]:
    assert got.proof is not None
    return [
        mark
        for copy in got.proof.edit_copies
        if copy.role == role
        for mark in entries_of(copy)
        if mark.address == address
    ]


class TestAnAddAtAnEmptyPlace:
    """An `add` at an empty place is re-read by every role of the stage, and
    only the adding role's copy holds a slot there --
    `no-command-for-the-middle` T29, T30 and T37."""

    def test_a_role_with_no_slot_there_is_seeded_one_from_the_page(self, tmp_path):
        binder, got = an_add_at_an_empty_place(tmp_path)
        batch = batch_of(got.escalations, got.rereads)
        answers = {
            **_answered(batch, "block-context", instruction="clean"),
            **_answered(batch, "function-context", **_A_QUERY),
        }
        again = run_turn(_at(got), binder, tmp_path, batch, answers)
        assert [p for p in again.revisit if p.role == "function-context"] == []
        page, _ = page_of(tmp_path / "m.py", rel="m.py")
        assert page is not None
        (held,) = _held_at(again, "function-context", EMPTY_PLACE)
        assert held.instruction is Instruction.QUERY
        assert held.anchor == page.cues.anchor_of("b3")
        assert held.raw_text == ""

    def test_every_role_clean_there_settles_the_add(self, tmp_path):
        """`Process: #116`: every other role's `clean` at an add's empty
        place is agreement. The other role adopts the add, and the place is a
        `stet` at this turn carrying the add's text to the chief's copy."""
        binder, got = an_add_at_an_empty_place(tmp_path)
        batch = batch_of(got.escalations, got.rereads)
        answers = {r: [{**batch[r][0], "instruction": "clean"}] for r in batch}
        again = run_turn(_at(got), binder, tmp_path, batch, answers)
        assert again.revisit == []
        assert again.problems == []
        assert again.rereads == [] and again.escalations == []
        held = _held_at(again, "function-context", EMPTY_PLACE)
        assert [(m.instruction, m.change) for m in held] == [
            (Instruction.ADD, ADDED_TEXT)
        ]
        ruled = again.determined[EMPTY_PLACE]
        assert (ruled.answer, ruled.turn, ruled.how) == (Answer.STET, 1, "identical")
        assert [(m.instruction, m.change) for m in entries_of(again.chief)] == [
            (Instruction.ADD, ADDED_TEXT)
        ]

    def test_a_place_the_page_does_not_carry_is_still_refused(self, tmp_path):
        binder, got = an_add_at_an_empty_place(tmp_path)
        batch = batch_of(got.escalations, got.rereads)
        # Malformed is the input: a sent slot naming a cue `m.py` does not have.
        stray = {**batch["function-context"][0], "address": "m.py@b9999"}
        sent = {**batch, "function-context": [*batch["function-context"], stray]}
        answers = {
            **_answered(batch, "block-context", instruction="clean"),
            "function-context": [
                {**slot, **_A_QUERY} for slot in sent["function-context"]
            ],
        }
        again = run_turn(_at(got), binder, tmp_path, sent, answers)
        refused = [p for p in again.revisit if p.address == "m.py@b9999"]
        assert [(p.role, p.unreadable) for p in refused] == [("function-context", True)]
        assert any("names no place on that page" in r for r in refused[0].reasons)
        assert _held_at(again, "function-context", "m.py@b9999") == []

    def test_a_place_the_batch_did_not_send_to_that_role_is_still_refused(
        self, tmp_path
    ):
        binder, got = an_add_at_an_empty_place(tmp_path)
        batch = batch_of(got.escalations, got.rereads)
        # Malformed is the input: the batch withholds the place from one role.
        sent = {**batch, "function-context": []}
        answers = {
            **_answered(batch, "block-context", instruction="clean"),
            **_answered(batch, "function-context", **_A_QUERY),
        }
        again = run_turn(_at(got), binder, tmp_path, sent, answers)
        refused = [p for p in again.revisit if p.role == "function-context"]
        assert [p.address for p in refused] == [EMPTY_PLACE]
        assert any("never sent" in r for r in refused[0].reasons)
        assert _held_at(again, "function-context", EMPTY_PLACE) == []

    @pytest.mark.parametrize(
        "answer",
        [
            pytest.param(
                {
                    "instruction": "correct",
                    "reason": "four is the word the rest of the fixture uses",
                    "claim": {"false": "w is 4", "true": "w is four"},
                    "sources": [{"cite": "m.py:7", "verbatim": "w = 4"}],
                    "change": ADDED_TEXT.replace("w is 4", "w is four"),
                },
                id="correct",
            ),
            pytest.param(
                {
                    "instruction": "patch",
                    "reason": "four is the word the rest of the fixture uses",
                    "claim": {"from": "w is 4", "to": "w is four"},
                    "change": ADDED_TEXT.replace("w is 4", "w is four"),
                },
                id="patch",
            ),
        ],
    )
    def test_a_correct_or_patch_quotes_the_text_it_was_sent(self, tmp_path, answer):
        """`no-command-for-the-middle` T34, `Process: #115`: a composition
        `correct` or `patch` is made against the slot's text -- here the add's,
        where the original holds nothing. It lands on the role's copy as the
        role gave it, and the fold checks its quote against the text sent."""
        binder, got = an_add_at_an_empty_place(tmp_path)
        batch = batch_of(got.escalations, got.rereads)
        assert _slot(batch, "function-context", EMPTY_PLACE)["raw_text"] == ADDED_TEXT
        answers = {
            **_answered(batch, "block-context", instruction="clean"),
            **_answered(batch, "function-context", **answer),
        }
        again = run_turn(_at(got), binder, tmp_path, batch, answers)
        assert again.revisit == []
        assert [p for p in again.problems if p.address == EMPTY_PLACE] == []
        (held,) = _held_at(again, "function-context", EMPTY_PLACE)
        assert held.instruction is Instruction(answer["instruction"])
        assert held.claim == answer["claim"]


class TestRefold:
    """`no-command-for-the-middle` T55, `Process: #127`: `refold` re-derives
    the fold at the turn the proof stands at, so a place the last turn left
    escalated is an escalation there as well."""

    def test_a_place_the_turn_escalated_is_an_escalation_again(self, tmp_path):
        binder, got = an_add_at_an_empty_place(tmp_path)
        batch = batch_of(got.escalations, got.rereads)
        answers = {
            **_answered(batch, "block-context", instruction="clean"),
            **_answered(
                batch,
                "function-context",
                instruction="patch",
                reason="four is the word the rest of the fixture uses",
                claim={"from": "w is 4", "to": "w is four"},
                change=ADDED_TEXT.replace("w is 4", "w is four"),
            ),
        }
        again = run_turn(_at(got), binder, tmp_path, batch, answers)
        assert again.revisit == []
        assert [e["address"] for e in again.escalations] == [EMPTY_PLACE]
        # The proof as `commands/turn.py` writes it and `disposition` reads it.
        wire = proof_after(again, ({"turn": 1, "sent": batch},)).serialize()
        proof, why = MasterProof.deserialize("turn 1", wire)
        assert proof is not None, why
        refolded = refold(proof, binder, tmp_path)
        assert [p for p in refolded.problems if p.address == EMPTY_PLACE] == []
        assert refolded.rereads == []
        assert [e["address"] for e in refolded.escalations] == [EMPTY_PLACE]


#: `GAPPED_PAGE`'s one filled place, the comment above `y = 2`.
MOVED_FROM = "m.py@b1"
MOVED_TEXT = "# one\n# two\n# three"


def _a_lone_move(root, change: str):
    """block-context moves `MOVED_FROM` to `EMPTY_PLACE` carrying `change`,
    function-context cleans `MOVED_FROM`, and `collate` folds the two.

    Both marks are placed by `fill` on copies seeded from a binder over the
    real page `GAPPED_PAGE`, as the `mark` command places them.
    """
    (root / "m.py").write_text(GAPPED_PAGE, encoding="utf-8")
    binder = binder_of(root, 0)
    copies = [seed(binder, role) for role in ("block-context", "function-context")]
    moved = {
        "address": MOVED_FROM,
        "instruction": "move",
        "claim": {"from": MOVED_FROM, "to": EMPTY_PLACE},
        "reason": "the comment is about w, not y",
        "sources": [{"cite": "m.py:7"}],
        "change": change,
    }
    _, why = fill(copies[0], moved, root)
    assert why == []
    _, why = fill(copies[1], {"address": MOVED_FROM, "instruction": "clean"}, root)
    assert why == []
    return binder, collate("4c", copies, binder, root=root)


class TestAMoversOwnClean:
    """A mover's own `clean` at its move's origin -- `no-command-for-the-middle`
    T43.

    A lone `move` with another role marking its origin goes back to both roles
    as a re-read at each end, and the origin's slot carries the move's own
    text. The mover answering `clean` there agrees with its own move, so after
    the turn it still holds that move.
    """

    @pytest.mark.parametrize(
        "change",
        [
            pytest.param(MOVED_TEXT, id="moved-as-it-stands"),
            pytest.param(MOVED_TEXT + ", which is about w", id="moved-reworded"),
        ],
    )
    def test_it_keeps_the_move(self, tmp_path, change):
        binder, got = _a_lone_move(tmp_path, change)
        assert sorted(e["address"] for e in got.rereads) == [MOVED_FROM, EMPTY_PLACE]
        batch = batch_of(got.escalations, got.rereads)
        assert _slot(batch, "block-context", MOVED_FROM)["raw_text"] == change
        answers = {
            role: [{**slot, "instruction": "clean"} for slot in slots]
            for role, slots in batch.items()
        }
        again = run_turn(_at(got), binder, tmp_path, batch, answers)
        (held,) = _held_at(again, "block-context", MOVED_FROM)
        assert held.instruction is Instruction.MOVE
        assert held.claim["to"] == EMPTY_PLACE


class TestAMoveWhoseEndsStillDisagree:
    """A move whose other end escalates -- `no-command-for-the-middle` T33.

    On turn 1 the other role patches the moved text at the move's origin, so
    both ends of the move hold two texts and `_disagreeing` escalates both
    (`Process: #127`). On turn 2 the mover answers its origin's escalation
    with a `correct`: that changes the moved text, the entry's `change`, and
    the destination stays where the mover put it.
    """

    def test_a_correct_changes_the_moved_text_and_keeps_the_destination(self, tmp_path):
        binder, got = _a_lone_move(tmp_path, MOVED_TEXT)
        batch = batch_of(got.escalations, got.rereads)
        patched = {
            "instruction": "patch",
            "claim": {"from": "two", "to": "TWO"},
            "reason": "the fixture spells its numbers in capitals",
            "change": MOVED_TEXT.replace("two", "TWO"),
        }
        answers = {
            role: [
                {**slot, **patched}
                if (role, slot["address"]) == ("function-context", MOVED_FROM)
                else {**slot, "instruction": "clean"}
                for slot in slots
            ]
            for role, slots in batch.items()
        }
        one = run_turn(_at(got), binder, tmp_path, batch, answers)
        assert one.revisit == []
        assert one.rereads == []
        assert sorted(e["address"] for e in one.escalations) == [
            MOVED_FROM,
            EMPTY_PLACE,
        ]

        batch2 = batch_of(one.escalations, one.rereads)
        moved_again = MOVED_TEXT.replace("two", "2")
        answers2 = {
            role: [
                {
                    **slot,
                    "instruction": "correct",
                    "reason": "a digit reads as the count it is",
                    "change": moved_again,
                }
                if (role, slot["address"]) == ("block-context", MOVED_FROM)
                else {**slot, "instruction": "hold", "reason": "mine stands"}
                for slot in slots
            ]
            for role, slots in batch2.items()
        }
        # The record carries what turn 1 sent, as `commands/turn.py` writes it.
        proof = proof_after(one, ({"turn": 1, "sent": batch},))
        two = run_turn(proof, binder, tmp_path, batch2, answers2)
        assert two.revisit == []
        (held,) = _held_at(two, "block-context", MOVED_FROM)
        assert held.instruction is Instruction.MOVE
        assert held.change == moved_again
        assert held.claim == {"from": MOVED_FROM, "to": EMPTY_PLACE}
        assert sorted(e["address"] for e in two.escalations) == [
            MOVED_FROM,
            EMPTY_PLACE,
        ]


def _the_mover_answers_at_the_destination(root, answer: dict, change: str = MOVED_TEXT):
    """Two real turns over `_a_lone_move` carrying `change`, the second
    answered by the mover at its move's destination end.

    Turn 1: function-context patches the moved text at the move's origin and
    every other slot is `clean` -- the mover's at `EMPTY_PLACE` among them --
    so both ends of the move escalate (`Process: #127`). Turn 2:
    block-context gives `answer` at `EMPTY_PLACE` and every other slot holds.

    Returns:
        The fold after turn 2.
    """
    binder, got = _a_lone_move(root, change)
    batch = batch_of(got.escalations, got.rereads)
    patched = {
        "instruction": "patch",
        "claim": {"from": "two", "to": "TWO"},
        "reason": "the fixture spells its numbers in capitals",
        "change": change.replace("two", "TWO"),
    }
    answers = {
        role: [
            {**slot, **patched}
            if (role, slot["address"]) == ("function-context", MOVED_FROM)
            else {**slot, "instruction": "clean"}
            for slot in slots
        ]
        for role, slots in batch.items()
    }
    one = run_turn(_at(got), binder, root, batch, answers)
    assert one.revisit == []
    assert sorted(e["address"] for e in one.escalations) == [
        MOVED_FROM,
        EMPTY_PLACE,
    ]

    batch2 = batch_of(one.escalations, one.rereads)
    answers2 = {
        role: [
            {**slot, **answer}
            if (role, slot["address"]) == ("block-context", EMPTY_PLACE)
            else {**slot, "instruction": "hold", "reason": "mine stands"}
            for slot in slots
        ]
        for role, slots in batch2.items()
    }
    proof = proof_after(one, ({"turn": 1, "sent": batch},))
    return run_turn(proof, binder, root, batch2, answers2)


class TestAMoversAnswerAtItsDestination:
    """A mover's answer at its move's destination end --
    `no-command-for-the-middle` T57 and T61, `Process: #129`.

    Turn 1 leaves both ends of a move escalated, as in T33's case. On turn 2
    the mover answers the escalation at the destination end, and the answer
    reaches the move at the origin. Neither turn writes a slot of the
    mover's at the destination: turn 1's `clean` there reaches the move too
    (`Process: #138`).
    """

    def test_the_answer_changes_the_moved_text(self, tmp_path):
        moved_again = MOVED_TEXT.replace("two", "2")
        two = _the_mover_answers_at_the_destination(
            tmp_path,
            {
                "instruction": "correct",
                "reason": "a digit reads as the count it is",
                "change": moved_again,
            },
        )
        assert two.revisit == []
        (held,) = _held_at(two, "block-context", MOVED_FROM)
        assert held.instruction is Instruction.MOVE
        assert held.change == moved_again
        assert held.claim == {"from": MOVED_FROM, "to": EMPTY_PLACE}
        assert _held_at(two, "block-context", EMPTY_PLACE) == []

    def test_a_withdraw_withdraws_the_move(self, tmp_path):
        two = _the_mover_answers_at_the_destination(
            tmp_path,
            {"instruction": "withdraw", "reason": "the comment is about y after all"},
        )
        assert two.revisit == []
        (held,) = _held_at(two, "block-context", MOVED_FROM)
        assert held.instruction is Instruction.CLEAN
        assert _held_at(two, "block-context", EMPTY_PLACE) == []


class TestAMoversCleanAtItsDestination:
    """A mover's composition `clean` at its move's destination end --
    `no-command-for-the-middle` T71, `Process: #138`.

    Turn 1 of `_the_mover_answers_at_the_destination` answers the mover's
    slot at `EMPTY_PLACE` with `clean`. That slot carries the origin's text
    as the page holds it, not the moved text, so the composition table would
    read the `clean` as a withdrawal. It reaches the move instead, leaves it
    as it stands, and writes no slot of the mover's at the destination.
    Turn 2 holds.
    """

    @pytest.mark.parametrize(
        "change",
        [
            pytest.param(MOVED_TEXT, id="moved-as-it-stands"),
            pytest.param(MOVED_TEXT + ", which is about w", id="moved-reworded"),
        ],
    )
    def test_it_keeps_the_move(self, tmp_path, change):
        two = _the_mover_answers_at_the_destination(
            tmp_path, {"instruction": "hold", "reason": "mine stands"}, change
        )
        assert two.revisit == []
        (held,) = _held_at(two, "block-context", MOVED_FROM)
        assert held.instruction is Instruction.MOVE
        assert held.change == change
        assert held.claim == {"from": MOVED_FROM, "to": EMPTY_PLACE}
        assert _held_at(two, "block-context", EMPTY_PLACE) == []


def _clean_but(batch: dict, role: str, address: str, answer: dict) -> dict:
    """Every slot of `batch` answered `clean`, but `role`'s at `address`,
    which is answered with `answer`."""
    return {
        who: [
            {**slot, **answer}
            if (who, slot["address"]) == (role, address)
            else {**slot, "instruction": "clean"}
            for slot in slots
        ]
        for who, slots in batch.items()
    }


def _clean_but_the_destination(batch: dict, answer: dict) -> dict:
    """`_clean_but`, answering block-context's slot at `EMPTY_PLACE`."""
    return _clean_but(batch, "block-context", EMPTY_PLACE, answer)


#: A mover's composition answers at its move's destination, each over the
#: text the slot there carries.
_A_COMPOSITION_CORRECT = {
    "instruction": "correct",
    "claim": {"false": "# two", "true": "# 2"},
    "reason": "a digit reads as the count it is",
    "sources": [{"cite": "m.py:7", "verbatim": "w = 4"}],
    "change": MOVED_TEXT.replace("two", "2"),
}
_A_COMPOSITION_PATCH = {
    "instruction": "patch",
    "claim": {"from": "two", "to": "2"},
    "reason": "a digit reads as the count it is",
    "change": MOVED_TEXT.replace("two", "2"),
}


class TestAMoversCompositionAnswerAtItsDestination:
    """A mover's composition answer at its move's destination end --
    `no-command-for-the-middle` T69, `Process: #129` and `#137`.

    `_a_lone_move` sends both ends of the move back as re-reads, and the
    destination only to the mover. A `correct` or `patch` there sets the
    move's text at the origin, the destination staying where the mover put
    it, and writes no slot of the mover's at the destination.
    """

    @pytest.mark.parametrize(
        "answer",
        [
            pytest.param(_A_COMPOSITION_CORRECT, id="correct"),
            pytest.param(_A_COMPOSITION_PATCH, id="patch"),
        ],
    )
    def test_it_sets_the_moved_text(self, tmp_path, answer):
        binder, got = _a_lone_move(tmp_path, MOVED_TEXT)
        batch = batch_of(got.escalations, got.rereads)
        assert _slot(batch, "block-context", EMPTY_PLACE)[QUESTION] == COMPOSITION
        one = run_turn(
            _at(got), binder, tmp_path, batch, _clean_but_the_destination(batch, answer)
        )
        assert one.revisit == []
        assert one.problems == []
        (held,) = _held_at(one, "block-context", MOVED_FROM)
        assert held.instruction is Instruction.MOVE
        assert held.change == answer["change"]
        assert held.claim == {"from": MOVED_FROM, "to": EMPTY_PLACE}
        assert _held_at(one, "block-context", EMPTY_PLACE) == []

    def test_it_follows_the_movers_clean_there(self, tmp_path):
        """Turn 1's `clean` at the destination writes no slot there
        (`Process: #138`). Turn 2's `correct` there still sets the move's
        text, and writes none either.

        On turn 1 function-context leaves its slot at the origin unanswered.
        An unanswered slot is not agreement, so the move is carried to turn 2
        rather than settled by every role's `clean` (`Process: #89`).
        """
        binder, got = _a_lone_move(tmp_path, MOVED_TEXT)
        batch = batch_of(got.escalations, got.rereads)
        answers = _clean_but_the_destination(batch, {"instruction": "clean"})
        answers["function-context"] = []
        one = run_turn(_at(got), binder, tmp_path, batch, answers)
        assert [(r.role, r.address) for r in one.revisit] == [
            ("function-context", MOVED_FROM)
        ]
        assert _held_at(one, "block-context", EMPTY_PLACE) == []

        batch2 = batch_of(one.escalations, one.rereads)
        proof = proof_after(one, ({"turn": 1, "sent": batch},))
        two = run_turn(
            proof,
            binder,
            tmp_path,
            batch2,
            _clean_but_the_destination(batch2, _A_COMPOSITION_CORRECT),
        )
        assert two.revisit == []
        (held,) = _held_at(two, "block-context", MOVED_FROM)
        assert held.instruction is Instruction.MOVE
        assert held.change == _A_COMPOSITION_CORRECT["change"]
        assert held.claim == {"from": MOVED_FROM, "to": EMPTY_PLACE}
        assert _held_at(two, "block-context", EMPTY_PLACE) == []


def _a_movers_query(shape: Shape) -> dict:
    """The mover's composition `query` at its move's destination, in `shape`."""
    return {
        "instruction": "query",
        "reason": "whether the comment belongs above w is not this role's to say",
        "claim": {
            "shape": shape,
            "attempted": "read the moved comment against the line below the place",
            "settles": "whoever rules on where the comment sits",
        },
        "sources": [{"cite": "m.py:7", "verbatim": "w = 4"}],
    }


class TestAMoversQueryAtItsDestination:
    """A mover's composition `query` at its move's destination end --
    `no-command-for-the-middle` T72, `Process: #138` and `#90`.

    The query is written to the mover's slot at `EMPTY_PLACE` and the move
    stays. It is filed against the move, so it stands at both ends: a
    `human-review-necessary` query holds both for the human, and a deferring
    query takes the mover out of the roles at both.
    """

    def test_a_human_review_query_holds_both_ends(self, tmp_path):
        binder, got = _a_lone_move(tmp_path, MOVED_TEXT)
        batch = batch_of(got.escalations, got.rereads)
        asked = _a_movers_query(Shape.HUMAN_REVIEW_NECESSARY)
        one = run_turn(
            _at(got), binder, tmp_path, batch, _clean_but_the_destination(batch, asked)
        )
        assert one.revisit == []
        assert one.problems == []
        (held,) = _held_at(one, "block-context", MOVED_FROM)
        assert (held.instruction, held.change) == (Instruction.MOVE, MOVED_TEXT)
        assert sorted(u["address"] for u in one.unsettlable) == [
            MOVED_FROM,
            EMPTY_PLACE,
        ]
        carried = {e["address"] for e in (*one.escalations, *one.rereads)}
        assert carried.isdisjoint({MOVED_FROM, EMPTY_PLACE})
        assert one.determined.keys().isdisjoint({MOVED_FROM, EMPTY_PLACE})

    @pytest.mark.parametrize(
        "shape", [Shape.OUTSIDE_MY_ROLE, Shape.UNABLE_TO_DETERMINE]
    )
    def test_a_deferring_query_abstains_at_both_ends(self, tmp_path, shape):
        binder, got = _a_lone_move(tmp_path, MOVED_TEXT)
        batch = batch_of(got.escalations, got.rereads)
        one = run_turn(
            _at(got),
            binder,
            tmp_path,
            batch,
            _clean_but_the_destination(batch, _a_movers_query(shape)),
        )
        assert one.revisit == []
        assert one.problems == []
        (held,) = _held_at(one, "block-context", MOVED_FROM)
        assert (held.instruction, held.change) == (Instruction.MOVE, MOVED_TEXT)
        assert one.unsettlable == []
        ends = {
            e["address"]: e["roles"]
            for e in (*one.escalations, *one.rereads)
            if e["address"] in (MOVED_FROM, EMPTY_PLACE)
        }
        assert sorted(ends) == [MOVED_FROM, EMPTY_PLACE]
        assert all("block-context" not in roles for roles in ends.values())
        assert "function-context" in ends[MOVED_FROM]


class TestAMoversCompositionAnswerAtItsOrigin:
    """A mover's composition `correct` or `patch` at its move's origin --
    `no-command-for-the-middle` T73, `Process: #137`.

    `_a_lone_move` sends the origin back to the mover as a re-read carrying
    the moved text. The mover answers it with a `correct` or a `patch`, and
    every other slot is `clean`. The test settles whether the mover still
    holds its move there afterwards, its claim naming both ends.
    """

    @pytest.mark.parametrize(
        "answer",
        [
            pytest.param(_A_COMPOSITION_CORRECT, id="correct"),
            pytest.param(_A_COMPOSITION_PATCH, id="patch"),
        ],
    )
    def test_the_move_survives(self, tmp_path, answer):
        binder, got = _a_lone_move(tmp_path, MOVED_TEXT)
        batch = batch_of(got.escalations, got.rereads)
        assert _slot(batch, "block-context", MOVED_FROM)[QUESTION] == COMPOSITION
        one = run_turn(
            _at(got),
            binder,
            tmp_path,
            batch,
            _clean_but(batch, "block-context", MOVED_FROM, answer),
        )
        assert one.revisit == []
        (held,) = _held_at(one, "block-context", MOVED_FROM)
        assert held.instruction is Instruction.MOVE
        assert held.change == answer["change"]
        assert held.claim == {"from": MOVED_FROM, "to": EMPTY_PLACE}


class TestEveryRoleCleansAMoveAsItStands:
    """Every role's `clean` over a lone move whose text is unchanged --
    `no-command-for-the-middle` T74, `Process: #89`.

    `_a_lone_move` carries the origin's text as it stands, and turn 1
    answers every slot `clean`, as T43's test does. Every role that marked
    the place has then agreed with the move's text, which `#89` says makes
    it a `stet`: the test asserts both ends are determined, each carrying
    the move.
    """

    def test_both_ends_settle_carrying_the_move(self, tmp_path):
        binder, got = _a_lone_move(tmp_path, MOVED_TEXT)
        batch = batch_of(got.escalations, got.rereads)
        answers = {
            role: [{**slot, "instruction": "clean"} for slot in slots]
            for role, slots in batch.items()
        }
        one = run_turn(_at(got), binder, tmp_path, batch, answers)
        assert one.revisit == []
        assert {MOVED_FROM, EMPTY_PLACE} <= one.determined.keys()
        for address in (MOVED_FROM, EMPTY_PLACE):
            ruled = one.determined[address]
            assert ruled.answer is Answer.STET
            assert ruled.mark is not None
            assert ruled.mark.instruction is Instruction.MOVE


class TestAMovesEndsDisagreeAfterATurn:
    """A move whose two ends hold different texts after a turn --
    `no-command-for-the-middle` T75, `Process: #127` and `#137`.

    `_a_lone_move` carries the moved text reworded. Turn 1 answers every
    slot `clean`, so function-context adopts the moved text at the origin
    and both ends go back to both roles as re-reads. On turn 2 the mover
    leaves the origin unanswered and cleans the destination, while
    function-context restates the moved text at the origin and corrects the
    destination to another text. The test asserts both ends of the move are
    in one carried list.
    """

    def test_both_ends_are_in_one_carried_list(self, tmp_path):
        reworded = MOVED_TEXT + ", which is about w"
        binder, got = _a_lone_move(tmp_path, reworded)
        batch = batch_of(got.escalations, got.rereads)
        answers = {
            role: [{**slot, "instruction": "clean"} for slot in slots]
            for role, slots in batch.items()
        }
        one = run_turn(_at(got), binder, tmp_path, batch, answers)
        assert one.revisit == []

        batch2 = batch_of(one.escalations, one.rereads)
        restated = {
            "instruction": "correct",
            "claim": {"false": "# three", "true": "# three, which is about w"},
            "reason": "the comment is about w",
            "sources": [{"cite": "m.py:7", "verbatim": "w = 4"}],
            "change": reworded,
        }
        answers2 = {
            "block-context": [
                {**slot, "instruction": "clean"}
                for slot in batch2["block-context"]
                if slot["address"] == EMPTY_PLACE
            ],
            "function-context": [
                {
                    **slot,
                    **(
                        restated
                        if slot["address"] == MOVED_FROM
                        else _A_COMPOSITION_CORRECT
                    ),
                }
                for slot in batch2["function-context"]
            ],
        }
        proof = proof_after(one, ({"turn": 1, "sent": batch},))
        two = run_turn(proof, binder, tmp_path, batch2, answers2)
        assert [(r.role, r.address) for r in two.revisit] == [
            ("block-context", MOVED_FROM)
        ]
        (held,) = _held_at(two, "block-context", MOVED_FROM)
        assert held.instruction is Instruction.MOVE
        escalated = {e["address"] for e in two.escalations}
        reread = {e["address"] for e in two.rereads}
        assert {MOVED_FROM, EMPTY_PLACE} <= escalated | reread
        assert (MOVED_FROM in escalated) == (EMPTY_PLACE in escalated)


class TestAMovesEndsResolveTogether:
    """Both ends of a move resolve together over the turn --
    `no-command-for-the-middle` T69, `Process: #137`.

    Turn 1 is T33's: function-context patches the moved text at the origin,
    so both ends escalate. On turn 2 function-context withdraws its patch and
    every other slot holds. The destination then carries the move alone and
    no other role marked it, which by itself stands as a `stet`, while the
    origin carries the move beside function-context's `clean` and goes back
    as a re-read. Neither end is determined, and both are carried.
    """

    def test_an_end_that_would_stand_alone_is_carried_with_the_other(self, tmp_path):
        binder, got = _a_lone_move(tmp_path, MOVED_TEXT)
        batch = batch_of(got.escalations, got.rereads)
        patched = {
            "instruction": "patch",
            "claim": {"from": "two", "to": "TWO"},
            "reason": "the fixture spells its numbers in capitals",
            "change": MOVED_TEXT.replace("two", "TWO"),
        }
        answers = {
            role: [
                {**slot, **patched}
                if (role, slot["address"]) == ("function-context", MOVED_FROM)
                else {**slot, "instruction": "clean"}
                for slot in slots
            ]
            for role, slots in batch.items()
        }
        one = run_turn(_at(got), binder, tmp_path, batch, answers)
        assert one.revisit == []
        assert sorted(e["address"] for e in one.escalations) == [
            MOVED_FROM,
            EMPTY_PLACE,
        ]

        batch2 = batch_of(one.escalations, one.rereads)
        answers2 = {
            role: [
                {**slot, "instruction": "withdraw", "reason": "the move carries it"}
                if (role, slot["address"]) == ("function-context", MOVED_FROM)
                else {**slot, "instruction": "hold", "reason": "mine stands"}
                for slot in slots
            ]
            for role, slots in batch2.items()
        }
        proof = proof_after(one, ({"turn": 1, "sent": batch},))
        two = run_turn(proof, binder, tmp_path, batch2, answers2)
        assert two.revisit == []
        (moved,) = _held_at(two, "block-context", MOVED_FROM)
        assert moved.instruction is Instruction.MOVE
        (withdrawn,) = _held_at(two, "function-context", MOVED_FROM)
        assert withdrawn.instruction is Instruction.CLEAN
        destination = next(e for e in two.rereads if e["address"] == EMPTY_PLACE)
        assert destination["roles"] == ["block-context"]
        assert [placed.mark for placed in destination["marks"]] == [moved]

        assert MOVED_FROM not in two.determined
        assert EMPTY_PLACE not in two.determined
        carried = {e["address"] for e in (*two.escalations, *two.rereads)}
        assert {MOVED_FROM, EMPTY_PLACE} <= carried


#: A second page, whose one paragraph two roles correct two ways.
OTHER_PAGE = "a = 1\n# one\n# two\n# three\nb = 2\n"
OTHER = "n.py@b1"


def _over_the_wire(proof: MasterProof) -> MasterProof:
    """The proof as the next command reads it back off disk."""
    again, why = MasterProof.deserialize("the wire", proof.serialize())
    assert again is not None, why
    return again


class TestAMoveSettledAtTurnZero:
    """A move settled at turn 0 reaches the final chief copy once --
    `no-command-for-the-middle` T68.

    block-context moves `MOVED_FROM` to `EMPTY_PLACE` and function-context
    defers there with an outside-my-role query, so the move is a `stet` at
    turn 0 at both its ends. The two roles correct `OTHER` two ways, which
    escalates it, both hold on turn 1, and the chief takes one side in at max
    turns. The proof crosses the wire between each step, as `collate`, `turn`
    and `disposition` hand it on.
    """

    def test_the_final_chief_copy_holds_the_move_once(self, tmp_path):
        (tmp_path / "m.py").write_text(GAPPED_PAGE, encoding="utf-8")
        (tmp_path / "n.py").write_text(OTHER_PAGE, encoding="utf-8")
        binder = binder_of(tmp_path, 0)
        copies = [seed(binder, role) for role in ("block-context", "function-context")]
        rulings = {
            "block-context": [
                {
                    "address": MOVED_FROM,
                    "instruction": "move",
                    "claim": {"from": MOVED_FROM, "to": EMPTY_PLACE},
                    "reason": "the comment is about w, not y",
                    "sources": [{"cite": "m.py:7"}],
                    "change": MOVED_TEXT,
                },
                {
                    "address": OTHER,
                    "instruction": "correct",
                    "claim": {"false": "two", "true": "TWO"},
                    "reason": "the fixture spells its numbers in capitals",
                    "sources": [{"cite": "n.py:1"}],
                },
            ],
            "function-context": [
                {
                    "address": MOVED_FROM,
                    "instruction": "query",
                    "claim": {
                        "shape": str(Shape.OUTSIDE_MY_ROLE),
                        "attempted": "read the paragraph against the code below it",
                        "settles": "block-context",
                    },
                    "reason": "where a comment sits is not this role's remit",
                    "sources": [{"cite": "m.py:5"}],
                },
                {
                    "address": OTHER,
                    "instruction": "correct",
                    "claim": {"false": "two", "true": "dos"},
                    "reason": "the fixture spells its numbers in Spanish",
                    "sources": [{"cite": "n.py:1"}],
                },
            ],
        }
        for copy in copies:
            for ruling in rulings[copy["role"]]:
                _, why = fill(copy, ruling, tmp_path)
                assert why == []
        got = collate("4c", copies, binder, root=tmp_path)
        assert got.problems == []
        moved = got.determined[MOVED_FROM]
        assert (moved.answer, moved.turn) == (Answer.STET, 0)
        assert got.determined[EMPTY_PLACE].mark == moved.mark
        assert [e["address"] for e in got.escalations] == [OTHER]

        batch = batch_for(got)
        answers = {
            role: [{**slot, "instruction": "hold", "reason": "mine"} for slot in slots]
            for role, slots in batch.items()
        }
        one = run_turn(
            _over_the_wire(proof_after(got)), binder, tmp_path, batch, answers
        )
        assert one.revisit == []
        proof = _over_the_wire(proof_after(one, ({"turn": 1, "sent": batch},)))

        last = refold(proof, binder, tmp_path)
        ruled = rule_at_max_turns(
            last, OTHER, Answer.TAKEN_IN, "block-context", "TWO", proof.turn
        )
        _, chief = close(last, [ruled], proof.turns)
        moves = [m for m in entries_of(chief) if m.instruction is Instruction.MOVE]
        assert [m.address for m in moves] == [MOVED_FROM]


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
        again = run_turn(_at(got), binder, REPO, batch, answers)
        problems = again.revisit
        assert problems == []
        assert again.determined["m.py@b1"].turn == 1
        assert [e["address"] for e in again.escalations] == ["m.py@b5"]
        return binder, again

    def test_a_stet_place_keeps_its_turn_and_leaves_every_later_batch(self):
        binder, one = self._turn_one()
        batch2 = batch_of(one.escalations, one.rereads)
        assert all(s["address"] == "m.py@b5" for r in batch2 for s in batch2[r])
        answers2 = {
            r: [{**batch2[r][0], "instruction": "hold", "reason": "still"}]
            for r in batch2
        }
        two = run_turn(_at(one, 1), binder, REPO, batch2, answers2)
        assert two.revisit == []
        assert two.determined["m.py@b1"].turn == 1
        assert [e["address"] for e in two.escalations] == ["m.py@b5"]

    def test_a_role_changing_its_entry_at_a_stet_place_changes_nothing(self):
        binder, one = self._turn_one()
        # block-context rewrites its b1 entry behind the fold's back -- on the
        # proof's wire, which is what the next turn reads.
        wire = _at(one, 1).serialize()
        for copy in wire["edit_copies"]:
            if copy["role"] == "block-context":
                for sheet in copy["sheets"]:
                    for entry in sheet["marks"]:
                        if entry["address"] == "m.py@b1":
                            entry["change"] = "# one\n# something else\n# three\n"
        proof, why = MasterProof.deserialize("rewritten", wire)
        assert proof is not None, why
        batch2 = batch_of(one.escalations, one.rereads)
        answers2 = {
            r: [{**batch2[r][0], "instruction": "hold", "reason": "still"}]
            for r in batch2
        }
        two = run_turn(proof, binder, REPO, batch2, answers2)
        assert two.determined["m.py@b1"].turn == 1
        assert two.determined["m.py@b1"].mark is not None
        assert two.determined["m.py@b1"].mark.change == DOS
        assert [e["address"] for e in two.escalations] == ["m.py@b5"]
        assert [m.change for m in entries_of(two.chief)] == [DOS]


class TestTheConflictOutcomes:
    """T15: the three outcomes of an escalation, driven through the real loop."""

    def test_hold_and_hold_go_another_turn(self):
        binder, copies, got = _escalated()
        batch = batch_of(got.escalations, got.rereads)
        answers = {
            r: [{**batch[r][0], "instruction": "hold", "reason": "mine"}] for r in batch
        }
        again = run_turn(_at(got), binder, REPO, batch, answers)
        assert [e["address"] for e in again.escalations] == ["m.py@b1"]
        assert again.determined == {}

    def test_hold_and_withdraw_take_the_held_in_after_the_withdrawers_read(self):
        binder, copies, got = _escalated()
        batch = batch_of(got.escalations, got.rereads)
        answers = {
            **_answered(
                batch, "block-context", instruction="withdraw", reason="theirs"
            ),
            **_answered(batch, "function-context", instruction="hold", reason="stands"),
        }
        one = run_turn(_at(got), binder, REPO, batch, answers)
        assert one.rereads[0]["composed"].change == DOS
        batch2 = batch_of(one.escalations, one.rereads)
        answers2 = {r: [{**batch2[r][0], "instruction": "clean"}] for r in batch2}
        two = run_turn(_at(one, 1), binder, REPO, batch2, answers2)
        assert two.revisit == []
        ruled = two.determined["m.py@b1"]
        assert ruled.answer is Answer.STET and ruled.turn == 2
        assert [m.change for m in entries_of(two.chief)] == [DOS]

    def test_withdraw_and_withdraw_leave_the_original_standing(self):
        binder, copies, got = _escalated()
        batch = batch_of(got.escalations, got.rereads)
        answers = {
            r: [{**batch[r][0], "instruction": "withdraw", "reason": "neither"}]
            for r in batch
        }
        again = run_turn(_at(got), binder, REPO, batch, answers)
        problems = again.revisit
        assert problems == []
        assert again.escalations == [] and again.rereads == []
        ruled = again.determined["m.py@b1"]
        assert ruled.answer is Answer.STET
        assert ruled.side == ORIGINAL
        assert ruled.how == "withdrawn"
        assert ruled.mark is None
        assert ruled.turn == 1
        assert entries_of(again.chief) == []


class TestARefusedAnswerIsARevisit:
    """T18. MEASURED in the game's hand 4: a refused answer was a problem
    string, which nothing could route; `flows.mark_errors.Revisit` is what
    the fold already routes, so a turn's refusals take that shape."""

    def test_a_malformed_answer_names_role_address_and_every_reason(self):
        binder, copies, got = _escalated()
        batch = batch_of(got.escalations, got.rereads)
        answers = {
            **_answered(batch, "block-context", instruction="correct", reason="x"),
            **_answered(batch, "function-context", instruction="hold", reason="stands"),
        }
        problems = run_turn(_at(got), binder, REPO, batch, answers).revisit
        assert len(problems) == 1
        one = problems[0]
        assert isinstance(one, Revisit)
        assert one.role == "block-context"
        assert one.address == "m.py@b1"
        assert one.unreadable is True
        assert any("change" in r for r in one.reasons)

    def test_an_unanswered_slot_is_a_revisit_that_is_not_unreadable(self):
        binder, copies, got = _escalated()
        batch = batch_of(got.escalations, got.rereads)
        answers = {
            "block-context": [],
            **_answered(batch, "function-context", instruction="hold", reason="stands"),
        }
        problems = run_turn(_at(got), binder, REPO, batch, answers).revisit
        assert [(p.role, p.address, p.unreadable) for p in problems] == [
            ("block-context", "m.py@b1", False)
        ]


class TestTheBatchThatGoesOut:
    """T11 / P13: the renderer lives at the flow. T19 / P2: the contracts are
    generated from the code."""

    def test_every_slot_carries_the_diff3_of_its_place(self):
        _, _, got = _escalated()
        batch = batch_for(got)
        for role in ("block-context", "function-context"):
            diff = batch[role][0]["diff"]
            assert "<<<<<<< conflict" in diff and ">>>>>>> end" in diff
            assert "======= block-context" in diff
            assert "======= function-context" in diff
        assert batch["block-context"][0]["diff"] == batch["function-context"][0]["diff"]

    def test_a_reread_slot_carries_the_diff_too(self, tmp_path):
        _, _, got = _composed(tmp_path)
        batch = batch_for(got)
        assert "<<<<<<< conflict" in batch["block-context"][0]["diff"]

    def test_the_contracts_are_the_codes_own_sets(self):
        got = contracts()
        assert set(got) == {"stage_4c_mark", "escalation", "composition"}
        assert got["escalation"]["instruction"] == [
            "correct",
            "hold",
            "patch",
            "withdraw",
        ]
        assert got["escalation"]["owes_change"] == ["correct", "patch"]
        assert got["composition"]["instruction"] == [
            "clean",
            "correct",
            "patch",
            "query",
        ]
        assert set(got["composition"]["claim"]) == {
            "clean",
            "correct",
            "patch",
            "query",
        }
        assert got["stage_4c_mark"]["instruction"] == sorted(
            ["add", "clean", "correct", "drop", "move", "patch", "query"]
        )


class TestTheCap:
    def test_taken_in_of_the_original_leaves_no_entry_on_the_chief(self):
        _, _, got = _escalated()
        ruled = rule_at_max_turns(
            got, "m.py@b1", Answer.TAKEN_IN, ORIGINAL, "neither reading holds", turn=2
        )
        assert ruled.mark is None
        assert ruled.side == ORIGINAL
        assert ruled.how == "max-turns"
        every, chief = determined_chief(got, [ruled])
        assert every["m.py@b1"] is ruled
        assert entries_of(chief) == []

    def test_taken_in_of_a_role_carries_that_roles_text(self):
        _, _, got = _escalated()
        ruled = rule_at_max_turns(
            got, "m.py@b1", Answer.TAKEN_IN, "function-context", "dos is right", turn=2
        )
        _, chief = determined_chief(got, [ruled])
        assert [m.change for m in entries_of(chief)] == [DOS]

    def test_close_returns_the_closed_proof_and_the_chief(self):
        """T23: what `disposition` writes is the flow's, not the console."""
        _, _, got = _escalated()
        ruled = rule_at_max_turns(
            got, "m.py@b1", Answer.TAKEN_IN, "function-context", "dos", turn=1
        )
        closed, chief = close(got, [ruled], ({"turn": 1},))
        assert closed.turn == 1
        assert [(d.address, d.answer) for d in closed.determined] == [
            ("m.py@b1", Answer.TAKEN_IN)
        ]
        assert [m.change for m in entries_of(chief)] == [DOS]

    def test_a_recast_of_an_add_stays_an_add(self):
        """Measured 2026-09-07 on claude-settings: a recast of an add was
        written as a correct, which asserts a sentence is false at a place
        holding no sentence, so the compositor wrote nothing and exited 0."""
        _, _, got = _escalated_add()
        ruled = rule_at_max_turns(
            got, "m.py@b1", Answer.RECAST, "", "chief's own", turn=2, prose="# mine\n"
        )
        assert ruled.mark is not None
        assert ruled.mark.instruction is Instruction.ADD
        _, chief = determined_chief(got, [ruled])
        entry = entries_of(chief)[0]
        again, why = Mark.deserialize(entry.address, entry.serialize())
        assert why == []
        assert again == entry

    @pytest.mark.parametrize(
        "escalated, instruction",
        [
            (_escalated_patch, Instruction.PATCH),
            (_escalated_drop, Instruction.DROP),
            (_escalated_move, Instruction.MOVE),
        ],
    )
    def test_a_recast_keeps_the_filed_instruction(self, escalated, instruction):
        """Fix round 1 on `_recast_claim`: `add` had its own test above and
        `correct` its own below, leaving `patch`, `drop` and `move` verified
        by code trace only. Each is carried through a real fold here rather
        than hand-traced -- `patch` and `drop` quote an original sentence and
        escalate; `move` quotes none and is re-read, widened by
        `_join_moves` to both its ends -- and each recast still parses under
        the instruction it carries."""
        _, _, got = escalated()
        ruled = rule_at_max_turns(
            got, "m.py@b1", Answer.RECAST, "", "chief's own", turn=2, prose="# mine\n"
        )
        assert ruled.mark is not None
        assert ruled.mark.instruction is instruction
        again, why = Mark.deserialize(ruled.mark.address, ruled.mark.serialize())
        assert why == []
        assert again == ruled.mark

    def test_a_recast_carries_the_chiefs_own_prose_and_parses(self):
        _, _, got = _escalated()
        prose = "# one\n# 2\n# three\n"
        ruled = rule_at_max_turns(
            got, "m.py@b1", Answer.RECAST, "", "both sides miss it", turn=2, prose=prose
        )
        assert ruled.side == CHIEF
        _, chief = determined_chief(got, [ruled])
        entry = entries_of(chief)[0]
        assert entry.change == prose
        again, why = Mark.deserialize(entry.address, entry.serialize())
        assert why == []
        assert again == entry

    def test_an_unsettlable_place_is_not_the_chiefs_to_rule(self):
        """`Process: #90`: the place with the human's query is asked of the
        human after everything else, not ruled at max turns."""
        binder = a_binder_over({"m.py@b1": BASE})
        copies = copies_over(
            binder,
            {
                "block-context": {"m.py@b1": a_correct_setting("m.py@b1", "two", TWO)},
                "function-context": {
                    "m.py@b1": a_correct_setting("m.py@b1", "two", DOS)
                },
                "module-context": {
                    "m.py@b1": a_query("m.py@b1", Shape.HUMAN_REVIEW_NECESSARY)
                },
            },
        )
        got = collate("4c", copies, binder, root=REPO)
        assert [u["address"] for u in got.unsettlable] == ["m.py@b1"]
        with pytest.raises(ValueError) as caught:
            rule_at_max_turns(
                got, "m.py@b1", Answer.TAKEN_IN, "block-context", "x", turn=2
            )
        assert "unsettlable" in str(caught.value)

    def test_the_cap_refuses_to_close_with_a_place_unruled(self):
        """T17. MEASURED in the game's hand 3: the chief recast one place and
        nothing would have noticed a second left unruled."""
        _, _, got = _escalated()
        with pytest.raises(ValueError) as caught:
            determined_chief(got, [])
        assert "m.py@b1" in str(caught.value)
        assert "block-context, function-context" in str(caught.value)

    def test_the_cap_closes_once_every_carried_place_is_ruled(self):
        _, _, got = _escalated()
        ruled = rule_at_max_turns(
            got, "m.py@b1", Answer.TAKEN_IN, ORIGINAL, "neither", turn=2
        )
        every, chief = determined_chief(got, [ruled])
        assert set(every) == {"m.py@b1"}
        assert entries_of(chief) == []

    def test_an_unsettlable_place_is_not_counted_as_unruled(self):
        binder = a_binder_over({"m.py@b1": BASE})
        copies = copies_over(
            binder,
            {
                "block-context": {"m.py@b1": a_correct_setting("m.py@b1", "two", TWO)},
                "function-context": {
                    "m.py@b1": a_correct_setting("m.py@b1", "two", DOS)
                },
                "module-context": {
                    "m.py@b1": a_query("m.py@b1", Shape.HUMAN_REVIEW_NECESSARY)
                },
            },
        )
        got = collate("4c", copies, binder, root=REPO)
        every, _ = determined_chief(got, [])
        assert every == {}

    def test_stet_is_not_the_chiefs_to_rule(self):
        _, _, got = _escalated()
        with pytest.raises(ValueError):
            rule_at_max_turns(got, "m.py@b1", Answer.STET, "block-context", "x", turn=2)

    def test_a_side_with_no_mark_there_cannot_be_taken_in(self):
        _, _, got = _escalated()
        with pytest.raises(ValueError):
            rule_at_max_turns(
                got, "m.py@b1", Answer.TAKEN_IN, "module-context", "x", turn=2
            )
