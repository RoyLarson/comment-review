"""`commands/proof.py`: the CLI's console face over `flows/proof_setter.run`.

Moved from `tests/test_proof_setter.py` 2026-08-26 -- `tests/test_addresser_command.py`
is the standing precedent for a command's own file.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest
from conftest import SAMPLE, SRC, build, run_command
from helpers import (
    BASE,
    BOTH_FIXED,
    TWO,
    TYPOS,
    a_clean,
    a_closed_run,
    a_correct,
    a_correct_setting,
    answer,
    copies_over,
    deal,
    patched,
    proof_to_docket,
    taken_in_as_filed,
    turn,
)

from comment_review.binder.binder import bind
from comment_review.commands import proof as proof_command
from comment_review.commands import report
from comment_review.commands import turn as turn_command
from comment_review.docket.docket import Docket


def draft_of(repo, original):
    """Where `proof_repository` keeps the draft of `original`."""
    return repo.parent / "drafts" / original.relative_to(repo)


def prove_args(repo):
    """The `prove_unchanged` options naming `proof_repository`'s two roots."""
    return ("--repo", str(repo), "--drafts", str(repo.parent / "drafts"))


def proof_repository(tmp_path, before, suffix):
    """A checkout holding `pkg/source<suffix>`, and a draft of it beside.

    Neither is a git repository: `prove_unchanged` reads the original from
    the checkout and the draft from the drafts root. The draft starts as a
    copy of the original; a test writes its edit there.
    """
    repo = tmp_path / "repo"
    (repo / "pkg").mkdir(parents=True)
    target = repo / "pkg" / f"source{suffix}"
    target.write_bytes(before.encode("utf-8"))
    draft = draft_of(repo, target)
    draft.parent.mkdir(parents=True)
    draft.write_bytes(target.read_bytes())
    return repo, target


@pytest.mark.parametrize("failed_side", ["draft", "original", "both"])
@pytest.mark.parametrize("stage", ["lex", "place"])
def test_standalone_proof_admits_both_pages(
    tmp_path, monkeypatch, capsys, failed_side, stage
):
    from comment_review.commands import prove_unchanged as command
    from comment_review.flows import page_for
    from comment_review.reading.diagnostics import (
        ReadDiagnostic,
        ReadFailure,
        ReadStage,
    )
    from comment_review.reading.source import SourceSpan

    suffix = ".rs"

    before, after = "const value = 1; // before\r\n", "const value = 1; // after\r\n"
    repo, target = proof_repository(tmp_path, before, suffix)
    draft_of(repo, target).write_bytes(after.encode("utf-8"))
    real_page_for = page_for.page_for

    def failing_page(path, text, *args, **kwargs):
        failed = failed_side == "both" or text == (
            before if failed_side == "original" else after
        )
        if failed:
            return ReadFailure(
                (
                    ReadDiagnostic(
                        ReadStage(stage),
                        "refused-input",
                        "source refused",
                        SourceSpan(0, 1),
                    ),
                )
            )
        return real_page_for(path, text, *args, **kwargs)

    monkeypatch.setattr(page_for, "page_for", failing_page)
    code, out = run_command(
        monkeypatch, capsys, command, *prove_args(repo), str(target)
    )
    assert code == 1, out
    assert "PROVEN" not in out
    assert f"{stage}/refused-input" in out
    assert "line 1" in out and "column 0" in out


def test_standalone_cli_preserves_exact_mixed_unicode_snapshots(
    tmp_path, monkeypatch, capsys
):
    from comment_review.commands import prove_unchanged as command
    from comment_review.flows import page_for

    before = "# caf\u00e9\r\nx = '\u03bb'\r\nx += 'e\u0301'\n"
    after = "# changed\r\nx = '\u03bb'\r\nx += 'e\u0301'\n"
    repo, target = proof_repository(tmp_path, before, ".py")
    draft_of(repo, target).write_bytes(after.encode("utf-8"))
    real_page_for = page_for.page_for
    admitted = []

    def watching_page(path, text, *args, **kwargs):
        admitted.append(text)
        return real_page_for(path, text, *args, **kwargs)

    monkeypatch.setattr(page_for, "page_for", watching_page)
    code, out = run_command(
        monkeypatch, capsys, command, *prove_args(repo), str(target)
    )
    assert code == 0, out
    assert admitted == [before, after]
    assert "PROVEN    pkg/source.py" in out
    cli = subprocess.run(
        [
            sys.executable,
            str(SRC / "comment-review.py"),
            "prove_unchanged",
            *prove_args(repo),
            str(target),
        ],
        capture_output=True,
        encoding="utf-8",
        timeout=30,
        check=False,
    )
    assert cli.returncode == 0, cli.stdout + cli.stderr
    assert "PROVEN    pkg/source.py" in cli.stdout


def test_standalone_failed_or_unprovable_inputs_cannot_prove_equal(
    tmp_path, monkeypatch, capsys
):
    from comment_review.commands import prove_unchanged as command

    suffix = ".rs"

    repo, target = proof_repository(tmp_path, "int value = 1; /* open\r\n", suffix)
    code, out = run_command(
        monkeypatch, capsys, command, *prove_args(repo), str(target)
    )
    assert code == 1
    assert "PROVEN" not in out


