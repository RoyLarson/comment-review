"""T50: the same judge reads one artifact twice, and the letters are compared.

! THE CLIENT IS INJECTED THROUGHOUT, so none of this reaches the API or bills.
A test driving the real SDK would pass for free on a machine with no credential
and quietly cost money on one that has it -- behaviour that depends on who runs
it is not a test. The stub is what lets a DISAGREEMENT be tested at all: two
real readings might happen to agree, so a suite over the live judge could not
cover the branch this module exists for.
"""

import json

import grader
import pytest
import reread


def _judged(overall="B", detection="B", **axes):
    """One judge answer in the shape `GRADING_SCHEMA` enforces."""
    grades = {axis: "B" for axis in grader.AXES}
    grades["detection"] = detection
    grades.update(axes)
    return {
        "axes": {a: {"grade": g, "reason": f"{a} reason"} for a, g in grades.items()},
        "unkeyed_claims": [],
        "reader_value": "recorded, not graded",
        "overall": overall,
        "overall_reason": "because",
    }


class _Stream:
    """What `client.messages.stream(...)` returns.

    !! THE STUBS MIRROR `stream`, NOT `create`, because that is what `grade`
    calls now -- `max_tokens` is the model's 128K ceiling and the SDK requires
    streaming that large. A stub still offering `create` would pass every test
    against a shape the code never uses, which is the failure that got the old
    suite deleted: a fixture agreeing with a contract that had moved.
    """

    def __init__(self, produce):
        self._produce = produce

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def get_final_message(self):
        return self._produce()


def _message(body, *, stop_reason="end_turn", stop_details=None, text=True, usage=True):
    """A response object in the shape `grade` reads back."""
    blocks = [type("B", (), {"type": "text", "text": body})] if text else []
    return type(
        "R",
        (),
        {
            "content": blocks,
            "stop_reason": stop_reason,
            "stop_details": stop_details,
            "usage": type("U", (), {"input_tokens": 1000, "output_tokens": 2500})
            if usage
            else None,
        },
    )


class _Judge:
    """A client returning a scripted answer per call, in order."""

    def __init__(self, *answers):
        self.answers = list(answers)
        self.prompts = []
        outer = self

        class messages:  # noqa: N801 - mirrors the SDK's attribute
            @staticmethod
            def stream(**kw):
                outer.prompts.append(kw["messages"][0]["content"])
                return _Stream(lambda: _message(json.dumps(outer.answers.pop(0))))

        self.messages = messages


class _Ceiling:
    """A judge cut off by `max_tokens`, which is what cost Roy a run."""

    class messages:  # noqa: N801
        @staticmethod
        def stream(**_):
            # ! Deliberately VALID-looking but truncated, so the only thing
            # separating it from a good reading is `stop_reason`.
            return _Stream(
                lambda: _message('{"axes": {"detect', stop_reason="max_tokens")
            )


class _Refuses:
    """A judge that declined, which may carry no text block at all."""

    class messages:  # noqa: N801
        @staticmethod
        def stream(**_):
            return _Stream(
                lambda: _message(
                    "",
                    stop_reason="refusal",
                    stop_details=type("D", (), {"category": "cyber"}),
                    text=False,
                )
            )


class _Garbage:
    """A judge that finished cleanly and returned prose, not JSON."""

    class messages:  # noqa: N801
        @staticmethod
        def stream(**_):
            return _Stream(lambda: _message("I think it is quite good, overall."))


class _Keyless:
    class messages:  # noqa: N801
        @staticmethod
        def stream(**_):
            raise TypeError(
                "Could not resolve authentication method. Expected one of "
                "api_key, auth_token, or credentials to be set."
            )


def _rejects(message):
    """A client raising one verbatim API error."""

    class _Client:
        class messages:  # noqa: N801
            @staticmethod
            def stream(**_):
                raise RuntimeError(f"Error code: 400 - {message}")

    return _Client()


