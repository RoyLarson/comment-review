"""A TODO's `Progress:` line agrees with its own boxes, and with the README row.

`TODO/README.md` states the rule this enforces: the boxes are the source of
truth, `Progress:` is what Roy assigns work from, and a stale-low count
manufactures a wrong instruction -- he asks for work already done and the
session spends context discovering that. It also names the condition for
writing this test: port it "at the point where hand-arithmetic starts being
wrong, not before". Five files disagreed with their own boxes on 2026-08-18.

! `scripts/todo_tool.py` is the WRITER of both; this only reads. Every box
counts, including a deferred one, because that is what the tool writes.

! A file counting something OTHER than tasks is skipped by the `tasks done`
suffix, not by name. `two-live-runs-proposed-fifteen-changes` counts PROPOSALS,
which the two field reports number separately, so its total is not its boxes.
"""

import re
import unittest

from conftest import ROOT

TODO = ROOT / "TODO"

BOX_DONE = re.compile(r"^- \[x\]", re.M)
BOX_OPEN = re.compile(r"^- \[ \]", re.M)
# Only a line that counts TASKS is checked against boxes.
PROGRESS = re.compile(r"^Progress: (\d+) of (\d+) tasks done", re.M)
# `| [name](path.md) | owner | roy? | 3/10 | ...` -- the README's open table,
# in the five-column shape `scripts/todo_tool.py` reads and writes.
ROW = re.compile(
    r"^\| \[([^\]]+)\]\(([^)]+\.md)\) \| [^|]* \| [^|]* \| \**(\d+)/(\d+)", re.M
)


def todo_files():
    """Every work order, which is every `TODO/*.md` except the index."""
    return sorted(p for p in TODO.glob("*.md") if p.name != "README.md")


class TestProgressAgreesWithBoxes(unittest.TestCase):
    def test_every_progress_line_matches_its_boxes(self):
        for p in todo_files():
            text = p.read_text(encoding="utf-8")
            m = PROGRESS.search(text)
            if not m:
                continue
            with self.subTest(todo=p.name):
                done = len(BOX_DONE.findall(text))
                total = done + len(BOX_OPEN.findall(text))
                self.assertEqual(
                    (done, total),
                    (int(m.group(1)), int(m.group(2))),
                    f"{p.name}: boxes say {done}/{total}, Progress says "
                    f"{m.group(1)}/{m.group(2)}. The boxes are the source of truth.",
                )

    def test_every_work_order_states_progress(self):
        """A file with boxes says how many are done, in one of the two units."""
        for p in todo_files():
            text = p.read_text(encoding="utf-8")
            if not (BOX_DONE.search(text) or BOX_OPEN.search(text)):
                continue
            with self.subTest(todo=p.name):
                self.assertRegex(
                    text, r"(?m)^Progress: ", f"{p.name} has boxes and no Progress line"
                )


class TestReadmeRowsAgree(unittest.TestCase):
    def test_open_table_counts_match_the_files(self):
        readme = (TODO / "README.md").read_text(encoding="utf-8")
        rows = ROW.findall(readme)
        self.assertTrue(rows, "the README's open table parsed to no rows")
        for name, rel, done, total in rows:
            target = TODO / rel
            with self.subTest(row=name):
                self.assertTrue(
                    target.exists(), f"{name} points at {rel}, which is not there"
                )
                text = target.read_text(encoding="utf-8")
                if not PROGRESS.search(text):
                    continue
                boxes_done = len(BOX_DONE.findall(text))
                boxes_total = boxes_done + len(BOX_OPEN.findall(text))
                self.assertEqual(
                    (boxes_done, boxes_total),
                    (int(done), int(total)),
                    f"README says {done}/{total} for {name}; the file's boxes say "
                    f"{boxes_done}/{boxes_total}",
                )
