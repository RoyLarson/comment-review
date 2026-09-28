"""Pulling a revise: the docket's pages, with one stage's corrections set.

`TODO/the-flow-assumes-every-role-reads-at-once.md` T3, delivered by task 8 of
`.superpowers/sdd/2026-08-28-the-mark-and-the-revise/task-8-brief.md`.
"""

import json
import shutil
import stat
from pathlib import Path

import pytest
from helpers import (
    BASE,
    BOTH_FIXED,
    FIRST_FIXED,
    TWO,
    TYPOS,
    VALIDATORS,
    a_clean,
    a_correct,
    a_correct_setting,
    a_docket_over,
    a_docket_whose_claim_is_not_in_the_page,
    a_drop,
    a_move,
    a_patch,
    a_query,
    a_real_binder_over,
    a_small_real_tree,
    answer,
    copies_over,
    deal,
    disposition,
    entries_of,
    patched,
    proof_at,
    returned,
    turn,
)

from comment_review.commands import collate as collate_command
from comment_review.desk.proof.edit_copy import EditCopy
from comment_review.desk.proof.mark import Shape
from comment_review.desk.proof.master_proof import MasterProof
from comment_review.flows import proof_setter
from comment_review.flows.page_for import page_of
from comment_review.flows.proof_io import load_proof
from comment_review.flows.revise import AddressesMoved, _set_by, pull
from comment_review.flows.transcribe import (
    CannotTranscribe,
    docket_of,
    docket_of_proof,
)


def a_copy(root: Path, role: str, paragraphs: dict[str, str], marks: dict) -> EditCopy:
    """One returned `edit_copy`, seeded from a real binder over real pages.

    ! THROUGH `seed` AND `EditCopy.deserialize`, never hand-built -- `copies_over`
    seeds from the binder the way `distribute` does, and `returned` runs the
    result through the container boundary. A dict shaped the way this test
    expects would agree with the test whatever the code did.

    The pages are on disk, and they did not have to be until `docket_of`
    folded. The fold measures every mark against the page at its place, so a
    copy whose pages are not in `root` decides nothing there.
    """
    binder = a_real_binder_over(root, paragraphs)
    return returned(copies_over(binder, {role: marks})[0])


def every_other_file_fails_to_gather(monkeypatch, names: set[str]) -> None:
    """Make the gate's reader raise on every file whose name is not in `names`.

    The gate reads pages through `comment_review.flows.revise.page_of`, and
    only that name is replaced, so `proof_setter.run` still reads and drafts
    through its own import.
    """

    def reads_only_the_named(path, *args, **kwargs):
        if Path(path).name not in names:
            raise OSError(f"{path} cannot be gathered (simulated)")
        return page_of(path, *args, **kwargs)

    monkeypatch.setattr("comment_review.flows.revise.page_of", reads_only_the_named)


