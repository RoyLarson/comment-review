"""Dealing one stage: one seeded copy per dispatch, in order, and `distribute --seed`.

`decision-log.md Process: #74`: the topology keeps a reader, and the reader is the
distribution -- one stage's dispatches, one seeded edit copy per dispatch, written
by `flows.fan_out.write_dealt`, which `stage open` calls.
"""

import json
from pathlib import Path

import pytest
from conftest import SAMPLE, build, run_command
from helpers import a_jacket_naming

from comment_review.binder.binder import bind
from comment_review.commands import check as check_command
from comment_review.commands import collate as collate_command
from comment_review.commands import distribute as distribute_command
from comment_review.commands import gather as gather_command
from comment_review.commands import topology as topology_command
from comment_review.desk.topology import read as read_topology
from comment_review.flows.distribute import IncompatibleBinder
from comment_review.flows.fan_out import (
    OverlappingShards,
    UncoveredPage,
    partition,
    write_dealt,
)
from comment_review.flows.proof_io import load_binder

DEAL_REFUSALS = (OverlappingShards, UncoveredPage, IncompatibleBinder)

FOUR_C = """
[[stage]]
name = "4a"
kind = "editorial"
reads = "original"
  [[stage.dispatch]]
  role = "ownership-context"

[[stage]]
name = "4c"
kind = "editorial"
reads = "revise:4a"
  [[stage.dispatch]]
  role = "block-context"
  paths = ["a.py"]
  [[stage.dispatch]]
  role = "block-context"
  paths = ["b.py"]
  [[stage.dispatch]]
  role = "function-context"
"""


@pytest.mark.parametrize("incompatible", [False, True])
def test_stage_admits_later_language_before_consuming_first_shard(
    tmp_path, monkeypatch, capsys, incompatible
):
    from comment_review.flows import reading_context
    from comment_review.reading.context import ReadingContext

    later = "b.rs"

    (tmp_path / "a.py").write_bytes(b"x = 1\n# first\ny = 2\n")
    (tmp_path / later).write_bytes(b"const x = 1;\n// later\nconst y = 2;\n")
    code, printed = run_command(
        monkeypatch,
        capsys,
        gather_command,
        "--repo",
        str(tmp_path),
        "--out",
        str(tmp_path / "binder.json"),
        str(tmp_path / "a.py"),
        str(tmp_path / later),
        with_stderr=True,
    )
    assert code == 0, printed
    (tmp_path / "t.toml").write_text(
        '[[stage]]\nname = "4a"\nkind = "editorial"\nreads = "original"\n'
        '[[stage.dispatch]]\nrole = "block-context"\npaths = ["a.py"]\n'
        f'[[stage.dispatch]]\nrole = "block-context"\npaths = ["{later}"]\n'
    )
    before = {path: path.read_bytes() for path in tmp_path.rglob("*") if path.is_file()}
    if incompatible:

        def changed(definition):
            reader = "rust-changed" if definition.language == "rust" else None
            return ReadingContext(definition.language, reader or definition.reader)

        monkeypatch.setattr(reading_context, "resolve_context", changed)

        def forbidden(*args, **kwargs):
            pytest.fail("first shard consumed before later language admission")

        monkeypatch.setattr("comment_review.flows.distribute.handed", forbidden)
    out = tmp_path / "copies"
    code, printed = _stage(tmp_path, "4a", out)
    if incompatible:
        assert code == 2, printed
        assert later in printed and "regather" in printed
        assert not out.exists()
        assert {
            path: path.read_bytes() for path in tmp_path.rglob("*") if path.is_file()
        } == before
    else:
        assert code == 0, printed
        assert [
            json.loads((out / f"4a_block-context_{n}.json").read_text())["sheets"][0][
                "path"
            ]
            for n in (1, 2)
        ] == ["a.py", later]


@pytest.mark.parametrize("route", ["seed", "stage"])
def test_distribution_refuses_installed_incompatible_saved_binder_before_addresses(
    tmp_path, monkeypatch, capsys, route
):
    from conftest import install_another_reader

    root = _tree(tmp_path, monkeypatch, capsys)
    before = {path: path.read_bytes() for path in root.rglob("*") if path.is_file()}
    install_another_reader(monkeypatch)

    def forbidden(*args, **kwargs):
        pytest.fail("incompatible binder reached saved address consumption")

    monkeypatch.setattr("comment_review.flows.distribute.handed", forbidden)
    if route == "seed":
        monkeypatch.setattr(distribute_command, "_as_json", forbidden)
        code, printed = run_command(
            monkeypatch,
            capsys,
            distribute_command,
            "--seed",
            "--binder",
            str(root / "binder.json"),
            "--role",
            "block-context",
            "--out",
            str(root / "seeded.json"),
            with_stderr=True,
        )
    else:
        code, printed = _stage(root, "4a", root / "copies")
    assert code == 2, printed
    assert "regather" in printed
    assert {
        path: path.read_bytes() for path in root.rglob("*") if path.is_file()
    } == before


