"""The real SDK, over a real socket, driving the SHIPPED `grade()` for free.

!! THIS IS THE ONLY TEST IN THE TREE THAT BUILDS THE REAL CLIENT, and it is the
one class of fact the stubs cannot reach. `tests/harness/test_grader.py` injects
an object with a `messages.stream` attribute, which proves `grade` reads what it
is given; it cannot prove the SDK ACCEPTS the request `grade` builds, that
`output_config` survives serialisation, or that a genuine SSE stream assembles
into the object the ceiling and refusal checks read. A stub agrees with whatever
shape it was written against.

!! AND IT SPENDS NOTHING, WHICH IS NOT A HOPE BUT AN ASSERTION. Every test here
checks `server.requests` is non-empty -- the rehearsal server RECEIVED the call
-- so a run that somehow escaped to the real endpoint fails rather than bills. !
The key is the string `not-a-real-key`, so the worst reachable outcome if the
redirect failed is a 401.

! IT LIFTS `conftest.py`'s AUTOUSE GUARD DELIBERATELY, and is the only file that
may. That guard refuses `grader._client()` because a test reaching the API is not
a test; here the client is pointed at 127.0.0.1 by `ANTHROPIC_BASE_URL`, so what
it builds is the real SDK talking to a socket in this process. **The guard's
reason -- no billed call -- is preserved; only its mechanism is in the way.**
"""

import json
import pathlib
import sys

import fake_api
import grader
import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]

#: !! CAPTURED AT IMPORT, WHICH IS THE ONLY MOMENT IT IS STILL ITSELF.
#: `conftest.py`'s autouse guard replaces `grader._client` before every test --
#: and autouse fixtures run BEFORE the fixtures that request them, so reading the
#: attribute inside `rehearsal` below returns the guard, not the function.
#: MEASURED: doing exactly that made all nine socket tests fail with the guard's
#: own message, which is the guard working rather than a bug in it.
REAL_CLIENT = grader._client


@pytest.fixture
def rehearsal(monkeypatch):
    """Start the server, point the SDK at it, and put the genuine `_client` back."""

    def start(scenario="ok", body=None):
        server = fake_api.serve(scenario, body or fake_api.DEFAULT_BODY, port=0)
        host, port = server.server_address[:2]
        monkeypatch.setenv("ANTHROPIC_BASE_URL", f"http://{host}:{port}")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "not-a-real-key")
        monkeypatch.delenv("ANTHROPIC_WORKSPACE_ID", raising=False)
        # ! REBUILT PER TEST because the SDK reads the base URL when the client
        # is CONSTRUCTED, not when the request is made.
        monkeypatch.setattr(grader, "_client", REAL_CLIENT)
        return server

    yield start


@pytest.fixture
def artifacts(tmp_path):
    findings = tmp_path / "findings.md"
    findings.write_text("RECORD: one finding\n", encoding="utf-8")
    return findings, {"src/x.py": "pass\n"}


def _grade(findings, shown, **over):
    return grader.grade(
        findings=findings,
        under_review=shown,
        start="60257485",
        end="8bd26ad7",
        end_diff="diff --git a/src/x.py b/src/x.py\n",
        mechanical={"citations_checked": 5, "citations_failed": 1},
        arm="with_skill",
        eval_id="rehearsal",
        **over,
    )


def test_a_whole_grade_comes_back_over_a_real_socket(rehearsal, artifacts):
    """The expensive path, end to end, for nothing."""
    server = rehearsal("ok")
    findings, shown = artifacts

    out = _grade(findings, shown)

    assert server.requests, "the call did not reach the rehearsal server"
    assert out["editorial"]["overall"] in ("A", "B", "C", "D", "F")
    assert out["usage"]["input_tokens"] == 62000
    assert out["summary"]["pass_rate"] == pytest.approx(0.8)