#: Both workspace 400s, MEASURED on live calls minutes apart 2026-08-29. The
#: second reached Roy as a raw traceback because the translation matched the
#: first sentence rather than the header name they share.
NO_WORKSPACE_SENT = (
    "{'type': 'error', 'error': {'type': 'invalid_request_error', 'message': "
    "'anthropic-workspace-id is required when authenticating with an "
    "identity-linked API key; send the id of the workspace this request "
    "acts in.'}}"
)
BAD_WORKSPACE_SENT = (
    "{'type': 'error', 'error': {'type': 'invalid_request_error', 'message': "
    "'anthropic-workspace-id header must be a valid workspace ID.'}}"
)
#: The LAST setup gate, reached 2026-08-29 only once auth and the workspace
#: both resolved.
NO_CREDIT = (
    "{'type': 'error', 'error': {'type': 'invalid_request_error', 'message': "
    "'Your credit balance is too low to access the Anthropic API. Please go "
    "to Plans & Billing to upgrade or purchase credits.'}}"
)
#: A 400 of OUR OWN making. It must NOT be translated -- a bug in the request
#: this file builds is not a problem with anybody's account.
OUR_OWN_BUG = (
    "{'type': 'error', 'error': {'type': 'invalid_request_error', 'message': "
    "'max_tokens: must be greater than 0'}}"
)


@pytest.fixture
def case(tmp_path):
    findings = tmp_path / "findings.md"
    findings.write_text("RECORD\n", encoding="utf-8")
    under_review = tmp_path / "x.py"
    under_review.write_text("pass\n", encoding="utf-8")
    return {
        "findings": findings,
        "under_review": under_review,
        "start": "aaaa",
        "end": "bbbb",
        "end_diff": "",
        "mechanical": {"citations_checked": 2, "citations_failed": 0},
        "arm": "with_skill",
        "eval_id": "a-case",
    }


def test_two_identical_readings_report_agreement(case):
    result = reread.reread(**case, runs=2, client=_Judge(_judged(), _judged()))

    assert result["agreed"] is True
    assert result["fields"]["overall"]["letters"] == ["B", "B"]
    assert result["fields"]["detection"]["agreed"] is True


def test_a_single_differing_axis_makes_the_whole_run_disagree(case):
    """The claim is that the letters HELD -- one that moved falsifies it."""
    result = reread.reread(
        **case, runs=2, client=_Judge(_judged(), _judged(detection="D"))
    )

    assert result["agreed"] is False
    assert result["fields"]["detection"] == {
        "letters": ["B", "D"],
        "measured": True,
        "agreed": False,
    }
    # ! The axes that did hold still report agreement; a disagreement is located,
    # not smeared across the whole grade.
    assert result["fields"]["evidence"]["agreed"] is True


def test_a_moved_overall_is_caught_even_when_every_axis_held(case):
    """`overall` is the judge's own field, not a function of the five axes.

    ! `grader.py` refuses to compute an overall from the axes, so the two can
    move independently and the comparison has to watch both.
    """
    result = reread.reread(
        **case, runs=2, client=_Judge(_judged(overall="B"), _judged(overall="C"))
    )

    assert result["agreed"] is False
    assert result["fields"]["overall"]["letters"] == ["B", "C"]
    assert all(result["fields"][axis]["agreed"] for axis in grader.AXES)


def test_the_letters_are_recorded_in_run_order(case):
    """T50 asks for them side by side, which a set would destroy."""
    result = reread.reread(
        **case,
        runs=3,
        client=_Judge(
            _judged(detection="A"), _judged(detection="F"), _judged(detection="A")
        ),
    )

    assert result["fields"]["detection"]["letters"] == ["A", "F", "A"]
    assert result["runs"] == 3
    assert len(result["readings"]) == 3


def test_every_reading_is_handed_the_same_prompt(case):
    """The only thing allowed to vary between runs is the model's sampling.

    ! IF THE PROMPTS DIFFERED, a disagreement would be evidence about the
    harness rather than about the judge, and T50 would measure nothing.
    """
    judge = _Judge(_judged(), _judged(), _judged())
    reread.reread(**case, runs=3, client=judge)

    assert len(judge.prompts) == 3
    assert len(set(judge.prompts)) == 1


