"""Nothing outside the three tables names a row.

The list below is the old middle, still allowed to name an instruction, an
answer or a disposition while its replacement is built. Each task of
docs/superpowers/plans/2026-09-14-the-middle-rebuilt.md removes the modules
it replaces; the list is empty when the rebuild is done, and a module added
to it afterward is the defect this gate exists to refuse.
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "src" / "comment_review"
TABLES = {
    ROOT / "desk" / "marks" / "table.py",
    ROOT / "desk" / "answers" / "table.py",
    ROOT / "desk" / "dispositions" / "table.py",
}
#: Modules the rebuild has not replaced yet. Shrinks; never grows.
#: `desk/mark.py`, `desk/containers.py` and `commands/mark.py` were in the
#: brief's own list but name no row by this gate's own second test -- removed
#: 2026-09-14, T1 of docs/superpowers/plans/2026-09-14-the-middle-rebuilt.md.
#: `flows/fill.py` came off when it stopped naming `add` to check an add's
#: words and asked the row instead; `flows/transcribe.py` when it stopped
#: branching on `move` to say which end of it a docket was writing.
STILL_OLD = {
    "desk/marks/mark.py",
    "desk/collator.py",
    "desk/determined.py",
    "desk/diff_mark.py",
    "flows/_collate.py",
    "flows/_turn.py",
}
NAMES = re.compile(
    r"\bInstruction\.[A-Z_]+\b|\bDiffInstruction\.[A-Z_]+\b|\bAnswer\.[A-Z_]+\b"
    r"|\"(taken_in|recast|stet|hold|withdraw)\""
)


class TestOnlyTheTablesNameARow(unittest.TestCase):
    def test_no_new_module_names_a_row(self):
        offenders = []
        for path in ROOT.rglob("*.py"):
            rel = path.relative_to(ROOT).as_posix()
            if path in TABLES or rel in STILL_OLD:
                continue
            if NAMES.search(path.read_text(encoding="utf-8")):
                offenders.append(rel)
        self.assertEqual(offenders, [])

    def test_the_old_list_names_only_modules_that_still_name_a_row(self):
        stale = [
            rel
            for rel in STILL_OLD
            if not (ROOT / rel).exists()
            or not NAMES.search((ROOT / rel).read_text(encoding="utf-8"))
        ]
        self.assertEqual(stale, [], "remove these from STILL_OLD")
