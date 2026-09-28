"""The `check` command: what the fold would refuse, named before the send.

! IT RUNS `main()` IN-PROCESS with a built argv. Inputs are real -- a binder
from `a_binder_over`, copies from the real `seed`, and batches from the fold
itself, as `flows.bus` sends them out.

! WHERE THE EXPECTATIONS COME FROM: the 2026-08-17 ruling that a role edits
the seeded template and a CLI validates it
(`TODO/completed/the-record-is-a-parsed-template-and-should-be-a-value.md` T2),
and the game of 2026-09-04 that measured what roles hand back -- an
unanswered slot, a `patch` meant as *keep my patch*, a batch keyed by role
(`decision-log.md Process: #86`-`#91`).
"""

import json

import pytest
from helpers import (
    MISSPELLINGS,
    REPO,
    TYPOS,
    a_binder_over,
    a_clean,
    a_correct,
    a_correct_setting,
    a_misspelled_address,
    a_move,
    a_query,
    a_real_binder_over,
    copies_over,
    patched,
    returned,
)

from comment_review.commands import check as command
from comment_review.desk.marks.mark import Shape
from comment_review.desk.work.events import Refused
from comment_review.flows.bus import AnswersReturned, CopiesReturned, handle

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

    def test_with_a_binder_a_destination_no_page_carries_is_named(
        self, tmp_path, monkeypatch, capsys
    ):
        """`no-command-for-the-middle` T99. `collate` resolves every mark's
        address and every move's destination against the real page, and
        `check` did not, so the 2026-09-14 self-run's copies passed `check` and
        were refused at the fold. A `path@cue` destination the page does not
        carry passes the mark's own parse; `check` now names it as the fold
        does."""
        root = tmp_path / "repo"
        binder = a_real_binder_over(root, {"m.py@b1": "# a paragraph\n"})
        move = a_move("m.py@b1", "m.py@b99")
        copy = copies_over(binder, {"block-context": {"m.py@b1": move}})[0]
        path = tmp_path / "copy.json"
        path.write_text(json.dumps(copy), encoding="utf-8")
        binder_path = tmp_path / "binder.json"
        binder_path.write_text(json.dumps(binder.serialize()), encoding="utf-8")
        code, out, _ = _run(
            monkeypatch,
            capsys,
            "--edit-copy",
            str(path),
            "--binder",
            str(binder_path),
            "--repo",
            str(root),
        )
        assert code == 1
        assert "m.py@b1" in out and "carries no place 'b99'" in out, out

    def test_with_a_binder_a_move_into_an_ungathered_file_is_held_to_its_page(
        self, tmp_path, monkeypatch, capsys
    ):
        """`decision-log.md Process: #187`. The destination's paragraph is read
        off the page, not off the binder, which holds no row for a file the run
        did not gather -- so a destination text that drops a word of what is
        already there is named here, as the fold names it."""
        root = tmp_path / "repo"
        binder = a_real_binder_over(root, {"m.py@b1": BASE})
        (root / "n.py").write_text(
            "v0 = 0\n# seven\n# eight\nv1 = 1\n", encoding="utf-8", newline="\n"
        )
        move = a_move("m.py@b1", "n.py@b1", change="# two\n", reads="# seven\n# two\n")
        copy = copies_over(binder, {"block-context": {"m.py@b1": move}})[0]
        path = tmp_path / "copy.json"
        path.write_text(json.dumps(copy), encoding="utf-8")
        binder_path = tmp_path / "binder.json"
        binder_path.write_text(json.dumps(binder.serialize()), encoding="utf-8")
        code, out, _ = _run(
            monkeypatch, capsys, "--edit-copy", str(path), "--binder", str(binder_path)
        )
        assert code == 1
        assert "block-context m.py@b1: the destination text does not keep 'eight'" in (
            out
        ), out

    def test_a_file_that_is_not_json_exits_two(self, tmp_path, monkeypatch, capsys):
        path = tmp_path / "copy.json"
        path.write_text("not json", encoding="utf-8")
        code, _, err = _run(monkeypatch, capsys, "--edit-copy", str(path))
        assert code == 2
        assert err


