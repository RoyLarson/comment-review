"""A local stand-in for the Messages API, so the expensive path runs for free.

!! WHAT A STUB CLIENT CANNOT PROVE. `tests/harness/` injects an object with a
`messages.stream` attribute, which exercises everything EXCEPT the part that
costs money: whether the SDK accepts the request `grade` builds, whether
`output_config` survives serialisation, whether a real SSE stream assembles into
the object the ceiling and refusal checks read. A stub agrees with whatever shape
it was written against -- `docs/gates.md`'s subject, and the mechanism that got
the old suite deleted.

!! SO THE REDIRECT IS THE WHOLE POINT, AND IT NEEDS NO CODE CHANGE. `_client()`
builds a bare `anthropic.Anthropic()`, and the SDK reads `ANTHROPIC_BASE_URL`
from the environment -- so pointing the grader at this server changes nothing in
`grader.py`. **The code path under test is the shipped one, byte for byte.**

    uv run python evals/fake_api.py --port 8787 &
    ANTHROPIC_BASE_URL=http://127.0.0.1:8787 ANTHROPIC_API_KEY=not-a-real-key \
      uv run python evals/reread.py --findings ... --under-review ... --out ...

! THE FAILURES ARE THE REASON, NOT THE HAPPY PATH. Every scenario below is one
that has actually cost Roy money or a run: the ceiling took $0.49 on 2026-08-29,
and the credential, workspace and credit gates were each found by a live run
failing in front of him. A rehearsal that only proves success proves the cheap
half.

! `no-auth` IS NOT A SCENARIO, and cannot be: the SDK raises it client-side
before a request is made, so no server can produce it. `tests/harness/
test_grader.py` covers that one by injection, which is the right tool for it.
"""

from __future__ import annotations

import argparse
import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

#: A grading body the pipeline accepts, for a rehearsal that supplies no file.
DEFAULT_BODY = {
    "axes": {
        axis: {"grade": "B", "reason": f"rehearsal placeholder for {axis}"}
        for axis in ("detection", "diagnosis", "prescription", "unkeyed", "evidence")
    },
    "unkeyed_claims": [],
    "reader_value": "rehearsal placeholder.",
    "overall": "B",
    "overall_reason": "rehearsal placeholder.",
}

#: 400 bodies quoted from the errors that actually reached Roy, because
#: `grader.setup_problem` matches on the MESSAGE. A paraphrase here would let the
#: rehearsal pass while the real string went on being unrecognised.
FOUR_HUNDREDS = {
    "no-credit": "Your credit balance is too low to access the Anthropic API.",
    "no-workspace": (
        "anthropic-workspace-id is required for this request, or must be a valid "
        "workspace ID"
    ),
}

SCENARIOS = ("ok", "truncated", "refusal", "garbage", *FOUR_HUNDREDS)


def _sse(events: list[tuple[str, dict]]) -> bytes:
    """The wire format the SDK's stream reader consumes."""
    out = []
    for name, data in events:
        out.append(f"event: {name}\ndata: {json.dumps(data)}\n\n")
    return "".join(out).encode("utf-8")


