"""The seeded record: what the tool fills, and what it leaves for the reviewer."""

import json  # noqa: I001  -- path shim below must import before record
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from _paths import SCRIPTS  # noqa: F401
import record
import verdicts

CENSUS = [
    {
        "path": "pkg/m.py",
        "start": 1,
        "end": 3,
        "kind": "docstring",
        "raw_lines": ["Summary.", "", "Args:"],
    },
    {"path": "pkg/m.py", "start": 4, "end": 4, "kind": "interval", "raw_lines": []},
    {
        "path": "pkg/m.py",
        "start": 5,
        "end": 5,
        "kind": "comment",
        "raw_lines": ["# a note"],
    },
]


class TestOnlyProseGetsASlot(unittest.TestCase):
    def test_intervals_are_skipped(self):
        self.assertEqual([i for i, _ in record.prose_blocks(CENSUS)], [1, 3])

    def test_a_census_of_only_intervals_seeds_nothing(self):
        only = [{"path": "a.py", "start": 1, "end": 1, "kind": "interval"}]
        self.assertEqual(record.seed(only, "block-context")["records"], [])

    def test_the_index_is_the_CENSUS_index_not_the_slot_number(self):
        # !! The second prose block is census index 3, not 2. The index IS the
        # block's identity, and renumbering it would make every citation wrong.
        self.assertEqual(record.seed(CENSUS, "x")["records"][1]["block"], 3)


class TestWhatTheToolFills(unittest.TestCase):
    def setUp(self):
        self.records = record.seed(CENSUS, "block-context")["records"]

    def test_the_address_is_built_from_the_census(self):
        self.assertEqual(self.records[0]["address"], "pkg/m.py:1-3")

    def test_the_record_does_NOT_carry_the_block_text(self):
        """!! The reviewer is told WHERE, not WHAT, and that is deliberate.

        A record carrying the prose lets a reviewer produce a complete,
        admissible ruling without opening the file, and nothing in the gate can
        tell that from real work. Every role's remit requires the read.

        !! The two errors are not symmetric, which is what decided it. Reading
        the wrong lines makes `CLAIM` quote a sentence the census block does not
        contain, and `block_problem` already catches that. Ruling from the
        record instead of the code is invisible. ! Re-check that asymmetry
        before reversing this; it has flipped three times.
        """
        self.assertNotIn("original", self.records[0])

    def test_every_seeded_field_is_present(self):
        for field in record.SEEDED:
            with self.subTest(field=field):
                self.assertIn(field, self.records[0])

    def test_only_the_index_and_the_address_are_seeded(self):
        self.assertEqual(record.SEEDED, ("block", "address"))


class TestWhatTheReviewerFills(unittest.TestCase):
    def setUp(self):
        self.records = record.seed(CENSUS, "block-context")["records"]

    def test_the_verdict_is_NULL_not_empty(self):
        # ! An unruled block must be distinguishable from one ruled with an
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
    stays a ROW and this block cannot drift from what the gate enforces. These
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

    def test_add_is_told_it_owes_an_anchor_and_a_side(self):
        self.assertIn("anchor", self.allowed["claim"]["add"])
        self.assertIn("side", self.allowed["claim"]["add"])
        self.assertEqual(self.allowed["values"]["side"], ["above", "below"])

    def test_the_boundary_shape_is_named(self):
        # ! One of the three query shapes is a scope report rather than work,
        # and a reader of the file alone cannot tell which.
        self.assertEqual(self.allowed["scope_shape"], record.OUT_OF_ROLE)
        self.assertIn(self.allowed["scope_shape"], self.allowed["values"]["shape"])

    def test_the_seeded_file_carries_it_before_the_records(self):
        keys = list(record.seed(CENSUS, "x"))
        self.assertLess(keys.index("allowed"), keys.index("records"))


class TestCheckNamesTheRightThing(unittest.TestCase):
    """Shape problems, each reported against the field that is actually wrong.

    !! This is the lesson from D7, D8 and D9, all in one day: every one of them
    reported its error against work that was CORRECT, which is the most
    expensive diagnostic there is. These tests assert WHAT IS NAMED, not merely
    that something was refused -- all three of those defects passed tests that
    checked only the latter.
    """

    def _filled(self, **fields):
        rec = record.slot(1, CENSUS[0])
        rec.update(fields)
        return rec

    def _at(self, **fields):
        return record.record_problems("block 1", self._filled(**fields), CENSUS[0])

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
        rec = self._filled(verdict="clean", address="WRONG:1-2")
        problem = " ".join(record.seeded_problems("block 1", rec, CENSUS[0]))
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
        report["records"][0].update(verdict="clean")
        _, unruled = record.check(report, CENSUS)
        self.assertEqual(unruled, 1)

    def test_a_file_that_is_not_a_report_says_so(self):
        problems, _ = record.check({"nothing": "here"}, CENSUS)
        self.assertIn("not a seeded report", " ".join(problems))


