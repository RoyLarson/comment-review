"""`commands/addresses.py`: the CLI's console face, over a real file in a repo.

Both lookups read the page from the file under `--repo` and no binder: a place
that holds no prose answers like any other, and a mark may cite it.
"""

import pytest
from conftest import SAMPLE, build, cue, run_command

from comment_review.commands import addresses


@pytest.fixture
def a_package(tmp_path):
    """`SAMPLE` at `pkg/m.py` under a root, and a file beside the root."""
    root = tmp_path / "repo"
    (root / "pkg").mkdir(parents=True)
    (root / "pkg" / "m.py").write_text(SAMPLE, encoding="utf-8", newline="")
    (tmp_path / "outside.py").write_text("SECRET = 1\n", encoding="utf-8")
    return root


class TestPaths:
    """Where the file is and how its path is spelled must not change the address.

    The address is the page's own: what `find` prints, `resolve` reads back, and
    nothing outside the root is read.
    """

    def _find(self, monkeypatch, capsys, repo, file, line="11", series="b"):
        return run_command(
            monkeypatch,
            capsys,
            addresses,
            *("find", "--repo", str(repo), "--file", file),
            *("--line", line, "--series", series),
        )

    def _resolve(self, monkeypatch, capsys, repo, address):
        return run_command(
            monkeypatch, capsys, addresses, "resolve", address, "--repo", str(repo)
        )

    def test_a_file_in_a_subdirectory(self, monkeypatch, capsys, a_package):
        code, out = self._find(monkeypatch, capsys, a_package, "pkg/m.py")
        assert code == 0, out
        assert out.split()[0] == "pkg:m.py@b2"

    def test_an_absolute_file_prints_the_same_address(
        self, monkeypatch, capsys, a_package
    ):
        absolute = str(a_package / "pkg" / "m.py")
        code, out = self._find(monkeypatch, capsys, a_package, absolute)
        assert code == 0, out
        assert out.split()[0] == "pkg:m.py@b2"

    def test_a_relative_root_reads_the_same_page(self, monkeypatch, capsys, a_package):
        monkeypatch.chdir(a_package.parent)
        code, out = self._resolve(monkeypatch, capsys, "repo", "pkg:m.py@a1")
        assert code == 0, out
        assert "None" not in out

    def test_what_find_prints_resolve_reads_back(self, monkeypatch, capsys, a_package):
        code, out = self._find(monkeypatch, capsys, a_package, "pkg/m.py", "6", "a")
        assert code == 0, out
        address = out.split()[0]
        code, out = self._resolve(monkeypatch, capsys, a_package, address)
        assert code == 0, out
        assert address in out

    @pytest.mark.parametrize("file", ["../outside.py", "pkg/../../outside.py"])
    def test_a_file_outside_the_root_is_refused(
        self, monkeypatch, capsys, a_package, file
    ):
        code, out = self._find(monkeypatch, capsys, a_package, file, "1", "c")
        assert code == 2
        assert "SECRET" not in out

    def test_an_address_outside_the_root_is_refused(
        self, monkeypatch, capsys, a_package
    ):
        code, out = self._resolve(monkeypatch, capsys, a_package, "..:outside.py@c0")
        assert code == 2
        assert "SECRET" not in out

    def test_an_address_with_no_path_is_not_an_address(
        self, monkeypatch, capsys, a_package
    ):
        code, out = self._resolve(monkeypatch, capsys, a_package, "@a1")
        assert code == 2
        assert "not an address" in out


