"""B3 -- the directory a run writes into, and the timing captured as it finishes.

`skill-creator` prescribes a workspace beside the skill, organised by iteration,
then by case, then by arm. This builds it.

!! THE LAYOUT COMES FROM `aggregate_benchmark.py`, NOT FROM `SKILL.md`, BECAUSE
THE TWO DISAGREE. SKILL.md:180 says outputs go to
`<workspace>/iteration-<N>/eval-<ID>/with_skill/outputs/` and never mentions a
`run-N` level anywhere in the file. The aggregator requires one:

    aggregate_benchmark.py:105   if not list(config_dir.glob("run-*")): continue

! AND THAT `continue` IS SILENT, where the neighbouring missing-`grading.json`
case prints a warning at :116. **A workspace built from the prose is invisible to
the tool** -- every arm skipped, `benchmark.json` written, exit 0, nothing
measured. That is the failure this harness exists to catch, arriving in the
harness's own input format.

    <workspace>/iteration-<N>/
      eval-<id>/
        eval_metadata.json        <- :87, read for `eval_id` and nothing else
        <arm>/                    <- the config: `with_skill`, `old_skill`
          run-<N>/
            grading.json          <- the grader's, per `agents/grader.md`
            timing.json           <- :139, when grading.json carries no timing
            outputs/              <- what the run produced
"""

from __future__ import annotations

import json
import pathlib


def eval_dir(
    workspace: pathlib.Path, iteration: int, eval_id: str
) -> pathlib.Path:
    """The case's directory, which is the level `eval_metadata.json` sits at."""
    return workspace / f"iteration-{iteration}" / f"eval-{eval_id}"


def run_dir(
    workspace: pathlib.Path,
    iteration: int,
    eval_id: str,
    arm: str,
    run: int = 1,
) -> pathlib.Path:
    """Create and return one arm's run directory, with its `outputs/` beside it.

    ! `run` IS A LEVEL, NOT A DECORATION. B4 reports mean and stddev over the
    default three runs, so an arm holds `run-1`..`run-3` -- and an arm holding
    the files directly is skipped without a word.
    """
    made = eval_dir(workspace, iteration, eval_id) / arm / f"run-{run}"
    (made / "outputs").mkdir(parents=True, exist_ok=True)
    return made


def write_eval_metadata(
    workspace: pathlib.Path, iteration: int, eval_id: str, **fields: object
) -> pathlib.Path:
    """Write the case's metadata at the eval level.

    ! `eval_id` IS THE ONLY KEY ANYTHING READS -- `aggregate_benchmark.py:87-91`
    takes it and falls back to the directory name. The rest is for a human, and
    `assertions` is read by nothing at all (`decision-log.md`, plan A2).
    """
    into = eval_dir(workspace, iteration, eval_id)
    into.mkdir(parents=True, exist_ok=True)
    written = into / "eval_metadata.json"
    written.write_text(
        json.dumps({"eval_id": eval_id, **fields}, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return written


def record_timing(
    run: pathlib.Path, total_tokens: int, duration_ms: int
) -> pathlib.Path:
    """Write the timing a task notification carried, in the shape the tool reads.

    !! THIS IS THE ONLY CHANCE TO CAPTURE IT. SKILL.md: the numbers arrive in the
    notification and are persisted nowhere else, so a run whose notification was
    batched or dropped has no timing and no way to recover one.

    ! THE SECONDS ARE DERIVED, because the two ends disagree: the notification
    gives `duration_ms`, and `aggregate_benchmark.py:144` reads
    `total_duration_seconds`. Omitting it is not an error -- it is a timing
    column of zeroes.
    """
    written = run / "timing.json"
    written.write_text(
        json.dumps(
            {
                "total_tokens": total_tokens,
                "duration_ms": duration_ms,
                "total_duration_seconds": round(duration_ms / 1000, 1),
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    return written
