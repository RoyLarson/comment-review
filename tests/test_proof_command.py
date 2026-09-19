"""`commands/proof.py`: the CLI's console face over `flows/proof_setter.run`.

Moved from `tests/test_proof_setter.py` 2026-08-26 -- `tests/test_addresser_command.py`
is the standing precedent for a command's own file.
"""

import json

import pytest
from conftest import SAMPLE, SRC, build, run_command
from helpers import (
    BASE,
    BOTH_FIXED,
    TWO,
    TYPOS,
    a_clean,
    a_correct,
    a_correct_setting,
    answer,
    copies_over,
    deal,
    patched,
    turn,
)

from comment_review.binder.binder import bind
from comment_review.commands import collate as collate_command
from comment_review.commands import proof as proof_command
from comment_review.docket.docket import Docket


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
    assert a_stage_dealt(tmp_path, monkeypatch, capsys) == collate_command.REREADS
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
    assert code == collate_command.OK, out
    return tmp_path / "proof1.json", tmp_path / "repo"


def a_closed_proof_with_a_place_that_stands(tmp_path, monkeypatch, capsys):
    """One place corrected and one left standing, settled at the first fold.

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
    assert code == collate_command.OK
    return tmp_path / "proof0.json", tmp_path / "repo"


class TestProofTakesAClosedProof:
    """`--proof` is the write end's input: the decided places the fold closed
    on, transcribed straight -- `decision-log.md Process: #184`.

    The text these cases land is one no filed mark sets and that no
    synthesized mark could carry, since `patch` owes no sources.
    """

    def test_a_closed_proof_pulls_a_revise(self, tmp_path, monkeypatch, capsys):
        proof, repo = a_closed_proof(tmp_path, monkeypatch, capsys)
        code, out = run_command(
            monkeypatch,
            capsys,
            proof_command,
            "--proof",
            str(proof),
            "--repo",
            str(repo),
            "--out",
            str(tmp_path / "r1"),
        )
        assert code == 0, out
        drafted = (tmp_path / "r1" / "m.py").read_text(encoding="utf-8")
        assert BOTH_FIXED in drafted

    def test_to_docket_over_a_proof_writes_a_docket_and_stops(
        self, tmp_path, monkeypatch, capsys
    ):
        proof, repo = a_closed_proof(tmp_path, monkeypatch, capsys)
        where = tmp_path / "d.json"
        code, out = run_command(
            monkeypatch,
            capsys,
            proof_command,
            "--proof",
            str(proof),
            "--repo",
            str(repo),
            "--to-docket",
            str(where),
        )
        assert code == 0, out
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
        assert a_stage_dealt(tmp_path, monkeypatch, capsys) == collate_command.REREADS
        code, out = run_command(
            monkeypatch,
            capsys,
            proof_command,
            "--proof",
            str(tmp_path / "proof0.json"),
            "--repo",
            str(tmp_path / "repo"),
            "--out",
            str(tmp_path / "r1"),
        )
        assert code == 1, out
        assert "REFUSED" in out and PLACE in out
        assert not (tmp_path / "r1").exists()

    def test_a_proof_that_will_not_read_reports_and_writes_nothing(
        self, tmp_path, monkeypatch, capsys
    ):
        bad = tmp_path / "proof.json"
        bad.write_text('{"edit_copies": 7}', encoding="utf-8", newline="")
        repo = tmp_path / "repo"
        repo.mkdir()
        code, out = run_command(
            monkeypatch,
            capsys,
            proof_command,
            "--proof",
            str(bad),
            "--repo",
            str(repo),
            "--out",
            str(tmp_path / "r1"),
        )
        assert code == 2, out
        assert "CANNOT READ THE PROOF" in out
        assert not (tmp_path / "r1").exists()

    def test_only_sets_the_named_place_and_leaves_the_rest(
        self, tmp_path, monkeypatch, capsys
    ):
        """`decision-log.md Process: #192`: a partial approval is a place
        filter on the closed proof. The place named is set; the place the
        author did not approve is left as the page has it."""
        proof, repo = a_closed_proof(tmp_path, monkeypatch, capsys)
        code, out = run_command(
            monkeypatch,
            capsys,
            proof_command,
            "--proof",
            str(proof),
            "--repo",
            str(repo),
            "--only",
            PLACE,
            "--out",
            str(tmp_path / "r1"),
        )
        assert code == 0, out
        assert BOTH_FIXED in (tmp_path / "r1" / "m.py").read_text(encoding="utf-8")

    def test_an_only_the_proof_does_not_carry_is_refused_by_name(
        self, tmp_path, monkeypatch, capsys
    ):
        proof, repo = a_closed_proof(tmp_path, monkeypatch, capsys)
        code, out = run_command(
            monkeypatch,
            capsys,
            proof_command,
            "--proof",
            str(proof),
            "--repo",
            str(repo),
            "--only",
            "m.py@b9",
            "--out",
            str(tmp_path / "r1"),
        )
        assert code == 1, out
        assert "m.py@b9" in out
        assert not (tmp_path / "r1").exists()

    def test_a_named_place_with_nothing_to_set_is_named_on_stdout(
        self, tmp_path, monkeypatch, capsys
    ):
        """Approving a place that stands on the text already there is not a
        refusal, and it draws no `<path> -> <draft>` line either -- so the
        run says so, or the author is told nothing about a place they ruled
        on. `--only` is repeatable, and this run names two places."""
        proof, repo = a_closed_proof_with_a_place_that_stands(
            tmp_path, monkeypatch, capsys
        )
        code, out = run_command(
            monkeypatch,
            capsys,
            proof_command,
            "--proof",
            str(proof),
            "--repo",
            str(repo),
            "--only",
            "m.py@b1",
            "--only",
            "m.py@b2",
            "--out",
            str(tmp_path / "r1"),
        )
        assert code == 0, out
        assert "m.py@b2" in out
        assert TWO in (tmp_path / "r1" / "m.py").read_text(encoding="utf-8")

    def test_only_without_a_proof_is_an_argument_error(
        self, tmp_path, monkeypatch, capsys
    ):
        """! IT FILTERS THE PROOF'S PLACES, and a copy has none: a run naming
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
        assert "--only" in out and "--proof" in out

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
                "--proof",
                "p.json",
                other,
                "x.json",
                "--repo",
                ".",
                "--out",
                str(tmp_path / "r1"),
            )


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
