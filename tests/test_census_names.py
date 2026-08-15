"""The name corpus is built from tracked files, so vendored code cannot mask a death."""

import subprocess  # noqa: I001  -- path shim below must import before census
import tempfile
import unittest
from pathlib import Path

from _paths import FIXTURES  # noqa: F401
import census


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


if __name__ == "__main__":
    unittest.main()
