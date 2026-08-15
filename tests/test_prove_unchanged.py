"""Code identity is proven by a script, not asserted by an agent."""

import unittest  # noqa: I001  -- path shim below must import before prove_unchanged
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


if __name__ == "__main__":
    unittest.main()
