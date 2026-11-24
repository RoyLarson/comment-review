"""The `distribute` command: its argument parsing and its exit code.

    comment_review distribute --shape
    comment_review distribute --seed --binder B.json --role block-context --out F.json

The work is `flows.distribute` and `desk.marks`; this is only the console face
of it. A stage's copies are seeded by `stage open`, from the jacket's row.

This command seeds and does not check. `collate` checks every copy before it
folds, so a malformed copy is never folded; the `check` command checks one
returned copy on its own, which is how a role validates its copy before handing
it back.
"""

import argparse
import json
import sys
from pathlib import Path

from comment_review.desk.marks.rules import allowed
from comment_review.desk.stages import ROLES
from comment_review.flows.distribute import IncompatibleBinder, admit_binder, seed
from comment_review.flows.proof_io import load_binder


def _as_json(payload: dict) -> str:
    """This command's one `json.dumps`, for every JSON it prints or writes.

    !! Two outputs, one spelling. `--shape` prints and `--seed` writes a
    file. Both are at the save end, which is where the
    rule allows raw json -- what the rule does not allow is one command holding
    two answers to *how does this command write JSON*, because that is where an
    indent or an encoding drifts apart between outputs nobody compares.
    """
    return json.dumps(payload, indent=2)


def main() -> int:
    """Publish the shape, or seed one `edit_copy`.

    Returns:
        0 when the shape printed or the copy was written; 2 when a required
        flag is missing, no mode was given, or the binder could not be read or
        was refused.
    """
    ap = argparse.ArgumentParser(description=__doc__)
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument(
        "--shape", action="store_true", help="print what a mark may carry, as JSON"
    )
    mode.add_argument("--seed", action="store_true", help="write a fillable edit_copy")
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
        print(_as_json(allowed()))
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
        binder, problems = load_binder(Path(args.binder))
        if binder is None:
            for line in problems:
                print(line, file=sys.stderr)
            return 2
        try:
            admit_binder(binder)
        except IncompatibleBinder as exc:
            print(str(exc), file=sys.stderr)
            return 2
        edit_copy = seed(binder, args.role)
        Path(args.out).write_text(_as_json(edit_copy), encoding="utf-8", newline="")
        places = sum(len(sheet["marks"]) for sheet in edit_copy["sheets"])
        print(
            f"{args.out}: {places} places for {args.role} to rule on; "
            f"{len(binder.freeform)} freeform"
        )
        return 0

    ap.print_usage()
    return 2
