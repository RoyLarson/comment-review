"""One admission at every entry point: `flows.verify.admit`.

`collate`, `check`, `mark` and `proof --copy` each admit a copy through the
one flow, and differ only in the inputs they hand it. A rule whose input an
entry point holds gives that entry point the verdict it gives `collate`; a
rule whose input it lacks is not asked there, and the entry point's own
docstring names the input (`decision-log.md` #397, #398).

! IT RUNS EACH COMMAND'S `main()` IN-PROCESS, over a real binder written to
`tmp_path / "repo"` and copies from the real `seed`.
"""

import json
from pathlib import Path

import pytest
from conftest import run_command
from helpers import (
    a_clean,
    a_correct_setting,
    a_jacket_naming,
    a_query,
    a_real_binder_over,
    copies_over,
)

from comment_review.commands import check, collate, mark, proof
from comment_review.desk.collator import Problem
from comment_review.desk.proof.mark import Shape

BASE = "# one\n# two\n# three\n"
PLACES = {"m.py@b1": BASE, "m.py@b5": BASE}

#: A row admitting fewer instructions than a copy may widen its own field to.
COMPACTING = (
    '[[stage]]\nname = "4c"\nkind = "editorial"\n'
    'admits = ["patch", "drop", "add", "clean"]\n'
    '  [[stage.dispatch]]\n  role = "block-context"\n'
)


def _clean_copy(binder) -> dict:
    """block-context's copy with a `clean` at both places: one the fold admits."""
    marks = {address: a_clean(address) for address in PLACES}
    return copies_over(binder, {"block-context": marks})[0]


def _sha(copy: dict) -> None:
    copy["sheets"][0]["sha"] = "0" * 40


def _verbatim(copy: dict) -> None:
    entry = copy["sheets"][0]["marks"][0]
    entry.update(a_correct_setting(entry["address"], "two", "# one\n# 2\n# three"))
    entry["sources"] = [{**entry["sources"][0], "verbatim": "not the cited line"}]


def _anchors(copy: dict) -> None:
    """A second `clean` at `m.py@b1` carrying another anchor: the fold refuses
    a place whose marks disagree on its anchor."""
    marks = copy["sheets"][0]["marks"]
    marks.append({**marks[0], "anchor": "v9 = 9"})


def _stage(copy: dict) -> None:
    copy["stage"] = "6"


def _admits(copy: dict) -> None:
    copy["admits"] = ["patch", "drop", "add", "clean", "correct"]
    _correct(copy)


def _correct(copy: dict) -> None:
    entry = copy["sheets"][0]["marks"][0]
    entry.update(a_correct_setting(entry["address"], "two", "# one\n# 2\n# three"))