class TestDocketOf:
    """`edit_copy -> the fold -> Docket`, the proof flow's first step.

    !! IT TAKES ANY COPY, NOT ONLY THE COPY CHIEF'S. Roy, 2026-09-02: *"it could
    also be ownership contexts edit-copy or any intermediate edit-copy which
    allows the stage outputs to run."* That is what lets a stage's own output
    become a revise, which `reads = "revise:N"` and `4b` both need.
    `decision-log.md Process: #76`.
    """

    def test_a_partial_move_leaves_the_remainder_and_lands_the_destination(
        self, tmp_path
    ):
        """`decision-log.md Process: #172` and `#175`: the snippet is
        subtracted from the origin's paragraph, and what is left stands there;
        the destination lands the paragraph the mark says it will read with."""
        root = tmp_path / "repo"
        copy = a_copy(
            root,
            "block-context",
            {"m.py@b1": "# one\n# two\n"},
            {"m.py@b1": a_move("m.py@b1", "m.py@b0", change="# two", reads="# two")},
        )
        schedule = docket_of(copy, root).schedules[0]
        assert [(one.cue, one.text) for one in schedule.alterations] == [
            ("b0", "# two"),
            ("b1", "# one\n"),
        ]

    def test_a_whole_move_empties_its_origin(self, tmp_path):
        """The snippet is the whole paragraph, so nothing is left at the
        origin and the alteration there is the `None` the write end reads as a
        delete."""
        root = tmp_path / "repo"
        copy = a_copy(
            root,
            "block-context",
            {"m.py@b1": "# a paragraph\n"},
            {
                "m.py@b1": a_move(
                    "m.py@b1", "m.py@b0", change="# a paragraph", reads="# a paragraph"
                )
            },
        )
        schedule = docket_of(copy, root).schedules[0]
        assert [(one.cue, one.text) for one in schedule.alterations] == [
            ("b0", "# a paragraph"),
            ("b1", None),
        ]

    def test_a_move_whose_destination_cannot_settle_writes_neither_end(self, tmp_path):
        """A move's two ends are one decision, so the fold holds the move
        whole when its destination cannot settle. Folded as two unrelated
        places, the origin settled as a removal and the destination as
        nothing, and the docket deleted the snippet without landing it."""
        root = tmp_path / "repo"
        copy = a_copy(
            root,
            "block-context",
            {"m.py@b1": "# a paragraph\n", "m.py@b2": "# another\n"},
            {
                "m.py@b1": a_move(
                    "m.py@b1",
                    "m.py@b2",
                    change="# a paragraph",
                    reads="# a paragraph\n# another",
                ),
                "m.py@b2": a_query("m.py@b2", Shape.HUMAN_REVIEW_NECESSARY),
            },
        )
        assert docket_of(copy, root).schedules == ()

    def test_a_move_onto_a_page_this_copy_holds_no_sheet_for_is_scheduled(
        self, tmp_path
    ):
        """The chief's copy files a move under its origin's page, so the
        destination's page can be one the copy never carried. `docket_of`
        reads that page out of the checkout and schedules it, taking the sha
        it read there -- the copy holds none for it."""
        root = tmp_path / "repo"
        copy = a_copy(
            root,
            "block-context",
            {"m.py@b1": "# a paragraph\n"},
            {
                "m.py@b1": a_move(
                    "m.py@b1", "n.py@b0", change="# a paragraph", reads="# a paragraph"
                )
            },
        )
        (root / "n.py").write_text("v0 = 0\nv1 = 1\n", encoding="utf-8", newline="\n")
        page, why = page_of(root / "n.py", rel="n.py")
        assert page is not None, why
        docket = docket_of(copy, root)
        assert [one.path for one in docket.schedules] == ["m.py", "n.py"]
        landed = docket.schedules[1]
        assert landed.sha == page.sha
        assert [(one.cue, one.text) for one in landed.alterations] == [
            ("b0", "# a paragraph")
        ]

    def test_a_copy_the_fold_sends_back_is_a_refusal_naming_its_reasons(self, tmp_path):
        """A rolled-back fold decides nothing, so there is no docket to build
        and the events are the report."""
        root = tmp_path / "repo"
        copy = a_copy(
            root,
            "block-context",
            {"m.py@b1": "# a paragraph\n"},
            {"m.py@b1": a_move("m.py@b1", "m.py@b0", change="# not in the paragraph")},
        )
        with pytest.raises(CannotTranscribe) as raised:
            docket_of(copy, root)
        assert any(
            "the snippet is not in the origin" in one for one in raised.value.reasons
        )

    def test_a_mark_the_envelope_refused_stops_the_docket(self, tmp_path):
        """A mark that would not read is on no sheet the fold walks, so
        transcribing the rest would drop that place from the docket without a
        word -- which is how a landing goes missing from a run that reports
        nothing wrong. Measured on the chief's own copy, whose synthesized add
        at an empty place carried an anchor the parse refuses."""
        root = tmp_path / "repo"
        copy = a_copy(
            root,
            "block-context",
            {"m.py@b1": "# a paragraph\n", "m.py@b2": "# another\n"},
            {
                "m.py@b1": a_correct_setting("m.py@b1", "a paragraph", "# corrected"),
                "m.py@b2": a_clean("m.py@b2"),
            },
        )
        wire = copy.serialize()
        for sheet in wire["sheets"]:
            for mark in sheet["marks"]:
                if mark["address"] == "m.py@b2":
                    mark["instruction"] = "add"
                    mark["claim"] = {"missing": "a note", "anchor": "no backticks"}
        with pytest.raises(CannotTranscribe) as raised:
            docket_of(returned(wire, "chief"), root)
        assert any("m.py@b2" in one for one in raised.value.reasons)
        assert any("anchor" in one for one in raised.value.reasons)

    def _a_correction_and_a_move_into_it(self, root, reads: str):
        """One role correcting `m.py@b1` and moving `m.py@b2`'s comment into it.

        `decision-log.md Process: #179`: the two are one role's marks at one
        place, so they compose or are refused together. `reads` is the
        destination paragraph the move says `b1` will have, which decides
        which.
        """
        return a_copy(
            root,
            "block-context",
            {"m.py@b1": "# one\n# two\n", "m.py@b2": "# five\n"},
            {
                "m.py@b1": a_correct_setting("m.py@b1", "two", "# one\n# 2"),
                "m.py@b2": a_move("m.py@b2", "m.py@b1", change="# five", reads=reads),
            },
        )

    def test_two_of_one_roles_marks_on_different_sentences_compose(self, tmp_path):
        """The move lands above the paragraph and the correction rewrites its
        last line, so the place takes one text holding both and the origin is
        emptied. Neither mark is lost, which is what a docket holding one
        alteration per place used to cost."""
        root = tmp_path / "repo"
        copy = self._a_correction_and_a_move_into_it(root, "# five\n# one\n# two")
        schedule = docket_of(copy, root).schedules[0]
        assert [(one.cue, one.text) for one in schedule.alterations] == [
            ("b1", "# five\n# one\n# 2"),
            ("b2", None),
        ]

    def test_a_move_landing_below_the_line_a_correction_rewrites_composes(
        self, tmp_path
    ):
        """`mark-defects` T28: the move's comment arrives on a line of its own
        after the paragraph's last line, which the correction rewrites. An
        insert at the edge of a rewrite has one order, so the place takes both."""
        root = tmp_path / "repo"
        copy = self._a_correction_and_a_move_into_it(root, "# one\n# two\n# five")
        schedule = docket_of(copy, root).schedules[0]
        assert [(one.cue, one.text) for one in schedule.alterations] == [
            ("b1", "# one\n# 2\n# five"),
            ("b2", None),
        ]

    def test_two_of_one_roles_marks_on_one_sentence_are_a_refusal(self, tmp_path):
        """The move's comment is run onto the paragraph's last line instead,
        which rewrites the line the correction rewrites. Two marks, one
        sentence, and the role is told which two."""
        root = tmp_path / "repo"
        copy = self._a_correction_and_a_move_into_it(root, "# one\n# two # five")
        with pytest.raises(CannotTranscribe) as raised:
            docket_of(copy, root)
        # The move has one mover, so it is agreed and split before the place
        # is decided; its add collides with the correction at b1, and the
        # reason names the move the role filed, not the add it never wrote.
        (why,) = raised.value.reasons
        assert why.startswith("block-context m.py@b1: ")
        assert "its correct at m.py@b1" in why
        assert "its move at m.py@b2" in why

    def test_a_page_this_checkout_cannot_read_is_a_refusal(self, tmp_path):
        """A page a mark writes at that the checkout has no page for would
        decide nothing and get no schedule, so the copy would draft as though
        those rulings were never made. It is named instead."""
        root = tmp_path / "repo"
        copy = a_copy(
            root,
            "block-context",
            {"m.py@b1": "# one\n"},
            {"m.py@b1": a_correct("m.py@b1", sentence="one")},
        )
        (root / "m.py").unlink()
        with pytest.raises(CannotTranscribe) as raised:
            docket_of(copy, root)
        (why,) = raised.value.reasons
        assert why.startswith("block-context m.py: ")
        assert "m.py@b1" in why

    def test_a_page_the_copy_files_no_mark_on_is_not_missed(self, tmp_path):
        """Only a page a mark writes at is owed. A sheet nobody ruled on has
        nothing to set, so the checkout need not answer for it."""
        root = tmp_path / "repo"
        copy = a_copy(
            root,
            "block-context",
            {"m.py@b1": "# one\n", "n.py@b1": "# two\n"},
            {"m.py@b1": a_correct("m.py@b1", sentence="one")},
        )
        (root / "n.py").unlink()
        assert [one.path for one in docket_of(copy, root).schedules] == ["m.py"]

    def test_a_moves_destination_carries_the_pages_anchor_there(self, tmp_path):
        """`decision-log.md Process: #135`, as amended: every alteration carries
        an anchor. At a mark's own address it is the mark's; at a move's
        destination the flow takes the page's anchor at that address. The
        destination here is an empty gap, so no slot on the copy holds it."""
        root = tmp_path / "repo"
        binder = a_real_binder_over(root, {"m.py@b1": "# a paragraph\n"})
        move = a_move(
            "m.py@b1", "m.py@b0", change="# a paragraph", reads="# a paragraph"
        )
        copy = returned(copies_over(binder, {"block-context": {"m.py@b1": move}})[0])
        (mark,) = entries_of(copy)
        page, why = page_of(root / "m.py", rel="m.py")
        assert page is not None, why
        schedule = docket_of(copy, root).schedules[0]
        assert [(one.cue, one.anchor) for one in schedule.alterations] == [
            ("b0", page.cues.places["b0"]),
            ("b1", mark.anchor),
        ]

    def test_the_schedule_carries_the_copys_own_role(self, tmp_path):
        """! THE COPY'S ROLE, NOT A PER-PLACE ONE. An ordinary role's copy names
        that role; the fold's names `copy-chief`. Either is what set the page."""
        root = tmp_path / "repo"
        copy = a_copy(
            root,
            "ownership-context",
            {"m.py@b1": "# a paragraph\n"},
            {"m.py@b1": a_correct("m.py@b1", sentence="a paragraph")},
        )
        assert docket_of(copy, root).schedules[0].role == "ownership-context"

    def test_a_sheet_becomes_a_schedule_with_its_own_path_and_sha(self, tmp_path):
        root = tmp_path / "repo"
        copy = a_copy(
            root,
            "block-context",
            {"m.py@b1": "# one\n", "n.py@b1": "# two\n"},
            {"m.py@b1": a_correct("m.py@b1", sentence="one")},
        )
        docket = docket_of(copy, root)
        assert [one.path for one in docket.schedules] == ["m.py"]
        assert docket.schedules[0].sha == copy.sheets[0].sha

    def test_an_ordinary_mark_yields_one_alteration_at_its_own_address(self, tmp_path):
        root = tmp_path / "repo"
        copy = a_copy(
            root,
            "block-context",
            {"m.py@b1": "# one\n"},
            {"m.py@b1": a_correct("m.py@b1", sentence="one")},
        )
        schedule = docket_of(copy, root).schedules[0]
        assert [(one.cue, one.text) for one in schedule.alterations] == [
            ("b1", "# set by the mark helpers (correct)")
        ]

    def test_a_drop_is_written_as_a_delete(self, tmp_path):
        """`drop` is the row whose `may_empty` is True, and an empty text at a
        decided place becomes the `None` the write end reads as a delete."""
        root = tmp_path / "repo"
        copy = a_copy(
            root,
            "block-context",
            {"m.py@b1": "# one\n"},
            {"m.py@b1": {**a_drop("m.py@b1", "one"), "change": ""}},
        )
        schedule = docket_of(copy, root).schedules[0]
        assert [(one.cue, one.text) for one in schedule.alterations] == [("b1", None)]

    def test_set_by_names_the_role_whose_copy_was_pulled(self, tmp_path):
        """!! WHICH ROLE SET A PLACE IS ANSWERED BY WHICH COPY YOU PULLED FROM.
        Roy, 2026-09-02: *"If we are pulling from the individual roles already
        then we know the answer."* `_set_by` maps every altered address to the
        schedule's role, so a role's own copy attributes every place to that
        role -- and the copy chief's attributes them to the fold, which is what
        set them.

        ! IT WAS `tests/test_docket.py::test_set_by_stops_mapping_everything_to_
        empty`, which built a `MasterProof` and went through `docket_from`. The
        subject is the same and the input is now the one production carries.
        """
        root = tmp_path / "repo"
        copy = a_copy(
            root,
            "module-context",
            {"m.py@b1": "# one\n"},
            {"m.py@b1": a_correct("m.py@b1", sentence="one")},
        )
        assert set(_set_by(docket_of(copy, root)).values()) == {"module-context"}

    def test_a_page_nobody_ruled_on_gets_no_schedule(self, tmp_path):
        """!! AN UNTOUCHED SLOT IS NOT AN ALTERATION. A seeded copy carries a
        slot for every place; only the ones a role filled become edits, and a
        page whose slots are all untouched must not reach the docket as an empty
        schedule the write end would then set nothing from."""
        root = tmp_path / "repo"
        copy = a_copy(root, "block-context", {"m.py@b1": "# one\n"}, {})
        assert docket_of(copy, root).schedules == ()

    def test_a_clean_or_query_mark_writes_no_alteration(self, tmp_path):
        """`docket-defects` T10 and `decision-log.md Process: #174`. A `clean`
        and a `query` propose no text, so the fold decides their places with
        none and neither is an edit. Transcribed as one, an empty change read
        as a delete, and `proof --copy` over a role's copy set every paragraph
        the role had certified or questioned as gone: measured 2026-09-14,
        `compositor.py` drafted from 439 lines to 219."""
        root = tmp_path / "repo"
        copy = a_copy(
            root,
            "block-context",
            {"m.py@b1": "# one\n", "m.py@b2": "# two\n", "m.py@b3": "# three\n"},
            {
                "m.py@b1": a_clean("m.py@b1"),
                "m.py@b2": a_query("m.py@b2"),
                "m.py@b3": a_correct("m.py@b3", sentence="three"),
            },
        )
        schedule = docket_of(copy, root).schedules[0]
        assert [one.cue for one in schedule.alterations] == ["b3"]

    def test_a_page_ruled_only_clean_or_query_gets_no_schedule(self, tmp_path):
        """A page whose marks propose no text has nothing for the write end to
        set, the same as a page nobody ruled on."""
        root = tmp_path / "repo"
        copy = a_copy(
            root,
            "block-context",
            {"m.py@b1": "# one\n", "m.py@b2": "# two\n"},
            {"m.py@b1": a_clean("m.py@b1"), "m.py@b2": a_query("m.py@b2")},
        )
        assert docket_of(copy, root).schedules == ()


