"""The seeded record: what the tool fills, and what it leaves for the reviewer."""

import json  # noqa: I001  -- path shim below must import before record
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from _paths import FIXTURES, SCRIPTS  # noqa: F401
import foliator
import lexer
import page
import record
import verdicts

CENSUS = [
    {
        "path": "pkg/m.py",
        "start": 1,
        "end": 3,
        "kind": "docstring",
        "raw_lines": ["Summary.", "", "Args:"],
        "address": "pkg:m.py@a0",
        # ! An `a`'s anchor is its declaration; `a0` is the module.
        "anchor": "<module>",
    },
    {
        "path": "pkg/m.py",
        "start": 4,
        "end": 4,
        "kind": "interval",
        "raw_lines": [],
        "address": "pkg:m.py@b1",
        # ! A `b`'s anchor is the code line it sits ABOVE, verbatim.
        "anchor": "import os",
    },
    {
        "path": "pkg/m.py",
        "start": 5,
        "end": 5,
        "kind": "comment",
        "raw_lines": ["# a note"],
        "address": "pkg:m.py@b2",
        "anchor": "def f():",
    },
]


def all_records(report):
    """Every record, flattened out of its page block.

    ! The file groups records under the page they sit on -- see
    `record.pages_of`. A test that asserts about ONE record does not care which
    page it came from; one that cares reaches into `report["pages"]` itself.
    """
    return [rec for _, rec in record.every_record(report)]


class TestOnlyProseGetsASlot(unittest.TestCase):
    def test_intervals_are_skipped(self):
        self.assertEqual([i for i, _ in record.prose_paragraphs(CENSUS)], [1, 3])

    def test_a_census_of_only_intervals_seeds_nothing(self):
        only = [
            {
                "path": "a.py",
                "start": 1,
                "end": 1,
                "kind": "interval",
                "address": "a.py@b0",
            }
        ]
        self.assertEqual(all_records(record.seed(only, "block-context")), [])

    def test_the_address_is_the_CENSUSS_not_a_slot_number(self):
        # !! THE ADDRESS IS THE CENSUS'S, not a slot number. The index this
        # once asserted was dropped 2026-08-19 -- it went stale the moment an
        # `add` or a `drop` shifted the list.
        self.assertEqual(all_records(record.seed(CENSUS, "x"))[1]["place"], "b2")


class TestWhatTheToolFills(unittest.TestCase):
    def setUp(self):
        self.records = all_records(record.seed(CENSUS, "block-context"))

    def test_the_place_is_built_from_the_census(self):
        self.assertEqual(self.records[0]["place"], "a0")

    def test_the_record_does_NOT_carry_the_block_text(self):
        """!! The reviewer is told WHERE, not WHAT, and that is deliberate.

        A record carrying the prose lets a reviewer produce a complete,
        admissible ruling without opening the file, and nothing in the gate can
        tell that from real work. Every role's remit requires the read.

        !! The two errors are not symmetric, which is what decided it. Reading
        the wrong lines makes `CLAIM` quote a sentence the census paragraph does not
        contain, and `block_problem` already catches that. Ruling from the
        record instead of the code is invisible. ! Re-check that asymmetry
        before reversing this; it has flipped three times.
        """
        self.assertNotIn("original", self.records[0])

    def test_every_seeded_field_is_present(self):
        for field in record.SEEDED:
            with self.subTest(field=field):
                self.assertIn(field, self.records[0])

    def test_only_the_address_and_the_anchor_are_seeded(self):
        self.assertEqual(record.SEEDED, ("place", "anchor"))


class TestWhatTheReviewerFills(unittest.TestCase):
    def setUp(self):
        self.records = all_records(record.seed(CENSUS, "block-context"))

    def test_the_verdict_is_NULL_not_empty(self):
        # ! An unruled paragraph must be distinguishable from one ruled with an
        # empty verdict. Only the first is a coverage gap.
        self.assertIsNone(self.records[0]["verdict"])

    def test_the_answered_fields_are_present_and_empty(self):
        empty = {"claim": {}, "reason": "", "sources": [], "change": []}
        for field, value in empty.items():
            with self.subTest(field=field):
                self.assertEqual(self.records[0][field], value)

    def test_every_answered_field_is_present(self):
        for field in record.ANSWERED:
            with self.subTest(field=field):
                self.assertIn(field, self.records[0])

    def test_code_concerns_is_a_list_not_a_section(self):
        # ! One more boundary that cannot be guessed wrong: it was a markdown
        # heading found with a regex.
        self.assertEqual(record.seed(CENSUS, "x")["code_concerns"], [])


