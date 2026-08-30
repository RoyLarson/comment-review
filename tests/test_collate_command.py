"""The `collate` command's exit codes and its report.

! IT RUNS `main()` IN-PROCESS with a built argv, not a subprocess -- the same
way the rest of this suite asks a question it can ask directly.
"""

import json

from helpers import (
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
    binder_path.write_text(json.dumps(binder), encoding="utf-8")
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

    def test_a_broken_mark_exits_one(self, tmp_path, monkeypatch, capsys):
        binder = a_binder_over({"m.py@b1": BASE})
        copies = copies_over(
            binder, {"block-context": {"m.py@b1": a_correct("m.py@b1")}}
        )
        copies[0]["sheets"][0]["marks"][0]["claim"] = {}
        binder_path = tmp_path / "binder.json"
        binder_path.write_text(json.dumps(binder), encoding="utf-8")
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
