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
    a_query,
    a_real_binder_over,
    an_add,
    copies_over,
    entries_of,
)

from comment_review.commands import collate as command
from comment_review.desk.answers.answer import Question
from comment_review.desk.evaluate.place import Place
from comment_review.desk.evaluate.state import State
from comment_review.desk.marks.mark import Shape
from comment_review.flows.proof_io import load_proof

BASE = "# one\n# two\n# three\n"


def run(
    tmp_path, marks_by_role, monkeypatch, capsys, *extra, on_copy=None, places=None
):
    """`collate` over one page's copies. `on_copy` is laid over each copy as
    it is written, which is how a role hand-edits one before returning it.
    `places` is the page's paragraphs by address, one at `m.py@b1` unless a
    case names more."""
    binder = a_real_binder_over(tmp_path / "repo", places or {"m.py@b1": BASE})
    copies = copies_over(binder, marks_by_role)
    binder_path = tmp_path / "binder.json"
    binder_path.write_text(json.dumps(binder.serialize()), encoding="utf-8")
    paths = []
    for i, copy in enumerate(copies):
        path = tmp_path / f"copy{i}.json"
        path.write_text(json.dumps({**copy, **(on_copy or {})}), encoding="utf-8")
        paths.append(str(path))
    argv = [
        "collate",
        "--stage",
        "4c",
        "--binder",
        str(binder_path),
        "--out",
        str(tmp_path / "chief.json"),
        *extra,
    ]
    for path in paths:
        argv += ["--edit-copy", path]
    monkeypatch.setattr("sys.argv", argv)
    code = command.main()
    return code, capsys.readouterr().out


TWO_ROLES = (
    '[[stage]]\nname = "4c"\nkind = "editorial"\n'
    '  [[stage.dispatch]]\n  role = "block-context"\n'
    '  [[stage.dispatch]]\n  role = "function-context"\n'
)


class TestTheDroppedList:
    """`decision-log.md Process: #163` and `#177`: the list reaches the chief
    under its own heading in the report, carries no exit code of its own, and
    settles the place it is about.

    ! IT IS THE `correct` ROW'S `notes` RULE NOW, reported as an `Advised`
    event rather than as a fourth list beside the fold's own. The heading and the
    sentence a reader sees are the ones `#163` landed."""

    def test_a_run_whose_only_finding_is_the_list_exits_as_it_did(
        self, tmp_path, monkeypatch, capsys
    ):
        code, out = run(
            tmp_path,
            {
                "block-context": {
                    "m.py@b1": a_correct_setting("m.py@b1", "two", "# one\n# TWO\n")
                }
            },
            monkeypatch,
            capsys,
        )
        assert code == 0, out
        assert command.FOR_THE_CHIEF in out
        assert (
            "block-context m.py@b1: its change drops 'three', which its claim never"
            " names" in out
        )

    def test_the_place_still_settles_and_the_chief_copy_is_written(
        self, tmp_path, monkeypatch, capsys
    ):
        """A note is not a refusal: the round commits over it."""
        code, out = run(
            tmp_path,
            {
                "block-context": {
                    "m.py@b1": a_correct_setting("m.py@b1", "two", "# one\n# TWO\n")
                }
            },
            monkeypatch,
            capsys,
        )
        assert code == command.OK, out
        assert "stet m.py@b1" in out
        chief = json.loads((tmp_path / "chief.json").read_text(encoding="utf-8"))
        assert [m["address"] for s in chief["sheets"] for m in s["marks"]] == [
            "m.py@b1"
        ]

    def test_the_heading_is_absent_where_nothing_is_advised(
        self, tmp_path, monkeypatch, capsys
    ):
        _code, out = run(
            tmp_path,
            {"block-context": {"m.py@b1": a_clean("m.py@b1")}},
            monkeypatch,
            capsys,
        )
        assert command.FOR_THE_CHIEF not in out


