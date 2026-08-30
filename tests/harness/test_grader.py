"""The independent grader: a pinned model, a versioned rubric, no arithmetic.

!! THERE IS NO TEST FOR AN AGGREGATION FUNCTION, AND THAT IS THE POINT. Roy,
2026-08-29: *"That would make sense if there was a way of turning these ordinals
into compossible vectors and be certain that there is a mappable relationship
across the grades to the final grade. Both of those are false so we are slightly
stuck with perception."* The judge gives the overall; this module RECORDS it.
A `mean(A=4, B=3, ...)` would assert a metric nobody has established.

! WHAT IS TESTED IS EVERYTHING THAT IS NOT A JUDGEMENT: the prompt the judge is
handed, the schema its answer must satisfy, the mechanical counts, the pinning,
and the refusal when there is no key. The live call is not tested -- it costs
money and needs a credential this machine does not have.
"""

import json
import pathlib

import grader
import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]


def test_the_model_is_pinned_to_an_exact_id():
    """Roy, 2026-08-29: a fresh clean specific model, with the version number.

    ! A FAMILY ALIAS IS NOT A VERSION. `opus` is what the Agent tool accepts and
    is why a subagent cannot be the grader -- it names a family, so two runs
    months apart can be graded by two different models and report the same word.
    """
    assert grader.MODEL == "claude-opus-5"
    assert grader.MODEL not in ("opus", "sonnet", "haiku", "fable")


def test_the_rubric_version_travels_with_the_grade():
    """Grades taken under different rubrics are not comparable.

    The later question -- does any mapping exist from the axes to the overall --
    can only be asked of samples graded the same way.
    """
    assert grader.RUBRIC_VERSION == 2
    assert "Version: 2" in grader.rubric_text()


def test_the_schema_demands_every_axis_and_the_reason():
    """The judge's answer has to carry the data the later analysis needs."""
    schema = grader.GRADING_SCHEMA["format"]["schema"]
    axes = schema["properties"]["axes"]["properties"]

    assert set(axes) == {
        "detection",
        "diagnosis",
        "prescription",
        "unkeyed",
        "evidence",
    }
    for axis in axes.values():
        assert set(axis["properties"]) == {"grade", "reason"}
        assert axis["properties"]["grade"]["enum"] == ["A", "B", "C", "D", "F", "N/A"]

    assert "overall" in schema["properties"]
    assert "overall_reason" in schema["properties"]
    assert schema["additionalProperties"] is False


def test_a_claim_outside_the_key_is_adjudicated_against_the_code():
    """END is a POSITIVE key -- absence of a fix is not evidence of correctness.

    Roy, 2026-08-29, ruling on how a finding outside the END diff is treated:
    adjudicate it against the code. A true finding the human missed is not a
    false positive, and an instrument that cannot record a run EXCEEDING its key
    is measuring the wrong thing.
    """
    schema = grader.GRADING_SCHEMA["format"]["schema"]
    claims = schema["properties"]["unkeyed_claims"]

    assert claims["type"] == "array"
    entry = claims["items"]["properties"]
    assert set(entry) == {"cite", "verdict", "reason"}
    assert entry["verdict"]["enum"] == ["true", "false", "query"]

    assert "unkeyed_claims" in schema["required"]


def test_reader_value_is_recorded_and_carries_no_grade():
    """Roy, 2026-08-29: record it unscored, decide later.

    ! IT IS NOT IN `axes`, WHICH IS THE WHOLE POINT. Adding the softest axis
    before the spread on the hard ones is even measured would put the most
    variance into the grade at the moment it is least able to carry it.
    """
    schema = grader.GRADING_SCHEMA["format"]["schema"]

    assert schema["properties"]["reader_value"]["type"] == "string"
    assert "reader_value" not in schema["properties"]["axes"]["properties"]
    assert "reader_value" in schema["required"]


def test_the_prompt_carries_the_rubric_and_the_artifacts(tmp_path):
    """What the judge is handed, and nothing else."""
    findings = tmp_path / "findings.md"
    findings.write_text("RECORD: a made-up finding\n", encoding="utf-8")
    under_review = tmp_path / "galley.py"
    under_review.write_text("def f():\n    return 1\n", encoding="utf-8")

    prompt = grader.build_prompt(
        findings=findings,
        under_review=under_review,
        start="1ad4ba72",
        end="deadbeef",
        end_diff="--- a/galley.py\n+++ b/galley.py\n",
        mechanical={"citations_checked": 3, "citations_failed": 0},
    )

    assert "Version: 2" in prompt
    assert "a made-up finding" in prompt
    assert "def f():" in prompt
    assert "1ad4ba72" in prompt and "deadbeef" in prompt


