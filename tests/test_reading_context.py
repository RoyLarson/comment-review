from dataclasses import FrozenInstanceError, replace
from pathlib import Path
from typing import Any

import pytest
from helpers import a_jacket_naming, proof_to_docket

from comment_review.flows import reading_context as flow_context
from comment_review.flows.compositor import round_trip
from comment_review.flows.gather import gather
from comment_review.reading.context import (
    Imprint,
    ReadingContext,
    compatible_contexts,
)
from comment_review.reading.context_io import context_to_wire
from comment_review.reading.diagnostics import ReadFailure


def test_saved_stage_with_no_dealt_rows_preserves_empty_shard_context(tmp_path):
    import json

    from comment_review.binder.binder import Binder
    from comment_review.desk.stages import Dispatch, Kind, Role, Stage
    from comment_review.flows.fan_out import dealt

    path = tmp_path / "m.py"
    path.write_bytes(b"x = 1\n# short\ny = 2\n")
    saved = tmp_path / "binder.json"
    saved.write_text(json.dumps(gather(tmp_path, [path]).binder.serialize()))
    binder, problems = Binder.deserialize(str(saved), json.loads(saved.read_text()))
    assert binder is not None, problems
    stage = Stage(
        name="empty",
        kind=Kind.EDITORIAL,
        reads="original",
        cap=10,
        series=("b",),
        dispatches=(Dispatch(Role.BLOCK_CONTEXT, ()),),
    )
    packets = dealt(binder, stage)
    assert len(packets) == 1
    received, copy = packets[0]
    assert received.pages[0].paragraphs == []
    expected = json.loads(saved.read_text())["pages"][0]["reading"]
    assert expected["reader"] == "python-lexical"
    assert received.serialize()["pages"][0]["reading"] == expected
    assert copy["sheets"][0]["reading"] == expected
    assert copy["sheets"][0]["marks"] == []


def test_ungathered_move_saved_proof_retains_destination_context_for_transcription(
    tmp_path, monkeypatch, capsys
):
    import json

    from conftest import run_command
    from helpers import BASE, a_clean, a_move, deal, disposition

    from comment_review.commands import proof

    root = tmp_path / "repo"
    root.mkdir()
    destination = root / "n.py"
    original = b"v0 = 0\n# seven\n# eight\nv1 = 1\n"
    destination.write_bytes(original)
    code = deal(
        tmp_path,
        monkeypatch,
        capsys,
        {
            "block-context": {
                "m.py@b1": a_move(
                    "m.py@b1",
                    "n.py@b1",
                    change="# two\n",
                    reads="# seven\n# eight\n# two",
                )
            },
            "function-context": {"m.py@b1": a_clean("m.py@b1")},
        },
    )
    assert code in (3, 4)
    binder = json.loads((tmp_path / "binder.json").read_text())
    assert [p["path"] for p in binder["pages"]] == ["m.py"]
    expected = binder["pages"][0]["reading"]
    assert expected["reader"] == "python-lexical"
    saved = json.loads((tmp_path / "proof0.json").read_text())
    assert saved["page_readings"] == {"m.py": expected, "n.py": expected}
    assert saved["page_shas"]["n.py"] == "19d7640ebdcb2fb1"
    code, out = disposition(
        tmp_path,
        monkeypatch,
        capsys,
        [
            {
                "address": "m.py@b1",
                "to": "n.py@b1",
                "answer": "taken_in",
                "side": "block-context",
                "reason": "move belongs here",
            }
        ],
        proof="proof0.json",
    )
    assert code in (3, 4), out
    code, out = disposition(
        tmp_path,
        monkeypatch,
        capsys,
        [
            {
                "address": "m.py@b1",
                "answer": "taken_in",
                "side": "block-context",
                "reason": "remainder stands",
            },
        ],
        proof="final.json",
    )
    assert code == 0, out
    assert json.loads((tmp_path / "final.json").read_text())["page_readings"] == {
        "m.py": expected,
        "n.py": expected,
    }
    assert json.loads((tmp_path / "final.json").read_text())["page_shas"]["n.py"] == (
        "19d7640ebdcb2fb1"
    )
    docket = tmp_path / "docket.json"
    why = proof_to_docket(tmp_path / "final.json", root, docket)
    code, out = (2 if why else 0), "\n".join(why)
    assert code == 0, out
    pages = json.loads(docket.read_text())["pages"]
    assert {p["path"]: p["reading"] for p in pages} == {
        "m.py": expected,
        "n.py": expected,
    }
    assert next(p for p in pages if p["path"] == "n.py")["sha"] == "19d7640ebdcb2fb1"
    code, out = run_command(
        monkeypatch,
        capsys,
        proof,
        "--from-docket",
        str(docket),
        "--repo",
        str(root),
        "--out",
        str(tmp_path / "revise"),
        with_stderr=True,
    )
    assert code == 0, out
    assert (tmp_path / "revise" / "n.py").read_bytes() == (
        b"v0 = 0\n# seven\n# eight\n# two\nv1 = 1\n"
    )
    assert destination.read_bytes() == original
    assert BASE.rstrip().encode() in (root / "m.py").read_bytes()