class TestTheTemplateStatesWhatIsAllowed(unittest.TestCase):
    """A constrained field that does not say its values has only moved the guessing.

    !! Every value here is DERIVED from the `Verdict` table, so adding a verdict
    stays a ROW and this paragraph cannot drift from what the gate enforces. These
    tests pin the correspondence, not the current contents.
    """

    def setUp(self):
        self.allowed = record.allowed()

    def test_every_verdict_the_gate_knows_is_offered(self):
        self.assertEqual(set(self.allowed["verdict"]), set(verdicts.VERDICTS))

    def test_a_claim_key_is_the_gates_marker_without_its_colon(self):
        for name, spec in verdicts.VERDICTS.items():
            for marker in spec.claim_all:
                with self.subTest(verdict=name, marker=marker):
                    self.assertIn(marker.rstrip(":"), self.allowed["claim"][name])

    def test_clean_is_offered_no_claim_keys(self):
        self.assertEqual(self.allowed["claim"]["clean"], [])

    def test_query_is_told_its_three_shapes(self):
        self.assertEqual(self.allowed["values"]["shape"], list(record.QUERY_SHAPES))
        self.assertIn("shape", self.allowed["claim"]["query"])

    def test_query_is_told_it_owes_attempted_and_settles(self):
        # ! Both are `needs_` flags on the table, not markers, so they would be
        # invisible to a reviewer that only saw the claim markers.
        self.assertIn("attempted", self.allowed["claim"]["query"])
        self.assertIn("settles", self.allowed["claim"]["query"])

    def test_add_is_told_it_owes_an_anchor_and_NOT_a_side(self):
        # !! THE ADDRESS SAYS WHICH SIDE -- `@bN` above code line N, `@cN`
        # beside it -- so the payload does not, and cannot contradict it.
        self.assertIn("anchor", self.allowed["claim"]["add"])
        self.assertNotIn("side", self.allowed["claim"]["add"])
        self.assertNotIn("side", self.allowed["values"])

    def test_the_boundary_shape_is_named(self):
        # ! One of the three query shapes is a scope report rather than work,
        # and a reader of the file alone cannot tell which.
        self.assertEqual(self.allowed["scope_shape"], record.OUT_OF_ROLE)
        self.assertIn(self.allowed["scope_shape"], self.allowed["values"]["shape"])

    def test_the_seeded_file_carries_it_before_the_records(self):
        keys = list(record.seed(CENSUS, "x"))
        self.assertLess(keys.index("allowed"), keys.index("pages"))


class TestCheckNamesTheRightThing(unittest.TestCase):
    """Shape problems, each reported against the field that is actually wrong.

    !! This is the lesson from D7, D8 and D9, all in one day: every one of them
    reported its error against work that was CORRECT, which is the most
    expensive diagnostic there is. These tests assert WHAT IS NAMED, not merely
    that something was refused -- all three of those defects passed tests that
    checked only the latter.
    """

    def _filled(self, **fields):
        rec = record.slot(CENSUS[0])
        rec.update(fields)
        return rec

    def _at(self, **fields):
        return record.record_problems("paragraph 1", self._filled(**fields), CENSUS[0])

    def test_a_well_formed_record_has_no_problems(self):
        self.assertEqual(
            self._at(
                verdict="correct",
                claim={"false": "x", "true": "y"},
                reason="because",
                sources=[{"cite": "a.py:1", "verbatim": "x"}],
                change=["# y"],
            ),
            [],
        )

    def test_a_wrong_claim_key_names_the_verdict_and_what_it_owes(self):
        problems = " ".join(self._at(verdict="drop", claim={"from": "x"}))
        self.assertIn("drop", problems)
        self.assertIn("'drop'", problems)
        self.assertIn("'from'", problems)

    def test_a_clobbered_address_blames_the_EDIT_not_the_reviewer(self):
        # !! The whole point. The reviewer never typed this field, so a message
        # accusing it of misquoting would send it to fix correct work.
        rec = self._filled(verdict="clean", place="WRONG")
        problem = " ".join(record.seeded_problems("paragraph 1", rec, CENSUS[0]))
        self.assertIn("WRITTEN BY THE TOOL", problem)
        self.assertIn("edited after seeding", problem)
        self.assertNotIn("misquot", problem.lower())

    def test_a_source_that_is_a_string_is_named_by_its_position(self):
        problems = " ".join(self._at(verdict="clean", sources=["a.py:1 | x"]))
        self.assertIn("source 1", problems)
        self.assertIn("{cite, verbatim}", problems)

    def test_a_constrained_value_shows_what_was_offered(self):
        problems = " ".join(
            self._at(
                verdict="query",
                claim={"shape": "outside the office", "attempted": "a", "settles": "s"},
            )
        )
        self.assertIn("outside the office", problems)
        self.assertIn("outside my role", problems)

    def test_an_unknown_verdict_lists_the_seven(self):
        problems = " ".join(self._at(verdict="reject"))
        self.assertIn("'reject'", problems)
        self.assertIn("correct", problems)

    def test_a_field_of_the_wrong_type_names_both_types(self):
        problems = " ".join(self._at(verdict="clean", reason=["a list"]))
        self.assertIn("`reason` is list, not str", problems)


