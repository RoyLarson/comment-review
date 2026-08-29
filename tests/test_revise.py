"""Pulling a revise: a copy of the tree with one stage's corrections set.

`TODO/the-flow-assumes-every-role-reads-at-once.md` T3, delivered by task 8 of
`.superpowers/sdd/2026-08-28-the-mark-and-the-revise/task-8-brief.md`.
"""

import shutil
import stat

import pytest
from helpers import (
    a_docket_over,
    a_docket_whose_claim_is_not_in_the_page,
    a_small_real_tree,
)

from comment_review.flows.revise import pull


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
