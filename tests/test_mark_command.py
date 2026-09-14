"""The `mark` command: one ruling placed on a copy from the console.

! DRIVEN THROUGH `main()` AND `sys.argv` via `conftest.run_command`, so every
flag is parsed by the command's own argparse. Inputs are real -- a binder
from `a_binder_over`, a copy from the real `seed`, a checkout under
`tmp_path`.

! WHERE THE EXPECTATIONS COME FROM: Roy's rulings of 2026-09-07 --
one invocation per ruling, `@path` for a value that spans lines, `--cite`
repeatable with `--ran` binding to the cite before it, and no bulk pass.
"""

import json

import pytest
from conftest import run_command
from helpers import a_binder_over

from comment_review.commands import mark as command
from comment_review.desk.mark import Mark
from comment_review.flows.distribute import seed

BASE = "# one\n# two\n# three\n"
PAGE = "x = 1\n# one\n# two\n# three\ny = 2\n"


class _Run:
    """A copy and a checkout on disk. Calling it runs `mark` with the flags
    given and returns `(exit code, stdout)`; `copy()` reads the copy as it
    now stands."""

    def __init__(self, tmp_path, monkeypatch, capsys):
        self.dir = tmp_path
        self._monkeypatch = monkeypatch
        self._capsys = capsys
        (tmp_path / "m.py").write_text(PAGE, encoding="utf-8")
        self.copy_path = tmp_path / "copy.json"
        binder = a_binder_over({"m.py@b1": BASE, "m.py@b5": BASE})
        self.copy_path.write_text(
            json.dumps(seed(binder, "block-context")), encoding="utf-8"
        )

    def __call__(self, *flags: str):
        return run_command(
            self._monkeypatch,
            self._capsys,
            command,
            "--edit-copy",
            str(self.copy_path),
            "--repo",
            str(self.dir),
            *flags,
        )

    def copy(self) -> dict:
        return json.loads(self.copy_path.read_text(encoding="utf-8"))


@pytest.fixture
def run(tmp_path, monkeypatch, capsys) -> _Run:
    return _Run(tmp_path, monkeypatch, capsys)


CORRECT: tuple[str, ...] = (
    "--address",
    "m.py@b1",
    "--instruction",
    "correct",
    "--false",
    "two",
    "--true",
    "2",
    "--reason",
    "the count moved",
    "--cite",
    "m.py:5",
)


