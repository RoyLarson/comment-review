"""The `disposition` command: the chief closes the proof, from the console.

! DRIVEN THROUGH `main()` AND `sys.argv` over the real chain -- `collate`
deals, `turn` holds the place open, `disposition` rules it. `P5` of
`docs/plans/0.2.4-the-turn-as-commands.md`, and T16's other half.
"""

from helpers import (
    BASE,
    DOS,
    TWO,
    a_query,
    disposition,
    entries_of,
    held_open,
    the_chief,
)

from comment_review.commands import collate as collate_command
from comment_review.commands import disposition as command
from comment_review.desk.determined import CHIEF, ORIGINAL, Answer
from comment_review.desk.mark import Shape
from comment_review.flows.proof_io import load_proof

RECAST = "# one\n# both\n# three\n"


class TestTheChiefRules:
    def test_a_taken_in_side_stands_on_the_chief_and_the_proof_closes(
        self, tmp_path, monkeypatch, capsys
    ):
        held_open(tmp_path, monkeypatch, capsys)
        code, out = disposition(
            tmp_path,
            monkeypatch,
            capsys,
            [
                {
                    "address": "m.py@b1",
                    "answer": "taken_in",
                    "side": "function-context",
                    "reason": "theirs reads better",
                }
            ],
        )
        assert code == command.OK, out
        chief = the_chief(tmp_path)
        assert chief.role == "copy-chief"
        assert [m.change for m in entries_of(chief)] == [DOS]
        final, why = load_proof(tmp_path / "final.json")
        assert final is not None, why
        (ruled,) = final.determined
        assert ruled.answer is Answer.TAKEN_IN
        assert ruled.side == "function-context"
        assert ruled.turn == 1
        assert ruled.how == "cap"
        assert len(final.turns) == 1

    def test_a_taken_in_of_the_original_writes_no_entry(
        self, tmp_path, monkeypatch, capsys
    ):
        held_open(tmp_path, monkeypatch, capsys)
        code, out = disposition(
            tmp_path,
            monkeypatch,
            capsys,
            [
                {
                    "address": "m.py@b1",
                    "answer": "taken_in",
                    "side": ORIGINAL,
                    "reason": "neither improves it",
                }
            ],
        )
        assert code == command.OK, out
        assert entries_of(the_chief(tmp_path)) == []
        final, _why = load_proof(tmp_path / "final.json")
        assert final is not None
        (ruled,) = final.determined
        assert ruled.side == ORIGINAL
        assert ruled.mark is None

    def test_a_recast_carries_the_chiefs_own_prose(self, tmp_path, monkeypatch, capsys):
        held_open(tmp_path, monkeypatch, capsys)
        code, out = disposition(
            tmp_path,
            monkeypatch,
            capsys,
            [
                {
                    "address": "m.py@b1",
                    "answer": "recast",
                    "reason": "both half right",
                    "prose": RECAST,
                }
            ],
        )
        assert code == command.OK, out
        assert [m.change for m in entries_of(the_chief(tmp_path))] == [RECAST]
        final, _why = load_proof(tmp_path / "final.json")
        assert final is not None
        assert final.determined[0].side == CHIEF

    def test_an_unsettlable_place_is_printed_for_the_human_and_not_ruled(
        self, tmp_path, monkeypatch, capsys
    ):
        texts = {"m.py@b1": BASE, "m.py@b2": "# four\n# five\n# six\n"}
        asked = {
            "block-context": {
                "m.py@b2": a_query("m.py@b2", Shape.HUMAN_REVIEW_NECESSARY)
            }
        }
        held_open(tmp_path, monkeypatch, capsys, asked, texts)
        code, out = disposition(
            tmp_path,
            monkeypatch,
            capsys,
            [
                {
                    "address": "m.py@b1",
                    "answer": "taken_in",
                    "side": "block-context",
                    "reason": "r",
                }
            ],
        )
        assert code == command.OK, out
        assert "unsettlable m.py@b2: block-context asks the human" in out
        assert [m.address for m in entries_of(the_chief(tmp_path))] == ["m.py@b1"]
        final, _why = load_proof(tmp_path / "final.json")
        assert final is not None
        assert [p["address"] for p in final.unsettlable] == ["m.py@b2"]


class TestRefusals:
    def test_an_unruled_place_is_BROKEN_naming_it_and_its_roles(
        self, tmp_path, monkeypatch, capsys
    ):
        held_open(tmp_path, monkeypatch, capsys)
        code, out = disposition(tmp_path, monkeypatch, capsys, [])
        assert code == command.BROKEN
        assert "unruled at the cap: m.py@b1 (block-context, function-context)" in out
        assert not (tmp_path / "chief.json").exists()
        assert not (tmp_path / "final.json").exists()

    def test_a_recast_without_prose_is_BROKEN(self, tmp_path, monkeypatch, capsys):
        held_open(tmp_path, monkeypatch, capsys)
        code, out = disposition(
            tmp_path,
            monkeypatch,
            capsys,
            [{"address": "m.py@b1", "answer": "recast", "reason": "r"}],
        )
        assert code == command.BROKEN
        assert "a recast needs the chief's own prose" in out
        assert not (tmp_path / "final.json").exists()

    def test_a_roles_answer_is_not_the_chiefs(self, tmp_path, monkeypatch, capsys):
        held_open(tmp_path, monkeypatch, capsys)
        code, out = disposition(
            tmp_path,
            monkeypatch,
            capsys,
            [{"address": "m.py@b1", "answer": "correct", "reason": "r"}],
        )
        assert code == command.BROKEN
        assert "`answer` must be one of" in out

    def test_rulings_that_are_not_a_list_are_UNREADABLE(
        self, tmp_path, monkeypatch, capsys
    ):
        held_open(tmp_path, monkeypatch, capsys)
        code, _out = disposition(tmp_path, monkeypatch, capsys, {"address": "m.py@b1"})
        assert code == collate_command.UNREADABLE


class TestTheGateSeesIt:
    def test_cap_is_in_COMMANDS(self):
        from comment_review.__main__ import COMMANDS

        assert "disposition" in COMMANDS

    def test_TWO_is_the_side_a_taken_in_can_name(self, tmp_path, monkeypatch, capsys):
        """The other side too -- so the test above is not passing by taking
        the one text the fold happened to hold."""
        held_open(tmp_path, monkeypatch, capsys)
        code, out = disposition(
            tmp_path,
            monkeypatch,
            capsys,
            [
                {
                    "address": "m.py@b1",
                    "answer": "taken_in",
                    "side": "block-context",
                    "reason": "r",
                }
            ],
        )
        assert code == command.OK, out
        assert [m.change for m in entries_of(the_chief(tmp_path))] == [TWO]
