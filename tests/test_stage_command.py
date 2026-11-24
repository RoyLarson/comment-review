"""`stage open`, `collate --jacket`, `stage close` and `proof --jacket` over a jacket.

`no-component-owns-the-run` T2 and T3, `move-is-a-composite-mark` T56,
`staged-chain-untested` T3 and `fold-admission-has-no-owner` T3, under
`docs/plans/0.2.4-the-run-has-a-jacket.md`. Each case drives the commands' own
`main()`: `4a` is gathered from a committed checkout, its copies filled,
folded by `collate --jacket` and closed on the proof the chief closed, and
`4c`'s tree is then built from the jacket alone.
"""

import json
import subprocess
from pathlib import Path

import pytest
from conftest import ROOT, run_command
from helpers import (
    BASE,
    TWO,
    _overlaid,
    a_clean,
    a_correct_setting,
    a_move,
    a_patch,
    a_real_binder_over,
    taken_in_as_filed,
)

from comment_review.commands import check as check_command
from comment_review.commands import collate as collate_command
from comment_review.commands import proof as proof_command
from comment_review.commands import report
from comment_review.commands import stage as stage_command
from comment_review.flows import revise
from comment_review.flows.fan_out import received_binder_of
from comment_review.flows.jacket import (
    JACKET_FILE,
    Jacket,
    jacket_from_wire,
    jacket_to_wire,
    load_jacket,
    put_topology,
    resolved_path,
    save_jacket,
)
from comment_review.flows.proof_io import load_binder, load_proof
from comment_review.flows.transcribe import docket_of_proof


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


def test_a_topology_that_is_not_one_chain_is_refused_naming_the_stage(tmp_path):
    """Two stages reading the original could open and close, and never be set."""
    repo = tmp_path / "repo"
    a_real_binder_over(repo, {"m.py@b1": BASE})
    _git(repo, "init")
    _git(repo, "add", ".")
    _commit(repo)
    run = tmp_path / "run"
    why = put_topology(run, TWO_ORIGINALS, "HEAD", ("m.py",), repo)
    assert len(why) == 1 and "stage '4b' reads 'original'" in why[0], why
    assert "so it reads 'revise:4a'" in why[0]
    assert not (run / JACKET_FILE).exists()
    wire = jacket_to_wire(Jacket("0" * 40, ("m.py",), FOUR_A_THEN_FOUR_C))
    wire["topology"] = TWO_ORIGINALS
    jacket, why = jacket_from_wire("j", wire)
    assert jacket is None and "stage '4b'" in why[0], why


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


@pytest.mark.parametrize(
    "admits",
    [["patch", "drop", "add", "clean", "correct"], ["patch", "clean"]],
    ids=["wider", "narrower"],
)
def test_a_copy_whose_admits_differ_from_the_row_is_refused_naming_both(
    tmp_path, monkeypatch, capsys, admits
):
    """`stage open` stamped `admits` from the row, so a copy holding any other
    list was edited after it was seeded, whichever way it moved. The one mark
    is a `clean`, which both lists and the row admit, so the list is the only
    thing refused."""
    _a_run(tmp_path, EDITS_ONLY)
    code, printed = _open(tmp_path, monkeypatch, capsys, "4a")
    assert code == 0, printed
    cleaned = {"block-context": {"m.py@b1": a_clean("m.py@b1")}}
    _filled(tmp_path, "4a", cleaned, admits=admits)
    code, printed = _collate(tmp_path, monkeypatch, capsys, "4a")
    assert code == report.BROKEN, printed
    assert (
        f"says it may file {', '.join(admits)}, and stage 4a's row admits"
        " patch, drop, add, clean" in printed
    ), printed
    assert not (tmp_path / "proof0.json").exists()


