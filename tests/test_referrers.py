"""Who names this file? The inbound half of FIND REFERENCES."""

import contextlib  # noqa: I001  -- path shim below must import before referrers
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from _paths import cli
from comment_review import referrers
from comment_review.commands import referrers as referrers_cmd


PY = '''"""A module."""


def visible_helper():
    pass


class VisibleThing:
    def _private(self):
        pass


def _hidden():
    pass
'''


class TestTokens(unittest.TestCase):
    def test_the_stem_is_a_token(self):
        self.assertIn("rates", referrers.tokens_for(Path("billing/rates.py"), PY))

    def test_the_posix_path_is_a_token(self):
        self.assertIn(
            "billing/rates.py", referrers.tokens_for(Path("billing/rates.py"), PY)
        )

    def test_top_level_names_are_tokens(self):
        got = referrers.tokens_for(Path("billing/rates.py"), PY)
        self.assertIn("visible_helper", got)
        self.assertIn("VisibleThing", got)

    def test_underscored_names_are_not_tokens(self):
        got = referrers.tokens_for(Path("billing/rates.py"), PY)
        self.assertNotIn("_hidden", got)
        self.assertNotIn("_private", got)

    def test_a_non_python_file_still_yields_its_path_tokens(self):
        got = referrers.tokens_for(Path("config/app.toml"), "key = 1\n")
        self.assertIn("app", got)
        self.assertIn("config/app.toml", got)


class TestCLI(unittest.TestCase):
    """`main()` end to end -- an unreadable target must be REPORTED, not dropped."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name) / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        self.target = self.repo / "bad.py"
        # 0xFF/0xFE are never valid UTF-8 lead bytes, so `read_text(encoding="utf-8")`
        # raises UnicodeDecodeError on this fixture regardless of platform locale.
        self.target.write_bytes(b"\xff\xfe not valid utf-8 \x80\x81")
        subprocess.run(["git", "-C", str(self.repo), "add", "bad.py"], check=True)
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
        cmd = [*cli("referrers"),
            "--repo",
            str(self.repo),
            *[str(p) for p in paths],
        ]
        return subprocess.run(
            cmd, capture_output=True, text=True, encoding="utf-8", check=False
        )

    def test_an_undecodable_target_is_reported_not_silently_degraded(self):
        result = self._run(self.target)
        self.assertEqual(result.returncode, 0)
        self.assertIn("NOT CHECKED", result.stdout)
        self.assertIn("bad.py", result.stdout)
        self.assertIn("UnicodeDecodeError", result.stdout)


class TestGrepStates(unittest.TestCase):
    """C1: "no matches" and "search failed" must not collapse to one value."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name) / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        (self.repo / "solo.py").write_text("x = 1\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(self.repo), "add", "solo.py"], check=True)
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

    def test_a_genuine_zero_match_search_is_an_empty_list_not_none(self):
        found, reason = referrers._grep(self.repo, "nowhere_in_this_repo")
        self.assertEqual(found, [])
        self.assertEqual(reason, "")

    def test_a_search_that_cannot_run_is_none_with_a_reason_not_an_empty_list(self):
        # No `git init` here: `git grep` exits >1 ("not a git repository"),
        # a real failure -- not the same value as a completed zero-match search.
        not_a_repo = Path(self.tmp.name) / "not-a-repo"
        not_a_repo.mkdir()
        found, reason = referrers._grep(not_a_repo, "anything")
        self.assertIsNone(found)
        self.assertNotEqual(reason, "")


class TestEmptyHitsFromFailedSearches(unittest.TestCase):
    """`hits` empty from every search FAILING must not read as a clean absence."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name) / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        self.target = self.repo / "target.py"
        self.target.write_text("def some_helper():\n    pass\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(self.repo), "add", "target.py"], check=True)
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

    def test_a_totally_failed_search_is_not_the_clean_none_message(self):
        # Forcing every real `git grep` invocation to fail (a timeout, a
        # corrupt index) is not reliably reproducible from a test; `_grep`
        # itself is already covered directly by `TestGrepStates`, so here it
        # is patched to always report "could not search" -- exercising the
        # one branch nothing else does: `hits` empty BECAUSE every token's
        # search failed, not because nothing was found.
        argv = ["referrers.py", "--repo", str(self.repo), str(self.target)]
        out = io.StringIO()
        with (
            mock.patch.object(sys, "argv", argv),
            # !! PATCHED WHERE IT IS USED, NOT WHERE IT IS DEFINED. The command
            # binds `_grep` into its own namespace at import, so replacing the
            # attribute on the library module leaves that binding untouched --
            # the patch applied, the real `git grep` ran, and the assertion
            # below failed on output that was CORRECT for a search that worked.
            mock.patch.object(
                referrers_cmd, "_grep", return_value=(None, "simulated failure")
            ),
            contextlib.redirect_stdout(out),
        ):
            code = referrers_cmd.main()
        output = out.getvalue()
        self.assertEqual(code, 0)
        self.assertNotIn("none -- nothing tracked names these files.", output)
        self.assertIn("NOT CHECKED", output)
        self.assertIn("could not be searched", output)


class TestNoGitIndex(unittest.TestCase):
    """The no-git-index gap must be SAID, not read as an empty result."""

    def test_a_non_git_directory_reports_no_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "solo.py"
            target.write_text("x = 1\n", encoding="utf-8")
            result = subprocess.run(
                [*cli("referrers"),
                    "--repo",
                    tmp,
                    str(target),
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0)
            self.assertIn("NO GIT INDEX", result.stdout)


class TestNothingIsWithheld(unittest.TestCase):
    """Property 2: a token naming many files is listed per file, never withheld.

    A cap on how many candidates were printed was removed 2026-08-16: this is an
    input to a review, and a reader deciding what to open is served by the whole
    list.
    """

    NAMERS = 41

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name) / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        self.target = self.repo / "target.py"
        self.target.write_text(
            "def widely_used_helper():\n    pass\n", encoding="utf-8"
        )
        names = ["target.py"]
        for i in range(self.NAMERS):
            p = self.repo / f"noise_{i}.py"
            p.write_text(
                f"# widely_used_helper, mentioned again ({i})\n", encoding="utf-8"
            )
            names.append(p.name)
        subprocess.run(["git", "-C", str(self.repo), "add", *names], check=True)
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

    def _run(self):
        cmd = [*cli("referrers"),
            "--repo",
            str(self.repo),
            str(self.target),
        ]
        return subprocess.run(
            cmd, capture_output=True, text=True, encoding="utf-8", check=False
        )

    def test_every_naming_file_is_printed(self):
        result = self._run()
        self.assertEqual(result.returncode, 0)
        self.assertNotIn("SUPPRESSED", result.stdout)
        self.assertIn("names: widely_used_helper", result.stdout)
        for i in (0, self.NAMERS - 1):
            self.assertIn(f"noise_{i}.py", result.stdout)
