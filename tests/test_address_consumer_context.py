from typing import Any

from conftest import SAMPLE, build

from comment_review.flows import reading_context, revise
from comment_review.reading.diagnostics import ReadFailure


def held_tree(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    (root / "m.py").write_text(SAMPLE, encoding="utf-8", newline="")
    page = build(SAMPLE)
    return root, page


def test_pull_refuses_direct_schedule_context_before_output(tmp_path):
    from comment_review.docket.docket import Docket, Schedule

    root, page = held_tree(tmp_path)
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


def test_pull_retains_the_saved_context(tmp_path, monkeypatch):
    from comment_review.docket.docket import Docket, Schedule
    from comment_review.flows import page_for

    root, page = held_tree(tmp_path)
    saved = reading_context.context_for(root / "m.py")
    assert not isinstance(saved, ReadFailure)
    page.reading = saved
    actual = page_for.page_for
    admitted = []

    def observe(*args, **kwargs):
        result = actual(*args, **kwargs)
        if not isinstance(result, ReadFailure):
            admitted.append(result.reading)
        return result

    monkeypatch.setattr(page_for, "page_for", observe)
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
