"""The `compositor` command: its argument parsing and its exit code.

The flow acquires and sets each source; this command presents its comparisons.

!! A MODULE DOES ONE JOB AND HAS NO CLI; A FLOW CALLS MODULES;
A COMMAND EXPOSES A FLOW. Ruled 2026-08-24 -- `decision-log.md Process: #12`.
"""

import argparse
from pathlib import Path

from comment_review.flows.compositor import round_trip
from comment_review.flows.read_diagnostics import format_failure
from comment_review.flows.reading_context import load_settings
from comment_review.reading.diagnostics import ReadFailure
from comment_review.results.compositor import identity, lossless


def main(argv: list[str] | None = None) -> int:
    """Compare each round trip; fail on refusals or lost or invented lines."""
    parser = argparse.ArgumentParser(description="Set a page as text.")
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--reading-settings", type=Path, metavar="FILE")
    args = parser.parse_args(argv)
    settings = {}
    if args.reading_settings is not None:
        settings, problems = load_settings(args.reading_settings, args.repo)
        if problems:
            for problem in problems:
                print(problem)
            return 2
    same = moved = broken = 0
    for path in args.paths:
        result = round_trip(path, settings=settings.get(path.resolve(), {}))
        if isinstance(result, ReadFailure):
            broken += 1
            print(f"  LOSSY   {format_failure(result, path=path.as_posix())}")
            continue
        gone = lossless(result.original, result.rendered)
        if gone is not None:
            broken += 1
            print(f"  LOSSY   {path} -- {gone}")
            continue
        why = identity(result.original, result.rendered)
        if why is None:
            same += 1
            print(f"  set     {path}")
        else:
            moved += 1
            print(f"  moved   {path} -- {why}")
    print(f"\n{same} identical, {moved} normalised, {broken} LOSSY")
    # Read or rendering refusals and lost or invented lines fail. A byte
    # difference retaining every line is reported as successful normalisation.
    return 1 if broken else 0