def test_collate_runs_only_from_a_jacket(tmp_path, monkeypatch, capsys):
    """A stage is folded from the jacket's record, and no flag names its parts."""
    proof = tmp_path / "proof0.json"
    with pytest.raises(SystemExit) as exited:
        run_command(
            monkeypatch,
            capsys,
            collate_command,
            "--stage",
            "4a",
            "--proof-out",
            str(proof),
        )
    assert exited.value.code == 2
    assert "--jacket" in capsys.readouterr().err
    assert not proof.exists()


def test_collate_jacket_folds_only_an_open_stage(tmp_path, monkeypatch, capsys):
    _closed_4a(tmp_path, monkeypatch, capsys, CORRECTED)
    for stage, why in (("4c", "has not opened"), ("4a", "has already closed")):
        code, printed = _collate(tmp_path, monkeypatch, capsys, stage)
        assert code == report.UNREADABLE, printed
        assert f"stage {stage!r} {why}" in printed


# -- proof --jacket: the author's approval, replayed over the manuscript -------

#: 4a's correction at `m.py@b1`, and 4c's over the text 4a set there.
FOUR_C_OVER_TWO = "# one\n# TWO C\n# three\n"
RECORRECTED = {
    "block-context": {"m.py@b1": a_correct_setting("m.py@b1", "TWO", FOUR_C_OVER_TWO)}
}
FOUR_A_ALONE = _row("4a", "original", "block-context")


def _stage_closed(tmp_path, monkeypatch, capsys, stage: str, by_role: dict) -> Path:
    """Stage `stage` opened, its copies filled and folded, and closed.

    The closed proof is kept at `final<stage>.json`, since the next stage's
    chief writes `final.json` again and the jacket holds each proof's sha.
    """
    code, printed = _open(tmp_path, monkeypatch, capsys, stage)
    assert code == 0, printed
    kept = tmp_path / f"final{stage}.json"
    _folded(tmp_path, monkeypatch, capsys, by_role, stage).replace(kept)
    code, printed = _close(tmp_path, monkeypatch, capsys, stage, kept)
    assert code == 0, printed
    return kept


def _set_run(tmp_path, monkeypatch, capsys, *only: str):
    """`proof --jacket` into `tmp_path/drafts`, accepting `only` where named."""
    return run_command(
        monkeypatch,
        capsys,
        proof_command,
        "--jacket",
        str(_jacket(tmp_path)),
        "--repo",
        str(tmp_path / "repo"),
        "--out",
        str(tmp_path / "drafts"),
        *(arg for one in only for arg in ("--only", one)),
        with_stderr=True,
    )


def _moved_into(tmp_path) -> str:
    """The address 4a's move landed at in `n.py`, as 4c's binder reads it."""
    (address,) = [
        p.address
        for p in _binder_of(tmp_path, "4c").paragraphs
        if p.address.startswith("n.py@") and p.raw_text == BASE.rstrip("\n")
    ]
    return address


def _drafts(tmp_path) -> dict[str, bytes]:
    drafts = tmp_path / "drafts"
    return {
        path.relative_to(drafts).as_posix(): path.read_bytes()
        for path in drafts.rglob("*")
        if path.is_file()
    }


