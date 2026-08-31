"""One stage's returned copies, folded into the copy chief's own.

! INPUTS ARE REAL -- binders from `bind`-shaped helpers, copies from the real
`seed`, marks built through `desk.mark.INSTRUCTIONS`. A literal appears only
where MALFORMED is the input.
"""

import pytest
from helpers import (
    REPO,
    _keeping_only,
    _without_sheet,
    a_binder_over,
    a_clean,
    a_copy_missing_its_sheets,
    a_correct,
    a_correct_citing,
    a_correct_setting,
    a_move,
    an_add,
    copies_over,
    seed,
)

from comment_review.desk.mark import parse
from comment_review.flows.collate import _reconcilable, collate

BASE = "# one\n# two\n# three\n"


def one_place():
    return a_binder_over({"m.py@b1": BASE})


def two_places():
    return a_binder_over({"m.py@b1": BASE, "m.py@b5": BASE})


class TestTheResolutions:
    def test_one_owing_mark_settles_onto_the_chiefs_copy(self):
        binder = one_place()
        copies = copies_over(
            binder, {"block-context": {"m.py@b1": a_correct("m.py@b1")}}
        )
        got = collate("4c", copies, binder, root=REPO)
        assert got.escalations == []
        assert got.rereads == []
        marks = [m for s in got.chief["sheets"] for m in s["marks"]]
        assert [m["address"] for m in marks] == ["m.py@b1"]

    def test_byte_identical_changes_are_not_a_contest(self):
        binder = one_place()
        same = "# one\n# TWO\n# three\n"
        copies = copies_over(
            binder,
            {
                "block-context": {"m.py@b1": a_correct_setting("m.py@b1", "two", same)},
                "function-context": {
                    "m.py@b1": a_correct_setting("m.py@b1", "two", same)
                },
            },
        )
        got = collate("4c", copies, binder, root=REPO)
        assert got.escalations == []
        marks = [m for s in got.chief["sheets"] for m in s["marks"]]
        assert [m["change"] for m in marks] == [same]

    def test_two_answers_to_one_sentence_escalate_and_reach_no_copy(self):
        binder = one_place()
        copies = copies_over(
            binder,
            {
                "block-context": {
                    "m.py@b1": a_correct_setting(
                        "m.py@b1", "two", "# one\n# TWO\n# three\n"
                    )
                },
                "function-context": {
                    "m.py@b1": a_correct_setting(
                        "m.py@b1", "two", "# one\n# dos\n# three\n"
                    )
                },
            },
        )
        got = collate("4c", copies, binder, root=REPO)
        assert [e["address"] for e in got.escalations] == ["m.py@b1"]
        assert [m for s in got.chief["sheets"] for m in s["marks"]] == []

    def test_disjoint_edits_compose_onto_the_chiefs_copy(self):
        binder = one_place()
        copies = copies_over(
            binder,
            {
                "block-context": {
                    "m.py@b1": a_correct_setting(
                        "m.py@b1", 0, "# ONE\n# two\n# three\n"
                    )
                },
                "function-context": {
                    "m.py@b1": a_correct_setting(
                        "m.py@b1", 2, "# one\n# two\n# THREE\n"
                    )
                },
            },
        )
        got = collate("4c", copies, binder, root=REPO)
        assert got.escalations == []
        assert got.rereads == []
        marks = [m for s in got.chief["sheets"] for m in s["marks"]]
        assert [m["change"] for m in marks] == ["# ONE\n# two\n# THREE\n"]

    def test_a_refused_compose_stays_a_reread(self):
        binder = one_place()
        copies = copies_over(
            binder,
            {
                "block-context": {
                    "m.py@b1": a_correct_setting(
                        "m.py@b1", 0, "# ONE\n# two\n# three\n"
                    )
                },
                "function-context": {
                    "m.py@b1": a_correct_setting(
                        "m.py@b1", 1, "# UNO\n# two\n# three\n"
                    )
                },
            },
        )
        got = collate("4c", copies, binder, root=REPO)
        assert [e["address"] for e in got.rereads] == ["m.py@b1"]
        assert [m for s in got.chief["sheets"] for m in s["marks"]] == []

    def test_every_role_clean_produces_an_empty_copy_and_no_carry_forward(self):
        binder = one_place()
        copies = copies_over(
            binder,
            {
                "block-context": {"m.py@b1": a_clean("m.py@b1")},
                "function-context": {"m.py@b1": a_clean("m.py@b1")},
            },
        )
        got = collate("4c", copies, binder, root=REPO)
        assert got.escalations == []
        assert got.rereads == []
        assert [m for s in got.chief["sheets"] for m in s["marks"]] == []

    def test_an_add_is_carried_forward(self):
        """`_outcome` widens an `add` to every role of the stage, because two
        adds at two addresses never meet under per-place grouping."""
        binder = one_place()
        copies = copies_over(binder, {"block-context": {"m.py@b1": an_add("m.py@b1")}})
        got = collate("4c", copies, binder, root=REPO)
        assert [e["address"] for e in got.rereads] == ["m.py@b1"]


