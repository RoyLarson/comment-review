"""Code identity is proven by a script, not asserted by an agent."""

import subprocess  # noqa: I001  -- path shim below must import before prove_unchanged
import tempfile
import unittest
from pathlib import Path

from _paths import FIXTURES  # noqa: F401
import prove_unchanged as pu


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


class TestPythonProof(unittest.TestCase):
    def test_prose_only_change_is_proven(self):
        path = Path("x.py")
        self.assertEqual(
            pu.code_signature(PY_BEFORE, path), pu.code_signature(PY_COMMENT_ONLY, path)
        )

    def test_a_code_change_is_caught(self):
        path = Path("x.py")
        self.assertNotEqual(
            pu.code_signature(PY_BEFORE, path), pu.code_signature(PY_CODE_CHANGED, path)
        )

    def test_the_proof_kind_is_named(self):
        kind, _ = pu.code_signature(PY_BEFORE, Path("x.py"))
        self.assertEqual(kind, "ast")


class TestLexicalProof(unittest.TestCase):
    def test_prose_only_change_is_proven(self):
        path = Path("x.go")
        self.assertEqual(
            pu.code_signature(GO_BEFORE, path), pu.code_signature(GO_COMMENT_ONLY, path)
        )

    def test_a_code_change_is_caught(self):
        path = Path("x.go")
        self.assertNotEqual(
            pu.code_signature(GO_BEFORE, path), pu.code_signature(GO_CODE_CHANGED, path)
        )

    def test_the_proof_kind_is_named(self):
        kind, _ = pu.code_signature(GO_BEFORE, Path("x.go"))
        self.assertEqual(kind, "residue")


class TestUnprovable(unittest.TestCase):
    def test_an_unknown_suffix_is_reported_not_passed(self):
        kind, _ = pu.code_signature("whatever\n", Path("x.zzz"))
        self.assertEqual(kind, "unprovable")

    def test_a_syntax_error_falls_back_to_residue_not_to_success(self):
        kind, _ = pu.code_signature("def (:\n", Path("x.py"))
        self.assertIn(kind, ("residue", "unprovable"))


class TestLineEndings(unittest.TestCase):
    def test_crlf_detected(self):
        self.assertEqual(pu.dominant_ending("a\r\nb\r\n"), "crlf")

    def test_lf_detected(self):
        self.assertEqual(pu.dominant_ending("a\nb\n"), "lf")

    def test_a_flip_is_visible(self):
        self.assertNotEqual(pu.dominant_ending("a\r\n"), pu.dominant_ending("a\n"))


class TestGitShowEncoding(unittest.TestCase):
    """`_show` must decode git's output as UTF-8, never the machine's locale.

    `code_signature` alone cannot catch this: the bug is not in comparing two
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
            pu.code_signature(shown, self.path), pu.code_signature(on_disk, self.path)
        )


if __name__ == "__main__":
    unittest.main()
