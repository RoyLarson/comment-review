"""The `vocabulary` command: its argument parsing and its exit code.

The work is `desk.vocabulary`; this is only the console face of it.

!! A LIBRARY MODULE DOES ONE JOB AND HAS NO CLI; A FLOW CALLS LIBRARIES;
A COMMAND EXPOSES A FLOW. Ruled 2026-08-24 -- `decision-log.md Process: #12`.
"""

import argparse
import sys

from comment_review.desk.vocabulary import VOCABULARY, Reviewer, load, render, terms_for
from comment_review.machine import exceptions


def main() -> int:
    """Print one role's vocabulary, or the roles that have one."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--reviewer", choices=[r.value for r in Reviewer])
    ap.add_argument("--roles", action="store_true", help="list the roles and exit")
    args = ap.parse_args()

    try:
        definitions, roles = load()
    except exceptions.TOML_ERRORS as e:
        print(f"cannot read {VOCABULARY}: {type(e).__name__}: {e}", file=sys.stderr)
        return 1

    if args.roles:
        for role in Reviewer:
            print(f"{role.value:<20} {len(terms_for(role.value, roles))} terms")
        return 0

    if not args.reviewer:
        ap.error("one of --reviewer or --roles is required")

    try:
        print(render(args.reviewer, definitions, roles), end="")
    except KeyError as e:
        print(e.args[0], file=sys.stderr)
        return 1
    return 0