class TestTheChiefsCopy:
    def test_it_parses_as_an_ordinary_edit_copy(self):
        binder = one_place()
        copies = copies_over(
            binder, {"block-context": {"m.py@b1": a_correct("m.py@b1")}}
        )
        got = collate("4c", copies, binder, root=REPO)
        from comment_review.desk.containers import parse_edit_copy

        copy, why = parse_edit_copy("the chief's", got.chief)
        assert why == []
        assert copy is not None
        assert copy.role == "copy-chief"

    def test_every_mark_on_it_parses(self):
        binder = one_place()
        copies = copies_over(
            binder, {"block-context": {"m.py@b1": a_correct("m.py@b1")}}
        )
        got = collate("4c", copies, binder, root=REPO)
        for sheet in got.chief["sheets"]:
            for entry in sheet["marks"]:
                mark, why = parse(entry["address"], entry)
                assert why == [], why
                assert mark is not None

    def test_a_composed_mark_carries_both_sides_sources(self):
        binder = one_place()
        copies = copies_over(
            binder,
            {
                "block-context": {
                    "m.py@b1": a_correct_setting(
                        "m.py@b1", 0, "# ONE\n# two\n# three\n"
                    )
                },
                "function-context": {
                    "m.py@b1": a_correct_setting(
                        "m.py@b1", 2, "# one\n# two\n# THREE\n"
                    )
                },
            },
        )
        got = collate("4c", copies, binder, root=REPO)
        entry = [m for s in got.chief["sheets"] for m in s["marks"]][0]
        assert len(entry["sources"]) == 2
        assert "block-context" in entry["reason"]
        assert "function-context" in entry["reason"]

    def test_sources_and_reason_AGREE_on_the_roles_ORDER(self):
        """!! `reason` NAMES THE ROLES ALPHABETICALLY (`roles = sorted(sides)`
        below `_composition`). `sources` must walk the SAME order rather than
        `owing`'s dispatch order -- the order `edit_copies` happened to be
        handed to `collate` in, which is not a property of the data. Three
        roles, dispatched in a non-alphabetical order, over three
        non-adjacent spans of a 7-line base so all three compose."""
        binder = a_binder_over({"m.py@b1": "# a\n# b\n# c\n# d\n# e\n# f\n# g\n"})
        by_role = {
            "zebra-context": a_correct_setting(
                "m.py@b1", 0, "# A\n# b\n# c\n# d\n# e\n# f\n# g\n"
            ),
            "apple-context": a_correct_setting(
                "m.py@b1", 1, "# a\n# b\n# c\n# D\n# e\n# f\n# g\n"
            ),
            "mango-context": a_correct_setting(
                "m.py@b1", 2, "# a\n# b\n# c\n# d\n# e\n# f\n# G\n"
            ),
        }
        for role, mark in by_role.items():
            mark["sources"] = [{"cite": f"{role}.py:1", "verbatim": "x"}]
        copies = copies_over(
            binder, {role: {"m.py@b1": mark} for role, mark in by_role.items()}
        )
        assert [c["role"] for c in copies] == [
            "zebra-context",
            "apple-context",
            "mango-context",
        ]
        got = collate("4c", copies, binder, root=REPO)
        entry = [m for s in got.chief["sheets"] for m in s["marks"]][0]
        roles_in_reason = entry["reason"].split(" by ")[1].split(" -- ")[0].split(", ")
        roles_in_sources = [s["cite"].split(".py:")[0] for s in entry["sources"]]
        assert roles_in_reason == sorted(roles_in_reason)
        assert roles_in_sources == roles_in_reason

    def test_a_null_sha_reads_as_ABSENT_not_the_word_None(self):
        """!! `.get("sha", "")` DEFAULTS ONLY WHEN THE KEY IS ABSENT. A sheet
        carrying `"sha": null` reaches this module's own copy of
        `desk.collator._real_pages` with the key PRESENT and holding None, so
        `.get` returns None and `str(None)` is the four-character word "None"
        -- the same class of defect as a null `verbatim` rendering as the
        word "None" in `results/verdicts.py`."""
        binder = one_place()
        copies = copies_over(
            binder, {"block-context": {"m.py@b1": a_correct("m.py@b1")}}
        )
        copies[0]["sheets"][0]["sha"] = None
        got = collate("4c", copies, binder, root=REPO)
        assert got.chief["sheets"][0]["sha"] == ""

    def test_an_unresolved_place_is_ABSENT_not_untouched(self):
        """!! `untouched` MEANS NOBODY WROTE HERE. A place two roles wrote on
        that nothing resolved is a different fact, and writing it as an
        untouched slot would give one shape two meanings."""
        from comment_review.desk.mark import untouched

        binder = one_place()
        copies = copies_over(
            binder,
            {
                "block-context": {
                    "m.py@b1": a_correct_setting("m.py@b1", "two", "# a\n")
                },
                "function-context": {
                    "m.py@b1": a_correct_setting("m.py@b1", "two", "# b\n")
                },
            },
        )
        got = collate("4c", copies, binder, root=REPO)
        entries = [m for s in got.chief["sheets"] for m in s["marks"]]
        assert entries == []
        assert not any(untouched(e) for e in entries)


