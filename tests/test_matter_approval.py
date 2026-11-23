"""A change to the file's matter asks the human at every step that makes one.

`decision-log.md Process: #274`, `#291`: each change to an `f` place is put to
the human on its own. A role's mark asks at collate; a role's rewriting answer
in a turn asks at that turn, and the chief's `recast` asks at the disposition.
"""

import json
from pathlib import Path

from helpers import (
    a_clean,
    a_correct_setting,
    a_source,
    copies_over,
    returned,
    run_command,
)

from comment_review.binder.binder import bind
from comment_review.binder.page import Page
from comment_review.commands import check as check_command
from comment_review.commands import disposition as disposition_command
from comment_review.commands import report
from comment_review.desk import report as events
from comment_review.desk.proof.state import DECIDED
from comment_review.flows.bus import (
    AnswersReturned,
    CopiesReturned,
    DispositionsWritten,
    handle,
)
from comment_review.flows.human import HumanAnswer, corrections_to_matter
from comment_review.flows.page_for import page_of
from comment_review.flows.proof_io import save_proof

F0 = "m.py@f0"
B0 = "m.py@b0"
LICENCE = "# Licensed under the example terms."
SAMPLE = "# Licensed under the sample terms."
OTHER = "# Licensed under the other terms."
RECAST = "# Licensed under the stated terms."
#: The one file `a_source` cites, copied into the test's root so it resolves.
CITED = "src/comment_review/desk/proof/mark.py"


def _root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    (root / CITED).parent.mkdir(parents=True)
    (root / CITED).write_bytes((Path(__file__).parents[1] / CITED).read_bytes())
    (root / "m.py").write_text(f"{LICENCE}\n\n# one\nv0 = 0\n", encoding="utf-8")
    return root


def _collated(tmp_path: Path, at_f0: dict):
    """The committed collate: each role cleans b0 and files `at_f0`'s mark at
    f0, a place no copy is dealt, so it is added to the role's sheet; each
    correction to f0 is approved."""
    root = _root(tmp_path)
    page = page_of(root / "m.py", rel="m.py")
    assert isinstance(page, Page), page
    binder = bind([page], read_from={"root": str(root), "revise": 0})
    roles = ("block-context", "function-context")
    wires = copies_over(binder, {role: {B0: a_clean(B0)} for role in roles})
    for wire in wires:
        if wire["role"] in at_f0:
            wire["sheets"][0]["marks"].append(at_f0[wire["role"]])
    copies = [returned(wire) for wire in wires]
    approved = tuple(
        HumanAnswer(q.role, q.at, q.question, "yes")
        for q in corrections_to_matter(copies, ())
    )
    out, result = handle(CopiesReturned("4c", copies, binder, root, None, approved))
    assert result is not None, out
    return root, result.proof


def test_check_reports_pending_matter_approval(tmp_path, monkeypatch, capsys):
    root = _root(tmp_path)
    page = page_of(root / "m.py", rel="m.py")
    assert isinstance(page, Page), page
    binder = bind([page], read_from={"root": str(root), "revise": 0})
    copy = copies_over(binder, {"block-context": {B0: a_clean(B0)}})[0]
    copy["sheets"][0]["marks"].append(a_correct_setting(F0, LICENCE, SAMPLE))
    binder_path = tmp_path / "binder.json"
    binder_path.write_text(json.dumps(binder.serialize()), encoding="utf-8")
    copy_path = tmp_path / "copy.json"
    copy_path.write_text(json.dumps(copy), encoding="utf-8")
    args = ("--edit-copy", str(copy_path), "--binder", str(binder_path))
    code, out = run_command(monkeypatch, capsys, check_command, *args)
    assert code == report.ASKS_THE_HUMAN, out
    assert "approve this correct to the file's matter" in out

    (question,) = corrections_to_matter([returned(copy)], ())
    human_path = tmp_path / "human.toml"
    human_path.write_text(
        f'[[answer]]\nrole = "{question.role}"\nat = "{question.at}"\n'
        f'question = {json.dumps(question.question)}\nanswer = "yes"\n',
        encoding="utf-8",
    )
    code, out = run_command(
        monkeypatch, capsys, check_command, *args, "--human", str(human_path)
    )
    assert code == report.OK, out


def _asked(out) -> list[tuple[str, str, str]]:
    return [
        (e.role, e.at, e.question) for e in out if isinstance(e, events.AsksTheHuman)
    ]