@pytest.mark.parametrize("fault", ["compatible", "missing", "old", "future"])
def test_saved_turn_and_disposition_keep_original_context_through_docket(
    tmp_path, monkeypatch, capsys, fault
):
    import json

    from conftest import run_command
    from helpers import DOS, held_open

    from comment_review.commands import disposition as disposition_command
    from comment_review.commands import proof

    held_open(tmp_path, monkeypatch, capsys)
    expected = json.loads((tmp_path / "binder.json").read_text())["pages"][0]["reading"]
    assert expected["reader"] == "python-lexical"
    for name in ("binder.json", "proof0.json", "proof1.json"):
        wire = json.loads((tmp_path / name).read_text())
        assert (
            wire["pages"][0]["reading"]
            if name == "binder.json"
            else wire["page_readings"]["m.py"]
        ) == expected
    if fault != "compatible":
        path = tmp_path / "proof1.json"
        wire = json.loads(path.read_text())
        if fault == "missing":
            wire.pop("page_readings")
        elif fault == "old":
            wire["edit_copies"][0]["sheets"][0].pop("reading")
        else:
            wire["page_readings"]["m.py"]["format"] = 2
        path.write_text(json.dumps(wire), encoding="utf-8")

        def forbidden(*args, **kwargs):
            pytest.fail("saved artifact refusal reached address work")

        monkeypatch.setattr("comment_review.flows.bus._places_on", forbidden)
    ruling = tmp_path / "dispositions.json"
    ruling.write_text(
        json.dumps(
            [
                {
                    "address": "m.py@b1",
                    "answer": "taken_in",
                    "side": "function-context",
                    "reason": "their wording stands",
                }
            ]
        ),
        encoding="utf-8",
    )
    before = {path: path.read_bytes() for path in tmp_path.rglob("*") if path.is_file()}
    code, out = run_command(
        monkeypatch,
        capsys,
        disposition_command,
        "--proof",
        str(tmp_path / "proof1.json"),
        "--dispositions",
        str(ruling),
        "--proof-out",
        str(tmp_path / "final.json"),
        with_stderr=True,
    )
    if fault != "compatible":
        assert code == 2, out
        assert "regather" in out
        assert {
            path: path.read_bytes() for path in tmp_path.rglob("*") if path.is_file()
        } == before
        return
    assert code == 0, out
    assert json.loads((tmp_path / "final.json").read_text())["page_readings"] == {
        "m.py": expected
    }
    docket = tmp_path / "docket.json"
    why = proof_to_docket(tmp_path / "final.json", tmp_path / "repo", docket)
    code, out = (2 if why else 0), "\n".join(why)
    assert code == 0, out
    assert json.loads(docket.read_text())["pages"][0]["reading"] == expected
    code, out = run_command(
        monkeypatch,
        capsys,
        proof,
        "--from-docket",
        str(docket),
        "--repo",
        str(tmp_path / "repo"),
        "--out",
        str(tmp_path / "revise"),
        with_stderr=True,
    )
    assert code == 0, out
    assert DOS.rstrip().encode() in (tmp_path / "revise" / "m.py").read_bytes()


