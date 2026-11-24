"""A compacting stage, end to end: dealt the over-cap places, folded, set.

`decision-log.md Process: #193`. Compaction is an ordinary stage over the
tree the review's closed proofs set -- the pages are gathered again, the role is
dealt a copy holding only the `b` and `c` places whose text runs over the cap,
it files the edit instructions with `mark`, and its copy is folded and set
like any stage's.

Driven through the commands' own `main()`, so what this asserts is what a
run does: nothing here calls the fold or the write end directly.
"""

import json
from pathlib import Path

from conftest import run_command
from helpers import (
    a_closed_run,
    a_jacket_naming,
    a_real_binder_over,
    taken_in_as_filed,
)

from comment_review.commands import check as check_command
from comment_review.commands import collate as collate_command
from comment_review.commands import gather as gather_command
from comment_review.commands import mark as mark_command
from comment_review.commands import proof as proof_command
from comment_review.commands import report
from comment_review.desk.stages import Kind, Stage
from comment_review.flows.distribute import assigned_binder, seed
from comment_review.flows.proof_io import load_binder

#: The stage a compacting run declares, as its row and as the topology text
#: that builds it. The two are the same row: the flow takes the `Stage` and
#: `collate` reads the file.
COMPACTING = Stage(
    name="6",
    kind=Kind.EDITORIAL,
    reads="original",
    cap=2,
    series=("b", "c"),
    admits=("patch", "drop", "add", "clean"),
    dispatches=(),
)

TOPOLOGY = (
    '[[stage]]\nname = "6"\nkind = "editorial"\nreads = "original"\n'
    'cap = 2\nseries = ["b", "c"]\n'
    'admits = ["patch", "drop", "add", "clean"]\n'
    '  [[stage.dispatch]]\n  role = "block-context"\n'
)

#: A five-line paragraph over the cap, and a one-line paragraph under it.
OVER = (
    "# The store keeps every lookup it has ever answered.\n"
    "# Nothing is removed from it.\n"
    "# The count is what the report prints.\n"
    "# It is printed once a day.\n"
    "# Nobody reads it twice."
)
UNDER = "# Counted once."

#: What the role condenses it to, written out by hand.
CONDENSED = "# Every lookup is kept, and the count is printed once a day."


def _run(tmp_path, monkeypatch, capsys, stage: Stage | None):
    """A binder over one page, and the copy `stage` deals from it."""
    root = tmp_path / "repo"
    binder = a_real_binder_over(root, {"m.py@b1": OVER, "m.py@b2": UNDER})
    (tmp_path / "binder.json").write_text(
        json.dumps(binder.serialize()), encoding="utf-8"
    )
    copy = tmp_path / "copy.json"
    copy.write_text(json.dumps(seed(binder, "block-context", stage)), encoding="utf-8")
    return root, copy


def _addresses(copy) -> list[str]:
    held = json.loads(copy.read_text(encoding="utf-8"))
    return [mark["address"] for sheet in held["sheets"] for mark in sheet["marks"]]


def test_the_stage_is_dealt_the_over_cap_place_alone(tmp_path, monkeypatch, capsys):
    _root, copy = _run(tmp_path, monkeypatch, capsys, COMPACTING)
    assert _addresses(copy) == ["m.py@b1"]


def test_a_whole_paragraph_is_condensed_with_one_patch(tmp_path, monkeypatch, capsys):
    """`patch` quotes the clause it replaces, so a condensation of the whole
    paragraph quotes the whole paragraph: `claim.from` is the five lines and
    `claim.to` is the two that replace them. The change is derived from the
    claim against the page, so the role types no `--change`.
    """
    root, copy = _run(tmp_path, monkeypatch, capsys, COMPACTING)
    (tmp_path / "from.txt").write_text(OVER, encoding="utf-8")
    (tmp_path / "to.txt").write_text(CONDENSED, encoding="utf-8")
    code, out = run_command(
        monkeypatch,
        capsys,
        mark_command,
        "--edit-copy",
        str(copy),
        "--repo",
        str(root),
        "--address",
        "m.py@b1",
        "--instruction",
        "patch",
        "--from",
        "@" + str(tmp_path / "from.txt"),
        "--to",
        "@" + str(tmp_path / "to.txt"),
        "--reason",
        "five lines state what two state",
        "--cite",
        "m.py:1",
    )
    assert code == mark_command.OK, out
    placed = json.loads(copy.read_text(encoding="utf-8"))["sheets"][0]["marks"][0]
    assert placed["change"] == CONDENSED


def test_a_correct_is_refused_naming_the_stage(tmp_path, monkeypatch, capsys):
    root, copy = _run(tmp_path, monkeypatch, capsys, COMPACTING)
    code, out = run_command(
        monkeypatch,
        capsys,
        mark_command,
        "--edit-copy",
        str(copy),
        "--repo",
        str(root),
        "--address",
        "m.py@b1",
        "--instruction",
        "correct",
        "--false",
        "Nobody reads it twice.",
        "--true",
        "Nobody reads it at all.",
        "--reason",
        "the report is read once",
        "--cite",
        "m.py:1",
    )
    assert code == mark_command.BROKEN, out
    assert "6" in out and "correct" in out


