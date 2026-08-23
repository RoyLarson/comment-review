"""The sweep's two buckets, proved on a tree built for the purpose.

!! THE REAL TREE HOLDS NOTHING IN EITHER, which is the state a broken check can
sit in for months while a green bar says nothing is wrong. Roy's rule for this
repo is that a check which never fires is not evidence -- so this builds a tree
where each bucket MUST catch something.
"""

import sys
import tempfile
import unittest
from pathlib import Path

from _paths import ROOT  # noqa: F401  -- puts the shipped scripts on the path

# ! `dead_sweep.py` is a development tool, not a shipped one, so it is not on
# the path `_paths` sets up for the plugin's own modules.
sys.path.insert(0, str(ROOT / "scripts"))
import dead_sweep  # noqa: E402


class TestBothBucketsFire(unittest.TestCase):
    """A name nothing reads is DEAD; one only prose names is RAISED, not passed."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        (root / "plugins").mkdir()
        (root / "scripts").mkdir()
        (root / "plugins" / "shipped.py").write_text(
            "ALIVE = 1\nDEAD_NAME = 2\nPROSE_ONLY = 3\n\n\ndef main():\n"
            "    return ALIVE\n",
            encoding="utf-8",
        )
        # ! Prose names one of them and no code does.
        (root / "plugins" / "SKILL.md").write_text(
            "Run the tool with PROSE_ONLY when the census is stale.\n",
            encoding="utf-8",
        )
        (root / "scripts" / "caller.py").write_text(
            "from shipped import ALIVE\n\nprint(ALIVE)\n", encoding="utf-8"
        )
        self._real = dead_sweep.ROOT
        dead_sweep.ROOT = root
        self.dead, self.raised = dead_sweep.unread_names()

    def tearDown(self):
        dead_sweep.ROOT = self._real
        self.tmp.cleanup()

    def test_a_name_nothing_reads_is_reported_dead(self):
        self.assertEqual([n for _, n in self.dead], ["DEAD_NAME"])

    def test_a_name_only_PROSE_reads_is_RAISED_not_reported_dead(self):
        # !! NEITHER PASSED NOR FAILED. Prose may be the only caller -- an agent
        # acting on a sentence in `SKILL.md` -- or it may be abandoned history.
        # Roy, 2026-08-21: *"a call still in the agents file stating something
        # that is possible because it USED to be possible."*
        self.assertEqual([n for _, n, _ in self.raised], ["PROSE_ONLY"])
        self.assertNotIn("PROSE_ONLY", [n for _, n in self.dead])

    def test_it_names_the_file_that_still_mentions_it(self):
        # ! The question needs somewhere to look, or it cannot be answered.
        self.assertEqual(self.raised[0][2], ["plugins/SKILL.md"])

    def test_a_name_CODE_reads_is_in_neither(self):
        # ! Guards the guard the other way: a sweep that reports everything is
        # not a sweep.
        named = [n for _, n in self.dead] + [n for _, n, _ in self.raised]
        self.assertNotIn("ALIVE", named)

    def test_main_is_never_reported(self):
        # ! Every CLI defines one and nothing imports it.
        named = [n for _, n in self.dead] + [n for _, n, _ in self.raised]
        self.assertNotIn("main", named)

    def test_a_CONSTANT_is_not_its_own_reader(self):
        """!! `ALIVE = 1` PUTS `ALIVE` IN AN `ast.Name` TOO, with a Store context.

        Counting every Name made each constant read itself, so the sweep
        reported NOTHING -- while a `def` escaped it, being a `FunctionDef`
        rather than a Name. Functions surfaced and constants never did, which
        is a shape that looks like a working check.
        """
        self.assertIn("DEAD_NAME", [n for _, n in self.dead])


class TestANameHeldONLYByATestIsRaised(unittest.TestCase):
    """The question Roy asked and a grep answered wrongly.

    !! `foliator.triggers` IS THE CASE. Called by one test and by no shipped
    code, while its own docstring claims *"ONE LIST, SO THE THREE SERIES CANNOT
    DRIFT APART"* -- a guarantee documented, tested for shape, and not
    implemented. Two sweeps cleared it: one because a test calls it, one because
    another module's DOCSTRING contains the word.

    ! So a test is a HOLDER here and not a reader. Roy, 2026-08-21: *"I thought
    we just sliced out all of the functions that have only callers in tests?"*
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        (root / "plugins").mkdir()
        (root / "tests").mkdir()
        (root / "plugins" / "shipped.py").write_text(
            "def used_by_code():\n    return 1\n\n\n"
            "def held_by_test():\n    return 2\n\n\n"
            # ! `main` because the sweep skips it as an entry point. It is here
            # only to give `used_by_code` a shipped caller.
            "def main():\n    return used_by_code()\n",
            encoding="utf-8",
        )
        # ! Another shipped module MENTIONS the test-only name in prose. This is
        # what cleared it before: a text scan counted the docstring as a caller.
        (root / "plugins" / "other.py").write_text(
            '"""Something about held_by_test, in prose only."""\n', encoding="utf-8"
        )
        (root / "tests" / "test_it.py").write_text(
            "from shipped import held_by_test\n\n\n"
            "def test_x():\n    assert held_by_test() == 2\n",
            encoding="utf-8",
        )
        self._real = dead_sweep.ROOT
        dead_sweep.ROOT = root
        self.dead, self.raised = dead_sweep.unread_names()

    def tearDown(self):
        dead_sweep.ROOT = self._real
        self.tmp.cleanup()

    def test_a_name_only_a_TEST_calls_is_raised(self):
        self.assertEqual([n for _, n, _ in self.raised], ["held_by_test"])

    def test_it_is_not_reported_DEAD(self):
        # ! A test calling it is a real fact about the name; it is just not the
        # fact the question asks for.
        self.assertEqual(self.dead, [])

    def test_a_name_SHIPPED_CODE_calls_is_in_neither(self):
        named = [n for _, n in self.dead] + [n for _, n, _ in self.raised]
        self.assertNotIn("used_by_code", named)

    def test_a_DOCSTRING_mention_does_not_count_as_a_caller(self):
        # !! THE FAILURE THAT HID IT. `other.py` names it in prose and calls it
        # nowhere; a text scan over `.py` files read that as a shipped caller.
        self.assertIn("held_by_test", [n for _, n, _ in self.raised])


class TestDanglingLinksAreFound(unittest.TestCase):
    """A relative link is checked; an EXAMPLE inside backticks is not a link."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        (root / "docs").mkdir()
        (root / "TODO").mkdir()
        (root / "docs" / "real.md").write_text("# there\n", encoding="utf-8")
        (root / "docs" / "a.md").write_text(
            "[good](real.md) and [bad](gone.md) and `[shown](example.md)`\n",
            encoding="utf-8",
        )
        self._real = dead_sweep.ROOT
        dead_sweep.ROOT = root
        self.found = [target for _, target in dead_sweep.dangling_links()]

    def tearDown(self):
        dead_sweep.ROOT = self._real
        self.tmp.cleanup()

    def test_a_link_that_resolves_nowhere_is_found(self):
        self.assertIn("gone.md", self.found)

    def test_a_link_that_resolves_is_not(self):
        self.assertNotIn("real.md", self.found)

    def test_a_link_inside_BACKTICKS_is_an_example(self):
        # !! MEASURED: `complete-breaks-links.md` writes `[x](sibling.md)` to
        # describe the defect, and the sweep reported its own documentation.
        self.assertNotIn("example.md", self.found)
