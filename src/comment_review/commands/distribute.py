"""The `distribute` command: its argument parsing and its exit code.

    comment_review distribute --shape
    comment_review distribute --seed --binder B.json --role block-context --out F.json

The work is `flows.distribute` and `desk.mark`; this is only the console face of it.

!! A MODULE DOES ONE JOB AND HAS NO CLI; A FLOW CALLS MODULES;
A COMMAND EXPOSES A FLOW. `decision-log.md Process: #12`.

!! `--check` LEFT 2026-08-30 AND IS `collate`'s FIRST ACT. `desk.collator.places`
already raises on an entry `parse` refuses, so a malformed copy could never be
folded; what a separate command added was the chance to fold WITHOUT EVER HAVING
RUN THE CHECK. ! The cost: a role can no longer validate its own returned copy
alone -- the whole stage's copies must be in hand. No caller does that today.
"""

import argparse
import json
import sys
from pathlib import Path

from comment_review.binder.binder import Binder
from comment_review.desk.mark import allowed
from comment_review.desk.stages import ROLES
from comment_review.flows.distribute import seed
from comment_review.machine import exceptions
from comment_review.machine.json_object import object_of


def main() -> int:
    """Publish the shape, or seed an `edit_copy`.

    Returns:
        0 when the shape printed or the edit_copy was written; 2 when an
        input could not be read.
    """
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--shape", action="store_true", help="print what a mark may carry, as JSON"
    )
    ap.add_argument("--seed", action="store_true", help="write a fillable edit_copy")
    ap.add_argument("--binder", help="the binder to seed from (--seed only)")
    # `choices=` takes the string values, not the `Role` members themselves:
    # argparse's "invalid choice" message reprs each choice, and a `StrEnum`
    # member's repr is `<Role.OWNERSHIP_CONTEXT: 'ownership-context'>` rather
    # than the plain name a user typed.
    ap.add_argument(
        "--role",
        choices=[str(role) for role in ROLES],
        help="the editorial role (--seed only)",
    )
    ap.add_argument("--out", help="the file to write (--seed only)")
    args = ap.parse_args()

    if args.shape:
        print(json.dumps(allowed(), indent=2))
        return 0

    if args.seed:
        # ! Every one is required together: an edit_copy with no role cannot be
        # collated, and one with no address cannot be filled -- which is the
        # whole reason it is seeded rather than described.
        missing = [n for n in ("binder", "role", "out") if not getattr(args, n)]
        if missing:
            wanted = ", ".join("--" + n for n in missing)
            print(f"--seed needs {wanted}", file=sys.stderr)
            return 2
        try:
            text = Path(args.binder).read_text(encoding="utf-8")
        except exceptions.READ_ERRORS as err:
            print(f"cannot read {args.binder}: {err}", file=sys.stderr)
            return 2
        # !! THE LOAD IS THE FLOW'S, THE DESERIALIZE THE CONTAINER'S --
        # `decision-log.md Process: #67`.
        loaded, problem = object_of(text, "binder")
        if problem:
            print(problem, file=sys.stderr)
            return 2
        binder, problems = Binder.deserialize(args.binder, loaded)
        if binder is None:
            for line in problems:
                print(line, file=sys.stderr)
            return 2
        edit_copy = seed(binder, args.role)
        Path(args.out).write_text(
            json.dumps(edit_copy, indent=2), encoding="utf-8", newline=""
        )
        places = sum(len(sheet["marks"]) for sheet in edit_copy["sheets"])
        print(f"{args.out}: {places} places for {args.role} to rule on")
        return 0

    ap.print_usage()
    return 2
