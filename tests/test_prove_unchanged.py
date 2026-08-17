"""Code identity is proven by a script, not asserted by an agent."""

import subprocess  # noqa: I001  -- path shim below must import before prove_unchanged
import sys
import tempfile
import unittest
from pathlib import Path

from _paths import FIXTURES, SCRIPTS  # noqa: F401
import prove_unchanged as pu


def _write(path: Path, text: str) -> None:
    """Write with NO newline translation, so a test controls endings exactly.

    `Path.write_text` defaults to `newline=None`, which on Windows turns
    every `\\n` in `text` into `\\r\\n` on write -- silently defeating any
    fixture that means to plant a specific line ending.
    """
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


PY_BEFORE = '''"""Old summary."""


def add(a, b):
    """Old docstring."""
    # an old comment
    return a + b
'''

PY_COMMENT_ONLY = '''"""New summary."""


def add(a, b):
    """New docstring."""
    # a new comment
    return a + b
'''

PY_CODE_CHANGED = '''"""Old summary."""


def add(a, b):
    """Old docstring."""
    # an old comment
    return a - b
'''

GO_BEFORE = "// old doc\nfunc Add(a, b int) int {\n\treturn a + b\n}\n"
GO_COMMENT_ONLY = (
    "// new doc\n// second line\nfunc Add(a, b int) int {\n\treturn a + b\n}\n"
)
GO_CODE_CHANGED = "// old doc\nfunc Add(a, b int) int {\n\treturn a - b\n}\n"

# A code change hidden behind a TRAILING comment, on the same line. The
# original fixtures above put every comment on its own line, which is why a
# `_without_comments` that drops a trailing-comment block's whole LINE (rather than
# just its comment tail) still passed them.
GO_TRAILING_BEFORE = "func Add(a, b int) int {\n\treturn a + b // sum\n}\n"
GO_TRAILING_CODE_CHANGED = "func Add(a, b int) int {\n\treturn a - b // sum\n}\n"

# Code sharing a line with a block-comment DELIMITER. Census stores the
# whole line for the opening/closing line of a block comment, so a line that
# is genuinely all-comment and a line that merely OPENS a comment mid-code
# are stored identically -- string equality alone cannot tell them apart.
C_MIDLINE_BEFORE = "int x = /* why */ 5;\nint y = 6;\n"
C_MIDLINE_CHANGED = "int x = /* why */ 7;\nint y = 6;\n"

# A file that is comment top to bottom: the stripped text is legitimately empty.
GO_ALL_COMMENT = "// just a comment\n// and another\n"

# An UNTERMINATED block comment. The lexer swallows every line below the opener
# into one run, so `func B` never reaches the stripped text -- and the surviving
# `func A() {}` makes the stripped text SHORT and plausible rather than empty, which
# is why the stripped-to-nothing guard does not catch this shape.
GO_RUNAWAY_BEFORE = "func A() {}\n/* note\nfunc B() {}\n"
GO_RUNAWAY_CODE_CHANGED = "func A() {}\n/* note edited\nfunc C() { panic(1) }\n"


class TestPythonProof(unittest.TestCase):
    def test_prose_only_change_is_proven(self):
        path = Path("x.py")
        self.assertEqual(
            pu.code_fingerprint(PY_BEFORE, path),
            pu.code_fingerprint(PY_COMMENT_ONLY, path),
        )

    def test_a_code_change_is_caught(self):
        path = Path("x.py")
        self.assertNotEqual(
            pu.code_fingerprint(PY_BEFORE, path),
            pu.code_fingerprint(PY_CODE_CHANGED, path),
        )

    def test_the_proof_kind_is_named(self):
        kind, _ = pu.code_fingerprint(PY_BEFORE, Path("x.py"))
        self.assertEqual(kind, "ast")


class TestLexicalProof(unittest.TestCase):
    def test_prose_only_change_is_proven(self):
        path = Path("x.go")
        self.assertEqual(
            pu.code_fingerprint(GO_BEFORE, path),
            pu.code_fingerprint(GO_COMMENT_ONLY, path),
        )

    def test_a_code_change_is_caught(self):
        path = Path("x.go")
        self.assertNotEqual(
            pu.code_fingerprint(GO_BEFORE, path),
            pu.code_fingerprint(GO_CODE_CHANGED, path),
        )

    def test_the_proof_kind_is_named(self):
        kind, _ = pu.code_fingerprint(GO_BEFORE, Path("x.go"))
        self.assertEqual(kind, "stripped")


