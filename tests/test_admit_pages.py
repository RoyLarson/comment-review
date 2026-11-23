"""`flows.reading_context.admit_pages`: each page's identity admitted once per load."""

import json
from collections import Counter
from dataclasses import replace

from conftest import install_another_reader, run_command
from helpers import (
    a_clean,
    a_correct_setting,
    a_real_binder_over,
    copies_over,
    returned,
)

from comment_review.commands import check, collate
from comment_review.desk import report as events
from comment_review.flows import on_the_page, page_for, reading_context
from comment_review.flows.bus import CopiesReturned, handle
from comment_review.flows.distribute import seed

BASE = "# one\n# two\n# three"
OTHER = "# four\n# five\n# six"
CORRECTED = "# one\n# TWO\n# three"

THREE_ROLES = {
    "block-context": {
        "m.py@b1": a_correct_setting("m.py@b1", "two", CORRECTED),
        "m.py@b2": a_clean("m.py@b2"),
    },
    "function-context": {
        "m.py@b1": a_clean("m.py@b1"),
        "m.py@b2": a_clean("m.py@b2"),
    },
    "module-context": {
        "m.py@b1": a_clean("m.py@b1"),
        "m.py@b2": a_clean("m.py@b2"),
    },
}


def _message(tmp_path):
    root = tmp_path / "repo"
    binder = a_real_binder_over(root, {"m.py@b1": BASE, "m.py@b2": OTHER})
    copies = [returned(wire) for wire in copies_over(binder, THREE_ROLES)]
    return CopiesReturned("4c", copies, binder, root, None)


def _refusals(out):
    return [
        reason
        for one in out
        if isinstance(one, events.Refused)
        for reason in one.reasons
    ]


def test_one_collate_checks_each_page_against_the_installed_reader_once(
    tmp_path, monkeypatch
):
    message = _message(tmp_path)
    asked = Counter()
    derive = reading_context.context_for

    def count(path, **kwargs):
        asked[path.name] += 1
        return derive(path, **kwargs)

    for module in (reading_context, on_the_page, page_for):
        monkeypatch.setattr(module, "context_for", count)
    out, result = handle(message)
    assert result is not None, out
    assert asked == {"m.py": 1}


def test_one_collate_compares_each_later_claim_once(tmp_path, monkeypatch):
    message = _message(tmp_path)
    compared = Counter()
    equal = reading_context.Imprint.__eq__

    def count(self, other):
        compared[self.sha] += 1
        return equal(self, other)

    monkeypatch.setattr(reading_context.Imprint, "__eq__", count)
    out, result = handle(message)
    assert result is not None, out
    # The stage binder sets the entry; each of the three copies is one later claim.
    assert sum(compared.values()) == len(message.copies)


def test_a_reader_mismatch_is_refused_once_naming_the_path(tmp_path, monkeypatch):
    message = _message(tmp_path)
    install_another_reader(monkeypatch)
    out, result = handle(message)
    assert result is None
    naming = [reason for reason in _refusals(out) if "m.py" in reason]
    assert len(naming) == 1, naming
    assert "regather" in naming[0]


def test_check_refuses_a_sheet_sha_that_disagrees_with_its_binder(
    tmp_path, monkeypatch, capsys
):
    binder = a_real_binder_over(tmp_path / "repo", {"m.py@b1": BASE})
    wire = seed(binder, "block-context")
    for sheet in wire["sheets"]:
        sheet["sha"] = "another-gather"
        for slot in sheet["marks"]:
            slot.update(a_clean(slot["address"]))
    copy_path = tmp_path / "copy.json"
    copy_path.write_text(json.dumps(wire), encoding="utf-8")
    binder_path = tmp_path / "binder.json"
    binder_path.write_text(json.dumps(binder.serialize()), encoding="utf-8")
    args = ("--edit-copy", str(copy_path), "--binder", str(binder_path))
    code, out = run_command(monkeypatch, capsys, check, *args, with_stderr=True)
    assert code == check.UNREADABLE, out
    assert "m.py" in out and "sha" in out, out

    wire["sheets"][0]["sha"] = binder.pages[0].sha
    copy_path.write_text(json.dumps(wire), encoding="utf-8")
    code, out = run_command(monkeypatch, capsys, check, *args)
    assert code == check.OK, out


def test_admit_pages_keeps_the_first_claimant_and_names_the_later(tmp_path):
    binder = a_real_binder_over(tmp_path / "repo", {"m.py@b1": BASE})
    page = binder.pages[0]
    later = replace(page, sha="another-gather")
    table, reasons = reading_context.admit_pages(
        ("stage binder", binder.pages), ("received binder", [later])
    )
    assert table == {}
    assert reasons == [
        reading_context.Unadmitted(
            "received binder",
            "received binder: m.py: sha disagrees with stage binder; regather",
        )
    ]
    table, reasons = reading_context.admit_pages(("stage binder", binder.pages))
    assert reasons == []
    assert table == {"m.py": reading_context.Imprint(page.sha, page.reading)}


def test_collate_exits_unreadable_for_a_sheet_sha_that_disagrees_with_its_binder(
    tmp_path, monkeypatch, capsys
):
    binder = a_real_binder_over(tmp_path / "repo", {"m.py@b1": BASE})
    wire = seed(binder, "block-context")
    for sheet in wire["sheets"]:
        sheet["sha"] = "another-gather"
        for slot in sheet["marks"]:
            slot.update(a_clean(slot["address"]))
    copy_path = tmp_path / "copy.json"
    copy_path.write_text(json.dumps(wire), encoding="utf-8")
    binder_path = tmp_path / "binder.json"
    binder_path.write_text(json.dumps(binder.serialize()), encoding="utf-8")
    proof_path = tmp_path / "proof.json"
    code, out = run_command(
        monkeypatch,
        capsys,
        collate,
        "--stage",
        "4c",
        "--binder",
        str(binder_path),
        "--proof-out",
        str(proof_path),
        "--edit-copy",
        str(copy_path),
    )
    assert code == 2, out
    assert "m.py: sha disagrees with stage binder" in out, out
    assert not proof_path.exists()


def test_a_fold_refusal_still_exits_broken(tmp_path):
    from comment_review.commands.report import BROKEN, UNREADABLE, code_for

    refused = events.Refused("block-context", "m.py@b1", ("a quote is not there",))
    unreadable = events.Refused("", "", ("m.py: sha disagrees",), unreadable=True)
    assert code_for(events.rollback([refused])) == BROKEN
    assert code_for(events.rollback([refused, unreadable])) == UNREADABLE