class TestTheEnvelope:
    """`P21`, `Process: #57`. Is this document a copy at all?

    !! REPORTED, NOT RAISED, AND THE RUN STILL ERRORS OUT. `commands/collate.py`
    prints every `Problem` and returns BROKEN without writing the chief copy, so
    the refusal is preserved while the report survives it. A raise here is
    finding #6 of the 2026-08-30 review: one role's bad envelope emptying stdout
    for every other role.
    """

    #: The three shapes `desk.collator.problems_in` cannot see. Its sheet walk
    #: reads `if not isinstance(marks, list): continue` (`collator.py:483-485`),
    #: so a sheet that is not an object and a sheet whose `marks` is not a list
    #: are SKIPPED, and `path` is never its question at all.
    #:
    #: !! MEASURED 2026-08-31 BEFORE THE ENVELOPE LANDED: all three gave
    #: `problems == []`, exit 0, and a chief copy written without that page's
    #: marks. A `sheets` key that is not a list is NOT among them -- that one
    #: `problems_in` already reports, which is why it is not the test here.
    UNSEEN = {
        "a sheet that is not an object": lambda c: c["sheets"].insert(0, "nope"),
        "a sheet whose marks is not a list": lambda c: c["sheets"][0].update(
            marks="nope"
        ),
        "a sheet with no path": lambda c: c["sheets"][0].pop("path"),
    }

    def a_copy_shaped(self, binder, mangle):
        copies = copies_over(
            binder, {"block-context": {"m.py@b1": a_correct("m.py@b1")}}
        )
        mangle(copies[0])
        return copies

    @pytest.mark.parametrize("name", sorted(UNSEEN))
    def test_a_copy_that_is_not_the_shape_of_a_copy_is_named_on_its_role(self, name):
        binder = one_place()
        got = collate(
            "4c", self.a_copy_shaped(binder, self.UNSEEN[name]), binder, root=REPO
        )
        assert [p.role for p in got.problems] == ["block-context"], name

    @pytest.mark.parametrize("name", sorted(UNSEEN))
    def test_no_chief_copy_is_folded_from_a_partial_set(self, name):
        """A silently partial chief -- one role's rulings missing, nothing
        saying so -- is what both mechanisms exist to prevent."""
        binder = one_place()
        got = collate(
            "4c", self.a_copy_shaped(binder, self.UNSEEN[name]), binder, root=REPO
        )
        assert got.chief["sheets"] == [], name

    def test_one_malformed_copy_does_not_silence_another_role(self):
        binder = one_place()
        bad = self.a_copy_shaped(binder, self.UNSEEN["a sheet with no path"])
        good = copies_over(
            binder, {"function-context": {"m.py@b1": a_correct("m.py@b1")}}
        )
        good[0]["sheets"][0]["marks"][0]["claim"] = {}
        got = collate("4c", bad + good, binder, root=REPO)
        assert {p.role for p in got.problems} == {"block-context", "function-context"}

    def test_the_master_proof_is_parsed_at_its_own_boundary(self, monkeypatch):
        """`P21`, `Process: #57` one level up. `gather` builds the proof and
        nothing states what a proof IS before `reconcile` walks it.

        ! THE PROOF IS BUILT INSIDE `collate`, so the only way to hand it a
        malformed one is to make `gather` return it. That is a seam, not a
        shape the chain can otherwise produce -- which is the point: the parse
        exists for what a FUTURE change could put there.
        """
        binder = one_place()
        copies = copies_over(
            binder, {"block-context": {"m.py@b1": a_correct("m.py@b1")}}
        )
        monkeypatch.setattr(
            "comment_review.flows.collate.gather",
            lambda stage, edit_copies: {"stage": stage, "edit_copies": "nope"},
        )
        got = collate("4c", copies, binder, root=REPO)
        assert any("edit_copies" in p.message for p in got.problems)
        assert got.chief["sheets"] == []

    def test_a_copy_missing_its_sheets_is_still_reported(self):
        """`problems_in` already answers this one; the envelope must not make
        its report vanish by refusing first and returning a different message."""
        binder = one_place()
        got = collate("4c", [a_copy_missing_its_sheets(binder)], binder, root=REPO)
        assert [p.role for p in got.problems] == ["block-context"]
        assert "sheets" in got.problems[0].message

    def test_a_well_formed_copy_still_reaches_the_per_mark_checks(self):
        """A container that refuses too much makes per-mark reporting
        unreachable, which is this plan's own defect from the other side."""
        binder = one_place()
        copies = copies_over(
            binder, {"block-context": {"m.py@b1": a_correct("m.py@b1")}}
        )
        copies[0]["sheets"][0]["marks"][0]["claim"] = {}
        got = collate("4c", copies, binder, root=REPO)
        assert [p.address for p in got.problems] == ["m.py@b1"]


