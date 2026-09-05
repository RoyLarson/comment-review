"""The `turn` command: one turn from the console, over what `collate` wrote.

! DRIVEN THROUGH `main()` AND `sys.argv`, the way `conftest.run_command` does,
and over the REAL chain: `collate --proof-out --batch-out` deals the hand, the
answers are the sent slots with their fields filled, and `turn` folds them.
`P4` of `docs/plans/0.2.4-the-turn-as-commands.md`.
"""

import json

from helpers import (
    BASE,
    DOS,
    HAND_ROLES,
    agreed,
    answer,
    contested,
    deal,
    merged,
    proof_at,
    turn,
)

from comment_review.commands import collate as collate_command
from comment_review.commands import turn as command
from comment_review.desk.determined import Answer

ROLES = HAND_ROLES


class TestOneTurn:
    def test_two_corrects_that_converge_are_a_stet_at_turn_1_and_exit_OK(
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
        assert code == command.OK, out
        proof = proof_at(tmp_path, 1)
        (ruled,) = proof.determined
        assert ruled.address == "m.py@b1"
        assert ruled.answer is Answer.STET
        assert ruled.turn == 1
        assert not (tmp_path / "batch2.json").exists()

    def test_the_turn_record_lands_on_the_proof(self, tmp_path, monkeypatch, capsys):
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
        proof = proof_at(tmp_path, 1)
        (record,) = proof.turns
        assert record["turn"] == 1
        assert sorted(record["sent"]) == list(ROLES)
        assert sorted(record["returned"]) == list(ROLES)
        assert record["revisit"] == []

    def test_two_holds_stay_escalated_and_the_next_batch_is_written(
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
        assert code == command.ESCALATIONS, out
        assert "escalated m.py@b1" in out
        assert proof_at(tmp_path, 1).determined == ()
        batch2 = json.loads((tmp_path / "batch2.json").read_text(encoding="utf-8"))
        assert sorted(batch2) == list(ROLES)

    def test_the_turn_number_is_the_records_length_plus_one(
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
        assert code == command.OK, out
        proof = proof_at(tmp_path, 2)
        assert [r["turn"] for r in proof.turns] == [1, 2]
        (ruled,) = proof.determined
        assert ruled.turn == 2


class TestOnceStetAlwaysStet:
    def test_an_earlier_stet_keeps_its_turn_across_the_command_boundary(
        self, tmp_path, monkeypatch, capsys
    ):
        """`Process: #91`, across two processes: `earlier` is the proof's own
        `determined`, read back off disk, so the place settled at the first
        fold still says turn 0 after a turn settled the other."""
        texts = {"m.py@b1": BASE, "m.py@b2": "# four\n# five\n# six\n"}
        cinco = "# four\n# cinco\n# six\n"
        by_role = merged(
            agreed("m.py@b1"),
            contested("m.py@b2", "five", "# four\n# FIVE\n# six\n", cinco),
        )
        assert deal(tmp_path, monkeypatch, capsys, by_role, texts) == 4
        before = proof_at(tmp_path, 0)
        assert [(d.address, d.turn) for d in before.determined] == [("m.py@b1", 0)]
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
        assert code == command.OK, out
        after = proof_at(tmp_path, 1)
        assert [(d.address, d.turn) for d in after.determined] == [
            ("m.py@b1", 0),
            ("m.py@b2", 1),
        ]


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
        assert code == command.BROKEN, out
        assert "block-context m.py@b1" in out
        assert not (tmp_path / "proof1.json").exists()
        assert not (tmp_path / "batch2.json").exists()

    def test_an_unanswered_slot_is_COVERAGE_and_the_place_stays(
        self, tmp_path, monkeypatch, capsys
    ):
        """Unanswered is not unreadable -- `Revisit.unreadable` is False -- so
        the proof is written and the place is still escalated."""
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
        assert code == command.ESCALATIONS, out
        assert "unanswered" in out
        assert (tmp_path / "proof1.json").exists()

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
        monkeypatch.setattr(
            "sys.argv",
            [
                "turn",
                "--proof",
                str(tmp_path / "proof0.json"),
                "--binder",
                str(tmp_path / "binder.json"),
                "--sent",
                str(tmp_path / "batch1.json"),
                "--proof-out",
                str(tmp_path / "proof1.json"),
                "--answers",
                str(tmp_path / "nope.json"),
            ],
        )
        assert command.main() == collate_command.UNREADABLE


class TestTheGateSeesIt:
    def test_turn_is_in_COMMANDS(self):
        from comment_review.__main__ import COMMANDS

        assert "turn" in COMMANDS