@pytest.mark.parametrize(
    ("text", "suffix"),
    [
        ("/* only prose */\r\n", ".rs"),
        ("# only prose\r\n", ".py"),
    ],
    ids=["rs", "py"],
)
def test_standalone_a_file_with_no_code_line_proves_under_its_row(
    tmp_path, monkeypatch, capsys, text, suffix
):
    from comment_review.commands import prove_unchanged as command

    repo, target = proof_repository(tmp_path, text, suffix)
    code, out = run_command(
        monkeypatch, capsys, command, *prove_args(repo), str(target)
    )
    assert code == 0
    assert "PROVEN" in out


def test_standalone_an_unprovable_comparison_refuses_at_equal_text(
    tmp_path, monkeypatch
):
    from comment_review.flows import prove_unchanged
    from comment_review.reading.diagnostics import ReadDiagnostic, ReadStage
    from comment_review.reading.proof import UNPROVABLE, PreservationResult
    from comment_review.reading.rust.records import RustRead

    repo, target = proof_repository(tmp_path, "const VALUE: i32 = 1;\r\n", ".rs")
    unprovable = PreservationResult(
        False, (ReadDiagnostic(ReadStage.PLACE, UNPROVABLE, "not separated"),)
    )
    monkeypatch.setattr(RustRead, "preserved", lambda *_, **__: unprovable)
    report = prove_unchanged.run(repo, repo.parent / "drafts", [target], approved={})
    assert report.failures == 1
    assert all("PROVEN" not in message for message in report.messages)
    assert any("UNPROVABLE" in message for message in report.messages)


@pytest.mark.parametrize("failed_side", ["draft", "original"])
def test_standalone_strict_decode_failure_refuses(
    tmp_path, monkeypatch, capsys, failed_side
):
    from comment_review.commands import prove_unchanged as command

    suffix = ".rs"

    repo, target = proof_repository(tmp_path, "const value = 1;\r\n", suffix)
    (target if failed_side == "original" else draft_of(repo, target)).write_bytes(
        b"\xff"
    )
    code, out = run_command(
        monkeypatch, capsys, command, *prove_args(repo), str(target)
    )
    assert code == 1
    assert f"{failed_side}:" in out
    assert "decode/invalid-utf8" in out and "byte offset 0" in out


@pytest.mark.parametrize("text,suffix", [("", ".rs"), ("# comment\r\n", ".py")])
def test_standalone_empty_and_supported_comment_only_success(
    tmp_path, monkeypatch, capsys, text, suffix
):
    from comment_review.commands import prove_unchanged as command

    repo, target = proof_repository(tmp_path, text, suffix)
    code, out = run_command(
        monkeypatch, capsys, command, *prove_args(repo), str(target)
    )
    assert code == 0, out
    assert "PROVEN" in out


@pytest.mark.parametrize("absent", ["original", "draft"])
def test_standalone_an_absent_side_fails_naming_it(
    tmp_path, monkeypatch, capsys, absent
):
    from comment_review.commands import prove_unchanged as command

    repo, target = proof_repository(tmp_path, "const value = 1;\r\n", ".rs")
    (target if absent == "original" else draft_of(repo, target)).unlink()
    code, out = run_command(
        monkeypatch, capsys, command, *prove_args(repo), str(target)
    )
    assert code == 1
    assert f"FAIL      {absent}: " in out and "acquire/io-error" in out


def test_an_uncommitted_original_proves_with_no_git_and_no_base(
    tmp_path, monkeypatch, capsys
):
    """The original is read from the checkout, never from a commit.

    `proof_repository` makes no git repository at all, and the command takes
    no `--base`.
    """
    from comment_review.commands import prove_unchanged as command

    repo, target = proof_repository(tmp_path, "const value = 1; // old\r\n", ".rs")
    draft_of(repo, target).write_bytes(b"const value = 1; // new\r\n")
    code, out = run_command(
        monkeypatch, capsys, command, *prove_args(repo), str(target)
    )
    assert code == 0, out
    assert "PROVEN    pkg/source.rs" in out
    assert not (repo / ".git").exists()
    with pytest.raises(SystemExit) as refused:
        run_command(
            monkeypatch, capsys, command, *prove_args(repo), "--base", "HEAD", "x"
        )
    assert refused.value.code == 2
    assert "unrecognized arguments: --base" in capsys.readouterr().err


CRLF_STRING = '"""Doc."""\r\n\r\nS = """a\r\nb\r\n"""\r\n'


def test_an_unchanged_crlf_file_holding_a_multi_line_string_proves(
    tmp_path, monkeypatch, capsys
):
    """The tokens of a multi-line string that is not a docstring hold its line
    endings; both sides are read from disk, so they carry the same ones."""
    from comment_review.commands import prove_unchanged as command

    repo, target = proof_repository(tmp_path, CRLF_STRING, ".py")
    code, out = run_command(
        monkeypatch, capsys, command, *prove_args(repo), str(target)
    )
    assert code == 0, out
    assert "PROVEN    pkg/source.py" in out


def test_a_draft_differing_only_in_line_endings_fails_on_a_multi_line_string(
    tmp_path, monkeypatch, capsys
):
    """The string's line endings are part of its value, so an LF draft of a CRLF
    original changes executable code."""
    from comment_review.commands import prove_unchanged as command

    repo, target = proof_repository(tmp_path, CRLF_STRING, ".py")
    draft_of(repo, target).write_bytes(CRLF_STRING.replace("\r\n", "\n").encode())
    code, out = run_command(
        monkeypatch, capsys, command, *prove_args(repo), str(target)
    )
    assert code == 1, out
    assert "executable code DIFFERS" in out


