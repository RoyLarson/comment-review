"""The version is stated three times, so the three must agree."""

import json
import re
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# The newest release heading. `[Unreleased]` is skipped: it carries no number,
# which is what makes it unreleased.
#
# !! A PRE-RELEASE SUFFIX IS PART OF THE NUMBER. Three numeric components only
# would skip `## [0.2.4-alpha]` and match the release BELOW it, so the check that
# holds the three files equal would compare the wrong one and pass -- or fail
# against a version nobody wrote. ! Ruled 2026-08-21: a pre-release is cut so an
# unreleased tree cannot land in the cache directory a measured release owns.
RELEASE = re.compile(r"^## \[(\d+\.\d+\.\d+(?:[-.]?[A-Za-z][\w.]*)?)\]", re.M)


class TestTheVersionIsStatedOnce(unittest.TestCase):
    """`pyproject.toml`, `CHANGELOG.md` and `plugin.json` must name one release.

    !! `CHANGELOG.md` says a version number lives only there, and that is still
    the intent. `uv` forces a second copy -- it requires `project.version` or a
    `dynamic` one, and a dynamic version can only be read by BUILDING, which
    `[tool.uv] package = false` otherwise avoids. This is what makes the copy
    safe, and it earns its place twice: it also fails a release cut without a
    bump.

    !! The THIRD copy is `plugin.json`'s, and it is the only one a running
    installation can read. Without it the plugin cache names its directory for
    the COMMIT -- `roy-local/comment-review/7a0945ad3f40/` where an official
    plugin has `code-simplifier/1.0.0/` -- and `claude plugin list` reports the
    hash. Measured 2026-08-17: an evidence package taken over two runs could
    not attribute its numbers to a release, because nothing the installation
    exposed named one. `claude plugin tag` also validates this field against
    the marketplace entry when cutting `{name}--v{version}`.
    """

    def setUp(self):
        self.pyproject = tomllib.loads(
            (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        )
        self.changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        self.plugin = json.loads(
            (ROOT / "plugins/comment-review/.claude-plugin/plugin.json").read_text(
                encoding="utf-8"
            )
        )

    def _newest_release(self) -> str:
        newest = RELEASE.search(self.changelog)
        self.assertIsNotNone(newest, "CHANGELOG.md names no released version")
        assert newest is not None  # narrows the type; the assert above is the check
        return newest.group(1)

    def test_the_two_agree(self):
        self.assertEqual(
            self.pyproject["project"]["version"],
            self._newest_release(),
            "pyproject.toml and CHANGELOG.md name different releases",
        )

    def test_the_plugin_states_its_version(self):
        # ! An installed plugin that cannot name its version makes every
        # measurement taken against it unattributable.
        self.assertIn(
            "version",
            self.plugin,
            "plugin.json states no version, so an installed plugin reports a "
            "commit hash and no run can be attributed to a release",
        )

    def test_the_plugin_agrees_with_the_changelog(self):
        self.assertEqual(
            self.plugin["version"],
            self._newest_release(),
            "plugin.json and CHANGELOG.md name different releases",
        )

    def test_the_project_is_not_a_package(self):
        # ! Without this `uv run` tries to BUILD the tree and setuptools refuses
        # it -- five top-level directories in a flat layout. Nothing here is
        # installed; the plugin is COPIED into a `.claude/` directory.
        self.assertFalse(self.pyproject["tool"]["uv"]["package"])

    def test_the_floor_is_declared_where_uv_enforces_it(self):
        # ! Measured 2026-08-17: with 3.14 on the dev machine, four of eight
        # shipped scripts raised NameError at IMPORT on 3.11 while every test
        # and the shipped-syntax gate passed.
        self.assertEqual(self.pyproject["project"]["requires-python"], ">=3.11")
        self.assertEqual(
            (ROOT / ".python-version").read_text(encoding="utf-8").strip(), "3.11"
        )

    def test_every_gate_tool_is_pinned_where_uv_enforces_it(self):
        """The floor rule, applied to the tools that check the floor.

        !! IT WAS APPLIED TO THE INTERPRETER AND NOT TO THE LINTER for months.
        `pyproject.toml` spent sixteen lines arguing that an ambient interpreter
        silently passed broken code -- and declared no dev dependencies at all,
        so `ruff` and `ty` were whatever the machine happened to have. Roy,
        2026-08-22: *"we can't have my personal computer's `ty` happens to
        work."*

        ! `==` AND NOT `>=`. `ruff format` REWRITES source and its output moves
        between releases, so a range lets a different formatter author this
        tree; `ty` is pre-1.0, so its diagnostics move too. A gate that changes
        under a green run is what `docs/gates.md` is about.
        """
        dev = self.pyproject["dependency-groups"]["dev"]
        pinned = {name.split("==")[0]: name for name in dev if "==" in name}
        self.assertEqual(sorted(pinned), ["ruff", "ty"], dev)
