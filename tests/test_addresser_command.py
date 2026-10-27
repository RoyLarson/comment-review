"""`commands/addresser.py`: the CLI's console face, exercised over a REAL binder.

`commands/` ran at 0.0% coverage -- 537 statements -- before this file: nothing
had ever watched `_resolve_one` or `_check` run. Filed against
`TODO/addresser-answers-wrongly-at-exit-0.md`, which found them answering
wrongly at exit 0 after the eleven-field row cut (`e56bea9`) removed `start`,
`end`, `kind` and `declares` -- fields they still read.

Every row here comes from `bind()` over a page `page_for` actually built, never
a hand-written dict -- a fixture written in the shape the code expects can only
confirm.

`TestByLine` is `binder-defects` T22, `decision-log.md Process: #96`: the
lookup takes a line NUMBER of the original file and a series, opens the file at
the binder's root and answers from the PAGE -- so a place the default binder
filtered out as holding no prose still answers, and a mark may cite it.
"""

import io
import json
from contextlib import redirect_stdout
from dataclasses import replace

import pytest
from conftest import READ_FROM, SAMPLE, build, cue, run_command

from comment_review.binder.binder import bind
from comment_review.commands import addresser
from comment_review.commands.addresser import _check, _resolve_one
from comment_review.flows.page_for import page_of
from comment_review.reading.diagnostics import ReadFailure


def _rows():
    page = build(SAMPLE)
    return bind([page], read_from=READ_FROM).paragraphs


def test_resolve_prints_the_real_lines_not_none_none():
    """`_resolve_one` used to read `start`/`end`, fields no row carries since
    `e56bea9` -- printing `alpha.py:None-None` at exit 0 for every address."""
    rows = _rows()
    target = next(r for r in rows if r.anchor == "def f(x):" and cue(r) == "a1")
    address = target.address

    out = io.StringIO()
    with redirect_stdout(out):
        code = _resolve_one(address, rows)

    assert code == 0
    printed = out.getvalue()
    assert "None-None" not in printed
    assert f"{target.original_start}-{target.original_end}" in printed


def test_check_reports_the_real_span_for_a_shared_address():
    """`_check`'s SHARED report read `paragraph.get('start')`/`.get('end')`,
    fields no row carries since `e56bea9` -- so a shared address always
    reported `None-None` regardless of where it actually sits.

    Two real rows made to share one address by duplicating a row `bind()`
    produced -- not a hand-written dict -- so the values checked are the ones a
    binder would actually carry for a comment run and the interval it fills.
    """
    rows = _rows()
    target = next(r for r in rows if r.anchor == "def f(x):" and cue(r) == "a1")
    mine = [*rows, replace(target)]

    out = io.StringIO()
    with redirect_stdout(out):
        _check(mine)

    printed = out.getvalue()
    assert "SHARED" in printed
    assert "None-None" not in printed
    assert f"{target.original_start}-{target.original_end}" in printed


@pytest.fixture
def a_default_binder(tmp_path):
    """`SAMPLE` on disk under a root, and the DEFAULT binder over it -- the one
    a role is handed, with every place holding no prose filtered out.

    Returns the binder's path and the file's repo-relative name.
    """
    root = tmp_path / "repo"
    root.mkdir()
    (root / "m.py").write_text(SAMPLE, encoding="utf-8", newline="")
    page = page_of(root / "m.py", rel="m.py")
    assert not isinstance(page, ReadFailure), page
    binder = bind([page], read_from={"root": str(root), "revise": 0})
    where = tmp_path / "binder.json"
    where.write_text(json.dumps(binder.serialize()), encoding="utf-8")
    return where, "m.py"


