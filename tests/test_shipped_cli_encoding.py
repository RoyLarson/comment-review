"""Every shipped CLI writes UTF-8, whatever console it lands on.

! Measured 2026-08-17, on a live run against another repo. `vocabulary.py` was
the one shipped CLI missing the guard, and it is the one whose whole output is
PASTED VERBATIM into a reviewer's prompt. On a `cp1252` console it corrupted
every em dash and **exited 0**; through a PowerShell redirect it wrote UTF-16,
which `grep` reports as a binary file. The run dispatched three reviewers
instead of four and nothing said why.

Silent corruption is the failure mode this file exists to stop. A crash would
have been visible.
"""

import re
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
    """Every .py that runs as a program, in each directory that holds one.

    !! NOT just the shipped ones. This globbed `plugins/.../scripts/` alone, so
    the root `scripts/` and `evals/` were outside the gate -- and
    `fetch_corpora.py` was found by review on 2026-08-17 with a U+26A0 in its
    own docstring and no guard, so `--help` died inside `argparse.print_help`
    on a cp1252 console and the same fault hit mid-run with corpora already
    cloned. A program that prints is a program that prints, wherever it lives.

    !! `evidence/ga/` IS ONE OF THOSE PLACES. The first widening said "wherever
    it lives" and then listed three directories, leaving `ground_truth.py` and
    `score.py` -- both argparse programs, both carrying a U+26A0 -- outside the
    gate the sentence claimed covered them. Measured 2026-08-17: neither had
    the guard.

    ! `tests/` is deliberately absent. Its files run as programs, but they
    write results through `unittest` to stderr, which this guard does not
    reconfigure -- including them would gate a stream nothing here protects.
    """
    roots = (SCRIPTS, ROOT / "scripts", ROOT / "evals", ROOT / "evidence" / "ga")
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


class TestWhatShipsIsAscii(unittest.TestCase):
    """Nothing under `plugins/` holds a character outside ASCII.

    The guard above keeps a non-ASCII character from being MANGLED on the way
    out. This keeps one from being there at all, which is the stronger property
    and the cheaper one: a plugin is copied onto a machine whose console
    encoding nobody here chose, and prose that is ASCII cannot be corrupted by
    any of them.

    Measured 2026-08-17, before the sweep that made this pass: 11,589 non-ASCII
    characters across the tree, 2,126 of them the U+26A0 that opened a warning
    and 6,956 em dashes. `unicodedata.normalize("NFKD", ...)` was rejected as
    the way to remove them -- it DELETES a character with no compatibility
    decomposition rather than transliterating it, which is 11,085 of those, and
    it turns U+2260 (not equal) into `=`.

    ! This gates what SHIPS, not the whole repo. A file under `evidence/` is a
    captured record and a file under `docs/` is read here; neither is copied
    onto anyone else's machine, which is the reason this rule exists.
    """

    def test_no_shipped_file_holds_a_non_ascii_character(self):
        for path in sorted((ROOT / "plugins").rglob("*")):
            if not path.is_file():
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            for i, line in enumerate(text.splitlines(), 1):
                bad = {c for c in line if ord(c) > 127}
                if bad:
                    rel = path.relative_to(ROOT).as_posix()
                    self.fail(
                        f"{rel}:{i} holds {sorted(hex(ord(c)) for c in bad)} -- "
                        "write it as an escape if a program needs the "
                        "character, or in ASCII if a reader does"
                    )


# !! LAST LINE, ALWAYS. A runner placed above a class runs before that
# class exists, so `python tests/<file>.py` reported a green bar over a
# SHORTER suite than `unittest discover` -- and the tests it skipped were
# the ones someone running a single file was iterating on. Measured
# 2026-08-17: 26 direct against 28 discovered here, 9 against 11 in
# test_vocabulary.py.
if __name__ == "__main__":
    unittest.main()
