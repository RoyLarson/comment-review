"""The `proof` command: its argument parsing and its exit code.

    comment_review proof --binder B.json --notations N.json --repo . --out DIR

The work is `flows.proof_setter`; this is only the console face of it.

!! A LIBRARY MODULE DOES ONE JOB AND HAS NO CLI; A FLOW CALLS LIBRARIES;
A COMMAND EXPOSES A FLOW. Ruled 2026-08-24 -- `decision-log.md Process: #12`.
This file parses arguments, reads two files and prints; the order of the
chain lives in `flows/proof_setter.py` and nowhere else.
"""

import argparse
from pathlib import Path

from comment_review.binder import binder as binder_mod
from comment_review.desk import notations as notations_mod
from comment_review.flows import proof_setter
from comment_review.machine import exceptions


def main() -> int:
    """Read the notations and the binder, run the chain, report what refused."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--repo", default=".", help="repo root the addresses resolve against"
    )
    ap.add_argument("--binder", required=True, help="the binder the agents ruled on")
    ap.add_argument(
        "--notations",
        required=True,
        help='JSON: {"<address>": "<replacement paragraph>"}, or null to delete',
    )
    ap.add_argument("--out", required=True, help="directory the drafts are written to")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    out = Path(args.out).resolve()
    # !! `--out` MUST BE DISJOINT FROM `--repo`, and the per-file guard cannot
    # ask this. On an OVERLAP a target lands inside `--out` by way of being the
    # source file itself -- MEASURED 2026-08-22 on `commands/galley.py`, which
    # overwrote the file under review, printed `1 page(s) set` and exited 0.
    # ! `is_relative_to` IS TRUE OF A PATH AND ITSELF, which is why both
    # directions are tested and an equality test would be redundant.
    if out.is_relative_to(repo) or repo.is_relative_to(out):
        print(
            f"REFUSED: --out {out} overlaps --repo {repo}, so a draft would be"
            " written over the files under review -- nothing written"
        )
        return 2
    try:
        binder_text = Path(args.binder).read_text(encoding="utf-8")
        notations_text = Path(args.notations).read_text(encoding="utf-8")
    except exceptions.READ_ERRORS as e:
        print(f"CANNOT READ ({type(e).__name__}) -- nothing written")
        return 2

    held, why = binder_mod.read(binder_text)
    if why:
        print(f"CANNOT READ THE BINDER: {why} -- nothing written")
        return 2
    marks, why = notations_mod.read(notations_text)
    if why:
        print(f"CANNOT READ THE NOTATIONS: {why} -- nothing written")
        return 2

    drafted, refused = proof_setter.run(marks, held, repo, out)
    for stopped in refused:
        where = stopped.path or "<the set>"
        print(f"REFUSED at {stopped.step}: {where} -- {stopped.why}")
    if refused:
        print(f"{len(refused)} refusal(s) -- nothing drafted")
        return 1
    for made in drafted:
        print(f"{made.path} -> {made.draft}")
    print(f"{len(drafted)} page(s) drafted for review")
    return 0