def test_a_sibling_with_other_line_endings_does_not_fail_the_page(
    tmp_path, monkeypatch, capsys
):
    from comment_review.commands import prove_unchanged as command

    repo, target = proof_repository(tmp_path, "const value = 1; // old\r\n", ".rs")
    (target.parent / "sibling.txt").write_bytes(b"one\ntwo\n")
    draft_of(repo, target).write_bytes(b"const value = 1; // new\r\n")
    code, out = run_command(
        monkeypatch, capsys, command, *prove_args(repo), str(target)
    )
    assert code == 0, out
    assert "line endings" not in out and "sibling" not in out


def a_copy_on_disk(tmp_path, binder):
    """A role's filled `edit_copy`, written to disk, and the address it rules on.

    The address comes from the binder, not the page, and that is the whole
    reason this helper picks it. MEASURED 2026-09-02: a page of `SAMPLE` carries
    14 addresses and `bind` keeps the 5 that hold prose, so an address taken off
    the page -- `m.py@a2` -- matches no seeded slot, `copies_over` attaches
    nothing, and the copy goes out empty. The write phase copies only the
    files it modifies (`decision-log.md Process: #117`), so an empty copy
    schedules no page at all: a test asserting the revise holds `m.py` fails
    outright, rather than passing over a page it never touched. **The binder
    is what a role is handed; it is the only honest source for an address a
    mark can rule on.**

    !! SEEDED FROM THE REAL BINDER, not a synthetic one. The docket carries each
    page's sha straight off the sheet, and `proof_setter` refuses a page whose
    sha does not match the file it is about to set -- so a copy seeded from
    `a_binder_over`'s `"0" * 40` would refuse for a reason that has nothing to do
    with what this test asks.

    ! AND THROUGH `copies_over`, so the copy is the shape `distribute` produces
    rather than the shape this test expects; it also replaces the mark's
    placeholder sentence with the page's real one, which is what makes the
    claim verifiable.
    """
    # ! A COMMENT PLACE, `b` or `c`. The file's own matter gets no seeded slot,
    # so `f0` is not a place a role can rule on; and `a_correct`'s placeholder
    # change is a `#` line, which set into a docstring's place leaves that
    # place holding nothing, and the reread refuses it.
    address = next(
        b.address
        for b in binder.paragraphs
        if b.address and b.address.split("@")[-1][0] in "bc"
    )
    copy = copies_over(binder, {"block-context": {address: a_correct(address)}})[0]
    ruled = [m for s in copy["sheets"] for m in s["marks"] if m.get("instruction")]
    assert len(ruled) == 1, "the mark did not attach -- the copy would go out empty"
    where = tmp_path / "copy.json"
    where.write_text(json.dumps(copy), encoding="utf-8", newline="")
    return where, address