def _stream_for(scenario: str, body: dict) -> bytes:
    """One scenario's whole SSE response.

    ! THE TEXT IS SENT AS ONE DELTA. Chunking it would exercise the SDK's
    reassembly, which the SDK's own tests own; what this file is for is that
    `grade` reads the assembled result correctly.
    """
    if scenario == "refusal":
        # ! NO TEXT BLOCK AT ALL, which is the case `grade` handles separately
        # because `next(...)` over the blocks would otherwise raise
        # `StopIteration` and say nothing about a refusal.
        return _sse(
            [
                ("message_start", {"type": "message_start", "message": _shell()}),
                (
                    "message_delta",
                    {
                        "type": "message_delta",
                        "delta": {"stop_reason": "refusal", "stop_sequence": None},
                        "usage": {"output_tokens": 12},
                    },
                ),
                ("message_stop", {"type": "message_stop"}),
            ]
        )

    if scenario == "truncated":
        text, stop = json.dumps(body)[: len(json.dumps(body)) // 2], "max_tokens"
    elif scenario == "garbage":
        text, stop = "I am afraid I cannot express this as JSON.", "end_turn"
    else:
        text, stop = json.dumps(body), "end_turn"

    return _sse(
        [
            ("message_start", {"type": "message_start", "message": _shell()}),
            (
                "content_block_start",
                {
                    "type": "content_block_start",
                    "index": 0,
                    "content_block": {"type": "text", "text": ""},
                },
            ),
            (
                "content_block_delta",
                {
                    "type": "content_block_delta",
                    "index": 0,
                    "delta": {"type": "text_delta", "text": text},
                },
            ),
            ("content_block_stop", {"type": "content_block_stop", "index": 0}),
            (
                "message_delta",
                {
                    "type": "message_delta",
                    "delta": {"stop_reason": stop, "stop_sequence": None},
                    "usage": {"output_tokens": 1400},
                },
            ),
            ("message_stop", {"type": "message_stop"}),
        ]
    )


def _shell() -> dict:
    """The message envelope every stream opens with."""
    return {
        "id": "msg_rehearsal",
        "type": "message",
        "role": "assistant",
        "model": "claude-opus-5",
        "content": [],
        "stop_reason": None,
        "stop_sequence": None,
        "usage": {"input_tokens": 62000, "output_tokens": 0},
    }


class Rehearsal(ThreadingHTTPServer):
    """The server, plus what it was asked -- which is half of what it is for.

    ! THE REQUESTS ARE KEPT so a caller can assert what the SDK actually SENT.
    That the prompt arrived, and that `output_config` survived the trip, are
    facts about the request no stub client can establish.
    """

    allow_reuse_address = True

    def __init__(self, address, scenario: str, body: dict):
        """Bind, and hold the scenario every request will be answered with."""
        super().__init__(address, _Handler)
        self.scenario = scenario
        self.body = body
        self.requests: list[dict] = []


class _Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    #: ! NARROWED FROM `BaseServer`, which knows none of the three attributes
    #: below. Without it a type checker calls every one of them unknown.
    server: Rehearsal

    def log_message(self, format, *args):  # noqa: A002 - the base's parameter name
        """Silent by default; the transcript is `server.requests`."""

    def do_POST(self):  # noqa: N802 - the name BaseHTTPRequestHandler dispatches on
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)
        try:
            sent = json.loads(raw)
        except json.JSONDecodeError:
            sent = {"unparsed": raw.decode("utf-8", "replace")}
        self.server.requests.append(
            {"path": self.path, "headers": dict(self.headers), "body": sent}
        )

        scenario = self.server.scenario
        if scenario in FOUR_HUNDREDS:
            payload = json.dumps(
                {"type": "error", "error": {"type": "invalid_request_error",
                                            "message": FOUR_HUNDREDS[scenario]}}
            ).encode("utf-8")
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        payload = _stream_for(scenario, self.server.body)
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def serve(scenario: str = "ok", body: dict | None = None, port: int = 0) -> Rehearsal:
    """Start the server on its own thread and return it. `port=0` picks a free one."""
    server = Rehearsal(("127.0.0.1", port), scenario, body or DEFAULT_BODY)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def main(argv: list[str] | None = None) -> int:
    """Run the rehearsal server until interrupted, and say how to point at it."""
    parser = argparse.ArgumentParser(
        description="A local stand-in for the Messages API, for rehearsing a grade."
    )
    parser.add_argument("--scenario", choices=SCENARIOS, default="ok")
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument(
        "--body-file",
        help="JSON the judge should return; omitted means a placeholder grade",
    )
    args = parser.parse_args(argv)

    # ! A Windows console is cp1252 and this prints a URL and a scenario name.
    # `evals/` cannot import the shipped package's `utf8_console`, so it spells
    # the same three lines itself, as `reread.py` and every script under
    # `scripts/` does. Gated by `tests/gates/test_shipped_cli_encoding.py`,
    # which is what caught this file missing them.
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="replace")

    body = DEFAULT_BODY
    if args.body_file:
        with open(args.body_file, encoding="utf-8") as f:
            body = json.load(f)

    server = serve(args.scenario, body, args.port)
    host, port = server.server_address[:2]
    print(f"rehearsal API on http://{host}:{port}  scenario={args.scenario}")
    print("point the grader at it, and NO REAL DOLLARS ARE SPENT:")
    print(f"  ANTHROPIC_BASE_URL=http://{host}:{port}")
    print("  ANTHROPIC_API_KEY=not-a-real-key")
    print("Ctrl-C to stop.")
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        print(f"\nserved {len(server.requests)} request(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