class TestByLine:
    """`SAMPLE`'s lines, as the probe over `page_for` numbers them: code on 6,
    8, 11 and 12; `def g(y):` on 11 opens with an EMPTY gap above it (`b2`), no
    docstring (`a2`) and nothing beside it (`c2`) -- three places the default
    binder does not carry."""

    def _ask(self, monkeypatch, capsys, binder, *flags):
        return run_command(
            monkeypatch, capsys, addresser, "--binder", str(binder), *flags
        )

    def test_an_absent_gap_answers_on_a_default_binder(
        self, monkeypatch, capsys, a_default_binder
    ):
        """The FitPlan run lost four `add`s to this: the command read the
        filtered binder and reported *"no `b` place"* for a gap the file has."""
        binder, name = a_default_binder
        code, out = self._ask(
            monkeypatch, capsys, binder, "--file", name, "--line", "11", "--series", "b"
        )
        assert code == 0, out
        assert "m.py@b2" in out
        assert "ABSENT" in out

    def test_a_blank_line_inside_the_gap_names_the_same_gap(
        self, monkeypatch, capsys, a_default_binder
    ):
        binder, name = a_default_binder
        code, out = self._ask(
            monkeypatch, capsys, binder, "--file", name, "--line", "9", "--series", "b"
        )
        assert code == 0, out
        assert "m.py@b2" in out

    def test_a_held_place_says_so(self, monkeypatch, capsys, a_default_binder):
        binder, name = a_default_binder
        code, out = self._ask(
            monkeypatch, capsys, binder, "--file", name, "--line", "6", "--series", "a"
        )
        assert code == 0, out
        assert "m.py@a1" in out
        assert "HELD" in out

    def test_an_undocumented_declaration_has_an_absent_a(
        self, monkeypatch, capsys, a_default_binder
    ):
        binder, name = a_default_binder
        code, out = self._ask(
            monkeypatch, capsys, binder, "--file", name, "--line", "11", "--series", "a"
        )
        assert code == 0, out
        assert "m.py@a2" in out
        assert "ABSENT" in out

    def test_a_line_that_declares_nothing_has_no_a(
        self, monkeypatch, capsys, a_default_binder
    ):
        binder, name = a_default_binder
        code, out = self._ask(
            monkeypatch, capsys, binder, "--file", name, "--line", "8", "--series", "a"
        )
        assert code == 1
        assert "declares nothing" in out

    def test_the_room_beside_a_line_of_code(
        self, monkeypatch, capsys, a_default_binder
    ):
        binder, name = a_default_binder
        code, out = self._ask(
            monkeypatch, capsys, binder, "--file", name, "--line", "8", "--series", "c"
        )
        assert code == 0, out
        assert "m.py@c1" in out
        assert "HELD" in out

    def test_a_blank_line_has_no_room_beside_it(
        self, monkeypatch, capsys, a_default_binder
    ):
        binder, name = a_default_binder
        code, out = self._ask(
            monkeypatch, capsys, binder, "--file", name, "--line", "9", "--series", "c"
        )
        assert code == 1
        assert "holds no code" in out

    def test_the_file_matter_answers_both_ends(
        self, monkeypatch, capsys, a_default_binder
    ):
        """A file's own matter has exactly two places and no line tells them
        apart; both are printed and the caller chooses by ADDRESS."""
        binder, name = a_default_binder
        code, out = self._ask(
            monkeypatch, capsys, binder, "--file", name, "--line", "1", "--series", "f"
        )
        assert code == 0, out
        assert "m.py@f0" in out
        assert "m.py@f1" in out

    def test_a_line_the_file_does_not_have_is_refused(
        self, monkeypatch, capsys, a_default_binder
    ):
        binder, name = a_default_binder
        code, out = self._ask(
            monkeypatch, capsys, binder, "--file", name, "--line", "99", "--series", "b"
        )
        assert code == 1
        assert "12 lines" in out

    def test_a_file_the_root_does_not_hold_is_refused(
        self, monkeypatch, capsys, a_default_binder
    ):
        binder, _ = a_default_binder
        gone = ("--file", "gone.py", "--line", "1", "--series", "b")
        code, out = self._ask(monkeypatch, capsys, binder, *gone)
        assert code == 2
        assert "gone.py" in out

    def test_a_line_that_is_neither_a_number_nor_a_sentinel_is_a_usage_error(
        self, monkeypatch, capsys, a_default_binder
    ):
        binder, name = a_default_binder
        with pytest.raises(SystemExit) as exited:
            self._ask(
                monkeypatch,
                capsys,
                binder,
                "--file",
                name,
                "--line",
                "end",
                "--series",
                "a",
            )
        assert exited.value.code == 2

    def test_line_without_file_or_series_is_a_usage_error(
        self, monkeypatch, capsys, a_default_binder
    ):
        binder, _ = a_default_binder
        code, out = self._ask(monkeypatch, capsys, binder, "--line", "11")
        assert code == 2
        assert "--file" in out and "--series" in out


@pytest.fixture
def a_closing_binder(tmp_path):
    """`class A {}` and a foot comment, gathered: its `<eof>` `a` is `a2`, which
    no line of the file names."""
    root = tmp_path / "repo"
    root.mkdir()
    (root / "A.java").write_text("class A {}\n// foot\n", encoding="utf-8", newline="")
    page = page_of(root / "A.java", rel="A.java")
    assert not isinstance(page, ReadFailure), page
    binder = bind([page], read_from={"root": str(root), "revise": 0})
    where = tmp_path / "binder.json"
    where.write_text(json.dumps(binder.serialize()), encoding="utf-8")
    return where


class TestBySentinel:
    """`--line` takes `<module>` or `<eof>` in place of a number, and names the
    places each series emitted at that end of the file."""

    def _ask(self, monkeypatch, capsys, binder, line, series):
        return run_command(
            monkeypatch,
            capsys,
            addresser,
            *("--binder", str(binder), "--file", "A.java"),
            *("--line", line, "--series", series),
        )

    def test_the_closing_a_answers_at_eof(self, monkeypatch, capsys, a_closing_binder):
        code, out = self._ask(monkeypatch, capsys, a_closing_binder, "<eof>", "a")
        assert code == 0, out
        assert out.split() == ["A.java@a2", "'<eof>'", "ABSENT"]

    def test_the_modules_a_answers_at_module(
        self, monkeypatch, capsys, a_closing_binder
    ):
        code, out = self._ask(monkeypatch, capsys, a_closing_binder, "<module>", "a")
        assert code == 0, out
        assert out.split() == ["A.java@a0", "'<module>'", "ABSENT"]

    @pytest.mark.parametrize(("line", "place"), [("<module>", "f0"), ("<eof>", "f1")])
    def test_a_sentinel_names_one_end_of_the_files_matter(
        self, monkeypatch, capsys, a_closing_binder, line, place
    ):
        code, out = self._ask(monkeypatch, capsys, a_closing_binder, line, "f")
        assert code == 0, out
        assert out.split()[0] == f"A.java@{place}"
        assert len(out.splitlines()) == 1

    def test_a_series_with_no_place_at_a_sentinel_says_so(
        self, monkeypatch, capsys, a_closing_binder
    ):
        code, out = self._ask(monkeypatch, capsys, a_closing_binder, "<module>", "c")
        assert code == 1
        assert "<module>" in out and "no `c` place" in out

    def test_the_binder_still_checks(self, monkeypatch, capsys, a_closing_binder):
        code, out = run_command(
            monkeypatch, capsys, addresser, "--binder", str(a_closing_binder), "--check"
        )
        assert code == 0, out
