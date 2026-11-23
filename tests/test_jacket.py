"""`flows/jacket.py`: the run's record, its wire pair, and the manuscript.

The expectations are the plan's own (`docs/plans/0.2.4-the-run-has-a-jacket.md`
P2): the jacket holds the pre-edit ref, the scope, the topology rows verbatim and,
per stage, a root relative to the jacket file, a binder, the dispatched copies and
the closed proof with its sha256 -- and `topology --build --run` writes the rows.
"""

import json
import subprocess
from pathlib import Path

import pytest
from conftest import run_command
from helpers import a_binder_over

from comment_review.commands import topology as topology_command
from comment_review.desk.topology import read
from comment_review.flows.jacket import (
    JACKET_FILE,
    MANUSCRIPT,
    Closed,
    Jacket,
    StageEntry,
    jacket_from_wire,
    jacket_to_wire,
    load_jacket,
    resolved_path,
    save_jacket,
    snapshot_manuscript,
    stored_path,
)

TOPOLOGY = (
    '[[stage]]\nname = "4a"\nkind = "editorial"\nreads = "original"\n'
    '  [[stage.dispatch]]\n  role = "ownership-context"\n'
)

A_SHA = "a" * 64


def _jacket() -> Jacket:
    return Jacket(
        ref="0123abc",
        scope=("pkg", "README.md"),
        topology=TOPOLOGY,
        stages={
            "4a": StageEntry(
                root="root4a",
                binder="binder4a.json",
                dispatched=("4a_ownership-context.json",),
                closed=Closed(proof="4a_proof1.json", sha256=A_SHA),
            )
        },
    )


def test_a_jacket_round_trips_through_its_wire_pair():
    wire = json.loads(json.dumps(jacket_to_wire(_jacket())))
    got, problems = jacket_from_wire("jacket.json", wire)
    assert problems == []
    assert got == _jacket()


def test_an_open_stage_round_trips_with_no_closed_proof():
    jacket = Jacket("0123abc", ("pkg",), TOPOLOGY, {"4a": StageEntry("r", "b", ())})
    got, problems = jacket_from_wire(
        "j", json.loads(json.dumps(jacket_to_wire(jacket)))
    )
    assert problems == [] and got == jacket


def _broken(edit) -> dict:
    wire = jacket_to_wire(_jacket())
    edit(wire)
    return wire


def _stage(wire: dict) -> dict:
    return wire["stages"]["4a"]


MALFORMED = {
    "not an object": lambda w: w.clear(),
    "format": lambda w: w.update(format=2),
    "unknown key": lambda w: w.update(extra=1),
    "ref missing": lambda w: w.pop("ref"),
    "ref empty": lambda w: w.update(ref=""),
    "scope not strings": lambda w: w.update(scope=["pkg", 3]),
    "scope escapes": lambda w: w.update(scope=["../other"]),
    "topology unreadable": lambda w: w.update(topology="not toml ["),
    "stages not an object": lambda w: w.update(stages=[]),
    "stage not a row": lambda w: w.update(stages={"9": _stage(w)}),
    "stage unknown key": lambda w: _stage(w).update(read={}),
    "root absolute": lambda w: _stage(w).update(root=str(Path.cwd().resolve())),
    "root not a string": lambda w: _stage(w).update(root=7),
    "binder not a string": lambda w: _stage(w).update(binder=None),
    "dispatched not strings": lambda w: _stage(w).update(dispatched="a.json"),
    "closed not an object": lambda w: _stage(w).update(closed="4a_proof1.json"),
    "closed proof missing": lambda w: _stage(w)["closed"].pop("proof"),
    "closed sha not a sha256": lambda w: _stage(w)["closed"].update(sha256="abc"),
}


@pytest.mark.parametrize("edit", MALFORMED.values(), ids=MALFORMED.keys())
def test_a_malformed_jacket_is_refused_with_a_reason(edit):
    got, problems = jacket_from_wire("jacket.json", _broken(edit))
    assert got is None
    assert problems and all(p.startswith("jacket.json") for p in problems)


def test_a_wire_that_is_not_an_object_is_refused():
    got, problems = jacket_from_wire("jacket.json", ["not", "a", "jacket"])
    assert got is None and problems


def test_a_jacket_saves_and_loads(tmp_path):
    path = tmp_path / JACKET_FILE
    save_jacket(path, _jacket())
    assert load_jacket(path) == (_jacket(), [])


def test_a_root_stored_relative_to_the_jacket_resolves_the_same_from_another_cwd(
    tmp_path, monkeypatch
):
    run = tmp_path / "work" / "run"
    root = run / "root4c"
    root.mkdir(parents=True)
    elsewhere = tmp_path / "elsewhere" / "deeper"
    elsewhere.mkdir(parents=True)

    monkeypatch.chdir(tmp_path / "work")
    stored = stored_path(Path("run/root4c"), Path("run") / JACKET_FILE)
    assert stored == "root4c"

    monkeypatch.chdir(elsewhere)
    jacket_file = Path("../../work/run") / JACKET_FILE
    assert resolved_path(stored, jacket_file) == root.resolve()