@pytest.mark.parametrize("route", ["seed", "assigned"])
@pytest.mark.parametrize("fault", ["compatible", "reader", "missing", "future"])
def test_direct_distribution_admits_context_before_saved_rows(
    tmp_path, monkeypatch, route, fault
):
    from conftest import install_another_reader

    from comment_review.binder.binder import Binder
    from comment_review.exceptions import Refused
    from comment_review.flows import distribute

    path = tmp_path / "m.py"
    path.write_bytes(b"x = 1\n# old\ny = 2\n")
    binder = gather(tmp_path, [path]).binder
    wire = binder.serialize()
    if fault in ("missing", "future"):
        if fault == "missing":
            wire["pages"][0].pop("reading")
        else:
            wire["pages"][0]["reading"]["format"] = 2
        loaded, problems = Binder.deserialize("saved binder", wire)
        assert loaded is None
        assert any("regather" in problem for problem in problems)
        return
    if fault == "reader":
        install_another_reader(monkeypatch)

        def forbidden(*args, **kwargs):
            pytest.fail("incompatible in-memory binder reached saved rows")

        monkeypatch.setattr(distribute, "handed", forbidden)

    def operation():
        distribute.admit_binder(binder)
        return (
            distribute.seed(binder, "block-context")
            if route == "seed"
            else distribute.assigned_binder(binder)
        )

    if fault == "reader":
        with pytest.raises(Refused, match="regather"):
            operation()
    else:
        assert operation() is not None
    assert path.read_bytes() == b"x = 1\n# old\ny = 2\n"