def test_the_full_grade_is_kept_not_just_the_letters(case):
    """`Process: #56`: the reason is the data, so a letter alone is not enough."""
    result = reread.reread(**case, runs=2, client=_Judge(_judged(), _judged()))

    first = result["readings"][0]
    assert first["editorial"]["overall_reason"] == "because"
    assert first["editorial"]["model"] == grader.MODEL
    assert first["editorial"]["rubric_version"] == grader.RUBRIC_VERSION
    assert first["summary"]["total"] == 2


def test_the_comparison_carries_what_makes_two_grades_comparable(case):
    """A stability figure under an unnamed rubric or model cannot be reused."""
    result = reread.reread(**case, runs=2, client=_Judge(_judged(), _judged()))

    assert result["model"] == grader.MODEL
    assert result["rubric_version"] == grader.RUBRIC_VERSION
    assert result["eval_id"] == "a-case"
    assert result["arm"] == "with_skill"


def test_one_run_is_refused_because_it_compares_nothing(case):
    with pytest.raises(reread.NotAComparison):
        reread.reread(**case, runs=1, client=_Judge(_judged()))


def test_a_run_count_too_low_is_refused_BEFORE_the_judge_is_called(case):
    """`compare` would catch this too, and one call later -- which costs money.

    ! THE TWO GUARDS ARE NOT REDUNDANT. Without the one in `reread`, `runs=1`
    makes a paid request and only then discovers it has nothing to compare it
    to. This asserts the refusal is free.
    """
    judge = _Judge(_judged())

    with pytest.raises(reread.NotAComparison):
        reread.reread(**case, runs=1, client=judge)

    assert judge.prompts == []


def test_compare_refuses_a_single_reading():
    with pytest.raises(reread.NotAComparison):
        reread.compare([_judged()])


def test_a_missing_credential_propagates_rather_than_reporting_agreement(case):
    """A comparison over the calls that happened to succeed is not a measurement."""
    with pytest.raises(grader.NoCredential):
        reread.reread(**case, runs=2, client=_Keyless())


@pytest.mark.parametrize(
    "message", [NO_WORKSPACE_SENT, BAD_WORKSPACE_SENT], ids=["none-sent", "bad-value"]
)
def test_either_workspace_400_is_a_setup_problem_not_a_traceback(case, message):
    """BOTH shapes, because matching the first sentence caught only one.

    ! The `bad-value` case reached Roy as a raw traceback on 2026-08-29, after
    the translation for `none-sent` had already landed -- so this is
    parametrised rather than written once.
    """
    with pytest.raises(grader.NoWorkspace) as refused:
        reread.reread(**case, runs=2, client=_rejects(message))

    assert grader.WORKSPACE_ENV in str(refused.value)


def test_the_refusal_says_WHICH_of_the_two_workspace_faults_it_is(case, monkeypatch):
    """The fix differs: supply a value, versus replace the one already set."""
    monkeypatch.delenv(grader.WORKSPACE_ENV, raising=False)
    with pytest.raises(grader.NoWorkspace) as unset:
        reread.reread(**case, runs=2, client=_rejects(NO_WORKSPACE_SENT))
    assert "is not set" in str(unset.value)

    monkeypatch.setenv(grader.WORKSPACE_ENV, "default")
    with pytest.raises(grader.NoWorkspace) as bad:
        reread.reread(**case, runs=2, client=_rejects(BAD_WORKSPACE_SENT))
    said = str(bad.value)
    assert "'default'" in said
    assert "rejected" in said


def test_the_refusal_records_that_default_does_not_work(case):
    """MEASURED 2026-08-29, and the next person will otherwise try it too."""
    with pytest.raises(grader.NoWorkspace) as refused:
        reread.reread(**case, runs=2, client=_rejects(BAD_WORKSPACE_SENT))

    assert '"default" is NOT accepted' in str(refused.value)


