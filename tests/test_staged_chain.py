"""`staged-chain-untested` T1 and P33: the fan-out fixture on a tree it was not written for.

! BOTH BRANCHES OF P33 ARE MECHANICAL. The fixture's globs name this repo's own
layout, so on a scratch tree `topology --verify` refuses it and NAMES THE GLOBS --
the "state why it is not" branch, said by the system rather than by a sentence
here. And `topology --build` writes the same shape for the scratch tree, which
`distribute --stage` then drives -- the "drives a scratch tree of four files"
branch, on a topology built for it.
"""

from pathlib import Path

from conftest import ROOT, SAMPLE, run_command

from comment_review.commands import distribute as distribute_command
from comment_review.commands import gather as gather_command
from comment_review.commands import topology as topology_command

FIXTURE = ROOT / "tests" / "fixtures" / "topologies" / "4a-then-4c.toml"


def _four(tmp_path, monkeypatch, capsys) -> Path:
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


def test_the_committed_fixture_is_refused_on_a_scratch_tree_by_its_globs(
    tmp_path, monkeypatch, capsys
):
    binder = _four(tmp_path, monkeypatch, capsys)
    code, printed = run_command(
        monkeypatch,
        capsys,
        topology_command,
        "--verify",
        str(FIXTURE),
        "--binder",
        str(binder),
    )
    assert code == 1, printed
    assert "src/comment_review/reading/*.py" in printed
    assert "src/comment_review/binder/*.py" in printed


def test_the_same_shape_built_for_the_scratch_tree_drives_it(
    tmp_path, monkeypatch, capsys
):
    binder = _four(tmp_path, monkeypatch, capsys)
    t = tmp_path / "t.toml"
    code, printed = run_command(
        monkeypatch,
        capsys,
        topology_command,
        "--build",
        "--binder",
        str(binder),
        "--out",
        str(t),
        "--stage",
        "4a=ownership-context",
        "--stage",
        "4c=block-context/2,function-context,module-context",
        with_stderr=True,
    )
    assert code == 0, printed
    out = tmp_path / "copies"
    code, printed = run_command(
        monkeypatch,
        capsys,
        distribute_command,
        "--topology",
        str(t),
        "--stage",
        "4c",
        "--binder",
        str(binder),
        "--out-dir",
        str(out),
        with_stderr=True,
    )
    assert code == 0, printed
    assert sorted(p.name for p in out.iterdir()) == [
        "4c_block-context_1.json",
        "4c_block-context_2.json",
        "4c_function-context_1.json",
        "4c_module-context_1.json",
    ]