@pytest.mark.parametrize("changed", [False, True])
def test_saved_mixed_workflow_keeps_literal_context_through_proof(
    tmp_path, monkeypatch, capsys, changed
):
    import json

    from conftest import install_another_reader, run_command

    from comment_review.commands import collate, distribute, mark, proof

    other = "n.rs"
    language = "rust"
    reader = "rust-lexical"

    root = tmp_path / "repo"
    root.mkdir()
    sources = {"m.py": b"x = 1\n# old\ny = 2\n", other: b""}
    for name, raw in sources.items():
        (root / name).write_bytes(raw)
    gathered = gather(root, [root / name for name in sources])
    assert not gathered.unreadable
    binder_path = tmp_path / "binder.json"
    binder_path.write_text(json.dumps(gathered.binder.serialize()), encoding="utf-8")
    wire = json.loads(binder_path.read_text(encoding="utf-8"))
    expected = {page["path"]: page["reading"] for page in wire["pages"]}
    assert expected["m.py"]["reader"] == "python-lexical"
    assert expected[other] == {"format": 1, "language": language, "reader": reader}
    copies = []
    for role in ("block-context", "function-context"):
        copy = tmp_path / f"{role}.json"
        code, out = run_command(
            monkeypatch,
            capsys,
            distribute,
            "--seed",
            "--binder",
            str(binder_path),
            "--role",
            role,
            "--out",
            str(copy),
            with_stderr=True,
        )
        assert code == 0, out
        code, out = run_command(
            monkeypatch,
            capsys,
            mark,
            "--edit-copy",
            str(copy),
            "--repo",
            str(root),
            "--address",
            "m.py@b1",
            "--instruction",
            "patch",
            "--cite",
            "m.py:1",
            "--change",
            "# new",
            "--from",
            "old",
            "--to",
            "new",
            "--reason",
            "clearer",
            with_stderr=True,
        )
        assert code == 0, out
        wire = json.loads(copy.read_text(encoding="utf-8"))
        assert {sheet["path"]: sheet["reading"] for sheet in wire["sheets"]} == expected
        assert next(s for s in wire["sheets"] if s["path"] == other)["marks"] == []
        copies.append(copy)
    proof_path = tmp_path / "proof.json"
    code, out = run_command(
        monkeypatch,
        capsys,
        collate,
        *a_jacket_naming(binder_path, copies),
        "--proof-out",
        str(proof_path),
        with_stderr=True,
    )
    assert code == 0, out
    saved_proof = json.loads(proof_path.read_text(encoding="utf-8"))
    assert saved_proof["page_readings"] == expected
    docket_path = tmp_path / "docket.json"
    if changed:
        install_another_reader(monkeypatch)
        before = {
            path: path.read_bytes() for path in tmp_path.rglob("*") if path.is_file()
        }

        def forbidden(*args, **kwargs):
            pytest.fail("saved proof context refusal reached address transcription")

        monkeypatch.setattr("comment_review.flows.transcribe._unclosed", forbidden)
    why = proof_to_docket(proof_path, root, docket_path)
    code, out = (2 if why else 0), "\n".join(why)
    if changed:
        assert code == 2, out
        assert "regather" in out
        assert {
            path: path.read_bytes() for path in tmp_path.rglob("*") if path.is_file()
        } == before
        return
    assert code == 0, out
    docket = json.loads(docket_path.read_text(encoding="utf-8"))
    assert docket["pages"][0]["reading"] == expected["m.py"]
    code, out = run_command(
        monkeypatch,
        capsys,
        proof,
        "--from-docket",
        str(docket_path),
        "--repo",
        str(root),
        "--out",
        str(tmp_path / "revise"),
        with_stderr=True,
    )
    assert code == 0, out
    assert (tmp_path / "revise" / "m.py").read_bytes() == b"x = 1\n# new\ny = 2\n"
    assert {name: (root / name).read_bytes() for name in sources} == sources


RUST_SOURCE = b"/// Adds one.\nfn add(x: i32) -> i32 {\n    // old\n    x + 1\n}\n"


def rust_context() -> ReadingContext:
    """The installed Rust context."""
    return ReadingContext("rust", "rust-lexical")


def rust_page(saved: ReadingContext):
    """`page_of` over the Rust source with a supplied saved context."""
    from comment_review.flows import page_for
    from comment_review.machine.repo import Source

    text = RUST_SOURCE.decode()
    return page_for.page_of(
        Path("m.rs"), source=Source(text, "sha"), reading_context=saved
    )


def test_rust_context_gathered_now_is_admitted(tmp_path):
    path = tmp_path / "m.rs"
    path.write_bytes(RUST_SOURCE)
    gathered = gather(tmp_path, [path])
    assert not gathered.unreadable
    current = gathered.binder.pages[0].reading
    assert current == rust_context()
    page = rust_page(current)
    assert not isinstance(page, ReadFailure)
    assert page.reading == current
    admitted, problems = flow_context.admit_pages(("binder", gathered.binder.pages))
    assert problems == []
    assert admitted == {"m.rs": Imprint(gathered.binder.pages[0].sha, current)}


