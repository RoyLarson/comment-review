"""Only one mechanism builds a draft tree: `flows/revise.py`'s `pull`.

`.superpowers/sdd/2026-08-28-the-mark-and-the-revise/task-12-brief.md`, delivering
`TODO/the-flow-assumes-every-role-reads-at-once.md` T7 and
`docs/plans/0.2.4-the-mark-and-the-collator.md` T2.7.

!! `commands/proof.py` CALLED `proof_setter.run` DIRECTLY UNTIL THIS TASK, beside
`flows/revise.py`'s own call -- two mechanisms assembling a draft tree, when
stage 7a must read ONE artifact: the final revise. This module pins that there
is exactly one caller left.

!! IT COUNTS CALLS, NOT TEXT, AND IT COUNTED TEXT FOR ONE COMMIT. The first
form asked `"proof_setter.run(" in p.read_text()`, which cannot tell a CALL from
a MENTION -- and `machine/repo.py`'s docstring cites the function by name while
calling nothing. MEASURED: that citation registered as a second caller, and the
docstring was REWORDED to get past the scan. ! A PROSE EDIT IN AN UNRELATED
MODULE TO SATISFY A GREP IS THE TEST BENDING THE CODE. The reword is reverted
and the question is asked of the syntax tree instead, where a citation in a
string is not a call.
"""

import ast

from conftest import ROOT as REPO


def _calls_proof_setter_run(source: str) -> bool:
    """Does this module CALL `proof_setter.run`, as against naming it?

    A mention in a docstring, a comment or any other string is not a call:
    only an `ast.Call` whose target is the attribute `run` on the name
    `proof_setter` counts.
    """
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if (
            isinstance(func, ast.Attribute)
            and func.attr == "run"
            and isinstance(func.value, ast.Name)
            and func.value.id == "proof_setter"
        ):
            return True
    return False


def test_only_one_path_builds_a_draft_tree():
    # EXPECTATION FROM docs/plans/0.2.4-the-mark-and-the-collator.md, T2.7:
    # one mechanism builds a draft tree, and it is the revise pull.
    callers = [
        p
        for p in (REPO / "src").rglob("*.py")
        if _calls_proof_setter_run(p.read_text(encoding="utf-8"))
    ]
    assert [p.name for p in callers] == ["revise.py"]


def test_naming_the_function_in_prose_is_not_calling_it():
    # ! WHAT PROVES THE CHECK ASKS THE RIGHT QUESTION. `machine/repo.py` cites
    # `proof_setter.run(alterations, binder, repo, repo)` in a measurement note
    # and calls nothing; under the substring form it read as a caller.
    cited = (
        '"""A note about proof_setter.run(alterations, binder, repo).\n'
        '\nStill prose, and still not a call.\n"""\n'
    )
    assert not _calls_proof_setter_run(cited)
    assert _calls_proof_setter_run("proof_setter.run(docket, repo, scratch)\n")