#: The paragraph `patched` puts its two typos in, at the one place these
#: cases deal.
TYPO_TEXTS = {"m.py@b1": TYPOS}
TWO_PATCHES = patched("m.py@b1")
#: Both roles patch the same line instead, so the two will not compose and the
#: place is contested for the chief to rule.
SAME_LINE = {
    "block-context": {"m.py@b1": a_patch("m.py@b1", "teh", "the", FIRST_FIXED)},
    "function-context": {
        "m.py@b1": a_patch(
            "m.py@b1", "count", "total", "# teh total\n# of the items\n# adn the sum"
        )
    },
}
RECAST_THERE = "# the total count\n# of the items\n# and the sum\n"

#: Two paragraphs with an empty place between them: `m.py@b2` holds no prose,
#: so the binder does not carry it and no seeded copy has a slot there.
GAPPED = {"m.py@b1": "# one\n# two\n# three\n", "m.py@b3": "# four\n# five\n# six\n"}
THE_GAP = "m.py@b2"
ADDED = "# the gap wants a sentence\n"
THE_ADD = {
    "address": THE_GAP,
    "instruction": "add",
    "claim": {"missing": "why the gap is here", "anchor": "`v2`"},
    "reason": "the gap is explained nowhere",
    "sources": [{"cite": "m.py:1"}],
    "change": ADDED,
}
_CLEAN_ABOVE = {"address": "m.py@b1", "instruction": "clean", "reason": "reads true"}
_CLEAN_BELOW = {"address": "m.py@b3", "instruction": "clean", "reason": "reads true"}

