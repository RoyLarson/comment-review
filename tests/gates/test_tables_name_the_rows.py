"""Nothing outside the tables and the mark, answer and ruling types names a row.

The three tables state what each instruction, answer and ruling does at a
place; `desk/proof/mark.py` states what each instruction's mark is,
`desk/proof/answer.py` what each answer is and `desk/proof/disposition.py` what
each ruling is, one type per name and the one `match` that picks it
(`decision-log.md Process: #206`). The
gate searches shipped Python source for the spellings in `NAMES`.
It does not catch single-quoted ruling and answer names, plain instruction
strings, references through `Shape` or `Touch`, or properties that identify
only one row. The text search also sees comments and docstrings.

An exemption list carried the old middle while its replacement was built.
It emptied when the last of those modules was deleted.
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "src" / "comment_review"
TABLES = {
    ROOT / "desk" / "marks" / "table.py",
    ROOT / "desk" / "answers" / "table.py",
    ROOT / "desk" / "dispositions" / "table.py",
    ROOT / "desk" / "proof" / "mark.py",
    ROOT / "desk" / "proof" / "answer.py",
    ROOT / "desk" / "proof" / "disposition.py",
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
