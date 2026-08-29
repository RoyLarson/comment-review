"""Only one mechanism builds a draft tree: `flows/revise.py`'s `pull`.

`.superpowers/sdd/2026-08-28-the-mark-and-the-revise/task-12-brief.md`, delivering
`TODO/the-flow-assumes-every-role-reads-at-once.md` T7 and
`docs/plans/0.2.4-the-mark-and-the-collator.md` T2.7.

!! `commands/proof.py` CALLED `proof_setter.run` DIRECTLY UNTIL THIS TASK, beside
`flows/revise.py`'s own call -- two mechanisms assembling a draft tree, when
stage 7a must read ONE artifact: the final revise. This module pins that there
is exactly one caller left.
"""

from conftest import ROOT as REPO


def test_only_one_path_builds_a_draft_tree():
    # EXPECTATION FROM docs/plans/0.2.4-the-mark-and-the-collator.md, T2.7:
    # one mechanism builds a draft tree, and it is the revise pull.
    callers = [
        p
        for p in (REPO / "src").rglob("*.py")
        if "proof_setter.run(" in p.read_text(encoding="utf-8")
    ]
    assert [p.name for p in callers] == ["revise.py"]