class TestAHumanQuestionInACopy:
    """`decision-log.md Process: #197`: a human question is named here as the
    fold names it, and `--human` says whether the answers file answers it."""

    def _asking(self, tmp_path):
        path, _ = _copy_file(
            tmp_path,
            {
                "m.py@b1": a_query("m.py@b1", Shape.HUMAN_REVIEW_NECESSARY),
                "m.py@b5": a_clean("m.py@b5"),
            },
        )
        return path

    def test_an_unanswered_query_alone_is_the_roles_part_done(
        self, tmp_path, monkeypatch, capsys
    ):
        """The reader is the role that filed it, which cannot ask the human --
        so the line tells it to hand the copy back, and the exit is not
        `BROKEN`, which would invite it to turn the question into a clean."""
        code, out, _ = _run(monkeypatch, capsys, "--edit-copy", self._asking(tmp_path))
        assert code == command.ASKS_THE_HUMAN, out
        assert (
            "asks the human m.py@b1: block-context -- "
            + a_query("m.py@b1", Shape.HUMAN_REVIEW_NECESSARY)["reason"]
            + "; this is the role's part done -- hand the copy back, and the task"
            " agent asks it"
        ) in out, out
        assert "record the answer in the answers file" not in out
        assert "0 thing(s) the fold would send back, 1 question(s) for the human" in (
            out
        ), out

    def test_an_unanswered_query_beside_another_finding_is_broken(
        self, tmp_path, monkeypatch, capsys
    ):
        path, _ = _copy_file(
            tmp_path,
            {"m.py@b1": a_query("m.py@b1", Shape.HUMAN_REVIEW_NECESSARY)},
        )
        code, out, _ = _run(monkeypatch, capsys, "--edit-copy", path)
        assert code == command.BROKEN, out
        assert "m.py@b5" in out and "not ruled on" in out
        assert "this is the role's part done" in out
        assert "1 thing(s) the fold would send back, 1 question(s) for the human" in (
            out
        ), out

    def test_an_answered_query_is_named_with_its_answer(
        self, tmp_path, monkeypatch, capsys
    ):
        path = self._asking(tmp_path)
        human = tmp_path / "human.toml"
        human.write_text(
            "[[answer]]\n"
            'role = "block-context"\n'
            'at = "m.py@b1"\n'
            'question = "q"\n'
            'answer = "Keep it."\n',
            encoding="utf-8",
        )
        code, out, _ = _run(
            monkeypatch, capsys, "--edit-copy", path, "--human", str(human)
        )
        assert code == command.ASKS_THE_HUMAN, out
        assert (
            "answered by the human m.py@b1: block-context -- Keep it.; block-context"
            " replaces this query with its mark or answer"
        ) in out
        assert "asks the human" not in out


@pytest.mark.parametrize("kind", MISSPELLINGS)
def test_an_address_spelled_otherwise_than_printed_is_named(
    tmp_path, monkeypatch, capsys, kind
):
    """`check` names each misspelling the fold refuses, so none passes here
    at exit 0 and is refused a round later."""
    places, marks, appended, named = a_misspelled_address(kind)
    root = tmp_path / "repo"
    binder = a_real_binder_over(root, places)
    copy = copies_over(binder, {"block-context": marks})[0]
    copy["sheets"][0]["marks"].extend(appended)
    path = tmp_path / "copy.json"
    path.write_text(json.dumps(copy), encoding="utf-8")
    binder_path = tmp_path / "binder.json"
    binder_path.write_text(json.dumps(binder.serialize()), encoding="utf-8")
    code, out, _ = _run(
        monkeypatch, capsys, "--edit-copy", str(path), "--binder", str(binder_path)
    )
    assert code == 1, out
    assert named in out, out


