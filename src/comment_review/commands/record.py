"""The `record` command: its argument parsing and its exit code.

The work is `binder.record`; this is only the console face of it.

!! A LIBRARY MODULE DOES ONE JOB AND HAS NO CLI; A FLOW CALLS LIBRARIES;
A COMMAND EXPOSES A FLOW. Ruled 2026-08-24 -- `decision-log.md Process: #12`.
"""

import argparse
import json
from pathlib import Path

from comment_review.binder.binder import read as read_binder
from comment_review.binder.binder import rows_of
from comment_review.binder.record import (
    ANSWERED,
    SEEDED,
    check,
    every_record,
    seed,
    version_problem,
)
from comment_review.machine import exceptions


def main() -> int:
    """Seed a reviewer's record file from the census."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seed", action="store_true", help="write an empty record file")
    ap.add_argument("--check", metavar="PATH", help="check a filled record file")
    ap.add_argument("--census", required=True, help="census.py --json output")
    ap.add_argument("--reviewer", help="the editorial role's name (--seed only)")
    ap.add_argument("--out", help="the file to write (--seed only)")
    args = ap.parse_args()

    if not args.seed and not args.check:
        print("nothing to do: pass --seed or --check")
        return 2
    try:
        census_text = Path(args.census).read_text(encoding="utf-8")
    except exceptions.READ_ERRORS as e:
        print(f"CANNOT READ {args.census} ({type(e).__name__})")
        return 2
    # ! REFUSED BY NAME. A binder this cannot read would otherwise seed a report
    # with NO slots, which reads downstream as a page with nothing to rule on.
    loaded, why = read_binder(census_text)
    if why:
        print(f"CANNOT USE {args.census}: {why}")
        return 2
    census = rows_of(loaded)

    if args.check:
        try:
            report = json.loads(Path(args.check).read_text(encoding="utf-8"))
        except exceptions.READ_ERRORS as e:
            print(f"CANNOT READ {args.check} ({type(e).__name__})")
            return 2
        except json.JSONDecodeError as e:
            # !! THE ONE FAILURE THIS FORMAT ADDS, and it names its own
            # position where a merged field never could.
            print(f"CANNOT PARSE {args.check} as JSON ({e})")
            return 2
        problems, unruled = check(report, census)
        # ! The version first, because every message below it assumes this
        # reader and that file agree about what a record is.
        stale = version_problem(report)
        if stale:
            print(f"  {stale}")
        for problem in problems:
            print(f"  {problem}")
        total = sum(1 for _ in every_record(report))
        print(f"\n{total - unruled} of {total} records ruled; {unruled} still empty.")
        # ! The VERSION counts as one. It is reported above and it is not in
        # `problems`, so a file whose only fault was a missing version printed
        # "0 problem(s)" and exited 1 -- a count contradicting the line above it
        # and the exit code below it.
        counted = len(problems) + bool(stale)
        if counted:
            print(f"{counted} problem(s). The shape is wrong, not the finding.")
            return 1
        # ! An unfilled report is INCOMPLETE, not malformed, and the two exit
        # differently: a reviewer part-way through is not in error.
        print("Every filled record is well formed." if total else "No records.")
        return 0

    if not args.reviewer or not args.out:
        print("--seed needs --reviewer and --out")
        return 2
    report = seed(census, args.reviewer)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=1), encoding="utf-8")

    prose = sum(1 for _ in every_record(report))
    print(
        f"{args.reviewer}: {prose} records seeded"
        f" from {len(census)} paragraphs -> {out}"
    )
    print(f"  the reviewer fills {', '.join(ANSWERED)}")
    print(f"  {', '.join(SEEDED)} are already there")
    return 0
