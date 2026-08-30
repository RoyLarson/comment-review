"""One stage's returned copies, folded into the copy chief's own.

! INPUTS ARE REAL -- binders from `bind`-shaped helpers, copies from the real
`seed`, marks built through `desk.mark.INSTRUCTIONS`. A literal appears only
where MALFORMED is the input.
"""

from helpers import (
    a_binder_over,
    a_clean,
    a_correct,
    a_correct_setting,
    an_add,
    copies_over,
)

from comment_review.desk.mark import parse
from comment_review.flows.collate import collate

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
        got = collate("4c", copies, binder)
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
        got = collate("4c", copies, binder)
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
        got = collate("4c", copies, binder)
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
        got = collate("4c", copies, binder)
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
        got = collate("4c", copies, binder)
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
        got = collate("4c", copies, binder)
        assert got.escalations == []
        assert got.rereads == []
        assert [m for s in got.chief["sheets"] for m in s["marks"]] == []

    def test_an_add_is_carried_forward(self):
        """`_outcome` widens an `add` to every role of the stage, because two
        adds at two addresses never meet under per-place grouping."""
        binder = one_place()
        copies = copies_over(binder, {"block-context": {"m.py@b1": an_add("m.py@b1")}})
        got = collate("4c", copies, binder)
        assert [e["address"] for e in got.rereads] == ["m.py@b1"]


class TestTheChiefsCopy:
    def test_it_parses_as_an_ordinary_edit_copy(self):
        binder = one_place()
        copies = copies_over(
            binder, {"block-context": {"m.py@b1": a_correct("m.py@b1")}}
        )
        got = collate("4c", copies, binder)
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
        got = collate("4c", copies, binder)
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
        got = collate("4c", copies, binder)
        entry = [m for s in got.chief["sheets"] for m in s["marks"]][0]
        assert len(entry["sources"]) == 2
        assert "block-context" in entry["reason"]
        assert "function-context" in entry["reason"]

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
        got = collate("4c", copies, binder)
        entries = [m for s in got.chief["sheets"] for m in s["marks"]]
        assert entries == []
        assert not any(untouched(e) for e in entries)


class TestTheStackedCheck:
    def test_a_malformed_copy_is_reported_with_its_role_and_address(self):
        binder = one_place()
        copies = copies_over(
            binder, {"block-context": {"m.py@b1": a_correct("m.py@b1")}}
        )
        copies[0]["sheets"][0]["marks"][0]["claim"] = {}
        got = collate("4c", copies, binder)
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
        got = collate("4c", copies, binder)
        assert {p.role for p in got.problems} == {"block-context", "function-context"}

    def test_drift_is_reported_and_does_not_stop_the_fold(self):
        binder = one_place()
        copies = copies_over(
            binder, {"block-context": {"m.py@b1": a_correct("m.py@b1")}}
        )
        copies[0]["sheets"][0]["marks"][0]["raw_text"] = "# not what was seeded\n"
        got = collate("4c", copies, binder)
        assert [p.address for p in got.drift] == ["m.py@b1"]
        assert [m for s in got.chief["sheets"] for m in s["marks"]] != []