def _folded(tmp_path):
    """One real escalation through the bus: the proof and the batch it sends."""
    root = tmp_path / "repo"
    binder = a_real_binder_over(root, {"m.py@b1": BASE})
    copies = [
        returned(wire)
        for wire in copies_over(
            binder,
            {
                "block-context": {
                    "m.py@b1": a_correct_setting(
                        "m.py@b1", "two", "# one\n# TWO\n# three"
                    )
                },
                "function-context": {
                    "m.py@b1": a_correct_setting(
                        "m.py@b1", "two", "# one\n# dos\n# three"
                    )
                },
            },
        )
    ]
    out, result = handle(CopiesReturned("4c", copies, binder, root, None))
    assert result is not None and result.batch, out
    return result


def _batch_file(tmp_path, answered_by_role: dict):
    """A real batch over a real escalation, with the given roles' slots
    written back as `answered_by_role` says -- a dict of field updates, or
    the string "role-keyed" to write the batch shape instead of a list."""
    result = _folded(tmp_path)
    batch = result.batch
    (tmp_path / "batch.json").write_text(json.dumps(batch), encoding="utf-8")
    paths = {"sent": str(tmp_path / "batch.json")}
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
        )
        assert code == 1
        assert "unanswered" in out

    def test_a_patch_meant_as_hold_is_named(self, tmp_path, monkeypatch, capsys):
        """MEASURED in the game's hand 4: a role answered `patch` to keep its
        own patch; an escalation patch owes a change."""
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


def _answers_file(tmp_path, role, entries):
    path = tmp_path / f"answers_{role}.json"
    path.write_text(json.dumps(entries), encoding="utf-8")
    return str(path)


def _check(monkeypatch, capsys, tmp_path, path, role):
    return _run(
        monkeypatch,
        capsys,
        "--answers",
        path,
        "--sent",
        str(tmp_path / "batch.json"),
        "--role",
        role,
        "--repo",
        str(tmp_path / "repo"),
    )


class TestABatchIsHeldToWhatTheTurnRefuses:
    """`check --answers` refuses one role's file for what the turn would refuse
    it for: both read it through `flows.answers.answers_of`, against the slots
    that went out -- `no-command-for-the-middle` T31."""

    def test_answers_the_turn_takes_exit_zero(self, tmp_path, monkeypatch, capsys):
        result = _folded(tmp_path)
        (tmp_path / "batch.json").write_text(json.dumps(result.batch), encoding="utf-8")
        answers = {
            role: [{"address": "m.py@b1", "instruction": "hold", "reason": "mine"}]
            for role in result.batch
        }
        for role, entries in answers.items():
            path = _answers_file(tmp_path, role, entries)
            code, out, _ = _check(monkeypatch, capsys, tmp_path, path, role)
            assert code == 0, out
            assert "1 answered, 0 the fold would refuse" in out
        out, turned = handle(AnswersReturned(result.proof, answers, tmp_path / "repo"))
        assert turned is not None, out

    def test_what_the_turn_refuses_is_named_here_too(
        self, tmp_path, monkeypatch, capsys
    ):
        """One role answers at a place the batch never sent it -- which the
        turn refuses the whole round for, and which `check` names before the
        send."""
        result = _folded(tmp_path)
        (tmp_path / "batch.json").write_text(json.dumps(result.batch), encoding="utf-8")
        answers = {
            "block-context": [
                {"address": "m.py@b1", "instruction": "hold", "reason": "mine"},
                {"address": "m.py@b9", "instruction": "hold", "reason": "and this"},
            ],
            "function-context": [
                {"address": "m.py@b1", "instruction": "hold", "reason": "mine"}
            ],
        }
        path = _answers_file(tmp_path, "block-context", answers["block-context"])
        code, out, _ = _check(monkeypatch, capsys, tmp_path, path, "block-context")
        assert code == 1
        assert "block-context m.py@b9" in out
        events, turned = handle(
            AnswersReturned(result.proof, answers, tmp_path / "repo")
        )
        assert turned is None
        assert any(
            one.role == "block-context" and one.address == "m.py@b9"
            for one in events
            if isinstance(one, Refused)
        )

    def test_the_root_comes_off_the_slots_where_no_repo_is_given(
        self, tmp_path, monkeypatch, capsys
    ):
        """A slot carries the tree the copies were read from, as an edit_copy
        and a proof do, so a role checking its answers names no tree of its
        own. The cite below resolves there and nowhere near this suite's own
        directory, which is what `--repo` would otherwise have to say."""
        result = _folded(tmp_path)
        (tmp_path / "batch.json").write_text(json.dumps(result.batch), encoding="utf-8")
        path = _answers_file(
            tmp_path,
            "block-context",
            [
                {
                    "address": "m.py@b1",
                    "instruction": "correct",
                    "reason": "the line I read says so",
                    "change": "# one\n# corrected\n# three",
                    "sources": [{"cite": "m.py:2", "verbatim": "# one"}],
                }
            ],
        )
        code, out, _ = _run(
            monkeypatch,
            capsys,
            "--answers",
            path,
            "--sent",
            str(tmp_path / "batch.json"),
            "--role",
            "block-context",
        )
        assert code == 0, out

    def test_a_cite_that_does_not_resolve_is_named_here_and_refused_at_the_turn(
        self, tmp_path, monkeypatch, capsys
    ):
        """`decision-log.md Process: #181`: an answer's evidence is verified
        as a mark's is, and the check runs what the turn runs -- so the role
        reads the same refusal before it sends."""
        result = _folded(tmp_path)
        (tmp_path / "batch.json").write_text(json.dumps(result.batch), encoding="utf-8")
        cited = {
            "address": "m.py@b1",
            "instruction": "correct",
            "reason": "the line I read says so",
            "change": "# one\n# corrected\n# three",
            "sources": [{"cite": "nowhere.py:1", "verbatim": "x = 1"}],
        }
        answers = {
            "block-context": [cited],
            "function-context": [
                {"address": "m.py@b1", "instruction": "hold", "reason": "mine"}
            ],
        }
        path = _answers_file(tmp_path, "block-context", answers["block-context"])
        code, out, _ = _check(monkeypatch, capsys, tmp_path, path, "block-context")
        assert code == 1
        assert "block-context m.py@b1" in out and "does not resolve" in out
        _events, turned = handle(
            AnswersReturned(result.proof, answers, tmp_path / "repo")
        )
        assert turned is None


