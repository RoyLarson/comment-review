import json
from dataclasses import replace

import pytest
from conftest import run_command
from helpers import a_clean, a_real_binder_over, returned

from comment_review.commands import check, collate
from comment_review.desk import report as events
from comment_review.desk.stages import Dispatch, Kind, Role, Stage
from comment_review.flows.bus import CopiesReturned, handle
from comment_review.flows.distribute import assigned_binder, seed


def _shards(tmp_path):
    binder = a_real_binder_over(
        tmp_path / "repo", {"m.py@b1": "# one", "n.py@b1": "# two"}
    )
    received = tuple(
        assigned_binder(replace(binder, pages=(page,))) for page in binder.pages
    )
    wires = [seed(b, "block-context") for b in received]
    for wire in wires:
        for sheet in wire["sheets"]:
            for slot in sheet["marks"]:
                slot.update(a_clean(slot["address"]))
    stage = Stage(
        "4c",
        Kind.EDITORIAL,
        "original",
        (),
        (
            Dispatch(Role.BLOCK_CONTEXT, ("m.py",)),
            Dispatch(Role.BLOCK_CONTEXT, ("n.py",)),
        ),
    )
    return binder, received, wires, stage


def test_check_detects_a_deleted_assigned_ruling(tmp_path, monkeypatch, capsys):
    binder, received, wires, _ = _shards(tmp_path)
    wires[0]["sheets"][0]["marks"] = []
    copy_path = tmp_path / "copy.json"
    copy_path.write_text(json.dumps(wires[0]), encoding="utf-8")
    binder_path = tmp_path / "received.json"
    binder_path.write_text(json.dumps(received[0].serialize()), encoding="utf-8")
    code, out = run_command(
        monkeypatch,
        capsys,
        check,
        "--edit-copy",
        str(copy_path),
        "--binder",
        str(binder_path),
        "--repo",
        str(binder.root),
    )
    assert code == check.BROKEN
    assert "m.py@b1" in out and "missing" in out
    assert "n.py@b1" not in out


def test_check_ignores_an_unassigned_blank(tmp_path, monkeypatch, capsys):
    binder, received, wires, _ = _shards(tmp_path)
    wires[0]["sheets"].extend(seed(received[1], "block-context")["sheets"])
    copy_path = tmp_path / "copy.json"
    copy_path.write_text(json.dumps(wires[0]), encoding="utf-8")
    binder_path = tmp_path / "received.json"
    binder_path.write_text(json.dumps(received[0].serialize()), encoding="utf-8")
    code, out = run_command(
        monkeypatch,
        capsys,
        check,
        "--edit-copy",
        str(copy_path),
        "--binder",
        str(binder_path),
        "--repo",
        str(binder.root),
    )
    assert code == check.OK, out


def test_collation_checks_each_copy_against_its_received_binder(tmp_path):
    binder, received, wires, stage = _shards(tmp_path)
    wires[0]["sheets"][0]["marks"] = []
    wires[1]["sheets"].extend(seed(received[0], "block-context")["sheets"])
    wires[1]["sheets"][-1]["marks"][0].update(a_clean("m.py@b1"))
    out, result = handle(
        CopiesReturned(
            "",
            [returned(w) for w in wires],
            binder,
            binder.root,
            stage,
            binders=received,
        )
    )
    assert result is None
    assert any(isinstance(e, events.Refused) and "m.py@b1" in str(e) for e in out)


def test_complete_shards_commit_without_changing_binders(tmp_path):
    binder, received, wires, stage = _shards(tmp_path)
    before = [b.serialize() for b in (binder, *received)]
    out, result = handle(
        CopiesReturned(
            "",
            [returned(w) for w in wires],
            binder,
            binder.root,
            stage,
            binders=received,
        )
    )
    assert result is not None, out
    assert [b.serialize() for b in (binder, *received)] == before


@pytest.mark.parametrize("defect", ["missing", "duplicate", "wrong-root"])
def test_received_binders_must_cover_the_role_assignment(tmp_path, defect):
    binder, received, wires, stage = _shards(tmp_path)
    if defect == "missing":
        received = (received[0], replace(received[1], pages=()))
    elif defect == "duplicate":
        received = (received[0], received[0])
    else:
        received = (
            received[0],
            replace(received[1], read_from={"root": "elsewhere", "revise": 0}),
        )
    out, result = handle(
        CopiesReturned(
            "",
            [returned(w) for w in wires],
            binder,
            binder.root,
            stage,
            binders=received,
        )
    )
    assert result is None
    assert any(isinstance(e, events.Refused) for e in out)


def test_cli_collation_accepts_paired_received_binders(tmp_path, monkeypatch, capsys):
    binder, received, wires, _ = _shards(tmp_path)
    binder_path = tmp_path / "binder.json"
    binder_path.write_text(json.dumps(binder.serialize()), encoding="utf-8")
    args = [
        "--stage",
        "",
        "--binder",
        str(binder_path),
        "--out",
        str(tmp_path / "chief.json"),
    ]
    for i, (b, wire) in enumerate(zip(received, wires, strict=True)):
        path = tmp_path / f"copy{i}.json"
        path.write_text(json.dumps(wire), encoding="utf-8")
        shard = tmp_path / f"received{i}.json"
        shard.write_text(json.dumps(b.serialize()), encoding="utf-8")
        args.extend(["--edit-copy", str(path), "--received-binder", str(shard)])
    code, out = run_command(monkeypatch, capsys, collate, *args)
    assert code == collate.OK, out
    assert (tmp_path / "chief.json").exists()
