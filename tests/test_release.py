"""The version is stated twice, so the two must agree."""

import re
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# The newest release heading. `[Unreleased]` is skipped: it carries no number,
# which is what makes it unreleased.
RELEASE = re.compile(r"^## \[(\d+\.\d+\.\d+)\]", re.M)


class TestTheVersionIsStatedOnce(unittest.TestCase):
    """`pyproject.toml` and `CHANGELOG.md` must name the same release.

    ⚠⚠ `CHANGELOG.md` says a version number lives only there, and that is still
    the intent. `uv` forces a second copy -- it requires `project.version` or a
    `dynamic` one, and a dynamic version can only be read by BUILDING, which
    `[tool.uv] package = false` otherwise avoids. This is what makes the copy
    safe, and it earns its place twice: it also fails a release cut without a
    bump.
    """

    def setUp(self):
        self.pyproject = tomllib.loads(
            (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        )
        self.changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

    def test_the_two_agree(self):
        newest = RELEASE.search(self.changelog)
        self.assertIsNotNone(newest, "CHANGELOG.md names no released version")
        self.assertEqual(
            self.pyproject["project"]["version"],
            newest.group(1),
            "pyproject.toml and CHANGELOG.md name different releases",
        )

    def test_the_project_is_not_a_package(self):
        # ⚠ Without this `uv run` tries to BUILD the tree and setuptools refuses
        # it -- five top-level directories in a flat layout. Nothing here is
        # installed; the plugin is COPIED into a `.claude/` directory.
        self.assertFalse(self.pyproject["tool"]["uv"]["package"])

    def test_the_floor_is_declared_where_uv_enforces_it(self):
        # ⚠ Measured 2026-08-17: with 3.14 on the dev machine, four of eight
        # shipped scripts raised NameError at IMPORT on 3.11 while every test
        # and the shipped-syntax gate passed.
        self.assertEqual(self.pyproject["project"]["requires-python"], ">=3.11")
        self.assertEqual(
            (ROOT / ".python-version").read_text(encoding="utf-8").strip(), "3.11"
        )


if __name__ == "__main__":
    unittest.main()
