"""The `check` command: what the fold would refuse, named before the send.

! IT RUNS `main()` IN-PROCESS with a built argv. Inputs are real -- a binder
from `a_binder_over`, copies from the real `seed`, batches from the real
`batch_of` over the real `collate`, and the proof each batch went out with
from `proof_after`.

! WHERE THE EXPECTATIONS COME FROM: the 2026-08-17 ruling that a role edits
the seeded template and a CLI validates it
(`TODO/completed/the-record-is-a-parsed-template-and-should-be-a-value.md` T2),
and the game of 2026-09-04 that measured what roles hand back -- an
unanswered slot, a `patch` meant as *keep my patch*, a batch keyed by role
(`decision-log.md Process: #86`-`#91`).
"""

import json

from helpers import (
    EMPTY_PLACE,
    REPO,
    a_binder_over,
    a_clean,
    a_correct,
    a_correct_setting,
    an_add_at_an_empty_place,
    copies_over,
)

from comment_review.commands import check as command
from comment_review.desk.diff_mark import batch_of
from comment_review.flows.collate import collate
from comment_review.flows.proof_io import save_batch, save_proof
from comment_review.flows.turn import batch_for, proof_after, run_turn

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
    (tmp_path / "batch.json").write_text(json.dumps(batch), encoding="utf-8")
    save_proof(tmp_path / "proof.json", proof_after(got, root=tmp_path))
    paths = {
        "sent": str(tmp_path / "batch.json"),
        "proof": str(tmp_path / "proof.json"),
    }
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
            "--sent",
            paths["sent"],
            "--role",
            "block-context",
            "--proof",
            paths["proof"],
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
            "--sent",
            paths["sent"],
            "--role",
            "block-context",
            "--proof",
            paths["proof"],
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
            "--sent",
            paths["sent"],
            "--role",
            "block-context",
            "--proof",
            paths["proof"],
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
            "--sent",
            paths["sent"],
            "--role",
            "block-context",
            "--proof",
            paths["proof"],
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
            "--sent",
            paths["sent"],
            "--role",
            "module-context",
            "--proof",
            paths["proof"],
        )
        assert code == 1
        assert "no slots were sent to module-context" in out

    def test_answers_without_a_role_exits_two(self, tmp_path, monkeypatch, capsys):
        paths = _batch_file(
            tmp_path, {"block-context": {"instruction": "hold", "reason": "x"}}
        )
        code, _, err = _run(monkeypatch, capsys, "--answers", paths["block-context"])
        assert code == 2
        assert "--role" in err and "--sent" in err


def _gapped_files(tmp_path, answered: dict):
    """A real fold over an `add` at an empty place, written as `collate`
    writes it -- `proof0.json` and `batch1.json` -- plus one answers file per
    role in `answered`: that role's sent slots with its fields laid over."""
    binder, got = an_add_at_an_empty_place(tmp_path)
    batch = batch_for(got)
    save_proof(tmp_path / "proof0.json", proof_after(got, root=tmp_path))
    save_batch(tmp_path / "batch1.json", batch)
    answers = {
        role: [{**slot, **fields} for slot in batch[role]]
        for role, fields in answered.items()
    }
    paths = {}
    for role, slots in answers.items():
        path = tmp_path / f"answers_{role}.json"
        path.write_text(json.dumps(slots), encoding="utf-8")
        paths[role] = str(path)
    return binder, got, batch, answers, paths


def _check(monkeypatch, capsys, tmp_path, paths, role):
    return _run(
        monkeypatch,
        capsys,
        "--answers",
        paths[role],
        "--sent",
        str(tmp_path / "batch1.json"),
        "--role",
        role,
        "--proof",
        str(tmp_path / "proof0.json"),
    )


class TestABatchIsAppliedAsTheTurnAppliesIt:
    """`check --answers` runs what `run_turn` runs for one role's answers, over
    the copies on the proof the batch went out with --
    `no-command-for-the-middle` T31."""

    def test_answers_the_turn_takes_exit_zero(self, tmp_path, monkeypatch, capsys):
        clean = {"instruction": "clean"}
        *_, paths = _gapped_files(
            tmp_path, {"block-context": clean, "function-context": clean}
        )
        for role in ("block-context", "function-context"):
            code, out, _ = _check(monkeypatch, capsys, tmp_path, paths, role)
            assert code == 0, out
            assert "1 answered, 0 the fold would refuse" in out

    def test_what_the_turn_refuses_is_named(self, tmp_path, monkeypatch, capsys):
        """An answer at a place the role's copy holds no slot for is placed
        from the page, so with the page gone from the checkout the turn refuses
        it when it applies the answer -- and `check` names the same refusal."""
        clean = {"instruction": "clean"}
        binder, got, batch, answers, paths = _gapped_files(
            tmp_path, {"block-context": clean, "function-context": clean}
        )
        (tmp_path / "m.py").unlink()
        turned = run_turn(
            proof_after(got, root=tmp_path), binder, tmp_path, batch, answers
        )
        refused = [p for p in turned.revisit if p.role == "function-context"]
        assert [p.address for p in refused] == [EMPTY_PLACE]
        code, out, _ = _check(monkeypatch, capsys, tmp_path, paths, "function-context")
        assert code == 1
        for one in refused:
            for reason in one.reasons:
                assert f"{one.role} {one.where}: {reason}" in out


class TestTheContract:
    def test_the_contract_prints_as_json_and_exits_zero(self, monkeypatch, capsys):
        code, out, _ = _run(monkeypatch, capsys, "--contract")
        assert code == 0
        got = json.loads(out)
        assert set(got) == {"stage_4c_mark", "escalation", "composition"}
        assert "hold" in got["escalation"]["instruction"]
