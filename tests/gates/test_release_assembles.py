"""The release command rebuilds the plugin from its two sources, and drops the rest.

! `docs/gates.md`: *"does the check pass" is not the question; "could the check
fail" is.* `assemble` takes its three roots as parameters, so each case runs
the real copy over a temporary tree that is wrong in one way.
"""

import sys
import tempfile
import unittest
from pathlib import Path

from conftest import ROOT

sys.path.insert(0, str(ROOT / "scripts"))
import release  # noqa: E402


class TestTheReleaseAssemblesThePlugin(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.prose, self.src = root / "prose", root / "src"
        self.plugin = root / "plugin"
        package = self.src / release.PACKAGE
        (self.prose / "agents").mkdir(parents=True)
        (self.prose / "agents" / "role.md").write_text("# role\n", encoding="utf-8")
        (package / "sub").mkdir(parents=True)
        (self.src / release.LAUNCHER).write_text("x = 1\n", encoding="utf-8")
        (package / "m.py").write_text("y = 2\n", encoding="utf-8")
        (package / "sub" / "n.py").write_text("z = 3\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def _assemble(self) -> list[str]:
        files = release.assemble(self.prose, self.src, self.plugin)
        return [p.as_posix() for p in files]

    def test_the_plugin_is_the_prose_plus_the_package_in_shape(self):
        scripts = release.SCRIPTS.as_posix()
        self.assertEqual(
            self._assemble(),
            [
                "agents/role.md",
                f"{scripts}/comment-review.py",
                f"{scripts}/comment_review/m.py",
                f"{scripts}/comment_review/sub/n.py",
            ],
        )

    def test_a_file_the_source_dropped_is_removed(self):
        # !! THE ONE A COPY-ONLY BUILD MISSES. A renamed or deleted file stays in
        # the shipped tree, which is what a stranger installs.
        self._assemble()
        gone = self.plugin / "agents" / "gone.md"
        gone.write_text("stale\n", encoding="utf-8")
        (self.plugin / release.SCRIPTS / release.PACKAGE / "gone.py").write_text(
            "w = 4\n", encoding="utf-8"
        )
        files = self._assemble()
        self.assertNotIn("agents/gone.md", files)
        self.assertNotIn(f"{release.SCRIPTS.as_posix()}/comment_review/gone.py", files)
        self.assertFalse(gone.exists())

    def test_bytecode_is_not_shipped(self):
        cache = self.src / release.PACKAGE / "__pycache__"
        cache.mkdir()
        (cache / "m.cpython-311.pyc").write_bytes(b"\x00")
        self.assertNotIn("__pycache__", "".join(self._assemble()))
