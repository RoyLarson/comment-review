"""The `proof` command: its argument parsing and its exit code.

    comment_review proof --docket D.json --repo . --out DIR

The work is `flows.proof_setter`; this is only the console face of it.

!! A MODULE DOES ONE JOB AND HAS NO CLI; A FLOW CALLS MODULES;
A COMMAND EXPOSES A FLOW. Ruled 2026-08-24 -- `decision-log.md Process: #12`.
This file parses arguments, reads ONE file and prints; the order of the
chain lives in `flows/proof_setter.py` and nowhere else.

! IT READ TWO UNTIL 2026-08-26. The docket now carries each page's path and the
sha it was read at, so the binder it used to be handed alongside has nothing
left to answer -- `decision-log.md Vocabulary: #14`.
"""

import argparse
from pathlib import Path

from comment_review.docket import docket as docket_mod
from comment_review.flows import proof_setter
from comment_review.machine import exceptions
from comment_review.machine.repo import undraftable


def main() -> int:
    """Read the docket, run the chain, report what refused."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--repo", default=".", help="repo root the addresses resolve against"
    )
    # !! `--binder` WENT ON 2026-08-26, WITH THE NESTED DOCKET. It was read for
    # exactly two facts -- each page's sha, and the paths `unflatten` needed to
    # recover a real path from an address's flattened one. A schedule carries
    # both, so the binder no longer reaches the write chain at all.
    ap.add_argument(
        "--docket",
        required=True,
        help='JSON: {"pages": [{"path", "sha", "alterations": [{"cue", "text"}]}]}',
    )
    ap.add_argument("--out", required=True, help="directory the drafts are written to")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    out = Path(args.out).resolve()
    # !! `--out` MUST BE DISJOINT FROM `--repo`, and the per-file guard cannot
    # ask this. On an OVERLAP a target lands inside `--out` by way of being the
    # source file itself -- MEASURED 2026-08-22 on the galley command, which
    # overwrote the file under review, printed `1 page(s) set` and exited 0.
    # See `docs/history.md`.
    #
    # !! THE RULE IS `repo.undraftable`'s AND IS ASKED IN TWO PLACES. It was
    # spelled out here and in the galley command -- two copies of one rule --
    # and `flows/proof_setter.run` asked it nowhere, so calling that flow with
    # `into == repo` wrote over the files under review at `refused=[]`. Asking
    # it here as well is what keeps a bad `--out` an INPUT error at exit 2
    # rather than a refusal at exit 1.
    #
    # ! IT ALSO ANSWERS `--out` NAMING A REGULAR FILE, which used to reach the
    # console as a `FileExistsError` traceback out of `run`'s
    # `into.mkdir(exist_ok=True)` -- `exist_ok` covers an existing DIRECTORY
    # only, and every other bad input here prints a reason and returns 2.
    why = undraftable(out, repo)
    if why:
        print(f"REFUSED: --out {why} -- nothing written")
        return 2
    try:
        docket_text = Path(args.docket).read_text(encoding="utf-8")
    except exceptions.READ_ERRORS as e:
        print(f"CANNOT READ ({type(e).__name__}) -- nothing written")
        return 2

    held, why = docket_mod.read(docket_text)
    if why:
        print(f"CANNOT READ THE DOCKET: {why} -- nothing written")
        return 2

    drafted, refused = proof_setter.run(held, repo, out)
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
