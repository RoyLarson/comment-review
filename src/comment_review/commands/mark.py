"""The `mark` command: its argument parsing and its exit code.

    comment_review mark --shape
    comment_review mark --seed --binder B.json --role block-context --out F.json
    comment_review mark --check F.json

The work is `flows.marks` and `desk.mark`; this is only the console face of it.

!! A MODULE DOES ONE JOB AND HAS NO CLI; A FLOW CALLS MODULES;
A COMMAND EXPOSES A FLOW. `decision-log.md Process: #12`.
"""

import argparse
import json
import sys
from pathlib import Path

from comment_review.binder.binder import read as read_binder
from comment_review.desk.mark import allowed
from comment_review.desk.stages import STAGES
from comment_review.flows.marks import problems_in, seed, tally, unruled
from comment_review.machine import exceptions

#: The four editorial role names, in `STAGES`' own order -- `T1.16` of
#: `docs/plans/0.2.4-the-mark-and-the-collator.md`. Derived, not retyped:
#: `STAGES` is the one canonical list of role names in `src/`.
ROLES = tuple(role for stage in STAGES for role in stage.roles)


def _load(path: str) -> tuple[dict, str]:
    """Read one JSON object, or say why it could not be read."""
    try:
        text = Path(path).read_text(encoding="utf-8")
    except exceptions.READ_ERRORS as err:
        return {}, f"cannot read {path}: {err}"
    try:
        got = json.loads(text)
    except ValueError as err:
        return {}, f"{path} is not JSON: {err}"
    if not isinstance(got, dict):
        return {}, f"{path} is a JSON {type(got).__name__}, not an object"
    return got, ""


def main() -> int:
    """Publish the shape, seed a sheet, or check a filled one.

    Returns:
        0 when the shape printed, the sheet was written, or the file is sound;
        1 when a filled file breaks a rule; 2 when an input could not be read.
    """
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--shape", action="store_true", help="print what a mark may carry, as JSON"
    )
    ap.add_argument("--seed", action="store_true", help="write a fillable sheet")
    ap.add_argument("--check", metavar="PATH", help="check a filled sheet")
    ap.add_argument("--binder", help="the binder to seed from (--seed only)")
    ap.add_argument(
        "--role", choices=ROLES, help="the editorial role (--seed only)"
    )
    ap.add_argument("--out", help="the file to write (--seed only)")
    args = ap.parse_args()

    if args.shape:
        print(json.dumps(allowed(), indent=2))
        return 0

    if args.seed:
        # ! Every one is required together: a sheet with no role cannot be
        # collated, and one with no address cannot be filled -- which is the
        # whole reason it is seeded rather than described.
        missing = [n for n in ("binder", "role", "out") if not getattr(args, n)]
        if missing:
            wanted = ', '.join('--' + n for n in missing)
            print(f"--seed needs {wanted}", file=sys.stderr)
            return 2
        try:
            text = Path(args.binder).read_text(encoding="utf-8")
        except exceptions.READ_ERRORS as err:
            print(f"cannot read {args.binder}: {err}", file=sys.stderr)
            return 2
        binder, problem = read_binder(text)
        if problem:
            print(problem, file=sys.stderr)
            return 2
        sheet = seed(binder, args.role)
        Path(args.out).write_text(
            json.dumps(sheet, indent=2), encoding="utf-8", newline=""
        )
        print(f"{args.out}: {len(sheet['marks'])} places for {args.role} to rule on")
        return 0

    if args.check:
        report, why = _load(args.check)
        if why:
            print(why, file=sys.stderr)
            return 2
        broken, ruled = problems_in(report)
        for line in broken:
            print(line)
        left = unruled(report)
        counts = ", ".join(f"{n} {name}" for name, n in sorted(tally(report).items()))
        summary = f"{ruled} ruled on, {len(left)} left unruled"
        print(summary + (f" -- {counts}" if counts else ""))
        return 1 if broken else 0

    ap.print_usage()
    return 2