def test_both_setup_problems_share_one_base_so_a_caller_catches_once(case):
    """Catching only `NoCredential` is what let the workspace 400 escape."""
    assert issubclass(grader.NoCredential, grader.SetupProblem)
    assert issubclass(grader.NoWorkspace, grader.SetupProblem)

    with pytest.raises(grader.SetupProblem):
        reread.reread(**case, runs=2, client=_rejects(BAD_WORKSPACE_SENT))
    with pytest.raises(grader.SetupProblem):
        reread.reread(**case, runs=2, client=_Keyless())


def test_an_empty_account_is_a_setup_problem_not_a_traceback(case):
    """The third gate, and the third to reach Roy as a traceback first."""
    with pytest.raises(grader.NoCredit) as refused:
        reread.reread(**case, runs=2, client=_rejects(NO_CREDIT))

    said = str(refused.value)
    assert "Plans & Billing" in said
    # ! It says grading is metered, because the next thing anyone does after
    # topping up is choose a run count.
    assert "billed" in said


def test_all_three_setup_gates_share_the_base(case):
    """One `except` covers the sequence, whichever gate a machine stops at."""
    for client in (
        _Keyless(),
        _rejects(BAD_WORKSPACE_SENT),
        _rejects(NO_CREDIT),
    ):
        with pytest.raises(grader.SetupProblem):
            reread.reread(**case, runs=2, client=client)


@pytest.mark.parametrize(
    "message",
    ["Error code: 500 - overloaded", f"Error code: 400 - {OUR_OWN_BUG}"],
    ids=["server-error", "our-own-malformed-request"],
)
def test_an_unnamed_failure_keeps_its_traceback(case, message):
    """Only named signatures are translated; the rest must not be hidden.

    ! THE SECOND CASE IS THE ONE THAT MATTERS. A 400 caused by a bug in the
    request THIS FILE builds is indistinguishable, to a reader, from a 400
    about the account -- unless one of them keeps its traceback.
    """

    class _Broken:
        class messages:  # noqa: N801
            @staticmethod
            def stream(**_):
                raise RuntimeError(message)

    with pytest.raises(RuntimeError) as raised:
        reread.reread(**case, runs=2, client=_Broken())

    assert not isinstance(raised.value, grader.SetupProblem)


def test_the_translation_keeps_the_original_error_chained(case):
    """A friendlier message must not cost the cause it replaced."""
    with pytest.raises(grader.NoCredit) as refused:
        reread.reread(**case, runs=2, client=_rejects(NO_CREDIT))

    assert refused.value.__cause__ is not None
    assert "credit balance is too low" in str(refused.value.__cause__)


# --- What the first live run cost, and the two defects it bought -----------


def _na(**over):
    """A judge answer with the keyed axes ungradeable, as a keyless case gets."""
    j = _judged(**over)
    for axis in reread.KEYED_AXES:
        j["axes"][axis] = {"grade": "N/A", "reason": "no key was supplied"}
    return j


def test_an_axis_ungraded_in_every_reading_is_NOT_counted_as_agreement(case):
    """MEASURED 2026-08-29: three N/A fields read as agreement and outvoted two
    real disagreements, so the run reported stability it had not observed."""
    result = reread.reread(
        **case, runs=2, client=_Judge(_na(overall="B"), _na(overall="B"))
    )

    for axis in reread.KEYED_AXES:
        assert result["fields"][axis]["measured"] is False
        # ! `None`, never `True` -- a boolean here reads as a verdict.
        assert result["fields"][axis]["agreed"] is None


def test_the_verdict_carries_how_many_fields_it_was_drawn_from(case):
    """`agreed` alone cannot be read without its denominator."""
    result = reread.reread(
        **case, runs=2, client=_Judge(_na(overall="B"), _na(overall="B"))
    )

    assert result["of"] == len(reread.COMPARED)
    assert result["measured"] == len(reread.COMPARED) - len(reread.KEYED_AXES)


