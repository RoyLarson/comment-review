"""`commands/proof.py`: the CLI's console face over `flows/proof_setter.run`.

Moved from `tests/test_proof_setter.py` 2026-08-26 -- `tests/test_addresser_command.py`
is the standing precedent for a command's own file.
"""

import json

import pytest
from conftest import SAMPLE, SRC, build
from helpers import a_correct, copies_over

from comment_review.binder.binder import bind
from comment_review.commands import proof as proof_command


def a_copy_on_disk(tmp_path, binder, address):
    """A role's filled `edit_copy`, written to disk for the command to read.

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
    copy = copies_over(binder, {"block-context": {address: a_correct(address)}})[0]
    where = tmp_path / "copy.json"
    where.write_text(json.dumps(copy), encoding="utf-8", newline="")
    return where


def run(monkeypatch, capsys, *argv):
    monkeypatch.setattr("sys.argv", ["proof", *argv])
    code = proof_command.main()
    return code, capsys.readouterr().out


class TestProofTakesAnEditCopy:
    """`P57`. The command's input is an `edit_copy`; the docket is transcribed
    on the flow's first step -- `decision-log.md Process: #76`.

    ! `--docket` IS GONE, not aliased. It named the artifact rather than the
    boundary, and `P58`/`P59` give the two boundaries their own flags.
    """

    def test_a_filled_copy_pulls_a_revise(self, tmp_path, monkeypatch, capsys):
        repo, binder, page = _tree(tmp_path)
        address = next(b.address for b in page.paragraphs if b.address)
        copy = a_copy_on_disk(tmp_path, binder, address)

        code, out = run(
            monkeypatch,
            capsys,
            "--copy",
            str(copy),
            "--repo",
            str(repo),
            "--out",
            str(tmp_path / "r1"),
        )
        assert code == 0, out
        assert (tmp_path / "r1" / "m.py").exists()

    def test_the_docket_flag_is_gone(self, monkeypatch, capsys):
        """! ASSERTED, NOT ASSUMED. A flag that still parses would let an old
        invocation run and produce a confusing refusal deep in the load."""
        with pytest.raises(SystemExit):
            run(monkeypatch, capsys, "--docket", "d.json", "--repo", ".", "--out", "o")

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
        code, out = run(
            monkeypatch,
            capsys,
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


def _tree(tmp_path):
    """A one-file repo, and the binder taken over it."""
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "m.py").write_text(SAMPLE, encoding="utf-8", newline="")
    page = build(SAMPLE)
    return repo, bind([page], read_from={"root": str(repo), "revise": 0}), page


class TestTheCommand:
    """`commands/proof.py` exposes this flow and orchestrates nothing: it takes
    a binder and hands it straight to `proof_setter.run`.

    ! `galley` WAS THE OLD NAME FOR IT, from 2026-08-26 until the CLI alias
    was removed 2026-08-28. It used to resolve an address through
    `rows_of(census)` -- the binder-row coupling this chain was ruled out of
    -- and keep a staleness comparison, an overlap guard and a draft loop of
    its own; all of it went, and the name is gone with it. See
    `docs/history.md`."""

    def test_the_command_holds_no_orchestration(self):
        """! A COMMAND EXPOSES A FLOW; IT IS NOT ONE. `commands/census.py` took
        446 lines calling page_for directly while flows/census.py kept 261 of
        helpers. See TODO/the-flow-lives-in-the-command.md."""
        text = (SRC / "comment_review" / "commands" / "proof.py").read_text(
            encoding="utf-8"
        )
        for forbidden in ("page_for", "galley.reset", "set_page", "code_fingerprint"):
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
        repo, binder, page = _tree(tmp_path)
        # ! DISCOVERED FROM THE PAGE, never hardcoded -- a literal cue is a
        # fixture asserting what the walk emitted last time someone looked.
        address = next(
            b.address
            for b in page.paragraphs
            if b.address and any(x.strip() for x in b.raw_lines)
        )
        copy = a_copy_on_disk(tmp_path, binder, address)
        code, out = run(
            monkeypatch,
            capsys,
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
        """!! `--out` IS THE REVISE ROOT SINCE 2026-08-28, and `revise.pull`
        copies `--repo` into it with `shutil.copytree`, which raises
        `FileExistsError` on a directory that is already there -- even an
        empty one, which `undraftable` (a non-directory or an overlap) does
        not refuse. The same convention as every other bad `--out` above:
        a reason printed at exit 2, not a traceback."""
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
