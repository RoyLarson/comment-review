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


def _tree(tmp_path, monkeypatch, capsys) -> Path:
    """Two pages, a binder over them, and the topology above, all on disk."""
    for name in ("a.py", "b.py"):
        (tmp_path / name).write_text(SAMPLE, encoding="utf-8", newline="")
    binder = tmp_path / "binder.json"
    code, printed = run_command(
        monkeypatch,
        capsys,
        gather_command,
        "--repo",
        str(tmp_path),
        "--out",
        str(binder),
        str(tmp_path / "a.py"),
        str(tmp_path / "b.py"),
        with_stderr=True,
    )
    assert code == 0, printed
    (tmp_path / "t.toml").write_text(FOUR_C, encoding="utf-8")
    return tmp_path


def _stage(root: Path, monkeypatch, capsys, stage: str, out: Path):
    return run_command(
        monkeypatch,
        capsys,
        distribute_command,
        "--topology",
        str(root / "t.toml"),
        "--stage",
        stage,
        "--binder",
        str(root / "binder.json"),
        "--out-dir",
        str(out),
        with_stderr=True,
    )


def test_a_stage_seeds_one_copy_per_dispatch_in_dispatch_order(
    tmp_path, monkeypatch, capsys
):
    root = _tree(tmp_path, monkeypatch, capsys)
    out = root / "copies"
    code, printed = _stage(root, monkeypatch, capsys, "4c", out)
    assert code == 0, printed
    names = sorted(p.name for p in out.iterdir())
    assert names == [
        "4c_block-context_1.json",
        "4c_block-context_2.json",
        "4c_function-context_1.json",
    ]
    first = json.loads((out / "4c_block-context_1.json").read_text(encoding="utf-8"))
    assert [s["path"] for s in first["sheets"]] == ["a.py"]
    third = json.loads((out / "4c_function-context_1.json").read_text(encoding="utf-8"))
    assert [s["path"] for s in third["sheets"]] == ["a.py", "b.py"]


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
    code, printed = _stage(root, monkeypatch, capsys, "4c", root / "copies")
    assert code == 2
    assert "no dispatch covers" in printed and "b.py" in printed
