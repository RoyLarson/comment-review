"""`scripts/smoke_fixture.py`: `fib.py`'s fixture yields every series, with
more than one member in each -- a series of one never exercises its ordinals --
the landing table agrees with both fixture files, and `write_texts` writes what
the smoke script reads.

The series are read off the real page builder, `flows/page_for.page_of` --
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


#: The instruction a `Landing.claim` is the claim of, keyed by its keys in
#: `mark`'s flag order.
DERIVED_BY: dict[tuple[str, ...], Instruction] = {
    ("false", "true"): Instruction.CORRECT,
    ("from", "to"): Instruction.PATCH,
}


class TestTheLandingTableAgreesWithTheFixture(unittest.TestCase):
    """`LANDINGS` against the pages built from `FIXTURE` and `RATE_FIXTURE`:
    a landing carrying a `claim` has as its `Landing.text` what
    `desk.mark.derived_change` makes of its fixture's paragraph at that
    address, and a landing at an empty place names the line its place is
    set against -- so the table cannot drift from what the fixtures hold.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.texts = {
            "fib.py": smoke_fixture.FIXTURE,
            "rate.py": smoke_fixture.RATE_FIXTURE,
        }
        self.pages = {}
        for path in (
            smoke_fixture.write_fixture(root),
            smoke_fixture.write_rate_fixture(root),
        ):
            page, why = page_of(path, rel=path.name)
            assert page is not None, why
            self.pages[path.name] = page

    def tearDown(self):
        self.tmp.cleanup()

    def test_rate_holds_a_comment_at_b1_and_a_trailing_comment_at_c3(self):
        by_cue = {cue_of(p): p for p in self.pages["rate.py"].paragraphs if p.text}
        self.assertEqual(
            {cue: p.kind for cue, p in by_cue.items()},
            {"b1": "comment", "c3": "trailing-comment"},
        )

    def test_each_claimed_landing_is_the_fixture_with_its_claim_applied(self):
        claimed = []
        for address, landing in smoke_fixture.LANDINGS.items():
            if landing.claim is None:
                continue
            claimed.append(address)
            path, cue = address.split("@")
            by_cue = {cue_of(p): p for p in self.pages[path].paragraphs if p.text}
            changed, why = derived_change(
                DERIVED_BY[tuple(landing.claim)], landing.claim, by_cue[cue].raw_text
            )
            self.assertEqual(why, [], address)
            self.assertEqual(changed, landing.text, address)
        self.assertEqual(set(claimed), {"fib.py@c6", "fib.py@c1", "rate.py@c3"})

    def test_each_landing_at_an_empty_place_names_the_line_it_is_set_against(self):
        """A text landing names a `line` exactly where its fixture left its
        place empty, and it is the line the place's anchor sits on in the page
        built from that fixture -- or, for a place with no anchor line (the
        closing gap), the file's last."""
        for address, landing in smoke_fixture.LANDINGS.items():
            path, cue = address.split("@")
            page = self.pages[path]
            filled = {cue_of(p) for p in page.paragraphs if p.text}
            empty = landing.outcome == "text" and cue not in filled
            self.assertEqual(landing.line is not None, empty, address)
            if landing.line is None:
                continue
            last = len(self.texts[path].splitlines())
            anchor = page.cues.anchor_line(cue)
            self.assertEqual(landing.line, last if anchor is None else anchor, address)


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

        def clause(address: str, key: str) -> str:
            claim = landings[address].claim
            assert claim is not None, address
            return claim[key]

        texts = {
            "fib.py@c6:false": ("c6-false.txt", clause("fib.py@c6", "false")),
            "fib.py@c6:true": ("c6-true.txt", clause("fib.py@c6", "true")),
            "fib.py@c1:false": ("c1-false.txt", clause("fib.py@c1", "false")),
            "fib.py@c1:true": ("c1-true.txt", clause("fib.py@c1", "true")),
            "rate.py@c3:from": ("c3-from.txt", clause("rate.py@c3", "from")),
            "rate.py@c3:to": ("c3-to.txt", clause("rate.py@c3", "to")),
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