class TestSourceVerificationRunsInProduction:
    """`P25`, `Process: #58`. Roy: *"the source-verification side needs to be
    wired into the flow - same as 1) the flow coordinates the things in the
    modules do."*

    !! REPORTED BY A RUN OF THE FLOW, not by calling the function. MEASURED
    2026-08-31 before this landed: `verify_report`, `address_problems`,
    `claim_verbatim_problems` and `source_problems` had test callers only.

    ! NEITHER OF THESE IS REFUSABLE BY `desk.mark.parse`, which imports no
    binder, no page and no filesystem. That is what makes them the flow's to
    ask rather than the mark's.
    """

    def test_a_citation_that_does_not_resolve_is_reported_by_a_RUN(self, tmp_path):
        binder = one_place()
        copies = copies_over(
            binder,
            {
                "block-context": {
                    "m.py@b1": a_correct_citing("m.py@b1", "nowhere.py:99")
                }
            },
        )
        got = collate("4c", copies, binder, root=tmp_path)
        assert any("nowhere.py" in p.message for p in got.problems)

    def test_a_source_finding_names_the_role_and_the_address(self, tmp_path):
        """`Problem` exists so a finding can be ROUTED. A source-verification
        finding names a mark, so it carries both -- an empty address would make
        it unroutable, which is the defect the type was introduced to end."""
        binder = one_place()
        copies = copies_over(
            binder,
            {
                "block-context": {
                    "m.py@b1": a_correct_citing("m.py@b1", "nowhere.py:99")
                }
            },
        )
        got = collate("4c", copies, binder, root=tmp_path)
        found = [p for p in got.problems if "nowhere.py" in p.message]
        assert [(p.role, p.address) for p in found] == [("block-context", "m.py@b1")]

    def test_a_claim_quoting_a_sentence_absent_from_its_paragraph_is_reported(
        self, tmp_path
    ):
        binder = one_place()
        copies = copies_over(
            binder,
            {
                "block-context": {
                    "m.py@b1": a_correct("m.py@b1", "a sentence that is not there")
                }
            },
        )
        got = collate("4c", copies, binder, root=tmp_path)
        assert got.problems != []

    def test_a_clean_run_still_reports_nothing(self, tmp_path):
        """The other side of it: verification must not invent a finding."""
        binder = one_place()
        copies = copies_over(binder, {"block-context": {"m.py@b1": a_clean("m.py@b1")}})
        got = collate("4c", copies, binder, root=tmp_path)
        assert got.problems == []


