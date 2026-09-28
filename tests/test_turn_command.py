"""The `turn` command: one turn from the console, over what `collate` wrote.

! DRIVEN THROUGH `main()` AND `sys.argv`, the way `conftest.run_command` does,
and over the REAL chain: `collate --proof-out --batch-out` deals the hand, the
answers are the sent slots with their fields filled, and `turn` folds them.
`P4` of `docs/plans/0.2.4-the-turn-as-commands.md`.

! THE PROOF IS WHAT THE TURN READS. It carries the places the last fold
decided, so what a role owes, and what its answer is read against, come off
the proof rather than off the batch -- the batch is what the answers were
written on, and `answer` below reads it for that.
"""

import json

from conftest import run_command
from helpers import (
    BASE,
    DOS,
    HAND_ROLES,
    TYPOS,
    agreed,
    answer,
    contested,
    deal,
    merged,
    patched,
    place_on,
    proof_at,
    turn,
)

# ! THE EXIT CODES ARE `collate`'s, and this reads them there. All three
# commands fold through the Unit of Work and exit the same five, so a test
# naming them anywhere else would be asserting a second copy of the contract.
from comment_review.commands import collate as collate_command
from comment_review.commands import turn as turn_command

ROLES = HAND_ROLES


class TestOneTurn:
    def test_two_corrects_that_converge_settle_the_place_and_exit_OK(
        self, tmp_path, monkeypatch, capsys
    ):
        assert deal(tmp_path, monkeypatch, capsys, contested("m.py@b1")) == 4
        code, out = turn(
            tmp_path,
            monkeypatch,
            capsys,
            1,
            answer(
                tmp_path,
                1,
                "block-context",
                "m.py@b1",
                instruction="correct",
                reason="met",
                change=DOS,
            ),
            answer(
                tmp_path,
                1,
                "function-context",
                "m.py@b1",
                instruction="hold",
                reason="stands",
            ),
        )
        assert code == collate_command.OK, out
        place = place_on(proof_at(tmp_path, 1), "m.py@b1")
        assert place["state"] == "agreed"
        assert place["text"] == DOS
        assert not (tmp_path / "batch2.json").exists()

    def test_each_roles_answer_lands_on_the_place_it_answered(
        self, tmp_path, monkeypatch, capsys
    ):
        """The place is the record: a turn writes each role's answer onto it
        under the turn's own number, and the next fold derives the place from
        that record."""
        deal(tmp_path, monkeypatch, capsys, contested("m.py@b1"))
        turn(
            tmp_path,
            monkeypatch,
            capsys,
            1,
            answer(
                tmp_path,
                1,
                "block-context",
                "m.py@b1",
                instruction="correct",
                reason="met",
                change=DOS,
            ),
            answer(
                tmp_path,
                1,
                "function-context",
                "m.py@b1",
                instruction="hold",
                reason="stands",
            ),
        )
        answers = place_on(proof_at(tmp_path, 1), "m.py@b1")["answers"]
        assert sorted(answers) == ["1"]
        assert sorted(answers["1"]) == list(ROLES)
        assert answers["1"]["block-context"]["instruction"] == "correct"

    def test_two_holds_stay_contested_and_the_next_batch_is_written(
        self, tmp_path, monkeypatch, capsys
    ):
        deal(tmp_path, monkeypatch, capsys, contested("m.py@b1"))
        code, out = turn(
            tmp_path,
            monkeypatch,
            capsys,
            1,
            answer(
                tmp_path,
                1,
                "block-context",
                "m.py@b1",
                instruction="hold",
                reason="mine",
            ),
            answer(
                tmp_path,
                1,
                "function-context",
                "m.py@b1",
                instruction="hold",
                reason="mine",
            ),
        )
        assert code == collate_command.ESCALATIONS, out
        assert "contested m.py@b1" in out
        assert place_on(proof_at(tmp_path, 1), "m.py@b1")["state"] == "contested"
        batch2 = json.loads((tmp_path / "batch2.json").read_text(encoding="utf-8"))
        assert sorted(batch2) == list(ROLES)

    def test_the_turn_number_counts_the_answers_already_on_the_places(
        self, tmp_path, monkeypatch, capsys
    ):
        deal(tmp_path, monkeypatch, capsys, contested("m.py@b1"))
        turn(
            tmp_path,
            monkeypatch,
            capsys,
            1,
            answer(
                tmp_path,
                1,
                "block-context",
                "m.py@b1",
                instruction="hold",
                reason="mine",
            ),
            answer(
                tmp_path,
                1,
                "function-context",
                "m.py@b1",
                instruction="hold",
                reason="mine",
            ),
        )
        code, out = turn(
            tmp_path,
            monkeypatch,
            capsys,
            2,
            answer(
                tmp_path,
                2,
                "block-context",
                "m.py@b1",
                instruction="correct",
                reason="met",
                change=DOS,
            ),
            answer(
                tmp_path,
                2,
                "function-context",
                "m.py@b1",
                instruction="hold",
                reason="stands",
            ),
        )
        assert code == collate_command.OK, out
        assert "after turn 2" in out
        place = place_on(proof_at(tmp_path, 2), "m.py@b1")
        assert sorted(place["answers"]) == ["1", "2"]
        assert place["text"] == DOS