def test_a_vacuous_field_cannot_outvote_a_real_disagreement(case):
    """The exact shape of the first live run: three N/A, one axis moved."""
    result = reread.reread(
        **case,
        runs=2,
        client=_Judge(_na(overall="B"), _na(overall="B", evidence="A")),
    )

    assert result["agreed"] is False
    assert result["measured"] == 3


def test_N_A_against_a_letter_is_a_disagreement_not_an_absence(case):
    """The readings then differ on whether the axis was gradeable at all."""
    result = reread.reread(**case, runs=2, client=_Judge(_na(), _judged()))

    detection = result["fields"]["detection"]
    assert detection["measured"] is True
    assert detection["agreed"] is False


def test_a_case_with_no_answer_key_is_REFUSED_before_it_is_paid_for(
    tmp_path, case, capsys
):
    """MEASURED: the first live T50 spent $0.61 to grade three axes N/A.

    ! THE HELPER IS NOT USED HERE, because it supplies `--allow-no-end` -- and
    the absence of that flag is the whole subject of this test.
    """
    code = reread.main(
        [
            "--findings",
            str(case["findings"]),
            "--under-review",
            str(case["under_review"]),
            "--start",
            "aaaa",
            "--arm",
            "with_skill",
            "--eval-id",
            "a-case",
            "--out",
            str(tmp_path / "o.json"),
        ]
    )

    assert code == 1
    named = _refusals(capsys)
    assert any("--end" in r for r in named)
    assert any("detection" in r and "N/A" in r for r in named)
    # ! The price is in the refusal, because that is what makes it a decision
    # rather than an obstacle.
    assert any("$" in r for r in named)


def test_allow_no_end_makes_the_keyless_run_deliberate(
    tmp_path, case, capsys, monkeypatch
):
    """T50 legitimately runs on an unkeyed case -- once chosen knowingly.

    !! `_client` IS SUBSTITUTED AND THAT IS NOT OPTIONAL. `main` takes no
    client, so without this the test calls the real API -- passing for free on
    a machine with no credential and BILLING one that has it, every time the
    suite runs. It was written that way first, on 2026-08-29, hours after this
    file's own docstring said not to.
    """
    judge = _Judge(_na(overall="B"), _na(overall="B"))
    monkeypatch.setattr(grader, "_client", lambda: judge)

    out = tmp_path / "o.json"
    code = reread.main(_argv(case, out))
    capsys.readouterr()

    assert code == 0
    assert len(judge.prompts) == 2
    written = json.loads(out.read_text(encoding="utf-8"))
    assert written["measured"] == 3


def test_the_conftest_guard_against_a_billed_test_can_itself_fire(case):
    """`conftest._no_live_api` is the mechanical form of "no test bills".

    ! PROVED ABLE TO FAIL, per `docs/gates.md`: a guard nothing demonstrates
    firing is indistinguishable from one that never fires. Reaching `reread`
    with no `client` is exactly what a forgetful test does.
    """
    with pytest.raises(AssertionError, match="billed API call"):
        reread.reread(**case, runs=2)


# --- What a billed failure must not do -------------------------------------
#
# !! EVERY ONE OF THESE COST MONEY WHEN IT HAPPENED. MEASURED 2026-08-29: a
# `--runs 5` hit the ceiling on a 43KB artifact, surfaced as
# `JSONDecodeError: Unterminated string ... char 11047`, and wrote NOTHING --
# so every reading already paid for was discarded with it.


def test_hitting_the_ceiling_is_reported_as_truncation_not_a_JSON_error(case):
    """`stop_reason` is the API saying so, and it is checked BEFORE the parse."""
    with pytest.raises(grader.Truncated) as lost:
        reread.reread(**case, runs=2, client=_Ceiling())

    said = str(lost.value)
    assert "max_tokens" in said
    assert "billed" in said
    # ! It must not surface as the parse error the truncation happens to cause.
    assert not isinstance(lost.value, json.JSONDecodeError)