class TestProofTakesAnEditCopy:
    """`P57`. The command's input is an `edit_copy`; the docket is transcribed
    on the flow's first step -- `decision-log.md Process: #76`.

    ! `--docket` IS GONE, not aliased. It named the artifact rather than the
    boundary, and `P58`/`P59` give the two boundaries their own flags.
    """

    def test_a_filled_copy_pulls_a_revise(self, tmp_path, monkeypatch, capsys):
        repo, binder, _page = _tree(tmp_path)
        copy, _address = a_copy_on_disk(tmp_path, binder)

        code, out = run_command(
            monkeypatch,
            capsys,
            proof_command,
            "--copy",
            str(copy),
            "--repo",
            str(repo),
            "--out",
            str(tmp_path / "r1"),
        )
        assert code == 0, out
        # The page must have changed, not merely exist. Since `decision-log.md
        # Process: #117` a revise holds only the pages the docket schedules,
        # so `m.py` is present here because `a_copy_on_disk` seeded a real
        # mark for it -- this asserts that mark actually landed, not merely
        # that the docket named the page.
        drafted = (tmp_path / "r1" / "m.py").read_text(encoding="utf-8")
        assert drafted != SAMPLE

    def test_the_docket_flag_is_gone(self, monkeypatch, capsys):
        """! ASSERTED, NOT ASSUMED. A flag that still parses would let an old
        invocation run and produce a confusing refusal deep in the load."""
        with pytest.raises(SystemExit):
            run_command(
                monkeypatch,
                capsys,
                proof_command,
                "--docket",
                "d.json",
                "--repo",
                ".",
                "--out",
                "o",
            )

    def test_to_docket_writes_a_docket_and_stops(self, tmp_path, monkeypatch, capsys):
        """`P58`. The run stops at the transcribe: a docket on disk, no revise.

        !! IT IS WHAT KEEPS `Docket.serialize` HONEST. Roy, 2026-09-02, wanted
        the serialization kept *"for some logging or troubleshooting ... since it
        is there it is worth not reinventing"* -- and a method kept on stated
        intent is what `scripts/dead_sweep.py` reports and a later session
        deletes. This flag is its production reader.
        """
        repo, binder, _page = _tree(tmp_path)
        copy, _address = a_copy_on_disk(tmp_path, binder)
        out = tmp_path / "d.json"

        code, _out = run_command(
            monkeypatch,
            capsys,
            proof_command,
            "--copy",
            str(copy),
            "--repo",
            str(repo),
            "--to-docket",
            str(out),
        )
        assert code == 0
        # ! READ BACK THROUGH THE BOUNDARY, so what it wrote is a docket rather
        # than merely a file -- `Docket.deserialize` is the same parse
        # `--from-docket` will use at `P59`.
        docket, why = Docket.deserialize(str(out), json.loads(out.read_text()))
        assert docket is not None, why
        assert docket.schedules[0].path == "m.py"

    def test_to_docket_does_not_need_an_out(self, tmp_path, monkeypatch, capsys):
        """! `--out` IS THE REVISE ROOT, and this run pulls no revise. Requiring
        it would make the caller name a directory nothing writes to."""
        repo, binder, _page = _tree(tmp_path)
        copy, _address = a_copy_on_disk(tmp_path, binder)
        code, _out = run_command(
            monkeypatch,
            capsys,
            proof_command,
            "--copy",
            str(copy),
            "--repo",
            str(repo),
            "--to-docket",
            str(tmp_path / "d.json"),
        )
        assert code == 0
        assert not (tmp_path / "r1").exists()

    def test_without_to_docket_an_out_is_still_required(self, monkeypatch, capsys):
        """! A NAMED REFUSAL AT EXIT 2, NOT AN ARGPARSE ERROR. `--out` cannot be
        `required=True` any more, because `--to-docket` runs without one -- so
        the requirement is conditional, and argparse has no way to state it. The
        message says which flag would have made the run legal, which
        `error: the following arguments are required: --out` could not.
        """
        code, out = run_command(
            monkeypatch, capsys, proof_command, "--copy", "c.json", "--repo", "."
        )
        assert code == 2
        assert "--to-docket" in out

    def test_the_two_halves_compose(self, tmp_path, monkeypatch, capsys):
        """`P59`. Stop at the docket, start again from it, and the revise is the
        same one a single run produces.

        !! THAT ROUND TRIP IS THE ASSERTION, not that each half runs. Either
        half could work while the pair disagreed -- a docket that serialises
        something `Docket.deserialize` reads back differently would pass two
        separate tests and still break the boundary the flags exist to create.
        """
        repo, binder, _page = _tree(tmp_path)
        copy, _address = a_copy_on_disk(tmp_path, binder)

        whole, out = run_command(
            monkeypatch,
            capsys,
            proof_command,
            "--copy",
            str(copy),
            "--repo",
            str(repo),
            "--out",
            str(tmp_path / "one-run"),
        )
        assert whole == 0, out

        stopped, out = run_command(
            monkeypatch,
            capsys,
            proof_command,
            "--copy",
            str(copy),
            "--repo",
            str(repo),
            "--to-docket",
            str(tmp_path / "d.json"),
        )
        assert stopped == 0, out

        resumed, out = run_command(
            monkeypatch,
            capsys,
            proof_command,
            "--from-docket",
            str(tmp_path / "d.json"),
            "--repo",
            str(repo),
            "--out",
            str(tmp_path / "two-runs"),
        )
        assert resumed == 0, out

        one = (tmp_path / "one-run" / "m.py").read_text(encoding="utf-8")
        two = (tmp_path / "two-runs" / "m.py").read_text(encoding="utf-8")
        assert one == two
        assert one != SAMPLE, "neither run set anything -- the claim is vacuous"

    def test_from_docket_and_copy_are_exclusive(self, tmp_path, monkeypatch, capsys):
        """! ONE OF THEM IS REQUIRED, and both together name two inputs for one
        run. argparse states this itself, so the exit is its own."""
        with pytest.raises(SystemExit):
            run_command(
                monkeypatch,
                capsys,
                proof_command,
                "--copy",
                "c.json",
                "--from-docket",
                "d.json",
                "--repo",
                ".",
                "--out",
                str(tmp_path / "r1"),
            )

    def test_neither_input_is_refused(self, monkeypatch, capsys):
        with pytest.raises(SystemExit):
            run_command(monkeypatch, capsys, proof_command, "--repo", ".", "--out", "o")

    def test_from_docket_with_to_docket_is_refused_by_name(
        self, tmp_path, monkeypatch, capsys
    ):
        """! IT WOULD READ A DOCKET IN ORDER TO WRITE IT BACK OUT. Refused with a
        reason rather than performed, because a run that copies its own input is
        never what the caller meant."""
        code, out = run_command(
            monkeypatch,
            capsys,
            proof_command,
            "--from-docket",
            "d.json",
            "--to-docket",
            "e.json",
            "--repo",
            ".",
        )
        assert code == 2
        assert "--from-docket" in out and "--to-docket" in out

    def test_a_copy_that_will_not_read_reports_and_writes_nothing(
        self, tmp_path, monkeypatch, capsys
    ):
        """! THE REFUSAL PATH KEEPS ITS SHAPE. `CANNOT READ` is what SKILL.md
        tells the agent to look for, and the three load steps still fail for
        their own reasons -- `Process: #67`."""
        bad = tmp_path / "copy.json"
        bad.write_text('{"role": "block-context"}', encoding="utf-8", newline="")
        repo = tmp_path / "repo"
        repo.mkdir()
        code, out = run_command(
            monkeypatch,
            capsys,
            proof_command,
            "--copy",
            str(bad),
            "--repo",
            str(repo),
            "--out",
            str(tmp_path / "r1"),
        )
        assert code == 2
        assert "CANNOT READ" in out
        assert not (tmp_path / "r1").exists()