def _written(tmp_path, copy: dict, topology: str | None = None) -> dict:
    """The copy, binder and topology files, by name."""
    paths = {"copy": tmp_path / "copy.json", "binder": tmp_path / "binder.json"}
    paths["copy"].write_text(json.dumps(copy), encoding="utf-8")
    if topology is not None:
        paths["topology"] = tmp_path / "t.toml"
        paths["topology"].write_text(topology, encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _binder(tmp_path):
    binder = a_real_binder_over(tmp_path / "repo", PLACES)
    (tmp_path / "binder.json").write_text(
        json.dumps(binder.serialize()), encoding="utf-8"
    )
    return binder


def _check(tmp_path, monkeypatch, capsys, files):
    return run_command(
        monkeypatch,
        capsys,
        check,
        "--edit-copy",
        files["copy"],
        "--binder",
        files["binder"],
        with_stderr=True,
    )


def _collate(tmp_path, monkeypatch, capsys, files):
    topology = files.get("topology")
    argv = a_jacket_naming(
        Path(files["binder"]),
        [Path(files["copy"])],
        topology=Path(topology).read_text(encoding="utf-8") if topology else "",
    )
    argv += ["--proof-out", str(tmp_path / "proof.json")]
    return run_command(monkeypatch, capsys, collate, *argv, with_stderr=True)


def _proof_copy(tmp_path, monkeypatch, capsys, files):
    return run_command(
        monkeypatch,
        capsys,
        proof,
        "--copy",
        files["copy"],
        "--repo",
        str(tmp_path / "repo"),
        "--to-docket",
        str(tmp_path / "docket.json"),
    )


def _mark(tmp_path, monkeypatch, capsys, files, *argv):
    return run_command(
        monkeypatch,
        capsys,
        mark,
        "--edit-copy",
        files["copy"],
        "--repo",
        str(tmp_path / "repo"),
        *argv,
    )


def _refusals(out: str) -> list[str]:
    """The refusal lines a command printed, which open with the role."""
    return sorted(
        line for line in out.splitlines() if line.startswith("block-context ")
    )


#: tamper -> (the topology collate is given, what check is not given, or None
#: where check holds every input the refusing rule reads, and a phrase of the
#: refusal collate prints).
TAMPERS = {
    "sheet sha": (_sha, None, None, "sha disagrees with stage binder"),
    "verbatim": (_verbatim, None, None, "`verbatim`"),
    "differing anchors": (_anchors, None, None, "carry differing anchors"),
    "stage": (_stage, None, "stage label", "a copy folds only in the stage"),
    "admits widened": (
        _admits,
        COMPACTING,
        "topology row",
        "what a stage admits is the row's",
    ),
}


@pytest.mark.parametrize("tamper", TAMPERS)
def test_check_and_collate_give_one_verdict_on_a_tampered_copy(
    tmp_path, monkeypatch, capsys, tamper
):
    """The tamper table: `check` gives `collate`'s verdict wherever it holds
    the rule's input, and its docstring names the input where it does not."""
    change, topology, lacks, refusal = TAMPERS[tamper]
    copy = _clean_copy(_binder(tmp_path))
    change(copy)
    files = _written(tmp_path, copy, topology)
    collated, by_collate = _collate(tmp_path, monkeypatch, capsys, files)
    checked, by_check = _check(tmp_path, monkeypatch, capsys, files)
    assert collated in (1, 2), by_collate
    assert refusal in by_collate, by_collate
    if lacks is None:
        assert checked == collated, (by_check, by_collate)
        assert _refusals(by_check) == _refusals(by_collate)
    else:
        assert checked == 0, by_check
        assert lacks in " ".join((check.__doc__ or "").split())


def test_a_clean_copy_is_admitted_by_every_entry_point(tmp_path, monkeypatch, capsys):
    files = _written(tmp_path, _clean_copy(_binder(tmp_path)))
    assert _collate(tmp_path, monkeypatch, capsys, files)[0] == 0
    assert _check(tmp_path, monkeypatch, capsys, files)[0] == 0
    assert _proof_copy(tmp_path, monkeypatch, capsys, files)[0] == 0


def test_one_rule_added_to_admit_refuses_at_every_entry_point(
    tmp_path, monkeypatch, capsys
):
    """C2's mutation check: a rule added in one place is asked by all four."""

    def fake(copies, *args, **kwargs):
        return [
            Problem(one.role, entry.address, "the fake rule refuses this")
            for one in copies
            for sheet in one.sheets
            for entry in sheet.marks
        ]

    monkeypatch.setattr(
        "comment_review.flows.verify._admitted_problems", fake, raising=False
    )
    binder = _binder(tmp_path)
    files = _written(tmp_path, _clean_copy(binder))
    for run in (_collate, _check, _proof_copy):
        code, out = run(tmp_path, monkeypatch, capsys, files)
        assert code == 1, (run.__name__, out)
        assert "the fake rule refuses this" in out, (run.__name__, out)
    seeded = copies_over(binder, {"block-context": {}})[0]
    files = _written(tmp_path, seeded)
    code, out = _mark(
        tmp_path,
        monkeypatch,
        capsys,
        files,
        "--address",
        "m.py@b1",
        "--instruction",
        "clean",
        *_cited(tmp_path),
    )
    assert code == 1, out
    assert "the fake rule refuses this" in out


def _cited(tmp_path) -> list[str]:
    """`--cite` and `--verbatim` naming line 1 of the page itself."""
    first = (tmp_path / "repo" / "m.py").read_text(encoding="utf-8").splitlines()[0]
    return ["--cite", "m.py:1", "--verbatim", first]


def test_a_refusal_beside_a_pending_human_question_exits_one_listing_both(
    tmp_path, monkeypatch, capsys
):
    """#398: the trial fold runs while a human question stands, so a refusal
    only the fold finds is listed beside the question, and the exit is 1."""
    copy = _clean_copy(_binder(tmp_path))
    marks = copy["sheets"][0]["marks"]
    marks[0].update(a_query("m.py@b1", Shape.HUMAN_REVIEW_NECESSARY))
    marks.append({**marks[1], "anchor": "v9 = 9"})
    files = _written(tmp_path, copy)
    code, out = _collate(tmp_path, monkeypatch, capsys, files)
    assert code == 1, out
    assert "asks the human m.py@b1" in out, out
    assert "block-context m.py@b5: the marks at m.py@b5 carry differing anchors" in (
        out
    ), out
    assert not (tmp_path / "proof.json").exists()


def test_mark_refuses_a_verbatim_the_cited_line_does_not_hold(
    tmp_path, monkeypatch, capsys
):
    """#397: a cite is verified when the mark is filed, as collate verifies it."""
    seeded = copies_over(_binder(tmp_path), {"block-context": {}})[0]
    files = _written(tmp_path, seeded)
    before = (tmp_path / "copy.json").read_bytes()
    code, out = _mark(
        tmp_path,
        monkeypatch,
        capsys,
        files,
        "--address",
        "m.py@b1",
        "--instruction",
        "clean",
        "--cite",
        "m.py:1",
        "--verbatim",
        "not the cited line",
    )
    assert code == 1, out
    assert "m.py@b1" in out, out
    assert (tmp_path / "copy.json").read_bytes() == before


def test_mark_places_a_ruling_whose_cite_holds(tmp_path, monkeypatch, capsys):
    seeded = copies_over(_binder(tmp_path), {"block-context": {}})[0]
    files = _written(tmp_path, seeded)
    code, out = _mark(
        tmp_path,
        monkeypatch,
        capsys,
        files,
        "--address",
        "m.py@b1",
        "--instruction",
        "clean",
        *_cited(tmp_path),
    )
    assert code == 0, out


def test_check_on_a_copy_holding_a_human_query_exits_five(
    tmp_path, monkeypatch, capsys
):
    """A human query is an ask, never fed to the trial fold, which would
    refuse it: `check` exits `ASKS_THE_HUMAN`, not `BROKEN`."""
    copy = _clean_copy(_binder(tmp_path))
    copy["sheets"][0]["marks"][0].update(
        a_query("m.py@b1", Shape.HUMAN_REVIEW_NECESSARY)
    )
    files = _written(tmp_path, copy)
    code, out = _check(tmp_path, monkeypatch, capsys, files)
    assert code == check.ASKS_THE_HUMAN, out
    assert "human query must be replaced" not in out, out


def _unadmittable(tmp_path) -> dict:
    """A seeded copy whose sheet claims a reading the installed reader does not
    give: a page identity that will not admit."""
    copy = copies_over(_binder(tmp_path), {"block-context": {}})[0]
    copy["sheets"][0]["reading"]["reader"] = "another-reader"
    return copy


def test_mark_exits_two_on_stderr_for_a_page_identity_that_will_not_admit(
    tmp_path, monkeypatch, capsys
):
    """#401: an identity refusal is an input that cannot be read, never a
    ruling sent back to the role."""
    files = _written(tmp_path, _unadmittable(tmp_path))
    before = (tmp_path / "copy.json").read_bytes()
    for flags in (
        ("--address", "m.py@b1", "--instruction", "clean", *_cited(tmp_path)),
        ("--address", "m.py@b1", "--instruction", "clean", "--withdraw"),
    ):
        monkeypatch.setattr("sys.argv", ["mark", "--edit-copy", files["copy"], *flags])
        code = mark.main()
        printed = capsys.readouterr()
        assert code == mark.UNREADABLE, printed
        assert printed.out == "", printed.out
        assert "regather" in printed.err and "block-context" in printed.err
    assert (tmp_path / "copy.json").read_bytes() == before


def test_proof_copy_exits_two_on_stderr_for_a_page_identity_that_will_not_admit(
    tmp_path, monkeypatch, capsys
):
    files = _written(tmp_path, _unadmittable(tmp_path))
    monkeypatch.setattr(
        "sys.argv",
        [
            "proof",
            "--copy",
            files["copy"],
            "--repo",
            str(tmp_path / "repo"),
            "--to-docket",
            str(tmp_path / "docket.json"),
        ],
    )
    code = proof.main()
    printed = capsys.readouterr()
    assert code == 2, printed
    assert printed.out == "", printed.out
    assert "regather" in printed.err and "block-context" in printed.err
    assert not (tmp_path / "docket.json").exists()


@pytest.mark.parametrize("withdrawing", [False, True])
def test_mark_admits_each_page_identity_once(
    tmp_path, monkeypatch, capsys, withdrawing
):
    """One `mark` call is one load: the copy's pages are compared once, and
    the admission of the placed ruling reuses that table."""
    from comment_review.flows import fill as fill_flow
    from comment_review.flows import verify

    seeded = copies_over(_binder(tmp_path), {"block-context": {}})[0]
    files = _written(tmp_path, seeded)
    placing = ("--address", "m.py@b1", "--instruction", "clean", *_cited(tmp_path))
    if withdrawing:
        assert _mark(tmp_path, monkeypatch, capsys, files, *placing)[0] == 0
    calls = []
    real = fill_flow.admit_pages

    def count(*sources):
        calls.append([(label, len(list(records))) for label, records in sources])
        return real(*sources)

    monkeypatch.setattr(fill_flow, "admit_pages", count)
    monkeypatch.setattr(verify, "admit_pages", count)
    flags = (
        ("--address", "m.py@b1", "--instruction", "clean", "--withdraw")
        if withdrawing
        else placing
    )
    code, out = _mark(tmp_path, monkeypatch, capsys, files, *flags)
    assert code == 0, out
    assert calls == [[("edit_copy: block-context", 1)]]
