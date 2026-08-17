"""Every shipped CLI writes UTF-8, whatever console it lands on.

⚠ Measured 2026-08-17, on a live run against another repo. `vocabulary.py` was
the one shipped CLI missing the guard, and it is the one whose whole output is
PASTED VERBATIM into a reviewer's prompt. On a `cp1252` console it corrupted
every em dash and **exited 0**; through a PowerShell redirect it wrote UTF-16,
which `grep` reports as a binary file. The run dispatched three reviewers
instead of four and nothing said why.

Silent corruption is the failure mode this file exists to stop. A crash would
have been visible.
"""

import re
import subprocess
import sys
import unittest
from pathlib import Path

from _paths import SCRIPTS  # noqa: F401

ROOT = Path(__file__).resolve().parent.parent

# A shipped CLI is a script under `scripts/` that argparse's and runs itself.
# The library modules -- `repo.py`, `annotate.py` -- write nothing and are
# excluded by that test rather than by a hand-kept list that would go stale.
ENTRY = re.compile(r'^if __name__ == "__main__":', re.M)
GUARD = re.compile(r"reconfigure\(encoding=\"utf-8\", errors=\"replace\"\)")


def shipped_clis():
    """Every .py in the repo that runs as a program.

    ⚠⚠ NOT just the shipped ones. This globbed `plugins/.../scripts/` alone, so
    the root `scripts/` and `evals/` were outside the gate — and
    `fetch_corpora.py` was found by review on 2026-08-17 with a U+26A0 in its
    own docstring and no guard, so `--help` died inside `argparse.print_help`
    on a cp1252 console and the same fault hit mid-run with corpora already
    cloned. A program that prints is a program that prints, wherever it lives.
    """
    roots = (SCRIPTS, ROOT / "scripts", ROOT / "evals")
    return sorted(
        p
        for root in roots
        for p in root.glob("*.py")
        if ENTRY.search(p.read_text(encoding="utf-8"))
    )


class TestEveryShippedCliGuardsItsOutput(unittest.TestCase):
    def test_there_are_clis_to_check(self):
        # A glob that matched nothing would make every test below vacuous.
        self.assertTrue(shipped_clis())

    def test_each_one_reconfigures_stdout(self):
        for path in shipped_clis():
            with self.subTest(script=path.name):
                self.assertRegex(
                    path.read_text(encoding="utf-8"),
                    GUARD,
                    f"{path.name} writes to stdout without the UTF-8 guard;"
                    " a console whose encoding lacks an em dash will corrupt it",
                )


class TestTheVocabularySurvivesACp1252Console(unittest.TestCase):
    """The specific failure, run end to end rather than matched in source.

    `vocabulary.py` is singled out because its output is the artifact pasted
    into four prompts: a mangled dash there reaches a reviewer as instruction.
    """

    def _emit(self, role):
        env = {"PYTHONIOENCODING": "cp1252", "SYSTEMROOT": "C:\\Windows"}
        return subprocess.run(
            [sys.executable, str(SCRIPTS / "vocabulary.py"), "--reviewer", role],
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env,
            check=False,
        )

    def test_every_role_keeps_its_em_dashes(self):
        for role in ("ownership-context", "block-context", "module-context"):
            with self.subTest(role=role):
                result = self._emit(role)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("—", result.stdout)
                self.assertNotIn("\ufffd", result.stdout)


# ⚠⚠ LAST LINE, ALWAYS. A runner placed above a class runs before that
# class exists, so `python tests/<file>.py` reported a green bar over a
# SHORTER suite than `unittest discover` — and the tests it skipped were
# the ones someone running a single file was iterating on. Measured
# 2026-08-17: 26 direct against 28 discovered here, 9 against 11 in
# test_vocabulary.py.
if __name__ == "__main__":
    unittest.main()
