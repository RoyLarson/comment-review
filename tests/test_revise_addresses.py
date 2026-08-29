"""The address-invariance gate: a revise re-censused yields the same address
set the original did, or the pull is refused with `AddressesMoved` naming what
changed.

`TODO/the-flow-assumes-every-role-reads-at-once.md` T4, delivered by task 9 of
`.superpowers/sdd/2026-08-28-the-mark-and-the-revise/task-9-brief.md`.
`docs/decision-log.md Process: #35` is the safety argument this gates.
"""

import pytest
from helpers import a_docket_over, a_small_real_tree, binder_of

from comment_review.binder.binder import rows_of
from comment_review.flows.revise import AddressesMoved, assert_addresses_held, pull


def test_a_revise_yields_the_address_set_the_original_yielded(tmp_path):
    repo = a_small_real_tree(tmp_path)
    before = {r["address"] for r in rows_of(binder_of(repo, 0))}
    pulled = pull(a_docket_over(repo, ["mark.py"]), repo, tmp_path / "r1", revise=1)
    after = {r["address"] for r in rows_of(binder_of(pulled.root, 1))}
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