class TestOneDefinitionOfAWellFormedCopy:
    """`P21`, T4, `Process: #57`. The container decides; nothing re-decides.

    !! A CUT GUARD CANNOT BE TESTED BY BEHAVIOUR ALONE, because a guard that
    could not fire changes no output when it goes. What IS testable is the
    consequence: `flows/collate.py`'s internals now DEPEND on the envelope
    having run, so the boundary is load-bearing rather than decorative. Both
    halves below can fail -- the first if a guard creeps back into
    `_reconcilable`, the second if the envelope stops running first.
    """

    def a_copy_whose_sheet_is_not_an_object(self):
        binder = one_place()
        copies = copies_over(
            binder, {"block-context": {"m.py@b1": a_correct("m.py@b1")}}
        )
        copies[0]["sheets"].insert(0, "nope")
        return binder, copies

    def test_reconcilable_no_longer_decides_what_a_sheet_is(self):
        """It passed a malformed sheet through, standing in for the container.
        Now it assumes the shape, which is what ONE definition means."""
        _binder, copies = self.a_copy_whose_sheet_is_not_an_object()
        with pytest.raises(TypeError):
            _reconcilable(copies[0])

    def test_and_the_flow_never_reaches_it_with_one(self):
        """The other half: the envelope answers first, so the assumption above
        is safe in production. A `TypeError` escaping here would mean the
        boundary had stopped running before the fold."""
        binder, copies = self.a_copy_whose_sheet_is_not_an_object()
        got = collate("4c", copies, binder, root=REPO)
        assert [p.role for p in got.problems] == ["block-context"]
        assert "sheet" in got.problems[0].message


class TestShardCoverage:
    """`P27`, `containers-and-verification-are-unwired` T6, `Process: #63`.

    !! `flows.fan_out.fan` REFUSES AN UNCOVERED PAGE AT THE DISPATCH; NOTHING
    READ THE RETURN. A partitioned role that answered for three of four files
    in its shard was invisible.

    !! THE UNIT IS THE ADDRESS, NOT THE PAGE. `P27` says files; T6 says the
    address set and carries the harder case -- a copy that kept 1 of its 4
    seeded slots. A dropped page is a dropped address set, so the address check
    answers both; a page check answers only `P27`.

    ! REPORTED, NOT REFUSED -- `Process: #63`. An incomplete shard is a fact
    about one role's coverage, not a statement that the documents are
    malformed, so the places that DID come back still settle.
    """

    def test_a_role_that_answered_for_part_of_its_shard_is_named(self):
        binder = two_places()
        copies = copies_over(binder, {"block-context": {"m.py@b1": a_clean("m.py@b1")}})
        short = [_without_sheet(copies[0], "m.py")]
        got = collate("4c", short, binder, root=REPO)
        assert [p.role for p in got.problems] == ["block-context"]
        assert "m.py@b1" in got.problems[0].message

    def test_a_copy_that_kept_one_of_its_four_seeded_slots_is_named(self):
        """T6's own measured case: today all four of its shapes give
        `problems == []` against a binder carrying `m.py@b1..b4`."""
        binder = a_binder_over({f"m.py@b{n}": BASE for n in (1, 2, 3, 4)})
        copies = copies_over(binder, {"block-context": {"m.py@b1": a_clean("m.py@b1")}})
        got = collate("4c", [_keeping_only(copies[0], ["m.py@b1"])], binder, root=REPO)
        assert [p.role for p in got.problems] == ["block-context"]
        for missing in ("m.py@b2", "m.py@b3", "m.py@b4"):
            assert missing in got.problems[0].message

    def test_two_shards_of_one_role_cover_the_binder_between_them(self):
        """!! COMPARED PER COPY THIS REPORTS EVERY FAN-OUT SHARD AS INCOMPLETE.
        `unruled` and `tally` are keyed by role and clobber under fan-out; this
        is what proves the coverage check did not copy that pattern."""
        binder = a_binder_over({"one.py@b1": BASE, "two.py@b1": BASE})
        halves = [
            {**seed(binder, "block-context"), "sheets": [sheet]}
            for sheet in seed(binder, "block-context")["sheets"]
        ]
        assert len(halves) == 2
        got = collate("4c", halves, binder, root=REPO)
        assert got.problems == []

    def test_the_places_that_did_come_back_still_settle(self):
        """`Process: #63` -- coverage reports; it does not void the round."""
        binder = two_places()
        copies = copies_over(
            binder, {"block-context": {"m.py@b1": a_correct("m.py@b1")}}
        )
        got = collate("4c", [_keeping_only(copies[0], ["m.py@b1"])], binder, root=REPO)
        assert got.problems != []
        marks = [m for s in got.chief["sheets"] for m in s["marks"]]
        assert [m["address"] for m in marks] == ["m.py@b1"]