#: One role moves the middle line of `m.py@b1` into `m.py@b2` and certifies
#: the destination, so every place it was handed is ruled.
MOVED = {"m.py@b1": "# one\n# two\n# three\n", "m.py@b2": "# four\n# five\n# six\n"}
REMAINDER = "# one\n# three"
MOVED_TO = "# four\n# five\n# six\n# two\n"


def the_closed_proof(tmp_path, name: str = "final.json") -> MasterProof:
    """One proof off disk, read back the way `proof --proof` reads one."""
    proof, why = load_proof(tmp_path / name)
    assert proof is not None, why
    return proof


class TestDocketOfProof:
    """The closed proof's decided places, as the docket the write chain reads.

    `decision-log.md Process: #184`: the proof holds each place's decided
    text, so the write end transcribes those places rather than folding the
    chief's marks a second time. What the chief's copy says about the same
    decisions is the readable record and is no longer an input.
    """

    def _closed(self, tmp_path, monkeypatch, capsys, by_role=None, **kwargs):
        """collate over one hand that settles at the first fold."""
        code = deal(tmp_path, monkeypatch, capsys, by_role, **kwargs)
        assert code == collate_command.OK
        return proof_at(tmp_path, 0), tmp_path / "repo"

    def test_two_patches_that_compose_reach_the_docket(
        self, tmp_path, monkeypatch, capsys
    ):
        """The decided text is a composition no filed mark sets, and every
        mark behind it is a row that owes no sources. Read from the place, the
        text reaches the docket; restated as a mark, it carried no source and
        the parse refused it."""
        assert deal(tmp_path, monkeypatch, capsys, TWO_PATCHES, TYPO_TEXTS) == (
            collate_command.REREADS
        )
        code, out = turn(
            tmp_path,
            monkeypatch,
            capsys,
            1,
            answer(
                tmp_path,
                1,
                "block-context",
                "m.py@b1",
                instruction="clean",
                reason="that reads right",
            ),
            answer(
                tmp_path,
                1,
                "function-context",
                "m.py@b1",
                instruction="clean",
                reason="that reads right",
            ),
        )
        assert code == collate_command.OK, out
        docket = docket_of_proof(proof_at(tmp_path, 1), tmp_path / "repo").docket
        (schedule,) = docket.schedules
        assert [(one.cue, one.text) for one in schedule.alterations] == [
            ("b1", BOTH_FIXED)
        ]

    def test_a_recast_over_patches_alone_reaches_the_docket(
        self, tmp_path, monkeypatch, capsys
    ):
        """The same case with the chief deciding it: the two patches will not
        compose, the chief writes its own paragraph, and nothing filed here
        brought a source for a synthesized mark to carry."""
        assert deal(tmp_path, monkeypatch, capsys, SAME_LINE, TYPO_TEXTS) == (
            collate_command.ESCALATIONS
        )
        code, out = disposition(
            tmp_path,
            monkeypatch,
            capsys,
            [
                {
                    "address": "m.py@b1",
                    "answer": "recast",
                    "reason": "neither patch carries it",
                    "prose": RECAST_THERE,
                }
            ],
            proof="proof0.json",
        )
        assert code == collate_command.OK, out
        docket = docket_of_proof(the_closed_proof(tmp_path), tmp_path / "repo").docket
        (schedule,) = docket.schedules
        assert [(one.cue, one.text) for one in schedule.alterations] == [
            ("b1", RECAST_THERE)
        ]

    def test_a_settled_correction_is_one_alteration(
        self, tmp_path, monkeypatch, capsys
    ):
        proof, repo = self._closed(
            tmp_path,
            monkeypatch,
            capsys,
            {"block-context": {"m.py@b1": a_correct_setting("m.py@b1", "two", TWO)}},
            texts={"m.py@b1": BASE},
        )
        (schedule,) = docket_of_proof(proof, repo).docket.schedules
        assert schedule.path == "m.py"
        assert [(one.cue, one.text) for one in schedule.alterations] == [("b1", TWO)]

    def test_the_schedule_carries_the_page_and_the_sha_the_run_read(
        self, tmp_path, monkeypatch, capsys
    ):
        proof, repo = self._closed(
            tmp_path,
            monkeypatch,
            capsys,
            {"block-context": {"m.py@b1": a_correct_setting("m.py@b1", "two", TWO)}},
            texts={"m.py@b1": BASE},
        )
        (sheet,) = proof.edit_copies[0].sheets
        (schedule,) = docket_of_proof(proof, repo).docket.schedules
        assert (schedule.path, schedule.sha) == (sheet.path, sheet.sha)

    def test_an_emptied_place_is_the_delete_the_write_end_reads(
        self, tmp_path, monkeypatch, capsys
    ):
        """A place the fold decided an empty text for is the `None` the write
        end reads as a delete, the same as on a role's own copy."""
        proof, repo = self._closed(
            tmp_path,
            monkeypatch,
            capsys,
            {"block-context": {"m.py@b1": {**a_drop("m.py@b1", "two"), "change": ""}}},
            texts={"m.py@b1": BASE},
        )
        (schedule,) = docket_of_proof(proof, repo).docket.schedules
        assert [(one.cue, one.text) for one in schedule.alterations] == [("b1", None)]

    def test_an_add_at_an_empty_place_lands_there(self, tmp_path, monkeypatch, capsys):
        """The place holds no prose, so the binder carries it nowhere and the
        ruling was placed from the page. Its decided text is still a place on
        the proof and still one alteration."""
        proof, repo = self._closed(
            tmp_path,
            monkeypatch,
            capsys,
            texts=GAPPED,
            placed={"block-context": [_CLEAN_ABOVE, _CLEAN_BELOW, THE_ADD]},
        )
        (schedule,) = docket_of_proof(proof, repo).docket.schedules
        assert [(one.cue, one.text) for one in schedule.alterations] == [("b2", ADDED)]

    def test_a_move_sets_each_end_from_its_own_place(
        self, tmp_path, monkeypatch, capsys
    ):
        """Two places, two decided texts, and neither is read off the other:
        the origin keeps what the snippet left and the destination takes the
        paragraph the move says it will read with."""
        proof, repo = self._closed(
            tmp_path,
            monkeypatch,
            capsys,
            {
                "block-context": {
                    "m.py@b1": a_move(
                        "m.py@b1", "m.py@b2", change="# two\n", reads=MOVED_TO
                    ),
                    "m.py@b2": a_clean("m.py@b2"),
                }
            },
            texts=MOVED,
        )
        (schedule,) = docket_of_proof(proof, repo).docket.schedules
        assert [(one.cue, one.text) for one in schedule.alterations] == [
            ("b1", REMAINDER),
            ("b2", MOVED_TO),
        ]

    def test_a_move_onto_a_page_no_copy_holds_a_sheet_for_is_scheduled(
        self, tmp_path, monkeypatch, capsys
    ):
        """The destination is on a page the stage never gathered, so no sheet
        records a sha for it. The page is read out of the checkout and the sha
        it was read at is what the schedule carries."""
        repo = tmp_path / "repo"
        repo.mkdir(parents=True, exist_ok=True)
        (repo / "n.py").write_text("v0 = 0\nv1 = 1\n", encoding="utf-8", newline="\n")
        proof, repo = self._closed(
            tmp_path,
            monkeypatch,
            capsys,
            {
                "block-context": {
                    "m.py@b1": a_move(
                        "m.py@b1",
                        "n.py@b0",
                        change="# one\n# two\n# three",
                        reads="# one\n# two\n# three",
                    )
                }
            },
            texts={"m.py@b1": BASE},
        )
        page, why = page_of(repo / "n.py", rel="n.py")
        assert page is not None, why
        docket = docket_of_proof(proof, repo).docket
        assert [one.path for one in docket.schedules] == ["m.py", "n.py"]
        landed = docket.schedules[1]
        assert landed.sha == page.sha
        assert [(one.cue, one.text, one.anchor) for one in landed.alterations] == [
            ("b0", "# one\n# two\n# three", page.cues.places["b0"])
        ]

    def test_a_place_that_stands_on_its_base_gets_no_alteration(
        self, tmp_path, monkeypatch, capsys
    ):
        """`decision-log.md Process: #174`. A place nobody proposed a text for
        and a place whose decided text is the paragraph already there are both
        nothing to set, and a page with neither gets no schedule."""
        proof, repo = self._closed(
            tmp_path,
            monkeypatch,
            capsys,
            {
                "block-context": {
                    "m.py@b1": a_clean("m.py@b1"),
                    "m.py@b2": a_correct_setting("m.py@b2", "five", "# four\n# five"),
                }
            },
            texts={"m.py@b1": BASE, "m.py@b2": "# four\n# five\n"},
        )
        assert docket_of_proof(proof, repo).docket.schedules == ()

    @pytest.mark.parametrize(
        ("by_role", "code", "state"),
        [
            (TWO_PATCHES, collate_command.REREADS, "composed"),
            (SAME_LINE, collate_command.ESCALATIONS, "contested"),
        ],
    )
    def test_a_proof_still_carrying_a_place_forward_is_a_refusal(
        self, tmp_path, monkeypatch, capsys, by_role, code, state
    ):
        """`decision-log.md Process: #180`: a carried-forward text has not
        settled, so a proof holding one is not closed and nothing on it is the
        write end's to set. The place is named."""
        assert deal(tmp_path, monkeypatch, capsys, by_role, TYPO_TEXTS) == code
        with pytest.raises(CannotTranscribe) as raised:
            docket_of_proof(proof_at(tmp_path, 0), tmp_path / "repo")
        (why,) = raised.value.reasons
        assert "m.py@b1" in why and state in why

    def test_a_place_that_will_not_read_is_a_refusal(
        self, tmp_path, monkeypatch, capsys
    ):
        """A place is parsed before it is transcribed, the way a returned
        copy's marks are. One that will not parse is named, and no page is
        set from what is left."""
        self._closed(
            tmp_path,
            monkeypatch,
            capsys,
            {"block-context": {"m.py@b1": a_correct_setting("m.py@b1", "two", TWO)}},
            texts={"m.py@b1": BASE},
        )
        wire = json.loads((tmp_path / "proof0.json").read_text(encoding="utf-8"))
        wire["places"][0]["filed"][0]["instruction"] = "not an instruction"
        proof, why = MasterProof.deserialize("hand-edited", wire, VALIDATORS)
        assert proof is None
        assert any("place 1 at m.py@b1" in one for one in why), why

    def test_a_page_this_checkout_cannot_read_is_a_refusal(
        self, tmp_path, monkeypatch, capsys
    ):
        """A decided place whose page this checkout cannot answer for would be
        dropped from the docket without a word, which is how a landing goes
        missing from a run that reports nothing wrong."""
        proof, repo = self._closed(
            tmp_path,
            monkeypatch,
            capsys,
            {"block-context": {"m.py@b1": a_correct_setting("m.py@b1", "two", TWO)}},
            texts={"m.py@b1": BASE},
        )
        (repo / "m.py").unlink()
        with pytest.raises(CannotTranscribe) as raised:
            docket_of_proof(proof, repo)
        (why,) = raised.value.reasons
        assert why.startswith("copy-chief m.py: ")
        assert "m.py@b1" in why


