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
import json
from pathlib import Path

from comment_review.desk.containers import EditCopy
from comment_review.flows import revise
from comment_review.machine import exceptions
from comment_review.machine.json_object import object_of
from comment_review.machine.repo import undraftable, write_raw


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
    # !! `--docket` BECAME `--copy` AT `P57`. The flow's first step transcribes
    # an `edit_copy` into a docket -- `flows.revise.docket_of`,
    # `decision-log.md Process: #76` -- so the input is the artifact the middle
    # actually produces, and the docket is an internal value.
    #
    # !! IT TAKES ANY COPY, NOT ONLY THE COPY CHIEF'S. Roy, 2026-09-02: *"it
    # could also be ownership contexts edit-copy or any intermediate edit-copy
    # which allows the stage outputs to run."* That is what lets one stage's
    # output become the revise the next stage reads.
    ap.add_argument(
        "--copy",
        required=True,
        help='JSON: an edit_copy -- {"role", "read_from", "sheets"}',
    )
    # !! `--to-docket` STOPS THE RUN AT THE TRANSCRIBE -- `P58`, Roy 2026-09-02:
    # *"we add a --from-docket, --to-docket flags that allow the flow to
    # start/stop in the middle of the flow."* It is also what gives
    # `Docket.serialize` a production reader, so the format is exercised rather
    # than merely kept.
    ap.add_argument(
        "--to-docket",
        help="write the transcribed docket here and stop -- no revise is pulled",
    )
    # ! NOT `required=True` ANY MORE. `--out` is the revise root, and a run that
    # stops at the docket pulls none; requiring it would make the caller name a
    # directory nothing writes to. Asked for below, where it is needed.
    ap.add_argument(
        "--out",
        help="the revise root the pulled drafts are written to (must not exist yet)",
    )
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    if not args.to_docket and not args.out:
        print("REFUSED: --out is required unless --to-docket stops the run")
        return 2
    # ! A PLACEHOLDER WHERE THE RUN STOPS EARLY, so the guards below can be
    # skipped rather than answered. Nothing reads it on that path.
    out = Path(args.out).resolve() if args.out else repo
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
    #
    # ! BOTH `--out` GUARDS ARE SKIPPED WHERE THE RUN STOPS AT THE DOCKET. They
    # are about the revise root, and `--to-docket` pulls no revise -- asking
    # them anyway would refuse a run for a directory it never touches.
    if not args.to_docket:
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
    if not args.to_docket and out.exists():
        print(
            f"REFUSED: --out {out} already exists, and a revise is pulled into"
            " a directory that does not exist yet -- nothing written"
        )
        return 2
    # !! THE LOAD IS THREE STEPS AND EACH FAILS FOR ITS OWN REASON -- Roy,
    # 2026-08-31: moving the load out of the module *"makes file io errors and
    # malformed json load dump errors an explicit different step in the flow so
    # those can be done without extra collisions."* `decision-log.md Process:
    # #67`.
    #
    #     read_text     the file is missing, unreadable, undecodable
    #     object_of     the text is not JSON, or is JSON that is not an object
    #     deserialize   it is an object, and it is not a docket
    #
    # ! THE MIDDLE TWO WERE ONE CALL UNTIL 2026-08-31. `docket.read` took TEXT
    # and did its own decode, so "not JSON" and "not a docket" came back as one
    # reason string from one call, and a caller wanting to answer them
    # differently had to match on the message.
    try:
        copy_text = Path(args.copy).read_text(encoding="utf-8")
    except exceptions.READ_ERRORS as e:
        print(f"CANNOT READ ({type(e).__name__}) -- nothing written")
        return 2

    loaded, why = object_of(copy_text, "edit_copy")
    if why:
        print(f"CANNOT READ THE COPY: {why} -- nothing written")
        return 2

    copy, problems = EditCopy.deserialize(args.copy, loaded)
    if copy is None:
        # ! EVERY BROKEN RULE, NOT THE FIRST. `docket.read` stopped at one, so a
        # copy with three bad pages took three runs to fix.
        for line in problems:
            print(f"CANNOT READ THE COPY: {line} -- nothing written")
        return 2

    # ! THE TRANSCRIBE IS THE FLOW'S FIRST STEP and cannot fail: every rule it
    # would have checked is settled by the parse above -- `Process: #76`.
    held = revise.docket_of(copy)

    # !! THE SERIALIZE IS THE CONTAINER'S AND THE DUMP IS THE COMMAND'S --
    # `decision-log.md Process: #65`, `#67`, and the same shape
    # `commands/collate.py` writes its chief copy with. Raw JSON at the save and
    # nowhere between.
    if args.to_docket:
        try:
            write_raw(Path(args.to_docket), json.dumps(held.serialize(), indent=2))
        except exceptions.READ_ERRORS as e:
            print(f"CANNOT WRITE ({type(e).__name__}) -- nothing written")
            return 2
        pages = len(held.schedules)
        print(f"{args.to_docket}: {pages} page(s) scheduled -- no revise pulled")
        return 0

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
    schedules = sorted(held.schedules, key=lambda s: s.path)
    for schedule in schedules:
        print(f"{schedule.path} -> {pulled.root / schedule.path}")
    print(f"{len(schedules)} page(s) drafted for review")
    return 0