class TestConvertKeepsAHeldRunReplayable(unittest.TestCase):
    """A 0.2.x report becomes records, so a captured run stays a regression test.

    !! Replaying held stage-4 output is what made 0.2.1 and 0.2.2 cheap to
    validate -- five joins over one set of reports, about 1.6M tokens of review
    reused -- and that property dies the day the shape moves unless something
    carries the old reports across.
    """

    def test_a_two_marker_claim_becomes_its_two_keys(self):
        self.assertEqual(
            record.claim_object(
                "correct", 'false: "the budget is 3" / true: "it is 5"'
            ),
            {"false": "the budget is 3", "true": "it is 5"},
        )

    def test_a_drop_carries_its_one_key(self):
        self.assertEqual(
            record.claim_object("drop", 'drop: "callers round separately"'),
            {"drop": "callers round separately"},
        )

    def test_an_add_recovers_its_ANCHOR_AND_SIDE_from_the_prose(self):
        # !! The old format carried these as prose inside CLAIM, checked by
        # regex rather than by marker. A conversion reading only markers turned
        # 179 of one report's 228 admissible records into malformed ones.
        got = record.claim_object(
            "add", 'missing: "the units are seconds", above `COOLDOWN_HOLD_S`'
        )
        self.assertEqual(got["anchor"], "`COOLDOWN_HOLD_S`")
        self.assertEqual(got["side"], "above")

    def test_before_and_after_map_onto_the_two_sides_offered(self):
        got = record.claim_object("add", 'missing: "x", before `F`')
        self.assertEqual(got["side"], "above")

    def test_a_query_recovers_its_shape_and_owes_the_rest(self):
        got = record.claim_object(
            "query", "outside my role -- I grepped for it and found nothing"
        )
        self.assertEqual(got["shape"], "outside my role")
        self.assertIn("attempted", got)
        self.assertIn("settles", got)

    def test_an_unknown_verdict_converts_to_an_empty_claim(self):
        self.assertEqual(record.claim_object("reject", 'drop: "x"'), {})


class TestConvertGivesACitedIntervalASlot(unittest.TestCase):
    """!! `add` cites an EMPTY INTERVAL, which `--seed` gives no slot.

    Seeding lays down the PROSE blocks because those are what a reviewer is
    accountable for. But an `add`'s finding is that a constraint holds in code
    and appears in no prose, so its subject is the GAP -- and a conversion that
    filled only seeded slots dropped both of one report's `add`s in silence.
    Measured 2026-08-17: 228 findings became 226.
    """

    @staticmethod
    def _F(block, verdict):
        """A finding, as `parse_report` builds them -- `convert`'s real input.

        ! A hand-rolled stub stood here and re-declared six of `Finding`'s
        fields. `convert` consumes real ones, so a field added to `Finding` --
        `claim_fields` was, on this branch -- would not have reached these
        tests, and a conversion could lose data with a green suite.
        """
        return record.Finding(
            reviewer="module-context",
            block=block,
            verdict=verdict,
            claim='missing: "x", above `F`',
            reason="r",
            sources=["a.py:1 | x"],
            change="# x",
        )

    def test_a_finding_on_an_interval_is_not_dropped(self):
        report = record.convert([self._F(2, "add")], CENSUS, "module-context")
        cited = [r for r in report["records"] if r["block"] == 2]
        self.assertEqual(len(cited), 1)
        self.assertEqual(cited[0]["verdict"], "add")

    def test_the_interval_slot_carries_the_censuss_address(self):
        report = record.convert([self._F(2, "add")], CENSUS, "module-context")
        cited = next(r for r in report["records"] if r["block"] == 2)
        self.assertEqual(cited["address"], "pkg/m.py:4-4")

    def test_records_stay_in_census_order(self):
        report = record.convert([self._F(2, "add")], CENSUS, "module-context")
        blocks = [r["block"] for r in report["records"]]
        self.assertEqual(blocks, sorted(blocks))

    def test_no_finding_is_lost(self):
        findings = [self._F(1, "add"), self._F(2, "add"), self._F(3, "add")]
        report = record.convert(findings, CENSUS, "module-context")
        ruled = [r for r in report["records"] if r["verdict"] is not None]
        self.assertEqual(len(ruled), 3)


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
        self.assertEqual(len(written["records"]), 2)
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
        report["records"][0].update(verdict="drop", claim={"from": "x"})
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
            "address": "a.py:1-2",
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
        problem = record.version_problem({"record_version": "2"})
        self.assertIn("'2'", problem)
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

    BLOCK = {
        "path": "a.py",
        "start": 1,
        "end": 1,
        "kind": "comment",
        "text": "x",
        "raw_lines": ["# x"],
    }

    def _rec(self, anchor):
        return {
            "block": 1,
            "address": "a.py:1-1",
            "verdict": "add",
            "claim": {"missing": "a note", "anchor": anchor, "side": "below"},
            "reason": "derived it",
            "sources": [{"cite": "a.py:1", "verbatim": "# x"}],
            "change": ["# x", "# a note"],
        }

    def test_a_bare_anchor_is_refused(self):
        problems = record.record_problems("block 1", self._rec("compute"), self.BLOCK)
        self.assertEqual(len(problems), 1)
        self.assertIn("backticks", problems[0])

    def test_a_backticked_anchor_passes(self):
        self.assertEqual(
            record.record_problems("block 1", self._rec("`compute`"), self.BLOCK), []
        )

    def test_an_empty_anchor_is_reported_as_EMPTY_not_as_unbackticked(self):
        # ! Two messages for two mistakes. A reviewer fixes them differently.
        problems = record.record_problems("block 1", self._rec(""), self.BLOCK)
        self.assertEqual(len(problems), 1)
        self.assertIn("empty", problems[0])

    def test_the_template_SAYS_the_form(self):
        # !! The file's own rule: constraining a field without saying what is
        # allowed has only moved the guessing.
        # ! Beside `scope_shape`, not under `values`: it is a FORM, and
        # `values` holds the closed sets a field may be one of.
        self.assertIn("backticks", record.allowed()["anchor_form"])


# !! LAST LINE, ALWAYS. A runner placed above a class runs before that class
# exists, so `python tests/<file>.py` reports a green bar over a shorter suite
# than `unittest discover`.
if __name__ == "__main__":
    unittest.main()
