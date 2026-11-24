"""`stage open` and `stage close`: a later stage starts from earlier stages' changes.

`no-component-owns-the-run` T2 and `move-is-a-composite-mark` T56, under
`docs/plans/0.2.4-the-run-has-a-jacket.md`. Each case drives the command's own
`main()`: `4a` is gathered from a committed checkout and closed on a proof the
fold closed, and `4c`'s tree is then built from the jacket alone.
"""

import json
import subprocess
from pathlib import Path

from conftest import run_command
from helpers import BASE, TWO, a_correct_setting, a_move, deal, taken_in_as_filed

from comment_review.commands import report
from comment_review.commands import stage as stage_command
from comment_review.flows.jacket import (
    JACKET_FILE,
    Jacket,
    load_jacket,
    resolved_path,
    save_jacket,
)
from comment_review.flows.proof_io import load_binder


def _row(name: str, reads: str, role: str) -> str:
    return (
        f'[[stage]]\nname = "{name}"\nkind = "editorial"\nreads = "{reads}"\n'
        f'  [[stage.dispatch]]\n  role = "{role}"\n'
    )


FOUR_A_THEN_FOUR_C = _row("4a", "original", "ownership-context") + _row(
    "4c", "revise:4a", "block-context"
)
TWO_ORIGINALS = _row("4a", "original", "ownership-context") + _row(
    "4b", "original", "block-context"
)

CORRECTED = {"block-context": {"m.py@b1": a_correct_setting("m.py@b1", "two", TWO)}}
#: The whole paragraph moves to `n.py`, a page the scope does not name.
MOVED_OUT = {
    "block-context": {
        "m.py@b1": a_move(
            "m.py@b1",
            "n.py@b0",
            change="# one\n# two\n# three",
            reads="# one\n# two\n# three",
        )
    }
}


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=True,
        timeout=60,
    ).stdout.strip()


#: `n.py` with an uncommitted edit to its code; its places are unchanged.
LOCAL_N = "v0 = 0\nv1 = 11\n"


def _commit(repo: Path) -> None:
    _git(
        repo,
        "-c",
        "user.name=Test",
        "-c",
        "user.email=test@example.invalid",
        "commit",
        "-q",
        "-m",
        "fixture",
    )