class TestOnceSettledAlwaysSettled:
    def test_a_place_the_first_fold_settled_still_reads_the_same_after_a_turn(
        self, tmp_path, monkeypatch, capsys
    ):
        """`Process: #91`, across two processes. The place is the record, so a
        place the first fold settled is derived again from the same marks and
        comes to the same text -- it is in no batch and no turn touches it."""
        texts = {"m.py@b1": BASE, "m.py@b2": "# four\n# five\n# six\n"}
        cinco = "# four\n# cinco\n# six\n"
        by_role = merged(
            agreed("m.py@b1"),
            contested("m.py@b2", "five", "# four\n# FIVE\n# six\n", cinco),
        )
        assert deal(tmp_path, monkeypatch, capsys, by_role, texts) == 4
        before = place_on(proof_at(tmp_path, 0), "m.py@b1")
        assert before["state"] == "agreed"
        batch1 = json.loads((tmp_path / "batch1.json").read_text(encoding="utf-8"))
        assert all(
            slot["address"] == "m.py@b2" for slots in batch1.values() for slot in slots
        )
        code, out = turn(
            tmp_path,
            monkeypatch,
            capsys,
            1,
            answer(
                tmp_path,
                1,
                "block-context",
                "m.py@b2",
                instruction="correct",
                reason="met",
                change=cinco,
            ),
            answer(
                tmp_path,
                1,
                "function-context",
                "m.py@b2",
                instruction="hold",
                reason="stands",
            ),
        )
        assert code == collate_command.OK, out
        after = proof_at(tmp_path, 1)
        assert place_on(after, "m.py@b1") == before
        assert place_on(after, "m.py@b2")["text"] == cinco


class TestRefusals:
    def test_an_unreadable_answer_is_BROKEN_and_nothing_is_written(
        self, tmp_path, monkeypatch, capsys
    ):
        deal(tmp_path, monkeypatch, capsys, contested("m.py@b1"))
        code, out = turn(
            tmp_path,
            monkeypatch,
            capsys,
            1,
            answer(
                tmp_path,
                1,
                "block-context",
                "m.py@b1",
                instruction="banana",
                reason="x",
            ),
            answer(
                tmp_path,
                1,
                "function-context",
                "m.py@b1",
                instruction="hold",
                reason="stands",
            ),
        )
        assert code == collate_command.BROKEN, out
        assert "block-context m.py@b1" in out
        assert not (tmp_path / "proof1.json").exists()
        assert not (tmp_path / "batch2.json").exists()

    def test_an_unanswered_slot_is_BROKEN_and_nothing_is_written(
        self, tmp_path, monkeypatch, capsys
    ):
        """An answer nobody wrote is not a withdrawal (`Process: #22`), so the
        round is void rather than folded past: the proof would otherwise carry
        a place decided without the ruling its own record says is owed."""
        deal(tmp_path, monkeypatch, capsys, contested("m.py@b1"))
        code, out = turn(
            tmp_path,
            monkeypatch,
            capsys,
            1,
            answer(
                tmp_path,
                1,
                "function-context",
                "m.py@b1",
                instruction="hold",
                reason="stands",
            ),
        )
        assert code == collate_command.BROKEN, out
        assert "block-context m.py@b1: unanswered" in out
        assert not (tmp_path / "proof1.json").exists()

    def test_a_slot_left_unanswered_beside_an_answered_one_is_BROKEN(
        self, tmp_path, monkeypatch, capsys
    ):
        """Both roles answer at `m.py@b1` and function-context leaves
        `m.py@b2`, a place it was put to, unanswered."""
        texts = {"m.py@b1": BASE, "m.py@b2": "# four\n# five\n# six\n"}
        by_role = merged(
            contested("m.py@b1"),
            contested("m.py@b2", "five", "# four\n# FIVE\n# six\n", "# four\n# 5\n"),
        )
        assert deal(tmp_path, monkeypatch, capsys, by_role, texts) == 4
        batch = json.loads((tmp_path / "batch1.json").read_text(encoding="utf-8"))
        held = [
            {**slot, "instruction": "hold", "reason": "mine"}
            for slot in batch["block-context"]
        ]
        assert sorted(s["address"] for s in held) == ["m.py@b1", "m.py@b2"]
        block = tmp_path / "answers1_block-context.json"
        block.write_text(json.dumps(held), encoding="utf-8")
        code, out = turn(
            tmp_path,
            monkeypatch,
            capsys,
            1,
            f"block-context={block}",
            answer(
                tmp_path,
                1,
                "function-context",
                "m.py@b1",
                instruction="hold",
                reason="mine",
            ),
        )
        assert code == collate_command.BROKEN, out
        assert "function-context m.py@b2: unanswered" in out
        assert not (tmp_path / "proof1.json").exists()

    def test_a_proof_that_is_not_one_is_UNREADABLE(self, tmp_path, monkeypatch, capsys):
        deal(tmp_path, monkeypatch, capsys, contested("m.py@b1"))
        code, _out = turn(
            tmp_path,
            monkeypatch,
            capsys,
            1,
            answer(
                tmp_path, 1, "block-context", "m.py@b1", instruction="hold", reason="x"
            ),
            proof=str(tmp_path / "binder.json"),
        )
        assert code == collate_command.UNREADABLE

    def test_answers_without_a_role_is_UNREADABLE(self, tmp_path, monkeypatch, capsys):
        deal(tmp_path, monkeypatch, capsys, contested("m.py@b1"))
        # ! A bare path where `ROLE=PATH` is owed.
        code, _out = turn(tmp_path, monkeypatch, capsys, 1, str(tmp_path / "nope.json"))
        assert code == collate_command.UNREADABLE