#: Two places one role corrects, each settling on its own text, and a third it
#: leaves standing. The filter's cases need more than one settled place: with
#: one, "these places alone" cannot be told from "every place".
TWO_CORRECTIONS = {
    "block-context": {
        "m.py@b1": a_correct_setting("m.py@b1", "two", TWO),
        "m.py@b2": a_correct_setting("m.py@b2", "five", "# four\n# FIVE\n# six"),
        "m.py@b3": a_clean("m.py@b3"),
    }
}
TWO_PLACES = {
    "m.py@b1": BASE,
    "m.py@b2": "# four\n# five\n# six\n",
    "m.py@b3": "# seven\n",
}


class TestOnlyTheApprovedPlaces:
    """`only`: the author approved some decided places and not others, so
    those places alone are transcribed -- `decision-log.md Process: #192`.

    The filter names places rather than pruning an artifact by hand: the
    proof is what the fold closed, and what the author ruled on is a set of
    addresses over it.
    """

    def _closed(self, tmp_path, monkeypatch, capsys, by_role, texts):
        code = deal(tmp_path, monkeypatch, capsys, by_role, texts)
        assert code == collate_command.OK
        return proof_at(tmp_path, 0), tmp_path / "repo"

    def test_the_named_place_alone_is_transcribed(self, tmp_path, monkeypatch, capsys):
        proof, repo = self._closed(
            tmp_path, monkeypatch, capsys, TWO_CORRECTIONS, TWO_PLACES
        )
        whole = docket_of_proof(proof, repo).docket
        assert [(one.cue, one.text) for one in whole.schedules[0].alterations] == [
            ("b1", TWO),
            ("b2", "# four\n# FIVE\n# six"),
        ]
        part = docket_of_proof(proof, repo, only=("m.py@b2",)).docket
        assert [(one.cue, one.text) for one in part.schedules[0].alterations] == [
            ("b2", "# four\n# FIVE\n# six")
        ]

    def test_an_address_the_proof_does_not_carry_is_a_refusal(
        self, tmp_path, monkeypatch, capsys
    ):
        """The author cannot approve a place the fold never decided, and a
        name the proof does not carry is more likely a typo than an approval
        -- transcribing the rest would set what was approved and say nothing
        about what was not."""
        proof, repo = self._closed(
            tmp_path, monkeypatch, capsys, TWO_CORRECTIONS, TWO_PLACES
        )
        with pytest.raises(CannotTranscribe) as raised:
            docket_of_proof(proof, repo, only=("m.py@b1", "m.py@b9"))
        (why,) = raised.value.reasons
        assert "m.py@b9" in why

    def test_a_named_place_that_sets_nothing_is_approved_and_named(
        self, tmp_path, monkeypatch, capsys
    ):
        """A place standing on the text already there is approved and has
        nothing to set, which is not a refusal: the author ruled on it, and
        the page already reads as the proof decided."""
        proof, repo = self._closed(
            tmp_path, monkeypatch, capsys, TWO_CORRECTIONS, TWO_PLACES
        )
        done = docket_of_proof(proof, repo, only=("m.py@b1", "m.py@b3"))
        assert done.sets_nothing == ("m.py@b3",)
        assert [
            (one.cue, one.text) for one in done.docket.schedules[0].alterations
        ] == [("b1", TWO)]

    def test_a_blanket_transcription_names_no_place_as_setting_nothing(
        self, tmp_path, monkeypatch, capsys
    ):
        """Without a filter nobody named a place, so a place that sets nothing
        is every clean place on the proof and reporting them would be noise."""
        proof, repo = self._closed(
            tmp_path, monkeypatch, capsys, TWO_CORRECTIONS, TWO_PLACES
        )
        assert docket_of_proof(proof, repo).sets_nothing == ()

    def test_both_ends_of_a_move_together_are_transcribed(
        self, tmp_path, monkeypatch, capsys
    ):
        """A move's two ends are approved each on its own (D8): the case
        naming both lands both, one decided text per place."""
        proof, repo = self._closed(
            tmp_path,
            monkeypatch,
            capsys,
            {
                "block-context": {
                    "m.py@b1": a_move(
                        "m.py@b1", "m.py@b2", change="# two\n", reads=MOVED_TO
                    ),
                    "m.py@b2": a_clean("m.py@b2"),
                }
            },
            MOVED,
        )
        done = docket_of_proof(proof, repo, only=("m.py@b1", "m.py@b2"))
        assert [
            (one.cue, one.text) for one in done.docket.schedules[0].alterations
        ] == [("b1", REMAINDER), ("b2", MOVED_TO)]