def _a_run(
    tmp_path,
    monkeypatch,
    capsys,
    by_role: dict,
    topology: str = FOUR_A_THEN_FOUR_C,
    stage: str = "4a",
    local: bool = False,
    autocrlf: str = "",
) -> Path:
    """A committed checkout, a jacket with no stage open, and a closed proof.

    The proof is the fold's over `m.py`, stamped `stage`. `n.py` and `gone.py`
    sit beside it, tracked and outside the scope. With `local`, the checkout
    holds an uncommitted edit to `n.py` and has deleted `gone.py`, and the
    fold read that checkout. Every file is written with LF endings; `autocrlf`
    sets the repo's `core.autocrlf`, and "" leaves the machine's own.

    Returns:
        The closed proof's path.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "n.py").write_text("v0 = 0\nv1 = 1\n", encoding="utf-8", newline="\n")
    (repo / "gone.py").write_text("g = 1\n", encoding="utf-8", newline="\n")
    _git(repo, "init")
    if autocrlf:
        _git(repo, "config", "core.autocrlf", autocrlf)
    _git(repo, "add", ".")
    _commit(repo)
    if local:
        (repo / "n.py").write_text(LOCAL_N, encoding="utf-8", newline="\n")
        (repo / "gone.py").unlink()
    code = deal(tmp_path, monkeypatch, capsys, by_role, {"m.py@b1": BASE}, stage=stage)
    assert code == report.REREADS
    taken_in_as_filed(tmp_path, monkeypatch, capsys)
    # Everything the fold wrote is committed; the local changes are not.
    _git(repo, "add", ".")
    _git(repo, "reset", "-q", "--", "n.py", "gone.py")
    _commit(repo)
    (tmp_path / "run").mkdir()
    save_jacket(
        _jacket(tmp_path), Jacket(_git(repo, "rev-parse", "HEAD"), ("m.py",), topology)
    )
    return tmp_path / "final.json"


def _jacket(tmp_path) -> Path:
    return tmp_path / "run" / JACKET_FILE


def _open(tmp_path, monkeypatch, capsys, stage: str, jacket: Path | None = None):
    return run_command(
        monkeypatch,
        capsys,
        stage_command,
        "open",
        "--jacket",
        str(jacket or _jacket(tmp_path)),
        "--stage",
        stage,
        "--repo",
        str(tmp_path / "repo"),
        with_stderr=True,
    )


def _close(tmp_path, monkeypatch, capsys, stage: str, proof: Path):
    return run_command(
        monkeypatch,
        capsys,
        stage_command,
        "close",
        "--jacket",
        str(_jacket(tmp_path)),
        "--stage",
        stage,
        "--proof",
        str(proof),
        with_stderr=True,
    )


def _closed_4a(
    tmp_path, monkeypatch, capsys, by_role: dict, local: bool = False, autocrlf=""
) -> None:
    proof = _a_run(
        tmp_path, monkeypatch, capsys, by_role, local=local, autocrlf=autocrlf
    )
    code, printed = _open(tmp_path, monkeypatch, capsys, "4a")
    assert code == 0, printed
    code, printed = _close(tmp_path, monkeypatch, capsys, "4a", proof)
    assert code == 0, printed


def _binder_of(tmp_path, stage: str):
    jacket, problems = load_jacket(_jacket(tmp_path))
    assert jacket is not None, problems
    binder, problems = load_binder(
        resolved_path(jacket.stages[stage].binder, _jacket(tmp_path))
    )
    assert binder is not None, problems
    return binder


def test_E1_4c_is_refused_until_4a_closes(tmp_path, monkeypatch, capsys):
    _a_run(tmp_path, monkeypatch, capsys, CORRECTED)
    code, printed = _open(tmp_path, monkeypatch, capsys, "4a")
    assert code == 0, printed
    code, printed = _open(tmp_path, monkeypatch, capsys, "4c")
    assert code == 1, printed
    assert "4a" in printed and "not closed" in printed
    assert not (tmp_path / "run" / "root4c").exists()
    jacket, _ = load_jacket(_jacket(tmp_path))
    assert jacket is not None and list(jacket.stages) == ["4a"]


def test_E2_4c_reads_the_text_4a_drafted(tmp_path, monkeypatch, capsys):
    _closed_4a(tmp_path, monkeypatch, capsys, CORRECTED)
    code, printed = _open(tmp_path, monkeypatch, capsys, "4c")
    assert code == 0, printed
    # What `distribute --stage` prints for each copy.
    assert "4c_block-context_1.json: " in printed
    assert "places for block-context to rule on" in printed

    binder = _binder_of(tmp_path, "4c")
    (row,) = [p for p in binder.paragraphs if p.address == "m.py@b1"]
    assert row.raw_text == TWO.rstrip("\n")
    assert binder.read_from["stage"] == "4c"
    # The checkout is not where the tree was built.
    assert BASE in (tmp_path / "repo" / "m.py").read_text(encoding="utf-8")

    jacket, _ = load_jacket(_jacket(tmp_path))
    assert jacket is not None
    entry = jacket.stages["4c"]
    assert (entry.root, entry.binder) == ("root4c", "binder4c.json")
    assert entry.dispatched == ("copies/4c_block-context_1.json",)
    assert entry.closed is None


def test_T56_a_page_4a_moved_text_into_is_in_4cs_binder(tmp_path, monkeypatch, capsys):
    _closed_4a(tmp_path, monkeypatch, capsys, MOVED_OUT)
    code, printed = _open(tmp_path, monkeypatch, capsys, "4c")
    assert code == 0, printed
    binder = _binder_of(tmp_path, "4c")
    assert sorted(page.path for page in binder.pages) == ["m.py", "n.py"]
    moved = [p.raw_text for p in binder.paragraphs if p.address.startswith("n.py@")]
    assert "# one\n# two\n# three" in moved


def test_the_root_resolves_from_a_cwd_other_than_the_one_it_was_built_from(
    tmp_path, monkeypatch, capsys
):
    _closed_4a(tmp_path, monkeypatch, capsys, CORRECTED)
    here = tmp_path / "a" / "b"
    here.mkdir(parents=True)
    monkeypatch.chdir(here)
    code, printed = _open(
        tmp_path, monkeypatch, capsys, "4c", Path("../../run") / JACKET_FILE
    )
    assert code == 0, printed

    elsewhere = tmp_path / "repo"
    monkeypatch.chdir(elsewhere)
    jacket_file = Path("../run") / JACKET_FILE
    jacket, _ = load_jacket(jacket_file)
    assert jacket is not None
    root = resolved_path(jacket.stages["4c"].root, jacket_file)
    assert root == (tmp_path / "run" / "root4c").resolve()
    assert TWO in (root / "m.py").read_text(encoding="utf-8")


def test_a_leftover_root_refuses_the_open_and_is_left_alone(
    tmp_path, monkeypatch, capsys
):
    _closed_4a(tmp_path, monkeypatch, capsys, CORRECTED)
    leftover = tmp_path / "run" / "root4c"
    leftover.mkdir()
    (leftover / "kept.txt").write_bytes(b"kept")
    code, printed = _open(tmp_path, monkeypatch, capsys, "4c")
    assert code == 1, printed
    assert "never reused" in printed
    assert [p.name for p in leftover.iterdir()] == ["kept.txt"]
    jacket, _ = load_jacket(_jacket(tmp_path))
    assert jacket is not None and "4c" not in jacket.stages


def test_a_stage_that_has_not_opened_does_not_close(tmp_path, monkeypatch, capsys):
    proof = _a_run(tmp_path, monkeypatch, capsys, CORRECTED)
    code, printed = _close(tmp_path, monkeypatch, capsys, "4a", proof)
    assert code == 1, printed
    assert "has not opened" in printed


def test_a_proof_that_has_not_closed_does_not_close_its_stage(
    tmp_path, monkeypatch, capsys
):
    _a_run(tmp_path, monkeypatch, capsys, CORRECTED)
    code, printed = _open(tmp_path, monkeypatch, capsys, "4a")
    assert code == 0, printed
    # The fold's first proof: the lone correction is still carried to the chief.
    code, printed = _close(
        tmp_path, monkeypatch, capsys, "4a", tmp_path / "proof0.json"
    )
    assert code == 1, printed
    assert "has not closed" in printed
    jacket, _ = load_jacket(_jacket(tmp_path))
    assert jacket is not None and jacket.stages["4a"].closed is None


def test_another_stages_proof_does_not_close_this_one(tmp_path, monkeypatch, capsys):
    proof = _a_run(tmp_path, monkeypatch, capsys, CORRECTED)
    code, printed = _open(tmp_path, monkeypatch, capsys, "4a")
    assert code == 0, printed
    wire = json.loads(proof.read_text(encoding="utf-8"))
    wire["stage"] = "4c"
    other = tmp_path / "other.json"
    other.write_text(json.dumps(wire), encoding="utf-8")
    code, printed = _close(tmp_path, monkeypatch, capsys, "4a", other)
    assert code == 1, printed
    assert "not stage '4a'" in printed


def test_a_stage_closes_only_in_topology_order(tmp_path, monkeypatch, capsys):
    proof = _a_run(tmp_path, monkeypatch, capsys, CORRECTED, TWO_ORIGINALS, "4b")
    for stage in ("4a", "4b"):
        code, printed = _open(tmp_path, monkeypatch, capsys, stage)
        assert code == 0, printed
    code, printed = _close(tmp_path, monkeypatch, capsys, "4b", proof)
    assert code == 1, printed
    assert "not next to close" in printed and "'4a'" in printed


def test_a_stage_tree_is_the_checkout_as_the_run_started_outside_the_scope(
    tmp_path, monkeypatch, capsys
):
    """A tracked file outside the scope holds an uncommitted edit, and 4a moves
    text into it; another was deleted. The tree holds both as the run found
    them, so the docket's sha refusal has nothing to refuse."""
    _closed_4a(tmp_path, monkeypatch, capsys, MOVED_OUT, local=True)
    code, printed = _open(tmp_path, monkeypatch, capsys, "4c")
    assert code == 0, printed
    root = tmp_path / "run" / "root4c"
    landed = (root / "n.py").read_text(encoding="utf-8")
    assert "v1 = 11" in landed and "# one\n# two\n# three" in landed
    assert not (root / "gone.py").exists()


