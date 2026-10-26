from dataclasses import FrozenInstanceError, replace
from hashlib import sha256
from inspect import signature
from pathlib import Path
from typing import Any

import pytest

from comment_review.flows import reading_context as flow_context
from comment_review.flows.compositor import round_trip
from comment_review.flows.gather import gather
from comment_review.reading import context as context_module
from comment_review.reading.context import ReadingContext, compatible_contexts
from comment_review.reading.context_io import context_to_wire
from comment_review.reading.definitions import LanguageDefinition, decode_definition
from comment_review.reading.diagnostics import ReadFailure
from comment_review.reading.lexer import LexicalRead
from comment_review.reading.registry import LanguageRegistry


def test_saved_stage_with_no_dealt_rows_preserves_empty_shard_context(tmp_path):
    import json

    from comment_review.binder.binder import Binder
    from comment_review.desk.stages import Dispatch, Kind, Role, Stage
    from comment_review.flows.fan_out import dealt

    path = tmp_path / "m.py"
    path.write_bytes(b"x = 1\n# short\ny = 2\n")
    saved = tmp_path / "binder.json"
    saved.write_text(json.dumps(gather(tmp_path, [path], 0).binder.serialize()))
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


def test_saved_nondefault_per_file_settings_ignore_unrelated_language_change(
    tmp_path, monkeypatch, capsys
):
    import json

    from conftest import run_command

    from comment_review.commands import distribute, mark, proof
    from comment_review.reading.readers import ReaderBinding, reader_for

    registry = flow_context.installed_registry()
    assert not isinstance(registry, ReadFailure)
    installed_python = reader_for(Path("a.py"), registry)
    assert isinstance(installed_python, tuple)
    assert isinstance(installed_python[1], ReaderBinding)
    fixture_binding = ReaderBinding(
        "invented-reader",
        "reader-1",
        ("comments",),
        "grammar-1",
        installed_python[1].read,
        lambda _: None,
    )
    unrelated = [replace(definition(), language="Unrelated", suffixes=(".other",))]

    def selected(path, registry):
        return (
            (unrelated[0], fixture_binding)
            if path.suffix == ".other"
            else (definition(), fixture_binding)
        )

    monkeypatch.setattr(flow_context, "reader_for", selected)
    monkeypatch.setattr(flow_context, "PLACEMENT_REVISION", "placement-1")
    for name in ("a.py", "b.py"):
        (tmp_path / name).write_bytes(b"x = 1\n# old\ny = 2\n")
    gathered = gather(
        tmp_path,
        [tmp_path / "a.py", tmp_path / "b.py"],
        0,
        settings={tmp_path / "a.py": {"mode": "wide"}, tmp_path / "b.py": {}},
    )
    assert not gathered.unreadable
    expected = {
        name: {
            "format": 1,
            "language": "Invented",
            "reader": "invented-reader",
            "compatibility": (
                "cefc5dc0563af6a3a811daa0bd6e7babbd224ca9ee1a3150c97e81adfc9be1fa"
            ),
            "settings": {"mode": "wide" if name == "a.py" else ""},
        }
        for name in ("a.py", "b.py")
    }
    binder = tmp_path / "binder.json"
    binder.write_text(json.dumps(gathered.binder.serialize()), encoding="utf-8")
    assert {
        p["path"]: p["reading"] for p in json.loads(binder.read_text())["pages"]
    } == expected
    unrelated[0] = replace(unrelated[0], revision="unrelated-new", rules={})
    copy = tmp_path / "copy.json"
    code, out = run_command(
        monkeypatch,
        capsys,
        distribute,
        "--seed",
        "--binder",
        str(binder),
        "--role",
        "block-context",
        "--out",
        str(copy),
        with_stderr=True,
    )
    assert code == 0, out
    for name in ("a.py", "b.py"):
        code, out = run_command(
            monkeypatch,
            capsys,
            mark,
            "--edit-copy",
            str(copy),
            "--repo",
            str(tmp_path),
            "--address",
            f"{name}@b1",
            "--instruction",
            "patch",
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
    docket = tmp_path / "docket.json"
    code, out = run_command(
        monkeypatch,
        capsys,
        proof,
        "--copy",
        str(copy),
        "--repo",
        str(tmp_path),
        "--to-docket",
        str(docket),
        with_stderr=True,
    )
    assert code == 0, out
    assert {
        p["path"]: p["reading"] for p in json.loads(docket.read_text())["pages"]
    } == expected
    revise = tmp_path.parent / (tmp_path.name + "-revise")
    code, out = run_command(
        monkeypatch,
        capsys,
        proof,
        "--from-docket",
        str(docket),
        "--repo",
        str(tmp_path),
        "--out",
        str(revise),
        with_stderr=True,
    )
    assert code == 0, out
    for name in ("a.py", "b.py"):
        assert (revise / name).read_bytes() == b"x = 1\n# new\ny = 2\n"
        assert (tmp_path / name).read_bytes() == b"x = 1\n# old\ny = 2\n"


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
    code, out = run_command(
        monkeypatch,
        capsys,
        proof,
        "--proof",
        str(tmp_path / "final.json"),
        "--repo",
        str(root),
        "--to-docket",
        str(docket),
        with_stderr=True,
    )
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
        "--out",
        str(tmp_path / "chief.json"),
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
    code, out = run_command(
        monkeypatch,
        capsys,
        proof,
        "--proof",
        str(tmp_path / "final.json"),
        "--repo",
        str(tmp_path / "repo"),
        "--to-docket",
        str(docket),
        with_stderr=True,
    )
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
@pytest.mark.parametrize("fault", ["compatible", "revision", "missing", "future"])
def test_direct_distribution_admits_context_before_saved_rows(
    tmp_path, monkeypatch, route, fault
):
    from comment_review.binder.binder import Binder
    from comment_review.exceptions import Refused
    from comment_review.flows import distribute

    path = tmp_path / "m.py"
    path.write_bytes(b"x = 1\n# old\ny = 2\n")
    binder = gather(tmp_path, [path], 0).binder
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
    if fault == "revision":
        monkeypatch.setattr(flow_context, "PLACEMENT_REVISION", "changed")

        def forbidden(*args, **kwargs):
            pytest.fail("incompatible in-memory binder reached saved rows")

        monkeypatch.setattr(distribute, "handed", forbidden)

    def operation():
        return (
            distribute.seed(binder, "block-context")
            if route == "seed"
            else distribute.assigned_binder(binder)
        )

    if fault == "revision":
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

    from conftest import run_command

    from comment_review.commands import collate, distribute, mark, proof

    root = tmp_path / "repo"
    root.mkdir()
    sources = {"m.py": b"x = 1\n# old\ny = 2\n", "n.js": b""}
    for name, raw in sources.items():
        (root / name).write_bytes(raw)
    gathered = gather(root, [root / name for name in sources], 0)
    assert not gathered.unreadable
    binder_path = tmp_path / "binder.json"
    binder_path.write_text(json.dumps(gathered.binder.serialize()), encoding="utf-8")
    wire = json.loads(binder_path.read_text(encoding="utf-8"))
    expected = {page["path"]: page["reading"] for page in wire["pages"]}
    assert expected["m.py"]["reader"] == "python-lexical"
    assert expected["n.js"] == {
        "format": 1,
        "language": "javascript",
        "reader": "javascript-lexical",
        "compatibility": (
            "ca68b8bee741bc94a7629874506b42b096c71332998219de636d73d1438f9f61"
        ),
        "settings": {},
    }
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
        assert next(s for s in wire["sheets"] if s["path"] == "n.js")["marks"] == []
        copies += ["--edit-copy", str(copy)]
    proof_path = tmp_path / "proof.json"
    code, out = run_command(
        monkeypatch,
        capsys,
        collate,
        "--stage",
        "4c",
        "--binder",
        str(binder_path),
        "--out",
        str(tmp_path / "chief.json"),
        "--proof-out",
        str(proof_path),
        *copies,
        with_stderr=True,
    )
    assert code == 0, out
    saved_proof = json.loads(proof_path.read_text(encoding="utf-8"))
    assert saved_proof["page_readings"] == expected
    docket_path = tmp_path / "docket.json"
    if changed:
        monkeypatch.setattr(flow_context, "PLACEMENT_REVISION", "changed")
        before = {
            path: path.read_bytes() for path in tmp_path.rglob("*") if path.is_file()
        }

        def forbidden(*args, **kwargs):
            pytest.fail("saved proof context refusal reached address transcription")

        monkeypatch.setattr("comment_review.flows.transcribe._unclosed", forbidden)
    code, out = run_command(
        monkeypatch,
        capsys,
        proof,
        "--proof",
        str(proof_path),
        "--repo",
        str(root),
        "--to-docket",
        str(docket_path),
        with_stderr=True,
    )
    if changed:
        assert code == 1, out
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

# What `context_for(Path("m.rs"), {})` returned at bc7096b8^, when `.rs` was a
# generic lexical row: reader `rust-lexical` revision 1, no grammar identity.
GENERIC_RUST_COMPATIBILITY = (
    "1bd8eac8d94fc381df1d21657ba156d8629407464331d63d8be9f0df8321d483"
)


def rust_context(**changes: str) -> ReadingContext:
    """The installed Rust context, re-resolved with definition fields changed."""
    from comment_review.reading.readers import ReaderBinding, reader_for

    registry = flow_context.installed_registry()
    assert not isinstance(registry, ReadFailure)
    selected = reader_for(Path("m.rs"), registry)
    assert isinstance(selected, tuple)
    rust, binding = selected
    assert isinstance(rust, LanguageDefinition)
    assert isinstance(binding, ReaderBinding)
    resolved = context_module.resolve_context(
        replace(rust, **changes),
        {},
        reader_revision=binding.revision,
        placement_revision=flow_context.PLACEMENT_REVISION,
        grammar_identity=binding.grammar_identity,
        digest=lambda data: sha256(data).hexdigest(),
    )
    assert isinstance(resolved, ReadingContext)
    return resolved


def rust_page(saved: ReadingContext):
    """`page_of` over the Rust source with a supplied saved context."""
    from comment_review.flows import page_for
    from comment_review.machine.repo import Source

    text = RUST_SOURCE.decode()
    return page_for.page_of(
        Path("m.rs"), source=Source(text, "sha"), reading_context=saved
    )


@pytest.mark.parametrize("saved", ["revision-1", "generic-lexical"])
def test_rust_context_from_before_the_rust_reader_is_refused(monkeypatch, saved):
    current = flow_context.context_for(Path("m.rs"), {})
    assert isinstance(current, ReadingContext)
    assert current == rust_context()
    old = (
        rust_context(revision="1")
        if saved == "revision-1"
        else ReadingContext("rust", "rust-lexical", GENERIC_RUST_COMPATIBILITY, ())
    )
    assert old != current
    from comment_review.binder import page as page_model

    monkeypatch.setattr(
        page_model,
        "read_source",
        lambda *_, **__: pytest.fail("refused context reached source recognition"),
    )
    failed = rust_page(old)
    assert isinstance(failed, ReadFailure)
    assert [d.code for d in failed.diagnostics] == ["reading-context-mismatch"]
    pages = [{"path": "m.rs", "reading": context_to_wire(old)}]
    admitted, problems = flow_context.page_reading_contexts(pages)
    assert admitted == {}
    assert problems and all("regather" in problem for problem in problems)


def test_rust_context_gathered_now_is_admitted(tmp_path):
    path = tmp_path / "m.rs"
    path.write_bytes(RUST_SOURCE)
    gathered = gather(tmp_path, [path], 0)
    assert not gathered.unreadable
    current = gathered.reading_contexts[path]
    assert current == rust_context()
    page = rust_page(current)
    assert not isinstance(page, ReadFailure)
    assert page.reading == current
    admitted, problems = flow_context.binder_reading_contexts(gathered.binder)
    assert problems == []
    assert admitted == {"m.rs": current}


def test_saved_rust_workflow_keeps_context_through_the_draft(
    tmp_path, monkeypatch, capsys
):
    import json

    from conftest import run_command

    from comment_review.commands import check, collate, distribute, mark, proof

    root = tmp_path / "repo"
    root.mkdir()
    (root / "m.rs").write_bytes(RUST_SOURCE)
    gathered = gather(root, [root / "m.rs"], 0)
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
            "--address",
            "m.rs@a1",
            "--instruction",
            "clean",
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
        copies += ["--edit-copy", str(copy)]
    proof_path = tmp_path / "proof.json"
    code, out = run_command(
        monkeypatch,
        capsys,
        collate,
        "--stage",
        "4c",
        "--binder",
        str(binder_path),
        "--out",
        str(tmp_path / "chief.json"),
        "--proof-out",
        str(proof_path),
        *copies,
        with_stderr=True,
    )
    assert code == 0, out
    saved_proof = json.loads(proof_path.read_text(encoding="utf-8"))
    assert saved_proof["page_readings"] == {"m.rs": expected}
    docket_path = tmp_path / "docket.json"
    code, out = run_command(
        monkeypatch,
        capsys,
        proof,
        "--proof",
        str(proof_path),
        "--repo",
        str(root),
        "--to-docket",
        str(docket_path),
        with_stderr=True,
    )
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


def test_saved_rust_binder_from_before_the_rust_reader_refuses_distribution(
    tmp_path, monkeypatch, capsys
):
    import json

    from conftest import run_command

    from comment_review.commands import distribute

    (tmp_path / "m.rs").write_bytes(RUST_SOURCE)
    wire = gather(tmp_path, [tmp_path / "m.rs"], 0).binder.serialize()
    wire["pages"][0]["reading"] = context_to_wire(rust_context(revision="1"))
    binder_path = tmp_path / "binder.json"
    binder_path.write_text(json.dumps(wire), encoding="utf-8")
    copy = tmp_path / "copy.json"
    code, out = run_command(
        monkeypatch,
        capsys,
        distribute,
        "--seed",
        "--binder",
        str(binder_path),
        "--role",
        "block-context",
        "--out",
        str(copy),
        with_stderr=True,
    )
    assert code != 0, out
    assert "regather" in out
    assert not copy.exists()


def test_chief_extra_destination_carries_original_context_and_sha():
    from comment_review.desk.proof.place import Place
    from comment_review.desk.proof.state import State
    from comment_review.flows.places import chief_copy_of

    original = ReadingContext("python", "lexical", "a" * 64, ())
    place = Place("extra.py@b1", "x = 1", "old", text="new", state=State.STANDS)
    chief = chief_copy_of(
        {place.address: place},
        "copy-chief",
        {},
        [],
        {"extra.py": original},
        {"extra.py": "original-sha"},
    )
    assert chief.sheets[0].reading is original
    assert chief.sheets[0].sha == "original-sha"
    assert chief.sheets[0].serialize()["reading"] == {
        "format": 1,
        "language": "python",
        "reader": "lexical",
        "compatibility": "a" * 64,
        "settings": {},
    }


def test_proof_transcription_admits_extra_context_before_saved_places(
    monkeypatch, tmp_path
):
    from comment_review.desk.proof.master_proof import MasterProof
    from comment_review.flows import transcribe

    saved = flow_context.context_for(Path("extra.py"), {})
    assert isinstance(saved, ReadingContext)
    proof = MasterProof(
        "4c",
        {},
        (),
        {"extra.py": replace(saved, compatibility="0" * 64)},
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

    saved = ReadingContext("python", "lexical", "a" * 64, (("flavor", "original"),))
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
        "reading": {
            "format": 1,
            "language": "python",
            "reader": "lexical",
            "compatibility": "a" * 64,
            "settings": {},
        },
    }
    second = {
        **first,
        "sha": "different",
        "reading": {**first["reading"], "compatibility": "b" * 64},
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

    (tmp_path / "extra.py").write_text("# old\nx = 1\n", encoding="utf-8")
    (tmp_path / "other.js").write_text("// old\nconst x = 1;\n", encoding="utf-8")
    page = page_of(tmp_path / "extra.py", rel="extra.py")
    other = page_of(tmp_path / "other.js", rel="other.js")
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


@pytest.mark.parametrize(
    "fault", ["compatible", "digest", "settings", "malformed", "duplicate"]
)
def test_direct_copy_metadata_is_admitted_without_trusting_annotations(fault):
    from comment_review.desk.proof.edit_copy import EditCopy
    from comment_review.desk.proof.sheet import Sheet

    saved = flow_context.context_for(Path("m.py"), {})
    assert isinstance(saved, ReadingContext)
    if fault == "digest":
        saved = replace(saved, compatibility="0" * 64)
    elif fault == "settings":
        saved = replace(saved, settings=(("unknown", "on"),))
    elif fault == "duplicate":
        object.__setattr__(saved, "settings", (("a", "on"), ("a", "off")))
    sheet = Sheet("m.py", "unchanged-sha", (), saved)
    if fault == "malformed":
        object.__setattr__(sheet, "reading", [])
    copy = EditCopy("block-context", {"root": ".", "revise": 0}, (sheet,))
    before = repr(copy)
    problems = flow_context.copy_reading_problems(copy)
    if fault == "compatible":
        assert problems == []
    else:
        assert problems and "regather" in " ".join(problems)
        assert "block-context" in " ".join(problems)
    assert repr(copy) == before


def test_direct_context_duplicate_supported_settings_cannot_collapse(monkeypatch):
    from types import SimpleNamespace

    from comment_review.desk.proof.edit_copy import EditCopy
    from comment_review.desk.proof.sheet import Sheet

    binding = SimpleNamespace(revision="reader-1", grammar_identity="grammar-1")
    monkeypatch.setattr(
        flow_context, "reader_for", lambda _, registry: (definition(), binding)
    )
    saved = flow_context.context_for(Path("m.ix"), {"mode": "wide"})
    assert isinstance(saved, ReadingContext)
    object.__setattr__(saved, "settings", (("mode", ""), ("mode", "wide")))
    copy = EditCopy(
        "block-context", {"root": ".", "revise": 0}, (Sheet("m.ix", "sha", (), saved),)
    )
    before = repr(copy)
    assert "regather" in " ".join(flow_context.copy_reading_problems(copy))
    assert repr(copy) == before


def test_direct_proof_saved_context_is_admitted_against_installed_identity():
    from comment_review.desk.proof.master_proof import MasterProof

    saved = flow_context.context_for(Path("m.py"), {})
    assert isinstance(saved, ReadingContext)
    proof = MasterProof("4c", {}, (), {"m.py": saved}, page_shas={"m.py": "sha"})
    assert flow_context.proof_reading_problems(proof) == []
    proof.page_readings["m.py"] = replace(saved, compatibility="0" * 64)
    assert "regather" in " ".join(flow_context.proof_reading_problems(proof))


@pytest.mark.parametrize(
    "path, sha",
    [("m.py", None), ("m.py", ""), ("m.py", " "), ("m.py", 3), ("", "sha"), (7, "sha")],
)
def test_direct_extra_page_proof_refuses_invalid_sha_metadata(path, sha):
    from comment_review.desk.proof.master_proof import MasterProof

    saved = flow_context.context_for(Path("m.py"), {})
    assert isinstance(saved, ReadingContext)
    proof = MasterProof("4c", {}, (), {"m.py": saved}, page_shas={path: sha})
    problems = flow_context.proof_reading_problems(proof)
    assert any("page_shas" in reason and "regather" in reason for reason in problems)


def test_direct_proof_malformed_settings_returns_refusal_before_conversion():
    from comment_review.desk.proof.master_proof import MasterProof

    saved = flow_context.context_for(Path("m.py"), {})
    assert isinstance(saved, ReadingContext)
    object.__setattr__(saved, "settings", (("x",),))
    proof = MasterProof("4c", {}, (), {"m.py": saved}, page_shas={"m.py": "sha"})
    problems = flow_context.proof_reading_problems(proof)
    assert problems == ["master_proof: m.py: malformed reading context; regather"]


def definition() -> LanguageDefinition:
    return LanguageDefinition(
        "Invented",
        (".ix",),
        "invented-reader",
        "definition-1",
        ("comments",),
        {"mode": ""},
        {"mode": ("", "wide")},
        {"nested": {"tokens": ["\u03bb", True, 1]}},
    )


def resolve(settings):
    return context_module.resolve_context(
        definition(),
        settings,
        reader_revision="reader-1",
        placement_revision="placement-1",
        grammar_identity="grammar-1",
        digest=lambda data: sha256(data).hexdigest(),
    )


def test_resolve_explicit_default_and_independent_override():
    default = resolve({})
    override = resolve({"mode": "wide"})
    assert isinstance(default, ReadingContext)
    assert isinstance(override, ReadingContext)
    assert default.settings == (("mode", ""),)
    assert override.settings == (("mode", "wide"),)
    assert (
        default.compatibility
        == "cefc5dc0563af6a3a811daa0bd6e7babbd224ca9ee1a3150c97e81adfc9be1fa"
    )


@pytest.mark.parametrize(
    "settings",
    [[], {"unknown": "wide"}, {"mode": "bad"}, {"mode": 1}, {1: "wide"}, {"": ""}],
)
def test_resolve_rejects_malformed_or_unsupported_settings(settings):
    assert isinstance(resolve(settings), ReadFailure)


@pytest.mark.parametrize(
    "text",
    [
        "[]",
        "{",
        '{"x.py":{},"x.py":{}}',
        '{"x.py":{"mode":"a","mode":"a"}}',
        '{"/x.py":{}}',
        '{"C:x.py":{}}',
        '{"\\\\\\\\host\\\\x.py":{}}',
        '{"":{}}',
        '{".":{}}',
        '{"../x.py":{}}',
        '{"x.py":[]}',
        '{"x.py":{"mode":1}}',
        '{"x.py":{"":"a"}}',
        '{"x.py":{},"./x.py":{"mode":"a"}}',
    ],
)
def test_settings_json_refuses_bad_shapes_paths_and_duplicates(tmp_path, text):
    settings = tmp_path / "settings.json"
    settings.write_text(text, encoding="utf-8")
    loaded, problems = flow_context.load_settings(settings, tmp_path)
    assert loaded == {}
    assert problems and str(settings) in problems[0]


def test_settings_normalize_without_discovering_source(tmp_path, monkeypatch):
    from comment_review.reading.readers import ReaderBinding

    binding = ReaderBinding(
        "invented-reader",
        "reader-1",
        ("comments",),
        "grammar-1",
        lambda *_: LexicalRead([], [], False, False),
        lambda _: None,
    )
    monkeypatch.setattr(
        flow_context, "reader_for", lambda _, registry: (definition(), binding)
    )
    settings = tmp_path / "settings.json"
    settings.write_text(
        '{"dir/../x.ix":{"mode":"wide"},"./x.ix":{"mode":"wide"},"other\\\\y.ix":{}}',
        encoding="utf-8",
    )
    loaded, problems = flow_context.load_settings(settings, tmp_path)
    assert problems == []
    assert loaded == {
        tmp_path / "x.ix": {"mode": "wide"},
        tmp_path / "other" / "y.ix": {},
    }
    assert not (tmp_path / "x.ix").exists()


def test_unused_json_entry_is_validated_without_source_acquisition(
    tmp_path, monkeypatch
):
    import importlib

    source = importlib.import_module("comment_review.flows.source")

    def forbidden(_):
        pytest.fail("settings loader acquired source")

    monkeypatch.setattr(source, "source_of", forbidden)
    settings = tmp_path / "settings.json"
    settings.write_text('{"missing.py":{"invented":"yes"}}', encoding="utf-8")
    loaded, problems = flow_context.load_settings(settings, tmp_path)
    assert loaded == {}
    assert problems and "missing.py" in problems[0] and "unknown setting" in problems[0]
    settings.write_text('{"missing.py":{}}', encoding="utf-8")
    assert flow_context.load_settings(settings, tmp_path) == (
        {tmp_path / "missing.py": {}},
        [],
    )
    assert not (tmp_path / "missing.py").exists()


def test_mixed_contexts_derive_independent_installed_binding_metadata(monkeypatch):
    from comment_review.reading.readers import ReaderBinding

    binding = ReaderBinding(
        "invented-reader",
        "reader-1",
        ("comments",),
        "grammar-1",
        lambda *_: LexicalRead([], [], False, False),
        lambda _: None,
    )
    monkeypatch.setattr(
        flow_context, "reader_for", lambda _, registry: (definition(), binding)
    )
    first = flow_context.context_for(Path("a.ix"), {})
    second = flow_context.context_for(Path("b.ix"), {"mode": "wide"})
    assert isinstance(first, ReadingContext)
    assert isinstance(second, ReadingContext)
    assert first.settings == (("mode", ""),)
    assert second.settings == (("mode", "wide"),)
    assert first.compatibility == second.compatibility
    assert flow_context.reading_problems(
        {Path("a.ix"): first}, {Path("a.ix"): second}
    ) == ["a.ix: reading context differs from saved context"]
    assert flow_context.reading_problems({Path("a.ix"): first}, {}) == [
        "a.ix: current reading context is missing"
    ]


def test_fresh_flows_reject_settings_before_source_acquisition(tmp_path, monkeypatch):
    import importlib

    gather_module = importlib.import_module("comment_review.flows.gather")
    compositor_module = importlib.import_module("comment_review.flows.compositor")
    path = tmp_path / "x.py"
    path.write_text("# prose\n", encoding="utf-8")

    def forbidden(_):
        pytest.fail("source acquired before unsupported setting refusal")

    monkeypatch.setattr(gather_module, "source_of", forbidden)
    monkeypatch.setattr(compositor_module, "source_of", forbidden)
    got = gather(tmp_path, [path], 0, settings={path: {"invented": "yes"}})
    assert got.unreadable and "unknown setting" in got.unreadable[0]
    assert isinstance(round_trip(path, settings={"invented": "yes"}), ReadFailure)


@pytest.mark.parametrize("command", ["gather", "compositor", "prove_unchanged"])
def test_cli_settings_reach_actual_fresh_flow(tmp_path, monkeypatch, capsys, command):
    import importlib
    import sys

    module = importlib.import_module(f"comment_review.commands.{command}")
    path = tmp_path / "x.py"
    path.write_text("# prose\n", encoding="utf-8")
    settings = tmp_path / "settings.json"
    settings.write_text('{"./x.py":{"invented":"yes"}}', encoding="utf-8")
    argv = [
        command,
        str(path),
        "--repo",
        str(tmp_path),
        "--reading-settings",
        str(settings),
    ]
    if command == "prove_unchanged":
        argv += ["--base", "HEAD"]
    monkeypatch.setattr(sys, "argv", argv)
    assert module.main() == 2
    captured = capsys.readouterr()
    assert "unknown setting 'invented'" in captured.out + captured.err
    settings.write_text('{"x.py":{},"x.py":{}}', encoding="utf-8")
    assert module.main() == 2
    captured = capsys.readouterr()
    assert "duplicate raw key" in captured.out + captured.err
    from comment_review.reading.readers import ReaderBinding

    binding = ReaderBinding(
        "invented-reader",
        "reader-1",
        ("comments",),
        "grammar-1",
        lambda *_: LexicalRead([], [], False, False),
        lambda _: None,
    )
    monkeypatch.setattr(
        flow_context, "reader_for", lambda _, registry: (definition(), binding)
    )
    entry = {"gather": "gather", "compositor": "round_trip", "prove_unchanged": "run"}[
        command
    ]
    actual = getattr(module, entry)
    received = []

    def capture(*args, **kwargs):
        received.append(kwargs["settings"])
        return actual(*args, **kwargs)

    monkeypatch.setattr(module, entry, capture)
    settings.write_text('{"x.py":{"mode":"wide"}}', encoding="utf-8")
    assert module.main() == (1 if command == "prove_unchanged" else 0)
    assert received == (
        [{"mode": "wide"}] if command == "compositor" else [{path: {"mode": "wide"}}]
    )


def test_default_contexts_are_retained_in_fresh_results(tmp_path):
    path = tmp_path / "x.py"
    path.write_text("# prose\n", encoding="utf-8")
    gathering = gather(tmp_path, [path], 0)
    assert gathering.reading_contexts[path].language == "python"
    result = round_trip(path)
    assert not isinstance(result, ReadFailure)
    assert isinstance(result.reading_context, ReadingContext)
    assert result.reading_context.settings == ()


def identity(value: LanguageDefinition, **revisions: str) -> str:
    return context_module.compatibility_identity(
        value,
        reader_revision=revisions.get("reader_revision", "reader-1"),
        placement_revision=revisions.get("placement_revision", "placement-1"),
        grammar_identity=revisions.get("grammar_identity", "grammar-1"),
        digest=lambda data: sha256(data).hexdigest(),
    )


def test_compatibility_has_independent_canonical_digest():
    canonical = (
        '{"definition":{"capabilities":["comments"],'
        '"choices":{"mode":["","wide"]},"defaults":{"mode":""},'
        '"language":"Invented","reader":"invented-reader",'
        '"revision":"definition-1","rules":{"nested":{"tokens":["\u03bb",true,1]}},'
        '"suffixes":[".ix"]},"grammar_identity":"grammar-1",'
        '"placement_revision":"placement-1","reader_revision":"reader-1"}'
    )
    expected = "cefc5dc0563af6a3a811daa0bd6e7babbd224ca9ee1a3150c97e81adfc9be1fa"
    assert sha256(canonical.encode("utf-8")).hexdigest() == expected
    assert identity(definition()) == expected


@pytest.mark.parametrize(
    "change",
    [
        {"language": "Other"},
        {"reader": "other-reader"},
        {"revision": "definition-2"},
        {"suffixes": (".other",)},
        {"capabilities": ("strings",)},
        {"defaults": {"mode": "wide"}},
        {"choices": {"mode": ("wide", "")}},
        {"choices": {"mode": ("", "wide", "extra")}},
        {"rules": {"nested": {"tokens": [1, True, "\u03bb"]}}},
        {"rules": {"nested": {"tokens": ["\u03bb", False, 1]}}},
        {"rules": {"nested": {"tokens": ["\u03bb", 1, 1]}}},
        {"rules": {"nested": {"tokens": ["\u03bb", True, "1"]}}},
    ],
)
def test_complete_definition_changes_invalidate_identity(change):
    original = definition()
    assert identity(replace(original, **change)) != identity(original)


@pytest.mark.parametrize(
    "field",
    [
        "reader_revision",
        "placement_revision",
        "grammar_identity",
    ],
)
def test_runtime_revisions_invalidate_identity(field):
    assert identity(definition(), **{field: "changed"}) != identity(definition())


@pytest.mark.parametrize("field", ["reader_revision", "placement_revision"])
@pytest.mark.parametrize("invalid", ["", None, 1, True])
def test_required_runtime_revisions_are_validated(field, invalid):
    with pytest.raises(ValueError):
        identity(definition(), **{field: invalid})


def test_empty_grammar_identity_is_valid():
    assert len(identity(definition(), grammar_identity="")) == 64


@pytest.mark.parametrize("invalid", [None, 1, True, ()])
def test_grammar_identity_must_be_a_string(invalid):
    with pytest.raises(ValueError):
        identity(definition(), grammar_identity=invalid)


@pytest.mark.parametrize("field", ["suffixes", "capabilities"])
def test_definition_arrays_preserve_order(field):
    values = (".ix", ".other") if field == "suffixes" else ("comments", "strings")
    original = replace(definition(), **{field: values})
    reordered = replace(original, **{field: tuple(reversed(values))})
    assert identity(original) != identity(reordered)


def test_settings_table_key_order_is_insignificant():
    original = replace(
        definition(),
        defaults={"mode": "", "other": "on"},
        choices={"mode": ("", "wide"), "other": ("on", "off")},
    )
    reordered = replace(
        original,
        defaults={"other": "on", "mode": ""},
        choices={"other": ("on", "off"), "mode": ("", "wide")},
    )
    assert identity(original) == identity(reordered)


def test_mapping_order_and_equivalent_toml_layout_do_not_change_identity():
    header = """format = 1
language = "Invented"
suffixes = [".ix"]
reader = "invented-reader"
revision = "definition-1"
capabilities = ["comments"]
"""
    first = decode_definition(
        header
        + """defaults = { mode = "" }
choices = { mode = ["", "wide"] }
rules = { z = {}, nested = { tokens = ["\u03bb", true, 1], a = "" } }
"""
    )
    second = decode_definition(
        header
        + """# Different layout and table ordering.
[rules.nested]
a = ""
tokens = ["\u03bb", true, 1]
[rules.z]
[choices]
mode = ["", "wide"]
[defaults]
mode = ""
"""
    )
    assert isinstance(first, LanguageDefinition)
    assert isinstance(second, LanguageDefinition)
    assert identity(first) == identity(second)


def test_compatibility_accepts_only_definition_and_relevant_revisions():
    assert tuple(signature(context_module.compatibility_identity).parameters) == (
        "definition",
        "reader_revision",
        "placement_revision",
        "grammar_identity",
        "digest",
    )
    original = definition()
    before = identity(original)
    unrelated = replace(original, language="Other", suffixes=(".other",))
    registry = LanguageRegistry((original, unrelated))
    selected = registry.for_language("Invented")
    assert isinstance(selected, LanguageDefinition)
    assert identity(selected) == before


def test_effective_settings_invalidate_context_with_same_derived_digest():
    digest = identity(definition())
    saved = ReadingContext("Invented", "invented-reader", digest, (("mode", ""),))
    current = replace(saved, settings=(("mode", "wide"),))
    assert not compatible_contexts(saved, current)


def test_exact_context_equality():
    saved = ReadingContext("invented", "reader-one", "a1" * 32, (("mode", "on"),))
    current = ReadingContext("invented", "reader-one", "a1" * 32, (("mode", "on"),))
    assert saved == current
    assert compatible_contexts(saved, current)


@pytest.mark.parametrize(
    "language,reader,digest,settings",
    [
        ("other", "reader-one", "a1" * 32, (("mode", "on"),)),
        ("invented", "reader-two", "a1" * 32, (("mode", "on"),)),
        ("invented", "reader-one", "b2" * 32, (("mode", "on"),)),
        ("invented", "reader-one", "a1" * 32, (("mode", "off"),)),
        ("invented", "reader-one", "a1" * 32, ()),
    ],
)
def test_each_context_field_must_match(language, reader, digest, settings):
    saved = ReadingContext("invented", "reader-one", "a1" * 32, (("mode", "on"),))
    current = ReadingContext(language, reader, digest, settings)
    assert not compatible_contexts(saved, current)
    assert not compatible_contexts(current, saved)


def test_settings_are_sorted_and_empty_values_are_preserved():
    saved = ReadingContext(
        "invented", "reader-one", "a1" * 32, (("z", "yes"), ("a", ""))
    )
    assert saved.settings == (("a", ""), ("z", "yes"))
    current = ReadingContext(
        "invented", "reader-one", "a1" * 32, (("a", ""), ("z", "yes"))
    )
    assert compatible_contexts(saved, current)


def test_empty_settings_are_valid():
    context = ReadingContext("invented", "reader-one", "0" * 64, ())
    assert context.settings == ()


@pytest.mark.parametrize("field", ["language", "reader"])
@pytest.mark.parametrize("invalid", ["", None, 1, True, [], (), {}])
def test_invalid_identity_is_rejected(field, invalid):
    values: dict[str, Any] = {
        "language": "invented",
        "reader": "reader-one",
        "compatibility": "a1" * 32,
        "settings": (),
    }
    values[field] = invalid
    with pytest.raises(ValueError):
        ReadingContext(**values)


@pytest.mark.parametrize(
    "invalid",
    [
        None,
        1,
        True,
        [],
        (),
        "",
        "a" * 63,
        "a" * 65,
        "A" * 64,
        "g" * 64,
        "a" * 64 + "\n",
        " " + "a" * 63,
    ],
)
def test_invalid_digest_is_rejected(invalid):
    with pytest.raises(ValueError):
        ReadingContext("invented", "reader-one", invalid, ())


@pytest.mark.parametrize(
    "invalid",
    [
        None,
        "mode",
        1,
        True,
        [],
        {},
        [("mode", "on")],
        ("mode",),
        (["mode", "on"],),
        (None,),
        ((),),
        (("mode",),),
        (("mode", "on", "extra"),),
        (("", "on"),),
        ((None, "on"),),
        ((1, "on"),),
        ((True, "on"),),
        (([], "on"),),
        (("mode", None),),
        (("mode", 1),),
        (("mode", True),),
        (("mode", []),),
        (("mode", {}),),
        (("mode", "on"), ("mode", "off")),
        (("mode", "on"), ("mode", "on")),
    ],
)
def test_invalid_settings_are_rejected(invalid):
    with pytest.raises(ValueError):
        ReadingContext("invented", "reader-one", "a1" * 32, invalid)


@pytest.mark.parametrize("field", ["language", "reader", "compatibility", "settings"])
def test_context_fields_cannot_be_reassigned(field):
    context = ReadingContext("invented", "reader-one", "a1" * 32, (("mode", "on"),))
    with pytest.raises(FrozenInstanceError):
        setattr(context, field, "replacement")


def test_nested_settings_cannot_be_mutated():
    context = ReadingContext("invented", "reader-one", "a1" * 32, (("mode", "on"),))
    with pytest.raises(TypeError):
        context.settings[0][1] = "off"  # ty: ignore[invalid-assignment]


def wire_context() -> dict[str, Any]:
    return {
        "format": 1,
        "language": "uninstalled-language",
        "reader": "uninstalled-reader",
        "compatibility": "ab" * 32,
        "settings": {"z": "on", "a": ""},
    }


def test_context_wire_decodes_literal_and_normalizes_settings():
    from comment_review.reading.context_io import context_from_wire

    decoded, problems = context_from_wire("input.json:context", wire_context())
    assert problems == []
    assert decoded == ReadingContext(
        "uninstalled-language",
        "uninstalled-reader",
        "ab" * 32,
        (("a", ""), ("z", "on")),
    )


def test_context_wire_serialization_is_exact_detached_and_round_trips():
    from comment_review.reading.context_io import context_from_wire, context_to_wire

    context = ReadingContext(
        "uninstalled-language",
        "uninstalled-reader",
        "ab" * 32,
        (("z", "on"), ("a", "")),
    )
    encoded = context_to_wire(context)
    assert encoded == wire_context()
    assert list(encoded["settings"]) == ["a", "z"]
    assert context_from_wire("context", encoded) == (context, [])
    again = context_to_wire(context)
    assert again is not encoded
    assert again["settings"] is not encoded["settings"]
    encoded["settings"]["a"] = "changed"
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


@pytest.mark.parametrize("key", ["extra", 1, None])
def test_context_wire_rejects_unknown_keys(key):
    from comment_review.reading.context_io import context_from_wire

    value = wire_context()
    value[key] = "extra"
    decoded, problems = context_from_wire("wire", value)
    assert decoded is None
    assert "wire" in problems[0]


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
        ("compatibility", ""),
        ("compatibility", "A" * 64),
        ("compatibility", "a" * 63),
        ("compatibility", "g" * 64),
        ("compatibility", None),
        ("compatibility", 1),
        ("settings", None),
        ("settings", []),
        ("settings", (("a", "on"),)),
        ("settings", {"": "on"}),
        ("settings", {1: "on"}),
        ("settings", {None: "on"}),
        ("settings", {"a": None}),
        ("settings", {"a": 1}),
        ("settings", {"a": True}),
        ("settings", {"a": []}),
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


def test_context_wire_settings_order_is_insignificant_and_empty_settings_valid():
    from comment_review.reading.context_io import context_from_wire

    value = wire_context()
    reordered = {**value, "settings": {"a": "", "z": "on"}}
    assert context_from_wire("wire", value) == context_from_wire("wire", reordered)
    empty, problems = context_from_wire("wire", {**value, "settings": {}})
    assert problems == []
    assert isinstance(empty, ReadingContext)
    assert empty.settings == ()


def test_context_wire_requires_exact_dictionary_types():
    from comment_review.reading.context_io import context_from_wire

    class DictionarySubclass(dict):
        pass

    for value in (
        DictionarySubclass(wire_context()),
        {**wire_context(), "settings": DictionarySubclass(a="on")},
    ):
        decoded, problems = context_from_wire("wire", value)
        assert decoded is None
        assert "wire" in problems[0]


def test_context_wire_unexpected_constructor_defects_propagate(monkeypatch):
    from comment_review.reading import context_io

    def broken_context(*args):
        raise RuntimeError("unexpected defect")

    monkeypatch.setattr(context_io, "ReadingContext", broken_context)
    with pytest.raises(RuntimeError, match="unexpected defect"):
        context_io.context_from_wire("wire", wire_context())
