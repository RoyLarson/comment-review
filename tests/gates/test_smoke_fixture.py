"""`scripts/smoke_fixture.py`: `fib.py`'s fixture yields every series, with
more than one member in each -- a series of one never exercises its ordinals --
the landing table agrees with all three fixture files, and `write_texts` and
`write_answers` write what the smoke script reads.

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

from comment_review.desk.answers.table import ANSWERS as ANSWER_ROWS  # noqa: E402
from comment_review.desk.dispositions.disposition import ORIGINAL  # noqa: E402
from comment_review.desk.dispositions.table import (  # noqa: E402
    DISPOSITIONS as DISPOSITION_ROWS,
)
from comment_review.desk.mark import (  # noqa: E402
    INSTRUCTIONS,
    Instruction,
    derived_change,
    first_word_dropped,
)
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

#: The landings whose text is wider than their claim, and the word each drops
#: beyond it -- written out by hand from the plant, never from the fold. One
#: entry: `store.py@c5`, where the `mark` call carries its own `--change`.
WIDER = {"store.py@c5": "wants"}


class TestTheLandingTableAgreesWithTheFixture(unittest.TestCase):
    """`LANDINGS` against the pages built from `FIXTURE` and `RATE_FIXTURE`:
    a landing carrying a `claim` has as its `Landing.marked`, or else its
    `Landing.text`, what `desk.mark.derived_change` makes of its fixture's
    paragraph at that address, and a landing at an empty place names the
    line its place is set against -- so the table cannot drift from what the
    fixtures hold.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.texts = {
            "fib.py": smoke_fixture.FIXTURE,
            "rate.py": smoke_fixture.RATE_FIXTURE,
            "store.py": smoke_fixture.STORE_FIXTURE,
        }
        self.pages = {}
        for path in (
            smoke_fixture.write_fixture(root),
            smoke_fixture.write_rate_fixture(root),
            smoke_fixture.write_store_fixture(root),
        ):
            page, why = page_of(path, rel=path.name)
            assert page is not None, why
            self.pages[path.name] = page

    def tearDown(self):
        self.tmp.cleanup()

    def test_rate_holds_comments_at_b1_and_b5_and_a_trailing_comment_at_c3(self):
        by_cue = {cue_of(p): p for p in self.pages["rate.py"].paragraphs if p.text}
        self.assertEqual(
            {cue: p.kind for cue, p in by_cue.items()},
            {"b1": "comment", "c3": "trailing-comment", "b5": "comment"},
        )

    def test_the_dropped_b5_owns_a_leading(self):
        """The drop at `rate.py@b5` reaches the compositor's leading rule only
        while the blank line below it is a leading `b5` owns."""
        self.assertIn("b5", self.pages["rate.py"].leading)

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
            if address in WIDER:
                continue
            self.assertEqual(changed, landing.marked or landing.text, address)
        self.assertEqual(
            set(claimed),
            {
                "fib.py@c6",
                "fib.py@c1",
                "rate.py@c3",
                "store.py@b7",
                "store.py@c5",
            },
        )

    def test_the_wider_landing_drops_the_word_its_claim_never_names(self):
        """`WIDER`'s one entry: the role wrote its own change rather than
        leaving the claim to derive one, so the change is not what the claim
        implies, and what it drops beyond the claim is the word named there --
        the advisory the fold reports and rolls nothing back for
        (`decision-log.md Process: #177`)."""
        for address, word in WIDER.items():
            landing = smoke_fixture.LANDINGS[address]
            assert landing.claim is not None
            path, cue = address.split("@")
            by_cue = {cue_of(p): p for p in self.pages[path].paragraphs if p.text}
            base = by_cue[cue].raw_text
            changed, why = derived_change(
                DERIVED_BY[tuple(landing.claim)], landing.claim, base
            )
            self.assertEqual(why, [], address)
            self.assertNotEqual(changed, landing.text, address)
            rest = base.replace(landing.claim["false"], "", 1)
            dropped = first_word_dropped(rest, landing.text or "")
            self.assertEqual(dropped, word, address)

    def test_each_landing_at_an_empty_place_names_the_line_it_is_set_against(self):
        """A landing names a `line` exactly where its fixture left its place
        empty, and it is the line the place's anchor sits on in the page built
        from that fixture -- or, for a place with no anchor line (the closing
        gap), the file's last."""
        for address, landing in smoke_fixture.LANDINGS.items():
            path, cue = address.split("@")
            page = self.pages[path]
            filled = {cue_of(p) for p in page.paragraphs if p.text}
            empty = cue not in filled
            self.assertEqual(landing.line is not None, empty, address)
            if landing.line is None:
                continue
            last = len(self.texts[path].splitlines())
            anchor = page.cues.anchor_line(cue)
            self.assertEqual(landing.line, last if anchor is None else anchor, address)


