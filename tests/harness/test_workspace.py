"""B3 -- the workspace a run writes into, and the timing it captures.

!! THE LAYOUT IS DERIVED FROM `aggregate_benchmark.py`, NOT FROM `SKILL.md`, AND
THE TWO DISAGREE. SKILL.md:180 says to save outputs to
`<workspace>/iteration-<N>/eval-<ID>/with_skill/outputs/` and never mentions a
`run-N` level. `aggregate_benchmark.py:105` skips any config directory with no
`run-*` child -- `continue`, with NO warning, where a missing `grading.json` does
warn at :116. So a workspace built from the prose is silently invisible to the
tool, and the benchmark reports nothing while exiting 0.

! WHICH IS WHY THE LAST TEST RUNS THE REAL AGGREGATOR. A test asserting my layout
against my own belief about the layout could only agree with itself -- the same
shape that let B1's eol claim stand.
"""

import json
import pathlib
import subprocess

import pytest
import workspace

SKILL_CREATOR = pathlib.Path(
    r"C:\Users\Roy\.claude\plugins\marketplaces\claude-plugins-official"
    r"\plugins\skill-creator\skills\skill-creator"
)

GRADING = {
    "summary": {"pass_rate": 1.0, "passed": 2, "failed": 0, "total": 2},
    "expectations": [
        {"text": "the obituary is caught", "passed": True, "evidence": "line 12"},
        {"text": "the constraint is checked", "passed": True, "evidence": "line 40"},
    ],
}


def test_the_run_directory_carries_the_run_level_the_prose_omits(tmp_path):
    """`run-N` is the level `SKILL.md` never mentions and the aggregator requires."""
    run = workspace.run_dir(tmp_path / "ws", 1, "the-first-case", "with_skill", run=1)

    assert run.relative_to(tmp_path).as_posix() == (
        "ws/iteration-1/eval-the-first-case/with_skill/run-1"
    )
    assert (run / "outputs").is_dir()


def test_timing_derives_the_seconds_from_the_milliseconds(tmp_path):
    """The three keys the notification supplies, in the shape the aggregator reads.

    `aggregate_benchmark.py:144` takes `total_duration_seconds`; the notification
    gives `duration_ms`. Deriving it is the whole job, and getting it wrong is a
    timing column of zeroes rather than an error.
    """
    run = workspace.run_dir(tmp_path / "ws", 1, "c", "with_skill", run=1)

    written = workspace.record_timing(run, total_tokens=84852, duration_ms=23332)

    assert json.loads(written.read_text(encoding="utf-8")) == {
        "total_tokens": 84852,
        "duration_ms": 23332,
        "total_duration_seconds": 23.3,
    }


def test_eval_metadata_sits_at_the_eval_level_not_the_run_level(tmp_path):
    """`aggregate_benchmark.py:87` opens it at `eval-*/`, and reads `eval_id` alone."""
    written = workspace.write_eval_metadata(
        tmp_path / "ws", 1, "the-first-case", prompt="review these files"
    )

    held = json.loads(written.read_text(encoding="utf-8"))

    assert written.parent.name == "eval-the-first-case"
    assert held["eval_id"] == "the-first-case"


@pytest.mark.skipif(
    not SKILL_CREATOR.is_dir(), reason="skill-creator is not installed on this machine"
)
def test_the_real_aggregator_finds_both_arms(tmp_path):
    """The cross-check: the TOOL accepts what this module builds.

    ! A CONFIG DIRECTORY WITH NO `run-*` IS SKIPPED IN SILENCE, so "the aggregator
    exited 0" proves nothing on its own -- the assertion is that BOTH arms appear
    in `benchmark.json`, which is the thing a wrong layout would take away.
    """
    ws = tmp_path / "ws"
    for arm in ("old_skill", "with_skill"):
        run = workspace.run_dir(ws, 1, "the-first-case", arm, run=1)
        (run / "grading.json").write_text(json.dumps(GRADING), encoding="utf-8")
        workspace.record_timing(run, total_tokens=1000, duration_ms=2000)
    workspace.write_eval_metadata(ws, 1, "the-first-case")

    done = subprocess.run(
        ["python", "scripts/aggregate_benchmark.py",
         str(ws / "iteration-1"), "--skill-name", "comment-review"],
        cwd=SKILL_CREATOR, capture_output=True, text=True,
    )

    assert done.returncode == 0, done.stderr
    benchmark = json.loads((ws / "iteration-1" / "benchmark.json").read_text())
    assert set(benchmark["run_summary"]) >= {"old_skill", "with_skill"}
