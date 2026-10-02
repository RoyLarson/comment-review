"""`commands/distribute.py --topology --stage`: one seeded copy per dispatch, in order.

`decision-log.md Process: #74`: the topology keeps a reader, and the reader is the
distribution -- one invocation reads one stage's dispatches and writes one seeded
edit copy per dispatch. The task agent reads the ORDER from SKILL.md (`#73`).
"""

import json
from pathlib import Path

from conftest import SAMPLE, run_command

from comment_review.commands import distribute as distribute_command
from comment_review.commands import gather as gather_command

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


def _bind(tmp_path, monkeypatch, capsys, repo: Path, out: Path, revise: int):
    """One binder over `repo`'s two pages, stamped with the revise `repo` is."""
    code, printed = run_command(
        monkeypatch,
        capsys,
        gather_command,
        "--repo",
        str(repo),
        "--revise",
        str(revise),
        "--out",
        str(out),
        str(repo / "a.py"),
        str(repo / "b.py"),
        with_stderr=True,
    )
    assert code == 0, printed


def _tree(tmp_path, monkeypatch, capsys) -> Path:
    """Two pages, a revise of them, a binder over each, and the topology above.

    The revise stands in for what stage `4a`'s `proof` pulls: `4c` reads it,
    so the copies it seeds are cut from the revise's binder rather than the
    original's.
    """
    pulled = tmp_path / "revise"
    pulled.mkdir()
    for name in ("a.py", "b.py"):
        (tmp_path / name).write_text(SAMPLE, encoding="utf-8", newline="")
        (pulled / name).write_text(SAMPLE, encoding="utf-8", newline="")
    _bind(tmp_path, monkeypatch, capsys, tmp_path, tmp_path / "binder.json", 0)
    _bind(tmp_path, monkeypatch, capsys, pulled, tmp_path / "revise-binder.json", 1)
    (tmp_path / "t.toml").write_text(FOUR_C, encoding="utf-8")
    return tmp_path


def _stage(
    root: Path,
    monkeypatch,
    capsys,
    stage: str,
    out: Path,
    revise: Path | None = None,
    binder: str = "",
):
    named = ["--revise", str(revise)] if revise is not None else []
    return run_command(
        monkeypatch,
        capsys,
        distribute_command,
        "--topology",
        str(root / "t.toml"),
        "--stage",
        stage,
        "--binder",
        str(root / (binder or "binder.json")),
        "--out-dir",
        str(out),
        *named,
        with_stderr=True,
    )


def _second(root: Path, monkeypatch, capsys, out: Path, **named):
    """Stage `4c` as it is meant to be run: the revise it reads, and its binder."""
    return _stage(
        root,
        monkeypatch,
        capsys,
        "4c",
        out,
        revise=named.pop("revise", root / "revise"),
        binder=named.pop("binder", "revise-binder.json"),
    )


def test_a_stage_seeds_one_copy_per_dispatch_in_dispatch_order(
    tmp_path, monkeypatch, capsys
):
    root = _tree(tmp_path, monkeypatch, capsys)
    out = root / "copies"
    code, printed = _second(root, monkeypatch, capsys, out)
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
    code, printed = _second(root, monkeypatch, capsys, out)
    assert code == 0, printed
    for name, paths in (
        ("4c_block-context_1.json", ["a.py"]),
        ("4c_block-context_2.json", ["b.py"]),
        ("4c_function-context_1.json", ["a.py", "b.py"]),
    ):
        binder = json.loads((out / "binders" / name).read_text(encoding="utf-8"))
        assert [p["path"] for p in binder["pages"]] == paths
        assert Path(binder["read_from"]["root"]).resolve() == root / "revise"
        assert binder["read_from"]["revise"] == 1
        assert str(out / "binders" / name) in printed


def test_received_binder_contains_only_stage_assigned_places(
    tmp_path, monkeypatch, capsys
):
    root = _tree(tmp_path, monkeypatch, capsys)
    for name in ("a.py", "b.py"):
        (root / "revise" / name).write_text(
            'x = 0\n# long\n# paragraph\nx = 1\n# short\ndef f():\n'
            '    """Doc."""\n    pass\n',
            encoding="utf-8",
        )
    _bind(root, monkeypatch, capsys, root / "revise", root / "revise-binder.json", 1)
    (root / "t.toml").write_text(
        FOUR_C.replace('name = "4c"', 'name = "4c"\nseries = ["b"]\ncap = 1'),
        encoding="utf-8",
    )
    out = root / "copies"
    code, printed = _second(root, monkeypatch, capsys, out)
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


def test_a_stage_the_topology_lacks_is_refused_by_name(tmp_path, monkeypatch, capsys):
    root = _tree(tmp_path, monkeypatch, capsys)
    code, printed = _stage(root, monkeypatch, capsys, "4b", root / "copies")
    assert code == 2
    assert "4b" in printed and "4a" in printed and "4c" in printed


def test_an_uncovered_page_is_refused_with_fan_outs_own_reason(
    tmp_path, monkeypatch, capsys
):
    root = _tree(tmp_path, monkeypatch, capsys)
    (root / "t.toml").write_text(
        FOUR_C.replace('paths = ["b.py"]', 'paths = ["zzz.py"]'), encoding="utf-8"
    )
    code, printed = _second(root, monkeypatch, capsys, root / "copies")
    assert code == 2
    assert "no dispatch covers" in printed and "b.py" in printed


def test_a_stage_reading_a_revise_is_refused_without_one(tmp_path, monkeypatch, capsys):
    """`4c` reads `revise:4a`, so the original's binder is not what seeds it."""
    root = _tree(tmp_path, monkeypatch, capsys)
    out = root / "copies"
    code, printed = _stage(root, monkeypatch, capsys, "4c", out)
    assert code == 2, printed
    assert "4c" in printed and "4a" in printed
    assert not out.exists()


def test_a_binder_gathered_from_another_tree_is_refused(tmp_path, monkeypatch, capsys):
    """The revise root is named and the binder is the original's."""
    root = _tree(tmp_path, monkeypatch, capsys)
    out = root / "copies"
    code, printed = _second(root, monkeypatch, capsys, out, binder="binder.json")
    assert code == 2, printed
    assert "revise" in printed
    assert not out.exists()


def test_a_stage_reading_the_original_takes_no_revise(tmp_path, monkeypatch, capsys):
    root = _tree(tmp_path, monkeypatch, capsys)
    out = root / "copies"
    code, printed = _stage(root, monkeypatch, capsys, "4a", out, revise=root / "revise")
    assert code == 2, printed
    assert "4a" in printed and "original" in printed
    assert not out.exists()
