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
#:
#: !! v2 REPLACED `restraint` WITH `unkeyed`, because `restraint` was INVALID:
#: it graded a run down for filing on any paragraph END left alone, which reads
#: *"the human did not fix this"* as *"this was correct"*. END is a POSITIVE key.
#: Roy, 2026-08-29: *"The human -- me in a lot of these cases -- certainly missed
#: things. Numpy and the other libraries are full of missed things."*
RUBRIC_VERSION = 2

RUBRIC = pathlib.Path(__file__).resolve().parent / "rubric.md"

GRADES = ["A", "B", "C", "D", "F", "N/A"]
AXES = ["detection", "diagnosis", "prescription", "unkeyed", "evidence"]

#: How a claim outside the END diff is ruled -- against the CODE, not the key.
#: ! `true` IS NOT A DEFECT. It is a finding the human missed, which on a real
#: corpus is the common case rather than the exception.
UNKEYED_VERDICTS = ["true", "false", "query"]


class SetupProblem(Exception):
    """The machine is not set up to grade -- not a bad grade, and not a bug.

    ! A SHARED BASE SO ONE `except` COVERS BOTH, because a caller does the same
    thing either way: say what is missing and stop, rather than retrying.
    """


class NoCredential(SetupProblem):
    """No credential resolved, which is a setup problem, not a grading failure."""


class NoWorkspace(SetupProblem):
    """A credential resolved, but the request names no workspace to act in."""


class NoCredit(SetupProblem):
    """Credential and workspace both resolved; the account cannot pay."""


#: What the SDK says when it has tried every credential path and found none.
#: MEASURED 2026-08-29 against `anthropic==1.2.0`: a `TypeError` raised BEFORE
#: any network call, so translating it costs nothing and reaches no API.
NO_AUTH = "Could not resolve authentication method"

#: The HEADER NAME, which is what every workspace 400 has in common.
#:
#: !! MATCHING THE FULL SENTENCE CAUGHT ONLY ONE OF TWO, and this read
#: `"anthropic-workspace-id is required"` for an hour on 2026-08-29. MEASURED,
#: both on live calls minutes apart:
#:
#:     no header sent      "anthropic-workspace-id is required when
#:                          authenticating with an identity-linked API key"
#:     header sent, bad    "anthropic-workspace-id header must be a valid
#:                          workspace ID."
#:
#: The second went to a raw traceback because the first was what was matched --
#: which is the failure the translation exists to prevent, reproduced by making
#: the pattern more specific than the thing it identifies.
NO_WORKSPACE = "anthropic-workspace-id"

#: What the API says when the account cannot pay for the call. MEASURED
#: 2026-08-29, reached only after auth and the workspace both resolved -- so it
#: is the LAST setup gate, and the first that costs nothing to hit.
NO_CREDIT = "credit balance is too low"

#: Read by `_client` and sent as a header. ! THE SDK DOES NOT READ IT ON THIS
#: PATH: `_fill_missing_from_env` fills a PROFILE's config, so with a bare
#: `ANTHROPIC_API_KEY` and no profile there is no config to fill and the
#: variable is never consulted. Sending the header is what makes it work.
WORKSPACE_ENV = "ANTHROPIC_WORKSPACE_ID"


def _client():
    """The SDK client, letting it resolve the credential itself.

    !! AN UNSET `ANTHROPIC_API_KEY` DOES NOT MEAN THERE IS NO CREDENTIAL, and
    this module checked exactly that until 2026-08-29. The constructor resolves
    an env key, an auth token, OR a profile written by `ant auth login` -- so
    gating on the variable REFUSES a machine that is correctly set up the other
    way.

    ! AND CONSTRUCTING TELLS YOU NOTHING EITHER: measured, `Anthropic()` builds
    fine with `api_key = None` and fails later. The only honest check is to make
    the request and translate the failure.

    !! THE WORKSPACE HEADER IS SENT HERE BECAUSE THE SDK WILL NOT SEND IT. An
    identity-linked key REQUIRES `anthropic-workspace-id`, and the env var that
    names it is only read when a profile supplies the config it fills -- so on
    the plain-key path the header has to be set explicitly or every request is
    a 400. ! Absent when the variable is unset, because a workspace-scoped key
    must not be sent one.
    """
    import anthropic

    workspace = os.environ.get(WORKSPACE_ENV)
    headers = {"anthropic-workspace-id": workspace} if workspace else {}
    return anthropic.Anthropic(default_headers=headers)