class TestUnprovable(unittest.TestCase):
    def test_an_unknown_suffix_is_reported_not_passed(self):
        kind, _ = pu.code_fingerprint("whatever\n", Path("x.zzz"))
        self.assertEqual(kind, "unprovable")

    def test_a_syntax_error_falls_back_to_without_comments_not_to_success(self):
        kind, _ = pu.code_fingerprint("def (:\n", Path("x.py"))
        self.assertIn(kind, ("stripped", "unprovable"))


class TestLineEndings(unittest.TestCase):
    def test_crlf_detected(self):
        self.assertEqual(pu.dominant_ending("a\r\nb\r\n"), "crlf")

    def test_lf_detected(self):
        self.assertEqual(pu.dominant_ending("a\nb\n"), "lf")

    def test_a_flip_is_visible(self):
        self.assertNotEqual(pu.dominant_ending("a\r\n"), pu.dominant_ending("a\n"))


class TestTrailingCommentExactness(unittest.TestCase):
    """A trailing comment's block spans the CODE line it sits on.

    Dropping the whole line erases the code, not just the comment, and two
    texts differing only in that code then stripped-compare EQUAL -- a false
    PROVEN on the exact case the trailing-comment kind exists to describe.
    """

    def test_a_code_change_behind_a_trailing_comment_is_caught(self):
        path = Path("x.go")
        self.assertNotEqual(
            pu.code_fingerprint(GO_TRAILING_BEFORE, path),
            pu.code_fingerprint(GO_TRAILING_CODE_CHANGED, path),
        )


class TestBlockCommentMidlineIsUnprovable(unittest.TestCase):
    """Code beside a block-comment delimiter is refused, never guessed at."""

    def test_code_beside_a_block_comment_opener_is_unprovable(self):
        kind, _ = pu.code_fingerprint(C_MIDLINE_BEFORE, Path("x.c"))
        self.assertEqual(kind, "unprovable")

    def test_it_stays_unprovable_even_though_only_a_literal_changed(self):
        # The DANGEROUS shape: before/after differ only in the value beside
        # the delimiter. A stripped text that dropped the whole line would compare
        # them equal (the differing value was never in the stripped text at all).
        kind, _ = pu.code_fingerprint(C_MIDLINE_CHANGED, Path("x.c"))
        self.assertEqual(kind, "unprovable")


class TestStrippingToNothingIsUnprovable(unittest.TestCase):
    """`"" == ""` proves nothing: an all-comment file must not read PROVEN."""

    def test_an_all_comment_file_is_unprovable_not_proven(self):
        kind, _ = pu.code_fingerprint(GO_ALL_COMMENT, Path("x.go"))
        self.assertEqual(kind, "unprovable")

    def test_a_genuinely_empty_file_is_still_provable(self):
        # The rule is "empty stripped text from NON-empty input", not "empty
        # stripped text" outright -- two truly empty files ARE identical.
        kind, _ = pu.code_fingerprint("", Path("x.go"))
        self.assertEqual(kind, "stripped")


class TestUnterminatedBlockCommentIsUnprovable(unittest.TestCase):
    """C1: a runaway `/*` hid a code change behind an equal, plausible stripped text.

    Both files strip to `func A() {}`, so the fingerprints compared EQUAL and
    the report read PROVEN while `func B` had become `func C() { panic(1) }`.
    The stripped-to-nothing guard cannot see this: some code survived.
    """

    def test_the_without_comments_is_refused_not_compared(self):
        kind, _ = pu.code_fingerprint(GO_RUNAWAY_BEFORE, Path("x.go"))
        self.assertEqual(kind, "unprovable")

    def test_a_code_change_behind_the_runaway_opener_is_not_proven(self):
        path = Path("x.go")
        before = pu.code_fingerprint(GO_RUNAWAY_BEFORE, path)
        after = pu.code_fingerprint(GO_RUNAWAY_CODE_CHANGED, path)
        self.assertEqual(before[0], "unprovable")
        self.assertEqual(after[0], "unprovable")


