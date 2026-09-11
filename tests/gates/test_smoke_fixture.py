"""The middle-chain smoke test's fixture yields every series, with more than
one member in each -- a series of one never exercises its ordinals, which is
what the first two drafts of this fixture got wrong.

Read off the real page builder, `flows/page_for.page_of`, on 2026-09-11 --
see `docs/superpowers/specs/2026-09-08-the-middle-chain-smoke-design.md`,
"The fixture" and "What it yields".
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

from conftest import ROOT

sys.path.insert(0, str(ROOT / "scripts"))
import smoke_fixture  # noqa: E402

from comment_review.desk.mark import Instruction, derived_change  # noqa: E402
from comment_review.flows.page_for import page_of  # noqa: E402


def cue_of(paragraph) -> str:
    """The cue half of a paragraph's address -- `a0` -- from `fib.py@a0`."""
    return (paragraph.address or "").split("@")[-1]


class TestTheFixtureYieldsEverySeries(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        path = smoke_fixture.write_fixture(self.root)
        page, why = page_of(path, rel="fib.py")
        assert page is not None, why
        self.page = page

    def tearDown(self):
        self.tmp.cleanup()

    def test_write_fixture_returns_the_path_it_wrote(self):
        path = smoke_fixture.write_fixture(self.root)
        self.assertEqual(path, self.root / "fib.py")
        self.assertTrue(path.exists())

    def test_every_series_is_present_with_no_d(self):
        # d is not a series in cues.places -- leading takes a symbol and
        # never a place, so it appears in page.leading, not here.
        series = {cue[0] for cue in self.page.cues.places}
        self.assertEqual(series, {"a", "b", "c", "f"})

    def test_the_series_counts(self):
        counts: dict[str, int] = {}
        for cue in self.page.cues.places:
            counts[cue[0]] = counts.get(cue[0], 0) + 1
        self.assertEqual(counts, {"a": 4, "b": 18, "c": 17, "f": 2})

    def test_a2_is_wrapper_with_no_docstring(self):
        self.assertEqual(self.page.cues.places["a2"], "    def wrapper(n):")
        by_cue = {cue_of(p): p for p in self.page.paragraphs if p.text}
        self.assertNotIn("a2", by_cue)

    def test_the_prose_holding_paragraphs(self):
        by_cue = {cue_of(p): p for p in self.page.paragraphs if p.text}
        self.assertEqual(
            set(by_cue),
            {"a0", "a1", "a3", "b1", "b9", "b14", "c1", "c6", "c12"},
        )
        for addr in ("a0", "a1", "a3"):
            self.assertEqual(by_cue[addr].kind, "docstring")
        for addr in ("b1", "b9", "b14"):
            self.assertEqual(by_cue[addr].kind, "comment")
        for addr in ("c1", "c6", "c12"):
            self.assertEqual(by_cue[addr].kind, "trailing-comment")
        self.assertEqual(by_cue["b9"].lines, 2)

    def test_f0_and_f1_hold_no_prose(self):
        by_cue = {cue_of(p): p for p in self.page.paragraphs if p.text}
        self.assertNotIn("f0", by_cue)
        self.assertNotIn("f1", by_cue)

    def test_leading_holds_seven_runs_d0_to_d6(self):
        self.assertEqual(len(self.page.leading), 7)
        self.assertEqual(set(self.page.leading.values()), {f"d{i}" for i in range(7)})


class TestTheLandingTableAgreesWithTheFixture(unittest.TestCase):
    """T32's check: for a correction, `Landing.text` is what `desk.mark`'s
    own derivation (`claim_change`) would produce -- the fixture's own
    paragraph at that address, with the `--false` clause replaced by the
    `--true` clause -- so the table cannot drift from what the fixture
    actually holds.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        path = smoke_fixture.write_fixture(self.root)
        page, why = page_of(path, rel="fib.py")
        assert page is not None, why
        self.page = page

    def tearDown(self):
        self.tmp.cleanup()

    def test_each_corrections_landing_is_the_fixture_with_true_for_false(self):
        by_cue = {cue_of(p): p for p in self.page.paragraphs if p.text}
        corrections = [
            address
            for address, landing in smoke_fixture.LANDINGS.items()
            if landing.false is not None
        ]
        self.assertEqual({a.split("@")[-1] for a in corrections}, {"c6", "c1"})
        for address in corrections:
            cue = address.split("@")[-1]
            landing = smoke_fixture.LANDINGS[address]
            corrected, why = derived_change(
                Instruction.CORRECT,
                {"false": landing.false, "true": landing.true},
                by_cue[cue].raw_text,
            )
            self.assertEqual(why, [], cue)
            self.assertEqual(corrected, landing.text, cue)

    def test_each_landing_at_an_empty_place_names_the_line_it_is_set_against(self):
        """A text landing names a `line` exactly where `FIXTURE` left its place
        empty, and it is the line the place's anchor sits on in the page built
        from `FIXTURE` -- or, for a place with no anchor line (the closing
        gap), the file's last."""
        filled = {cue_of(p) for p in self.page.paragraphs if p.text}
        last = len(smoke_fixture.FIXTURE.splitlines())
        for address, landing in smoke_fixture.LANDINGS.items():
            cue = address.split("@")[-1]
            empty = landing.outcome == "text" and cue not in filled
            self.assertEqual(landing.line is not None, empty, cue)
            if landing.line is None:
                continue
            anchor = self.page.cues.anchor_line(cue)
            self.assertEqual(landing.line, last if anchor is None else anchor, cue)


class TestWriteTextsWritesWhatTheScriptReads(unittest.TestCase):
    """`write_texts` writes the files smoke_middle.ps1 names for its `mark`
    calls, its addresser row and its disposition stage, each holding the
    value the plant gives it, and nothing else."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.run_dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_each_file_it_writes_and_what_it_holds(self):
        paths = smoke_fixture.write_texts(self.run_dir)
        landings = smoke_fixture.LANDINGS
        texts = {
            "fib.py@c6:false": ("c6-false.txt", landings["fib.py@c6"].false),
            "fib.py@c6:true": ("c6-true.txt", landings["fib.py@c6"].true),
            "fib.py@c1:false": ("c1-false.txt", landings["fib.py@c1"].false),
            "fib.py@c1:true": ("c1-true.txt", landings["fib.py@c1"].true),
        }
        for cue in ("b0", "a2", "b8", "b17", "b15", "c3", "c12", "a0"):
            address = f"fib.py@{cue}"
            texts[address] = (f"{cue}.txt", landings[address].text)
        others = {
            "dispositions": "dispositions.json",
            "addresser-row": "addresser-row.json",
        }

        self.assertEqual(set(paths), set(texts) | set(others))
        self.assertEqual(
            {p.name for p in self.run_dir.iterdir()},
            {name for name, _ in texts.values()} | set(others.values()),
        )
        for key, (name, text) in texts.items():
            self.assertEqual(paths[key], self.run_dir / name, key)
            self.assertEqual(paths[key].read_bytes().decode("utf-8"), text, key)
        for key, name in others.items():
            self.assertEqual(paths[key], self.run_dir / name, key)
        self.assertEqual(
            json.loads(paths["dispositions"].read_bytes()), smoke_fixture.DISPOSITIONS
        )
        self.assertEqual(
            json.loads(paths["addresser-row"].read_bytes()),
            {"address": "fib.py@b15", "line": 33},
        )