def test_saved_rust_workflow_keeps_context_through_the_draft(
    tmp_path, monkeypatch, capsys
):
    import json

    from conftest import run_command

    from comment_review.commands import check, collate, distribute, mark, proof

    root = tmp_path / "repo"
    root.mkdir()
    (root / "m.rs").write_bytes(RUST_SOURCE)
    gathered = gather(root, [root / "m.rs"])
    assert not gathered.unreadable
    binder_path = tmp_path / "binder.json"
    binder_path.write_text(json.dumps(gathered.binder.serialize()), encoding="utf-8")
    expected = json.loads(binder_path.read_text(encoding="utf-8"))["pages"][0][
        "reading"
    ]
    assert expected == context_to_wire(rust_context())
    assert expected["reader"] == "rust-lexical"
    copies = []
    for role in ("block-context", "function-context"):
        copy = tmp_path / f"{role}.json"
        code, out = run_command(
            monkeypatch,
            capsys,
            distribute,
            "--seed",
            "--binder",
            str(binder_path),
            "--role",
            role,
            "--out",
            str(copy),
            with_stderr=True,
        )
        assert code == 0, out
        code, out = run_command(
            monkeypatch,
            capsys,
            mark,
            "--edit-copy",
            str(copy),
            "--repo",
            str(root),
            "--address",
            "m.rs@b1",
            "--instruction",
            "patch",
            "--cite",
            "m.rs:1",
            "--change",
            "    // new",
            "--from",
            "old",
            "--to",
            "new",
            "--reason",
            "clearer",
            with_stderr=True,
        )
        assert code == 0, out
        code, out = run_command(
            monkeypatch,
            capsys,
            mark,
            "--edit-copy",
            str(copy),
            "--repo",
            str(root),
            "--address",
            "m.rs@a1",
            "--instruction",
            "clean",
            "--cite",
            "m.rs:1",
            with_stderr=True,
        )
        assert code == 0, out
        code, out = run_command(
            monkeypatch,
            capsys,
            check,
            "--edit-copy",
            str(copy),
            "--binder",
            str(binder_path),
            with_stderr=True,
        )
        assert code == 0, out
        sheets = json.loads(copy.read_text(encoding="utf-8"))["sheets"]
        assert [sheet["reading"] for sheet in sheets] == [expected]
        copies.append(copy)
    proof_path = tmp_path / "proof.json"
    code, out = run_command(
        monkeypatch,
        capsys,
        collate,
        *a_jacket_naming(binder_path, copies),
        "--proof-out",
        str(proof_path),
        with_stderr=True,
    )
    assert code == 0, out
    saved_proof = json.loads(proof_path.read_text(encoding="utf-8"))
    assert saved_proof["page_readings"] == {"m.rs": expected}
    docket_path = tmp_path / "docket.json"
    why = proof_to_docket(proof_path, root, docket_path)
    code, out = (2 if why else 0), "\n".join(why)
    assert code == 0, out
    docket = json.loads(docket_path.read_text(encoding="utf-8"))
    assert [page["reading"] for page in docket["pages"]] == [expected]
    code, out = run_command(
        monkeypatch,
        capsys,
        proof,
        "--from-docket",
        str(docket_path),
        "--repo",
        str(root),
        "--out",
        str(tmp_path / "revise"),
        with_stderr=True,
    )
    assert code == 0, out
    assert (tmp_path / "revise" / "m.rs").read_bytes() == RUST_SOURCE.replace(
        b"// old", b"// new"
    )
    assert (root / "m.rs").read_bytes() == RUST_SOURCE


def test_proof_transcription_admits_extra_context_before_saved_places(
    monkeypatch, tmp_path
):
    from comment_review.desk.proof.master_proof import MasterProof
    from comment_review.flows import transcribe

    saved = flow_context.context_for(Path("extra.py"))
    assert isinstance(saved, ReadingContext)
    proof = MasterProof(
        "4c",
        {},
        (),
        {"extra.py": replace(saved, reader="another-reader")},
        page_shas={"extra.py": "original-sha"},
    )
    monkeypatch.setattr(
        transcribe, "_unclosed", lambda _: pytest.fail("places inspected")
    )
    with pytest.raises(transcribe.CannotTranscribe, match="regather"):
        transcribe.docket_of_proof(proof, tmp_path)