class TestARulingIsPlaced:
    def test_a_correct_lands_with_its_change_derived_and_its_line_quoted(self, run):
        code, out = run(*CORRECT)
        assert code == command.OK, out
        assert "m.py@b1" in out and "correct" in out
        slot = run.copy()["sheets"][0]["marks"][0]
        assert slot["instruction"] == "correct"
        assert slot["change"] == "# one\n# 2\n# three\n"
        assert slot["sources"] == [{"cite": "m.py:5", "verbatim": "y = 2"}]
        mark, why = Mark.deserialize("m.py@b1", slot)
        assert why == [] and mark is not None

    def test_the_other_slot_is_still_null(self, run):
        run(*CORRECT)
        assert run.copy()["sheets"][0]["marks"][1]["instruction"] is None

    def test_a_value_spelled_at_path_is_read_from_that_file(self, run):
        (run.dir / "true.txt").write_text("two and\n# three", encoding="utf-8")
        flags = list(CORRECT)
        flags[flags.index("two")] = "two\n# three"
        flags[flags.index("2")] = "@" + str(run.dir / "true.txt")
        code, out = run(*flags)
        assert code == command.OK, out
        assert (
            run.copy()["sheets"][0]["marks"][0]["change"]
            == "# one\n# two and\n# three\n"
        )

    def test_a_value_spelled_flag_equals_at_path_is_read_from_that_file(self, run):
        """`mark-defects` T23. argparse takes `--true=@f` as it takes `--true
        @f`, but an `@path` was expanded only as a token of its own, so the
        literal path was saved as the clause and inside the derived change --
        measured 2026-09-14, module-context 1 saved eight marks that way and
        `check` passed them."""
        (run.dir / "true.txt").write_text("2", encoding="utf-8")
        flags = list(CORRECT)
        at = flags.index("--true")
        flags[at : at + 2] = ["--true=@" + str(run.dir / "true.txt")]
        code, out = run(*flags)
        assert code == command.OK, out
        slot = run.copy()["sheets"][0]["marks"][0]
        assert slot["claim"]["true"] == "2"
        assert slot["change"] == "# one\n# 2\n# three\n"

    def test_a_flag_equals_at_path_that_cannot_be_read_exits_two(self, run):
        flags = list(CORRECT)
        at = flags.index("--true")
        flags[at : at + 2] = ["--true=@" + str(run.dir / "missing.txt")]
        code, _ = run(*flags)
        assert code == command.UNREADABLE

    def test_withdraw_takes_a_placed_mark_back(self, run):
        """`mark-defects` T24, through the command: the slot is handed back as
        it was seeded, and the role places its ruling again."""
        run(*CORRECT)
        code, out = run("--address", "m.py@b1", "--withdraw")
        assert code == command.OK, out
        assert "m.py@b1" in out and "withdrawn" in out
        slot = run.copy()["sheets"][0]["marks"][0]
        assert slot["instruction"] is None and "claim" not in slot

    def test_withdraw_where_nothing_is_placed_is_refused(self, run):
        code, out = run("--address", "m.py@b1", "--withdraw")
        assert code == command.BROKEN
        assert "nothing is placed" in out

    def test_ran_binds_to_the_cite_before_it(self, run):
        code, out = run(*CORRECT, "--cite", "m.py:1", "--ran", "rg -n x m.py")
        assert code == command.OK, out
        assert run.copy()["sheets"][0]["marks"][0]["sources"] == [
            {"cite": "m.py:5", "verbatim": "y = 2"},
            {"cite": "m.py:1", "verbatim": "x = 1", "ran": "rg -n x m.py"},
        ]

    def test_a_verbatim_given_overrides_the_read(self, run):
        code, out = run(*CORRECT, "--verbatim", "y = 2  # given")
        assert code == command.OK, out
        assert run.copy()["sheets"][0]["marks"][0]["sources"] == [
            {"cite": "m.py:5", "verbatim": "y = 2  # given"}
        ]


class TestARefusalWritesNothing:
    def test_a_claim_flag_the_row_does_not_carry(self, run):
        before = run.copy()
        code, out = run(*CORRECT, "--drop", "two")
        assert code == command.BROKEN
        assert "--drop" in out and "correct" in out
        assert run.copy() == before

    def test_a_clause_not_in_the_paragraph(self, run):
        before = run.copy()
        flags = list(CORRECT)
        flags[flags.index("two")] = "four"
        code, out = run(*flags)
        assert code == command.BROKEN
        assert "`claim.false`" in out
        assert run.copy() == before

    def test_a_missing_reason_is_named_by_the_parse(self, run):
        flags = [f for f in CORRECT if f not in ("--reason", "the count moved")]
        code, out = run(*flags)
        assert code == command.BROKEN
        assert "reason" in out

    def test_ran_before_any_cite_is_a_usage_error(self, run):
        with pytest.raises(SystemExit) as raised:
            run("--address", "m.py@b1", "--instruction", "correct", "--ran", "rg")
        assert raised.value.code == 2

    def test_a_copy_that_is_not_json_exits_two(self, tmp_path, monkeypatch, capsys):
        path = tmp_path / "copy.json"
        path.write_text("not json", encoding="utf-8")
        code, out = run_command(
            monkeypatch,
            capsys,
            command,
            "--edit-copy",
            str(path),
            *CORRECT,
            with_stderr=True,
        )
        assert code == command.UNREADABLE
        assert out

    def test_an_at_path_that_cannot_be_read_exits_two(self, run):
        flags = list(CORRECT)
        flags[flags.index("2")] = "@" + str(run.dir / "missing.txt")
        code, _ = run(*flags)
        assert code == command.UNREADABLE


def test_mark_is_in_COMMANDS():
    from comment_review.__main__ import COMMANDS

    assert "mark" in COMMANDS