def _contested(tmp_path):
    """Two roles correcting f0 two ways: the place is carried to a turn."""
    return _collated(
        tmp_path,
        {
            "block-context": a_correct_setting(F0, "example", SAMPLE),
            "function-context": a_correct_setting(F0, "example", OTHER),
        },
    )


def _turn_answers(reason: str) -> dict:
    return {
        "block-context": [
            {"address": F0, "instruction": "hold", "reason": "mine reads correctly"}
        ],
        "function-context": [
            {
                "address": F0,
                "instruction": "correct",
                "reason": reason,
                "change": RECAST,
                "sources": a_source(),
            }
        ],
    }


def test_a_rewriting_answer_at_an_f_place_asks_the_human(tmp_path):
    root, proof = _contested(tmp_path)
    out, result = handle(AnswersReturned(proof, _turn_answers("stated"), root))
    assert result is None
    assert _asked(out) == [
        (
            "function-context",
            F0,
            "approve this correct to the file's matter: stated",
        )
    ]


def test_an_approved_rewriting_answer_at_an_f_place_folds(tmp_path):
    root, proof = _contested(tmp_path)
    yes = HumanAnswer(
        "function-context",
        F0,
        "approve this correct to the file's matter: stated",
        "yes",
    )
    out, result = handle(AnswersReturned(proof, _turn_answers("stated"), root, (yes,)))
    assert result is not None, out
    assert _asked(out) == []


def test_a_hold_at_an_f_place_asks_nothing(tmp_path):
    root, proof = _contested(tmp_path)
    answers = {
        role: [{"address": F0, "instruction": "hold", "reason": "mine stands"}]
        for role in ("block-context", "function-context")
    }
    out, _ = handle(AnswersReturned(proof, answers, root))
    assert _asked(out) == []


def _settled(tmp_path):
    """One role's approved correct at f0, which the other role then reads and
    cleans in a turn: it settles."""
    root, proof = _collated(
        tmp_path, {"block-context": a_correct_setting(F0, "example", SAMPLE)}
    )
    clean = {
        "address": F0,
        "instruction": "clean",
        "reason": "the corrected line reads right",
        "sources": a_source(),
    }
    out, turned = handle(AnswersReturned(proof, {"function-context": [clean]}, root))
    assert turned is not None, out
    assert {p.address: p.state for p in turned.proof.places}[F0] in DECIDED
    return turned.proof


RULING = {"address": F0, "answer": "recast", "prose": RECAST, "reason": "the sheet"}


def test_a_recast_at_an_f_place_asks_the_human(tmp_path):
    out, result = handle(DispositionsWritten(_settled(tmp_path), [RULING]))
    assert result is None
    assert _asked(out) == [
        ("copy-chief", F0, "approve this recast to the file's matter: the sheet")
    ]


def test_an_approved_recast_at_an_f_place_closes(tmp_path):
    yes = HumanAnswer(
        "copy-chief", F0, "approve this recast to the file's matter: the sheet", "yes"
    )
    out, result = handle(DispositionsWritten(_settled(tmp_path), [RULING], (yes,)))
    assert result is not None, out
    (place,) = [p for p in result.proof.places if p.address == F0]
    assert place.text == RECAST


def test_the_disposition_command_takes_the_approval_with_human(
    tmp_path, monkeypatch, capsys
):
    proof = tmp_path / "proof.json"
    save_proof(proof, _settled(tmp_path))
    rulings = tmp_path / "rulings.json"
    rulings.write_text(json.dumps([RULING]), encoding="utf-8")
    flags = [
        "--proof",
        str(proof),
        "--dispositions",
        str(rulings),
        "--proof-out",
        str(tmp_path / "final.json"),
    ]
    code, out = run_command(monkeypatch, capsys, disposition_command, *flags)
    assert code == report.ASKS_THE_HUMAN, out
    assert not (tmp_path / "final.json").exists()
    human = tmp_path / "human.toml"
    human.write_text(
        '[[answer]]\nrole = "copy-chief"\nat = "m.py@f0"\n'
        'question = "approve this recast to the file\'s matter: the sheet"\n'
        'answer = "yes"\n',
        encoding="utf-8",
    )
    code, out = run_command(
        monkeypatch, capsys, disposition_command, *flags, "--human", str(human)
    )
    assert code == report.OK, out
    assert (tmp_path / "final.json").exists()
