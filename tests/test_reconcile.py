"""`desk/collator.py`'s `places` and `reconcile` -- T4.1 and T4.2,
reconciliation's grouping and its settle/escalate/reread rule.

! INPUTS FROM REALITY, `decision-log.md Vocabulary: #23`: every mark below is
built through `desk.mark.INSTRUCTIONS` by `tests/helpers.py`'s `a_correct`,
`a_move`, `a_clean` and `a_query`, and every `master_proof` is composed
through the real `seed()` and `gather()` by `a_master_proof` -- never a
hand-authored container literal.

!! `reconcile`'s expectation is `Process: #49`, NOT `reconcile` ITSELF --
`CLAUDE.md`'s rule that no test takes its expectation from the code under
test. Settle/escalate/reread come from Roy's own ruling, quoted on
`reconcile`'s docstring; the tests below check the outcomes that ruling
names, not whatever the function happens to return.
"""

from helpers import a_clean, a_correct, a_master_proof, a_move, a_query, an_add

from comment_review.desk.collator import places, reconcile
from comment_review.desk.mark import Shape


def test_a_move_lands_in_both_the_origin_and_the_destination():
    # T1's failing case: a move a0 -> a8 against another role's correct on a8.
    proof = a_master_proof(
        {
            "block-context": {"m.py@a0": a_move("m.py@a0", "m.py@a8")},
            "module-context": {"m.py@a8": a_correct("m.py@a8")},
        }
    )
    grouped = places(proof)
    assert "m.py@a0" in grouped and "m.py@a8" in grouped
    assert len(grouped["m.py@a8"]) == 2, "the move must reach its destination"


def test_every_mark_carries_the_role_that_made_it():
    proof = a_master_proof({"block-context": {"m.py@b1": a_correct("m.py@b1")}})
    assert places(proof)["m.py@b1"][0].role == "block-context"


def test_one_change_settles_because_nobody_composed_anything():
    proof = a_master_proof({"block-context": {"m.py@b1": a_correct("m.py@b1")}})
    out = reconcile(proof)
    assert [s["address"] for s in out.settled] == ["m.py@b1"]
    assert out.escalations == [] and out.rereads == []


def test_two_changes_on_different_sentences_are_RE_READ_not_merged():
    """! THE TWO TEXTS DIFFER HERE, since `Process: #88`. `a_correct` writes one
    fixed `change` for every mark, and two marks carrying one text agree
    whatever sentence each quoted -- so the case this asks about, different
    sentences and different texts, has to say so."""
    first = a_correct("m.py@b1", sentence=0)
    first["change"] = "# the first sentence, reworded\n"
    second = a_correct("m.py@b1", sentence=2)
    second["change"] = "# the third sentence, reworded\n"
    proof = a_master_proof(
        {
            "block-context": {"m.py@b1": first},
            "module-context": {"m.py@b1": second},
        }
    )
    out = reconcile(proof)
    assert out.settled == []
    assert [r["address"] for r in out.rereads] == ["m.py@b1"]
    assert sorted(out.rereads[0]["roles"]) == ["block-context", "module-context"]


def test_two_changes_on_the_SAME_sentence_escalate():
    proof = a_master_proof(
        {
            "block-context": {"m.py@b1": a_correct("m.py@b1", sentence=0)},
            "module-context": {"m.py@b1": a_correct("m.py@b1", sentence=0)},
        }
    )
    out = reconcile(proof)
    assert [e["address"] for e in out.escalations] == ["m.py@b1"]


def test_clean_and_query_owe_no_change_so_they_compose_nothing():
    proof = a_master_proof(
        {
            "block-context": {"m.py@b1": a_clean("m.py@b1")},
            "module-context": {"m.py@b1": a_query("m.py@b1")},
        }
    )
    out = reconcile(proof)
    assert out.rereads == [] and out.escalations == []


def test_an_add_reaches_a_role_that_marked_nothing_there():
    # ! Two adds at two addresses never meet under per-place grouping, so a
    # duplicated comment passes every check unless the whole stage reads them.
    proof = a_master_proof(
        {
            "block-context": {"m.py@b1": an_add("m.py@b1")},
            "module-context": {"m.py@b9": a_clean("m.py@b9")},
        }
    )
    out = reconcile(proof)
    reread = [r for r in out.rereads if r["address"] == "m.py@b1"][0]
    # !! THE EXACT SET, NOT `in`. An inclusion assertion cannot fail against
    # over-inclusion, which is the direction the narrowing below can break in.
    assert reread["roles"] == ["block-context", "module-context"]


def test_an_add_does_not_reach_a_role_that_never_saw_this_page():
    """`Process: #49`'s NARROWING: *"all roles of the stage, and for a
    partitioned role only the shard holding that file."* A role whose
    `edit_copy` covers another page is another shard, and cross-file
    duplication is not chased -- it would cost the fan-out's whole benefit on
    any page carrying an `add`."""
    proof = a_master_proof(
        {
            "block-context": {"m.py@b1": an_add("m.py@b1")},
            "module-context": {"other.py@b1": a_clean("other.py@b1")},
        }
    )
    out = reconcile(proof)
    reread = [r for r in out.rereads if r["address"] == "m.py@b1"][0]
    assert reread["roles"] == ["block-context"]


