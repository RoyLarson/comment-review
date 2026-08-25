"""The name corpus is built from tracked files, so vendored code cannot mask a death."""

import subprocess  # noqa: I001  -- path shim below must import before census
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from _paths import FIXTURES  # noqa: F401
from comment_review.flows import census
from comment_review.machine import repo
from comment_review import referrers


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
        tracked = repo.tracked_paths(self.repo)
        names, _ = census.code_names([self.repo], tracked)
        self.assertIn("tracked_name", names)

    def test_an_untracked_name_does_not_mask_an_obituary(self):
        tracked = repo.tracked_paths(self.repo)
        names, _ = census.code_names([self.repo], tracked)
        self.assertNotIn("vendored_name", names)

    def test_no_git_falls_back_and_says_so(self):
        plain = Path(self.tmp.name) / "nogit"  # sibling of the repo, not inside it
        plain.mkdir()
        (plain / "a.py").write_text("def only_name():\n    pass\n")
        self.assertIsNone(repo.git_ls_files(plain))
        names, unread = census.code_names([plain], repo.tracked_paths(plain))
        self.assertIn("only_name", names)
        self.assertTrue(
            any("not a git" in u.lower() or "untracked" in u.lower() for u in unread)
        )


class TestNonAsciiTrackedPath(unittest.TestCase):
    """C4: `core.quotePath` defaults to TRUE, so git octal-escapes a path.

    A tracked `caf\303\251.py` -- a name holding one non-ASCII
    letter -- came back as `"caf\\303\\251.py"`, quotes included, so
    it matched nothing in `tracked_paths` and was skipped by `code_names` --
    every symbol defined only there became a false obituary, with NOTHING
    appended to `unread`. `path_index` indexed the escaped string, so a
    comment citing the real name reported UNRESOLVED: a false finding handed
    to four reviewers as settled fact.
    """

    NAME = "caf\u00e9.py"

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
        self.assertEqual(repo.git_ls_files(self.repo), [self.NAME])

    def test_a_symbol_defined_there_is_alive(self):
        names, unread = census.code_names([self.repo], repo.tracked_paths(self.repo))
        self.assertIn("helper_name", names, unread)

    def test_it_is_never_dropped_silently(self):
        # The one-sided failure: a file absent from the corpus AND absent from
        # `unread` is a coverage hole nothing reports.
        _, unread = census.code_names([self.repo], repo.tracked_paths(self.repo))
        tracked = repo.tracked_paths(self.repo)
        self.assertIn((self.repo / self.NAME).resolve(), tracked)
        self.assertEqual(unread, [])

    def test_a_citation_to_it_resolves(self):
        self.assertIn(self.NAME, repo.path_index(self.repo))

    def test_git_grep_reports_the_real_name(self):
        found, reason = referrers._grep(self.repo, "helper_name")
        self.assertEqual(reason, "")
        self.assertEqual(found, [self.NAME])


class TestGitOutputNotValidUtf8(unittest.TestCase):
    """The wave centralised every git call into `git()`, which pins
    `encoding="utf-8"` (`errors="strict"` by default) -- so a tracked path or
    blob that is not valid UTF-8 raises `UnicodeDecodeError` out of
    `subprocess.run` itself, before any caller sees a return code. Each
    caller's `except GIT_ERRORS:` must actually catch it rather than let it
    traceback out of the one helper this wave wrote for exactly this class of
    hazard (C4, non-ASCII paths).

    A real non-UTF-8 filename is not reliably constructible across platforms
    from a test, so `subprocess.run` is mocked to raise the same exception
    `text=True, encoding="utf-8"` would raise on undecodable output.
    """

    def setUp(self):
        self.repo = Path(".")  # never touched -- subprocess.run is mocked
        self.err = UnicodeDecodeError("utf-8", b"\xff\xfe", 0, 1, "invalid start byte")

    # `git()` lives in census.py and is only ever IMPORTED elsewhere (`from
    # census import git`), so patching `census.subprocess.run` is what reaches
    # every caller -- referrers.py and prove_unchanged.py hold a reference to
    # the same function object, not a copy.
    def test_git_ls_files_degrades_instead_of_raising(self):
        with patch("comment_review.machine.repo.subprocess.run", side_effect=self.err):
            self.assertIsNone(repo.git_ls_files(self.repo))

    def test_grep_names_the_reason_instead_of_raising(self):
        with patch("comment_review.machine.repo.subprocess.run", side_effect=self.err):
            found, reason = referrers._grep(self.repo, "token")
        self.assertIsNone(found)
        self.assertEqual(reason, "UnicodeDecodeError")

    def test_show_degrades_instead_of_raising(self):
        from comment_review.results import prove_unchanged

        with patch("comment_review.machine.repo.subprocess.run", side_effect=self.err):
            self.assertIsNone(prove_unchanged._show(self.repo, "HEAD", "a.py"))
