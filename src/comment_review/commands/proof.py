"""The `proof` command: its argument parsing and its exit code.

    comment_review proof --proof P.json --repo . --out DIR
    comment_review proof --proof P.json --only ADDRESS --repo . --out DIR

The work is `flows.revise.pull`; this is only the console face of it.

The input is the closed master proof, ruled `decision-log.md Process: #184`:
its decided places are what the write end sets. `--copy` takes a role's own
edit_copy instead, for that role's own draft.

`--only` is the author's partial approval, ruled `Process: #192`: the places
they approved, named over that same proof, and nothing set anywhere else.

!! A MODULE DOES ONE JOB AND HAS NO CLI; A FLOW CALLS MODULES;
A COMMAND EXPOSES A FLOW. Ruled 2026-08-24 -- `decision-log.md Process: #12`.
This file parses arguments, reads ONE file and prints; the order of the
chain this command exposes lives in `flows/revise.py` since 2026-08-28 --
`flows/proof_setter.py` still orders the per-page draft steps `revise.pull`
calls into, but no longer the whole chain.

! IT READ TWO UNTIL 2026-08-26. The docket now carries each page's path and the
sha it was read at, so the binder it used to be handed alongside has nothing
left to answer -- `decision-log.md Vocabulary: #14`.

`--out` is the revise root: it holds only the pages the docket schedules,
as drafted, and no other file -- the write phase copies only the files it
modifies, `docs/decision-log.md Process: #117`. `pull` is what stage 7a
reads -- see `TODO/the-flow-assumes-every-role-reads-at-once.md` T7 -- and
its own `into.mkdir` requires `--out` not to exist yet. `revise=1`: this
command pulls straight off the checkout (the original, revise 0), and has
no record of an earlier revise to number itself after -- the same number
`tests/test_revise.py` and `tests/test_revise_addresses.py` use for a pull
off the original.
"""

import argparse
import json
from pathlib import Path