def test_a_refusal_does_not_surface_as_StopIteration(case):
    """A declined answer may carry NO text block, and `next()` would raise."""
    with pytest.raises(grader.Malformed) as lost:
        reread.reread(**case, runs=2, client=_Refuses())

    assert "declined" in str(lost.value)
    assert "cyber" in str(lost.value)


def test_valid_prose_that_is_not_JSON_is_told_apart_from_truncation(case):
    """The fix differs: one needs a smaller artifact, the other is a shape bug."""
    with pytest.raises(grader.Malformed) as lost:
        reread.reread(**case, runs=2, client=_Garbage())

    said = str(lost.value)
    assert "not valid JSON" in said
    assert "shape problem, not a length one" in said


def test_every_billed_failure_is_a_Spent_so_one_except_catches_it(case):
    for client in (_Ceiling(), _Refuses(), _Garbage()):
        with pytest.raises(grader.Spent):
            reread.reread(**case, runs=2, client=client)


def test_a_billed_failure_is_NOT_a_setup_problem(case):
    """They need different exit codes: one is free to retry, one is not."""
    with pytest.raises(grader.Spent) as lost:
        reread.reread(**case, runs=2, client=_Ceiling())

    assert not isinstance(lost.value, grader.SetupProblem)


def test_readings_already_paid_for_are_KEPT_when_a_later_one_fails(case, tmp_path):
    """THE fix for what the ceiling cost: a failure loses one reading, not all.

    ! The judge answers twice and then hits the ceiling, so two readings were
    bought before the third failed. Both must be on disk afterwards.
    """
    keep = tmp_path / "readings"

    class _ThenCeiling:
        """Two good answers, then a truncation."""

        def __init__(self):
            self.calls = 0
            outer = self

            class messages:  # noqa: N801
                @staticmethod
                def stream(**_):
                    outer.calls += 1
                    if outer.calls <= 2:
                        return _Stream(lambda: _message(json.dumps(_judged())))
                    return _Stream(lambda: _message("{trunc", stop_reason="max_tokens"))

            self.messages = messages

    with pytest.raises(grader.Truncated):
        reread.reread(**case, runs=5, client=_ThenCeiling(), keep=keep)

    kept = sorted(keep.glob("reading-*.json"))
    assert [p.name for p in kept] == ["reading-1.json", "reading-2.json"]
    # ! They are whole gradings, not fragments -- a later run can read them.
    first = json.loads(kept[0].read_text(encoding="utf-8"))
    assert first["editorial"]["model"] == grader.MODEL


def test_nothing_is_kept_when_the_very_first_reading_fails(case, tmp_path):
    keep = tmp_path / "readings"

    with pytest.raises(grader.Truncated):
        reread.reread(**case, runs=3, client=_Ceiling(), keep=keep)

    assert not list(keep.glob("reading-*.json")) if keep.exists() else True


def test_each_reading_records_what_it_cost(case):
    """Raising the cap to the ceiling unbounds the spend, so it is OBSERVED.

    ! The cap used to bound the bill as a side effect. At the model's ceiling
    it no longer does, and the only way to choose the next `--runs` honestly is
    to know what the last reading actually cost.
    """
    result = reread.reread(**case, runs=2, client=_Judge(_judged(), _judged()))

    for reading in result["readings"]:
        assert reading["usage"]["input_tokens"] == 1000
        assert reading["usage"]["output_tokens"] == 2500


def test_usage_sits_beside_the_grade_not_inside_it(case):
    """A token count is a fact about the request, never part of the judgement."""
    result = reread.reread(**case, runs=2, client=_Judge(_judged(), _judged()))

    editorial = result["readings"][0]["editorial"]
    assert "usage" not in editorial
    assert "input_tokens" not in json.dumps(editorial)