#: The one place the proof cases deal, and the roles that patch it.
PLACE = "m.py@b1"
HANDS = ("block-context", "function-context")


def a_stage_dealt(tmp_path, monkeypatch, capsys) -> int:
    """Two roles patching one paragraph, folded once: `proof0.json`.

    The two patch different lines, so the place composes and is carried
    forward to each of them -- `decision-log.md Process: #180`.
    """
    return deal(tmp_path, monkeypatch, capsys, patched(PLACE), {PLACE: TYPOS})


def a_closed_proof(tmp_path, monkeypatch, capsys):
    """That stage settled by a turn in which both roles accept: `proof1.json`.

    Returns:
        `(the closed proof, the repo its addresses answer to)`.
    """
    assert a_stage_dealt(tmp_path, monkeypatch, capsys) == report.REREADS
    code, out = turn(
        tmp_path,
        monkeypatch,
        capsys,
        1,
        *[
            answer(
                tmp_path,
                1,
                role,
                PLACE,
                instruction="clean",
                reason="that reads right",
            )
            for role in HANDS
        ],
    )
    assert code == report.OK, out
    return tmp_path / "proof1.json", tmp_path / "repo"


def a_closed_proof_with_a_place_that_stands(tmp_path, monkeypatch, capsys):
    """One place corrected and one left standing, closed by the chief taking
    the one role's correction in.

    The filter's cases need a place the write end sets nothing at, which
    `a_closed_proof` above has none of: its one place carries a text.
    """
    code = deal(
        tmp_path,
        monkeypatch,
        capsys,
        {
            "block-context": {
                "m.py@b1": a_correct_setting("m.py@b1", "two", TWO),
                "m.py@b2": a_clean("m.py@b2"),
            }
        },
        {"m.py@b1": BASE, "m.py@b2": "# four\n"},
    )
    assert code == report.REREADS
    taken_in_as_filed(tmp_path, monkeypatch, capsys)
    return tmp_path / "final.json", tmp_path / "repo"


def test_a_bad_place_is_named_the_same_by_every_command_that_reads_the_proof(
    tmp_path, monkeypatch, capsys
):
    """A place that will not read is named where the proof is read, so `turn`
    and `proof` refuse the same file with the same line."""
    assert a_stage_dealt(tmp_path, monkeypatch, capsys) == report.REREADS
    path = tmp_path / "proof0.json"
    wire = json.loads(path.read_text(encoding="utf-8"))
    assert len(wire["places"]) == 1
    wire["places"].append("not a place")
    path.write_text(json.dumps(wire), encoding="utf-8")
    named = f"{path}: place 2: a place must be an object"

    code, out = run_command(
        monkeypatch,
        capsys,
        turn_command,
        "--proof",
        str(path),
        "--proof-out",
        str(tmp_path / "proof1.json"),
        "--batch-out",
        str(tmp_path / "batch2.json"),
        with_stderr=True,
    )
    assert code != 0 and named in out, out
    code, out = run_command(
        monkeypatch,
        capsys,
        proof_command,
        "--jacket",
        str(a_closed_run(tmp_path / "repo", path)),
        "--repo",
        str(tmp_path / "repo"),
        "--out",
        str(tmp_path / "r1"),
        with_stderr=True,
    )
    assert code != 0 and named in out, out


MODULE_PLACE = "m.py@a0"


def a_closed_proof_adding_a_module_docstring(tmp_path, monkeypatch, capsys):
    """`m.py@b1` corrected and a module docstring added at `m.py@a0`, closed by
    the chief taking both in as filed."""
    code = deal(
        tmp_path,
        monkeypatch,
        capsys,
        {"block-context": {"m.py@b1": a_correct_setting("m.py@b1", "two", TWO)}},
        {"m.py@b1": BASE},
        placed={
            "block-context": [
                {
                    "address": MODULE_PLACE,
                    "instruction": "add",
                    "claim": {"missing": "what the module holds", "anchor": "`v0`"},
                    "reason": "the module is explained nowhere",
                    "sources": [{"cite": "m.py:1"}],
                    "change": '"""Hold four values."""\n',
                }
            ]
        },
    )
    assert code == report.REREADS
    taken_in_as_filed(tmp_path, monkeypatch, capsys)
    return tmp_path / "final.json", tmp_path / "repo"


def _set(tmp_path, monkeypatch, capsys, proof: Path, repo: Path, *only: str):
    """`proof --jacket` over a run whose one stage closed on `proof`, into r1."""
    return run_command(
        monkeypatch,
        capsys,
        proof_command,
        "--jacket",
        str(a_closed_run(repo, proof)),
        "--repo",
        str(repo),
        *(flag for one in only for flag in ("--only", one)),
        "--out",
        str(tmp_path / "r1"),
    )