from comment_review import exceptions
from comment_review.desk.proof.edit_copy import EditCopy
from comment_review.desk.proof.master_proof import MasterProof
from comment_review.docket.docket import Docket
from comment_review.flows import revise, transcribe
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
    # an `edit_copy` into a docket -- `flows.transcribe.docket_of`,
    # `decision-log.md Process: #76` -- so the input is the artifact the middle
    # actually produces, and the docket is an internal value.
    #
    # !! IT TAKES ANY COPY, NOT ONLY THE COPY CHIEF'S. Roy, 2026-09-02: *"it
    # could also be ownership contexts edit-copy or any intermediate edit-copy
    # which allows the stage outputs to run."* That is what lets one stage's
    # output become the revise the next stage reads.
    # !! THE TWO INPUTS ARE EXCLUSIVE AND ONE IS REQUIRED -- `P59`. `--copy`
    # enters at the top of the flow and transcribes; `--from-docket` enters
    # BELOW the transcribe, at the docket a `--to-docket` run stopped on. Both
    # together would name two inputs for one run, and argparse states that
    # itself rather than leaving it to a hand-written check.
    # !! `--proof` IS THE WRITE END'S INPUT -- `decision-log.md Process: #184`.
    # A closed master proof holds every place the fold decided, so the
    # transcribe reads those places. The chief's copy restated the same
    # decisions as marks, and folding them again made this command depend on
    # that restatement reproducing the fold exactly. `--copy` stays for a
    # role's own draft, which is the artifact it was written for.
    source = ap.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--proof",
        help="JSON: a closed master_proof -- its decided places are what is set",
    )
    source.add_argument(
        "--copy",
        help='JSON: an edit_copy -- {"role", "read_from", "sheets"} -- for a'
        " role's own draft",
    )
    source.add_argument(
        "--from-docket",
        help="JSON: a docket a --to-docket run wrote -- skips the transcribe",
    )
    # `--only` is the partial approval -- `decision-log.md Process: #192`.
    # The author approves some decided places and not others, and what they
    # ruled is a set of addresses over the proof rather than a second
    # artifact. Repeatable, and a place it does not name is left as the page
    # has it.
    ap.add_argument(
        "--only",
        action="append",
        default=[],
        metavar="ADDRESS",
        help="set this decided place alone; repeat for each place the author"
        " approved (requires --proof)",
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
    # ! READING A DOCKET IN ORDER TO WRITE IT BACK OUT IS NEVER THE INTENT.
    # The two flags are the two BOUNDARIES of one flow, so naming both leaves
    # no flow between them.
    if args.from_docket and args.to_docket:
        print(
            "REFUSED: --from-docket and --to-docket are the two ends of the"
            " transcribe, and naming both leaves nothing to run"
        )
        return 2
    # `--only` filters places, and only a proof has any. A copy holds marks
    # and a docket holds alterations already chosen, so the flag has nothing
    # to filter on either -- an input error rather than a refusal further
    # down, where it would read as a fact about the file.
    if args.only and not args.proof:
        print("REFUSED: --only names places of a closed proof, so it needs --proof")
        return 2
    # !! ONE FORK, ASKED ONCE: is a revise being pulled, or does the run stop at
    # the docket? Every `--out` rule below belongs to the pulling path alone,
    # and `--to-docket` touches no revise root -- so they are answered inside
    # this branch rather than each re-testing the same flag. `out` stays None on
    # the stop path, which is what makes "nothing reads it" a fact the code
    # states rather than a comment a reader has to trust.
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
    # `--out` must not exist yet, and the check below is what refuses it:
    # `pull` makes `--out` itself with `into.mkdir`, which raises
    # `FileExistsError` on a directory that is already there -- even an
    # empty one -- so this turns that into a named reason at exit 2 rather
    # than a traceback out of `pull`. `undraftable` does not ask this: it
    # refuses a non-directory or an overlap, and a pre-existing, disjoint
    # `--out` passes it.
    out = None
    if not args.to_docket:
        if not args.out:
            print("REFUSED: --out is required unless --to-docket stops the run")
            return 2
        out = Path(args.out).resolve()
        why = undraftable(out, repo)
        if why:
            print(f"REFUSED: --out {why} -- nothing written")
            return 2
        if out.exists():
            print(
                f"REFUSED: --out {out} already exists, and a revise is pulled"
                " into a directory that does not exist yet -- nothing written"
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
    #
    # ! EVERY INPUT TAKES THE SAME THREE STEPS; only the container differs. The
    # noun in each message is the flag the caller passed, so a reason names the
    # thing they handed over rather than an internal type.
    source = args.from_docket or args.proof or args.copy
    noun = "DOCKET" if args.from_docket else "PROOF" if args.proof else "COPY"
    try:
        text = Path(source).read_text(encoding="utf-8")
    except exceptions.READ_ERRORS as e:
        print(f"CANNOT READ ({type(e).__name__}) -- nothing written")
        return 2

    loaded, why = object_of(text, noun.lower())
    if why:
        print(f"CANNOT READ THE {noun}: {why} -- nothing written")
        return 2

    # ! EVERY BROKEN RULE, NOT THE FIRST. `docket.read` stopped at one, so a
    # document with three bad pages took three runs to fix.
    if args.from_docket:
        held, problems = Docket.deserialize(source, loaded)
    elif args.proof:
        # The transcribe refuses a proof that has not closed, one whose
        # places will not read back, and a page it cannot open -- so the
        # same console face reports it here as below.
        proof, problems = MasterProof.deserialize(source, loaded)
        try:
            held = (
                transcribe.docket_of_proof(proof, repo, only=tuple(args.only) or None)
                if proof is not None
                else None
            )
        # The approval's refusals open with their own sentence, and shared
        # the proof's until `#192` was reviewed. *The proof decided nothing
        # that can be set* is false where the proof decided everything and
        # the list of places could not be honoured, so the two are told
        # apart by the exception rather than by the reader.
        except transcribe.CannotApprove as refused:
            print(
                "REFUSED: the approval names a place this proof cannot set"
                " -- nothing written"
            )
            for line in refused.reasons:
                print(line)
            return 1
        except transcribe.CannotTranscribe as refused:
            print(
                "REFUSED: the proof decided nothing that can be set -- nothing written"
            )
            for line in refused.reasons:
                print(line)
            return 1
    else:
        copy, problems = EditCopy.deserialize(source, loaded)
        # The transcribe folds, so it can refuse, and it could not until the
        # marks table decided what a mark sets. `docket_of` runs the Unit of
        # Work over the copy's own places, so a mark whose row cannot read it
        # against the page rolls the fold back and nothing is drafted. A
        # console face prints the reasons rather than handing over a
        # traceback, the same way `AddressesMoved` is reported below.
        try:
            held = transcribe.docket_of(copy, repo) if copy is not None else None
        except transcribe.CannotTranscribe as refused:
            print("REFUSED: the copy's own marks were sent back -- nothing written")
            for line in refused.reasons:
                print(line)
            return 1
    if held is None:
        for line in problems:
            print(f"CANNOT READ THE {noun}: {line} -- nothing written")
        return 2

    # !! THE SERIALIZE IS THE CONTAINER'S AND THE DUMP IS THE COMMAND'S --
    # `decision-log.md Process: #65`, `#67`, and the same shape
    # `commands/collate.py` writes its chief copy with. Raw JSON at the save and
    # nowhere between.
    #
    # ! THE SAME FORK AS THE `--out` BRANCH ABOVE, AND ITS OTHER SIDE. `out` is
    # None exactly when this branch is taken, so the pull below reaches it only
    # where it is a real path -- which is why the two are written as one
    # question asked twice rather than four independent flag tests.
    if out is None:
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