class TestAHumanQuestion:
    """`decision-log.md Process: #197` and `#198`: a human question given as
    an answer stops the turn before the fold, and `--human` is the answers
    file it is read from."""

    QUERY = {
        "instruction": "query",
        "reason": "which of the two the author meant is theirs to say",
        "claim": {
            "shape": "human-review-necessary",
            "attempted": "read both texts against the code",
            "settles": "the author",
        },
    }

    def _answers(self, tmp_path, monkeypatch, capsys) -> list[str]:
        """Two patches on different lines compose, and a composition admits a
        `query` answer where an escalation does not."""
        code = deal(
            tmp_path, monkeypatch, capsys, patched("m.py@b1"), {"m.py@b1": TYPOS}
        )
        assert code == collate_command.REREADS
        return [
            answer(tmp_path, 1, "block-context", "m.py@b1", **self.QUERY),
            answer(
                tmp_path,
                1,
                "function-context",
                "m.py@b1",
                instruction="clean",
                reason="the two read as one paragraph",
            ),
        ]

    def test_a_human_query_exits_asks_the_human_and_writes_nothing(
        self, tmp_path, monkeypatch, capsys
    ):
        answers = self._answers(tmp_path, monkeypatch, capsys)
        code, out = turn(tmp_path, monkeypatch, capsys, 1, *answers)
        assert code == collate_command.ASKS_THE_HUMAN, out
        assert "asks the human m.py@b1: block-context -- " in out
        assert not (tmp_path / "proof1.json").exists()
        assert not (tmp_path / "batch2.json").exists()

    def test_a_human_file_that_is_not_toml_is_unreadable(
        self, tmp_path, monkeypatch, capsys
    ):
        """Review Focus 3."""
        answers = self._answers(tmp_path, monkeypatch, capsys)
        human = tmp_path / "human.toml"
        human.write_text("[[answer]\nrole = ", encoding="utf-8")
        argv = [
            "--proof",
            str(tmp_path / "proof0.json"),
            "--proof-out",
            str(tmp_path / "proof1.json"),
            "--human",
            str(human),
        ]
        for one in answers:
            argv += ["--answers", one]
        code, out = run_command(
            monkeypatch, capsys, turn_command, *argv, with_stderr=True
        )
        assert code == collate_command.UNREADABLE, out
        assert f"{human}: not TOML" in out
        assert not (tmp_path / "proof1.json").exists()


class TestTheGateSeesIt:
    def test_turn_is_in_COMMANDS(self):
        from comment_review.__main__ import COMMANDS

        assert "turn" in COMMANDS
