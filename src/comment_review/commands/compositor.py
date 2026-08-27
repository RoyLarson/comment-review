"""The `compositor` command: its argument parsing and its exit code.

The work is `results.compositor`; this is only the console face of it.

!! A MODULE DOES ONE JOB AND HAS NO CLI; A FLOW CALLS MODULES;
A COMMAND EXPOSES A FLOW. Ruled 2026-08-24 -- `decision-log.md Process: #12`.
"""

import argparse
from pathlib import Path

from comment_review.results.compositor import identity, lossless


def main(argv: list[str] | None = None) -> int:
    """Prove the identity over every path given; nonzero if any file differs."""
    parser = argparse.ArgumentParser(description="Set a page as text.")
    # !! NO `--repo`, and it was ADVERTISED rather than merely unread. It was
    # parsed here, named on line 3 of this module's own docstring, and passed
    # nowhere. MEASURED 2026-08-22, while `identity` and `lossless` still took
    # the `rel` it fed -- `identity(p)` and `identity(p, rel="totally/other.py")`
    # both answered `None`, and they had to: `rel` set only the PATH half of an
    # address, `_held` keys on the cue half, and `set_page` never reads
    # `page.path`. A documented flag that cannot change an answer is a false
    # statement where a reader looks first, so the flag went and the parameter
    # went after it.
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args(argv)
    same = moved = broken = 0
    for path in args.paths:
        gone = lossless(path)
        if gone is not None:
            broken += 1
            print(f"  LOSSY   {path} -- {gone}")
            continue
        why = identity(path)
        if why is None:
            same += 1
            print(f"  set     {path}")
        else:
            moved += 1
            print(f"  moved   {path} -- {why}")
    print(f"\n{same} identical, {moved} normalised, {broken} LOSSY")
    # !! ONLY A LOST OR INVENTED LINE FAILS. A normalised file is the ruled
    # series order doing what it was ruled to do -- see `set_page`.
    return 1 if broken else 0