def test_a_root_outside_the_run_dir_is_stored_walking_up(tmp_path):
    (tmp_path / "run").mkdir()
    (tmp_path / "trees" / "root4c").mkdir(parents=True)
    jacket_file = tmp_path / "run" / JACKET_FILE
    stored = stored_path(tmp_path / "trees" / "root4c", jacket_file)
    assert stored == "../trees/root4c"
    assert (
        resolved_path(stored, jacket_file) == (tmp_path / "trees" / "root4c").resolve()
    )


FOUR = {f"{n}.py@a0": f"Doc for {n}." for n in "abcd"}


def _binder_file(tmp_path) -> Path:
    where = tmp_path / "binder.json"
    where.write_text(json.dumps(a_binder_over(FOUR).serialize()), encoding="utf-8")
    return where


def _repo(tmp_path) -> Path:
    """The test's checkout, made on first use."""
    repo = tmp_path / "repo"
    return repo if repo.exists() else _checkout(tmp_path)


def _head(repo: Path) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
    ).stdout.strip()


def _build_into_run(tmp_path, monkeypatch, capsys, *extra: str):
    return run_command(
        monkeypatch,
        capsys,
        topology_command,
        "--build",
        "--binder",
        str(_binder_file(tmp_path)),
        "--run",
        str(tmp_path / "run"),
        "--repo",
        str(_repo(tmp_path)),
        "--stage",
        "4a=ownership-context",
        "--stage",
        "4c=block-context/2,function-context,module-context",
        "--stage",
        "6=block-context",
        "--cap",
        "6=12",
        "--series",
        "6=b,c",
        "--admits",
        "6=patch,drop,add,clean,query",
        *extra,
        with_stderr=True,
    )


def test_topology_build_writes_every_row_into_the_jacket_including_compaction(
    tmp_path, monkeypatch, capsys
):
    out = tmp_path / "t.toml"
    code, printed = _build_into_run(
        tmp_path,
        monkeypatch,
        capsys,
        "--out",
        str(out),
        "--ref",
        "HEAD",
        "a.py",
        "b.py",
    )
    assert code == 0, printed

    jacket, problems = load_jacket(tmp_path / "run" / JACKET_FILE)
    assert problems == [] and jacket is not None
    assert jacket.scope == ("a.py", "b.py")
    assert jacket.stages == {}
    # Verbatim: the rows the jacket holds are the text `--out` wrote.
    assert jacket.topology == out.read_text(encoding="utf-8")

    stages, why = read(jacket.topology)
    assert why == ""
    assert [s.name for s in stages] == ["4a", "4c", "6"]
    compaction = stages[-1]
    assert compaction.reads == "revise:4c"
    assert compaction.cap == 12
    assert compaction.series == ("b", "c")
    assert compaction.admits == ("patch", "drop", "add", "clean", "query")
    assert [d.role for d in compaction.dispatches] == ["block-context"]

    again, _ = load_jacket(tmp_path / "run" / JACKET_FILE)
    assert again is not None and read(again.topology) == (stages, "")


def test_the_jacket_records_the_sha_a_ref_names_and_a_later_commit_moves_nothing(
    tmp_path, monkeypatch, capsys
):
    repo = _repo(tmp_path)
    before = _head(repo)
    code, printed = _build_into_run(
        tmp_path, monkeypatch, capsys, "--ref", "HEAD", "pkg"
    )
    assert code == 0, printed
    jacket, _ = load_jacket(tmp_path / "run" / JACKET_FILE)
    assert jacket is not None and jacket.ref == before and len(before) == 40

    _git(repo, "add", ".")
    _git(
        repo,
        "-c",
        "user.name=Test",
        "-c",
        "user.email=test@example.invalid",
        "commit",
        "-m",
        "later",
    )
    assert _head(repo) != before

    code, printed = _build_into_run(tmp_path, monkeypatch, capsys)
    assert code == 0, printed
    jacket, _ = load_jacket(tmp_path / "run" / JACKET_FILE)
    assert jacket is not None and jacket.ref == before

    # HEAD now names the later commit, which is not the run's.
    code, printed = _build_into_run(tmp_path, monkeypatch, capsys, "--ref", "HEAD")
    assert code == 2, printed
    assert before in printed


def test_a_ref_naming_no_commit_is_refused(tmp_path, monkeypatch, capsys):
    code, printed = _build_into_run(
        tmp_path, monkeypatch, capsys, "--ref", "no-such-branch", "pkg"
    )
    assert code == 2, printed
    assert "no-such-branch" in printed
    assert not (tmp_path / "run" / JACKET_FILE).exists()