class TestStageCoverage:
    """P26: a dispatch the topology named that returned no copy is reported.

    The fold is a Unit of Work, so the report routes back to the role and the
    round rolls back: a stage that is short a dispatch has not been folded.
    """

    def test_a_dispatch_that_returned_nothing_is_named_with_its_count(
        self, tmp_path, monkeypatch, capsys
    ):
        (tmp_path / "t.toml").write_text(TWO_ROLES, encoding="utf-8")
        code, out = run(
            tmp_path,
            {"block-context": {"m.py@b1": a_correct("m.py@b1")}},
            monkeypatch,
            capsys,
            "--topology",
            str(tmp_path / "t.toml"),
        )
        assert code == command.BROKEN, out
        assert "stage 4c: function-context returned 0 of 1 dispatches" in out
        assert not (tmp_path / "chief.json").exists()

    def test_every_dispatch_returned_is_no_report(self, tmp_path, monkeypatch, capsys):
        (tmp_path / "t.toml").write_text(TWO_ROLES, encoding="utf-8")
        code, out = run(
            tmp_path,
            # ! The two agree, so the fold settles and nothing else is reported.
            {
                "block-context": {"m.py@b1": a_correct("m.py@b1")},
                "function-context": {"m.py@b1": a_correct("m.py@b1")},
            },
            monkeypatch,
            capsys,
            "--topology",
            str(tmp_path / "t.toml"),
        )
        assert code == 0, out
        assert "dispatches" not in out

    def test_a_stage_the_topology_lacks_is_refused_by_name(
        self, tmp_path, monkeypatch, capsys
    ):
        (tmp_path / "t.toml").write_text(
            TWO_ROLES.replace('"4c"', '"4a"'), encoding="utf-8"
        )
        code, out = run(
            tmp_path,
            {"block-context": {"m.py@b1": a_correct("m.py@b1")}},
            monkeypatch,
            capsys,
            "--topology",
            str(tmp_path / "t.toml"),
        )
        assert code == command.UNREADABLE


#: A compacting stage's row over the same page: dealt the `b` places over two
#: lines, admitting the edit instructions -- `decision-log.md Process: #193`.
COMPACTING = (
    '[[stage]]\nname = "4c"\nkind = "editorial"\n'
    'cap = 2\nseries = ["b"]\nadmits = ["patch", "drop", "add", "clean"]\n'
    '  [[stage.dispatch]]\n  role = "block-context"\n'
)


class TestWhatTheStageAdmits:
    """The row is what a mark is held to, and the copy is not where that is
    decided (`decision-log.md Process: #193`).

    `mark` and `check` read the copy's own `admits`, which is the field a role
    can edit; this is the door the fold opens behind, where the copies are
    already in hand together with the row they were dealt under.
    """

    def test_a_copy_that_widened_its_own_admits_is_BROKEN_by_name(
        self, tmp_path, monkeypatch, capsys
    ):
        (tmp_path / "t.toml").write_text(COMPACTING, encoding="utf-8")
        code, out = run(
            tmp_path,
            {"block-context": {"m.py@b1": a_correct("m.py@b1")}},
            monkeypatch,
            capsys,
            "--topology",
            str(tmp_path / "t.toml"),
            on_copy={"stage": "4c", "admits": ["patch", "correct"]},
        )
        assert code == command.BROKEN, out
        assert "stage 4c admits patch, drop, add, clean, and not correct" in out
        assert "block-context (the copy):" in out
        assert not (tmp_path / "chief.json").exists()

    def test_the_same_copy_under_no_topology_is_held_to_its_own_admits(
        self, tmp_path, monkeypatch, capsys
    ):
        """Without a row there is nothing else to hold a mark to, and the
        copy's own field is what `check` would have used -- so `collate` is
        never weaker than `check`."""
        code, out = run(
            tmp_path,
            {"block-context": {"m.py@b1": a_correct("m.py@b1")}},
            monkeypatch,
            capsys,
            on_copy={"stage": "6", "admits": ["patch", "drop", "add", "clean"]},
        )
        assert code == command.BROKEN, out
        assert "stage 6 admits patch, drop, add, clean, and not correct" in out


