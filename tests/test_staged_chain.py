"""`staged-chain-untested` T1 and P33: the fan-out fixture on a tree it was not
written for.

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


def _bind(tmp_path, monkeypatch, capsys, repo: Path, out: Path, revise: int) -> Path:
    """One binder over `repo`'s four pages, stamped with the revise `repo` is."""
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
        *[str(repo / f"{n}.py") for n in "abcd"],
        with_stderr=True,
    )
    assert code == 0, printed
    return out


def _four(tmp_path, monkeypatch, capsys) -> Path:
    """Four pages on disk and a binder over them."""
    for n in "abcd":
        (tmp_path / f"{n}.py").write_text(SAMPLE, encoding="utf-8", newline="")
    return _bind(tmp_path, monkeypatch, capsys, tmp_path, tmp_path / "binder.json", 0)


def _revise(tmp_path, monkeypatch, capsys) -> tuple[Path, Path]:
    """A revise of the four pages, standing in for what `4a`'s proof pulls.

    `4c` reads `revise:4a`, so it is seeded from a binder gathered over that
    revise rather than over the original -- `desk.topology.seeded_from_problem`.
    """
    pulled = tmp_path / "revise"
    pulled.mkdir()
    for n in "abcd":
        (pulled / f"{n}.py").write_text(SAMPLE, encoding="utf-8", newline="")
    binder = _bind(
        tmp_path, monkeypatch, capsys, pulled, tmp_path / "revise-binder.json", 1
    )
    return pulled, binder


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
    pulled, revise_binder = _revise(tmp_path, monkeypatch, capsys)
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
        str(revise_binder),
        "--revise",
        str(pulled),
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