def test_a_new_jacket_needs_the_pre_edit_ref_and_the_scope(
    tmp_path, monkeypatch, capsys
):
    code, printed = _build_into_run(tmp_path, monkeypatch, capsys, "a.py")
    assert code == 2, printed
    assert "pre-edit ref" in printed
    assert not (tmp_path / "run" / JACKET_FILE).exists()


def test_a_rebuild_keeps_the_ref_and_scope_already_recorded(
    tmp_path, monkeypatch, capsys
):
    first, printed = _build_into_run(
        tmp_path, monkeypatch, capsys, "--ref", "HEAD", "a.py"
    )
    assert first == 0, printed
    code, printed = _build_into_run(tmp_path, monkeypatch, capsys)
    assert code == 0, printed
    jacket, _ = load_jacket(tmp_path / "run" / JACKET_FILE)
    head = _head(_repo(tmp_path))
    assert jacket is not None and (jacket.ref, jacket.scope) == (head, ("a.py",))


def test_a_rebuild_after_a_stage_opened_is_refused(tmp_path, monkeypatch, capsys):
    run = tmp_path / "run"
    run.mkdir()
    opened = Jacket("0123abc", ("a.py",), TOPOLOGY, {"4a": StageEntry("r", "b", ())})
    save_jacket(run / JACKET_FILE, opened)
    code, printed = _build_into_run(tmp_path, monkeypatch, capsys)
    assert code == 2, printed
    assert "4a" in printed
    assert load_jacket(run / JACKET_FILE) == (opened, [])


def test_a_compaction_key_naming_no_stage_is_refused(tmp_path, monkeypatch, capsys):
    code, printed = _build_into_run(
        tmp_path, monkeypatch, capsys, "--cap", "9=3", "--ref", "HEAD", "a.py"
    )
    assert code == 2, printed
    assert "'9'" in printed


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, check=True, timeout=30
    )


def _checkout(tmp_path) -> Path:
    """A checkout holding, in and out of scope, tracked, untracked and ignored files."""
    repo = tmp_path / "repo"
    files = {
        "pkg/core.py": "x = 1\r\n",
        "pkg/sub/util.py": "y = 2\n",
        "other/tracked.py": "z = 3\n",
        ".gitignore": "*.log\n",
    }
    for rel, text in files.items():
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
        (repo / rel).write_bytes(text.encode("utf-8"))
    _git(repo, "init")
    _git(repo, "add", ".")
    _git(
        repo,
        "-c",
        "user.name=Test",
        "-c",
        "user.email=test@example.invalid",
        "commit",
        "-m",
        "fixture",
    )
    # After the commit: edited in scope, new in scope, new outside it, ignored.
    (repo / "pkg/core.py").write_bytes(b"x = 10\r\n")
    (repo / "pkg/new.py").write_bytes(b"n = 1\n")
    (repo / "notes/draft.md").parent.mkdir()
    (repo / "notes/draft.md").write_bytes(b"cite me\n")
    (repo / "pkg/run.log").write_bytes(b"ignored\n")
    (repo / "other/run.log").write_bytes(b"ignored\n")
    return repo


def test_the_manuscript_is_the_scope_and_the_untracked_files_as_they_stand(tmp_path):
    repo = _checkout(tmp_path)
    run = tmp_path / "run"
    copied, problems = snapshot_manuscript(repo, ("pkg",), run)
    assert problems == []
    manuscript = run / MANUSCRIPT
    on_disk = sorted(
        p.relative_to(manuscript).as_posix()
        for p in manuscript.rglob("*")
        if p.is_file()
    )
    # The scope as the checkout holds it -- the gather's walk, so an ignored file
    # under a scoped directory is in it -- and every untracked file outside the
    # scope; a tracked file outside the scope is not.
    expected = [
        "notes/draft.md",
        "pkg/core.py",
        "pkg/new.py",
        "pkg/run.log",
        "pkg/sub/util.py",
    ]
    assert on_disk == expected
    assert copied == expected
    assert (manuscript / "pkg/core.py").read_bytes() == b"x = 10\r\n"


def test_a_manuscript_already_on_disk_is_refused_and_left_alone(tmp_path):
    repo = _checkout(tmp_path)
    run = tmp_path / "run"
    (run / MANUSCRIPT).mkdir(parents=True)
    (run / MANUSCRIPT / "kept.txt").write_bytes(b"kept")
    copied, problems = snapshot_manuscript(repo, ("pkg",), run)
    assert copied == [] and problems
    assert [p.name for p in (run / MANUSCRIPT).iterdir()] == ["kept.txt"]


def test_a_scope_path_that_matches_nothing_is_refused(tmp_path):
    repo = _checkout(tmp_path)
    copied, problems = snapshot_manuscript(repo, ("nope",), tmp_path / "run")
    assert copied == [] and any("nope" in p for p in problems)
    assert not (tmp_path / "run" / MANUSCRIPT).exists()