class TestUnruledIsCountedNotRefused(unittest.TestCase):
    def test_an_empty_report_is_not_malformed(self):
        report = record.seed(CENSUS, "block-context")
        problems, unruled = record.check(report, CENSUS)
        self.assertEqual(problems, [])
        self.assertEqual(unruled, 2)

    def test_a_filled_record_is_not_counted_as_unruled(self):
        report = record.seed(CENSUS, "block-context")
        all_records(report)[0].update(verdict="clean")
        _, unruled = record.check(report, CENSUS)
        self.assertEqual(unruled, 1)

    def test_a_file_that_is_not_a_report_says_so(self):
        problems, _ = record.check({"nothing": "here"}, CENSUS)
        self.assertIn("not a seeded report", " ".join(problems))


class TestCLI(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.census = self.root / "census.json"
        self.census.write_text(json.dumps(CENSUS), encoding="utf-8")
        self.out = self.root / "nested" / "block-context.json"

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, *extra):
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "record.py"),
                "--census",
                str(self.census),
                "--reviewer",
                "block-context",
                "--out",
                str(self.out),
                *extra,
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )

    def test_it_writes_a_file_and_makes_its_directory(self):
        result = self._run("--seed")
        self.assertEqual(result.returncode, 0, result.stdout)
        written = json.loads(self.out.read_text(encoding="utf-8"))
        self.assertEqual(len(all_records(written)), 2)
        self.assertEqual(written["reviewer"], "block-context")

    def test_it_round_trips_as_json(self):
        self._run("--seed")
        # ! The point of the format: reading it back needs no parser of ours.
        self.assertIsInstance(json.loads(self.out.read_text(encoding="utf-8")), dict)

    def test_without_seed_it_does_nothing(self):
        self.assertEqual(self._run().returncode, 2)
        self.assertFalse(self.out.exists())

    def test_an_unreadable_census_is_refused(self):
        self.census.write_text("not json at all", encoding="utf-8")
        result = self._run("--seed")
        self.assertEqual(result.returncode, 2)
        self.assertIn("CANNOT PARSE", result.stdout)

    def _check(self, path):
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "record.py"),
                "--check",
                str(path),
                "--census",
                str(self.census),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )

    def test_an_empty_report_exits_0_and_says_how_much_is_left(self):
        # ! INCOMPLETE is not MALFORMED. A reviewer checking its own work
        # part-way through is not in error, and the two must exit differently.
        self._run("--seed")
        result = self._check(self.out)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("0 of 2 records ruled; 2 still empty", result.stdout)

    def test_a_malformed_record_exits_1(self):
        self._run("--seed")
        report = json.loads(self.out.read_text(encoding="utf-8"))
        all_records(report)[0].update(verdict="drop", claim={"from": "x"})
        self.out.write_text(json.dumps(report), encoding="utf-8")
        result = self._check(self.out)
        self.assertEqual(result.returncode, 1)
        self.assertIn("The shape is wrong, not the finding", result.stdout)

    def test_unparseable_json_NAMES_ITS_OWN_POSITION(self):
        # !! The one failure this format adds, and the reason it is acceptable:
        # a parse error says WHERE it is. A merged field never could -- it
        # blamed the neighbour, which is what D7, D8 and D9 each cost a session.
        self._run("--seed")
        self.out.write_text('{"records": [ {"block": 1,, } ]}', encoding="utf-8")
        result = self._check(self.out)
        self.assertEqual(result.returncode, 2)
        self.assertIn("CANNOT PARSE", result.stdout)
        self.assertRegex(result.stdout, r"line \d+ column \d+")


