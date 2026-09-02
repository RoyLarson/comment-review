"""`commands/proof.py`: the CLI's console face over `flows/proof_setter.run`.

Moved from `tests/test_proof_setter.py` 2026-08-26 -- `tests/test_addresser_command.py`
is the standing precedent for a command's own file.
"""

import json

import pytest
from conftest import SAMPLE, SRC, build, run_command
from helpers import a_correct, copies_over

from comment_review.binder.binder import bind
from comment_review.commands import proof as proof_command
from comment_review.docket.docket import Docket


def a_copy_on_disk(tmp_path, binder):
    """A role's filled `edit_copy`, written to disk, and the address it rules on.

    !! THE ADDRESS COMES FROM THE BINDER, NOT THE PAGE, and that is the whole
    reason this helper picks it. MEASURED 2026-09-02: a page of `SAMPLE` carries
    14 addresses and `bind` keeps the 5 that hold prose, so an address taken off
    the page -- `m.py@a2` -- matches no seeded slot, `copies_over` attaches
    nothing, and the copy goes out EMPTY. A test then asserting that the revise
    holds `m.py` passes anyway, because `pull` copies the whole tree before it
    sets a single page. **The binder is what a role is handed; it is the only
    honest source for an address a mark can rule on.**

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
    address = next(b.address for b in binder.paragraphs if b.address)
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
        # !! THE PAGE MUST HAVE CHANGED, not merely exist. `pull` copies the whole
        # tree before it sets anything, so `m.py` is present under a revise even
        # when the docket is empty -- which is exactly what this assertion said
        # until 2026-09-02, over a copy that carried no mark at all.
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
