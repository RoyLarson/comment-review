"""Pulling a revise: the docket's pages, with one stage's corrections set.

`TODO/the-flow-assumes-every-role-reads-at-once.md` T3, delivered by task 8 of
`.superpowers/sdd/2026-08-28-the-mark-and-the-revise/task-8-brief.md`.
"""

import shutil
import stat
from pathlib import Path

import pytest
from helpers import (
    a_binder_over,
    a_clean,
    a_correct,
    a_docket_over,
    a_docket_whose_claim_is_not_in_the_page,
    a_drop,
    a_move,
    a_query,
    a_real_binder_over,
    a_small_real_tree,
    copies_over,
    entries_of,
    returned,
)

from comment_review.desk.containers import EditCopy
from comment_review.flows import proof_setter
from comment_review.flows.page_for import page_of
from comment_review.flows.revise import AddressesMoved, _set_by, pull
from comment_review.flows.transcribe import docket_of


def a_copy(role: str, paragraphs: dict[str, str], marks: dict) -> EditCopy:
    """One returned `edit_copy`, seeded from a real binder and PARSED.

    ! THROUGH `seed` AND `EditCopy.deserialize`, never hand-built -- `copies_over`
    seeds from the binder the way `distribute` does, and `returned` runs the
    result through the container boundary. A dict shaped the way this test
    expects would agree with the test whatever the code did.
    """
    binder = a_binder_over(paragraphs)
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
    """`edit_copy -> Docket`, the proof flow's first step.

    !! IT TAKES ANY COPY, NOT ONLY THE COPY CHIEF'S. Roy, 2026-09-02: *"it could
    also be ownership contexts edit-copy or any intermediate edit-copy which
    allows the stage outputs to run."* That is what lets a stage's own output
    become a revise, which `reads = "revise:N"` and `4b` both need.
    `decision-log.md Process: #76`.
    """

    def test_one_move_mark_yields_two_alterations(self, tmp_path):
        """!! ONE `Mark` HOLDS BOTH ENDS. `claim_all` for a move is
        `("from", "to")`, so the origin and the destination are derivable from
        the single entry a copy carries -- the delete at `address`, the text at
        `claim.to`. Nothing here needs the copy to carry a move twice."""
        copy = a_copy(
            "block-context",
            {"m.py@b1": "# a paragraph\n", "m.py@b8": "# elsewhere\n"},
            {"m.py@b1": a_move("m.py@b1", "m.py@b8")},
        )
        schedule = docket_of(copy, tmp_path).schedules[0]
        assert [(one.cue, one.text) for one in schedule.alterations] == [
            ("b1", None),
            ("b8", "# set by the reconcile test suite (move)"),
        ]

    def test_a_moves_destination_carries_the_pages_anchor_there(self, tmp_path):
        """`decision-log.md Process: #135`, as amended: every alteration carries
        an anchor. At a mark's own address it is the mark's; at a move's
        destination the flow takes the page's anchor at that address. The
        destination here is an empty gap, so no slot on the copy holds it."""
        root = tmp_path / "repo"
        binder = a_real_binder_over(root, {"m.py@b1": "# a paragraph\n"})
        move = a_move("m.py@b1", "m.py@b0")
        copy = returned(copies_over(binder, {"block-context": {"m.py@b1": move}})[0])
        (mark,) = entries_of(copy)
        page, why = page_of(root / "m.py", rel="m.py")
        assert page is not None, why
        schedule = docket_of(copy, root).schedules[0]
        assert [(one.cue, one.anchor) for one in schedule.alterations] == [
            ("b1", mark.anchor),
            ("b0", page.cues.places["b0"]),
        ]

    def test_the_schedule_carries_the_copys_own_role(self, tmp_path):
        """! THE COPY'S ROLE, NOT A PER-PLACE ONE. An ordinary role's copy names
        that role; the fold's names `copy-chief`. Either is what set the page."""
        copy = a_copy(
            "ownership-context",
            {"m.py@b1": "# a paragraph\n"},
            {"m.py@b1": a_correct("m.py@b1", sentence="a paragraph")},
        )
        assert docket_of(copy, tmp_path).schedules[0].role == "ownership-context"

    def test_a_sheet_becomes_a_schedule_with_its_own_path_and_sha(self, tmp_path):
        copy = a_copy(
            "block-context",
            {"m.py@b1": "# one\n", "n.py@b1": "# two\n"},
            {"m.py@b1": a_correct("m.py@b1", sentence="one")},
        )
        docket = docket_of(copy, tmp_path)
        assert [one.path for one in docket.schedules] == ["m.py"]
        assert docket.schedules[0].sha == "0" * 40

    def test_an_ordinary_mark_yields_one_alteration_at_its_own_address(self, tmp_path):
        copy = a_copy(
            "block-context",
            {"m.py@b1": "# one\n"},
            {"m.py@b1": a_correct("m.py@b1", sentence="one")},
        )
        schedule = docket_of(copy, tmp_path).schedules[0]
        assert [(one.cue, one.text) for one in schedule.alterations] == [
            ("b1", "# set by the reconcile test suite (correct)")
        ]

    def test_a_drop_is_written_as_a_delete(self, tmp_path):
        """! `drop` IS THE ROW WHOSE `may_empty` IS TRUE, and `text_at` turns an
        empty change into None -- which is what the write end reads as a
        delete."""
        copy = a_copy(
            "block-context",
            {"m.py@b1": "# one\n"},
            {"m.py@b1": {**a_drop("m.py@b1", "one"), "change": ""}},
        )
        schedule = docket_of(copy, tmp_path).schedules[0]
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
        copy = a_copy(
            "module-context",
            {"m.py@b1": "# one\n"},
            {"m.py@b1": a_correct("m.py@b1", sentence="one")},
        )
        assert set(_set_by(docket_of(copy, tmp_path)).values()) == {"module-context"}

    def test_a_page_nobody_ruled_on_gets_no_schedule(self, tmp_path):
        """!! AN UNTOUCHED SLOT IS NOT AN ALTERATION. A seeded copy carries a
        slot for every place; only the ones a role filled become edits, and a
        page whose slots are all untouched must not reach the docket as an empty
        schedule the write end would then set nothing from."""
        copy = a_copy("block-context", {"m.py@b1": "# one\n"}, {})
        assert docket_of(copy, tmp_path).schedules == ()

    def test_a_clean_or_query_mark_writes_no_alteration(self, tmp_path):
        """`docket-defects` T10. `clean` and `query` owe no change -- they
        propose no text -- so neither is an edit. Transcribed as one, `text_at`
        read the empty change as a delete, and `proof --copy` over a role's copy
        set every paragraph the role had certified or questioned as gone:
        measured 2026-09-14, `compositor.py` drafted from 439 lines to 219."""
        copy = a_copy(
            "block-context",
            {"m.py@b1": "# one\n", "m.py@b2": "# two\n", "m.py@b3": "# three\n"},
            {
                "m.py@b1": a_clean("m.py@b1"),
                "m.py@b2": a_query("m.py@b2"),
                "m.py@b3": a_correct("m.py@b3", sentence="three"),
            },
        )
        schedule = docket_of(copy, tmp_path).schedules[0]
        assert [one.cue for one in schedule.alterations] == ["b3"]

    def test_a_page_ruled_only_clean_or_query_gets_no_schedule(self, tmp_path):
        """A page whose marks propose no text has nothing for the write end to
        set, the same as a page nobody ruled on."""
        copy = a_copy(
            "block-context",
            {"m.py@b1": "# one\n", "m.py@b2": "# two\n"},
            {"m.py@b1": a_clean("m.py@b1"), "m.py@b2": a_query("m.py@b2")},
        )
        assert docket_of(copy, tmp_path).schedules == ()


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
