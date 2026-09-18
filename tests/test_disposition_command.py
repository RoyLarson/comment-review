"""The `disposition` command: the chief closes the proof, from the console.

! DRIVEN THROUGH `main()` AND `sys.argv` over the real chain -- `collate`
deals, `turn` holds the place open, `disposition` rules it. `P5` of
`docs/plans/0.2.4-the-turn-as-commands.md`, and T16's other half.

! THE EXIT CODES ARE `collate`'s, read there for the reason
`tests/test_turn_command.py` gives.
"""

from helpers import (
    BASE,
    DOS,
    TWO,
    a_clean,
    a_move,
    a_query,
    deal,
    disposition,
    entries_of,
    held_open,
    place_on,
    the_chief,
)

from comment_review.commands import collate as collate_command
from comment_review.desk.dispositions.disposition import ORIGINAL
from comment_review.desk.mark import Shape
from comment_review.flows.proof_io import load_proof

RECAST = "# one\n# both\n# three\n"


def _closed(tmp_path):
    proof, why = load_proof(tmp_path / "final.json")
    assert proof is not None, why
    return proof


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
        assert code == collate_command.OK, out
        chief = the_chief(tmp_path)
        assert chief.role == "copy-chief"
        assert [m.change for m in entries_of(chief)] == [DOS]
        place = place_on(_closed(tmp_path), "m.py@b1")
        assert place["state"] == "stands"
        assert place["text"] == DOS
        assert place["disposition"]["side"] == "function-context"

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
        assert code == collate_command.OK, out
        assert entries_of(the_chief(tmp_path)) == []
        place = place_on(_closed(tmp_path), "m.py@b1")
        assert place["disposition"]["side"] == ORIGINAL
        assert place["text"] is None

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
        assert code == collate_command.OK, out
        assert [m.change for m in entries_of(the_chief(tmp_path))] == [RECAST]
        assert place_on(_closed(tmp_path), "m.py@b1")["text"] == RECAST

    def test_an_unsettlable_place_is_printed_for_the_human_and_not_ruled(
        self, tmp_path, monkeypatch, capsys
    ):
        texts = {"m.py@b1": BASE, "m.py@b2": "# four\n# five\n# six\n"}
        # function-context cleans m.py@b2, so the turn owes no answer there and
        # exits as the escalation at m.py@b1 alone, which `held_open` asserts.
        asked = {
            "block-context": {
                "m.py@b2": a_query("m.py@b2", Shape.HUMAN_REVIEW_NECESSARY)
            },
            "function-context": {"m.py@b2": a_clean("m.py@b2")},
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
        assert code == collate_command.OK, out
        assert "unsettlable m.py@b2: block-context asks the human" in out
        assert [m.address for m in entries_of(the_chief(tmp_path))] == ["m.py@b1"]
        assert place_on(_closed(tmp_path), "m.py@b2")["state"] == "unsettlable"


class TestAMoveHeldForTheHuman:
    """A move a role sent to the human prints as one entry naming both ends --
    `decision-log.md Process: #155` and `#182`. The author approves or refuses
    the move whole, so the paragraph dropped at one place and added at the
    other are one question, not two.
    """

    TEXTS = {"m.py@b1": "# one\n# two\n# three\n", "m.py@b2": "# four\n# five\n# six\n"}
    #: block-context moves b1's middle line to b2, which reads with it at the
    #: end; function-context puts the origin to the human, so both ends are
    #: held and the chief rules neither.
    PLANT = {
        "block-context": {
            "m.py@b1": a_move(
                "m.py@b1",
                "m.py@b2",
                change="# two\n",
                reads="# four\n# five\n# six\n# two",
            ),
            "m.py@b2": a_clean("m.py@b2"),
        },
        "function-context": {
            "m.py@b1": a_query("m.py@b1", Shape.HUMAN_REVIEW_NECESSARY),
            "m.py@b2": a_clean("m.py@b2"),
        },
    }

    def _closed(self, tmp_path, monkeypatch, capsys):
        deal(tmp_path, monkeypatch, capsys, self.PLANT, self.TEXTS)
        return disposition(tmp_path, monkeypatch, capsys, [], proof="proof0.json")

    def test_both_ends_are_one_entry(self, tmp_path, monkeypatch, capsys):
        code, out = self._closed(tmp_path, monkeypatch, capsys)
        assert code == collate_command.OK, out
        assert out.count("unsettlable ") == 1, out
        assert (
            "unsettlable m.py@b1 and m.py@b2: function-context asks the human" in out
        ), out

    def test_the_move_rides_with_the_entry(self, tmp_path, monkeypatch, capsys):
        """`test_disposition_prints_the_drop_with_the_held_origin` asked this
        of the old flow: the role that asks is not the role that moved, so the
        entry names the move as well as the question."""
        _code, out = self._closed(tmp_path, monkeypatch, capsys)
        assert (
            "block-context's move drops the paragraph at m.py@b1 and adds it at"
            " m.py@b2, one move" in out
        ), out


class TestRefusals:
    def test_an_unruled_place_is_BROKEN_naming_it_and_its_roles(
        self, tmp_path, monkeypatch, capsys
    ):
        held_open(tmp_path, monkeypatch, capsys)
        code, out = disposition(tmp_path, monkeypatch, capsys, [])
        assert code == collate_command.BROKEN
        assert "copy-chief m.py@b1: carried forward and not ruled on" in out
        assert "block-context, function-context" in out
        assert not (tmp_path / "chief.json").exists()
        assert not (tmp_path / "final.json").exists()

    def test_a_ruling_at_a_place_nothing_carries_forward_is_BROKEN(
        self, tmp_path, monkeypatch, capsys
    ):
        """The unsettlable place rides to the human (`Process: #90`), and a
        settled one is closed; neither is the chief's to rule."""
        texts = {"m.py@b1": BASE, "m.py@b2": "# four\n# five\n# six\n"}
        asked = {
            "block-context": {
                "m.py@b2": a_query("m.py@b2", Shape.HUMAN_REVIEW_NECESSARY)
            },
            "function-context": {"m.py@b2": a_clean("m.py@b2")},
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
                },
                {
                    "address": "m.py@b2",
                    "answer": "taken_in",
                    "side": "block-context",
                    "reason": "and this one",
                },
            ],
        )
        assert code == collate_command.BROKEN
        assert "copy-chief m.py@b2: not carried forward" in out
        assert not (tmp_path / "final.json").exists()

    def test_a_recast_without_prose_is_BROKEN(self, tmp_path, monkeypatch, capsys):
        held_open(tmp_path, monkeypatch, capsys)
        code, out = disposition(
            tmp_path,
            monkeypatch,
            capsys,
            [{"address": "m.py@b1", "answer": "recast", "reason": "r"}],
        )
        assert code == collate_command.BROKEN
        assert "needs `prose`" in out
        assert not (tmp_path / "final.json").exists()

    def test_a_roles_answer_is_not_the_chiefs(self, tmp_path, monkeypatch, capsys):
        held_open(tmp_path, monkeypatch, capsys)
        code, out = disposition(
            tmp_path,
            monkeypatch,
            capsys,
            [{"address": "m.py@b1", "answer": "correct", "reason": "r"}],
        )
        assert code == collate_command.BROKEN
        assert "the chief's ruling is owed here" in out

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
        assert code == collate_command.OK, out
        assert [m.change for m in entries_of(the_chief(tmp_path))] == [TWO]