class TestABlankClaimKeyIsMissing(unittest.TestCase):
    """A key present and empty answers nothing, and must not read as answered.



    !! It is D8's shape one layer in. The seed lays down every key the verdict

    owes, so a reviewer that skips one leaves it there holding `""` -- and

    `verdicts.py` now reads the FIELD rather than the prose it renders into, so

    an empty field would satisfy a check by existing.

    """

    def _rec(self, **claim):

        return {
            "block": 1,
            "address": "a.py@b0",
            "verdict": "query",
            "claim": claim,
            "reason": "r",
            "sources": [],
            "change": [],
        }

    def test_an_empty_value_is_reported(self):

        problems = record.claim_problems(
            "x", self._rec(shape="outside my role", attempted="grepped", settles="")
        )

        self.assertEqual(len(problems), 1)

        self.assertIn("empty", problems[0])

        self.assertIn("settles", problems[0])

    def test_whitespace_is_empty(self):

        problems = record.claim_problems(
            "x", self._rec(shape="outside my role", attempted="grepped", settles="  ")
        )

        self.assertIn("empty", problems[0])

    def test_every_blank_key_is_named_at_once(self):

        # ! One message per record, not one per key: a reviewer fixes the record.

        problems = record.claim_problems(
            "x", self._rec(shape="", attempted="", settles="")
        )

        self.assertEqual(len(problems), 1)

        for key in ("shape", "attempted", "settles"):
            self.assertIn(key, problems[0])

    def test_a_filled_claim_is_not_reported(self):

        self.assertEqual(
            record.claim_problems(
                "x",
                self._rec(
                    shape="outside my role", attempted="grepped", settles="reading it"
                ),
            ),
            [],
        )

    def test_a_MISSING_key_still_reads_as_missing_not_blank(self):

        # ! The two messages tell a reviewer different things: one field was

        # skipped, or the record was built from the wrong verdict's shape.

        problems = record.claim_problems(
            "x", self._rec(shape="outside my role", attempted="grepped")
        )

        self.assertEqual(len(problems), 1)

        self.assertIn("needs `claim` keys", problems[0])


class TestTheRecordVersionIsRead(unittest.TestCase):
    """The field was written by `seed` and read by nothing.

    !! Its own comment claims it keeps a held report a REGRESSION TEST rather
    than an archive the day the shape moves. Nothing said so, so a file from a
    future version read as one of this version and the first sign of it would
    have been a field silently absent.
    """

    def test_this_readers_own_version_passes(self):
        self.assertIsNone(
            record.version_problem({"record_version": record.RECORD_VERSION})
        )

    def test_a_seeded_file_passes(self):
        self.assertIsNone(record.version_problem(record.seed(CENSUS, "block-context")))

    def test_a_different_version_is_named(self):
        # !! DERIVED FROM THE CONSTANT, NOT SPELT. This said `"2"` and broke the
        # day `RECORD_VERSION` became "2" -- the test asserting that a DIFFERENT
        # version is caught was itself pinned to a literal that stopped being
        # different. A bump should cost nothing here.
        other = f"{record.RECORD_VERSION}-not-this"
        problem = record.version_problem({"record_version": other})
        self.assertIn(repr(other), problem)
        self.assertIn(repr(record.RECORD_VERSION), problem)

    def test_a_missing_version_is_reported_differently(self):
        # ! The two mean different things: a shape that moved, against a file
        # `--seed` never wrote. A reviewer fixes them differently.
        self.assertIn("no `record_version`", record.version_problem({}))


