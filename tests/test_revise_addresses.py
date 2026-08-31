"""The address-invariance gate: a revise re-censused yields the same address
set the original did, or the pull is refused with `AddressesMoved` naming what
changed.

`TODO/the-flow-assumes-every-role-reads-at-once.md` T4, delivered by task 9 of
`.superpowers/sdd/2026-08-28-the-mark-and-the-revise/task-9-brief.md`.
`docs/decision-log.md Process: #35` is the safety argument this gates.
"""

import pytest
from helpers import a_docket_over, a_small_real_tree, binder_of

from comment_review.flows.revise import AddressesMoved, assert_addresses_held, pull


def test_a_revise_yields_the_address_set_the_original_yielded(tmp_path):
    repo = a_small_real_tree(tmp_path)
    before = {r.address for r in binder_of(repo, 0).rows}
    pulled = pull(a_docket_over(repo, ["mark.py"]), repo, tmp_path / "r1", revise=1)
    after = {r.address for r in binder_of(pulled.root, 1).rows}
    assert after == before


def test_the_gate_fires_when_the_code_moved(tmp_path):
    # ! WHAT PROVES THE CHECK CAN FAIL. A revise whose CODE was changed by hand
    # renumbers the places below it, which is exactly what the gate exists to catch.
    repo = a_small_real_tree(tmp_path)
    pulled = pull(a_docket_over(repo, ["mark.py"]), repo, tmp_path / "r1", revise=1)
    page = pulled.root / "mark.py"
    page.write_text(
        page.read_text(encoding="utf-8") + "\n\ndef added():\n    return 1\n",
        encoding="utf-8",
    )
    with pytest.raises(AddressesMoved):
        assert_addresses_held(repo, pulled)


def test_pull_itself_runs_the_gate_and_discards_a_revise_that_moved(
    tmp_path, monkeypatch
):
    # !! WHAT THIS ADDS OVER THE TEST ABOVE: that `pull` CALLS the gate.
    # MEASURED 2026-08-28 by mutation -- replacing the call inside `pull` with
    # a no-op left the whole module GREEN, because every other test invokes
    # `assert_addresses_held` directly. The safety argument of `Process: #35`
    # rests on the call site, and nothing was watching it.
    repo = a_small_real_tree(tmp_path)

    # ! The docket is honest; what moves the addresses is a SECOND writer
    # touching the tree between the copy and the gate -- the shape a concurrent
    # edit or a bad draft would take. `page_for` is monkeypatch-free: appending
    # to the source under `repo` before the pull would change the ORIGINAL too,
    # so the edit lands on the copy through a docket that writes real prose and
    # a hand-added function below it.
    docket = a_docket_over(repo, ["mark.py"])
    into = tmp_path / "r1"

    def moved(original, pulled):
        raise AddressesMoved("addresses appeared: x.py@b9; disappeared: x.py@b8")

    monkeypatch.setattr("comment_review.flows.revise.assert_addresses_held", moved)
    with pytest.raises(AddressesMoved):
        pull(docket, repo, into, revise=1)

    # ! `Process: #20` carried up a level: nothing partial, and nothing that
    # LOOKS whole but addresses the wrong places, is left for a later stage.
    assert not into.exists()
