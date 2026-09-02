"""Pulling a revise: a copy of the tree with one stage's corrections set.

`TODO/the-flow-assumes-every-role-reads-at-once.md` T3, delivered by task 8 of
`.superpowers/sdd/2026-08-28-the-mark-and-the-revise/task-8-brief.md`.
"""

import shutil
import stat

import pytest
from helpers import (
    a_binder_over,
    a_correct,
    a_docket_over,
    a_docket_whose_claim_is_not_in_the_page,
    a_drop,
    a_move,
    a_small_real_tree,
    copies_over,
    returned,
)

from comment_review.desk.containers import EditCopy
from comment_review.flows.revise import _set_by, docket_of, pull


def a_copy(role: str, paragraphs: dict[str, str], marks: dict) -> EditCopy:
    """One returned `edit_copy`, seeded from a real binder and PARSED.

    ! THROUGH `seed` AND `EditCopy.deserialize`, never hand-built -- `copies_over`
    seeds from the binder the way `distribute` does, and `returned` runs the
    result through the container boundary. A dict shaped the way this test
    expects would agree with the test whatever the code did.
    """
    binder = a_binder_over(paragraphs)
    return returned(copies_over(binder, {role: marks})[0])


class TestDocketOf:
    """`edit_copy -> Docket`, the proof flow's first step.

    !! IT TAKES ANY COPY, NOT ONLY THE COPY CHIEF'S. Roy, 2026-09-02: *"it could
    also be ownership contexts edit-copy or any intermediate edit-copy which
    allows the stage outputs to run."* That is what lets a stage's own output
    become a revise, which `reads = "revise:N"` and `4b` both need.
    `decision-log.md Process: #76`.
    """

    def test_one_move_mark_yields_two_alterations(self):
        """!! ONE `Mark` HOLDS BOTH ENDS. `claim_all` for a move is
        `("from", "to")`, so the origin and the destination are derivable from
        the single entry a copy carries -- the delete at `address`, the text at
        `claim.to`. Nothing here needs the copy to carry a move twice."""
        copy = a_copy(
            "block-context",
            {"m.py@b1": "# a paragraph\n", "m.py@b8": "# elsewhere\n"},
            {"m.py@b1": a_move("m.py@b1", "m.py@b8")},
        )
        schedule = docket_of(copy).schedules[0]
        assert [(one.cue, one.text) for one in schedule.alterations] == [
            ("b1", None),
            ("b8", "# set by the reconcile test suite (move)"),
        ]

    def test_the_schedule_carries_the_copys_own_role(self):
        """! THE COPY'S ROLE, NOT A PER-PLACE ONE. An ordinary role's copy names
        that role; the fold's names `copy-chief`. Either is what set the page."""
        copy = a_copy(
            "ownership-context",
            {"m.py@b1": "# a paragraph\n"},
            {"m.py@b1": a_correct("m.py@b1", sentence="a paragraph")},
        )
        assert docket_of(copy).schedules[0].role == "ownership-context"

    def test_a_sheet_becomes_a_schedule_with_its_own_path_and_sha(self):
        copy = a_copy(
            "block-context",
            {"m.py@b1": "# one\n", "n.py@b1": "# two\n"},
            {"m.py@b1": a_correct("m.py@b1", sentence="one")},
        )
        docket = docket_of(copy)
        assert [one.path for one in docket.schedules] == ["m.py"]
        assert docket.schedules[0].sha == "0" * 40

    def test_an_ordinary_mark_yields_one_alteration_at_its_own_address(self):
        copy = a_copy(
            "block-context",
            {"m.py@b1": "# one\n"},
            {"m.py@b1": a_correct("m.py@b1", sentence="one")},
        )
        schedule = docket_of(copy).schedules[0]
        assert [(one.cue, one.text) for one in schedule.alterations] == [
            ("b1", "# set by the reconcile test suite (correct)")
        ]

    def test_a_drop_is_written_as_a_delete(self):
        """! `drop` IS THE ROW WHOSE `may_empty` IS TRUE, and `text_at` turns an
        empty change into None -- which is what the write end reads as a
        delete."""
        copy = a_copy(
            "block-context",
            {"m.py@b1": "# one\n"},
            {"m.py@b1": {**a_drop("m.py@b1", "one"), "change": ""}},
        )
        schedule = docket_of(copy).schedules[0]
        assert [(one.cue, one.text) for one in schedule.alterations] == [("b1", None)]

    def test_set_by_names_the_role_whose_copy_was_pulled(self):
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
        copy = a_copy(
            "module-context",
            {"m.py@b1": "# one\n"},
            {"m.py@b1": a_correct("m.py@b1", sentence="one")},
        )
        assert set(_set_by(docket_of(copy)).values()) == {"module-context"}

    def test_a_page_nobody_ruled_on_gets_no_schedule(self):
        """!! AN UNTOUCHED SLOT IS NOT AN ALTERATION. A seeded copy carries a
        slot for every place; only the ones a role filled become edits, and a
        page whose slots are all untouched must not reach the docket as an empty
        schedule the write end would then set nothing from."""
        copy = a_copy("block-context", {"m.py@b1": "# one\n"}, {})
        assert docket_of(copy).schedules == ()


def test_the_revise_holds_every_library_file_and_only_the_scheduled_ones_differ(
    tmp_path,
):
    repo = a_small_real_tree(tmp_path)  # INPUT FROM REALITY, not a fixture literal
    pulled = pull(a_docket_over(repo, ["mark.py"]), repo, tmp_path / "r1", revise=1)
    assert {p.name for p in pulled.root.rglob("*.py")} == {
        p.name for p in repo.rglob("*.py")
    }
    changed = [
        p
        for p in pulled.root.rglob("*.py")
        if p.read_bytes() != (repo / p.relative_to(pulled.root)).read_bytes()
    ]
    assert [p.name for p in changed] == ["mark.py"]


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


def test_a_refusal_leaves_no_revise(tmp_path):
    repo = a_small_real_tree(tmp_path)
    docket = a_docket_whose_claim_is_not_in_the_page(repo, "mark.py")
    pulled = pull(docket, repo, tmp_path / "r1", revise=1)
    assert pulled.refusals and not pulled.root.exists()


def test_a_refusal_leaves_no_revise_when_the_copy_holds_a_read_only_file(tmp_path):
    """!! `Pulled.refusals` SAYS *"root was discarded and does not exist"*, and
    a checkout carries files the platform refuses to unlink: git writes loose
    objects and packs under `.git/objects` read-only, and `shutil.copytree`
    reproduces the mode. `pull` copies the tree WHOLE, so `.git` comes with it.

    ! THE PRECONDITION IS ASSERTED, NOT ASSUMED -- the same probe
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
