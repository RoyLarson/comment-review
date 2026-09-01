"""The `collate` command's exit codes and its report.

! IT RUNS `main()` IN-PROCESS with a built argv, not a subprocess -- the same
way the rest of this suite asks a question it can ask directly.
"""

import json

from helpers import (
    REPO,
    _keeping_only,
    a_binder_over,
    a_clean,
    a_correct,
    a_correct_setting,
    an_add,
    copies_over,
)

from comment_review.commands import collate as command

BASE = "# one\n# two\n# three\n"


def run(tmp_path, marks_by_role, monkeypatch, capsys):
    binder = a_binder_over({"m.py@b1": BASE})
    copies = copies_over(binder, marks_by_role)
    binder_path = tmp_path / "binder.json"
    binder_path.write_text(json.dumps(binder.serialize()), encoding="utf-8")
    paths = []
    for i, copy in enumerate(copies):
        path = tmp_path / f"copy{i}.json"
        path.write_text(json.dumps(copy), encoding="utf-8")
        paths.append(str(path))
    argv = [
        "collate",
        "--stage",
        "4c",
        "--binder",
        str(binder_path),
        "--out",
        str(tmp_path / "chief.json"),
    ]
    for path in paths:
        argv += ["--edit-copy", path]
    monkeypatch.setattr("sys.argv", argv)
    code = command.main()
    return code, capsys.readouterr().out