class TestSiblingSkipsUnreadable(unittest.TestCase):
    """`_sibling` must not commit to the first NAME it finds -- try the next."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name) / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        self.target = self.repo / "target.py"
        _write(self.target, "x = 1\n")
        # Sorts BEFORE the good sibling, so a "first match wins" _sibling
        # would return this one and silently disable the ending check.
        self.binary_sibling = self.repo / "aaa_binary.bin"
        self.binary_sibling.write_bytes(b"\xff\xfe\x00\x01not-utf8")
        self.good_sibling = self.repo / "zzz_good.py"
        _write(self.good_sibling, "y = 2\n")
        subprocess.run(
            [
                "git",
                "-C",
                str(self.repo),
                "add",
                "target.py",
                "aaa_binary.bin",
                "zzz_good.py",
            ],
            check=True,
        )
        subprocess.run(
            [
                "git",
                "-C",
                str(self.repo),
                "-c",
                "user.email=t@t",
                "-c",
                "user.name=t",
                "commit",
                "-qm",
                "init",
            ],
            check=True,
        )

    def tearDown(self):
        self.tmp.cleanup()

    def test_an_unreadable_candidate_is_skipped_for_a_readable_one(self):
        tracked = pu.git_ls_files(self.repo) or []
        sib = pu._sibling(self.repo, self.target, {self.target.resolve()}, tracked)
        self.assertEqual(sib, self.good_sibling.resolve())


class TestCLI(unittest.TestCase):
    """`main()` end to end -- exit code and the labels it prints, for real."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name) / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        self.target = self.repo / "add.py"
        _write(
            self.target,
            '"""Old summary."""\n\n\ndef add(a, b):\n'
            '    """Old docstring."""\n    # an old comment\n    return a + b\n',
        )
        self.sibling = self.repo / "sibling.py"
        _write(self.sibling, '"""A sibling nobody edits."""\n')
        subprocess.run(
            ["git", "-C", str(self.repo), "add", "add.py", "sibling.py"], check=True
        )
        subprocess.run(
            [
                "git",
                "-C",
                str(self.repo),
                "-c",
                "user.email=t@t",
                "-c",
                "user.name=t",
                "commit",
                "-qm",
                "init",
            ],
            check=True,
        )

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, *paths):
        cmd = [
            sys.executable,
            str(SCRIPTS / "prove_unchanged.py"),
            "--base",
            "HEAD",
            "--repo",
            str(self.repo),
            *[str(p) for p in paths],
        ]
        return subprocess.run(
            cmd, capture_output=True, text=True, encoding="utf-8", check=False
        )

    def test_exit_0_on_a_prose_only_change(self):
        _write(
            self.target,
            '"""New summary."""\n\n\ndef add(a, b):\n'
            '    """New docstring."""\n    # a NEW comment\n    return a + b\n',
        )
        result = self._run(self.target)
        self.assertEqual(result.returncode, 0)
        self.assertIn("PROVEN", result.stdout)

    def test_exit_1_on_a_code_change(self):
        _write(
            self.target,
            '"""Old summary."""\n\n\ndef add(a, b):\n'
            '    """Old docstring."""\n    # an old comment\n    return a - b\n',
        )
        result = self._run(self.target)
        self.assertEqual(result.returncode, 1)
        self.assertIn("FAIL", result.stdout)

    def test_exit_1_on_an_unprovable_file(self):
        unknown = self.repo / "data.xyz"
        _write(unknown, "whatever\n")
        subprocess.run(["git", "-C", str(self.repo), "add", "data.xyz"], check=True)
        subprocess.run(
            [
                "git",
                "-C",
                str(self.repo),
                "-c",
                "user.email=t@t",
                "-c",
                "user.name=t",
                "commit",
                "-qm",
                "add unknown",
            ],
            check=True,
        )
        _write(unknown, "whatever, still\n")
        result = self._run(unknown)
        self.assertEqual(result.returncode, 1)
        self.assertIn("UNPROVABLE", result.stdout)

    def test_a_code_change_behind_a_runaway_block_comment_does_not_read_proven(self):
        # C1 end to end. A fingerprint-level test only shows the stripped text is
        # refused; only the CLI shows that PROVEN is never printed and the
        # exit code changes -- the distinction that let this ship.
        runaway = self.repo / "runaway.go"
        _write(runaway, "func A() {}\n/* note\nfunc B() {}\n")
        subprocess.run(["git", "-C", str(self.repo), "add", "runaway.go"], check=True)
        subprocess.run(
            [
                "git",
                "-C",
                str(self.repo),
                "-c",
                "user.email=t@t",
                "-c",
                "user.name=t",
                "commit",
                "-qm",
                "add runaway",
            ],
            check=True,
        )
        _write(runaway, "func A() {}\n/* note edited\nfunc C() { panic(1) }\n")
        result = self._run(runaway)
        self.assertEqual(result.returncode, 1)
        self.assertIn("UNPROVABLE", result.stdout)
        self.assertNotIn("PROVEN", result.stdout)

    def test_a_line_ending_mismatch_against_the_sibling_fails(self):
        crlf_text = (
            '"""New summary."""\r\n\r\n\r\ndef add(a, b):\r\n'
            '    """New docstring."""\r\n    # a new comment\r\n    return a + b\r\n'
        )
        _write(self.target, crlf_text)  # sibling.py stays LF
        result = self._run(self.target)
        self.assertEqual(result.returncode, 1)
        self.assertIn("line endings", result.stdout)

    def test_a_genuinely_crlf_pair_does_not_false_fail(self):
        # The regression this guards: reading the edited file with universal
        # newlines makes a REAL crlf file measure as "lf", so on a crlf tree
        # this check used to FAIL every single file it looked at.
        crlf_target = (
            '"""New summary."""\r\n\r\n\r\ndef add(a, b):\r\n'
            '    """New docstring."""\r\n    # a new comment\r\n    return a + b\r\n'
        )
        _write(self.target, crlf_target)
        _write(self.sibling, '"""A sibling nobody edits."""\r\n')
        result = self._run(self.target)
        self.assertEqual(result.returncode, 0)
        self.assertNotIn("line endings", result.stdout)

    def test_a_file_with_no_line_ending_at_all_does_not_fail_the_check(self):
        # Minor: a single-line file with no trailing newline measures "none",
        # which is not a WRONG ending -- it is an absent one. Guarding only
        # `want` failed such a file against any CRLF sibling.
        _write(self.sibling, '"""A sibling nobody edits."""\r\n')
        _write(self.target, "x = 1")  # no trailing newline at all
        result = self._run(self.target)
        self.assertNotIn("line endings", result.stdout)

    def test_no_readable_sibling_is_unchecked_but_still_exits_0(self):
        lonely_dir = self.repo / "lonely"
        lonely_dir.mkdir()
        lonely = lonely_dir / "only.py"
        _write(lonely, '"""Doc."""\n')
        subprocess.run(
            ["git", "-C", str(self.repo), "add", "lonely/only.py"], check=True
        )
        subprocess.run(
            [
                "git",
                "-C",
                str(self.repo),
                "-c",
                "user.email=t@t",
                "-c",
                "user.name=t",
                "commit",
                "-qm",
                "add lonely",
            ],
            check=True,
        )
        result = self._run(lonely)
        self.assertEqual(result.returncode, 0)
        self.assertIn("UNCHECKED", result.stdout)