class TestTheStackedCheck:
    def test_a_malformed_copy_is_reported_with_its_role_and_address(self):
        binder = one_place()
        copies = copies_over(
            binder, {"block-context": {"m.py@b1": a_correct("m.py@b1")}}
        )
        copies[0]["sheets"][0]["marks"][0]["claim"] = {}
        got = collate("4c", copies, binder, root=REPO)
        assert got.problems
        assert got.problems[0].role == "block-context"
        assert got.problems[0].address == "m.py@b1"

    def test_TWO_malformed_copies_are_BOTH_reported(self):
        """!! IT DOES NOT STOP AT THE FIRST BAD COPY. Roy, 2026-08-30: the
        errors stack so each can be fixed or sent back to the role. A check
        that stopped here would hide the second until the next run."""
        binder = one_place()
        copies = copies_over(
            binder,
            {
                "block-context": {"m.py@b1": a_correct("m.py@b1")},
                "function-context": {"m.py@b1": a_correct("m.py@b1")},
            },
        )
        for copy in copies:
            copy["sheets"][0]["marks"][0]["claim"] = {}
        got = collate("4c", copies, binder, root=REPO)
        assert {p.role for p in got.problems} == {"block-context", "function-context"}

    def test_a_copy_carrying_no_read_from_is_named_and_folds_nothing(self):
        """A field a stage FABRICATES is a field the boundary can no longer
        refuse -- which is why `_reconcilable` filters rather than produces.

        !! THE MECHANISM MOVED ON 2026-08-31 AND THE PROPERTY DID NOT. Written
        first against `desk.proof.gather`'s `KeyError`, because `_reconcilable`
        through `EditCopy.seed` handed it `read_from: {}` and the raise could
        not fire. The envelope parse now answers one step earlier and REPORTS,
        so there is no `KeyError` left to catch -- see
        `TestTheEnvelope`. What is still asserted is that an absent
        `read_from` is never silently filled in on the way past.
        """
        binder = one_place()
        copies = copies_over(
            binder, {"block-context": {"m.py@b1": a_correct("m.py@b1")}}
        )
        del copies[0]["read_from"]
        got = collate("4c", copies, binder, root=REPO)
        assert [p.role for p in got.problems] == ["block-context"]
        assert "read_from" in got.problems[0].message
        assert got.chief["sheets"] == []

    def test_reconcilable_preserves_an_absent_read_from(self):
        """The property directly, since the envelope now guards the flow path.

        `_reconcilable` runs only after the parse has passed, so `collate` can
        no longer reach it with the field missing. The rule still binds the
        function: a filter that fabricates a field defeats whatever checks it.
        """
        binder = one_place()
        copies = copies_over(
            binder, {"block-context": {"m.py@b1": a_correct("m.py@b1")}}
        )
        del copies[0]["read_from"]
        assert "read_from" not in _reconcilable(copies[0])

    def test_drift_is_reported_and_does_not_stop_the_fold(self):
        binder = one_place()
        copies = copies_over(
            binder, {"block-context": {"m.py@b1": a_correct("m.py@b1")}}
        )
        copies[0]["sheets"][0]["marks"][0]["raw_text"] = "# not what was seeded\n"
        got = collate("4c", copies, binder, root=REPO)
        assert [p.address for p in got.drift] == ["m.py@b1"]
        assert [m for s in got.chief["sheets"] for m in s["marks"]] != []