def test_a_checkout_holding_lf_where_git_writes_crlf_opens_4c(
    tmp_path, monkeypatch, capsys
):
    """`core.autocrlf` true: a fresh checkout writes `n.py` with CRLF, while the
    checkout holds the LF bytes 4a read, and `git diff` reports no change."""
    _closed_4a(tmp_path, monkeypatch, capsys, MOVED_OUT, autocrlf="true")
    assert _git(tmp_path / "repo", "diff", "--name-only", "HEAD") == ""
    code, printed = _open(tmp_path, monkeypatch, capsys, "4c")
    assert code == 0, printed
    landed = (tmp_path / "run" / "root4c" / "n.py").read_bytes()
    assert b"\r\n" not in landed and b"# one\n# two\n# three" in landed


def _streams(monkeypatch, capsys, *argv: str) -> tuple[int, str, str]:
    monkeypatch.setattr("sys.argv", ["stage", *argv])
    code = stage_command.main()
    got = capsys.readouterr()
    return code, got.out, got.err


def test_an_unreadable_jacket_is_an_input_that_cannot_be_read(
    tmp_path, monkeypatch, capsys
):
    proof = _a_run(tmp_path, monkeypatch, capsys, CORRECTED)
    _jacket(tmp_path).write_text('{"format": 1}', encoding="utf-8")
    missing = tmp_path / "run" / "nowhere.json"
    for jacket in (_jacket(tmp_path), missing):
        for argv in (
            ("open", "--repo", str(tmp_path / "repo")),
            ("close", "--proof", str(proof)),
        ):
            verb, *rest = argv
            code, out, err = _streams(
                monkeypatch,
                capsys,
                verb,
                "--jacket",
                str(jacket),
                "--stage",
                "4a",
                *rest,
            )
            assert (code, out) == (2, ""), err
            assert str(jacket) in err