class TestProofTakesAClosedProof:
    """The write end's input is each stage's closed proof: the decided places
    the fold closed on, transcribed straight -- `decision-log.md Process: #184`.

    The text these cases land is one no filed mark sets.
    """

    def test_a_closed_proof_pulls_a_revise(self, tmp_path, monkeypatch, capsys):
        proof, repo = a_closed_proof(tmp_path, monkeypatch, capsys)
        code, out = _set(tmp_path, monkeypatch, capsys, proof, repo)
        assert code == 0, out
        drafted = (tmp_path / "r1" / "m.py").read_text(encoding="utf-8")
        assert BOTH_FIXED in drafted

    def test_a_closed_proof_transcribes_to_one_alteration_per_decided_place(
        self, tmp_path, monkeypatch, capsys
    ):
        proof, repo = a_closed_proof(tmp_path, monkeypatch, capsys)
        where = tmp_path / "d.json"
        assert proof_to_docket(proof, repo, where) == []
        docket, why = Docket.deserialize(str(where), json.loads(where.read_text()))
        assert docket is not None, why
        (schedule,) = docket.schedules
        assert schedule.path == "m.py"
        assert [one.text for one in schedule.alterations] == [BOTH_FIXED]

    def test_a_proof_still_carrying_a_place_forward_is_refused(
        self, tmp_path, monkeypatch, capsys
    ):
        """The fold has not settled that text, so there is nothing to set and
        no revise is pulled. The place is named on stdout."""
        assert a_stage_dealt(tmp_path, monkeypatch, capsys) == report.REREADS
        code, out = _set(
            tmp_path, monkeypatch, capsys, tmp_path / "proof0.json", tmp_path / "repo"
        )
        assert code == 1, out
        assert PLACE in out and "nothing drafted" in out
        assert not (tmp_path / "r1").exists()

    def test_a_jacket_that_will_not_read_reports_and_writes_nothing(
        self, tmp_path, monkeypatch, capsys
    ):
        bad = tmp_path / "jacket.json"
        bad.write_text('{"format": 7}', encoding="utf-8", newline="")
        repo = tmp_path / "repo"
        repo.mkdir()
        code, out = run_command(
            monkeypatch,
            capsys,
            proof_command,
            "--jacket",
            str(bad),
            "--repo",
            str(repo),
            "--out",
            str(tmp_path / "r1"),
            with_stderr=True,
        )
        assert code == 2, out
        assert "jacket.json" in out
        assert not (tmp_path / "r1").exists()

    def test_only_sets_the_named_place_and_leaves_the_rest(
        self, tmp_path, monkeypatch, capsys
    ):
        """`decision-log.md Process: #192`: a partial approval is a place
        filter on the closed proof. The place named is set; the place the
        author did not approve is left as the page has it."""
        proof, repo = a_closed_proof(tmp_path, monkeypatch, capsys)
        code, out = _set(tmp_path, monkeypatch, capsys, proof, repo, f"4c:{PLACE}")
        assert code == 0, out
        assert BOTH_FIXED in (tmp_path / "r1" / "m.py").read_text(encoding="utf-8")

    def test_an_only_the_proof_does_not_carry_is_refused_by_name(
        self, tmp_path, monkeypatch, capsys
    ):
        proof, repo = a_closed_proof(tmp_path, monkeypatch, capsys)
        code, out = _set(tmp_path, monkeypatch, capsys, proof, repo, "4c:m.py@b9")
        assert code == 1, out
        assert "m.py@b9" in out
        assert not (tmp_path / "r1").exists()
        # Its own opener: the proof decided everything it holds, and what
        # could not be honoured is the list of places -- so this must not
        # read as a fact about the proof.
        assert "the approval names a place this proof cannot set" in out
        assert "the proof decided nothing that can be set" not in out

    def test_an_unchanged_approved_place_produces_no_message_or_alteration(
        self, tmp_path, monkeypatch, capsys
    ):
        proof, repo = a_closed_proof_with_a_place_that_stands(
            tmp_path, monkeypatch, capsys
        )
        code, out = _set(
            tmp_path, monkeypatch, capsys, proof, repo, "4c:m.py@b1", "4c:m.py@b2"
        )
        assert code == 0, out
        assert "m.py@b2" not in out
        assert TWO in (tmp_path / "r1" / "m.py").read_text(encoding="utf-8")
        assert "# four\n" in (tmp_path / "r1" / "m.py").read_text(encoding="utf-8")

    @pytest.mark.parametrize(
        ("only", "imprimatur"),
        [
            ((), {"m.py": ["a0"]}),
            ((f"4c:{MODULE_PLACE}",), {"m.py": ["a0"]}),
            (("4c:m.py@b1",), {"m.py": []}),
        ],
        ids=["jacket", "only-the-docstring", "only-the-comment"],
    )
    def test_proof_records_the_docstrings_it_was_approved_to_change(
        self, tmp_path, monkeypatch, capsys, only, imprimatur
    ):
        """`decision-log.md Process: #415`: beside its drafts, `proof` writes
        each page's `a` places an accepted alteration set, for stage 7b."""
        proof, repo = a_closed_proof_adding_a_module_docstring(
            tmp_path, monkeypatch, capsys
        )
        code, out = _set(tmp_path, monkeypatch, capsys, proof, repo, *only)
        assert code == 0, out
        record = json.loads(
            (tmp_path / "r1" / "imprimatur.json").read_text(encoding="utf-8")
        )
        assert record == imprimatur

    def test_only_without_a_proof_is_an_argument_error(
        self, tmp_path, monkeypatch, capsys
    ):
        """It filters the closed proofs' places, and a copy has none: a run naming
        `--only` beside `--copy` asked for something this command cannot do,
        which is an input error rather than a refusal further down."""
        code, out = run_command(
            monkeypatch,
            capsys,
            proof_command,
            "--copy",
            "c.json",
            "--repo",
            ".",
            "--only",
            "m.py@b1",
            "--out",
            str(tmp_path / "r1"),
        )
        assert code == 2, out
        assert "--only" in out and "--jacket" in out

    @pytest.mark.parametrize("other", ["--copy", "--from-docket"])
    def test_the_proof_is_exclusive_with_the_other_inputs(
        self, tmp_path, monkeypatch, capsys, other
    ):
        """One run has one input, and argparse states it rather than a
        hand-written check."""
        with pytest.raises(SystemExit):
            run_command(
                monkeypatch,
                capsys,
                proof_command,
                "--jacket",
                "j.json",
                other,
                "x.json",
                "--repo",
                ".",
                "--out",
                str(tmp_path / "r1"),
            )


