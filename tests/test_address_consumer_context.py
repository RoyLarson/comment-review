import json
from typing import Any

import pytest
from conftest import SAMPLE, build, run_command

from comment_review.binder.binder import bind
from comment_review.commands import carry as carry_command
from comment_review.flows import reading_context, revise
from comment_review.reading.diagnostics import ReadFailure


def held_tree(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    (root / "m.py").write_text(SAMPLE, encoding="utf-8", newline="")
    page = build(SAMPLE)
    binder = bind([page], read_from={"root": str(root)})
    return root, page, binder


def test_carry_command_refuses_before_read_or_write(tmp_path, monkeypatch, capsys):
    root, _, binder = held_tree(tmp_path)
    artifact = tmp_path / "binder.json"
    wire = binder.serialize()
    wire["pages"][0]["reading"]["reader"] = "uninstalled-reader"
    original = json.dumps(wire)
    artifact.write_text(original, encoding="utf-8")
    monkeypatch.setattr(
        carry_command, "page_of", lambda *a, **k: pytest.fail("read before admission")
    )
    code, out = run_command(
        monkeypatch,
        capsys,
        carry_command,
        "--binder",
        str(artifact),
        "--repo",
        str(root),
        "--path",
        "m.py",
        "--cue",
        "b99",
    )
    assert code == 2 and "regather" in out
    assert artifact.read_text(encoding="utf-8") == original


def test_pull_refuses_direct_schedule_context_before_output(tmp_path):
    from comment_review.docket.docket import Docket, Schedule

    root, page, _ = held_tree(tmp_path)
    invalid: Any = None
    docket = Docket(
        schedules=(
            Schedule(path="m.py", sha=page.sha, reading=invalid, alterations=()),
        )
    )
    output = tmp_path / "missing-parent" / "revise"
    result = revise.pull(docket, root, output)
    assert result.refusals and "regather" in result.refusals[0].why
    assert not output.parent.exists()


@pytest.mark.parametrize("consumer", ["carry", "pull"])
def test_saved_consumers_retain_the_saved_context(
    tmp_path, monkeypatch, capsys, consumer
):
    from comment_review.docket.docket import Docket, Schedule
    from comment_review.flows import page_for

    root, page, _ = held_tree(tmp_path)
    saved = reading_context.context_for(root / "m.py")
    assert not isinstance(saved, ReadFailure)
    page.reading = saved
    binder = bind([page], read_from={"root": str(root)})
    actual = page_for.page_for
    admitted = []

    def observe(*args, **kwargs):
        result = actual(*args, **kwargs)
        if not isinstance(result, ReadFailure):
            admitted.append(result.reading)
        return result

    monkeypatch.setattr(page_for, "page_for", observe)
    if consumer == "carry":
        artifact = tmp_path / "binder.json"
        artifact.write_text(json.dumps(binder.serialize()), encoding="utf-8")
        empty = next(
            p.address.split("@")[-1]
            for p in page.paragraphs
            if p.address and not p.raw_text.strip()
        )
        code, out = run_command(
            monkeypatch,
            capsys,
            carry_command,
            "--binder",
            str(artifact),
            "--repo",
            str(root),
            "--path",
            "m.py",
            "--cue",
            empty,
        )
        assert code == 0, out
    else:
        docket = Docket(
            schedules=(
                Schedule(path="m.py", sha=page.sha, reading=saved, alterations=()),
            )
        )
        output = tmp_path / "revise"
        result = revise.pull(docket, root, output)
        assert not result.refusals
    assert admitted
    assert all(reading == saved for reading in admitted)
