"""`scripts/smoke_fixture.py`: `fib.py`'s fixture yields every series, with
more than one member in each -- a series of one never exercises its ordinals --
the landing table agrees with all four fixture files, and `write_texts` and
`write_answers` write what the smoke script reads.

The series are read off the real page builder, `flows/page_for.page_of` --
see `docs/superpowers/specs/2026-09-08-the-middle-chain-smoke-design.md`,
"The fixture" and "What it yields".
"""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from conftest import ROOT

sys.path.insert(0, str(ROOT / "scripts"))
import smoke_fixture  # noqa: E402
from smoke_fixture import write_second_plant as smoke_second_plant  # noqa: E402

from comment_review.desk.answers.answer import Question  # noqa: E402
from comment_review.desk.answers.table import ANSWERS as ANSWER_ROWS  # noqa: E402
from comment_review.desk.dispositions.disposition import ORIGINAL  # noqa: E402
from comment_review.desk.dispositions.table import (  # noqa: E402
    DISPOSITIONS as DISPOSITION_ROWS,
)
from comment_review.desk.marks.mark import (  # noqa: E402
    Instruction,
    Shape,
    derived_change,
    first_word_dropped,
)
from comment_review.desk.marks.table import INSTRUCTIONS  # noqa: E402
from comment_review.flows.answers import slot_key  # noqa: E402
from comment_review.flows.fill import marks_on  # noqa: E402
from comment_review.flows.human import HumanAnswer, read_answers  # noqa: E402
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
    `Landing.text`, what `desk.marks.mark.derived_change` makes of its fixture's
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
            "tally.py": smoke_fixture.TALLY_FIXTURE,
        }
        self.pages = {}
        for path in (
            smoke_fixture.write_fixture(root),
            smoke_fixture.write_rate_fixture(root),
            smoke_fixture.write_store_fixture(root),
            smoke_fixture.write_tally_fixture(root),
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
                "fib.py@a1",
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

    def test_the_compacting_plants_places_are_where_the_fixture_puts_them(self):
        """`decision-log.md Process: #193`. The compacting stage is dealt the
        places over its cap and no other, so the plant's own table has to
        agree with the fixture about which places those are -- and about the
        paragraph its one `patch` quotes, which it spells out to pass by
        `@path`."""
        by_cue = {cue_of(p): p for p in self.pages["store.py"].paragraphs if p.text}
        dealt = {
            f"store.py@{cue}"
            for cue, p in by_cue.items()
            if cue[0] in ("b", "c") and p.lines > smoke_fixture.COMPACTING_CAP
        }
        self.assertEqual(dealt, set(smoke_fixture.DEALT))
        self.assertEqual(
            {f"store.py@{cue}" for cue in by_cue} & set(smoke_fixture.UNTOUCHED),
            set(smoke_fixture.UNTOUCHED),
        )
        patched = by_cue[smoke_fixture.DEALT[0].split("@")[1]]
        self.assertEqual(patched.raw_text, smoke_fixture.OVER_THE_CAP)
        self.assertLessEqual(
            len(smoke_fixture.CONDENSED.splitlines()), smoke_fixture.COMPACTING_CAP
        )

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
    itself, and `TestTheCopiesFileWhatTheLandingTableSays` below, over the
    copies one run leaves behind.
    """

    def test_every_instruction_is_filed_at_some_place(self):
        planted = {
            instruction
            for landing in smoke_fixture.LANDINGS.values()
            for instruction in landing.filed
        }
        self.assertEqual(planted, {str(one) for one in INSTRUCTIONS})

    def test_every_answer_is_given_under_the_question_it_answers(self):
        """The first turn's answers, and the second turn's placements: a
        placement is answered by move in either turn, so `question_at` reads
        its question off the key, while a place's question in the second turn
        is whatever the first left it carried as, which `ESCALATED` does not
        record."""
        planted = {
            (smoke_fixture.question_at(key), str(fields["instruction"]))
            for table in (smoke_fixture.ANSWERS, smoke_fixture.ANSWERS2)
            for given in table.values()
            for key, fields in given.items()
            if table is smoke_fixture.ANSWERS or smoke_fixture.MOVE_KEY in key
        }
        # The `clean`s `write_answers` fills in are not in `ANSWERS` itself.
        planted.add(("composition", "clean"))
        self.assertEqual(planted, {(str(q), name) for q, name in ANSWER_ROWS})

    def test_each_placement_is_keyed_by_a_move_the_plant_files(self):
        """A placement answer's key names a move some role files: its origin
        is a place whose `filed` holds a `move`, and so is its destination."""
        keys = {
            key
            for table in (smoke_fixture.ANSWERS, smoke_fixture.ANSWERS2)
            for given in table.values()
            for key in given
            if smoke_fixture.question_at(key) == str(Question.PLACEMENT)
        }
        self.assertTrue(keys)
        for key in keys:
            origin, destination = key.split(smoke_fixture.MOVE_KEY)
            for end in (origin, destination):
                self.assertIn("move", smoke_fixture.LANDINGS[end].filed, key)

    def test_every_query_shape_is_answered(self):
        """A `query` is one answer row and two effects, which the shape
        decides: human-review-necessary holds the place for the person and
        the other two abstain. Each is planted, so both effects are reached.
        """
        planted = {
            str(fields["claim"]["shape"])
            for given in smoke_fixture.ANSWERS.values()
            for fields in given.values()
            if fields["instruction"] == "query"
        }
        self.assertEqual(planted, {str(one) for one in Shape})

    def test_every_human_question_is_answered_and_replaced(self):
        """Each question `HUMAN` answers is one the plant asks -- a
        human-review query in `ANSWERS` or at a place the mark stage queries
        -- and each is replaced once answered, in `REPLACED_MARKS` or
        `REPLACED_ANSWERS`, so no query reaches the fold (`decision-log.md
        Process: #197`)."""
        human = [one for asked in smoke_fixture.HUMAN.values() for one in asked]
        asked_in_answers = {
            (role, key)
            for role, given in smoke_fixture.ANSWERS.items()
            for key, fields in given.items()
            if fields.get("claim", {}).get("shape") == str(Shape.HUMAN_REVIEW_NECESSARY)
        }
        replaced = {
            (smoke_fixture.ASKER, address) for address in smoke_fixture.REPLACED_MARKS
        } | {
            (role, key)
            for role, given in smoke_fixture.REPLACED_ANSWERS.items()
            for key in given
        }
        answered = {(one["role"], one["at"]) for one in human}
        self.assertEqual(answered, replaced)
        self.assertLessEqual(asked_in_answers, answered)
        for address in smoke_fixture.REPLACED_MARKS:
            self.assertIn("query", smoke_fixture.LANDINGS[address].filed, address)

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


def normalized(text: str) -> str:
    """Prose with its comment markers dropped and its whitespace collapsed,
    lowercased, so a sentence reads the same however a paragraph wraps it."""
    return " ".join(text.replace("#", " ").split()).lower()


class TestTheChiefRulesAPlacementForItsMoverThenItsEnds(unittest.TestCase):
    """`decision-log.md Process: #195` item 4 and `#201`: an undecided move
    reaches the chief as a placement, ruled once with `to`; taken in for a
    mover it splits, and each end is then ruled in a second `disposition`
    call. The plant carries one such move, and these read its tables."""

    def setUp(self):
        self.moves = [
            one
            for one in smoke_fixture.DISPOSITIONS
            if "to" in one and one["side"] != ORIGINAL
        ]

    def test_a_placement_is_taken_in_for_a_mover_of_a_contested_move(self):
        """Contested when the turns are spent: some role stets its placement
        in the last turn, and the side taken in is a role that answered it."""
        self.assertTrue(self.moves, "no placement is ruled for a mover")
        for one in self.moves:
            key = str(one["address"]) + smoke_fixture.MOVE_KEY + str(one["to"])
            last = {
                role: str(given[key]["instruction"])
                for role, given in smoke_fixture.ANSWERS2.items()
                if key in given
            }
            self.assertIn("stet", last.values(), key)
            origin = smoke_fixture.LANDINGS[str(one["address"])]
            self.assertIn("move", origin.filed, key)

    def test_ends_rules_both_ends_of_each_such_move_and_nothing_else(self):
        """The second call rules exactly the ends the first one split, and
        the first call rules neither -- a ruling at a to-come end is refused."""
        ends = {one["address"] for one in smoke_fixture.ENDS}
        split = {end for one in self.moves for end in (one["address"], one["to"])}
        self.assertEqual(ends, split)
        first = {
            one["address"] for one in smoke_fixture.DISPOSITIONS if "to" not in one
        }
        self.assertFalse(ends & first)
        for one in smoke_fixture.ENDS:
            self.assertNotIn("to", one)

    def test_the_snippet_lands_once_and_each_end_as_the_chief_ruled_it(self):
        """The moved sentence leaves the origin and reads once on the page,
        and each end's landing is what `ENDS` makes of it."""
        expected = {"tally.py": smoke_fixture.TALLY_EXPECTED}
        for one in self.moves:
            origin = smoke_fixture.LANDINGS[str(one["address"])]
            destination = smoke_fixture.LANDINGS[str(one["to"])]
            page = expected[str(one["address"]).split("@")[0]]
            assert origin.marked is not None and origin.text is not None
            assert destination.text is not None
            snippet = normalized(origin.marked).removeprefix("a ")
            self.assertEqual(normalized(page).count(snippet), 1, one["address"])
            self.assertNotIn(snippet, normalized(origin.text))
            self.assertIn(origin.text + "\n", page)
            self.assertIn(destination.text + "\n", page)
            recast = {
                r["address"]: r["prose"]
                for r in smoke_fixture.ENDS
                if r["answer"] == "recast"
            }
            self.assertEqual(recast.get(one["to"], destination.text), destination.text)


class TestTheCopiesFileWhatTheLandingTableSays(unittest.TestCase):
    """`LANDINGS`' `filed` against the copies one real plant leaves behind.

    The row-coverage gate above reads that field to say which rows of the
    three tables the smoke reaches, and a field nothing checks would say so
    whether or not the `mark` calls still place them. The copies are what the
    calls placed. It ran beside the old fold's differential until that was
    deleted with the fold; the run is the same one, stopped after `mark`.
    """

    @classmethod
    def setUpClass(cls):
        if shutil.which("pwsh") is None:
            raise unittest.SkipTest("pwsh is not on PATH")
        done = subprocess.run(
            [
                "pwsh",
                "-NoProfile",
                "-File",
                str(ROOT / "scripts" / "smoke_middle.ps1"),
                "-Stop",
                "mark",
            ],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        assert done.returncode == 0, done.stdout + done.stderr
        lines = [line.strip() for line in done.stdout.splitlines() if line.strip()]
        assert lines, done.stdout + done.stderr
        cls.run_dir = Path(lines[-1])

    def test_the_copies_file_what_the_landing_table_says_they_do(self):
        placed: dict[str, set] = {}
        for path in sorted((self.run_dir / "copies").glob("*.json")):
            copy = json.loads(path.read_text(encoding="utf-8"))
            for mark in marks_on(copy):
                for address, _touch in INSTRUCTIONS[mark.instruction].places(mark):
                    placed.setdefault(address, set()).add(str(mark.instruction))
        # A landing with nothing filed is a place only a replacement files,
        # after the mark stage this run stops at -- and only that.
        replaced = {
            one["address"]
            for marks in smoke_fixture.REPLACED_MARKS.values()
            for one in marks
        }
        unfiled = {
            address
            for address, landing in smoke_fixture.LANDINGS.items()
            if not landing.filed
        }
        self.assertLessEqual(unfiled, replaced)
        said = {
            address: set(landing.filed)
            for address, landing in smoke_fixture.LANDINGS.items()
            if landing.filed
        }
        self.assertEqual(placed, said)


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

    def test_write_second_plant_writes_the_clauses_and_the_clean_list(self):
        """The stage's `mark` call reads its clauses by `@path`, as every
        other clause in the plant does, so the script spells no clause of its
        own beside the table's."""
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp)
            paths = smoke_second_plant(run)
            self.assertEqual(set(paths), {*smoke_fixture.SECOND_CLAIM, "clean"})
            for key, value in smoke_fixture.SECOND_CLAIM.items():
                self.assertEqual(paths[key], run / f"second-a0-{key}.txt", key)
                self.assertEqual(paths[key].read_bytes().decode("utf-8"), value, key)
            self.assertEqual(paths["clean"], run / "second-clean.json")
            listed = json.loads(paths["clean"].read_bytes())
            self.assertEqual(listed, list(smoke_fixture.SECOND_CLEAN))
            self.assertEqual(
                {p.name for p in run.iterdir()},
                {p.name for p in paths.values()},
            )

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
            "fib.py@a1": ("false", "true"),
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
        carried = [
            f"fib.py@{cue}" for cue in ("b0", "a2", "b8", "b17", "b15", "c3", "c5")
        ]
        carried += [f"fib.py@{cue}" for cue in ("c12", "a0")]
        carried += [
            f"store.py@{cue}" for cue in ("b1", "b3", "b8", "b9", "b10", "b11", "b12")
        ]
        carried += [f"tally.py@{cue}" for cue in ("b1", "b3")]
        for address in carried:
            landing = landings[address]
            stem, cue = address.split(".")[0], address.split("@")[1]
            held = landing.marked or landing.text
            assert held is not None, address
            texts[address] = (f"{stem}-{cue}.txt", held)
        others = {
            "dispositions": "dispositions.json",
            "ends": "dispositions-ends.json",
            "addresser-row": "addresser-row.json",
            "code-concern": "code-concern.json",
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
        self.assertEqual(json.loads(paths["ends"].read_bytes()), smoke_fixture.ENDS)
        self.assertEqual(
            json.loads(paths["addresser-row"].read_bytes()),
            {"address": "fib.py@b15", "line": 33},
        )
        self.assertEqual(
            json.loads(paths["code-concern"].read_bytes()), smoke_fixture.CODE_CONCERN
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
            # A placement is written at its move's origin with the destination
            # as `to`, so one role can answer a place and a move out of it.
            by_address = {slot_key(entry): entry for entry in written}
            for entry in written:
                entry.pop("address")
                entry.pop("to", None)
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


class TestWriteHumanWritesWhatTheCommandsRead(unittest.TestCase):
    """`write_human` writes the answers file `collate`, `turn` and `check`
    read with `--human`, read here by the same `flows.human.read_answers`
    they read it with, and grown one command's answers at a time; and
    `replace_answers` swaps the asking role's query for its replacement and
    nothing else."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.run_dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def read(self, path: Path) -> list[HumanAnswer]:
        answers, problems = read_answers(path.read_text(encoding="utf-8"), str(path))
        self.assertEqual(problems, [])
        return answers

    def test_each_stage_writes_its_own_answers_and_every_earlier_one(self):
        wanted: list[HumanAnswer] = []
        for stage, asked in smoke_fixture.HUMAN.items():
            wanted += [HumanAnswer(**one) for one in asked]
            path = smoke_fixture.write_human(self.run_dir, stage)
            self.assertEqual(path, self.run_dir / "human.toml")
            self.assertEqual(self.read(path), wanted, stage)
        replaced = json.loads((self.run_dir / "human-replaced.json").read_bytes())
        self.assertEqual(
            [one["query"] for one in replaced], list(smoke_fixture.REPLACED_MARKS)
        )
        for one in replaced:
            self.assertEqual(one["role"], smoke_fixture.ASKER)
            planted = smoke_fixture.REPLACED_MARKS[one["query"]]
            self.assertEqual(len(one["marks"]), len(planted), one["query"])
            for written, mark in zip(one["marks"], planted, strict=True):
                self.assertEqual(written["address"], mark["address"])
                args = written["args"]
                flags = dict(zip(args[::2], args[1::2], strict=True))
                self.assertEqual(list(flags), list(mark["flags"]))
                for flag, value in mark["flags"].items():
                    if value.startswith("@"):
                        path = Path(flags[flag][1:])
                        self.assertEqual(path, self.run_dir / value[1:], flag)
                    else:
                        self.assertEqual(flags[flag], value, flag)

    def test_the_code_concern_is_answered_add_a_todo_and_replaced_by_a_todo(self):
        """`decision-log.md Process: #199`: the code concern is a
        human-review query whose `settles` is `code concern`, the author
        answers it `add a TODO`, and the role replaces it with a ruling on the
        paragraph and an `add` whose text is a `TODO:` comment -- which is the
        text the expected page carries."""
        concern = smoke_fixture.CODE_CONCERN
        self.assertEqual(concern["settles"], "code concern")
        self.assertEqual(concern["shape"], str(Shape.HUMAN_REVIEW_NECESSARY))
        answers = [
            one
            for asked in smoke_fixture.HUMAN.values()
            for one in asked
            if one["at"] == concern["address"]
        ]
        self.assertEqual(len(answers), 1)
        self.assertEqual(answers[0]["answer"], "add a TODO")
        self.assertEqual(answers[0]["question"], concern["reason"])
        marks = smoke_fixture.REPLACED_MARKS[concern["address"]]
        by_instruction = {one["flags"]["--instruction"]: one for one in marks}
        self.assertEqual(set(by_instruction), {"correct", "add"})
        self.assertEqual(by_instruction["correct"]["address"], concern["address"])
        add = by_instruction["add"]
        self.assertEqual(
            add["flags"]["--change"], "@" + smoke_fixture.file_for(add["address"])
        )
        todo = smoke_fixture.LANDINGS[add["address"]].text
        assert todo is not None
        self.assertTrue(todo.lstrip().startswith("# TODO: "), todo)
        self.assertIn("        global CALLS" + todo + "\n", smoke_fixture.EXPECTED)

    def test_replace_answers_swaps_the_query_and_nothing_else(self):
        smoke_fixture.write_answers(self.run_dir)
        paths = smoke_fixture.replace_answers(self.run_dir)
        for role, replaced in smoke_fixture.REPLACED_ANSWERS.items():
            written = json.loads(paths[role].read_bytes())
            before = smoke_fixture.answers_for(role)
            self.assertEqual(len(written), len(before), role)
            for now, was in zip(written, before, strict=True):
                if slot_key(was) in replaced:
                    self.assertEqual(
                        now, {"address": was["address"], **replaced[slot_key(was)]}
                    )
                else:
                    self.assertEqual(now, was)
