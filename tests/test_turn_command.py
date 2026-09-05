"""The `turn` command: one turn from the console, over what `collate` wrote.

! DRIVEN THROUGH `main()` AND `sys.argv`, the way `conftest.run_command` does,
and over the REAL chain: `collate --proof-out --batch-out` deals the hand, the
answers are the sent slots with their fields filled, and `turn` folds them.
`P4` of `docs/plans/0.2.4-the-turn-as-commands.md`.
"""

import json

from helpers import a_binder_over, a_correct_setting, copies_over

from comment_review.commands import collate as collate_command
from comment_review.commands import turn as command
from comment_review.desk.determined import Answer
from comment_review.flows.proof_io import load_proof

BASE = "# one\n# two\n# three\n"
TWO = "# one\n# TWO\n# three\n"
DOS = "# one\n# dos\n# three\n"
ROLES = ("block-context", "function-context")


def _contested(address: str, sentence="two", one=TWO, other=DOS) -> dict:
    return {
        "block-context": {address: a_correct_setting(address, sentence, one)},
        "function-context": {address: a_correct_setting(address, sentence, other)},
    }


def _agreed(address: str) -> dict:
    return {role: {address: a_correct_setting(address, "two", DOS)} for role in ROLES}


def _merged(*by_roles: dict) -> dict:
    out: dict = {}
    for by_role in by_roles:
        for role, marks in by_role.items():
            out.setdefault(role, {}).update(marks)
    return out


def deal(tmp_path, monkeypatch, capsys, by_role: dict, texts: dict | None = None):
    """`collate` over `by_role`, writing binder.json, proof0.json and batch1.json."""
    binder = a_binder_over(texts or {"m.py@b1": BASE})
    copies = copies_over(binder, by_role)
    (tmp_path / "binder.json").write_text(
        json.dumps(binder.serialize()), encoding="utf-8"
    )
    argv = [
        "collate",
        "--stage",
        "4c",
        "--binder",
        str(tmp_path / "binder.json"),
        "--out",
        str(tmp_path / "chief0.json"),
        "--proof-out",
        str(tmp_path / "proof0.json"),
        "--batch-out",
        str(tmp_path / "batch1.json"),
    ]
    for i, copy in enumerate(copies):
        path = tmp_path / f"copy{i}.json"
        path.write_text(json.dumps(copy), encoding="utf-8")
        argv += ["--edit-copy", str(path)]
    monkeypatch.setattr("sys.argv", argv)
    code = collate_command.main()
    capsys.readouterr()
    return code


def answer(tmp_path, n: int, role: str, address: str, **fields) -> str:
    """This role's sent slot at `address` on batch<n>, with `fields` laid over."""
    batch = json.loads((tmp_path / f"batch{n}.json").read_text(encoding="utf-8"))
    slot = next(s for s in batch[role] if s["address"] == address)
    path = tmp_path / f"answers{n}_{role}.json"
    path.write_text(json.dumps([{**slot, **fields}]), encoding="utf-8")
    return f"{role}={path}"


def turn(tmp_path, monkeypatch, capsys, n: int, *answers: str, proof: str = ""):
    argv = [
        "turn",
        "--proof",
        proof or str(tmp_path / f"proof{n - 1}.json"),
        "--binder",
        str(tmp_path / "binder.json"),
        "--sent",
        str(tmp_path / f"batch{n}.json"),
        "--proof-out",
        str(tmp_path / f"proof{n}.json"),
        "--batch-out",
        str(tmp_path / f"batch{n + 1}.json"),
    ]
    for one in answers:
        argv += ["--answers", one]
    monkeypatch.setattr("sys.argv", argv)
    return command.main(), capsys.readouterr().out


def proof_at(tmp_path, n: int):
    got, why = load_proof(tmp_path / f"proof{n}.json")
    assert got is not None, why
    return got


class TestOneTurn:
    def test_two_corrects_that_converge_are_a_stet_at_turn_1_and_exit_OK(
        self, tmp_path, monkeypatch, capsys
    ):
        assert deal(tmp_path, monkeypatch, capsys, _contested("m.py@b1")) == 4
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
        deal(tmp_path, monkeypatch, capsys, _contested("m.py@b1"))
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
        deal(tmp_path, monkeypatch, capsys, _contested("m.py@b1"))
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
        deal(tmp_path, monkeypatch, capsys, _contested("m.py@b1"))
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
        by_role = _merged(
            _agreed("m.py@b1"),
            _contested("m.py@b2", "five", "# four\n# FIVE\n# six\n", cinco),
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
        deal(tmp_path, monkeypatch, capsys, _contested("m.py@b1"))
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
        deal(tmp_path, monkeypatch, capsys, _contested("m.py@b1"))
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
        deal(tmp_path, monkeypatch, capsys, _contested("m.py@b1"))
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
        deal(tmp_path, monkeypatch, capsys, _contested("m.py@b1"))
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
