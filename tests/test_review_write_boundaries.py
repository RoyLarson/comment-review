import pytest
from conftest import build
from helpers import a_clean, a_move, a_real_binder_over, copies_over, returned

from comment_review.desk.marks.rules import comment_at
from comment_review.desk.proof.master_proof import MasterProof
from comment_review.docket.docket import Alteration, Docket, Schedule
from comment_review.flows.bus import (
    AnswersReturned,
    CopiesReturned,
    DispositionsWritten,
    handle,
)
from comment_review.flows.page_for import page_of
from comment_review.flows.proof_setter import run
from comment_review.flows.transcribe import CannotTranscribe, docket_of_proof
from comment_review.results import compositor, galley


def _move_into_ungathered_page(tmp_path, peer=False):
    repo = tmp_path / "repo"
    binder = a_real_binder_over(repo, {"m.py@b1": "# origin\n"})
    (repo / "n.py").write_text("v0 = 0\n# destination\nv1 = 1\n", encoding="utf-8")
    mark = a_move(
        "m.py@b1",
        "n.py@b1",
        change="# origin",
        reads="# destination\n# origin",
    )
    by_role = {"block-context": {"m.py@b1": mark}}
    if peer:
        by_role["function-context"] = {"m.py@b1": a_clean("m.py@b1")}
    copies = [returned(wire) for wire in copies_over(binder, by_role)]
    events, result = handle(CopiesReturned("4c", copies, binder, repo, None))
    assert result is not None, events
    return result, repo


@pytest.mark.parametrize(
    "changed",
    [
        "v0 = 0\n# newer destination\nv1 = 1\n",
        "v0 = 0\n# destination\nv1 = 1\nv2 = 2\n",
    ],
)
def test_saved_proof_refuses_a_destination_changed_after_collation(tmp_path, changed):
    result, repo = _move_into_ungathered_page(tmp_path)
    proof = result.proof
    proof, problems = MasterProof.deserialize("proof", proof.serialize())
    assert proof is not None and not problems
    (repo / "n.py").write_text(changed, encoding="utf-8")
    drafted, refused = run(docket_of_proof(proof, repo), repo, tmp_path / "draft")
    assert refused and not drafted
    assert not (tmp_path / "draft" / "n.py").exists()
    assert (repo / "n.py").read_text(encoding="utf-8") == changed


def test_unchanged_destination_identity_survives_a_committed_transition(tmp_path):
    result, repo = _move_into_ungathered_page(tmp_path)
    proof = result.proof
    events, result = handle(DispositionsWritten(proof, []))
    assert result is not None, events
    assert result.proof.page_shas == proof.page_shas
    assert "n.py" in proof.page_shas
    drafted, refused = run(
        docket_of_proof(result.proof, repo), repo, tmp_path / "draft"
    )
    assert not refused and len(drafted) == 2


def test_a_legacy_proof_cannot_invent_an_ungathered_destination_identity(tmp_path):
    result, repo = _move_into_ungathered_page(tmp_path)
    proof = result.proof
    wire = proof.serialize()
    wire.pop("page_shas", None)
    proof, problems = MasterProof.deserialize("legacy", wire)
    assert proof is not None and not problems
    with pytest.raises(CannotTranscribe, match="recorded.*sha"):
        docket_of_proof(proof, repo)


def test_destination_identity_survives_an_answer_turn(tmp_path):
    collated, repo = _move_into_ungathered_page(tmp_path, peer=True)
    proof, batch = collated.proof, collated.batch
    assert batch
    answers = {
        role: [
            {
                "address": slot["address"],
                "anchor": slot["anchor"],
                "instruction": "agree" if slot["question"] == "placement" else "clean",
                "reason": "Accept the move.",
                **({"to": slot["to"]} if "to" in slot else {}),
            }
            for slot in slots
        ]
        for role, slots in batch.items()
    }
    events, result = handle(AnswersReturned(proof, answers, repo))
    assert result is not None and result.batch, events
    assert result.proof.page_shas == proof.page_shas
    answers = {
        role: [
            {
                "address": slot["address"],
                "anchor": slot["anchor"],
                "instruction": "clean",
                "reason": "Accept the remaining text.",
            }
            for slot in slots
        ]
        for role, slots in result.batch.items()
    }
    events, result = handle(AnswersReturned(result.proof, answers, repo))
    assert result is not None and result.batch is None, events
    assert result.proof.page_shas == proof.page_shas
    drafted, refused = run(
        docket_of_proof(result.proof, repo), repo, tmp_path / "draft"
    )
    assert not refused and len(drafted) == 2