def _composed(tmp_path):
    """Two patches on different lines of one place: a composition, which
    admits a `query` answer where an escalation does not."""
    root = tmp_path / "repo"
    binder = a_real_binder_over(root, {"m.py@b1": TYPOS})
    copies = [returned(wire) for wire in copies_over(binder, patched("m.py@b1"))]
    out, result = handle(CopiesReturned("4c", copies, binder, root, None))
    assert result is not None and result.batch, out
    return result


def test_a_human_question_alone_in_answers_is_the_roles_part_done(
    tmp_path, monkeypatch, capsys
):
    """`--answers` holds a human question to the same exit `--edit-copy` does:
    the role's part is done, and it is the task agent who asks."""
    result = _composed(tmp_path)
    (tmp_path / "batch.json").write_text(json.dumps(result.batch), encoding="utf-8")
    (slot,) = result.batch["block-context"]
    path = _answers_file(
        tmp_path,
        "block-context",
        [
            {
                **slot,
                "instruction": "query",
                "reason": "which the author meant is theirs to say",
                "claim": {
                    "shape": "human-review-necessary",
                    "attempted": "read both texts against the code",
                    "settles": "the author",
                },
            }
        ],
    )
    code, out, _ = _check(monkeypatch, capsys, tmp_path, path, "block-context")
    assert code == command.ASKS_THE_HUMAN, out
    assert (
        "asks the human m.py@b1: block-context -- which the author meant is theirs"
        " to say; this is the role's part done"
    ) in out, out
    assert "1 answered, 0 the fold would refuse, 1 question(s) for the human" in out


class TestTheContract:
    def test_the_contract_prints_as_json_and_exits_zero(self, monkeypatch, capsys):
        code, out, _ = _run(monkeypatch, capsys, "--contract")
        assert code == 0
        got = json.loads(out)
        assert set(got) == {"stage_4c_mark", "escalation", "composition", "placement"}
        assert "hold" in got["escalation"]["instruction"]
