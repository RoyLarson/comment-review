"""`commands/addresser.py`: the CLI's console face, exercised over a REAL binder.

`commands/` ran at 0.0% coverage -- 537 statements -- before this file: nothing
had ever watched `_resolve_one` or `_check` run. Filed against
`TODO/addresser-answers-wrongly-at-exit-0.md`, which found them answering
wrongly at exit 0 after the eleven-field row cut (`e56bea9`) removed `start`,
`end`, `kind` and `declares` -- fields they still read.

Every row here comes from `bind()` over a page `page_for` actually built, never
a hand-written dict -- a fixture written in the shape the code expects can only
confirm.

`TestByLine` is `binder-defects` T22 and `an-empty-place-is-not-citable` T5:
the lookup takes a repo, a file in it, a line NUMBER and a series, and answers
from the PAGE alone -- no binder is read, so a place that holds no prose answers
like any other, and a mark may cite it.
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
def a_repo(tmp_path):
    """`SAMPLE` on disk under a root. Returns the root and the file's name."""
    root = tmp_path / "repo"
    root.mkdir()
    (root / "m.py").write_text(SAMPLE, encoding="utf-8", newline="")
    return root, "m.py"


class TestByLine:
    """`SAMPLE`'s lines, as the probe over `page_for` numbers them: code on 6,
    8, 11 and 12; `def g(y):` on 11 opens with an EMPTY gap above it (`b2`), no
    docstring (`a2`) and nothing beside it (`c2`) -- three places that hold no
    prose."""

    def _ask(self, monkeypatch, capsys, repo, *flags):
        return run_command(monkeypatch, capsys, addresser, "--repo", str(repo), *flags)

    def test_an_empty_gap_answers(self, monkeypatch, capsys, a_repo):
        """The FitPlan run lost four `add`s to this: the command read the
        filtered binder and reported *"no `b` place"* for a gap the file has."""
        repo, name = a_repo
        code, out = self._ask(
            monkeypatch, capsys, repo, "--file", name, "--line", "11", "--series", "b"
        )
        assert code == 0, out
        assert "m.py@b2" in out

    def test_a_blank_line_inside_the_gap_names_the_same_gap(
        self, monkeypatch, capsys, a_repo
    ):
        repo, name = a_repo
        code, out = self._ask(
            monkeypatch, capsys, repo, "--file", name, "--line", "9", "--series", "b"
        )
        assert code == 0, out
        assert "m.py@b2" in out

    def test_a_filled_place_answers(self, monkeypatch, capsys, a_repo):
        repo, name = a_repo
        code, out = self._ask(
            monkeypatch, capsys, repo, "--file", name, "--line", "6", "--series", "a"
        )
        assert code == 0, out
        assert "m.py@a1" in out

    def test_an_undocumented_declaration_has_an_absent_a(
        self, monkeypatch, capsys, a_repo
    ):
        repo, name = a_repo
        code, out = self._ask(
            monkeypatch, capsys, repo, "--file", name, "--line", "11", "--series", "a"
        )
        assert code == 0, out
        assert "m.py@a2" in out

    def test_a_line_that_declares_nothing_has_no_a(self, monkeypatch, capsys, a_repo):
        repo, name = a_repo
        code, out = self._ask(
            monkeypatch, capsys, repo, "--file", name, "--line", "8", "--series", "a"
        )
        assert code == 1
        assert "declares nothing" in out

    def test_the_room_beside_a_line_of_code(self, monkeypatch, capsys, a_repo):
        repo, name = a_repo
        code, out = self._ask(
            monkeypatch, capsys, repo, "--file", name, "--line", "8", "--series", "c"
        )
        assert code == 0, out
        assert "m.py@c1" in out

    def test_a_blank_line_has_no_room_beside_it(self, monkeypatch, capsys, a_repo):
        repo, name = a_repo
        code, out = self._ask(
            monkeypatch, capsys, repo, "--file", name, "--line", "9", "--series", "c"
        )
        assert code == 1
        assert "holds no code" in out

    def test_the_file_matter_answers_both_ends(self, monkeypatch, capsys, a_repo):
        """A file's own matter has exactly two places and no line tells them
        apart; both are printed and the caller chooses by ADDRESS."""
        repo, name = a_repo
        code, out = self._ask(
            monkeypatch, capsys, repo, "--file", name, "--line", "1", "--series", "f"
        )
        assert code == 0, out
        assert "m.py@f0" in out
        assert "m.py@f1" in out

    def test_a_line_the_file_does_not_have_is_refused(
        self, monkeypatch, capsys, a_repo
    ):
        repo, name = a_repo
        code, out = self._ask(
            monkeypatch, capsys, repo, "--file", name, "--line", "99", "--series", "b"
        )
        assert code == 1
        assert "12 lines" in out

    def test_a_file_the_root_does_not_hold_is_refused(
        self, monkeypatch, capsys, a_repo
    ):
        repo, _ = a_repo
        gone = ("--file", "gone.py", "--line", "1", "--series", "b")
        code, out = self._ask(monkeypatch, capsys, repo, *gone)
        assert code == 2
        assert "gone.py" in out

    def test_a_line_that_is_neither_a_number_nor_a_sentinel_is_a_usage_error(
        self, monkeypatch, capsys, a_repo
    ):
        repo, name = a_repo
        with pytest.raises(SystemExit) as exited:
            self._ask(
                monkeypatch,
                capsys,
                repo,
                "--file",
                name,
                "--line",
                "end",
                "--series",
                "a",
            )
        assert exited.value.code == 2

    def test_line_without_file_or_series_is_a_usage_error(
        self, monkeypatch, capsys, a_repo
    ):
        repo, _ = a_repo
        code, out = self._ask(monkeypatch, capsys, repo, "--line", "11")
        assert code == 2
        assert "--file" in out and "--series" in out

    def test_a_file_with_no_prose_answers_its_gap(self, monkeypatch, capsys, tmp_path):
        """A file holding no comment gathers to a binder with no paragraphs, and
        the lookup refused it before reading the page (2026-11-04). It reads no
        binder now."""
        repo = tmp_path / "bare"
        repo.mkdir()
        (repo / "n.py").write_text("x = 1\ny = 2\n", encoding="utf-8", newline="")
        code, out = self._ask(
            monkeypatch, capsys, repo, "--file", "n.py", "--line", "2", "--series", "b"
        )
        assert code == 0, out
        assert "n.py@b1" in out