class TestTheMovesAreADag:
    def test_a_move_resolves_only_if_BOTH_its_ends_resolve(self):
        """! PINS `desk.collator._join_moves`, NOT THIS TASK'S CODE. Traced
        2026-08-30: `resolved` never holds either address here -- b5 carries
        two owing marks with different `_sentence_key`s (the move's `id(mark)`
        and the `correct`'s quoted sentence), so `_join_moves` promotes BOTH
        ends to `rereads` before `_resolve` runs, and `_pair_moves` sees `{}`
        moves. Deleting `_pair_moves` and its wiring would not change this
        test's outcome. Kept as regression cover for the property it names --
        a move does not half-apply -- with the DAG logic itself covered by
        `TestPairMoves`, below."""
        binder = two_places()
        copies = copies_over(
            binder,
            {
                "block-context": {"m.py@b1": a_move("m.py@b1", "m.py@b5")},
                "function-context": {
                    "m.py@b5": a_correct_setting("m.py@b5", "two", "# a\n")
                },
            },
        )
        got = collate("4c", copies, binder, root=REPO)
        assert [m for s in got.chief["sheets"] for m in s["marks"]] == []
        assert {e["address"] for e in got.rereads} >= {"m.py@b1", "m.py@b5"}

    def test_independent_moves_emit_in_a_stable_order(self):
        binder = a_binder_over({f"m.py@b{n}": BASE for n in (1, 2, 7, 8)})
        marks = {
            "m.py@b1": a_move("m.py@b1", "m.py@b2"),
            "m.py@b7": a_move("m.py@b7", "m.py@b8"),
        }
        first = collate(
            "4c", copies_over(binder, {"block-context": marks}), binder, root=REPO
        )
        flipped = dict(reversed(list(marks.items())))
        second = collate(
            "4c", copies_over(binder, {"block-context": flipped}), binder, root=REPO
        )
        assert first.order == second.order

    def test_a_move_whose_origin_another_move_fills_is_emitted_FIRST(self):
        """B must VACATE the address before A fills it.

        ! PINS `desk.collator._join_moves`, NOT THIS TASK'S CODE. Traced
        2026-08-30: `resolved` is `{}` here -- b5 carries two owing move marks
        (b1's destination touch and b5's own address), different
        `id(mark)`-valued `_sentence_key`s, so `_join_moves`'s fixed point
        promotes all three addresses to `rereads` before `_resolve` runs, and
        the guarded assertion below never fires. Deleting `_move_order` and its
        wiring would not change this test's outcome. Kept as regression cover
        for stable emission of an independent-looking pair, with the
        vacate-before-fill ordering itself covered by
        `test_a_chain_orders_rather_than_cycling`'s direct call to
        `_move_order`."""
        binder = a_binder_over({f"m.py@b{n}": BASE for n in (1, 5, 9)})
        marks = {
            "m.py@b1": a_move("m.py@b1", "m.py@b5"),
            "m.py@b5": a_move("m.py@b5", "m.py@b9"),
        }
        copies = copies_over(binder, {"block-context": marks})
        got = collate("4c", copies, binder, root=REPO)
        resolved = {e["address"]: e for s in got.chief["sheets"] for e in s["marks"]}
        if "m.py@b1" in resolved and "m.py@b5" in resolved:
            assert got.order.index("m.py@b5") < got.order.index("m.py@b1")

    def test_a_cycle_is_carried_forward_and_NAMED(self):
        """! DRIVEN WITH A `Reconciled` BUILT DIRECTLY, because no cycle
        reaches the resolution step through `reconcile` today -- a shared
        address is a two-mark place. That is exactly why the rule is written:
        the protection upstream is a side effect, and a side effect is not a
        rule."""
        from comment_review.desk.mark import parse
        from comment_review.flows.collate import _move_order

        def a_resolved_move(origin, destination):
            mark, why = parse(origin, a_move(origin, destination))
            assert why == [], why
            assert mark is not None, "parse returned no mark despite why == []"
            return mark

        resolved = {
            "m.py@b1": a_resolved_move("m.py@b1", "m.py@b2"),
            "m.py@b2": a_resolved_move("m.py@b2", "m.py@b1"),
        }
        order, cycle = _move_order(resolved)
        assert order == []
        assert set(cycle) == {"m.py@b1", "m.py@b2"}

    def test_a_chain_orders_rather_than_cycling(self):
        from comment_review.desk.mark import parse
        from comment_review.flows.collate import _move_order

        def a_resolved_move(origin, destination):
            mark, why = parse(origin, a_move(origin, destination))
            assert why == [], why
            assert mark is not None, "parse returned no mark despite why == []"
            return mark

        resolved = {
            "m.py@b1": a_resolved_move("m.py@b1", "m.py@b5"),
            "m.py@b5": a_resolved_move("m.py@b5", "m.py@b9"),
        }
        order, cycle = _move_order(resolved)
        assert cycle == []
        assert order.index("m.py@b5") < order.index("m.py@b1")