def test_two_moves_into_one_place_quote_no_sentence_so_they_are_RE_READ():
    """`docs/the-mark.md`'s classifier table gives both `add` and `move` `--`
    in the VERBATIM column: neither quotes an existing sentence, so two of them
    at one place can never be found to have named the SAME sentence -- which is
    the re-read row of `Process: #49`'s table, not the escalation row."""
    proof = a_master_proof(
        {
            "block-context": {"m.py@a0": a_move("m.py@a0", "m.py@a8")},
            "module-context": {"m.py@a16": a_move("m.py@a16", "m.py@a8")},
        }
    )
    out = reconcile(proof)
    assert out.escalations == []
    assert "m.py@a8" in [r["address"] for r in out.rereads]


def test_a_move_whose_destination_is_marked_again_settles_at_NEITHER_end():
    """`docs/the-mark.md`: *"a `move` escalated at EITHER place escalates
    WHOLE. It may not be settled at one end and escalated at the other."*
    Settled alone, the origin is a delete the destination never receives."""
    proof = a_master_proof(
        {
            "block-context": {"m.py@a0": a_move("m.py@a0", "m.py@a8")},
            "module-context": {"m.py@a8": a_correct("m.py@a8", "a different sentence")},
        }
    )
    out = reconcile(proof)
    assert out.settled == []
    assert sorted(r["address"] for r in out.rereads) == ["m.py@a0", "m.py@a8"]


def test_a_move_whose_ORIGIN_is_marked_again_settles_at_NEITHER_end():
    """The same rule from the other side. Settled alone, the destination is
    written and the origin never emptied, so the paragraph reads twice."""
    proof = a_master_proof(
        {
            "block-context": {"m.py@a0": a_move("m.py@a0", "m.py@a8")},
            "module-context": {"m.py@a0": a_correct("m.py@a0", "a different sentence")},
        }
    )
    out = reconcile(proof)
    assert out.settled == []
    assert sorted(r["address"] for r in out.rereads) == ["m.py@a0", "m.py@a8"]


def test_a_move_alone_still_settles_at_both_of_its_ends():
    """! THE OTHER HALF OF THE RULE. Joining the two ends must not hold back a
    `move` nobody else marked -- both places settle, and the docket sets the
    pair together."""
    proof = a_master_proof(
        {
            "block-context": {"m.py@a0": a_move("m.py@a0", "m.py@a8")},
        }
    )
    out = reconcile(proof)
    assert sorted(s["address"] for s in out.settled) == ["m.py@a0", "m.py@a8"]
    assert out.escalations == [] and out.rereads == []


def test_a_scope_declaring_query_does_not_block_the_other_roles():
    proof = a_master_proof(
        {
            "block-context": {"m.py@b1": a_clean("m.py@b1")},
            "function-context": {"m.py@b1": a_clean("m.py@b1")},
            "module-context": {"m.py@b1": a_clean("m.py@b1")},
            "ownership-context": {
                "m.py@b1": a_query("m.py@b1", shape=Shape.OUTSIDE_MY_ROLE)
            },
        }
    )
    out = reconcile(proof)
    assert out.escalations == []


#: !! THREE `UnnamedRole` CASES WERE DELETED HERE BY `P42`, and the deletion is
#: the point rather than a gap. They each built a real proof and then did `del
#: proof["edit_copies"][i]["role"]` -- reaching INTO the document to make a
#: shape the parse would have refused. `places` and `reconcile` now take a
#: `MasterProof`, whose every `EditCopy` carried a `role` before it could be
#: constructed, so there is no value left to hand in and `UnnamedRole` is gone
#: with them. The refusal itself did not move house: it is
#: `tests/test_containers.py::TestAnEditCopyThatIsNotOne::
#: test_an_edit_copy_with_no_role`, one boundary earlier.
#: ! WHAT THEY MEASURED IS ON THE RECORD and is not being re-asserted here: a
#: `sorted()` over two role names aborted the stage with a bare `TypeError`
#: naming `str` and `NoneType`, and a SINGLE unnamed role passed silently
#: carrying `None` to every later reader.


def test_a_promoted_entry_names_the_role_and_mark_that_forced_it():
    """`m.py@a0`'s move, ruled by `block-context` alone, would SETTLE on its
    own -- `test_a_move_alone_still_settles_at_both_of_its_ends` covers that.
    Here `module-context` also rules a `correct` at the destination, `a8`,
    which pulls BOTH ends to `rereads` (`test_a_move_whose_destination_is_
    marked_again_settles_at_NEITHER_end` covers the address list). This test
    is the entry CONTENT at the weaker end: before the 2026-08-30 fix, `a0`'s
    `roles`/`marks` named only `block-context`, with no trace of the
    `module-context` `correct` that is the actual reason `a0` could not
    settle.
    """
    proof = a_master_proof(
        {
            "block-context": {"m.py@a0": a_move("m.py@a0", "m.py@a8")},
            "module-context": {"m.py@a8": a_correct("m.py@a8", "a different sentence")},
        }
    )
    out = reconcile(proof)
    origin = next(r for r in out.rereads if r["address"] == "m.py@a0")
    assert origin["roles"] == ["block-context", "module-context"]
    assert {p.role for p in origin["marks"]} == {"block-context", "module-context"}


def test_undetermined_settles_where_another_role_ruled_substantively():
    proof = a_master_proof(
        {
            "block-context": {
                "m.py@b1": a_query("m.py@b1", shape=Shape.UNABLE_TO_DETERMINE)
            },
            "module-context": {"m.py@b1": a_correct("m.py@b1")},
        }
    )
    out = reconcile(proof)
    assert [s["address"] for s in out.settled] == ["m.py@b1"]
    assert out.escalations == []
