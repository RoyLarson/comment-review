"""The name corpus is built from tracked files, so vendored code cannot mask a death."""

import subprocess  # noqa: I001  -- path shim below must import before census
import tempfile
import unittest
from pathlib import Path

from _paths import FIXTURES  # noqa: F401
import census
import referrers


class TestNameCorpusScope(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        # The repo is a SUBDIRECTORY of the temp dir, so the no-git case below
        # can be a sibling. A directory inside the repo is still inside a git
        # checkout, and `git -C <repo>/sub ls-files` would answer for it.
        self.repo = Path(self.tmp.name) / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        (self.repo / "tracked.py").write_text("def tracked_name():\n    pass\n")
        (self.repo / "vendored.py").write_text("def vendored_name():\n    pass\n")
        (self.repo / ".gitignore").write_text("vendored.py\n")
        subprocess.run(
            ["git", "-C", str(self.repo), "add", "tracked.py", ".gitignore"], check=True
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

    def test_a_tracked_name_is_alive(self):
        tracked = census.tracked_paths(self.repo)
        names, _ = census.code_names([self.repo], tracked)
        self.assertIn("tracked_name", names)

    def test_an_untracked_name_does_not_mask_an_obituary(self):
        tracked = census.tracked_paths(self.repo)
        names, _ = census.code_names([self.repo], tracked)
        self.assertNotIn("vendored_name", names)

    def test_no_git_falls_back_and_says_so(self):
        plain = Path(self.tmp.name) / "nogit"  # sibling of the repo, not inside it
        plain.mkdir()
        (plain / "a.py").write_text("def only_name():\n    pass\n")
        self.assertIsNone(census.git_ls_files(plain))
        names, unread = census.code_names([plain], census.tracked_paths(plain))
        self.assertIn("only_name", names)
        self.assertTrue(
            any("not a git" in u.lower() or "untracked" in u.lower() for u in unread)
        )


class TestNonAsciiTrackedPath(unittest.TestCase):
    """C4: `core.quotePath` defaults to TRUE, so git octal-escapes a path.

    A tracked `café.py` came back as `"caf\\303\\251.py"`, quotes included, so
    it matched nothing in `tracked_paths` and was skipped by `code_names` --
    every symbol defined only there became a false obituary, with NOTHING
    appended to `unread`. `path_index` indexed the escaped string, so a
    comment citing the real name reported UNRESOLVED: a false finding handed
    to four reviewers as settled fact.
    """

    NAME = "café.py"

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name) / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        (self.repo / self.NAME).write_text(
            "def helper_name():\n    return 1\n", encoding="utf-8"
        )
        subprocess.run(["git", "-C", str(self.repo), "add", "-A"], check=True)
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

    def test_git_ls_files_returns_the_real_name(self):
        self.assertEqual(census.git_ls_files(self.repo), [self.NAME])

    def test_a_symbol_defined_there_is_alive(self):
        names, unread = census.code_names([self.repo], census.tracked_paths(self.repo))
        self.assertIn("helper_name", names, unread)

    def test_it_is_never_dropped_silently(self):
        # The one-sided failure: a file absent from the corpus AND absent from
        # `unread` is a coverage hole nothing reports.
        _, unread = census.code_names([self.repo], census.tracked_paths(self.repo))
        tracked = census.tracked_paths(self.repo)
        self.assertIn((self.repo / self.NAME).resolve(), tracked)
        self.assertEqual(unread, [])

    def test_a_citation_to_it_resolves(self):
        self.assertIn(self.NAME, census.path_index(self.repo))

    def test_git_grep_reports_the_real_name(self):
        found, reason = referrers._grep(self.repo, "helper_name")
        self.assertEqual(reason, "")
        self.assertEqual(found, [self.NAME])


if __name__ == "__main__":
    unittest.main()