class TestExitCodes:
    def test_everything_resolved_exits_zero(self, tmp_path, monkeypatch, capsys):
        code, _out = run(
            tmp_path,
            {"block-context": {"m.py@b1": a_correct("m.py@b1")}},
            monkeypatch,
            capsys,
        )
        assert code == 0

    def test_a_reread_exits_three(self, tmp_path, monkeypatch, capsys):
        code, _out = run(
            tmp_path,
            {"block-context": {"m.py@b1": an_add("m.py@b1")}},
            monkeypatch,
            capsys,
        )
        assert code == 3

    def test_an_escalation_exits_four(self, tmp_path, monkeypatch, capsys):
        code, _out = run(
            tmp_path,
            {
                "block-context": {
                    "m.py@b1": a_correct_setting("m.py@b1", "two", "# a\n")
                },
                "function-context": {
                    "m.py@b1": a_correct_setting("m.py@b1", "two", "# b\n")
                },
            },
            monkeypatch,
            capsys,
        )
        assert code == 4

    def test_escalation_beats_reread_when_both_are_present(
        self, tmp_path, monkeypatch, capsys
    ):
        """Proves the ORDER `main` checks, not just its result: `if
        got.escalations: return ESCALATIONS` sits before `if got.rereads:
        return REREADS`, so a run holding both reports 4, never 3.

        !! DRIVEN THROUGH THE REAL FLOW, not a hand-built `Collated` -- a
        stage CAN produce both at once, on two different addresses of one
        page: `m.py@b1` gets two `correct` marks ruling on the same sentence
        with different `change`s (an escalation, per `desk.collator._outcome`
        -- `_identical` refuses since the changes disagree), and `m.py@b2`
        gets one `add` (a re-read, per the same function's `add` rule, which
        fires regardless of how many marks are owing at that place).

        Confirmed to FAIL if the two `if` branches in `commands/collate.py`
        are swapped -- see the task report for the swapped-branch run.
        """
        binder = a_binder_over({"m.py@b1": BASE, "m.py@b2": "# four\n# five\n# six\n"})
        copies = copies_over(
            binder,
            {
                "block-context": {
                    "m.py@b1": a_correct_setting("m.py@b1", "two", "# a\n"),
                    "m.py@b2": an_add("m.py@b2"),
                },
                "function-context": {
                    "m.py@b1": a_correct_setting("m.py@b1", "two", "# b\n"),
                },
            },
        )
        binder_path = tmp_path / "binder.json"
        binder_path.write_text(json.dumps(binder.serialize()), encoding="utf-8")
        paths = []
        for i, copy in enumerate(copies):
            path = tmp_path / f"copy{i}.json"
            path.write_text(json.dumps(copy), encoding="utf-8")
            paths.append(str(path))
        argv = [
            "collate",
            "--stage",
            "4c",
            "--binder",
            str(binder_path),
            "--out",
            str(tmp_path / "chief.json"),
        ]
        for path in paths:
            argv += ["--edit-copy", path]
        monkeypatch.setattr("sys.argv", argv)
        code = command.main()
        out = capsys.readouterr().out
        # ! BOTH OUTCOMES REACHED, so a failure of this precondition (rather
        # than of the order itself) is distinguishable from the real claim.
        assert "escalated" in out
        assert "re-read" in out
        assert code == 4

    def test_a_broken_mark_exits_one(self, tmp_path, monkeypatch, capsys):
        binder = a_binder_over({"m.py@b1": BASE})
        copies = copies_over(
            binder, {"block-context": {"m.py@b1": a_correct("m.py@b1")}}
        )
        copies[0]["sheets"][0]["marks"][0]["claim"] = {}
        binder_path = tmp_path / "binder.json"
        binder_path.write_text(json.dumps(binder.serialize()), encoding="utf-8")
        copy_path = tmp_path / "copy.json"
        copy_path.write_text(json.dumps(copies[0]), encoding="utf-8")
        monkeypatch.setattr(
            "sys.argv",
            [
                "collate",
                "--stage",
                "4c",
                "--binder",
                str(binder_path),
                "--out",
                str(tmp_path / "chief.json"),
                "--edit-copy",
                str(copy_path),
            ],
        )
        assert command.main() == 1

    def test_a_copy_with_no_role_exits_one_naming_the_reason(
        self, tmp_path, monkeypatch, capsys
    ):
        """The CLI's answer to a copy that names no role: exit 1, say so,
        write nothing.

        !! THE DOOR MOVED TWICE AND THIS TEST DID NOT. It was written against
        `desk.collator.UnnamedRole`, raised by `places()` inside `collate` --
        `problems_in` also reported a missing `role`, but nothing branched on
        that before `gather` and `reconcile` ran, so a role-less copy reached
        `places()` and the raise aborted `collate` before it could return a
        `Collated` at all. Then `P21` made the envelope parse report it as a
        `Problem` first, and `P42` deleted `UnnamedRole` outright. ! WHAT THE
        TEST ASSERTS -- the exit code, the reason on the reader's screen, and
        no chief copy on disk -- is the same claim through all three, which is
        why it is a CLI test and not a test of whichever door is current.
        """
        binder = a_binder_over({"m.py@b1": BASE})
        copies = copies_over(
            binder, {"block-context": {"m.py@b1": a_correct("m.py@b1")}}
        )
        del copies[0]["role"]
        binder_path = tmp_path / "binder.json"
        binder_path.write_text(json.dumps(binder.serialize()), encoding="utf-8")
        copy_path = tmp_path / "copy.json"
        copy_path.write_text(json.dumps(copies[0]), encoding="utf-8")
        monkeypatch.setattr(
            "sys.argv",
            [
                "collate",
                "--stage",
                "4c",
                "--binder",
                str(binder_path),
                "--out",
                str(tmp_path / "chief.json"),
                "--edit-copy",
                str(copy_path),
            ],
        )
        code = command.main()
        out = capsys.readouterr()
        assert code == 1
        # !! IT MOVED FROM stderr TO stdout ON 2026-08-31, and the exit code did
        # not. The envelope parse reports a copy with no `role` as a `Problem`
        # rather than letting a raise carry it -- `P21`, `decision-log.md
        # Process: #57`. A refusal that raises empties the report for every
        # OTHER role, which is what the report path fixes.
        assert "role" in out.out.lower()
        assert not (tmp_path / "chief.json").exists()

    def test_mismatched_roots_exit_one_naming_the_reason(
        self, tmp_path, monkeypatch, capsys
    ):
        """`desk.proof.MismatchedRoot`, raised by `gather()` inside
        `flows.collate.collate` on the second copy's disagreeing `read_from`.
        """
        binder = a_binder_over({"m.py@b1": BASE})
        copies = copies_over(
            binder,
            {
                "block-context": {"m.py@b1": a_correct("m.py@b1")},
                "function-context": {"m.py@b1": a_correct("m.py@b1", 2)},
            },
        )
        copies[1]["read_from"] = {"root": "somewhere/else", "revise": 0}
        binder_path = tmp_path / "binder.json"
        binder_path.write_text(json.dumps(binder.serialize()), encoding="utf-8")
        paths = []
        for i, copy in enumerate(copies):
            path = tmp_path / f"copy{i}.json"
            path.write_text(json.dumps(copy), encoding="utf-8")
            paths.append(str(path))
        argv = [
            "collate",
            "--stage",
            "4c",
            "--binder",
            str(binder_path),
            "--out",
            str(tmp_path / "chief.json"),
        ]
        for path in paths:
            argv += ["--edit-copy", path]
        monkeypatch.setattr("sys.argv", argv)
        code = command.main()
        err = capsys.readouterr().err
        assert code == 1
        assert "somewhere/else" in err

    def test_a_refusal_still_prints_the_problems_the_pass_found(
        self, tmp_path, monkeypatch, capsys
    ):
        """Finding #6 of the 2026-08-30 review, by RUNNING the real CLI.

        !! MEASURED BEFORE THE FIX: exit 1, **stdout EMPTY**, and only the
        REFUSED line on stderr. `collate` accumulates its `Problem`s into a
        local list and only reaches `return Collated(...)` past `gather`, so a
        refusal there made every one of them unrecoverable -- **one role's
        incompatible header blocking routing for every other role**, which is
        the opposite of Roy's rule that the errors stack so each can be fixed or
        sent back to the role that owes it.
        """
        binder = a_binder_over({"m.py@b1": BASE})
        copies = copies_over(
            binder,
            {
                "block-context": {"m.py@b1": a_correct("m.py@b1")},
                "function-context": {"m.py@b1": a_correct("m.py@b1", 2)},
            },
        )
        # one ROUTABLE problem, and one copy that cannot be reconciled with it
        copies[0]["sheets"][0]["marks"][0]["claim"] = {}
        copies[1]["read_from"] = {"root": "somewhere/else", "revise": 0}
        binder_path = tmp_path / "binder.json"
        binder_path.write_text(json.dumps(binder.serialize()), encoding="utf-8")
        argv = [
            "collate",
            "--stage",
            "4c",
            "--binder",
            str(binder_path),
            "--out",
            str(tmp_path / "chief.json"),
        ]
        for i, copy in enumerate(copies):
            path = tmp_path / f"copy{i}.json"
            path.write_text(json.dumps(copy), encoding="utf-8")
            argv += ["--edit-copy", str(path)]
        monkeypatch.setattr("sys.argv", argv)
        code = command.main()
        out = capsys.readouterr()
        assert code == 1
        assert "block-context" in out.out
        assert "m.py@b1" in out.out
        assert "somewhere/else" in out.err
        assert not (tmp_path / "chief.json").exists()

    def test_a_copy_missing_read_from_exits_one_not_a_traceback(
        self, tmp_path, monkeypatch, capsys
    ):
        """`desk.proof.gather`'s bare `copy["read_from"]` raises `KeyError` by
        design (its own `Raises:` calls this intentional), and until this fix
        that `KeyError` was not in `RECONCILE_ERRORS` -- so it escaped `main`
        uncaught, past this module's own promise that "a raise is not a
        refusal". Confirmed BEFORE the fix: `command.main()` raised `KeyError`
        out of this test rather than returning, with an eight-frame traceback
        -- see the task report for that run's output.
        """
        binder = a_binder_over({"m.py@b1": BASE})
        copies = copies_over(
            binder, {"block-context": {"m.py@b1": a_correct("m.py@b1")}}
        )
        del copies[0]["read_from"]
        binder_path = tmp_path / "binder.json"
        binder_path.write_text(json.dumps(binder.serialize()), encoding="utf-8")
        copy_path = tmp_path / "copy.json"
        copy_path.write_text(json.dumps(copies[0]), encoding="utf-8")
        monkeypatch.setattr(
            "sys.argv",
            [
                "collate",
                "--stage",
                "4c",
                "--binder",
                str(binder_path),
                "--out",
                str(tmp_path / "chief.json"),
                "--edit-copy",
                str(copy_path),
            ],
        )
        code = command.main()
        out = capsys.readouterr()
        assert code == 1
        # !! ALSO MOVED TO stdout ON 2026-08-31, and the history above still
        # holds -- the `KeyError` was real and escaping. The envelope parse now
        # names an absent `read_from` before `gather` is reached, so the
        # `RECONCILE_ERRORS` catch is no longer what answers this input.
        assert "read_from" in out.out
        assert not (tmp_path / "chief.json").exists()

    def test_drift_alone_exits_five_and_still_writes_the_chief(
        self, tmp_path, monkeypatch, capsys
    ):
        """`desk.collator.drift_in`'s ruling is that the COPY is never
        discarded over drift -- the chief is still written -- but before this
        fix `main` gave no exit-code signal that a drifted place fed the
        output: it returned 0, indistinguishable from a run with nothing to
        report at all."""
        binder = a_binder_over({"m.py@b1": BASE})
        copies = copies_over(
            binder, {"block-context": {"m.py@b1": a_correct("m.py@b1")}}
        )
        copies[0]["sheets"][0]["marks"][0]["raw_text"] = "# not what was seeded\n"
        binder_path = tmp_path / "binder.json"
        binder_path.write_text(json.dumps(binder.serialize()), encoding="utf-8")
        copy_path = tmp_path / "copy.json"
        copy_path.write_text(json.dumps(copies[0]), encoding="utf-8")
        out_path = tmp_path / "chief.json"
        monkeypatch.setattr(
            "sys.argv",
            [
                "collate",
                "--stage",
                "4c",
                "--binder",
                str(binder_path),
                "--out",
                str(out_path),
                "--edit-copy",
                str(copy_path),
            ],
        )
        code = command.main()
        assert code == command.DRIFT
        assert code == 5
        assert out_path.exists()

    def test_a_short_shard_exits_six_and_still_writes_the_chief(
        self, tmp_path, monkeypatch, capsys
    ):
        """`Process: #63` AT THE BOUNDARY WHERE THE FIX WAS MADE.

        !! MEASURED 2026-08-31, BEFORE IT: coverage findings rode in
        `got.problems`, `main` returned BROKEN on a non-empty `problems` before
        writing, and a round that settled `m.py@b1` threw that settled mark
        away. The ruling says a missing answer ROUTES and does not VOID the
        round -- *the places that did come back still settle*.

        ! IT WAS VERIFIED ONLY AT FLOW LEVEL UNTIL NOW. `TestShardCoverage`
        asserts `Collated.coverage`, which cannot see the command's exit code
        or whether the file was written -- and those two ARE the fix.
        """
        binder = a_binder_over({"m.py@b1": BASE, "m.py@b5": BASE})
        copies = copies_over(
            binder, {"block-context": {"m.py@b1": a_correct("m.py@b1")}}
        )
        short = _keeping_only(copies[0], ["m.py@b1"])
        binder_path = tmp_path / "binder.json"
        binder_path.write_text(json.dumps(binder.serialize()), encoding="utf-8")
        copy_path = tmp_path / "copy.json"
        copy_path.write_text(json.dumps(short), encoding="utf-8")
        out_path = tmp_path / "chief.json"
        monkeypatch.setattr(
            "sys.argv",
            [
                "collate",
                "--stage",
                "4c",
                "--binder",
                str(binder_path),
                "--out",
                str(out_path),
                "--edit-copy",
                str(copy_path),
                "--repo",
                str(REPO),
            ],
        )
        code = command.main()
        out = capsys.readouterr().out
        assert code == command.COVERAGE
        assert code == 6
        assert code != command.BROKEN
        assert "missing m.py@b5" in out
        # !! THE HALF THE FLOW-LEVEL TEST CANNOT SEE: the round still settled.
        assert out_path.exists()
        chief = json.loads(out_path.read_text(encoding="utf-8"))
        settled = [m["address"] for s in chief["sheets"] for m in s["marks"]]
        assert settled == ["m.py@b1"]

    def test_AN_ADDRESS_LESS_ENTRY_NAMES_ITS_PAGE_rather_than_the_whole_copy(
        self, tmp_path, monkeypatch, capsys
    ):
        """`(the copy)` MEANS ONE THING, and meant two until 2026-09-01.

        !! MEASURED: a bare string in `marks` printed `block-context (the copy):
        this mark: a mark must be an object`. That rendering means *this finding
        is about the whole document* -- a missing `role`, a bad `read_from`, a
        short shard -- and here it meant *we cannot tell you where*. Two facts,
        one label, and the one that needed a locator had none.

        ! THE COVERAGE LINE IS THE OTHER MEANING and stays, which is what makes
        this a distinction rather than a rename: both appear in this run.
        """
        binder = a_binder_over({"m.py@b1": BASE, "m.py@b5": BASE})
        copies = copies_over(binder, {"block-context": {"m.py@b1": a_clean("m.py@b1")}})
        copies[0]["sheets"][0]["marks"][0] = "not an object"
        binder_path = tmp_path / "binder.json"
        binder_path.write_text(json.dumps(binder.serialize()), encoding="utf-8")
        copy_path = tmp_path / "copy.json"
        copy_path.write_text(json.dumps(copies[0]), encoding="utf-8")
        monkeypatch.setattr(
            "sys.argv",
            [
                "collate",
                "--stage",
                "4c",
                "--binder",
                str(binder_path),
                "--out",
                str(tmp_path / "chief.json"),
                "--edit-copy",
                str(copy_path),
                "--repo",
                str(REPO),
            ],
        )
        command.main()
        out = capsys.readouterr().out
        assert "m.py mark 1: " in out, "the entry names the page it sits on"
        assert "(the copy): this mark" not in out
        assert "(the copy): a mark must be an object" not in out

    def test_a_place_HANDED_TO_A_ROLE_AND_NOT_RULED_ON_is_named_and_exits_six(
        self, tmp_path, monkeypatch, capsys
    ):
        """!! MEASURED 2026-09-01, AND IT EXITED `OK`. A role that keeps every
        slot and fills ONE is complete by every check the command ran:
        `_coverage_problems` asks whether the copy came BACK with the binder's
        addresses, and an untouched slot still carries its address. So over a
        three-place binder with `module-context` ruling one, `got.problems` and
        `got.coverage` were both EMPTY, the chief copy was written, and stdout
        said `0 places resolved` -- **which is also what an all-`clean` round
        prints**. Nothing separated *everyone read it and had nothing to say*
        from *a role skipped two thirds of its work*.

        ! `Collated.unruled` HELD THE ANSWER THE WHOLE TIME: the flow computed
        `{'module-context': ['m.py@b5', 'm.py@b7']}` and this command threw it
        away. That is why the fix is a report and a code, not a new check.

        ! IT TAKES `COVERAGE` DELIBERATELY -- see the constant. Both mean this
        role owes an answer at this address, and a code exists so a caller can
        branch on something it would act on differently.
        """
        binder = a_binder_over({"m.py@b1": BASE, "m.py@b5": BASE})
        # ! ONE ROLE, ONE RULING, EVERY SLOT KEPT -- the shape `_keeping_only`
        # cannot make, since that helper REMOVES the entry and this case needs
        # it present and unfilled.
        copies = copies_over(binder, {"block-context": {"m.py@b1": a_clean("m.py@b1")}})
        binder_path = tmp_path / "binder.json"
        binder_path.write_text(json.dumps(binder.serialize()), encoding="utf-8")
        copy_path = tmp_path / "copy.json"
        copy_path.write_text(json.dumps(copies[0]), encoding="utf-8")
        out_path = tmp_path / "chief.json"
        monkeypatch.setattr(
            "sys.argv",
            [
                "collate",
                "--stage",
                "4c",
                "--binder",
                str(binder_path),
                "--out",
                str(out_path),
                "--edit-copy",
                str(copy_path),
                "--repo",
                str(REPO),
            ],
        )
        code = command.main()
        out = capsys.readouterr().out
        assert code == command.COVERAGE
        assert code != command.OK, "a silently short round used to exit 0"
        # ! THE ADDRESS AND THE ROLE, so the task agent can send it back.
        assert "block-context m.py@b5: handed to this role and not ruled on" in out
        # ! AND THE PLACE THAT *WAS* RULED ON IS NOT NAMED -- a report that
        # listed every address would be a list nobody reads.
        assert "m.py@b1: handed to this role" not in out
        # ! THE ROUND STILL SETTLES, `Process: #63`.
        assert out_path.exists()

    def test_an_unreadable_input_exits_two(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setattr(
            "sys.argv",
            [
                "collate",
                "--stage",
                "4c",
                "--binder",
                str(tmp_path / "nowhere.json"),
                "--out",
                str(tmp_path / "chief.json"),
                "--edit-copy",
                str(tmp_path / "nowhere-either.json"),
            ],
        )
        assert command.main() == 2


class TestTheReport:
    def test_a_carried_forward_place_is_NAMED_not_counted(
        self, tmp_path, monkeypatch, capsys
    ):
        """`A-T2`: a run that settles 4 of 10 must say what became of the other
        6 rather than dropping them silently."""
        _code, out = run(
            tmp_path,
            {
                "block-context": {
                    "m.py@b1": a_correct_setting("m.py@b1", "two", "# a\n")
                },
                "function-context": {
                    "m.py@b1": a_correct_setting("m.py@b1", "two", "# b\n")
                },
            },
            monkeypatch,
            capsys,
        )
        assert "m.py@b1" in out
        assert "block-context" in out
        assert "function-context" in out

    def test_a_resolved_run_says_so_and_names_nothing(
        self, tmp_path, monkeypatch, capsys
    ):
        _code, out = run(
            tmp_path,
            {"block-context": {"m.py@b1": a_clean("m.py@b1")}},
            monkeypatch,
            capsys,
        )
        assert "escalation" not in out.lower() or "0 escalation" in out.lower()


class TestTheGateSeesIt:
    def test_collate_is_in_COMMANDS(self):
        from comment_review.__main__ import COMMANDS

        assert "collate" in COMMANDS