def _bind(tmp_path, monkeypatch, capsys, repo: Path, out: Path):
    """One binder over `repo`'s two pages."""
    code, printed = run_command(
        monkeypatch,
        capsys,
        gather_command,
        "--repo",
        str(repo),
        "--out",
        str(out),
        str(repo / "a.py"),
        str(repo / "b.py"),
        with_stderr=True,
    )
    assert code == 0, printed


def _tree(tmp_path, monkeypatch, capsys) -> Path:
    """Two pages, a copy of them, a binder over each, and the topology above.

    The copy stands in for the tree `stage open` builds for `4c`, so the copies
    `4c` deals are cut from that tree's binder.
    """
    pulled = tmp_path / "revise"
    pulled.mkdir()
    for name in ("a.py", "b.py"):
        (tmp_path / name).write_text(SAMPLE, encoding="utf-8", newline="")
        (pulled / name).write_text(SAMPLE, encoding="utf-8", newline="")
    _bind(tmp_path, monkeypatch, capsys, tmp_path, tmp_path / "binder.json")
    _bind(tmp_path, monkeypatch, capsys, pulled, tmp_path / "revise-binder.json")
    (tmp_path / "t.toml").write_text(FOUR_C, encoding="utf-8")
    return tmp_path


def _stage(root: Path, stage: str, out: Path, binder: str = "") -> tuple[int, str]:
    """Deal `stage` of `root / "t.toml"` from the binder into `out`.

    Returns:
        `(0, the lines written)`, or `(2, the refusal)` -- the codes `stage
        open` exits with for a stage that deals or does not.
    """
    held, problems = load_binder(root / (binder or "binder.json"))
    if held is None:
        return 2, "\n".join(problems)
    stages, why = read_topology((root / "t.toml").read_text(encoding="utf-8"))
    assert why == "", why
    (row,) = [one for one in stages if one.name == stage]
    try:
        written = write_dealt(held, row, out)
    except DEAL_REFUSALS as refused:
        return 2, str(refused)
    return 0, "\n".join(line for _, line in written)


def _second(root: Path, out: Path) -> tuple[int, str]:
    """Stage `4c`, dealt from the binder over its own tree."""
    return _stage(root, "4c", out, binder="revise-binder.json")


def test_a_stage_seeds_one_copy_per_dispatch_in_dispatch_order(
    tmp_path, monkeypatch, capsys
):
    root = _tree(tmp_path, monkeypatch, capsys)
    out = root / "copies"
    code, printed = _second(root, out)
    assert code == 0, printed
    names = sorted(p.name for p in out.iterdir())
    assert names == [
        "4c_block-context_1.json",
        "4c_block-context_2.json",
        "4c_function-context_1.json",
        "binders",
    ]
    first = json.loads((out / "4c_block-context_1.json").read_text(encoding="utf-8"))
    assert [s["path"] for s in first["sheets"]] == ["a.py"]
    third = json.loads((out / "4c_function-context_1.json").read_text(encoding="utf-8"))
    assert [s["path"] for s in third["sheets"]] == ["a.py", "b.py"]


def test_each_dispatched_copy_has_its_received_binder(tmp_path, monkeypatch, capsys):
    root = _tree(tmp_path, monkeypatch, capsys)
    out = root / "copies"
    code, printed = _second(root, out)
    assert code == 0, printed
    for name, paths in (
        ("4c_block-context_1.json", ["a.py"]),
        ("4c_block-context_2.json", ["b.py"]),
        ("4c_function-context_1.json", ["a.py", "b.py"]),
    ):
        binder = json.loads((out / "binders" / name).read_text(encoding="utf-8"))
        assert [p["path"] for p in binder["pages"]] == paths
        assert Path(binder["read_from"]["root"]).resolve() == root / "revise"
        assert str(out / "binders" / name) in printed


def test_received_binder_contains_only_stage_assigned_places(
    tmp_path, monkeypatch, capsys
):
    root = _tree(tmp_path, monkeypatch, capsys)
    for name in ("a.py", "b.py"):
        (root / "revise" / name).write_text(
            "x = 0\n# long\n# paragraph\nx = 1\n# short\ndef f():\n"
            '    """Doc."""\n    pass\n',
            encoding="utf-8",
        )
    _bind(root, monkeypatch, capsys, root / "revise", root / "revise-binder.json")
    (root / "t.toml").write_text(
        FOUR_C.replace('name = "4c"', 'name = "4c"\nseries = ["b"]\ncap = 1'),
        encoding="utf-8",
    )
    out = root / "copies"
    code, printed = _second(root, out)
    assert code == 0, printed
    for copy_path in out.glob("*.json"):
        copy = json.loads(copy_path.read_text(encoding="utf-8"))
        binder = json.loads(
            (out / "binders" / copy_path.name).read_text(encoding="utf-8")
        )
        for page in binder["pages"]:
            assert [row["cue"] for row in page["rows"]] == ["b1"]
            assert page["rows"][0]["raw_text"] == "# long\n# paragraph"
        assert [page["path"] for page in binder["pages"]] == [
            sheet["path"] for sheet in copy["sheets"]
        ]


