"""The `check` command: what the fold would refuse, named before the send.

! IT RUNS `main()` IN-PROCESS with a built argv. Inputs are real -- a binder
from `a_binder_over`, copies from the real `seed`, batches from the real
`batch_of` over the real `collate`.
"""

import json

from helpers import (
    REPO,
    a_binder_over,
    a_clean,
    a_correct,
    a_correct_setting,
    copies_over,
)

from comment_review.commands import check as command
from comment_review.desk.diff_mark import batch_of
from comment_review.flows.collate import collate

BASE = "# one\n# two\n# three\n"


def _run(monkeypatch, capsys, *argv):
    monkeypatch.setattr("sys.argv", ["check", *argv])
    code = command.main()
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def _copy_file(tmp_path, marks, role="block-context"):
    binder = a_binder_over({"m.py@b1": BASE, "m.py@b5": BASE})
    copy = copies_over(binder, {role: marks})[0]
    path = tmp_path / "copy.json"
    path.write_text(json.dumps(copy), encoding="utf-8")
    binder_path = tmp_path / "binder.json"
    binder_path.write_text(json.dumps(binder.serialize()), encoding="utf-8")
    return str(path), str(binder_path)


class TestACopy:
    def test_a_copy_answering_every_place_exits_zero(
        self, tmp_path, monkeypatch, capsys
    ):
        path, _ = _copy_file(
            tmp_path, {"m.py@b1": a_correct("m.py@b1"), "m.py@b5": a_clean("m.py@b5")}
        )
        code, out, _ = _run(monkeypatch, capsys, "--edit-copy", path)
        assert code == 0
        assert "0 thing(s)" in out

    def test_a_place_left_alone_is_named(self, tmp_path, monkeypatch, capsys):
        path, _ = _copy_file(tmp_path, {"m.py@b1": a_correct("m.py@b1")})
        code, out, _ = _run(monkeypatch, capsys, "--edit-copy", path)
        assert code == 1
        assert "m.py@b5" in out and "not ruled on" in out

    def test_a_malformed_mark_is_named_with_every_reason(
        self, tmp_path, monkeypatch, capsys
    ):
        broken = a_correct("m.py@b1")
        del broken["sources"]
        del broken["reason"]
        path, _ = _copy_file(
            tmp_path, {"m.py@b1": broken, "m.py@b5": a_clean("m.py@b5")}
        )
        code, out, _ = _run(monkeypatch, capsys, "--edit-copy", path)
        assert code == 1
        assert "m.py@b1" in out
        assert "reason" in out and "source" in out

    def test_with_a_binder_a_bad_citation_is_named(self, tmp_path, monkeypatch, capsys):
        mark = a_correct("m.py@b1")
        mark["sources"] = [{"cite": "nowhere/at/all.py:1", "verbatim": "x"}]
        path, binder = _copy_file(
            tmp_path, {"m.py@b1": mark, "m.py@b5": a_clean("m.py@b5")}
        )
        code, out, _ = _run(
            monkeypatch,
            capsys,
            "--edit-copy",
            path,
            "--binder",
            binder,
            "--repo",
            str(REPO),
        )
        assert code == 1
        assert "cite" in out

    def test_a_file_that_is_not_json_exits_two(self, tmp_path, monkeypatch, capsys):
        path = tmp_path / "copy.json"
        path.write_text("not json", encoding="utf-8")
        code, _, err = _run(monkeypatch, capsys, "--edit-copy", str(path))
        assert code == 2
        assert err


def _batch_file(tmp_path, answered_by_role: dict):
    """A real batch over a real escalation, with the given roles' slots
    written back as `answered_by_role` says -- a dict of field updates, or
    the string "role-keyed" to write the batch shape instead of a list."""
    binder = a_binder_over({"m.py@b1": BASE})
    copies = copies_over(
        binder,
        {
            "block-context": {
                "m.py@b1": a_correct_setting(
                    "m.py@b1", "two", "# one\n# TWO\n# three\n"
                )
            },
            "function-context": {
                "m.py@b1": a_correct_setting(
                    "m.py@b1", "two", "# one\n# dos\n# three\n"
                )
            },
        },
    )
    got = collate("4c", copies, binder, root=REPO)
    batch = batch_of(got.escalations, got.rereads)
    paths = {}
    for role, how in answered_by_role.items():
        slots = batch[role]
        if how == "role-keyed":
            body = {role: slots}
        else:
            body = [{**slots[0], **how}]
        path = tmp_path / f"answers_{role}.json"
        path.write_text(json.dumps(body), encoding="utf-8")
        paths[role] = str(path)
    return paths


class TestABatch:
    def test_an_answered_batch_exits_zero(self, tmp_path, monkeypatch, capsys):
        paths = _batch_file(
            tmp_path, {"block-context": {"instruction": "hold", "reason": "stands"}}
        )
        code, out, _ = _run(
            monkeypatch,
            capsys,
            "--answers",
            paths["block-context"],
            "--role",
            "block-context",
        )
        assert code == 0
        assert "1 answered, 0" in out

    def test_an_unanswered_slot_is_named(self, tmp_path, monkeypatch, capsys):
        paths = _batch_file(tmp_path, {"block-context": {}})
        code, out, _ = _run(
            monkeypatch,
            capsys,
            "--answers",
            paths["block-context"],
            "--role",
            "block-context",
        )
        assert code == 1
        assert "unanswered" in out

    def test_a_patch_meant_as_hold_is_named(self, tmp_path, monkeypatch, capsys):
        """MEASURED in the game's hand 4: a role answered `patch` to keep its
        own patch; a DiffMark patch owes a change."""
        paths = _batch_file(
            tmp_path, {"block-context": {"instruction": "patch", "reason": "keep mine"}}
        )
        code, out, _ = _run(
            monkeypatch,
            capsys,
            "--answers",
            paths["block-context"],
            "--role",
            "block-context",
        )
        assert code == 1
        assert "patch needs a `change`" in out

    def test_the_batch_shape_keyed_by_role_is_taken_as_that_roles_slots(
        self, tmp_path, monkeypatch, capsys
    ):
        paths = _batch_file(tmp_path, {"block-context": "role-keyed"})
        code, out, _ = _run(
            monkeypatch,
            capsys,
            "--answers",
            paths["block-context"],
            "--role",
            "block-context",
        )
        # ! The slots are the seeded ones, unanswered -- so BROKEN, but for the
        # right reason: the shape was read, and the slot inside it was empty.
        assert code == 1
        assert "unanswered" in out

    def test_the_wrong_role_finds_no_slots(self, tmp_path, monkeypatch, capsys):
        paths = _batch_file(tmp_path, {"block-context": "role-keyed"})
        code, out, _ = _run(
            monkeypatch,
            capsys,
            "--answers",
            paths["block-context"],
            "--role",
            "module-context",
        )
        assert code == 1
        assert "no slots for module-context" in out

    def test_answers_without_a_role_exits_two(self, tmp_path, monkeypatch, capsys):
        paths = _batch_file(
            tmp_path, {"block-context": {"instruction": "hold", "reason": "x"}}
        )
        code, _, err = _run(monkeypatch, capsys, "--answers", paths["block-context"])
        assert code == 2
        assert "--role" in err
