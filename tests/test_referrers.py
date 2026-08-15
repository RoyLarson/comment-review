"""Who names this file? The inbound half of FIND REFERENCES."""

import unittest  # noqa: I001  -- path shim below must import before referrers
from pathlib import Path

from _paths import FIXTURES  # noqa: F401
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


if __name__ == "__main__":
    unittest.main()