def test_an_uncovered_page_is_refused_with_fan_outs_own_reason(
    tmp_path, monkeypatch, capsys
):
    root = _tree(tmp_path, monkeypatch, capsys)
    (root / "t.toml").write_text(
        FOUR_C.replace('paths = ["b.py"]', 'paths = ["zzz.py"]'), encoding="utf-8"
    )
    code, printed = _second(root, root / "copies")
    assert code == 2
    assert "no dispatch covers" in printed and "b.py" in printed


def test_a_binder_with_no_freeform_path_deals_shards_with_none():
    binder = bind([build(SAMPLE, "a.py")], read_from={"root": "."})
    stage, _ = read_topology(FOUR_C)
    assert [free for _, _, free in partition(binder, stage[0])] == [[]]


def _freeform_run(root: Path, monkeypatch, capsys) -> tuple[Path, Path, Path]:
    """Gather two freeform files, build a topology over them, and deal it."""
    for name in ("a.js", "b.js"):
        (root / name).write_text("// one\n", encoding="utf-8")
    binder = root / "binder.json"
    code, printed = run_command(
        monkeypatch,
        capsys,
        gather_command,
        "--repo",
        str(root),
        "--out",
        str(binder),
        str(root / "a.js"),
        str(root / "b.js"),
        with_stderr=True,
    )
    assert code == 0, printed
    topology = root / "t.toml"
    code, printed = run_command(
        monkeypatch,
        capsys,
        topology_command,
        "--build",
        "--binder",
        str(binder),
        "--out",
        str(topology),
        "--stage",
        "4a=ownership-context/2",
        with_stderr=True,
    )
    assert code == 0, printed
    out = root / "copies"
    code, printed = _stage(root, "4a", out)
    assert code == 0, printed
    assert "0 places for ownership-context to rule on; 1 freeform" in printed
    return binder, topology, out


def test_a_shard_keeps_its_freeform_paths_on_its_received_binder(
    tmp_path, monkeypatch, capsys
):
    _, _, out = _freeform_run(tmp_path, monkeypatch, capsys)
    held = [
        json.loads((out / "binders" / name).read_text(encoding="utf-8"))["freeform"]
        for name in ("4a_ownership-context_1.json", "4a_ownership-context_2.json")
    ]
    assert held == [["a.js"], ["b.js"]]


def test_check_and_collate_accept_a_copy_with_no_sheets(tmp_path, monkeypatch, capsys):
    binder, topology, out = _freeform_run(tmp_path, monkeypatch, capsys)
    copies = sorted(out.glob("*.json"))
    assert [json.loads(c.read_text(encoding="utf-8"))["sheets"] for c in copies] == [
        [],
        [],
    ]
    for copy in copies:
        code, printed = run_command(
            monkeypatch,
            capsys,
            check_command,
            "--edit-copy",
            str(copy),
            "--binder",
            str(out / "binders" / copy.name),
            "--repo",
            str(tmp_path),
            with_stderr=True,
        )
        assert code == 0, printed
    flags = a_jacket_naming(
        binder,
        copies,
        stage="4a",
        topology=topology.read_text(encoding="utf-8"),
        received=[out / "binders" / copy.name for copy in copies],
        root=tmp_path,
    )
    argv = [*flags, "--proof-out", str(tmp_path / "proof.json")]
    code, printed = run_command(
        monkeypatch, capsys, collate_command, *argv, with_stderr=True
    )
    assert code == 0, printed
    assert (
        json.loads((tmp_path / "proof.json").read_text(encoding="utf-8"))["places"]
        == []
    )


def test_a_seeded_copy_says_how_many_freeform_paths_its_binder_holds(
    tmp_path, monkeypatch, capsys
):
    binder, _, _ = _freeform_run(tmp_path, monkeypatch, capsys)
    code, printed = run_command(
        monkeypatch,
        capsys,
        distribute_command,
        "--seed",
        "--binder",
        str(binder),
        "--role",
        "block-context",
        "--out",
        str(tmp_path / "seeded.json"),
        with_stderr=True,
    )
    assert code == 0, printed
    assert "0 places for block-context to rule on; 2 freeform" in printed


def test_two_modes_together_are_a_usage_error(tmp_path, monkeypatch, capsys):
    with pytest.raises(SystemExit) as exited:
        run_command(monkeypatch, capsys, distribute_command, "--shape", "--seed")
    assert exited.value.code == 2
    assert "not allowed with" in capsys.readouterr().err