@pytest.mark.parametrize("reading", [None, {}, {"format": 2}])
def test_schedule_requires_reading_even_without_alterations(reading):
    from comment_review.docket.docket import Schedule

    schedule, problems = Schedule.deserialize(
        "docket",
        {
            "path": "m.py",
            "sha": "original",
            "alterations": [],
            "reading": reading,
        },
    )
    assert schedule is None
    assert any("regather" in reason for reason in problems)


def test_schedule_real_save_load_preserves_exact_original_context(tmp_path):
    import json

    from comment_review.docket.docket import Alteration, Docket, Schedule

    saved = ReadingContext("python", "lexical")
    docket = Docket(
        (Schedule("extra.py", "original-sha", (Alteration("b1", "new"),), saved),)
    )
    path = tmp_path / "docket.json"
    path.write_text(json.dumps(docket.serialize()), encoding="utf-8")
    loaded, problems = Docket.deserialize(
        str(path), json.loads(path.read_text(encoding="utf-8"))
    )
    assert problems == []
    assert loaded == docket


def test_docket_refuses_contradictory_repeated_schedule_metadata():
    from comment_review.docket.docket import Docket

    first = {
        "path": "m.py",
        "sha": "original",
        "alterations": [{"cue": "b1", "text": "new"}],
        "reading": {"format": 1, "language": "python", "reader": "lexical"},
    }
    second = {
        **first,
        "sha": "different",
        "reading": {**first["reading"], "reader": "another"},
    }
    docket, problems = Docket.deserialize("docket", {"pages": [first, second]})
    assert docket is None
    assert problems == ["m.py: two schedules for one page"]


def test_saved_mixed_proof_transcribes_original_extra_destination(tmp_path):
    import json

    from comment_review.desk.proof.master_proof import MasterProof
    from comment_review.desk.proof.place import Place
    from comment_review.desk.proof.state import State
    from comment_review.flows.page_for import page_of
    from comment_review.flows.transcribe import docket_of_proof

    name = "other.rs"
    text = "// old\nconst X: i32 = 1;\n"

    (tmp_path / "extra.py").write_text("# old\nx = 1\n", encoding="utf-8")
    (tmp_path / name).write_text(text, encoding="utf-8")
    page = page_of(tmp_path / "extra.py", rel="extra.py")
    other = page_of(tmp_path / name, rel=name)
    assert not isinstance(page, ReadFailure)
    assert not isinstance(other, ReadFailure)
    place = Place(
        "extra.py@b1", page.cues.anchor_of("b1"), "old", text="new", state=State.STANDS
    )
    proof = MasterProof(
        "4c",
        {},
        (),
        {page.path: page.reading, other.path: other.reading},
        places=(place,),
        page_shas={page.path: page.sha, other.path: other.sha},
    )
    saved = tmp_path / "proof.json"
    saved.write_text(json.dumps(proof.serialize()), encoding="utf-8")
    loaded, problems = MasterProof.deserialize(
        str(saved), json.loads(saved.read_text(encoding="utf-8"))
    )
    assert loaded is not None, problems
    docket = docket_of_proof(loaded, tmp_path)
    assert len(docket.schedules) == 1
    schedule = docket.schedules[0]
    assert schedule.reading is loaded.page_readings["extra.py"]
    assert schedule.sha == page.sha


@pytest.mark.parametrize("fault", ["compatible", "reader", "language", "malformed"])
def test_direct_copy_metadata_is_admitted_without_trusting_annotations(fault):
    from comment_review.desk.proof.edit_copy import EditCopy
    from comment_review.desk.proof.sheet import Sheet

    saved = flow_context.context_for(Path("m.py"))
    assert isinstance(saved, ReadingContext)
    if fault == "reader":
        saved = replace(saved, reader="another-reader")
    elif fault == "language":
        object.__setattr__(saved, "language", "")
    sheet = Sheet("m.py", "unchanged-sha", (), saved)
    if fault == "malformed":
        object.__setattr__(sheet, "reading", [])
    copy = EditCopy("block-context", {"root": "."}, (sheet,))
    before = repr(copy)
    _, unadmitted = flow_context.admit_pages(("edit_copy: block-context", copy.sheets))
    problems = [one.text for one in unadmitted]
    if fault == "compatible":
        assert problems == []
    else:
        assert problems and "regather" in " ".join(problems)
        assert "block-context" in " ".join(problems)
    assert repr(copy) == before


