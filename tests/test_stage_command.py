"""`stage open`, `collate --jacket` and `stage close` over one run's jacket.

`no-component-owns-the-run` T2, `move-is-a-composite-mark` T56 and
`fold-admission-has-no-owner` T3, under
`docs/plans/0.2.4-the-run-has-a-jacket.md`. Each case drives the commands' own
`main()`: `4a` is gathered from a committed checkout, its copies filled,
folded by `collate --jacket` and closed on the proof the chief closed, and
`4c`'s tree is then built from the jacket alone.
"""

import json
import subprocess
from pathlib import Path

from conftest import run_command
from helpers import (
    BASE,
    TWO,
    _overlaid,
    a_correct_setting,
    a_move,
    a_real_binder_over,
    taken_in_as_filed,
)

from comment_review.commands import check as check_command
from comment_review.commands import collate as collate_command
from comment_review.commands import report
from comment_review.commands import stage as stage_command
from comment_review.flows.fan_out import received_binder_of
from comment_review.flows.jacket import (
    JACKET_FILE,
    Jacket,
    load_jacket,
    resolved_path,
    save_jacket,
)
from comment_review.flows.proof_io import load_binder, load_proof


def _row(name: str, reads: str, *roles: str, admits: str = "") -> str:
    return (
        f'[[stage]]\nname = "{name}"\nkind = "editorial"\nreads = "{reads}"\n'
        + (f"admits = [{admits}]\n" if admits else "")
        + "".join(f'  [[stage.dispatch]]\n  role = "{role}"\n' for role in roles)
    )


FOUR_A_THEN_FOUR_C = _row("4a", "original", "block-context") + _row(
    "4c", "revise:4a", "block-context"
)
TWO_ORIGINALS = _row("4a", "original", "block-context") + _row(
    "4b", "original", "block-context"
)
#: 4a dispatched to three roles.
THREE_ROLES = _row(
    "4a", "original", "block-context", "function-context", "module-context"
)
#: 4a admitting the edit instructions only, so a `correct` is not admitted.
EDITS_ONLY = _row(
    "4a", "original", "block-context", admits='"patch", "drop", "add", "clean"'
)
NOT_ADMITTED = "stage 4a admits patch, drop, add, clean, and not correct"

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
    topology: str = FOUR_A_THEN_FOUR_C,
    local: bool = False,
    autocrlf: str = "",
) -> None:
    """A committed checkout and a jacket with no stage open.

    The checkout holds `m.py`, whose one place is `BASE`, with `n.py` and
    `gone.py` beside it, tracked and outside the scope. With `local`, it holds
    an uncommitted edit to `n.py` and has deleted `gone.py`. Every file is
    written with LF endings; `autocrlf` sets the repo's `core.autocrlf`, and
    "" leaves the machine's own.
    """
    repo = tmp_path / "repo"
    a_real_binder_over(repo, {"m.py@b1": BASE})
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
    (tmp_path / "run").mkdir()
    save_jacket(
        _jacket(tmp_path), Jacket(_git(repo, "rev-parse", "HEAD"), ("m.py",), topology)
    )


def _jacket(tmp_path) -> Path:
    return tmp_path / "run" / JACKET_FILE


def _copies(tmp_path, stage: str) -> list[Path]:
    """Each copy the jacket records stage `stage` dispatched."""
    jacket, problems = load_jacket(_jacket(tmp_path))
    assert jacket is not None, problems
    return [
        resolved_path(one, _jacket(tmp_path)) for one in jacket.stages[stage].dispatched
    ]


def _filled(tmp_path, stage: str, by_role: dict, **fields) -> None:
    """Each of the stage's copies with its role's marks laid over, and `fields`."""
    for path in _copies(tmp_path, stage):
        copy = json.loads(path.read_text(encoding="utf-8"))
        _overlaid(copy, by_role.get(copy["role"], {}))
        path.write_text(json.dumps({**copy, **fields}), encoding="utf-8")


def _collate(tmp_path, monkeypatch, capsys, stage: str, *extra: str):
    """`collate --jacket` over the stage, its proof to proof0.json."""
    return run_command(
        monkeypatch,
        capsys,
        collate_command,
        "--jacket",
        str(_jacket(tmp_path)),
        "--stage",
        stage,
        "--proof-out",
        str(tmp_path / "proof0.json"),
        *extra,
        with_stderr=True,
    )


