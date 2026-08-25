"""The `run_context` command: its argument parsing and its exit code.

The work is `desk.run_context`; this is only the console face of it.

!! A LIBRARY MODULE DOES ONE JOB AND HAS NO CLI; A FLOW CALLS LIBRARIES;
A COMMAND EXPOSES A FLOW. Ruled 2026-08-24 -- `decision-log.md Process: #12`.
"""

import argparse
from contextlib import redirect_stdout
from pathlib import Path

from comment_review.desk.run_context import (
    HINTS,
    PATH_SECTIONS,
    REQUIRED,
    TASK_AGENT_ONLY,
    invalid_answers,
    missing_sections,
    template,
)
from comment_review.machine import exceptions


def main() -> int:
    """Print the template, or check a filled packet."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--template", action="store_true")
    ap.add_argument("--check", metavar="FILE")
    ap.add_argument(
        "--out", metavar="PATH", help="write the report to PATH, not stdout"
    )
    args = ap.parse_args()
    # ! REFUSED BEFORE `--out` OPENS ANYTHING, so a usage error leaves no empty
    # packet behind for the next stage to read as an answered one.
    if not args.template and not args.check:
        ap.error("one of --template or --check is required")

    # ! WRITES ITS OWN FILE, for the reason `census.py:276` carries: a
    # worktree-isolated harness REFUSES a command carrying a shell redirect,
    # and the packet is what stage 4 dispatches from -- so the only documented
    # route to it was unrunnable there. This module's own usage line said
    # `--template > run-<id>/context.md` until this landed.
    if args.out:
        with open(args.out, "w", encoding="utf-8", newline="") as fh:
            with redirect_stdout(fh):
                return _report(args)
    return _report(args)


def _report(args: argparse.Namespace) -> int:
    """Everything the run prints, so `--out` can wrap it in one place."""
    if args.template:
        print(template())
        return 0

    try:
        text = Path(args.check).read_text(encoding="utf-8")
    except exceptions.READ_ERRORS as e:
        print(f"CANNOT READ {args.check} ({type(e).__name__}) -- no packet to check")
        return 1

    bad = missing_sections(text)
    if bad:
        print(f"INCOMPLETE -- {len(bad)} section(s) would dispatch unanswered:")
        for name in bad:
            print(f"  {name}: {HINTS[name]}")
        print(
            "\nDo not dispatch. A reviewer cannot report a context it never received."
        )
        return 1

    invalid = invalid_answers(text)
    if invalid:
        print(f"UNUSABLE -- {len(invalid)} answer(s) a reviewer cannot act on:")
        for problem in invalid:
            print(f"  {problem}")
        print(
            "\nDo not dispatch. An answer that does not resolve is the same"
            " dispatch failure as a blank one, arriving later."
        )
        return 1

    # ! BOTH NUMBERS ARE DERIVED. The message named three sections and
    # subtracted three while FOUR were checked -- `LOOKUP CENSUS` joined them
    # and the sentence did not, so the line under-reported what it had
    # verified and over-reported what it had not.
    checked = ", ".join(PATH_SECTIONS)
    print(
        f"Complete: all {len(REQUIRED)} sections answered, and {checked}"
        f" check out.\n! The other {len(REQUIRED) - len(PATH_SECTIONS)} are"
        " prose nothing here can settle. Dispatch all four in ONE message, so no"
        " role sees another's findings.\n! Withhold every TASK AGENT ONLY"
        f" section: {', '.join(sorted(TASK_AGENT_ONLY))}."
    )
    return 0