class TestPairMoves:
    """`_pair_moves` DRIVEN DIRECTLY, for the same reason
    `test_a_cycle_is_carried_forward_and_NAMED` is: `desk.collator._join_moves`
    already gives both ends of a move ONE outcome before `_resolve` ever builds
    a `resolved` dict, so `_pair_moves`'s own withdrawal branch cannot fire
    through `collate()` today -- see its docstring. These build `resolved` by
    hand, the one shape a caller bypassing `_join_moves` could still produce."""

    def test_withdraws_a_move_whose_other_end_is_absent(self):
        from comment_review.desk.mark import parse
        from comment_review.flows.collate import _pair_moves

        mark, why = parse("m.py@b1", a_move("m.py@b1", "m.py@b5"))
        assert why == [], why
        assert mark is not None, "parse returned no mark despite why == []"
        resolved = {"m.py@b1": mark}  # "m.py@b5" is not in `resolved` at all

        assert _pair_moves(resolved) == {"m.py@b1"}

    def test_withdrawal_cascades_through_a_chain(self):
        """B's destination (b3) is unresolved, so B withdraws first; A's
        destination is B's address (b2), which only becomes withdrawn on that
        same pass -- so A is orphaned one pass LATER, and a single un-looped
        pass over `resolved` (in insertion order: b1 then b2) would check A
        while b2 still looks resolved and miss it. This is what the fixed
        point in `_pair_moves`'s docstring is for."""
        from comment_review.desk.mark import parse
        from comment_review.flows.collate import _pair_moves

        a_mark, why_a = parse("m.py@b1", a_move("m.py@b1", "m.py@b2"))
        b_mark, why_b = parse("m.py@b2", a_move("m.py@b2", "m.py@b3"))
        assert why_a == [], why_a
        assert why_b == [], why_b
        assert a_mark is not None, "parse returned no mark despite why_a == []"
        assert b_mark is not None, "parse returned no mark despite why_b == []"
        resolved = {"m.py@b1": a_mark, "m.py@b2": b_mark}  # "m.py@b3" absent

        assert _pair_moves(resolved) == {"m.py@b1", "m.py@b2"}


class TestAResolvedMoveIsOneEntry:
    """`_chief_copy` -- `resolved` carries a settled `move`'s `Mark` under
    BOTH its addresses (`desk.collator._join_moves` gives both ends one
    outcome), but the chief's copy must write it ONCE, at its own origin.
    Regression cover for the double-write / mislabelled-destination defect
    fixed 2026-08-30."""

    def test_two_independent_moves_write_one_entry_each_at_their_origins(self):
        binder = a_binder_over({f"m.py@b{n}": BASE for n in (1, 2, 7, 8)})
        marks = {
            "m.py@b1": a_move("m.py@b1", "m.py@b2"),
            "m.py@b7": a_move("m.py@b7", "m.py@b8"),
        }
        got = collate(
            "4c", copies_over(binder, {"block-context": marks}), binder, root=REPO
        )
        entries = [m for s in got.chief["sheets"] for m in s["marks"]]
        assert [e["address"] for e in entries] == ["m.py@b1", "m.py@b7"]

    def test_a_cross_file_move_lands_only_in_the_origins_sheet(self):
        binder = a_binder_over({"a.py@b1": BASE, "b.py@b1": BASE})
        marks = {"a.py@b1": a_move("a.py@b1", "b.py@b1")}
        got = collate(
            "4c", copies_over(binder, {"block-context": marks}), binder, root=REPO
        )
        sheets = {
            s["path"]: [m["address"] for m in s["marks"]] for s in got.chief["sheets"]
        }
        # ! NO "b.py" SHEET AT ALL -- `_chief_copy` only ever creates a sheet
        # when it has an entry to put in it, and the destination writes none.
        assert sheets == {"a.py": ["a.py@b1"]}

    def test_every_entry_on_the_chiefs_copy_still_parses(self):
        """The other option -- writing a second entry at the destination with
        `address` rewritten to it -- cannot satisfy this: `claim.to` would
        then equal that entry's own `address`, which `desk.mark.parse`
        refuses by name (`desk.mark._destination_problems`) as a move to
        where the paragraph already is."""
        binder = a_binder_over({"m.py@b1": BASE, "m.py@b5": BASE})
        marks = {"block-context": {"m.py@b1": a_move("m.py@b1", "m.py@b5")}}
        got = collate("4c", copies_over(binder, marks), binder, root=REPO)
        for sheet in got.chief["sheets"]:
            for entry in sheet["marks"]:
                mark, why = parse(entry["address"], entry)
                assert why == [], why
                assert mark is not None

    def test_the_chiefs_copy_still_parses_as_an_ordinary_edit_copy(self):
        from comment_review.desk.containers import parse_edit_copy

        binder = a_binder_over({"m.py@b1": BASE, "m.py@b5": BASE})
        marks = {"block-context": {"m.py@b1": a_move("m.py@b1", "m.py@b5")}}
        got = collate("4c", copies_over(binder, marks), binder, root=REPO)
        copy, why = parse_edit_copy("the chief's", got.chief)
        assert why == []
        assert copy is not None