class TestEveryRowOfTheThreeTablesIsPlanted(unittest.TestCase):
    """The marks table, the answers table and the dispositions table against
    the plant's own tables: every row one of them carries has a scenario in
    `LANDINGS`, `ANSWERS` or `DISPOSITIONS`.

    ! IT READS THE PLANT'S TABLES AND NOT THE SCRIPT. A row named nowhere in
    them is a row the smoke cannot be driving, whatever `smoke_middle.ps1`
    types; what holds those tables to what the script places is the smoke
    itself, and `tests/test_differential_collate.py` over the copies one run
    leaves behind.
    """

    def test_every_instruction_is_filed_at_some_place(self):
        planted = {
            instruction
            for landing in smoke_fixture.LANDINGS.values()
            for instruction in landing.filed
        }
        self.assertEqual(planted, {str(one) for one in INSTRUCTIONS})

    def test_every_answer_is_given_under_the_question_it_answers(self):
        planted = {
            (smoke_fixture.question_at(address), str(fields["instruction"]))
            for given in smoke_fixture.ANSWERS.values()
            for address, fields in given.items()
        }
        # The `clean`s `write_answers` fills in are not in `ANSWERS` itself.
        planted.add(("composition", "clean"))
        self.assertEqual(planted, {(str(q), name) for q, name in ANSWER_ROWS})

    def test_every_disposition_is_ruled_and_taken_in_takes_both_sides(self):
        ruled = {str(one["answer"]) for one in smoke_fixture.DISPOSITIONS}
        self.assertEqual(ruled, set(DISPOSITION_ROWS))
        sides = {
            str(one["side"])
            for one in smoke_fixture.DISPOSITIONS
            if one["answer"] == "taken_in"
        }
        self.assertIn(ORIGINAL, sides)
        self.assertTrue(sides - {ORIGINAL}, "taken_in is never ruled for a role's side")


class TestTheSecondStageRulesTheRevisesOwnPlaces(unittest.TestCase):
    """`SECOND_CORRECT` and `SECOND_CLEAN` against the page built from
    `EXPECTED`, which is the revise the first stage pulls: the second stage
    rules every prose place that revise carries and no other, so `check`
    cannot refuse its copy for a place it left alone, and the addresses are
    the revise's rather than the original's."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        path = root / "fib.py"
        path.write_text(smoke_fixture.EXPECTED, encoding="utf-8", newline="\n")
        page, why = page_of(path, rel="fib.py")
        assert page is not None, why
        self.page = page

    def tearDown(self):
        self.tmp.cleanup()

    def test_it_rules_every_prose_place_the_revise_carries_and_no_other(self):
        prose = {p.address for p in self.page.paragraphs if p.text}
        ruled = {smoke_fixture.SECOND_CORRECT, *smoke_fixture.SECOND_CLEAN}
        self.assertEqual(ruled, prose)
        self.assertEqual(len(smoke_fixture.SECOND_CLEAN), len(prose) - 1)

    def test_the_corrected_place_is_one_the_first_stage_changed(self):
        """The point of the stage: the correction is measured against the
        revised text, so the clause it quotes is one only the revise holds."""
        false = smoke_fixture.SECOND_CLAIM["false"]
        self.assertIn(false, smoke_fixture.EXPECTED)
        self.assertNotIn(false, smoke_fixture.FIXTURE)

    def test_the_second_expected_keeps_what_the_first_stage_left_alone(self):
        """A paragraph neither stage changed is still on the page: the defect
        this stage is watching for is a revise that drops them."""
        self.assertIn("    if n < 2:  # base case\n", smoke_fixture.SECOND_EXPECTED)
        self.assertIn(smoke_fixture.SECOND_CLAIM["true"], smoke_fixture.SECOND_EXPECTED)


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

        clauses = {
            "fib.py@c6": ("false", "true"),
            "fib.py@c1": ("false", "true"),
            "rate.py@c3": ("from", "to"),
            "store.py@b7": ("false", "true"),
            "store.py@c5": ("false", "true"),
        }
        texts = {
            f"{address}:{key}": (
                f"{address.split('.')[0]}-{address.split('@')[1]}-{key}.txt",
                clause(address, key),
            )
            for address, keys in clauses.items()
            for key in keys
        }
        carried = [f"fib.py@{cue}" for cue in ("b0", "a2", "b8", "b17", "b15", "c3")]
        carried += [f"fib.py@{cue}" for cue in ("c12", "a0")]
        carried += [f"store.py@{cue}" for cue in ("b1", "b3", "b8")]
        for address in carried:
            landing = landings[address]
            stem, cue = address.split(".")[0], address.split("@")[1]
            held = landing.marked or landing.text
            assert held is not None, address
            texts[address] = (f"{stem}-{cue}.txt", held)
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


class TestWriteAnswersWritesWhatTheScriptReads(unittest.TestCase):
    """`write_answers` writes one file per role the smoke script's turn stage
    names, each holding that role's answers from `ANSWERS` and a `clean`
    carrying `CLEAN_REASON` at every `PROPOSED` place those leave out, and
    nothing else."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.run_dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_each_file_it_writes_and_what_it_holds(self):
        paths = smoke_fixture.write_answers(self.run_dir)
        roles = {
            "ownership-context",
            "block-context",
            "function-context",
            "module-context",
        }

        self.assertEqual(set(paths), roles)
        self.assertEqual(
            {p.name for p in self.run_dir.iterdir()},
            {f"answers-{role}.json" for role in roles},
        )
        for role, given in smoke_fixture.ANSWERS.items():
            self.assertEqual(paths[role], self.run_dir / f"answers-{role}.json", role)
            written = json.loads(paths[role].read_bytes())
            by_address = {entry.pop("address"): entry for entry in written}
            self.assertEqual(len(by_address), len(written), role)
            cleans = {
                address: {
                    "instruction": "clean",
                    "reason": smoke_fixture.CLEAN_REASON,
                }
                for address, proposer in smoke_fixture.PROPOSED.items()
                if address not in given and role != proposer
            }
            self.assertEqual(by_address, {**given, **cleans}, role)
