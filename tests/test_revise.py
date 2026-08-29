"""Pulling a revise: a copy of the tree with one stage's corrections set.

`TODO/the-flow-assumes-every-role-reads-at-once.md` T3, delivered by task 8 of
`.superpowers/sdd/2026-08-28-the-mark-and-the-revise/task-8-brief.md`.
"""

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