class TestTheAnchorFormIsCheckedHereToo(unittest.TestCase):
    """`--check` passed an `add` the join fatally refused.

    !! Two tools, one record, different answers -- which is the defect the
    typed record was adopted to end, and this file had it in the direction
    opposite the one already fixed: an EMPTY anchor used to pass the join, and
    a BARE one passed `--check`.
    """

    PARAGRAPH = {
        "path": "a.py",
        "start": 1,
        "end": 1,
        "kind": "comment",
        "text": "x",
        "raw_lines": ["# x"],
        "address": "a.py@b0",
        # ! Every address has one, and a record without it is a broken record.
        "anchor": "x = 1",
    }

    def _rec(self, anchor):
        return {
            "block": 1,
            "place": "b0",
            "anchor": "x = 1",
            "verdict": "add",
            "claim": {"missing": "a note", "anchor": anchor},
            "reason": "derived it",
            "sources": [{"cite": "a.py:1", "verbatim": "# x"}],
            "change": ["# x", "# a note"],
        }

    def test_a_bare_anchor_is_refused(self):
        problems = record.record_problems(
            "paragraph 1", self._rec("compute"), self.PARAGRAPH
        )
        self.assertEqual(len(problems), 1)
        self.assertIn("backticks", problems[0])

    def test_a_backticked_anchor_passes(self):
        self.assertEqual(
            record.record_problems(
                "paragraph 1", self._rec("`compute`"), self.PARAGRAPH
            ),
            [],
        )

    def test_an_empty_anchor_is_reported_as_EMPTY_not_as_unbackticked(self):
        # ! Two messages for two mistakes. A reviewer fixes them differently.
        problems = record.record_problems("paragraph 1", self._rec(""), self.PARAGRAPH)
        self.assertEqual(len(problems), 1)
        self.assertIn("empty", problems[0])

    def test_the_template_SAYS_the_form(self):
        # !! The file's own rule: constraining a field without saying what is
        # allowed has only moved the guessing.
        # ! Beside `scope_shape`, not under `values`: it is a FORM, and
        # `values` holds the closed sets a field may be one of.
        self.assertIn("backticks", record.allowed()["anchor_form"])

    def test_the_published_example_is_what_the_pattern_accepts(self):
        # !! THE SENTENCE AND THE PATTERN ARE HELD EQUAL HERE, and nothing else
        # holds them. `allowed()` PUBLISHES a form and the join ENFORCES a
        # regex; the assertion above only checks the word "backticks" is in the
        # sentence, so loosening the pattern left the published rule promising
        # something no longer true.
        self.assertIn(record.ANCHOR_EXAMPLE, record.allowed()["anchor_form"])
        self.assertTrue(record.ANCHOR_NAME.search(record.ANCHOR_EXAMPLE))

    def test_a_bare_name_is_not_the_published_form(self):
        # ! The counter-example matters as much: a pattern that accepts
        # everything would satisfy the test above and refuse nothing.
        bare = record.ANCHOR_EXAMPLE.strip("`")
        self.assertIsNone(record.ANCHOR_NAME.search(bare))


class TestARecordWithNoAnchorIsBroken(unittest.TestCase):
    """Both fields are SEEDED and only `address` was ever checked.

    !! ROY, 2026-08-19: *"an anchor missing in a Record is a broken Record."*

    ! Measured the same day against the commit before this rule: **6,376 of
    6,531 paragraphs** in this repo's own shipped scripts carried an EMPTY anchor --
    98% of the census -- and every seeded record repeated it. It was invisible
    from both ends at once: `census.py` printed *"NO COMMENT carries an anchor
    at either tier"* as a statement of intent, and the test above asserts which
    KEYS are seeded rather than that either holds a value. The two agreed with
    each other and agreed on nothing.
    """

    PARAGRAPH = dict(CENSUS[2])

    def _rec(self, **over):
        rec = {
            "place": self.PARAGRAPH["address"].split("@")[-1],
            "anchor": self.PARAGRAPH["anchor"],
            "verdict": "clean",
            "claim": {},
            "reason": "",
            "sources": [],
            "change": [],
        }
        return rec | over

    def test_a_census_block_with_no_anchor_breaks_the_record(self):
        blank = self.PARAGRAPH | {"anchor": ""}
        problems = record.seeded_problems("paragraph 3", self._rec(anchor=""), blank)
        self.assertEqual(len(problems), 1)
        self.assertIn("no anchor", problems[0])

    def test_an_anchor_the_census_never_gave_is_REFUSED(self):
        problems = record.seeded_problems(
            "paragraph 3", self._rec(anchor="def other():"), self.PARAGRAPH
        )
        self.assertEqual(len(problems), 1)
        self.assertIn("WRITTEN BY THE TOOL", problems[0])

    def test_the_matching_anchor_passes(self):
        self.assertEqual(
            record.seeded_problems("paragraph 3", self._rec(), self.PARAGRAPH), []
        )

    def test_the_message_does_not_accuse_the_reviewer(self):
        # ! Same rule the `address` message follows: the reviewer never typed
        # this field, so a mismatch means the FILE was edited.
        problems = record.seeded_problems(
            "paragraph 3", self._rec(anchor="nope"), self.PARAGRAPH
        )
        self.assertNotIn("misquot", problems[0])
        self.assertIn("restore it", problems[0])

    def test_every_seeded_slot_carries_the_census_anchor(self):
        for i, slot in enumerate(all_records(record.seed(CENSUS, "block-context"))):
            with self.subTest(slot=i):
                self.assertTrue(slot["anchor"], "a seeded slot with no anchor")


