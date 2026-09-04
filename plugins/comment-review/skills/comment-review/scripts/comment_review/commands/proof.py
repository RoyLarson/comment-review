"""The `proof` command: its argument parsing and its exit code.

    comment_review proof --docket D.json --repo . --out DIR

The work is `flows.revise.pull`; this is only the console face of it.

!! A MODULE DOES ONE JOB AND HAS NO CLI; A FLOW CALLS MODULES;
A COMMAND EXPOSES A FLOW. Ruled 2026-08-24 -- `decision-log.md Process: #12`.
This file parses arguments, reads ONE file and prints; the order of the
chain this command exposes lives in `flows/revise.py` since 2026-08-28 --
`flows/proof_setter.py` still orders the per-page draft steps `revise.pull`
calls into, but no longer the whole chain.

! IT READ TWO UNTIL 2026-08-26. The docket now carries each page's path and the
sha it was read at, so the binder it used to be handed alongside has nothing
left to answer -- `decision-log.md Vocabulary: #14`.

!! `--out` IS THE REVISE ROOT SINCE 2026-08-28, NOT A DIRECTORY OF ONLY THE
CHANGED PAGES. This command used to call `flows.proof_setter.run` directly,
which drafted only the docket's own pages into `--out`; `commands/proof.py`
and `flows/revise.py`'s own `pull` were then two mechanisms that each built a
draft tree, when stage 7a must read ONE artifact. `pull` is what stage 7a
reads now -- see `TODO/the-flow-assumes-every-role-reads-at-once.md` T7 --
so `--out` holds a full copy of `--repo` with the docket's pages overlaid,
and `pull`'s own `shutil.copytree` requires it not to exist yet. `revise=1`:
this command pulls straight off the checkout (the original, revise 0), and
has no record of an earlier revise to number itself after -- the same number
`tests/test_revise.py` and `tests/test_revise_addresses.py` use for a pull
off the original.
"""

import argparse
from pathlib import Path

from comment_review.docket import docket as docket_mod
from comment_review.flows import revise
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
    ap.add_argument(
        "--out",
        required=True,
        help="the revise root the pulled drafts are written to (must not exist yet)",
    )
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
    # !! `--out` MUST NOT EXIST YET, since 2026-08-28. `revise.pull` copies
    # `--repo` into it with `shutil.copytree`, which raises `FileExistsError`
    # on a directory that is already there -- even an empty one. `undraftable`
    # above does not ask this: it refuses a non-directory or an overlap, and a
    # pre-existing, disjoint `--out` passes it. Asked here so this stays an
    # INPUT error at exit 2, the same as every other bad `--out` above.
    if out.exists():
        print(
            f"REFUSED: --out {out} already exists, and a revise is pulled into"
            " a directory that does not exist yet -- nothing written"
        )
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

    # !! ROUTED THROUGH `revise.pull` SINCE 2026-08-28, NOT `proof_setter.run`
    # DIRECTLY. `pull` is the one mechanism left that builds a draft tree --
    # see this module's own docstring -- and `revise=1` is explained there.
    # !! `AddressesMoved` IS CAUGHT AND REPORTED, AND PROPAGATED UNCAUGHT UNTIL
    # 2026-08-28. Letting it escape made this command exit on a TRACEBACK while
    # every other failure in this file prints a reason and returns 1 or 2 --
    # and `binder.py`'s own `_read_from_problem` states the rule one commit
    # earlier: *"RAISING IS NOT REFUSING: a refusal in this module is a NAMED
    # REASON and an exit code."*
    #
    # ! THE RAISE ITSELF STAYS RIGHT, and `flows/revise.py` keeps it: a moved
    # address space is a defect to surface loudly, not a state to paper over.
    # What changes is that the CONSOLE FACE of a flow does not hand a user a
    # stack trace -- and this is the rarest input path, which is where a
    # traceback is least actionable. `pull` has already removed the revise
    # root by the time this runs, so there is nothing to clean up here.
    try:
        pulled = revise.pull(held, repo, out, revise=1)
    except revise.AddressesMoved as moved:
        print(f"REFUSED: the address space moved -- {moved}")
        print("nothing drafted -- the revise could not be trusted")
        return 1
    for stopped in pulled.refusals:
        where = stopped.path or "<the set>"
        print(f"REFUSED at {stopped.step}: {where} -- {stopped.why}")
    if pulled.refusals:
        print(f"{len(pulled.refusals)} refusal(s) -- nothing drafted")
        return 1
    # !! LISTED FROM THE DOCKET'S OWN SCHEDULES, NOT FROM A `Drafted` LIST --
    # `pull` returns the assembled revise, not a per-page record of what it
    # drafted. `sorted` matches the order `proof_setter.run` itself drafts in.
    schedules = sorted(docket_mod.schedules_of(held))
    for schedule in schedules:
        print(f"{schedule.path} -> {pulled.root / schedule.path}")
    print(f"{len(schedules)} page(s) drafted for review")
    return 0
