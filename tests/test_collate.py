"""One stage's returned copies, folded into the copy chief's own.

! INPUTS ARE REAL -- binders from `bind`-shaped helpers, copies from the real
`seed`, marks built through `desk.mark.INSTRUCTIONS`. A literal appears only
where MALFORMED is the input.
"""

import pytest
from helpers import (
    a_binder_over,
    a_clean,
    a_correct,
    a_correct_setting,
    a_move,
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
        got = collate("4c", copies, binder)
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
        got = collate("4c", copies, binder)
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

    def test_a_copy_carrying_no_read_from_still_reaches_gathers_refusal(self):
        """`_reconcilable` FILTERS a copy; it must not PRODUCE one.

        MEASURED 2026-08-31: written through `EditCopy.seed`, which requires
        every declared field, it handed `gather` a copy holding `read_from:
        {}` -- and `gather` subscripts that key precisely so an absent one
        raises. A field the filter fabricates is a field the boundary below it
        can no longer refuse.
        """
        binder = one_place()
        copies = copies_over(
            binder, {"block-context": {"m.py@b1": a_correct("m.py@b1")}}
        )
        del copies[0]["read_from"]
        with pytest.raises(KeyError):
            collate("4c", copies, binder)

    def test_drift_is_reported_and_does_not_stop_the_fold(self):
        binder = one_place()
        copies = copies_over(
            binder, {"block-context": {"m.py@b1": a_correct("m.py@b1")}}
        )
        copies[0]["sheets"][0]["marks"][0]["raw_text"] = "# not what was seeded\n"
        got = collate("4c", copies, binder)
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
        got = collate("4c", copies, binder)
        assert [m for s in got.chief["sheets"] for m in s["marks"]] == []
        assert {e["address"] for e in got.rereads} >= {"m.py@b1", "m.py@b5"}

    def test_independent_moves_emit_in_a_stable_order(self):
        binder = a_binder_over({f"m.py@b{n}": BASE for n in (1, 2, 7, 8)})
        marks = {
            "m.py@b1": a_move("m.py@b1", "m.py@b2"),
            "m.py@b7": a_move("m.py@b7", "m.py@b8"),
        }
        first = collate("4c", copies_over(binder, {"block-context": marks}), binder)
        flipped = dict(reversed(list(marks.items())))
        second = collate("4c", copies_over(binder, {"block-context": flipped}), binder)
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
        got = collate("4c", copies, binder)
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
        got = collate("4c", copies_over(binder, {"block-context": marks}), binder)
        entries = [m for s in got.chief["sheets"] for m in s["marks"]]
        assert [e["address"] for e in entries] == ["m.py@b1", "m.py@b7"]

    def test_a_cross_file_move_lands_only_in_the_origins_sheet(self):
        binder = a_binder_over({"a.py@b1": BASE, "b.py@b1": BASE})
        marks = {"a.py@b1": a_move("a.py@b1", "b.py@b1")}
        got = collate("4c", copies_over(binder, {"block-context": marks}), binder)
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
        got = collate("4c", copies_over(binder, marks), binder)
        for sheet in got.chief["sheets"]:
            for entry in sheet["marks"]:
                mark, why = parse(entry["address"], entry)
                assert why == [], why
                assert mark is not None

    def test_the_chiefs_copy_still_parses_as_an_ordinary_edit_copy(self):
        from comment_review.desk.containers import parse_edit_copy

        binder = a_binder_over({"m.py@b1": BASE, "m.py@b5": BASE})
        marks = {"block-context": {"m.py@b1": a_move("m.py@b1", "m.py@b5")}}
        got = collate("4c", copies_over(binder, marks), binder)
        copy, why = parse_edit_copy("the chief's", got.chief)
        assert why == []
        assert copy is not None
