"""The independent grader -- a pinned model, a versioned rubric, and no arithmetic.

!! IT RECORDS A JUDGEMENT; IT DOES NOT COMPUTE ONE. Roy, 2026-08-29: *"That would
make sense if there was a way of turning these ordinals into compossible vectors
and be certain that there is a mappable relationship across the grades to the
final grade. Both of those are false so we are slightly stuck with perception.
Maybe after several runs we could figure out how to make them correct."*

! SO THERE IS NO `aggregate()` HERE, DELIBERATELY. A mean over A=4, B=3, C=2
asserts the A-to-B distance equals the B-to-C distance, which nothing
establishes, and a weighted combination asserts a mapping from the five axes to
an overall, which nothing establishes either. **Putting either in code would not
make it auditable -- it would make a guess look like arithmetic.**

! WHAT IS RECORDED IS WHAT MAKES THE MAPPING FINDABLE LATER: every axis, the
overall, the judge's REASON for the overall, and the two things that decide
whether two grades are comparable at all -- the rubric version and the exact
model id.

!! AND THE ONE REAL NUMBER IS KEPT SEPARATE. `benchmark.json` wants a
`pass_rate` float. The MECHANICAL half is a genuine count -- N of M citations
verified -- so that fills it; the letters ride alongside untouched. Putting a
letter there would smuggle the invented metric back in through the reporting.

! THE JUDGE IS NOT A SUBAGENT, ON A MECHANICAL GROUND: the `Agent` tool's model
parameter takes a FAMILY ALIAS, so a subagent grade cannot name a version and
inherits a context lineage besides (`decision-log.md Process: #55`).
"""

from __future__ import annotations

import json
import os
import pathlib

#: The judge. An exact id, never a family alias -- `opus` names a family, so two
#: runs months apart could be graded by two different models and report the same
#: word. Ruled by Roy, 2026-08-29.
MODEL = "claude-opus-5"

#: Bumped whenever `rubric.md` changes. Grades made under different rubrics
#: answer different questions and must not be pooled.
RUBRIC_VERSION = 1

RUBRIC = pathlib.Path(__file__).resolve().parent / "rubric.md"

GRADES = ["A", "B", "C", "D", "F", "N/A"]
AXES = ["detection", "diagnosis", "prescription", "restraint", "evidence"]


class NoCredential(Exception):
    """No API key, which is a setup problem rather than a grading failure."""


def _axis_schema() -> dict:
    return {
        "type": "object",
        "properties": {
            "grade": {"type": "string", "enum": GRADES},
            "reason": {"type": "string"},
        },
        "required": ["grade", "reason"],
        "additionalProperties": False,
    }


#: The shape the judge's answer must satisfy. ! IT IS ENFORCED BY THE API, not
#: parsed hopefully afterwards -- `output_config.format` guarantees the first
#: block is text holding valid JSON of this shape, which removes the failure
#: where a judge invents a field name and the downstream tool silently skips it.
GRADING_SCHEMA = {
    "format": {
        "type": "json_schema",
        "schema": {
            "type": "object",
            "properties": {
                "axes": {
                    "type": "object",
                    "properties": {axis: _axis_schema() for axis in AXES},
                    "required": AXES,
                    "additionalProperties": False,
                },
                "overall": {"type": "string", "enum": GRADES},
                "overall_reason": {"type": "string"},
            },
            "required": ["axes", "overall", "overall_reason"],
            "additionalProperties": False,
        },
    }
}


def rubric_text() -> str:
    """The rules the judge is handed, as a versioned file rather than a prompt.

    ! A PROMPT TYPED INTO A SESSION CANNOT BE DIFFED OR RE-RUN. Keeping the rules
    on disk is what lets a later reader see which rules produced a grade, and
    lets the same grade be re-derived.
    """
    return RUBRIC.read_text(encoding="utf-8")


def build_prompt(
    *,
    findings: pathlib.Path,
    under_review: pathlib.Path,
    start: str,
    end: str,
    end_diff: str,
    mechanical: dict,
) -> str:
    """Everything the judge sees, and nothing else.

    ! NO ARM IS NAMED. The judge is not told which version produced this, or that
    a second one exists -- `Process: #55`. A judge told to ignore the other arm
    has still been told about it.
    """
    return "\n".join(
        [
            rubric_text(),
            "",
            "---",
            "",
            f"## The case: START `{start}` -> END `{end}`",
            "",
            "### What END changed (the answer key)",
            "",
            "```diff",
            end_diff.strip() or "(no diff supplied)",
            "```",
            "",
            "### The file as it stood at START -- what the run read",
            "",
            "```python",
            under_review.read_text(encoding="utf-8"),
            "```",
            "",
            "### What the run filed",
            "",
            findings.read_text(encoding="utf-8"),
            "",
            "### Mechanical verification, already performed for you",
            "",
            "```json",
            json.dumps(mechanical, indent=2, sort_keys=True),
            "```",
            "",
            "Grade the five axes and give the overall, in the required shape.",
        ]
    )


def stamp(graded: dict, *, arm: str, eval_id: str) -> dict:
    """Attach what a later reader needs to know a grade is comparable."""
    return {
        **graded,
        "model": MODEL,
        "rubric_version": RUBRIC_VERSION,
        "arm": arm,
        "eval_id": eval_id,
    }


def to_grading_json(judged: dict, *, mechanical: dict, arm: str, eval_id: str) -> dict:
    """The artifact on disk: a real count in `summary`, the letters beside it.

    ! `summary` IS THE MECHANICAL HALF ALONE, because it is the half that is
    actually countable. `aggregate_benchmark` reads `summary.pass_rate` and would
    happily take a number derived from letters -- which is the invented metric
    arriving through the back door.
    """
    checked = int(mechanical.get("citations_checked", 0))
    failed = int(mechanical.get("citations_failed", 0))
    passed = checked - failed
    return {
        "summary": {
            "passed": passed,
            "failed": failed,
            "total": checked,
            "pass_rate": (passed / checked) if checked else 0.0,
        },
        "mechanical": mechanical,
        "editorial": stamp(judged, arm=arm, eval_id=eval_id),
    }


def grade(
    *,
    findings: pathlib.Path,
    under_review: pathlib.Path,
    start: str,
    end: str,
    end_diff: str,
    mechanical: dict,
    arm: str,
    eval_id: str,
) -> dict:
    """Call the judge, and return the artifact to write.

    ! THE CREDENTIAL IS CHECKED BEFORE THE FILES ARE READ, so a machine with no
    key fails on the thing that is actually missing rather than on a path.
    """
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise NoCredential(
            "ANTHROPIC_API_KEY is not set. The grader is a direct API call so its "
            "model can be pinned to an exact version; set the key, or run "
            "`ant auth login`, before grading."
        )

    import anthropic

    client = anthropic.Anthropic()
    response = client.messages.create(
        model=MODEL,
        max_tokens=16000,
        output_config={**GRADING_SCHEMA, "effort": "high"},
        messages=[
            {
                "role": "user",
                "content": build_prompt(
                    findings=findings,
                    under_review=under_review,
                    start=start,
                    end=end,
                    end_diff=end_diff,
                    mechanical=mechanical,
                ),
            }
        ],
    )
    text = next(b.text for b in response.content if b.type == "text")
    return to_grading_json(
        json.loads(text), mechanical=mechanical, arm=arm, eval_id=eval_id
    )