class TestResolve:
    """An address in, the lines that cover it out, read from the file now."""

    def _ask(self, monkeypatch, capsys, repo, address):
        return run_command(
            monkeypatch, capsys, addresses, "resolve", address, "--repo", str(repo)
        )

    def test_a_filled_place_prints_its_lines(self, monkeypatch, capsys, a_repo):
        repo, name = a_repo
        target = next(
            p for p in build(SAMPLE) if p.anchor == "def f(x):" and cue(p) == "a1"
        )
        code, out = self._ask(monkeypatch, capsys, repo, f"{name}@a1")
        assert code == 0, out
        assert f"{target.original_start}-{target.original_end}" in out
        assert "None-None" not in out

    def test_an_empty_place_prints_as_one(self, monkeypatch, capsys, a_repo):
        """An empty place stands on no line: it prints as empty, beside the line
        of code it is anchored to, never as a span it does not have."""
        repo, name = a_repo
        code, out = self._ask(monkeypatch, capsys, repo, f"{name}@b2")
        assert code == 0, out
        assert out.startswith(f"{name}: empty, beside 'def g(y):'")
        assert "None" not in out

    def test_a_place_the_page_lacks_says_so(self, monkeypatch, capsys, a_repo):
        repo, name = a_repo
        code, out = self._ask(monkeypatch, capsys, repo, f"{name}@b99")
        assert code == 1
        assert "names no place" in out

    def test_a_string_with_no_place_is_not_an_address(
        self, monkeypatch, capsys, a_repo
    ):
        repo, name = a_repo
        code, out = self._ask(monkeypatch, capsys, repo, name)
        assert code == 2
        assert "not an address" in out


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
        return run_command(
            monkeypatch, capsys, addresses, "find", "--repo", str(repo), *flags
        )

    def test_an_empty_gap_answers(self, monkeypatch, capsys, a_repo):
        """A live run lost four `add`s to this: the command read the
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
        with pytest.raises(SystemExit) as exited:
            self._ask(monkeypatch, capsys, repo, "--line", "11")
        assert exited.value.code == 2
        err = capsys.readouterr().err
        assert "--file" in err and "--series" in err

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
def an_ends_repo(tmp_path):
    """A declaration and a foot comment on disk. Returns the root and the name."""
    name = "A.rs"
    root = tmp_path / "repo"
    root.mkdir()
    (root / name).write_text("fn a() {}\n// foot\n", encoding="utf-8", newline="")
    return root, name


class TestBySentinel:
    """`--line` takes `<module>` or `<eof>` in place of a number, and names the
    places each series emitted at that end of the file."""

    def _ask(self, monkeypatch, capsys, repo, line, series, name):
        return run_command(
            monkeypatch,
            capsys,
            addresses,
            *("find", "--repo", str(repo), "--file", name),
            *("--line", line, "--series", series),
        )

    def test_the_modules_a_answers_at_module(self, monkeypatch, capsys, an_ends_repo):
        repo, name = an_ends_repo
        code, out = self._ask(monkeypatch, capsys, repo, "<module>", "a", name)
        assert code == 0, out
        assert out.split() == [f"{name}@a0", "'<module>'"]

    @pytest.mark.parametrize(("line", "place"), [("<module>", "f0"), ("<eof>", "f1")])
    def test_a_sentinel_names_one_end_of_the_files_matter(
        self, monkeypatch, capsys, an_ends_repo, line, place
    ):
        repo, name = an_ends_repo
        code, out = self._ask(monkeypatch, capsys, repo, line, "f", name)
        assert code == 0, out
        assert out.split()[0] == f"{name}@{place}"
        assert len(out.splitlines()) == 1

    def test_a_series_with_no_place_at_a_sentinel_says_so(
        self, monkeypatch, capsys, an_ends_repo
    ):
        repo, name = an_ends_repo
        code, out = self._ask(monkeypatch, capsys, repo, "<module>", "c", name)
        assert code == 1
        assert "<module>" in out and "no `c` place" in out

    def test_the_usage_line_names_both_sentinels(self, monkeypatch, capsys):
        monkeypatch.setattr("sys.argv", ["addresses", "find", "--help"])
        with pytest.raises(SystemExit):
            addresses.main()
        usage = capsys.readouterr().out.split("\n\n")[0]
        assert "--line N|<module>|<eof>" in " ".join(usage.split())