class TestFrontMatterIsNotSEEDED(unittest.TestCase):
    """A slot nobody can fill reports INCOMPLETE forever.

    !! FRONT MATTER HOLDS REAL PROSE AND THE REVIEWER NEVER SEES IT. A licence
    header, a shebang or a coding line is filtered out of the census a role
    reads, so a seeded slot for one stays `null` and joins as a COVERAGE GAP --
    on every run, for as long as the file carries a licence.

    ! `verdicts.py` already excluded it from the set it counts coverage
    against. This is the other half: the two disagreed, so the gap was reported
    by neither and the slot was answered by nobody.

    ! It is the OPPOSITE case to an `interval`, which gets no slot because it
    holds nothing. This one holds prose and is not the reviewer's to rule on.
    """

    SRC = (
        "# Copyright 2026 Roy. All rights reserved.\n"
        "# Licensed under the Apache Licence, Version 2.0.\n"
        '"""What this module is for."""\n'
        "\n"
        "# what f is for\n"
        "def f():\n"
        '    """Do it."""\n'
        "    return 1\n"
    )

    def setUp(self):
        path = Path("m.py")
        paragraphs = page.page_for(path, self.SRC, lexer.language_for(path))
        list(page.code_lines(self.SRC, [vars(b) for b in paragraphs]))
        self.census = [vars(b) for b in paragraphs]
        # ! THE KIND, NOT AN ANNOTATION, since 2026-08-21 -- the lexer types a
        # run `matter` and the page no longer stamps it afterwards.
        self.marked = [b for b in self.census if b["kind"] == lexer.Kind.MATTER]

    def test_the_fixture_really_has_front_matter(self):
        # ! Guards the guard: a fixture whose header stopped being marked would
        # make every assertion below pass without exercising anything.
        self.assertTrue(self.marked, "the licence header is not marked front matter")

    def test_no_seeded_slot_is_front_matter(self):
        seeded = all_records(record.seed(self.census, "ownership-context"))
        at = {b["address"] for b in self.marked}
        self.assertEqual([s for s in seeded if s["place"] in at], [])

    def test_the_prose_a_reviewer_DOES_owe_still_gets_one(self):
        # ! The filter must not take the ordinary prose with it.
        seeded = all_records(record.seed(self.census, "ownership-context"))
        self.assertTrue(seeded)
        for s in seeded:
            held = (
                record.entry_for(record.address_for("m.py", s["place"]), self.census)
                or {}
            )
            with self.subTest(place=s["place"]):
                self.assertNotIn(lexer.Kind.MATTER, held.get("annotations") or ())

    def test_the_JOIN_and_the_SEED_agree_on_what_is_accountable(self):
        """!! They disagreed, which is how the gap reached nobody.

        `verdicts.py` builds its coverage set with the same two exclusions --
        `HOLDS_NO_PROSE` and `MATTER` -- and `record.prose_paragraphs`
        excluded only the first.
        """
        seeded = {
            record.address_for(where, s["place"])
            for where, s in record.every_record(record.seed(self.census, "x"))
        }
        # ! ASKED BY SERIES, as the shipped code does -- the annotation is what
        # `attach` reads to ASSIGN the place, not what a consumer asks.
        accountable = {
            str(b.get("address", ""))
            for b in self.census
            if not lexer.Kind.holds_no_prose(str(b.get("kind", "")))
            and b.get("address")
            and foliator.series_of(b) != foliator.COVERS
        }
        self.assertEqual(seeded, accountable)