def test_the_prompt_never_mentions_another_arm(tmp_path):
    """`decision-log.md Process: #55` -- no arm judges another arm.

    ! CHECKED ON THE ACTUAL STRING, because the isolation is a property of what
    was SENT. A grader told to ignore the other arm has still been told about it.
    """
    findings = tmp_path / "findings.md"
    findings.write_text("RECORD\n", encoding="utf-8")
    under_review = tmp_path / "x.py"
    under_review.write_text("pass\n", encoding="utf-8")

    prompt = grader.build_prompt(
        findings=findings,
        under_review=under_review,
        start="a",
        end="b",
        end_diff="",
        mechanical={},
    )

    for leak in ("old_skill", "with_skill", "the other arm", "baseline"):
        assert leak not in prompt, leak


def test_a_grade_records_what_produced_it():
    """A grade whose judge is unnamed cannot be re-derived -- D2 asks for it."""
    recorded = grader.stamp({"overall": "C"}, arm="old_skill", eval_id="a-case")

    assert recorded["model"] == "claude-opus-5"
    assert recorded["rubric_version"] == 2
    assert recorded["arm"] == "old_skill"
    assert recorded["eval_id"] == "a-case"
    assert recorded["overall"] == "C"


def test_the_summary_carries_only_the_MECHANICAL_rate(tmp_path):
    """`benchmark.json` wants a float, and the editorial letters are not one.

    !! FORCING A LETTER INTO `pass_rate` SMUGGLES THE INVENTED METRIC BACK IN
    THROUGH THE REPORTING. The mechanical half is a real count -- N of M
    citations verified -- so that is what fills it, and the letters ride
    alongside untouched.
    """
    graded = grader.to_grading_json(
        {
            "axes": {
                "detection": {"grade": "A", "reason": "r"},
                "diagnosis": {"grade": "F", "reason": "r"},
                "prescription": {"grade": "N/A", "reason": "r"},
                "unkeyed": {"grade": "B", "reason": "r"},
                "evidence": {"grade": "A", "reason": "r"},
            },
            "unkeyed_claims": [],
            "reader_value": "the replacement states the what, never the why",
            "overall": "D",
            "overall_reason": "right paragraph, wrong reason",
        },
        mechanical={"citations_checked": 4, "citations_failed": 1},
        arm="with_skill",
        eval_id="a-case",
    )

    assert graded["summary"]["passed"] == 3
    assert graded["summary"]["total"] == 4
    assert graded["summary"]["pass_rate"] == 0.75
    assert graded["editorial"]["overall"] == "D"
    assert graded["editorial"]["axes"]["diagnosis"]["grade"] == "F"

    # the letters are nowhere in the numeric summary
    assert "D" not in json.dumps(graded["summary"])


class _Keyless:
    """A client that fails the way the real SDK does with no credential.

    MEASURED against `anthropic==1.2.0`: a `TypeError` whose message is
    "Could not resolve authentication method ...", raised BEFORE any network
    call -- so the SDK had already tried the env key, the auth token and the
    `ant auth login` profile.
    """

    class messages:  # noqa: N801 - mirrors the SDK's attribute, not a class name
        @staticmethod
        def stream(**_):
            raise TypeError(
                "Could not resolve authentication method. Expected one of "
                "api_key, auth_token, or credentials to be set."
            )


class _Broken:
    """A client whose call has a genuine bug in it."""

    class messages:  # noqa: N801
        @staticmethod
        def stream(**_):
            raise TypeError("stream() got an unexpected keyword argument 'moddel'")


def _files(tmp_path):
    findings = tmp_path / "findings.md"
    findings.write_text("RECORD\n", encoding="utf-8")
    under_review = tmp_path / "x.py"
    under_review.write_text("pass\n", encoding="utf-8")
    return findings, under_review


def test_it_refuses_clearly_when_no_credential_resolves(tmp_path):
    """A missing credential is a setup problem and must read as one.

    !! IT DOES NOT GATE ON `ANTHROPIC_API_KEY`, AND DID UNTIL 2026-08-29. An
    unset variable does not mean there is no credential -- a profile written by
    `ant auth login` is resolved by the same constructor -- so the old check
    refused a machine that was correctly set up the other way.

    ! THE CLIENT IS INJECTED so this costs nothing and reaches no API. Driving
    the real SDK would pass for free where there is no credential and quietly
    bill where there is one.
    """
    findings, under_review = _files(tmp_path)

    with pytest.raises(grader.NoCredential) as refused:
        grader.grade(
            findings=findings,
            under_review=under_review,
            start="a",
            end="b",
            end_diff="",
            mechanical={},
            arm="old_skill",
            eval_id="c",
            client=_Keyless(),
        )

    assert "ANTHROPIC_API_KEY" in str(refused.value)
    assert "ant auth login" in str(refused.value)


def test_a_real_TypeError_is_not_mistaken_for_a_missing_credential(tmp_path):
    """Matching on the type alone would hide a bug in the call as a setup problem."""
    findings, under_review = _files(tmp_path)

    with pytest.raises(TypeError) as raised:
        grader.grade(
            findings=findings,
            under_review=under_review,
            start="a",
            end="b",
            end_diff="",
            mechanical={},
            arm="old_skill",
            eval_id="c",
            client=_Broken(),
        )

    assert not isinstance(raised.value, grader.NoCredential)
    assert "moddel" in str(raised.value)