class TestExitCodes:
    def test_everything_resolved_exits_zero(self, tmp_path, monkeypatch, capsys):
        code, _out = run(
            tmp_path,
            {"block-context": {"m.py@b1": a_correct("m.py@b1")}},
            monkeypatch,
            capsys,
        )
        assert code == 0

    def test_a_composition_exits_three(self, tmp_path, monkeypatch, capsys):
        code, out = run(
            tmp_path,
            {
                "block-context": {
                    "m.py@b1": a_correct_setting(
                        "m.py@b1", "one", "# 1\n# two\n# three"
                    )
                },
                "function-context": {
                    "m.py@b1": a_correct_setting(
                        "m.py@b1", "three", "# one\n# two\n# 3"
                    )
                },
            },
            monkeypatch,
            capsys,
        )
        assert code == 3, out
        assert "composed m.py@b1" in out

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

    def test_escalation_beats_composition_when_both_are_present(
        self, tmp_path, monkeypatch, capsys
    ):
        """Proves the ORDER `main` checks, not just its result: the escalation
        branch of `_code_for` sits before the composition branch, so a run
        holding both reports 4, never 3.

        !! DRIVEN THROUGH THE REAL FOLD, not a hand-built event list -- a
        stage CAN produce both at once, on two different addresses of one
        page: at `m.py@b1` two `correct` marks replace the same clause with
        different text, which composes into nothing and contests; at
        `m.py@b2` two `correct` marks touch clauses the other left alone,
        which composes.
        """
        binder = a_real_binder_over(
            tmp_path / "repo", {"m.py@b1": BASE, "m.py@b2": "# four\n# five\n# six"}
        )
        copies = copies_over(
            binder,
            {
                "block-context": {
                    "m.py@b1": a_correct_setting("m.py@b1", "two", "# a\n"),
                    "m.py@b2": a_correct_setting(
                        "m.py@b2", "four", "# 4\n# five\n# six"
                    ),
                },
                "function-context": {
                    "m.py@b1": a_correct_setting("m.py@b1", "two", "# b\n"),
                    "m.py@b2": a_correct_setting(
                        "m.py@b2", "six", "# four\n# five\n# 6"
                    ),
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
        assert "contested m.py@b1" in out
        assert "composed m.py@b2" in out
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
        that before the proof was assembled and folded, so a role-less copy reached
        `places()` and the raise aborted `collate` before it could return a
        a report at all. Then `P21` made the envelope parse report it as a
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
        """`decision-log.md Process: #178`: two copies gathered from different
        trees share no address space, so the handler refuses the round.

        ! THE OLD FOLD RAISED `desk.proof.MismatchedRoot` from `master_proof_of`
        and the command caught it onto stderr. The handler reaches no
        `master_proof_of`, so the comparison is `flows.bus._root_problems` and
        the reason routes to the role that owes it, on stdout, like every
        other finding."""
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
        out = capsys.readouterr().out
        assert code == command.BROKEN
        assert "somewhere/else" in out
        assert "function-context (the copy):" in out
        assert not (tmp_path / "chief.json").exists()

    def test_every_copys_findings_are_printed_not_just_the_first(
        self, tmp_path, monkeypatch, capsys
    ):
        """Finding #6 of the 2026-08-30 review, by RUNNING the real CLI.

        !! MEASURED BEFORE THE FIX: exit 1, **stdout EMPTY**, and only the
        REFUSED line on stderr. `collate` accumulated its `Problem`s into a
        local list and only reached its return past `master_proof_of`, so a
        refusal there made every one of them unrecoverable -- **one role's
        incompatible header blocking routing for every other role**, which is
        the opposite of Roy's rule that the errors stack so each can be fixed or
        sent back to the role that owes it.

        ! THE INCOMPATIBLE HEADER IS NO LONGER WHAT REFUSES. The Unit of Work
        reaches no `master_proof_of`, so this drives the rule on two broken
        marks instead: each role must read its own line.
        """
        binder = a_binder_over({"m.py@b1": BASE})
        copies = copies_over(
            binder,
            {
                "block-context": {"m.py@b1": a_correct("m.py@b1")},
                "function-context": {"m.py@b1": a_correct("m.py@b1", 2)},
            },
        )
        for copy in copies:
            copy["sheets"][0]["marks"][0]["claim"] = {}
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
        assert "block-context m.py@b1:" in out.out
        assert "function-context m.py@b1:" in out.out
        assert not (tmp_path / "chief.json").exists()

    def test_a_copy_missing_read_from_exits_one_not_a_traceback(
        self, tmp_path, monkeypatch, capsys
    ):
        """`desk.proof.master_proof_of`'s bare `copy["read_from"]` raises `KeyError` by
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
        # names an absent `read_from` before `master_proof_of` is reached, so the
        # `RECONCILE_ERRORS` catch is no longer what answers this input.
        assert "read_from" in out.out
        assert not (tmp_path / "chief.json").exists()

    def test_a_short_shard_is_named_and_refuses_the_round(
        self, tmp_path, monkeypatch, capsys
    ):
        """A role whose copy does not carry every address it was handed is
        named by the addresses it is missing, and the round rolls back.

        !! IT EXITED 6 AND WROTE THE CHIEF UNTIL THE FOLD BECAME A UNIT OF
        WORK, on `Process: #63` -- a missing answer ROUTES and does not VOID
        the round. The routing is unchanged: the line still names the role and
        every address it owes. What changed is that a fold commits every place
        or none, so the places that did come back are not settled over a
        question nobody answered.
        """
        root = tmp_path / "repo"
        binder = a_real_binder_over(root, {"m.py@b1": BASE, "m.py@b5": BASE})
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
                str(root),
            ],
        )
        code = command.main()
        out = capsys.readouterr().out
        assert code == command.BROKEN
        assert "missing m.py@b5" in out
        assert not out_path.exists()

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

    def test_a_place_HANDED_TO_A_ROLE_AND_NOT_RULED_ON_is_named_and_refuses(
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

        ! THE OLD FOLD'S `unruled` HELD THE ANSWER THE WHOLE TIME: it computed
        `{'module-context': ['m.py@b5', 'm.py@b7']}` and this command threw it
        away. That is why the fix is a report and a code, not a new check.

        ! IT TOOK `COVERAGE` UNTIL THE FOLD BECAME A UNIT OF WORK, and takes
        `BROKEN` now: a place nobody ruled on is a question the fold cannot
        answer, so it refuses the round rather than settling the rest around
        it. The line a task agent reads is word for word the one it was.
        """
        root = tmp_path / "repo"
        binder = a_real_binder_over(root, {"m.py@b1": BASE, "m.py@b5": BASE})
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
                str(root),
            ],
        )
        code = command.main()
        out = capsys.readouterr().out
        assert code == command.BROKEN
        assert code != command.OK, "a silently short round used to exit 0"
        # ! THE ADDRESS AND THE ROLE, so the task agent can send it back.
        assert "block-context m.py@b5: handed to this role and not ruled on" in out
        # ! AND THE PLACE THAT *WAS* RULED ON IS NOT NAMED -- a report that
        # listed every address would be a list nobody reads.
        assert "m.py@b1: handed to this role" not in out
        assert not out_path.exists()

    def test_an_unruled_place_refuses_a_round_that_would_have_escalated(
        self, tmp_path, monkeypatch, capsys
    ):
        """`decision-log.md Process: #112`, `collate-command-defects` T21.

        Two roles correct `m.py@b1` to different texts, which would contest,
        and function-context leaves `m.py@b5` as it was handed, an unruled
        place. A place nobody ruled on is found before the fold opens, so the
        round rolls back and the contest is never reached: there is no round
        to carry it forward into.

        !! IT EXITED `CARRIED_AND_UNRULED` (7) UNTIL THE FOLD BECAME A UNIT OF
        WORK, which is what `Process: #112` asked for while a round could
        settle around a place a role still owed. It cannot now.
        """
        root = tmp_path / "repo"
        binder = a_real_binder_over(root, {"m.py@b1": BASE, "m.py@b5": BASE})
        copies = copies_over(
            binder,
            {
                "block-context": {
                    "m.py@b1": a_correct_setting("m.py@b1", "two", "# a\n"),
                    "m.py@b5": a_clean("m.py@b5"),
                },
                "function-context": {
                    "m.py@b1": a_correct_setting("m.py@b1", "two", "# b\n"),
                },
            },
        )
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
        out = capsys.readouterr().out
        assert "function-context m.py@b5: handed to this role and not ruled on" in out
        assert code != command.ESCALATIONS, out
        assert code == command.BROKEN
        assert "contested m.py@b1" not in out
        assert not (tmp_path / "chief.json").exists()

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

    def test_a_rolled_back_round_names_its_refusal_and_settles_nothing(
        self, tmp_path, monkeypatch, capsys
    ):
        """A rollback commits nothing, so no place is reported as standing.

        `m.py@b1` would settle on its own; the add at `m.py@b2` drops a word
        of the paragraph already there, which its row refuses at the fold.
        """
        dropping = {**an_add("m.py@b2"), "raw_text": "# one\n# three\n"}
        code, out = run(
            tmp_path,
            {"block-context": {"m.py@b1": a_clean("m.py@b1"), "m.py@b2": dropping}},
            monkeypatch,
            capsys,
            places={"m.py@b1": BASE, "m.py@b2": BASE},
        )
        assert code == command.BROKEN, out
        assert "block-context m.py@b2: the text does not keep 'two'" in out
        assert "stet" not in out

    def test_a_rolled_back_round_prints_its_refusals_and_nothing_else(
        self, tmp_path, monkeypatch, capsys
    ):
        """A rollback writes no chief's copy, no proof and no batch, so a
        settled, a contested and an unsettlable place are not reported: each
        line would say something happens that does not.

        The same copies with the refused place ruled `clean` instead commit
        and print all three, which is what shows the rollback withheld them.
        """
        places = {address: BASE for address in ("m.py@b1", "m.py@b2", "m.py@b3")}
        places["m.py@b4"] = BASE

        def marks(at_b4: dict) -> dict:
            return {
                "block-context": {
                    "m.py@b1": a_clean("m.py@b1"),
                    "m.py@b2": a_correct_setting("m.py@b2", "two", "# a\n"),
                    "m.py@b3": a_query("m.py@b3", Shape.HUMAN_REVIEW_NECESSARY),
                    "m.py@b4": at_b4,
                },
                "function-context": {
                    "m.py@b1": a_clean("m.py@b1"),
                    "m.py@b2": a_correct_setting("m.py@b2", "two", "# b\n"),
                    "m.py@b3": a_clean("m.py@b3"),
                    "m.py@b4": a_clean("m.py@b4"),
                },
            }

        committed = tmp_path / "committed"
        committed.mkdir()
        code, out = run(
            committed,
            marks(a_clean("m.py@b4")),
            monkeypatch,
            capsys,
            places=places,
        )
        assert code == command.ESCALATIONS, out
        assert "stet m.py@b1" in out
        assert "contested m.py@b2" in out
        assert "unsettlable m.py@b3" in out

        dropping = {**an_add("m.py@b4"), "raw_text": "# one\n# three\n"}
        code, out = run(tmp_path, marks(dropping), monkeypatch, capsys, places=places)
        assert code == command.BROKEN, out
        assert out.splitlines() == [
            "block-context m.py@b4: the text does not keep 'two'"
        ]
        assert not (tmp_path / "chief.json").exists()


class TestTheGateSeesIt:
    def test_collate_is_in_COMMANDS(self):
        from comment_review.__main__ import COMMANDS

        assert "collate" in COMMANDS


class TestTheStateBetweenTurnsOnDisk:
    """`P3` of `docs/plans/0.2.4-the-turn-as-commands.md`: `--proof-out` writes
    the master proof as `Process: #87`'s state between turns, `--batch-out` the
    first turn's batch -- and only when a place is carried forward."""

    ONE = {"block-context": {"m.py@b1": a_correct("m.py@b1")}}
    CONTESTED = {
        "block-context": {"m.py@b1": a_correct_setting("m.py@b1", "two", "# a\n")},
        "function-context": {"m.py@b1": a_correct_setting("m.py@b1", "two", "# b\n")},
    }

    def test_proof_out_writes_a_proof_the_container_reads_back(
        self, tmp_path, monkeypatch, capsys
    ):
        proof_path = tmp_path / "proof.json"
        code, out = run(
            tmp_path, self.ONE, monkeypatch, capsys, "--proof-out", str(proof_path)
        )
        assert code == command.OK, out
        # ! THE SUMMARY COUNTS THE PLACES BY WHAT THEY CAME TO. A bare place
        # count says nothing a reader can act on, which is what it said for
        # one commit.
        assert "1 places -- 1 settled, 0 unsettlable, 0 carried forward" in out
        proof, why = load_proof(proof_path)
        assert why == []
        assert proof is not None
        assert [p["address"] for p in proof.places] == ["m.py@b1"]
        place, why = Place.deserialize("the place", proof.places[0])
        assert place is not None, why
        assert place.state is State.STANDS
        assert place.text == proof.places[0]["text"]

    def test_the_proof_carries_the_copies_as_they_stand(
        self, tmp_path, monkeypatch, capsys
    ):
        """So `turn` can mutate and re-fold them: the role's own mark is on the
        proof's copy, not a derived summary of it."""
        proof_path = tmp_path / "proof.json"
        run(
            tmp_path,
            self.CONTESTED,
            monkeypatch,
            capsys,
            "--proof-out",
            str(proof_path),
        )
        proof, why = load_proof(proof_path)
        assert proof is not None, why
        assert [c.role for c in proof.edit_copies] == list(self.CONTESTED)
        changes = {c.role: [m.change for m in entries_of(c)] for c in proof.edit_copies}
        assert changes == {"block-context": ["# a\n"], "function-context": ["# b\n"]}

    def test_batch_out_is_written_when_a_place_is_carried_forward(
        self, tmp_path, monkeypatch, capsys
    ):
        batch_path = tmp_path / "batch1.json"
        code, out = run(
            tmp_path,
            self.CONTESTED,
            monkeypatch,
            capsys,
            "--batch-out",
            str(batch_path),
        )
        assert code == command.ESCALATIONS, out
        batch = json.loads(batch_path.read_text(encoding="utf-8"))
        assert sorted(batch) == ["block-context", "function-context"]
        for slots in batch.values():
            (slot,) = slots
            assert slot["address"] == "m.py@b1"
            assert slot["question"] == str(Question.ESCALATION)
            # ! EVERY SIDE ON EVERY SLOT, so a role reads the text it is being
            # asked about beside its own.
            assert slot["sides"] == {
                "block-context": "# a\n",
                "function-context": "# b\n",
            }

    def test_batch_out_writes_nothing_when_nothing_is_carried_forward(
        self, tmp_path, monkeypatch, capsys
    ):
        batch_path = tmp_path / "batch1.json"
        code, out = run(
            tmp_path, self.ONE, monkeypatch, capsys, "--batch-out", str(batch_path)
        )
        assert code == command.OK, out
        assert not batch_path.exists()

    def test_an_unsettlable_place_is_reported_and_rides_on_the_proof(
        self, tmp_path, monkeypatch, capsys
    ):
        """`Process: #90`: the human's query rides with the set, and the place
        it holds settles for nobody else.

        ! IT RODE IN `MasterProof.unsettlable` UNTIL THE FOLD BECAME A UNIT OF
        WORK, as `{address, roles, query}`. The place itself carries the state
        now, so there is one list rather than a list and a summary of it, and
        the run says on the console who asked and why.
        """
        proof_path = tmp_path / "proof.json"
        asked = {
            "block-context": {
                "m.py@b1": a_query("m.py@b1", Shape.HUMAN_REVIEW_NECESSARY)
            }
        }
        _code, out = run(
            tmp_path, asked, monkeypatch, capsys, "--proof-out", str(proof_path)
        )
        assert "unsettlable m.py@b1: block-context asks the human -- " in out
        assert "1 places -- 0 settled, 1 unsettlable, 0 carried forward" in out
        proof, why = load_proof(proof_path)
        assert proof is not None, why
        (entry,) = proof.places
        place, why = Place.deserialize("the place", entry)
        assert place is not None, why
        assert place.address == "m.py@b1"
        assert place.state is State.UNSETTLABLE
        assert place.text is None
        assert [one.role for one in place.filed] == ["block-context"]