class TestGitShowEncoding(unittest.TestCase):
    """`_show` must decode git's output as UTF-8, never the machine's locale.

    `code_fingerprint` alone cannot catch this: the bug is not in comparing two
    in-memory strings, it is in how `_show` turns `git show`'s bytes into one.
    A real commit, read back through `_show`, is the only way to exercise it.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name) / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        self.path = self.repo / "x.py"
        # The non-ASCII characters sit in a plain string CONSTANT, not a
        # docstring: a docstring's value is blanked before comparison and
        # would hide exactly the corruption this test exists to catch (this
        # is the real shape of the bug found in census.py's CALLFORM regex).
        self.text = 'MARK = "an ellipsis … and a warning ⚠ mark"\n'
        self.path.write_text(self.text, encoding="utf-8")
        subprocess.run(["git", "-C", str(self.repo), "add", "x.py"], check=True)
        subprocess.run(
            [
                "git",
                "-C",
                str(self.repo),
                "-c",
                "user.email=t@t",
                "-c",
                "user.name=t",
                "commit",
                "-qm",
                "init",
            ],
            check=True,
        )

    def tearDown(self):
        self.tmp.cleanup()

    def test_a_non_ascii_commit_is_shown_byte_for_byte(self):
        shown = pu._show(self.repo, "HEAD", "x.py")
        self.assertEqual(shown, self.text)

    def test_an_untouched_non_ascii_file_proves_identical_to_itself(self):
        shown = pu._show(self.repo, "HEAD", "x.py")
        on_disk = self.path.read_text(encoding="utf-8")
        self.assertEqual(
            pu.code_fingerprint(shown, self.path),
            pu.code_fingerprint(on_disk, self.path),
        )


# ⚠⚠ LAST LINE, ALWAYS. A runner placed above a class runs before that
# class exists, so `python tests/<file>.py` reported a green bar over a
# SHORTER suite than `unittest discover` — and the tests it skipped were
# the ones someone running a single file was iterating on. Measured
# 2026-08-17: 26 direct against 28 discovered here, 9 against 11 in
# test_vocabulary.py.
if __name__ == "__main__":
    unittest.main()
