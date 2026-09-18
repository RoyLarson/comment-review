"""Nothing outside the three tables names a row.

The whole tree is held to it. An exemption list carried the old middle while
its replacement was built, and it emptied when the last of those modules was
deleted; a module exempted again is the defect this gate exists to refuse.
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
NAMES = re.compile(
    r"\bInstruction\.[A-Z_]+\b|\bAnswer\.[A-Z_]+\b"
    r"|\"(taken_in|recast|stet|hold|withdraw)\""
)


class TestOnlyTheTablesNameARow(unittest.TestCase):
    def test_no_module_outside_the_tables_names_a_row(self):
        offenders = []
        for path in ROOT.rglob("*.py"):
            if path in TABLES:
                continue
            if NAMES.search(path.read_text(encoding="utf-8")):
                offenders.append(path.relative_to(ROOT).as_posix())
        self.assertEqual(offenders, [])