def test_a_response_with_no_usage_does_not_crash_the_run(case):
    """The field is read defensively -- a missing count must not lose a grade."""

    class _NoUsage:
        class messages:  # noqa: N801
            @staticmethod
            def stream(**_):
                return _Stream(lambda: _message(json.dumps(_judged()), usage=False))

    result = reread.reread(**case, runs=2, client=_NoUsage())

    assert result["readings"][0]["usage"] == {
        "input_tokens": None,
        "output_tokens": None,
    }


def test_the_ceiling_is_the_models_maximum_so_it_is_not_a_guess():
    """`max_tokens` is REQUIRED by the API; the only choice is which number.

    ! 128,000 is `claude-opus-5`'s documented maximum output. Any smaller
    default is a bet on the shape of an answer nobody has seen yet, which is
    the bet that was lost at 16,000.
    """
    assert grader.MAX_TOKENS == 128000


def test_setup_problem_returns_None_for_anything_it_does_not_name():
    """The seam the `raise` decision turns on, tested directly."""
    assert grader.setup_problem("Error code: 500 - overloaded") is None
    assert grader.setup_problem("") is None
    assert isinstance(grader.setup_problem(NO_CREDIT), grader.NoCredit)


def test_reader_value_carries_no_letter_and_is_not_compared():
    """It is recorded and not graded, so it has no grade to disagree about."""
    assert "reader_value" not in reread.COMPARED
    assert "unkeyed_claims" not in reread.COMPARED
    assert set(reread.COMPARED) == {*grader.AXES, "overall"}


def test_nothing_averages_the_letters(case):
    """`grader.py` has no `aggregate()` deliberately; neither has this.

    ! A mean over A=4, B=3, C=2 asserts the A-to-B distance equals the B-to-C
    distance, which nothing establishes. Equality is the only operation these
    letters support, so no numeric summary of them may appear in the artifact.
    """
    result = reread.reread(
        **case, runs=2, client=_Judge(_judged(overall="A"), _judged(overall="F"))
    )

    for field in result["fields"].values():
        assert set(field) == {"letters", "measured", "agreed"}
        assert all(isinstance(v, str) for v in field["letters"])
    assert "mean" not in json.dumps(result["fields"])


def test_main_refuses_to_overwrite_an_existing_comparison(tmp_path, case):
    """Refused BEFORE the calls: discovering it after N requests wastes money."""
    out = tmp_path / "taken.json"
    out.write_text("{}", encoding="utf-8")

    code = reread.main(
        [
            "--findings",
            str(case["findings"]),
            "--under-review",
            str(case["under_review"]),
            "--start",
            "aaaa",
            "--arm",
            "with_skill",
            "--eval-id",
            "a-case",
            "--out",
            str(out),
        ]
    )

    assert code == 1
    assert out.read_text(encoding="utf-8") == "{}"


# --- What broke, said explicitly -------------------------------------------
#
# ! EVERY ONE OF THESE ASSERTS THE FLAG IS NAMED, not merely that the run
# failed. A refusal that says only "no such file" leaves the caller matching a
# path against their own command line -- which is the failure that sent a
# placeholder path into a real invocation on 2026-08-29.


def _argv(case, out, **over):
    """A valid command line, always carrying `--allow-no-end`.

    ! THESE CASES HAVE NO KEY, so without the flag the no-end guard refuses
    every one of them before the thing under test is reached. A test OF the
    guard builds its argv without this helper.
    """
    argv = {
        "--findings": str(case["findings"]),
        "--under-review": str(case["under_review"]),
        "--start": "aaaa",
        "--arm": "with_skill",
        "--eval-id": "a-case",
        "--out": str(out),
        **over,
    }
    return [str(x) for pair in argv.items() for x in pair] + ["--allow-no-end"]


def _refusals(capsys):
    err = capsys.readouterr().err
    return [ln for ln in err.splitlines() if ln.startswith("REFUSED")]


def test_a_missing_findings_file_names_the_flag(tmp_path, case, capsys):
    code = reread.main(
        _argv(case, tmp_path / "o.json", **{"--findings": tmp_path / "nope.md"})
    )

    assert code == 1
    assert any("--findings" in r and "no such file" in r for r in _refusals(capsys))