@pytest.mark.parametrize(
    "page_shas", [None, [], "sha", {"": "sha"}, {"m.py": ""}, {"m.py": 7}, {7: "sha"}]
)
def test_proof_refuses_malformed_page_identities(page_shas):
    proof, problems = MasterProof.deserialize(
        "proof",
        {
            "edit_copies": [],
            "page_shas": page_shas,
        },
    )
    assert proof is None and problems


@pytest.mark.parametrize(
    "text",
    [
        "x = 1",
        "x = 1\n",
        "# before\nx = 1\n# after",
        "# before\nx = 1\n# after\n",
        "x = 1\r\n# after\r\n",
    ],
)
def test_inserted_closing_gap_survives_proof_and_rereading(tmp_path, text):
    repo = tmp_path / "repo"
    repo.mkdir()
    source = repo / "m.py"
    source.write_text(text, encoding="utf-8", newline="")
    page, problems = page_of(source, rel="m.py")
    assert page is not None, problems
    docket = Docket(
        (
            Schedule(
                "m.py",
                page.sha,
                (Alteration("b1", "# new", page.cues.anchor_of("b1")),),
            ),
        )
    )
    drafted, refused = run(docket, repo, tmp_path / "draft")
    assert not refused and len(drafted) == 1
    reread, problems = page_of(tmp_path / "draft" / "m.py", rel="m.py")
    assert reread is not None, problems
    assert next(p for p in reread.paragraphs if p.address == "m.py@b1").text == "new"
    if "# after" in text:
        assert (
            next(p for p in reread.paragraphs if p.address == "m.py@f1").text == "after"
        )


@pytest.mark.parametrize(
    "expression",
    [
        '"First " "second."',
        "'First ' \"second.\"",
        '"Fir" "st second."',
        '("First "\n     "second.")',
        'r"First " u"second."',
    ],
)
def test_all_concatenated_docstring_literals_are_prose(expression):
    source = "def f():\n    " + expression + "\n    return 1\n"
    page = build(source, "m.py")
    paragraph = next(p for p in page if p.address == "m.py@a1")
    form = comment_at(paragraph.address, paragraph.raw_text)
    assert form.text == paragraph.text == "First second."
    changed = form.without_once("second.")
    assert changed is not None
    assert not galley.reset(page, {"a1": changed})
    output = compositor.set_page(page)
    namespace = {}
    exec(compile(output, "m.py", "exec"), namespace)
    assert namespace["f"]() == 1
    reread = build("def f():\n" + changed + "\n    return 1\n", "m.py")
    assert next(p for p in reread if p.address == "m.py@a1").text == "First"


def test_dropping_concatenated_docstrings_keeps_the_adjacent_statement():
    source = 'def f():\n    "First " "second."; print("other")\n    return 1\n'
    paragraph = next(p for p in build(source, "m.py") if p.address == "m.py@a1")
    form = comment_at(paragraph.address, paragraph.raw_text)
    assert form.text == "First second."
    assert form.without_once("First second.") == '    print("other")'


@pytest.mark.parametrize(
    "expression,snippet,remaining",
    [
        ('"First\\n" "second."', "second.", "First"),
        ('"First " "second\\x2e"', "second.", "First"),
        ('"Café " "second."', "second.", "Café"),
        ('"First " "second."; "other statement"', "second.", "First"),
        ('"Fir" "st second."', "First", "second."),
    ],
)
def test_concatenated_docstring_removals_follow_decoded_payloads(
    expression, snippet, remaining
):
    raw = "    " + expression
    form = comment_at("m.py@a1", raw)
    changed = form.without_once(snippet)
    assert changed is not None
    assert comment_at("m.py@a1", changed).text == remaining
    compile("def f():\n" + changed + "\n    return 1\n", "m.py", "exec")


def test_raw_literal_removal_refuses_an_invalid_closing_quote():
    form = comment_at("m.py@a1", '    r"Kept\\\\" "Move."')
    assert form.without_once("\\Move.") is None
