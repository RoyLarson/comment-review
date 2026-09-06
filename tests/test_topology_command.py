"""`commands/topology.py`: the console face of `fit` and `compose`.

`decision-log.md Process: #55`: the fit check lives in a command with a repo,
so a bad configuration is caught before the first page is read.
"""

from pathlib import Path

from conftest import SAMPLE, run_command

from comment_review.commands import gather as gather_command
from comment_review.commands import topology as topology_command

UNCOVERED = (
    '[[stage]]\nname = "4c"\nkind = "editorial"\n'
    '  [[stage.dispatch]]\n  role = "block-context"\n  paths = ["a.py", "zzz.py"]\n'
)
FORWARD_READ = (
    '[[stage]]\nname = "4c"\nkind = "editorial"\nreads = "revise:4a"\n'
    '  [[stage.dispatch]]\n  role = "block-context"\n'
)


def _binder(tmp_path, monkeypatch, capsys) -> Path:
    """Four pages on disk and a binder over them."""
    for n in "abcd":
        (tmp_path / f"{n}.py").write_text(SAMPLE, encoding="utf-8", newline="")
    binder = tmp_path / "binder.json"
    code, printed = run_command(
        monkeypatch,
        capsys,
        gather_command,
        "--repo",
        str(tmp_path),
        "--out",
        str(binder),
        *[str(tmp_path / f"{n}.py") for n in "abcd"],
        with_stderr=True,
    )
    assert code == 0, printed
    return binder


def _verify(monkeypatch, capsys, topology: Path, binder: Path):
    return run_command(
        monkeypatch,
        capsys,
        topology_command,
        "--verify",
        str(topology),
        "--binder",
        str(binder),
        with_stderr=True,
    )


def test_build_then_verify_round_trips(tmp_path, monkeypatch, capsys):
    binder = _binder(tmp_path, monkeypatch, capsys)
    out = tmp_path / "t.toml"
    code, printed = run_command(
        monkeypatch,
        capsys,
        topology_command,
        "--build",
        "--binder",
        str(binder),
        "--out",
        str(out),
        "--stage",
        "4a=ownership-context",
        "--stage",
        "4c=block-context/2,function-context,module-context",
        with_stderr=True,
    )
    assert code == 0, printed
    assert "fits" in printed and out.exists()
    code, printed = _verify(monkeypatch, capsys, out, binder)
    assert code == 0, printed
    assert "2 stages" in printed


def test_verify_names_the_misfit_with_its_stage_kind_pages_and_globs(
    tmp_path, monkeypatch, capsys
):
    binder = _binder(tmp_path, monkeypatch, capsys)
    t = tmp_path / "t.toml"
    t.write_text(UNCOVERED, encoding="utf-8")
    code, printed = _verify(monkeypatch, capsys, t, binder)
    assert code == 1
    assert "4c  uncovered" in printed and "b.py" in printed
    # ! The stage's globs ride on the uncovered line, so `zzz.py` is named too.
    assert "zzz.py" in printed


def test_a_file_read_refuses_is_the_reads_kind_at_exit_2(tmp_path, monkeypatch, capsys):
    binder = _binder(tmp_path, monkeypatch, capsys)
    t = tmp_path / "t.toml"
    t.write_text(FORWARD_READ, encoding="utf-8")
    code, printed = _verify(monkeypatch, capsys, t, binder)
    assert code == 2
    assert "reads" in printed and "4a" in printed


def test_build_refuses_a_directive_the_binder_cannot_honour(
    tmp_path, monkeypatch, capsys
):
    binder = _binder(tmp_path, monkeypatch, capsys)
    code, printed = run_command(
        monkeypatch,
        capsys,
        topology_command,
        "--build",
        "--binder",
        str(binder),
        "--out",
        str(tmp_path / "t.toml"),
        "--stage",
        "4c=block-context/9",
        with_stderr=True,
    )
    assert code == 2
    assert "9 ways" in printed


def test_it_is_a_command():
    from comment_review.__main__ import COMMANDS

    assert "topology" in COMMANDS