def _folded(tmp_path, monkeypatch, capsys, by_role: dict, stage: str = "4a") -> Path:
    """The open stage's copies filled, folded and closed by the chief.

    Returns:
        The closed proof's path.
    """
    _filled(tmp_path, stage, by_role)
    code, printed = _collate(tmp_path, monkeypatch, capsys, stage)
    assert code == report.REREADS, printed
    taken_in_as_filed(tmp_path, monkeypatch, capsys)
    return tmp_path / "final.json"


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
    _a_run(tmp_path, local=local, autocrlf=autocrlf)
    code, printed = _open(tmp_path, monkeypatch, capsys, "4a")
    assert code == 0, printed
    proof = _folded(tmp_path, monkeypatch, capsys, by_role)
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
    _a_run(tmp_path)
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
    _a_run(tmp_path)
    code, printed = _close(tmp_path, monkeypatch, capsys, "4a", tmp_path / "p.json")
    assert code == 1, printed
    assert "has not opened" in printed


def test_a_proof_that_has_not_closed_does_not_close_its_stage(
    tmp_path, monkeypatch, capsys
):
    _a_run(tmp_path)
    code, printed = _open(tmp_path, monkeypatch, capsys, "4a")
    assert code == 0, printed
    _filled(tmp_path, "4a", CORRECTED)
    code, printed = _collate(tmp_path, monkeypatch, capsys, "4a")
    assert code == report.REREADS, printed
    # The fold's first proof: the lone correction is still carried to the chief.
    code, printed = _close(
        tmp_path, monkeypatch, capsys, "4a", tmp_path / "proof0.json"
    )
    assert code == 1, printed
    assert "has not closed" in printed
    jacket, _ = load_jacket(_jacket(tmp_path))
    assert jacket is not None and jacket.stages["4a"].closed is None


def test_another_stages_proof_does_not_close_this_one(tmp_path, monkeypatch, capsys):
    _a_run(tmp_path)
    code, printed = _open(tmp_path, monkeypatch, capsys, "4a")
    assert code == 0, printed
    proof = _folded(tmp_path, monkeypatch, capsys, CORRECTED)
    wire = json.loads(proof.read_text(encoding="utf-8"))
    wire["stage"] = "4c"
    other = tmp_path / "other.json"
    other.write_text(json.dumps(wire), encoding="utf-8")
    code, printed = _close(tmp_path, monkeypatch, capsys, "4a", other)
    assert code == 1, printed
    assert "not stage '4a'" in printed


def test_a_stage_closes_only_in_topology_order(tmp_path, monkeypatch, capsys):
    _a_run(tmp_path, TWO_ORIGINALS)
    for stage in ("4a", "4b"):
        code, printed = _open(tmp_path, monkeypatch, capsys, stage)
        assert code == 0, printed
    proof = _folded(tmp_path, monkeypatch, capsys, CORRECTED, "4b")
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
    _a_run(tmp_path)
    proof = tmp_path / "p.json"
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
    _a_run(tmp_path)
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


def test_W_S14_a_dispatch_that_never_returned_is_named_and_nothing_folds(
    tmp_path, monkeypatch, capsys
):
    _a_run(tmp_path, THREE_ROLES)
    code, printed = _open(tmp_path, monkeypatch, capsys, "4a")
    assert code == 0, printed
    gone = _copies(tmp_path, "4a")[1]
    gone.unlink()
    code, printed = _collate(tmp_path, monkeypatch, capsys, "4a")
    assert code == report.NOT_RETURNED == 6, printed
    assert printed.splitlines() == [f"not returned {gone}: function-context"]
    assert not (tmp_path / "proof0.json").exists()


def test_the_closed_proof_records_what_was_dispatched_and_returned(
    tmp_path, monkeypatch, capsys
):
    """Through the chief's ruling too: `final.json` is `disposition`'s proof."""
    _closed_4a(tmp_path, monkeypatch, capsys, CORRECTED)
    proof, why = load_proof(tmp_path / "final.json")
    assert proof is not None, why
    sent = ("copies/4a_block-context_1.json",)
    assert (proof.dispatched, proof.returned) == (sent, sent)
    wire = json.loads((tmp_path / "final.json").read_text(encoding="utf-8"))
    assert (wire["dispatched"], wire["returned"]) == (list(sent), list(sent))