def test_the_revise_holds_only_the_docket_page_as_drafted(tmp_path):
    """A pull holds each page the docket schedules, as drafted, and no other file.

    The write phase copies only the files it modifies --
    `docs/decision-log.md Process: #117`. The expected bytes are
    `proof_setter.run`'s own draft of the same docket, so this test does not
    restate what a draft holds.
    """
    repo = a_small_real_tree(tmp_path)  # input from reality, not a fixture literal
    assert len(list(repo.glob("*.py"))) > 1, "one file cannot show a file left out"
    docket = a_docket_over(repo, ["mark.py"])
    pulled = pull(docket, repo, tmp_path / "r1", revise=1)
    held = sorted(
        p.relative_to(pulled.root).as_posix()
        for p in pulled.root.rglob("*")
        if p.is_file()
    )
    assert held == ["mark.py"]
    drafted, refusals = proof_setter.run(docket, repo, tmp_path / "drafts")
    assert not refusals
    assert [made.path for made in drafted] == ["mark.py"]
    assert (pulled.root / "mark.py").read_bytes() == drafted[0].draft.read_bytes()
    assert drafted[0].draft.read_bytes() != (repo / "mark.py").read_bytes()


def test_the_gate_passes_reading_only_the_docket_pages(tmp_path, monkeypatch):
    """The gate compares the docket's pages and reads no other file.

    Every file the docket does not name fails to gather here, so a gate that
    walked either tree would raise on the first of them. `pull` runs the gate
    before it returns, so a pull that returns is a gate that passed.
    """
    repo = a_small_real_tree(tmp_path)
    docket = a_docket_over(repo, ["mark.py"])
    every_other_file_fails_to_gather(monkeypatch, {"mark.py"})
    pulled = pull(docket, repo, tmp_path / "r1", revise=1)
    assert not pulled.refusals
    assert (pulled.root / "mark.py").is_file()