def test_a_missing_under_review_file_names_the_flag(tmp_path, case, capsys):
    code = reread.main(
        _argv(case, tmp_path / "o.json", **{"--under-review": tmp_path / "gone.py"})
    )

    assert code == 1
    assert any("--under-review" in r and "no such file" in r for r in _refusals(capsys))


def test_a_directory_handed_to_a_file_flag_says_so(tmp_path, case, capsys):
    """`no such file` would be a lie, and the caller would look for a typo."""
    code = reread.main(_argv(case, tmp_path / "o.json", **{"--findings": tmp_path}))

    assert code == 1
    assert any("--findings" in r and "is a directory" in r for r in _refusals(capsys))


def test_malformed_mechanical_json_reports_the_line_and_column(tmp_path, case, capsys):
    bad = tmp_path / "mech.json"
    bad.write_text('{"citations_checked": 2,\n  "oops"\n}', encoding="utf-8")

    code = reread.main(_argv(case, tmp_path / "o.json", **{"--mechanical": bad}))

    assert code == 1
    named = _refusals(capsys)
    assert any("--mechanical" in r and "not valid JSON" in r for r in named)
    assert any("line 3" in r for r in named)


def test_mechanical_holding_a_list_is_refused_before_the_calls(tmp_path, case, capsys):
    """`to_grading_json` calls `.get` on it, so a list fails AFTER paying."""
    listy = tmp_path / "mech.json"
    listy.write_text("[1, 2]", encoding="utf-8")

    code = reread.main(_argv(case, tmp_path / "o.json", **{"--mechanical": listy}))

    assert code == 1
    assert any("--mechanical" in r and "list" in r for r in _refusals(capsys))


def test_a_run_count_below_two_is_refused_by_the_CLI_not_a_traceback(
    tmp_path, case, capsys
):
    """It reached `NotAComparison` uncaught until 2026-08-29 -- a raw traceback."""
    code = reread.main(_argv(case, tmp_path / "o.json", **{"--runs": 1}))

    assert code == 1
    assert any("--runs=1" in r for r in _refusals(capsys))


def test_every_fault_is_reported_in_one_pass(tmp_path, case, capsys):
    """Three mistakes must not be three edit-and-retry cycles."""
    code = reread.main(
        _argv(
            case,
            tmp_path / "o.json",
            **{
                "--findings": tmp_path / "a.md",
                "--under-review": tmp_path / "b.py",
                "--runs": 0,
            },
        )
    )

    assert code == 1
    named = _refusals(capsys)
    assert {"--findings", "--under-review", "--runs=0"} <= {
        r.split(":")[0].removeprefix("REFUSED  ") for r in named
    }


def test_a_bad_argument_and_a_missing_credential_exit_differently(
    tmp_path, case, capsys, monkeypatch
):
    """One means the command was wrong; the other means the machine is not set up.

    ! THE CLIENT IS SUBSTITUTED so this never reaches the API. `main` takes no
    `client`, so the seam is `grader._client` -- which is what `reread` calls
    when none is injected.
    """
    monkeypatch.setattr(grader, "_client", lambda: _Keyless())

    bad_argument = reread.main(
        _argv(case, tmp_path / "a.json", **{"--findings": tmp_path / "x.md"})
    )
    capsys.readouterr()
    no_credential = reread.main(_argv(case, tmp_path / "b.json"))
    err = capsys.readouterr().err

    assert bad_argument == 1
    assert no_credential == 2
    # ! THE KIND IS NAMED, so the two setup problems are told apart in the
    # output and not only by the shared exit code.
    assert "NoCredential" in err


def test_nothing_is_written_when_an_argument_is_refused(tmp_path, case, capsys):
    out = tmp_path / "sub" / "o.json"

    code = reread.main(_argv(case, out, **{"--runs": 1}))
    capsys.readouterr()

    assert code == 1
    assert not out.exists()
