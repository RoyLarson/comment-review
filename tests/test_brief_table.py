"""The brief's verdict table is generated, and stays equal to the row it came from.

`VERDICTS` in `record.py` decides what each verdict's `claim` must carry --
the keys through `claim_keys`, the prose through each row's `payload` --
and `reviewer-brief.md` restated it by hand.

!! THE HAND COPY HAD DRIFTED, which is why the generator exists rather than a
rule asking an author to keep two files equal. Measured 2026-08-18: the table
taught the 0.2.x MARKER form -- `false: "..." / true: "..."` -- forty lines
under a JSON worked example that used JSON keys; `query`'s row never named
`settles`; and ten of the eleven keys a reviewer must type appeared nowhere in
the brief as keys. The record became a typed object on this branch and the
table below it did not follow.

! The brief is what four reviewers read, so a drifted table is not a
documentation defect -- it is an instruction to write the wrong thing.
"""

import subprocess
import sys
import unittest
from pathlib import Path

from _paths import SCRIPTS  # noqa: F401
from record import VERDICTS, claim_keys

ROOT = Path(__file__).resolve().parents[1]
RENDER = ROOT / "scripts" / "render_brief.py"

# ! `_paths` puts the SHIPPED scripts on the path; the generator is a dev script
# and lives outside them, so its directory is added here and nowhere else.
sys.path.insert(0, str(ROOT / "scripts"))
BRIEF = (
    ROOT / "plugins/comment-review/skills/comment-review/references/reviewer-brief.md"
)


class TestTheBriefMatchesTheVerdictRow(unittest.TestCase):
    def test_the_checker_passes_on_the_shipped_brief(self):
        done = subprocess.run(
            [sys.executable, str(RENDER)], capture_output=True, text=True
        )
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)

    def test_every_verdict_has_a_row(self):
        brief = BRIEF.read_text(encoding="utf-8")
        for name in VERDICTS:
            with self.subTest(verdict=name):
                self.assertIn(f"| `{name}` |", brief)

    def test_every_claim_key_appears_as_a_key(self):
        """!! The defect that raised this: ten of eleven appeared nowhere.

        A reviewer types these as JSON keys. Prose describing them -- "the
        check you ATTEMPTED" -- reads as guidance and leaves the reviewer
        guessing at the spelling.
        """
        brief = BRIEF.read_text(encoding="utf-8")
        for name, spec in VERDICTS.items():
            markers, extras = claim_keys(spec)
            for key in markers + extras:
                with self.subTest(verdict=name, key=key):
                    self.assertIn(f"`{key}`", brief)

    def test_the_marker_form_is_gone_from_the_table(self):
        # ! `drop: "` and `false: "` are the 0.2.x record's syntax. The
        # deprecated PARSER still reads them; the brief must not teach them.
        table = BRIEF.read_text(encoding="utf-8").split("BEGIN GENERATED", 1)[1]
        table = table.split("END GENERATED", 1)[0]
        for marker in ('drop: "', 'false: "', 'from: "', 'missing: "'):
            with self.subTest(marker=marker):
                self.assertNotIn(marker, table)


class TestTheGeneratorItselfFires(unittest.TestCase):
    """A generator that cannot detect drift would pass over any edit."""

    def test_an_edited_table_is_reported(self):
        original = BRIEF.read_text(encoding="utf-8")
        try:
            BRIEF.write_text(
                original.replace("| `drop` | `drop` |", "| `drop` | `deleted` |", 1),
                encoding="utf-8",
            )
            done = subprocess.run(
                [sys.executable, str(RENDER)], capture_output=True, text=True
            )
            self.assertEqual(done.returncode, 1)
            self.assertIn("DRIFTED", done.stdout)
        finally:
            BRIEF.write_text(original, encoding="utf-8")

    def test_write_restores_it(self):
        original = BRIEF.read_text(encoding="utf-8")
        try:
            BRIEF.write_text(
                original.replace("| `drop` | `drop` |", "| `drop` | `deleted` |", 1),
                encoding="utf-8",
            )
            subprocess.run(
                [sys.executable, str(RENDER), "--write"], capture_output=True, text=True
            )
            self.assertEqual(BRIEF.read_text(encoding="utf-8"), original)
        finally:
            BRIEF.write_text(original, encoding="utf-8")

    def test_a_row_added_to_VERDICTS_would_reach_the_brief(self):
        # ! The property that makes this ONE source: the table is built from
        # the dict, so a new row appears without anyone editing the brief.
        import render_brief

        self.assertEqual(
            render_brief.table().count("\n"), len(VERDICTS) + 1, render_brief.table()
        )


# !! LAST LINE, ALWAYS. A runner placed above a class runs before that class
# exists, so `python tests/<file>.py` reports a green bar over a shorter suite
# than `unittest discover`.
if __name__ == "__main__":
    unittest.main()
