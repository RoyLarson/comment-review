"""The rig, assembled: two plugin versions, one staged case, one workspace.

This is the test that asks whether the four mechanics HOLD TOGETHER, rather than
whether each works alone. Roy, 2026-08-29: *"grab the 0.1.0 scripts and the 0.2.2
scripts and run the test on a couple of the local script files to make certain
this runs and sticks together."*

! `v0.1.0` DOES NOT EXIST. The earliest tag in this repo is `v0.1.6`
(2026-08-16), and it is used as the early arm.

! NOTHING HERE DISPATCHES A SUBAGENT. What is asserted is that both arms are
staged, isolated and addressable, and that the real aggregator can see them --
the half of B3 that is code. The half that spawns the two arms is an agent
action at run time.
"""

import json
import pathlib
import subprocess

import pytest
import snapshot_plugin
import stage_case
import workspace

REPO = pathlib.Path(__file__).resolve().parents[2]

SKILL_CREATOR = pathlib.Path(
    r"C:\Users\Roy\.claude\plugins\marketplaces\claude-plugins-official"
    r"\plugins\skill-creator\skills\skill-creator"
)

ARMS = {"old_skill": "v0.1.6", "with_skill": "v0.2.2"}

# The material under review: two of this repo's own scripts, at the later ref.
START = "v0.2.2"
CASE_PATHS = [
    "scripts/check_shipped_syntax.py",
    "scripts/vocabulary_sweep.py",
]

GRADING = {
    "summary": {"pass_rate": 0.5, "passed": 1, "failed": 1, "total": 2},
    "expectations": [
        {"text": "the stale path is caught", "passed": True, "evidence": "line 95"},
        {"text": "the floor claim is checked", "passed": False, "evidence": "none"},
    ],
}


def blob_at(commit: str, path: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(REPO), "show", f"{commit}:{path}"],
        capture_output=True, check=True,
    ).stdout


def test_two_plugin_versions_are_isolated_from_each_other(tmp_path):
    """Each arm is a different tree, and each is clean against its own manifest."""
    taken = {
        arm: snapshot_plugin.snapshot(REPO, ref, tmp_path / arm)
        for arm, ref in ARMS.items()
    }

    assert taken["old_skill"].commit != taken["with_skill"].commit
    for arm, manifest in taken.items():
        assert snapshot_plugin.verify(manifest) == [], arm
        assert manifest.files, arm

    # the two versions genuinely differ, or the comparison measures nothing
    assert taken["old_skill"].files != taken["with_skill"].files


def test_the_case_material_is_staged_byte_identical(tmp_path):
    """Two of this repo's own scripts, as they stood at the ref."""
    staged = stage_case.stage(REPO, START, CASE_PATHS, tmp_path / "case")

    assert staged == sorted(CASE_PATHS)
    for path in CASE_PATHS:
        assert (tmp_path / "case" / path).read_bytes() == blob_at(START, path)


@pytest.mark.skipif(
    not SKILL_CREATOR.is_dir(), reason="skill-creator is not installed on this machine"
)
def test_the_rig_assembles_and_the_aggregator_reads_it(tmp_path):
    """Snapshot both arms, stage the case, build the workspace, aggregate.

    ! THE ASSERTION IS THAT BOTH ARMS SURVIVE TO `benchmark.json`. An arm the
    aggregator skips is skipped in silence, so "it exited 0" is not the check.
    """
    ws = tmp_path / "comment-review-workspace"
    case = tmp_path / "case"
    stage_case.stage(REPO, START, CASE_PATHS, case)
    workspace.write_eval_metadata(
        ws, 1, "two-local-scripts", prompt="review the comments in these files",
        files=CASE_PATHS, start=START,
    )

    taken = {}
    for arm, ref in ARMS.items():
        taken[arm] = snapshot_plugin.snapshot(REPO, ref, tmp_path / "plugin" / arm)
        run = workspace.run_dir(ws, 1, "two-local-scripts", arm, run=1)
        (run / "grading.json").write_text(json.dumps(GRADING), encoding="utf-8")
        workspace.record_timing(run, total_tokens=84852, duration_ms=23332)

    done = subprocess.run(
        ["python", "scripts/aggregate_benchmark.py",
         str(ws / "iteration-1"), "--skill-name", "comment-review"],
        cwd=SKILL_CREATOR, capture_output=True, text=True,
    )
    assert done.returncode == 0, done.stderr

    benchmark = json.loads((ws / "iteration-1" / "benchmark.json").read_text())
    assert set(benchmark["run_summary"]) >= set(ARMS)

    # every arm still names the tree it scored, after the whole assembly
    for arm, manifest in taken.items():
        assert snapshot_plugin.verify(manifest) == [], arm
        assert manifest.ref == ARMS[arm]


@pytest.mark.skipif(
    not SKILL_CREATOR.is_dir(), reason="skill-creator is not installed on this machine"
)
def test_a_variant_over_an_arm_survives_the_assembly(tmp_path):
    """The rig's own cycle: load a theory onto one arm, and it stays declared.

    A run comparing `v0.2.2` against `v0.2.2 plus one edited role` is the shape
    `Process: #53` describes, and it must remain distinguishable from tampering
    all the way through.
    """
    base = snapshot_plugin.snapshot(REPO, "v0.2.2", tmp_path / "plugin")
    role = "plugins/comment-review/agents/comment-review-block-context.md"
    edit = tmp_path / "theory.md"
    edit.write_text("a narrowed remit\n", encoding="utf-8")

    loaded = snapshot_plugin.overlay(base, {role: edit})

    assert snapshot_plugin.verify(loaded) == []
    assert snapshot_plugin.verify(base) == [role]
    assert list(loaded.variant) == [role]

    clean = snapshot_plugin.reset(REPO, loaded)
    assert clean.variant == {}
    assert snapshot_plugin.verify(clean) == []
