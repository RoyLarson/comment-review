"""The `disposition` command: the chief closes the proof, from the console.

! DRIVEN THROUGH `main()` AND `sys.argv` over the real chain -- `collate`
deals, `turn` holds the place open, `disposition` rules it. `P5` of
`docs/plans/0.2.4-the-turn-as-commands.md`, and T16's other half.

! THE EXIT CODES ARE `collate`'s, read there for the reason
`tests/test_turn_command.py` gives.
"""

import json

import pytest
from helpers import (
    BASE,
    DOS,
    TWO,
    a_clean,
    a_correct_setting,
    a_move,
    changes_of,
    deal,
    disposition,
    entries_of,
    held_open,
    place_on,
    the_chief,
    turn,
)

from comment_review.commands import collate as collate_command
from comment_review.desk.proof.disposition import ORIGINAL
from comment_review.desk.proof.mark import Instruction
from comment_review.flows.proof_io import load_proof
from comment_review.flows.transcribe import docket_of_proof

RECAST = "# one\n# both\n# three\n"


def _taken_in(address: str, side: str, reason: str) -> dict:
    return {"address": address, "answer": "taken_in", "side": side, "reason": reason}


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
        assert changes_of(entries_of(chief)) == [DOS]
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
        assert changes_of(entries_of(the_chief(tmp_path))) == [RECAST]
        assert place_on(_closed(tmp_path), "m.py@b1")["text"] == RECAST


class TestTheChiefRulesAMoveThenItsEnds:
    """The chief rules an undecided move's placement once, then its ends.

    `decision-log.md Process: #195` item 4 and `#201`: the placement ruling
    names the move by its two addresses and agrees or withdraws it; each end
    is then an ordinary place, and one that needs words is carried back to
    the chief, who rules it with `disposition` on the proof the first ruling
    wrote.
    """

    TEXTS = {"m.py@b1": "# one\n# two\n# three\n", "m.py@b2": "# four\n# five\n# six\n"}
    #: block-context moves b1's middle line to b2; function-context corrects
    #: b2 and is owed the placement.
    PLANT = {
        "block-context": {
            "m.py@b1": a_move(
                "m.py@b1",
                "m.py@b2",
                change="# two\n",
                reads="# four\n# five\n# six\n# two\n",
            ),
            "m.py@b2": a_clean("m.py@b2"),
        },
        "function-context": {
            "m.py@b1": a_clean("m.py@b1"),
            "m.py@b2": a_correct_setting("m.py@b2", "five", "# four\n# 5\n# six\n"),
        },
    }
    PLACEMENT = {
        "address": "m.py@b1",
        "to": "m.py@b2",
        "answer": "taken_in",
        "side": "block-context",
        "reason": "the line belongs with five",
    }
    #: The origin's paragraph with the moved line taken out of it.
    REMAINDER = "# one\n# three"
    CHIEFS_OWN = "# four\n# 5\n# six\n# two, as the chief words it\n"

    def _placed(self, tmp_path, monkeypatch, capsys):
        deal(tmp_path, monkeypatch, capsys, self.PLANT, self.TEXTS)
        return disposition(
            tmp_path, monkeypatch, capsys, [self.PLACEMENT], proof="proof0.json"
        )

    def test_the_placement_ruling_agrees_the_move_and_carries_its_ends(
        self, tmp_path, monkeypatch, capsys
    ):
        code, out = self._placed(tmp_path, monkeypatch, capsys)
        assert code in (collate_command.REREADS, collate_command.ESCALATIONS), out
        # The ends are carried, so the proof it writes is not closed yet.
        assert "the proof closed" not in out, out
        assert "the proof at turn 0 is not closed" in out, out
        placed = _closed(tmp_path)
        assert [m.placement for m in placed.moves] == ["agreed"]
        assert place_on(placed, "m.py@b1")["state"] == "composed"
        assert place_on(placed, "m.py@b2")["state"] in ("composed", "contested")

    def test_then_each_end_closes_on_its_own_ruling(
        self, tmp_path, monkeypatch, capsys
    ):
        self._placed(tmp_path, monkeypatch, capsys)
        code, out = disposition(
            tmp_path,
            monkeypatch,
            capsys,
            [
                _taken_in("m.py@b1", "block-context", "the remainder reads true"),
                {
                    "address": "m.py@b2",
                    "answer": "recast",
                    "reason": "the arrival and the correction together",
                    "prose": self.CHIEFS_OWN,
                },
            ],
            proof="final.json",
        )
        assert code == collate_command.OK, out
        closed = _closed(tmp_path)
        assert place_on(closed, "m.py@b1")["text"] == self.REMAINDER
        assert place_on(closed, "m.py@b2")["text"] == self.CHIEFS_OWN
        docket = docket_of_proof(closed, tmp_path / "repo")
        (schedule,) = docket.schedules
        assert [(one.cue, one.text) for one in schedule.alterations] == [
            ("b1", self.REMAINDER),
            ("b2", self.CHIEFS_OWN),
        ]

    def test_an_undecided_move_with_no_placement_ruling_is_BROKEN_naming_it(
        self, tmp_path, monkeypatch, capsys
    ):
        deal(tmp_path, monkeypatch, capsys, self.PLANT, self.TEXTS)
        code, out = disposition(tmp_path, monkeypatch, capsys, [], proof="proof0.json")
        assert code == collate_command.BROKEN, out
        assert "copy-chief m.py@b1 -> m.py@b2: the placement of this move" in out
        assert not (tmp_path / "final.json").exists()

    def test_a_ruling_at_an_end_of_an_undecided_move_is_BROKEN(
        self, tmp_path, monkeypatch, capsys
    ):
        deal(tmp_path, monkeypatch, capsys, self.PLANT, self.TEXTS)
        code, out = disposition(
            tmp_path,
            monkeypatch,
            capsys,
            [self.PLACEMENT, _taken_in("m.py@b2", "block-context", "too soon")],
            proof="proof0.json",
        )
        assert code == collate_command.BROKEN, out
        assert "copy-chief m.py@b2: an end of an undecided move" in out


