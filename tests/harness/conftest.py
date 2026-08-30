"""Put `evals/` on the path for the harness tests, and cut the wire to the API.

The harness is not a shipped package and is not installed -- `evals/` is
`testing`'s tree and never leaves this repo -- so its modules are imported from
where they live rather than from the venv.
"""

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]

sys.path.insert(0, str(REPO / "evals"))


@pytest.fixture(autouse=True)
def _no_live_api(monkeypatch):
    """Fail any test that reaches the real SDK client, rather than billing for it.

    !! A TEST THAT CALLS THE API IS NOT A TEST, and this repo already said so
    before it had one: a run that reaches the network passes for free on a
    machine with no credential and quietly costs money on one that has it, so
    its behaviour depends on who runs it.

    ! MADE MECHANICAL BECAUSE THE RULE ALONE DID NOT HOLD. MEASURED 2026-08-29:
    a test driving `main` -- which takes no `client` -- was written with no
    substitution, hours after `test_reread.py`'s own docstring stated the rule.
    It passed here, on a machine with no key, and would have billed Roy's
    account on every suite run.

    ! IT ONLY BITES WHERE NOTHING WAS INJECTED. Every honest test passes
    `client=` explicitly, or patches this seam itself with its own stub; both
    reach their stub and never this. A test that hits this has forgotten.
    """
    import grader

    def _refuse():
        raise AssertionError(
            "This test reached grader._client(), which builds the REAL SDK "
            "client and would make a billed API call. Pass `client=<stub>` to "
            "`grade`/`reread`, or monkeypatch `grader._client` with one."
        )

    monkeypatch.setattr(grader, "_client", _refuse)
