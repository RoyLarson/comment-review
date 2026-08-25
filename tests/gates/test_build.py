"""`plugins/` is built from `src/`, and the gate that says so can fail.

!! THE SHIPPED TREE IS A COPY SINCE 2026-08-24, and a copy is a second place the
truth can live. Before the move the shipped scripts WERE the source, so nothing
could disagree; now something can, and the only thing standing between a
hand-edited `plugins/` and a stranger's install is this check.

! `docs/gates.md`: *"does the check pass" is not the question; "could the check
fail" is.* `TestTheCheckItselfFires` is that question asked of this gate.
"""

import shutil
import sys
import unittest

from conftest import ROOT

sys.path.insert(0, str(ROOT / "scripts"))
import build_plugin as bp  # noqa: E402


class TestTheShippedTreeMatchesTheSource(unittest.TestCase):
    def test_the_plugin_is_built_from_the_current_source(self):
        missing, extra, differing = bp.differences()
        self.assertEqual(
            (missing, extra, differing),
            ([], [], []),
            "run `python scripts/build_plugin.py` -- and edit `src/`, never `plugins/`",
        )

    def test_there_are_files_to_compare(self):
        # A comparison over nothing agrees with everything.
        self.assertGreaterEqual(len(bp.sources()), 20)

    def test_the_launcher_ships(self):
        # ! Without it the package cannot be reached by path, and every command
        # in SKILL.md names it.
        self.assertIn(bp.LAUNCHER, [p.as_posix() for p in bp.sources()])


class TestTheCheckItselfFires(unittest.TestCase):
    """Each case is the gate run against a tree that is WRONG in one way.

    ! `differences()` reads `bp.SRC` and `bp.DEST` at call time, so pointing
    both at temporary directories exercises the real comparison rather than a
    re-implementation of it.
    """

    def setUp(self):
        import tempfile
        from pathlib import Path

        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.src, self.dest = root / "src", root / "dest"
        (self.src / bp.PACKAGE).mkdir(parents=True)
        self.dest.mkdir()
        (self.src / bp.LAUNCHER).write_text("x = 1\n", encoding="utf-8")
        (self.src / bp.PACKAGE / "m.py").write_text("y = 2\n", encoding="utf-8")
        self._saved = (bp.SRC, bp.DEST)
        bp.SRC, bp.DEST = self.src, self.dest

    def tearDown(self):
        bp.SRC, bp.DEST = self._saved
        self.tmp.cleanup()

    def _build(self):
        shutil.copytree(self.src / bp.PACKAGE, self.dest / bp.PACKAGE)
        shutil.copy2(self.src / bp.LAUNCHER, self.dest / bp.LAUNCHER)

    def test_a_clean_build_agrees(self):
        self._build()
        self.assertEqual(bp.differences(), ([], [], []))

    def test_a_HAND_EDITED_shipped_file_is_reported(self):
        self._build()
        (self.dest / bp.PACKAGE / "m.py").write_text("y = 3\n", encoding="utf-8")
        _, _, differing = bp.differences()
        self.assertEqual([p.as_posix() for p in differing], ["comment_review/m.py"])

    def test_a_file_NEVER_BUILT_is_reported(self):
        self._build()
        (self.dest / bp.PACKAGE / "m.py").unlink()
        missing, _, _ = bp.differences()
        self.assertEqual([p.as_posix() for p in missing], ["comment_review/m.py"])

    def test_a_file_the_SOURCE_DROPPED_is_reported(self):
        # !! THE ONE A COPY-ONLY BUILD MISSES. A renamed or deleted module stays
        # in the shipped tree, which is what a stranger installs, and every gate
        # reading `plugins/` keeps passing on it.
        self._build()
        (self.dest / bp.PACKAGE / "gone.py").write_text("z = 4\n", encoding="utf-8")
        _, extra, _ = bp.differences()
        self.assertEqual([p.as_posix() for p in extra], ["comment_review/gone.py"])

    def test_an_EMPTY_shipped_tree_is_reported(self):
        # ! Never built at all. The gate must not read this as "nothing differs".
        missing, extra, differing = bp.differences()
        self.assertEqual(len(missing), 2)
        self.assertEqual((extra, differing), ([], []))