#: The two paragraphs the add cases stand between: `m.py@b2` is the gap they
#: leave, which holds no prose, so the binder does not carry it and no seeded
#: copy has a slot there.
GAPPED = {"m.py@b1": "# one\n# two\n# three\n", "m.py@b3": "# four\n# five\n# six\n"}
EMPTY_PLACE = "m.py@b2"
ADDED = "# the gap wants a sentence\n"
#: The chief's own paragraph for that place.
RECAST_THERE = "# the chief's own sentence for the gap\n"

_CLEAN_ABOVE = {"address": "m.py@b1", "instruction": "clean", "reason": "reads true"}
_CLEAN_BELOW = {"address": "m.py@b3", "instruction": "clean", "reason": "reads true"}
THE_ADD = {
    "address": EMPTY_PLACE,
    "instruction": "add",
    "claim": {"missing": "why the gap is here", "anchor": "`v2`"},
    "reason": "the gap is explained nowhere",
    "sources": [{"cite": "m.py:1"}],
    "change": ADDED,
}


def _answer_every_slot(tmp_path, n: int, **fields) -> list[str]:
    """One answers file per role of batch `n`, every slot given `fields`."""
    batch = json.loads((tmp_path / f"batch{n}.json").read_text(encoding="utf-8"))
    out = []
    for role, slots in batch.items():
        path = tmp_path / f"answers{n}_{role}.json"
        path.write_text(
            json.dumps([{**slot, **fields} for slot in slots]), encoding="utf-8"
        )
        out.append(f"{role}={path}")
    return out


class TestTheChiefRecastsAnAdd:
    """The chief's recast at an add's empty place lands there as an `add`.

    Ported from `tests/test_turn.py::TestTheChiefRecastsAnAdd`,
    `decision-log.md Process: #157`: the recast at an empty place is an `add`
    whatever answer reached it first, so the chief's prose gets to the docket.
    A `correct` or a `patch` there would quote an empty paragraph and write
    nothing.

    block-context adds at the gap and everyone cleans the two real
    paragraphs, so the add is composed and put to function-context; that role
    answers with its own text, which contests the place; both then hold, and
    the chief recasts it.
    """

    @pytest.mark.parametrize(
        "answer",
        [
            pytest.param(
                {
                    "instruction": "correct",
                    "claim": {"false": "wants", "true": "needs"},
                    "change": ADDED.replace("wants", "needs"),
                    "reason": "the fixture says needs",
                },
                id="a-correct-first",
            ),
            pytest.param(
                {
                    "instruction": "patch",
                    "claim": {"from": "wants", "to": "needs"},
                    "change": ADDED.replace("wants", "needs"),
                    "reason": "the fixture says needs",
                },
                id="a-patch-first",
            ),
        ],
    )
    def test_the_recast_is_an_add_whatever_answer_comes_first(
        self, tmp_path, monkeypatch, capsys, answer
    ):
        code = deal(
            tmp_path,
            monkeypatch,
            capsys,
            texts=GAPPED,
            placed={
                "block-context": [_CLEAN_ABOVE, _CLEAN_BELOW, THE_ADD],
                "function-context": [_CLEAN_ABOVE, _CLEAN_BELOW],
            },
        )
        assert code == collate_command.REREADS
        code, out = turn(
            tmp_path, monkeypatch, capsys, 1, *_answer_every_slot(tmp_path, 1, **answer)
        )
        assert code == collate_command.ESCALATIONS, out
        code, out = turn(
            tmp_path,
            monkeypatch,
            capsys,
            2,
            *_answer_every_slot(tmp_path, 2, instruction="hold", reason="mine"),
        )
        assert code == collate_command.ESCALATIONS, out
        code, out = disposition(
            tmp_path,
            monkeypatch,
            capsys,
            [
                {
                    "address": EMPTY_PLACE,
                    "answer": "recast",
                    "reason": "neither wording carries it",
                    "prose": RECAST_THERE,
                }
            ],
            proof="proof2.json",
        )
        assert code == collate_command.OK, out
        marks = entries_of(the_chief(tmp_path))
        assert [(m.address, m.instruction) for m in marks] == [
            (EMPTY_PLACE, Instruction.ADD)
        ]
        assert changes_of(marks) == [RECAST_THERE]
        assert place_on(_closed(tmp_path), EMPTY_PLACE)["text"] == RECAST_THERE


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
        """A place the roles settled is closed, so it is not the chief's to
        rule."""
        texts = {"m.py@b1": BASE, "m.py@b2": "# four\n# five\n# six\n"}
        settled = {
            "block-context": {"m.py@b2": a_clean("m.py@b2")},
            "function-context": {"m.py@b2": a_clean("m.py@b2")},
        }
        held_open(tmp_path, monkeypatch, capsys, settled, texts)
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
        assert changes_of(entries_of(the_chief(tmp_path))) == [TWO]


def test_the_help_names_the_answer_the_parse_accepts():
    import comment_review.commands.disposition as disposition

    assert "taken-in" not in (disposition.__doc__ or "")
