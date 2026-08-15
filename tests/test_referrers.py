"""Who names this file? The inbound half of FIND REFERENCES."""

import subprocess  # noqa: I001  -- path shim below must import before referrers
import sys
import tempfile
import unittest
from pathlib import Path

from _paths import FIXTURES, SCRIPTS  # noqa: F401
import referrers


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
        cmd = [
            sys.executable,
            str(SCRIPTS / "referrers.py"),
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


if __name__ == "__main__":
    unittest.main()