def test_accept_all_sets_the_last_stages_tree_page_for_page(
    tmp_path, monkeypatch, capsys
):
    """4a moves `m.py@b1` into `n.py`; 4c corrects the moved paragraph. The
    replay equals 4c's root with 4c's proof set over it, page for page."""
    _a_run(tmp_path)
    _stage_closed(tmp_path, monkeypatch, capsys, "4a", MOVED_OUT)
    _open(tmp_path, monkeypatch, capsys, "4c")
    there = _moved_into(tmp_path)
    landed = {"block-context": {there: a_correct_setting(there, "two", TWO)}}
    _filled(tmp_path, "4c", landed)
    code, printed = _collate(tmp_path, monkeypatch, capsys, "4c")
    assert code == report.REREADS, printed
    taken_in_as_filed(tmp_path, monkeypatch, capsys)
    code, printed = _close(tmp_path, monkeypatch, capsys, "4c", tmp_path / "final.json")
    assert code == 0, printed

    code, printed = _set_run(tmp_path, monkeypatch, capsys)
    assert code == 0, printed
    assert "2 page(s) drafted for review" in printed

    root4c = tmp_path / "run" / "root4c"
    proof4c, why = load_proof(tmp_path / "final.json")
    assert proof4c is not None, why
    docket = docket_of_proof(proof4c, root4c)
    pulled = revise.pull(docket, root4c, tmp_path / "last")
    assert pulled.refusals == []
    last = {
        rel: (pulled.root / rel if (pulled.root / rel).exists() else root4c / rel)
        for rel in ("m.py", "n.py")
    }
    assert _drafts(tmp_path) == {rel: path.read_bytes() for rel, path in last.items()}
    assert TWO in (tmp_path / "drafts" / "n.py").read_text(encoding="utf-8")


def _corrected_twice(tmp_path, monkeypatch, capsys) -> None:
    """4a corrects `m.py@b1` to `TWO`; 4c corrects what 4a set there."""
    _a_run(tmp_path)
    _stage_closed(tmp_path, monkeypatch, capsys, "4a", CORRECTED)
    _stage_closed(tmp_path, monkeypatch, capsys, "4c", RECORRECTED)


def test_E4_a_later_stages_place_without_the_earlier_one_is_refused_naming_it(
    tmp_path, monkeypatch, capsys
):
    _corrected_twice(tmp_path, monkeypatch, capsys)
    code, printed = _set_run(tmp_path, monkeypatch, capsys, "4c:m.py@b1")
    assert code == 1, printed
    assert "stage '4c': REFUSED at verify: m.py" in printed
    assert "with 4a:m.py@b1 set, and the author did not accept it" in printed
    assert not (tmp_path / "drafts").exists()

    code, printed = _set_run(tmp_path, monkeypatch, capsys, "4a:m.py@b1", "4c:m.py@b1")
    assert code == 0, printed
    assert _drafts(tmp_path).keys() == {"m.py"}
    assert FOUR_C_OVER_TWO in (tmp_path / "drafts" / "m.py").read_text(encoding="utf-8")


def test_an_earlier_stages_place_accepted_alone_is_drafted(
    tmp_path, monkeypatch, capsys
):
    _corrected_twice(tmp_path, monkeypatch, capsys)
    code, printed = _set_run(tmp_path, monkeypatch, capsys, "4a:m.py@b1")
    assert code == 0, printed
    assert TWO in (tmp_path / "drafts" / "m.py").read_text(encoding="utf-8")


def test_an_accepted_move_drafts_both_pages_and_one_end_is_refused(
    tmp_path, monkeypatch, capsys
):
    _a_run(tmp_path, FOUR_A_ALONE)
    _stage_closed(tmp_path, monkeypatch, capsys, "4a", MOVED_OUT)
    code, printed = _set_run(tmp_path, monkeypatch, capsys, "4a:m.py@b1")
    assert code == 1, printed
    assert "approve both ends of this move together" in printed
    assert not (tmp_path / "drafts").exists()

    code, printed = _set_run(tmp_path, monkeypatch, capsys, "4a:m.py@b1", "4a:n.py@b0")
    assert code == 0, printed
    drafts = _drafts(tmp_path)
    assert drafts.keys() == {"m.py", "n.py"}
    assert b"# one\n# two\n# three" in drafts["n.py"]
    assert b"# one" not in drafts["m.py"]


def test_a_run_with_a_stage_not_closed_is_not_set(tmp_path, monkeypatch, capsys):
    _closed_4a(tmp_path, monkeypatch, capsys, CORRECTED)
    code, printed = _set_run(tmp_path, monkeypatch, capsys)
    assert code == 1, printed
    assert "stage 4c has not closed" in printed
    assert not (tmp_path / "drafts").exists()