def _tree(tmp_path):
    """A one-file repo, and the binder taken over it.

    The file the mark builders cite is copied in beside it, so a copy's
    sources verify against the repo it is drafted from.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "m.py").write_text(SAMPLE, encoding="utf-8", newline="")
    cited = repo / "src" / "comment_review" / "desk" / "proof" / "mark.py"
    cited.parent.mkdir(parents=True)
    cited.write_bytes(
        (SRC / "comment_review" / "desk" / "proof" / "mark.py").read_bytes()
    )
    page = build(SAMPLE)
    return repo, bind([page], read_from={"root": str(repo)}), page


class TestTheCommand:
    """`commands/proof.py` exposes this flow and orchestrates nothing: it takes
    a binder and hands it straight to `proof_setter.run`.

    ! `galley` WAS THE OLD NAME FOR IT, from 2026-08-26 until the CLI alias
    was removed 2026-08-28. It used to resolve an address through
    `rows_of(binder)` -- the binder-row coupling this chain was ruled out of
    -- and keep a staleness comparison, an overlap guard and a draft loop of
    its own; all of it went, and the name is gone with it. See
    `docs/history.md`."""

    def test_the_command_holds_no_orchestration(self):
        """! A COMMAND EXPOSES A FLOW; IT IS NOT ONE. The gather's command took
        446 lines calling page_for directly while its flow kept 261 of helpers,
        until TODO/the-flow-lives-in-the-command.md T2 moved the chain."""
        text = (SRC / "comment_review" / "commands" / "proof.py").read_text(
            encoding="utf-8"
        )
        for forbidden in ("page_for", "galley.reset", "set_page"):
            assert forbidden not in text

    def test_proof_is_a_named_command(self):
        from comment_review.__main__ import COMMANDS

        assert "proof" in COMMANDS

    def test_A_VALID_RUN_READS_THE_DOCKET_AND_DRAFTS(
        self, tmp_path, capsys, monkeypatch
    ):
        """!! THE HAPPY PATH HAD NO TEST UNTIL 2026-08-26, and the two argv
        cases below are why it looked covered: both stop at the `--out` guard,
        which returns 2 BEFORE the docket is read. So nothing exercised the
        line that turns an argparse flag into an attribute.

        !! MEASURED THE SAME DAY: renaming `--notations` to `--docket` left the
        body reading `args.alterations`, and `cmd.main()` raised
        `AttributeError: 'Namespace' object has no attribute 'alterations'` --
        past 946 green tests, ruff, ty, the build gate and the floor check. It
        was found by running the command, which is the only thing that could.

        !! THE INPUT IS AN `edit_copy` SINCE `P57`, and the note this docstring
        used to carry moved with it. It read *"THE DOCKET IS HAND-WRITTEN ... it
        arrives from outside the system, so a helper building it would only
        agree with the reader"* -- true while `--docket` was the input, and not
        true now: what arrives from outside is a role's copy, and the docket is
        transcribed from it inside the flow. The hand-written docket is the
        `--from-docket` case at `P59`, where it is an input again.
        """
        repo, binder, _page = _tree(tmp_path)
        # ! THE ADDRESS IS DISCOVERED FROM THE BINDER, never hardcoded -- see
        # `a_copy_on_disk`, which is where the choice and its measurement live.
        copy, _address = a_copy_on_disk(tmp_path, binder)
        code, out = run_command(
            monkeypatch,
            capsys,
            proof_command,
            "--repo",
            str(repo),
            "--copy",
            str(copy),
            "--out",
            str(tmp_path / "out"),
        )
        assert code == 0, out
        assert "drafted for review" in out
        # ! AND THE SOURCE IS UNTOUCHED, which is the whole promise of a draft.
        assert (repo / "m.py").read_text(encoding="utf-8") == SAMPLE

    def test_an_out_that_overlaps_the_repo_is_REFUSED(
        self, tmp_path, capsys, monkeypatch
    ):
        """!! THE DESTRUCTIVE CASE, MEASURED 2026-08-22 on the galley: on an
        overlap the per-file guard is satisfied by the SOURCE FILE ITSELF, so
        the draft was written over the file under review at exit 0."""
        from comment_review.commands import proof as cmd

        repo, _, _ = _tree(tmp_path)
        monkeypatch.setattr(
            "sys.argv",
            [
                "proof",
                "--repo",
                str(repo),
                "--copy",
                "n.json",
                "--out",
                str(repo / "inside"),
            ],
        )
        assert cmd.main() == 2
        assert "REFUSED" in capsys.readouterr().out

    def test_an_out_that_NAMES_A_FILE_prints_a_reason(
        self, tmp_path, capsys, monkeypatch
    ):
        """IMPORTANT, measured 2026-08-25: `run`'s
        `into.mkdir(parents=True, exist_ok=True)` raises `FileExistsError` when
        `--out` names a regular file -- `exist_ok` covers an existing DIRECTORY
        only -- and it reached the console as a traceback. Every other bad
        input in this command prints a reason and returns 2."""
        from comment_review.commands import proof as cmd

        repo, _, _ = _tree(tmp_path)
        not_a_dir = tmp_path / "notadir"
        not_a_dir.write_text("x", encoding="utf-8")
        monkeypatch.setattr(
            "sys.argv",
            [
                "proof",
                "--repo",
                str(repo),
                "--copy",
                "n.json",
                "--out",
                str(not_a_dir),
            ],
        )
        assert cmd.main() == 2
        assert "is not a directory" in capsys.readouterr().out

    def test_an_out_that_ALREADY_EXISTS_is_REFUSED(self, tmp_path, capsys, monkeypatch):
        """`--out` is the revise root, and this command's own `out.exists()`
        check is what refuses one already there: `pull` makes `--out` itself
        with `into.mkdir`, which would otherwise raise `FileExistsError` even
        on an empty directory, which `undraftable` (a non-directory or an
        overlap) does not refuse. The same convention as every other bad
        `--out` above: a reason printed at exit 2, not a traceback."""
        from comment_review.commands import proof as cmd

        repo, _, _ = _tree(tmp_path)
        already_there = tmp_path / "out"
        already_there.mkdir()
        monkeypatch.setattr(
            "sys.argv",
            [
                "proof",
                "--repo",
                str(repo),
                "--copy",
                "n.json",
                "--out",
                str(already_there),
            ],
        )
        assert cmd.main() == 2
        assert "already exists" in capsys.readouterr().out


def test_a_file_no_reader_claims_is_unchecked(tmp_path, monkeypatch, capsys):
    from comment_review.commands import prove_unchanged as command

    repo, target = proof_repository(tmp_path, "// before\r\n", ".js")
    draft_of(repo, target).write_bytes(b"// after\r\n")
    code, out = run_command(
        monkeypatch, capsys, command, *prove_args(repo), str(target)
    )
    assert code == 0, out
    assert (
        "UNCHECKED  pkg/source.js: no reader -- formatter and compiler are the check"
        in out
    )
    assert "FAIL" not in out and "proven" not in out


@pytest.mark.parametrize("suffix", [".md", ".toml", ".json", ".png"])
def test_a_file_outside_the_source_suffixes_fails(
    tmp_path, monkeypatch, capsys, suffix
):
    from comment_review.commands import prove_unchanged as command

    repo, target = proof_repository(tmp_path, "# before\r\n", suffix)
    draft_of(repo, target).write_bytes(b"# after\r\n")
    code, out = run_command(
        monkeypatch, capsys, command, *prove_args(repo), str(target)
    )
    assert code == 1, out
    assert f"FAIL      pkg/source{suffix}" in out
    assert "unsupported-language" in out
    assert "UNCHECKED" not in out and "PROVEN" not in out


def test_the_summary_never_counts_a_freeform_path_as_proven(
    tmp_path, monkeypatch, capsys
):
    from comment_review.commands import prove_unchanged as command
    from comment_review.flows import prove_unchanged

    repo, target = proof_repository(tmp_path, "x = 1  # before\r\n", ".py")
    note = target.parent / "note.js"
    note.write_bytes(b"// before\r\n")
    draft_of(repo, note).write_bytes(b"// after\r\n")
    report = prove_unchanged.run(
        repo, repo.parent / "drafts", [target, note], approved={}
    )
    assert report.freeform == 1 and report.failures == 0
    base = prove_args(repo)
    code, out = run_command(monkeypatch, capsys, command, *base, str(target), str(note))
    assert code == 0, out
    assert "1 proven, 1 UNCHECKED" in out
    code, out = run_command(monkeypatch, capsys, command, *base, str(note))
    assert code == 0, out
    assert "proven" not in out and "1 UNCHECKED" in out


def test_a_python_file_that_fails_to_read_still_fails(tmp_path, monkeypatch, capsys):
    from comment_review.commands import prove_unchanged as command

    repo, target = proof_repository(tmp_path, "x = 1\r\n", ".py")
    draft_of(repo, target).write_bytes(b"\xff")
    code, out = run_command(
        monkeypatch, capsys, command, *prove_args(repo), str(target)
    )
    assert code == 1, out
    assert "PROVEN" not in out
    assert "no reader" not in out and "FAIL" in out


def test_a_failing_python_file_beside_a_freeform_one_exits_1(
    tmp_path, monkeypatch, capsys
):
    from comment_review.commands import prove_unchanged as command

    repo, target = proof_repository(tmp_path, "x = 1\r\n", ".py")
    note = target.parent / "note.js"
    note.write_bytes(b"// before\r\n")
    draft_of(repo, target).write_bytes(b"\xff")
    draft_of(repo, note).write_bytes(b"// after\r\n")
    base = prove_args(repo)
    code, out = run_command(monkeypatch, capsys, command, *base, str(target), str(note))
    assert code == 1, out
    assert "UNCHECKED  pkg/note.js: no reader" in out
    assert "UNCHECKED (no reader)" not in out