def test_the_gate_raises_on_a_docket_page_whose_addresses_moved(tmp_path, monkeypatch):
    """A draft whose code moved raises `AddressesMoved`, and no revise is left.

    The draft gains a function at its end after `proof_setter.run` proved it,
    so addresses appear in the revise that the original does not hold -- the
    change `Process: #35`'s gate exists to catch. Every other file fails to
    gather, so the raise comes from the docket's page alone.
    """
    repo = a_small_real_tree(tmp_path)
    docket = a_docket_over(repo, ["mark.py"])
    real_run = proof_setter.run

    def drafts_then_moves_the_code(docket, repo, into):
        drafted, refusals = real_run(docket, repo, into)
        for made in drafted:
            added = b"\n\ndef added():\n    return 1\n"
            made.draft.write_bytes(made.draft.read_bytes() + added)
        return drafted, refusals

    monkeypatch.setattr(
        "comment_review.flows.revise.proof_setter.run", drafts_then_moves_the_code
    )
    every_other_file_fails_to_gather(monkeypatch, {"mark.py"})
    into = tmp_path / "r1"
    with pytest.raises(AddressesMoved):
        pull(docket, repo, into, revise=1)
    assert not into.exists()


def test_a_failure_mid_overlay_leaves_no_partial_revise(tmp_path, monkeypatch):
    # !! WHAT THIS PINS: this module's docstring asserts that "nothing partial
    # is left on disk". Only the refusal and `AddressesMoved` paths discarded
    # the copy until 2026-08-28 -- so `shutil.copy2` failing partway through
    # the overlay (a full disk, a permission, a locked target) left `into`
    # holding SOME of the stage's corrections and not the rest, which is
    # verbatim the state the docstring says cannot exist.
    repo = a_small_real_tree(tmp_path)
    into = tmp_path / "r1"

    def explodes(src, dst, *a, **kw):
        raise OSError("disk full (simulated)")

    monkeypatch.setattr("comment_review.flows.revise.shutil.copy2", explodes)
    with pytest.raises(OSError):
        pull(a_docket_over(repo, ["mark.py"]), repo, into, revise=1)
    assert not into.exists()