def test_the_condensed_text_folds_and_is_set(tmp_path, monkeypatch, capsys):
    """The stage's one role files a lone proposal at a place no other role
    read, so it is put to the chief (`decision-log.md Process: #387`), and
    once the chief takes it in, `proof --jacket` sets the closed proof's
    decided place. Nothing about the write end changes for a compacting stage.
    """
    root, copy = _run(tmp_path, monkeypatch, capsys, COMPACTING)
    (tmp_path / "from.txt").write_text(OVER, encoding="utf-8")
    (tmp_path / "to.txt").write_text(CONDENSED, encoding="utf-8")
    code, out = run_command(
        monkeypatch,
        capsys,
        mark_command,
        "--edit-copy",
        str(copy),
        "--repo",
        str(root),
        "--address",
        "m.py@b1",
        "--instruction",
        "patch",
        "--from",
        "@" + str(tmp_path / "from.txt"),
        "--to",
        "@" + str(tmp_path / "to.txt"),
        "--reason",
        "five lines state what two state",
        "--cite",
        "m.py:1",
    )
    assert code == mark_command.OK, out

    binder, why = load_binder(tmp_path / "binder.json")
    assert binder is not None, why
    received = tmp_path / "received.json"
    received.write_text(
        json.dumps(assigned_binder(binder, COMPACTING).serialize()), encoding="utf-8"
    )
    flags = a_jacket_naming(
        tmp_path / "binder.json",
        [copy],
        stage="6",
        topology=TOPOLOGY,
        received=[received],
        root=root,
    )
    code, out = run_command(
        monkeypatch,
        capsys,
        collate_command,
        *flags,
        "--proof-out",
        str(tmp_path / "proof.json"),
    )
    assert code == report.REREADS, out
    assert "composed m.py@b1: copy-chief (composition)" in out
    taken_in_as_filed(tmp_path, monkeypatch, capsys, proof="proof.json")

    code, out = run_command(
        monkeypatch,
        capsys,
        proof_command,
        "--jacket",
        str(a_closed_run(root, tmp_path / "final.json")),
        "--repo",
        str(root),
        "--out",
        str(tmp_path / "set"),
    )
    assert code == 0, out
    drafted = (tmp_path / "set" / "m.py").read_text(encoding="utf-8")
    assert CONDENSED in drafted
    assert UNDER in drafted, "the place the stage never dealt was set over"


def test_an_ordinary_stage_over_the_same_binder_deals_both_places(
    tmp_path, monkeypatch, capsys
):
    """The control: without the three keys the same binder hands the role
    every place it ever held, so the narrowing above is the row's doing and
    not the fixture's."""
    _root, copy = _run(tmp_path, monkeypatch, capsys, None)
    assert _addresses(copy) == ["m.py@b1", "m.py@b2"]


def test_a_stage_6_copy_names_the_proof_pages_root_mark_and_check_read(
    tmp_path, monkeypatch, capsys
):
    """Stage 6 is gathered from the tree `stage open` builds for it, so the
    copy it seeds names that tree as its `read_from.root`. `mark` with no
    `--repo` admits a ruling against the copy's own root, and compact.md's
    `check` passes `--repo <stage tree>`: both read one tree."""
    monkeypatch.chdir(tmp_path)
    pages = tmp_path / "run" / "proof4c"
    a_real_binder_over(pages, {"m.py@b1": OVER, "m.py@b2": UNDER})
    code, out = run_command(
        monkeypatch,
        capsys,
        gather_command,
        "--repo",
        "run/proof4c",
        "--out",
        "run/binder6.json",
        "m.py",
        with_stderr=True,
    )
    assert code == 0, out
    binder, why = load_binder(Path("run/binder6.json"))
    assert binder is not None, why
    wire = seed(binder, "block-context", COMPACTING)
    assert (Path.cwd() / wire["read_from"]["root"]).resolve() == pages.resolve()
    copy = tmp_path / "copy.json"
    copy.write_text(json.dumps(wire), encoding="utf-8")
    (tmp_path / "from.txt").write_text(OVER, encoding="utf-8")
    (tmp_path / "to.txt").write_text(CONDENSED, encoding="utf-8")
    code, out = run_command(
        monkeypatch,
        capsys,
        mark_command,
        "--edit-copy",
        str(copy),
        "--address",
        "m.py@b1",
        "--instruction",
        "patch",
        "--from",
        "@" + str(tmp_path / "from.txt"),
        "--to",
        "@" + str(tmp_path / "to.txt"),
        "--reason",
        "five lines state what two state",
        "--cite",
        "m.py:1",
    )
    assert code == mark_command.OK, out
    # The received binder `distribute` writes beside the copy.
    received = tmp_path / "received.json"
    received.write_text(
        json.dumps(assigned_binder(binder, COMPACTING).serialize()), encoding="utf-8"
    )
    code, out = run_command(
        monkeypatch,
        capsys,
        check_command,
        "--edit-copy",
        str(copy),
        "--binder",
        str(received),
        "--repo",
        str(pages),
    )
    assert code == check_command.OK, out