def test_the_sdk_sends_the_request_grade_builds(rehearsal, artifacts):
    """What a stub cannot establish: that this survives serialisation.

    ! `output_config` IS THE ONE WORTH CHECKING. It is the newest parameter in
    the call and the one an SDK bump is most likely to reject or rename -- and a
    stub that records `kw` would go on passing either way.
    """
    server = rehearsal("ok")
    findings, shown = artifacts

    _grade(findings, shown)

    sent = server.requests[0]["body"]
    assert sent["model"] == "claude-opus-5"
    assert sent["max_tokens"] == 128000
    assert sent["stream"] is True, "the ceiling requires streaming"
    assert sent["output_config"]["effort"] == "high"
    assert sent["output_config"]["format"]["type"] == "json_schema"
    required = sent["output_config"]["format"]["schema"]["required"]
    assert "axes" in required and "overall" in required


def test_the_prompt_arrives_whole(rehearsal, artifacts):
    """The file set reaches the judge as text, not as a path the server cannot open."""
    server = rehearsal("ok")
    findings, _ = artifacts

    _grade(findings, {"src/a.py": "AAA_MARKER = 1\n", "src/b.py": "BBB_MARKER = 2\n"})

    prompt = server.requests[0]["body"]["messages"][0]["content"]
    assert "AAA_MARKER" in prompt and "BBB_MARKER" in prompt
    assert "`src/a.py`" in prompt and "`src/b.py`" in prompt


@pytest.mark.parametrize(
    "scenario,expected",
    [
        ("truncated", "Truncated"),
        ("refusal", "Malformed"),
        ("garbage", "Malformed"),
        ("no-credit", "NoCredit"),
        ("no-workspace", "NoWorkspace"),
    ],
)
def test_each_costly_failure_is_reproduced_and_named(
    rehearsal, artifacts, scenario, expected
):
    """Every one of these has cost Roy a run or a bill; each must still be told apart.

    ! THE CEILING IS THE MEASURED ONE: $0.49 on 2026-08-29, reported only as
    `JSONDecodeError: Unterminated string`. The three setup gates were each found
    by a live run failing in front of him, in the order they are reached.
    """
    server = rehearsal(scenario)
    findings, shown = artifacts

    with pytest.raises(Exception) as refused:
        _grade(findings, shown)

    assert server.requests, "the call did not reach the rehearsal server"
    assert type(refused.value).__name__ == expected


def test_a_billed_failure_and_a_setup_failure_stay_different_kinds(
    rehearsal, artifacts
):
    """`Spent` means the money is gone; `SetupProblem` means it never left."""
    findings, shown = artifacts

    server = rehearsal("truncated")
    with pytest.raises(grader.Spent):
        _grade(findings, shown)
    assert server.requests

    server = rehearsal("no-credit")
    with pytest.raises(grader.SetupProblem):
        _grade(findings, shown)
    assert server.requests


def test_the_rehearsal_is_not_a_stand_in_for_the_stubs():
    """The scenarios are the SERVER's, so the shipped module keeps no test hook.

    ! WHAT THIS GUARDS is the temptation to add a `--pretend` flag to `grader.py`
    itself. A module carrying its own fake is a module whose shipped path differs
    from the tested one; here the seam is an environment variable the SDK already
    reads, and `grader.py` has no idea it is being rehearsed.
    """
    source = (REPO / "evals" / "grader.py").read_text(encoding="utf-8")
    for hook in ("fake_api", "rehearsal", "ANTHROPIC_BASE_URL"):
        assert hook not in source, f"grader.py mentions {hook}"


def test_the_server_speaks_the_shape_it_claims_to():
    """A direct read of the wire, so a change to the SSE writer cannot pass silently."""
    wire = fake_api._stream_for("ok", fake_api.DEFAULT_BODY).decode("utf-8")

    for event in (
        "message_start",
        "content_block_start",
        "content_block_delta",
        "content_block_stop",
        "message_delta",
        "message_stop",
    ):
        assert f"event: {event}\n" in wire

    body = [
        json.loads(line[len("data: ") :])
        for line in wire.splitlines()
        if line.startswith("data: ")
    ]
    assert body[0]["message"]["usage"]["input_tokens"] == 62000
    assert body[-2]["delta"]["stop_reason"] == "end_turn"


def test_a_refusal_carries_no_text_block():
    """The case `grade` handles separately, because `next(...)` would raise instead."""
    wire = fake_api._stream_for("refusal", fake_api.DEFAULT_BODY).decode("utf-8")

    assert "content_block_start" not in wire
    assert "refusal" in wire


if __name__ == "__main__":
    sys.exit(pytest.main([__file__]))