@pytest.fixture
def an_ends_binder(tmp_path):
    """A declaration and a foot comment, gathered, and the file's name."""
    name = "A.rs"
    root = tmp_path / "repo"
    root.mkdir()
    (root / name).write_text("fn a() {}\n// foot\n", encoding="utf-8", newline="")
    page = page_of(root / name, rel=name)
    assert not isinstance(page, ReadFailure), page
    binder = bind([page], read_from={"root": str(root), "revise": 0})
    where = tmp_path / "binder.json"
    where.write_text(json.dumps(binder.serialize()), encoding="utf-8")
    return root, where, name


class TestBySentinel:
    """`--line` takes `<module>` or `<eof>` in place of a number, and names the
    places each series emitted at that end of the file."""

    def _ask(self, monkeypatch, capsys, repo, line, series, name):
        return run_command(
            monkeypatch,
            capsys,
            addresser,
            *("--repo", str(repo), "--file", name),
            *("--line", line, "--series", series),
        )

    def test_the_modules_a_answers_at_module(self, monkeypatch, capsys, an_ends_binder):
        repo, _, name = an_ends_binder
        code, out = self._ask(monkeypatch, capsys, repo, "<module>", "a", name)
        assert code == 0, out
        assert out.split() == [f"{name}@a0", "'<module>'"]

    @pytest.mark.parametrize(("line", "place"), [("<module>", "f0"), ("<eof>", "f1")])
    def test_a_sentinel_names_one_end_of_the_files_matter(
        self, monkeypatch, capsys, an_ends_binder, line, place
    ):
        repo, _, name = an_ends_binder
        code, out = self._ask(monkeypatch, capsys, repo, line, "f", name)
        assert code == 0, out
        assert out.split()[0] == f"{name}@{place}"
        assert len(out.splitlines()) == 1

    def test_a_series_with_no_place_at_a_sentinel_says_so(
        self, monkeypatch, capsys, an_ends_binder
    ):
        repo, _, name = an_ends_binder
        code, out = self._ask(monkeypatch, capsys, repo, "<module>", "c", name)
        assert code == 1
        assert "<module>" in out and "no `c` place" in out

    def test_the_usage_line_names_both_sentinels(self, monkeypatch, capsys):
        monkeypatch.setattr("sys.argv", ["addresser", "--help"])
        with pytest.raises(SystemExit):
            addresser.main()
        usage = capsys.readouterr().out.split("\n\n")[0]
        assert "--line N|<module>|<eof>" in " ".join(usage.split())

    def test_the_binder_still_checks(self, monkeypatch, capsys, an_ends_binder):
        _, binder, _ = an_ends_binder
        code, out = run_command(
            monkeypatch, capsys, addresser, "--binder", str(binder), "--check"
        )
        assert code == 0, out