def test_direct_proof_saved_context_is_admitted_against_installed_identity():
    from comment_review.desk.proof.master_proof import MasterProof

    saved = flow_context.context_for(Path("m.py"))
    assert isinstance(saved, ReadingContext)
    proof = MasterProof("4c", {}, (), {"m.py": saved}, page_shas={"m.py": "sha"})
    assert flow_context.admit_proof(proof)[1] == []
    proof.page_readings["m.py"] = replace(saved, reader="another-reader")
    assert "regather" in " ".join(
        one.text for one in flow_context.admit_proof(proof)[1]
    )


@pytest.mark.parametrize(
    "path, sha",
    [("m.py", None), ("m.py", ""), ("m.py", " "), ("m.py", 3), ("", "sha"), (7, "sha")],
)
def test_direct_extra_page_proof_refuses_invalid_sha_metadata(path, sha):
    from comment_review.desk.proof.master_proof import MasterProof

    saved = flow_context.context_for(Path("m.py"))
    assert isinstance(saved, ReadingContext)
    proof = MasterProof("4c", {}, (), {"m.py": saved}, page_shas={path: sha})
    problems = proof.reading_problems("master_proof")
    assert any("page_shas" in reason and "regather" in reason for reason in problems)


def test_installed_contexts_are_retained_in_fresh_results(tmp_path):
    path = tmp_path / "x.py"
    path.write_text("# prose\n", encoding="utf-8")
    gathering = gather(tmp_path, [path])
    assert gathering.binder.pages[0].reading.language == "python"
    result = round_trip(path)
    assert not isinstance(result, ReadFailure)
    assert result.reading_context == gathering.binder.pages[0].reading


@pytest.mark.parametrize("command", ["gather", "compositor", "prove_unchanged"])
def test_reading_settings_is_not_an_option(tmp_path, monkeypatch, command):
    import importlib
    import sys

    module = importlib.import_module(f"comment_review.commands.{command}")
    argv = [command, str(tmp_path / "x.py"), "--reading-settings", "s.json"]
    if command == "prove_unchanged":
        argv += ["--base", "HEAD"]
    monkeypatch.setattr(sys, "argv", argv)
    with pytest.raises(SystemExit) as refused:
        module.main(argv[1:]) if command == "compositor" else module.main()
    assert refused.value.code == 2


def test_exact_context_equality():
    saved = ReadingContext("invented", "reader-one")
    current = ReadingContext("invented", "reader-one")
    assert saved == current
    assert compatible_contexts(saved, current)


@pytest.mark.parametrize(
    "language,reader", [("other", "reader-one"), ("invented", "reader-two")]
)
def test_each_context_field_must_match(language, reader):
    saved = ReadingContext("invented", "reader-one")
    current = ReadingContext(language, reader)
    assert not compatible_contexts(saved, current)
    assert not compatible_contexts(current, saved)


@pytest.mark.parametrize("field", ["language", "reader"])
@pytest.mark.parametrize("invalid", ["", None, 1, True, [], (), {}])
def test_invalid_identity_is_rejected(field, invalid):
    values: dict[str, Any] = {"language": "invented", "reader": "reader-one"}
    values[field] = invalid
    with pytest.raises(ValueError):
        ReadingContext(**values)


@pytest.mark.parametrize("field", ["language", "reader"])
def test_context_fields_cannot_be_reassigned(field):
    context = ReadingContext("invented", "reader-one")
    with pytest.raises(FrozenInstanceError):
        setattr(context, field, "replacement")