def setup_problem(message: str) -> SetupProblem | None:
    """The setup fault this API error names, or None if it names none.

    !! THREE GATES SIT IN FRONT OF A GRADE, AND EACH WAS FOUND BY A LIVE RUN
    FAILING IN FRONT OF SOMEONE -- credential, then workspace, then credit,
    discovered in that order on 2026-08-29 because each one has to pass before
    the next can be reached. ! Adding the fourth is a clause here rather than a
    fourth place to catch an exception, which is what this was on the first two.

    !! IT RETURNS RATHER THAN RAISES so the caller keeps `raise ... from e` and
    the original error stays chained. A translation that discarded the cause
    would trade one unreadable failure for a different one.

    ! ANYTHING NOT NAMED HERE IS NOT A SETUP PROBLEM and gets `None`, so its
    traceback survives. A malformed request of OUR OWN making is also a 400,
    and hiding that behind a friendly sentence is how a bug in this file would
    come to read as a problem with someone's account.
    """
    if NO_WORKSPACE in message:
        # ! WHICH OF THE TWO IS SAID, because the fix differs: one needs a value
        # supplied, the other needs the value REPLACED, and "set the workspace"
        # is unhelpful advice to someone who already did.
        sent = os.environ.get(WORKSPACE_ENV)
        if sent:
            detail = (
                f"{WORKSPACE_ENV} is {sent!r}, and the API rejected that as not "
                "a valid workspace ID."
            )
        else:
            detail = f"{WORKSPACE_ENV} is not set, so the request named no workspace."
        return NoWorkspace(
            f"The credential resolved, but the request names no usable "
            f"workspace. {detail} An IDENTITY-LINKED key -- one the console "
            f"describes as available for ALL workspaces -- cannot be inferred, "
            f"so it must name the one it acts in. Set {WORKSPACE_ENV} to a "
            "`wrkspc_...` id from console.anthropic.com -> Settings -> "
            'Workspaces. ! The literal "default" is NOT accepted on this header '
            "-- measured 2026-08-29; the SDK documents it for the federation "
            "token exchange only. ! A workspace-SCOPED key needs none of this: "
            "leave the variable unset."
        )
    if NO_CREDIT in message:
        return NoCredit(
            "The credential and the workspace both resolved -- this is the last "
            "setup gate -- but the account cannot pay for the call. Add credit "
            "at console.anthropic.com -> Plans & Billing, to the organisation "
            f"that owns the workspace {os.environ.get(WORKSPACE_ENV) or 'in use'}"
            ". ! A grade is a real API call at a pinned model, so grading is a "
            "metered activity and every reading is billed: `--runs 3` is three."
        )
    return None


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
                # !! ITEMISED, NOT COUNTED INTO AN AXIS. A run finding ten real
                # defects the human missed and a run finding none must not come
                # out alike, and the `unkeyed` grade -- which is about the FALSE
                # ones -- cannot tell them apart on its own.
                "unkeyed_claims": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "cite": {"type": "string"},
                            "verdict": {"type": "string", "enum": UNKEYED_VERDICTS},
                            "reason": {"type": "string"},
                        },
                        "required": ["cite", "verdict", "reason"],
                        "additionalProperties": False,
                    },
                },
                # ! RECORDED, NOT GRADED, and deliberately outside `axes` -- see
                # `rubric.md`. Whether a reader learns the REASON is the half of
                # this system's stated purpose the axes do not cover, and
                # whether it is a real axis is still open.
                "reader_value": {"type": "string"},
                "overall": {"type": "string", "enum": GRADES},
                "overall_reason": {"type": "string"},
            },
            "required": [
                "axes",
                "unkeyed_claims",
                "reader_value",
                "overall",
                "overall_reason",
            ],
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
    client=None,
) -> dict:
    """Call the judge, and return the artifact to write.

    ! `client` IS INJECTABLE SO THE REFUSAL CAN BE TESTED WITHOUT A NETWORK OR A
    BILL. A test that drove the real SDK would pass for free on a machine with no
    credential and quietly cost money on one that has it -- which is a test whose
    behaviour depends on who runs it.
    """
    client = client or _client()
    try:
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
    except TypeError as e:
        # ! MATCHED ON THE MESSAGE, not on the type. `TypeError` is what the SDK
        # happens to raise here, and swallowing every one of them would hide a
        # real bug in the call above as though it were a missing key.
        if NO_AUTH not in str(e):
            raise
        raise NoCredential(
            "No Anthropic credential resolved. The grader is a direct API call so "
            "its model can be pinned to an exact version. Set ANTHROPIC_API_KEY, "
            "or run `ant auth login` -- either is read automatically."
        ) from e
    except Exception as e:
        # ! MATCHED ON THE MESSAGE FOR THE SAME REASON, and re-raised otherwise.
        # Catching the SDK's own error class would need it imported at module
        # level, which this module deliberately avoids -- and a 400 this table
        # does not name is a real failure that must keep its traceback.
        problem = setup_problem(str(e))
        if problem is None:
            raise
        raise problem from e
    text = next(b.text for b in response.content if b.type == "text")
    return to_grading_json(
        json.loads(text), mechanical=mechanical, arm=arm, eval_id=eval_id
    )