def test_a_proof_short_of_a_dispatch_does_not_close_its_stage(
    tmp_path, monkeypatch, capsys
):
    _a_run(tmp_path)
    code, printed = _open(tmp_path, monkeypatch, capsys, "4a")
    assert code == 0, printed
    proof = _folded(tmp_path, monkeypatch, capsys, CORRECTED)
    wire = json.loads(proof.read_text(encoding="utf-8"))
    wire["returned"] = []
    proof.write_text(json.dumps(wire), encoding="utf-8")
    code, printed = _close(tmp_path, monkeypatch, capsys, "4a", proof)
    assert code == 1, printed
    assert "folded 0 of the 1 copies stage '4a' dispatched" in printed
    assert "not returned: copies/4a_block-context_1.json" in printed
    jacket, _ = load_jacket(_jacket(tmp_path))
    assert jacket is not None and jacket.stages["4a"].closed is None


def _checked(tmp_path, monkeypatch, capsys, copy: Path):
    return run_command(
        monkeypatch,
        capsys,
        check_command,
        "--edit-copy",
        str(copy),
        "--binder",
        str(received_binder_of(copy)),
        "--repo",
        str(tmp_path / "repo"),
        with_stderr=True,
    )


def test_check_and_collate_hold_a_mark_to_the_admits_the_row_stamped(
    tmp_path, monkeypatch, capsys
):
    """`check` reads `admits` off the copy, which `stage open` stamped from the
    jacket's row; `collate --jacket` reads the row. Both refuse the `correct`."""
    _a_run(tmp_path, EDITS_ONLY)
    code, printed = _open(tmp_path, monkeypatch, capsys, "4a")
    assert code == 0, printed
    (copy,) = _copies(tmp_path, "4a")
    _filled(tmp_path, "4a", CORRECTED)
    code, printed = _checked(tmp_path, monkeypatch, capsys, copy)
    assert code == report.BROKEN, printed
    assert NOT_ADMITTED in printed
    code, printed = _collate(tmp_path, monkeypatch, capsys, "4a")
    assert code == report.BROKEN, printed
    assert NOT_ADMITTED in printed


def test_a_copy_that_widened_its_admits_is_held_to_the_jacket_row(
    tmp_path, monkeypatch, capsys
):
    _a_run(tmp_path, EDITS_ONLY)
    code, printed = _open(tmp_path, monkeypatch, capsys, "4a")
    assert code == 0, printed
    _filled(tmp_path, "4a", CORRECTED, admits=["patch", "correct"])
    code, printed = _collate(tmp_path, monkeypatch, capsys, "4a")
    assert code == report.BROKEN, printed
    assert NOT_ADMITTED in printed
    assert "what a stage admits is the row's" in printed
    assert not (tmp_path / "proof0.json").exists()


def test_collate_jacket_takes_none_of_the_flags_the_jacket_replaces(
    tmp_path, monkeypatch, capsys
):
    _a_run(tmp_path)
    code, printed = _open(tmp_path, monkeypatch, capsys, "4a")
    assert code == 0, printed
    topology = tmp_path / "t.toml"
    topology.write_text(FOUR_A_THEN_FOUR_C, encoding="utf-8")
    code, printed = _collate(
        tmp_path, monkeypatch, capsys, "4a", "--topology", str(topology)
    )
    assert code == report.UNREADABLE, printed
    assert "--jacket names what --topology would" in printed
    assert not (tmp_path / "proof0.json").exists()


def test_collate_jacket_folds_only_an_open_stage(tmp_path, monkeypatch, capsys):
    _closed_4a(tmp_path, monkeypatch, capsys, CORRECTED)
    for stage, why in (("4c", "has not opened"), ("4a", "has already closed")):
        code, printed = _collate(tmp_path, monkeypatch, capsys, stage)
        assert code == report.UNREADABLE, printed
        assert f"stage {stage!r} {why}" in printed
