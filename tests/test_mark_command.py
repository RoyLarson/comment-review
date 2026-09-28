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
from comment_review.desk.marks.rules import validate
from comment_review.desk.proof.mark import read_mark
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


#: What a compacting stage admits -- `decision-log.md Process: #193`, Roy:
#: *"Then they only get to patch, drop, add, the edits"*, and `clean` for a
#: dealt paragraph the role cannot condense without cutting evidence.
ADMITTED = ("patch", "drop", "add", "clean")


class TestAStageAdmitsSomeInstructionsAndNotOthers:
    """A stage's row says what its roles may file, and the copy carries it.

    `mark` refuses the rest as it places, so a role learns the rule from the
    refusal rather than from the fold, three commands later.
    """

    @pytest.fixture
    def dealt(self, tmp_path, monkeypatch, capsys) -> _Run:
        run = _Run(tmp_path, monkeypatch, capsys)
        copy = run.copy()
        run.copy_path.write_text(
            json.dumps({**copy, "stage": "6", "admits": list(ADMITTED)}),
            encoding="utf-8",
        )
        return run

    def test_an_instruction_the_stage_does_not_admit_is_refused_by_name(self, dealt):
        code, out = dealt(*CORRECT)
        assert code == command.BROKEN, out
        assert "correct" in out
        assert "6" in out
        for admitted in ADMITTED:
            assert admitted in out

    def test_nothing_is_placed_by_a_refused_ruling(self, dealt):
        dealt(*CORRECT)
        assert dealt.copy()["sheets"][0]["marks"][0]["instruction"] is None

    def test_an_instruction_it_admits_is_placed(self, dealt):
        code, out = dealt(
            "--address",
            "m.py@b1",
            "--instruction",
            "patch",
            "--from",
            "# one\n# two\n# three",
            "--to",
            "# one and two",
            "--reason",
            "three lines where one says it",
            "--change",
            "# one and two",
        )
        assert code == command.OK, out
        assert dealt.copy()["sheets"][0]["marks"][0]["instruction"] == "patch"

    def test_a_copy_naming_no_stage_admits_every_instruction(self, run):
        """An ordinary stage's copy carries no `admits`, and the seven
        instructions are what its role may file, as before."""
        code, out = run(*CORRECT)
        assert code == command.OK, out


class TestARulingIsPlaced:
    def test_a_correct_lands_with_its_change_derived_and_its_line_quoted(self, run):
        code, out = run(*CORRECT)
        assert code == command.OK, out
        assert "m.py@b1" in out and "correct" in out
        slot = run.copy()["sheets"][0]["marks"][0]
        assert slot["instruction"] == "correct"
        assert slot["change"] == "# one\n# 2\n# three\n"
        assert slot["sources"] == [{"cite": "m.py:5", "verbatim": "y = 2"}]
        mark, why = read_mark("m.py@b1", slot, validate)
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


#: An `add` at `m.py@b1`, which already holds `BASE` -- so the paragraph as it
#: will read is owed (`decision-log.md Process: #176`).
ADD_OVER_PROSE: tuple[str, ...] = (
    "--address",
    "m.py@b1",
    "--instruction",
    "add",
    "--missing",
    "nothing says why the count is three",
    "--anchor",
    "`three`",
    "--reason",
    "the run of three is unexplained",
    "--cite",
    "m.py:5",
    "--change",
    "# and that is all of them\n",
)


class TestAnAddAndAMoveCarryTheParagraphAsItWillRead:
    """`decision-log.md Process: #175` and `#176`, through the console."""

    def test_an_add_over_prose_takes_its_raw_text_from_a_file(self, run):
        reads = "# one\n# two\n# three\n# and that is all of them\n"
        (run.dir / "reads.txt").write_text(reads, encoding="utf-8")
        code, out = run(*ADD_OVER_PROSE, "--raw-text", "@" + str(run.dir / "reads.txt"))
        assert code == command.OK, out
        slot = run.copy()["sheets"][0]["marks"][0]
        assert slot["raw_text"] == reads
        assert slot["change"] == "# and that is all of them\n"

    def test_a_raw_text_spelled_flag_equals_at_path_is_read_too(self, run):
        reads = "# one\n# two\n# three\n# and that is all of them\n"
        (run.dir / "reads.txt").write_text(reads, encoding="utf-8")
        code, out = run(*ADD_OVER_PROSE, "--raw-text=@" + str(run.dir / "reads.txt"))
        assert code == command.OK, out
        assert run.copy()["sheets"][0]["marks"][0]["raw_text"] == reads

    def test_an_add_over_prose_with_no_raw_text_is_refused(self, run):
        before = run.copy()
        code, out = run(*ADD_OVER_PROSE)
        assert code == command.BROKEN
        assert "--raw-text" in out and "m.py@b1" in out
        assert run.copy() == before

    def test_a_move_places_its_snippet_and_its_destination_text(self, run):
        code, out = run(
            "--address",
            "m.py@b1",
            "--instruction",
            "move",
            "--from",
            "m.py@b1",
            "--to",
            "m.py@b5",
            "--change",
            "# two\n",
            "--raw-text",
            "# two\n",
            "--reason",
            "the note belongs beside the code it describes",
            "--cite",
            "m.py:5",
        )
        assert code == command.OK, out
        slot = run.copy()["sheets"][0]["marks"][0]
        assert slot["change"] == "# two\n"
        assert slot["raw_text"] == "# two\n"


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