def test_a_proof_that_cannot_be_read_at_close_is_an_unreadable_input(
    tmp_path, monkeypatch, capsys
):
    _a_run(tmp_path, monkeypatch, capsys, CORRECTED)
    code, printed = _open(tmp_path, monkeypatch, capsys, "4a")
    assert code == 0, printed
    broken = tmp_path / "broken.json"
    broken.write_text("not json", encoding="utf-8")
    jacket = str(_jacket(tmp_path))
    for proof in (broken, tmp_path / "nowhere.json"):
        code, out, err = _streams(
            monkeypatch,
            capsys,
            "close",
            "--jacket",
            jacket,
            "--stage",
            "4a",
            "--proof",
            str(proof),
        )
        assert (code, out) == (2, ""), err
        assert proof.name in err


def test_a_closed_proof_gone_at_open_is_an_unreadable_input(
    tmp_path, monkeypatch, capsys
):
    _closed_4a(tmp_path, monkeypatch, capsys, CORRECTED)
    (tmp_path / "final.json").unlink()
    code, out, err = _streams(
        monkeypatch,
        capsys,
        "open",
        "--jacket",
        str(_jacket(tmp_path)),
        "--stage",
        "4c",
        "--repo",
        str(tmp_path / "repo"),
    )
    assert (code, out) == (2, ""), err
    assert "final.json" in err
    assert not (tmp_path / "run" / "root4c").exists()