def wire_context() -> dict[str, Any]:
    return {
        "format": 1,
        "language": "uninstalled-language",
        "reader": "uninstalled-reader",
    }


def test_context_wire_decodes_literal():
    from comment_review.reading.context_io import context_from_wire

    decoded, problems = context_from_wire("input.json:context", wire_context())
    assert problems == []
    assert decoded == ReadingContext("uninstalled-language", "uninstalled-reader")


def test_context_wire_serialization_is_exact_detached_and_round_trips():
    from comment_review.reading.context_io import context_from_wire, context_to_wire

    context = ReadingContext("uninstalled-language", "uninstalled-reader")
    encoded = context_to_wire(context)
    assert encoded == wire_context()
    assert context_from_wire("context", encoded) == (context, [])
    again = context_to_wire(context)
    assert again is not encoded
    encoded["language"] = "changed"
    assert context_to_wire(context) == wire_context()


@pytest.mark.parametrize("value", [None, [], (), "context", 1, True])
def test_context_wire_requires_object_with_regather_diagnostic(value):
    from comment_review.reading.context_io import context_from_wire

    decoded, problems = context_from_wire("input.json:context", value)
    assert decoded is None
    assert len(problems) == 1
    assert "input.json:context" in problems[0]
    assert "regather" in problems[0].lower()


@pytest.mark.parametrize("key", list(wire_context()))
def test_context_wire_requires_every_key(key):
    from comment_review.reading.context_io import context_from_wire

    value = wire_context()
    del value[key]
    decoded, problems = context_from_wire("input.json:context", value)
    assert decoded is None
    assert "input.json:context" in problems[0]
    assert key in problems[0]
    assert "regather" in problems[0].lower()


@pytest.mark.parametrize("key", ["extra", 1, None, "compatibility", "settings"])
def test_context_wire_rejects_unknown_keys(key):
    from comment_review.reading.context_io import context_from_wire

    value = wire_context()
    value[key] = "extra"
    decoded, problems = context_from_wire("wire", value)
    assert decoded is None
    assert "wire" in problems[0]
    assert "regather" in problems[0].lower()


@pytest.mark.parametrize("version", [2, 0, -1, True, False, 1.0, "1", None])
def test_context_wire_rejects_unsupported_and_noninteger_formats(version):
    from comment_review.reading.context_io import context_from_wire

    value = wire_context()
    value["format"] = version
    decoded, problems = context_from_wire("wire", value)
    assert decoded is None
    assert "wire" in problems[0]
    assert "format" in problems[0]
    assert "regather" in problems[0].lower()


@pytest.mark.parametrize(
    "field,invalid",
    [
        ("language", ""),
        ("language", None),
        ("language", 1),
        ("reader", ""),
        ("reader", True),
        ("reader", []),
    ],
)
def test_context_wire_rejects_invalid_values_with_located_diagnostic(field, invalid):
    from comment_review.reading.context_io import context_from_wire

    value = wire_context()
    value[field] = invalid
    decoded, problems = context_from_wire("input.json:context", value)
    assert decoded is None
    assert len(problems) == 1
    assert "input.json:context" in problems[0]
    assert "regather" in problems[0].lower()


def test_context_wire_requires_exact_dictionary_types():
    from comment_review.reading.context_io import context_from_wire

    class DictionarySubclass(dict):
        pass

    decoded, problems = context_from_wire("wire", DictionarySubclass(wire_context()))
    assert decoded is None
    assert "wire" in problems[0]


def test_context_wire_unexpected_constructor_defects_propagate(monkeypatch):
    from comment_review.reading import context_io

    def broken_context(*args):
        raise RuntimeError("unexpected defect")

    monkeypatch.setattr(context_io, "ReadingContext", broken_context)
    with pytest.raises(RuntimeError, match="unexpected defect"):
        context_io.context_from_wire("wire", wire_context())