def test_a_failure_mid_copy_leaves_no_partial_revise(tmp_path, monkeypatch):
    """A write of the drafts that fails part way leaves no `into`.

    The docket names two pages. The patched copy writes the first draft and
    raises on the second, so one drafted page is on disk under `into` when the
    exception leaves the copy.
    """
    repo = a_small_real_tree(tmp_path)
    into = tmp_path / "r1"
    real = shutil.copy2
    written = []

    def copies_once_then_fails(src, dst, *a, **kw):
        if written:
            raise OSError("path too long (simulated)")
        written.append(real(src, dst, *a, **kw))

    monkeypatch.setattr(
        "comment_review.flows.revise.shutil.copy2", copies_once_then_fails
    )
    with pytest.raises(OSError):
        pull(a_docket_over(repo, ["mark.py", "collator.py"]), repo, into, revise=1)
    assert written, "no draft was written, so nothing failed part way"
    assert not into.exists()


def test_a_refusal_leaves_no_revise(tmp_path):
    repo = a_small_real_tree(tmp_path)
    docket = a_docket_whose_claim_is_not_in_the_page(repo, "mark.py")
    pulled = pull(docket, repo, tmp_path / "r1", revise=1)
    assert pulled.refusals and not pulled.root.exists()


def test_a_refusal_leaves_no_revise_when_the_copy_holds_a_read_only_file(tmp_path):
    """A refused pull leaves no revise when the checkout holds a read-only file.

    `Pulled.refusals` says *"root was discarded and does not exist"*, and a
    checkout carries files the platform refuses to unlink: git writes loose
    objects and packs under `.git/objects` read-only. The revise holds only
    the docket's pages -- `docs/decision-log.md Process: #117` -- so such a
    file never reaches it.

    The precondition is asserted, not assumed -- the same probe
    `tests/test_machine.py` uses, so this says nothing about a platform where
    a read-only file unlinks freely.
    """
    probe = tmp_path / "probe"
    probe.mkdir()
    (probe / "object").write_bytes(b"contents\n")
    (probe / "object").chmod(stat.S_IREAD)
    try:
        shutil.rmtree(probe)
    except PermissionError:
        pass
    else:
        pytest.skip("this platform unlinks a read-only file; the defect cannot arise")

    repo = a_small_real_tree(tmp_path)
    unwritable = repo / "object"
    unwritable.write_bytes(b"contents\n")
    unwritable.chmod(stat.S_IREAD)

    docket = a_docket_whose_claim_is_not_in_the_page(repo, "mark.py")
    pulled = pull(docket, repo, tmp_path / "r1", revise=1)
    assert pulled.refusals and not pulled.root.exists()