def test_an_approval_naming_no_stage_is_refused(tmp_path, monkeypatch, capsys):
    _corrected_twice(tmp_path, monkeypatch, capsys)
    code, printed = _set_run(tmp_path, monkeypatch, capsys, "m.py@b1")
    assert code == 1, printed
    assert "'m.py@b1' names no stage's place" in printed


#: 4a, 4c and a compacting stage 6, each block-context alone.
CHAIN = (
    FOUR_A_THEN_FOUR_C
    + '[[stage]]\nname = "6"\nkind = "editorial"\nreads = "revise:4c"\ncap = 2\n'
    'series = ["b", "c"]\nadmits = ["patch", "drop", "add", "clean"]\n'
    '  [[stage.dispatch]]\n  role = "block-context"\n'
)
AT = "m.py@b1"
#: Per stage: its name, the role it dispatches, its mark at `AT`, and the
#: paragraph once it is set -- one more marker than the stage before.
FOUR_A_C_6 = (
    ("4a", "block-context", "# one A\n# two\n# three", ("correct", "one")),
    ("4c", "block-context", "# one A\n# two C\n# three", ("correct", "two")),
    ("6", "block-context", "# one A\n# two C\n# three 6", ("patch", "three")),
)
SEQUENTIAL = tuple(
    (
        name,
        role,
        "# one " + " ".join("1234"[: int(name)]) + "\n# two\n# three",
        ("correct", "one"),
    )
    for name, role in (
        ("1", "ownership-context"),
        ("2", "block-context"),
        ("3", "function-context"),
        ("4", "module-context"),
    )
)


def _marked(after: str, how: tuple[str, str]) -> dict:
    instruction, sentence = how
    if instruction == "patch":
        return a_patch(AT, sentence, f"{sentence} 6", after)
    return a_correct_setting(AT, sentence, after)


@pytest.mark.parametrize(
    ("topology", "stages"),
    [
        (CHAIN, FOUR_A_C_6),
        (
            (ROOT / "tests/fixtures/topologies/sequential.toml").read_text(
                encoding="utf-8"
            ),
            SEQUENTIAL,
        ),
    ],
    ids=["4a-4c-6", "sequential.toml"],
)
def test_staged_chain_T3_each_stage_reads_the_one_before_and_the_edits_accumulate(
    tmp_path, monkeypatch, capsys, topology, stages
):
    """`staged-chain-untested` T3: one marker per stage in one paragraph, each
    stage reading the text the stage before it set, and the run set holds all."""
    _a_run(tmp_path, topology)
    before = BASE.rstrip("\n")
    for name, role, after, how in stages:
        _stage_closed(
            tmp_path, monkeypatch, capsys, name, {role: {AT: _marked(after, how)}}
        )
        (row,) = [p for p in _binder_of(tmp_path, name).paragraphs if p.address == AT]
        assert row.raw_text == before, name
        before = after

    code, printed = _set_run(tmp_path, monkeypatch, capsys)
    assert code == 0, printed
    assert _drafts(tmp_path).keys() == {"m.py"}
    assert before in (tmp_path / "drafts" / "m.py").read_text(encoding="utf-8")


def test_E5_check_from_another_cwd_at_4c_passes_with_the_stage_root(
    tmp_path, monkeypatch, capsys
):
    _closed_4a(tmp_path, monkeypatch, capsys, CORRECTED)
    code, printed = _open(tmp_path, monkeypatch, capsys, "4c")
    assert code == 0, printed
    _filled(tmp_path, "4c", RECORRECTED)
    (copy,) = _copies(tmp_path, "4c")
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)
    code, printed = run_command(
        monkeypatch,
        capsys,
        check_command,
        "--edit-copy",
        str(copy),
        "--binder",
        str(received_binder_of(copy)),
        "--repo",
        str(tmp_path / "run" / "root4c"),
        with_stderr=True,
    )
    assert code == report.OK, printed
