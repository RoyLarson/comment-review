"""The `proof` command: its argument parsing and its exit code.

    comment_review proof --proof P.json --repo . --out DIR
    comment_review proof --proof P.json --only ADDRESS --repo . --out DIR

The work is `flows.revise.pull`; this is only the console face of it.

The input is the closed master proof: its decided places are what the write
end sets. `--copy` takes a role's own edit_copy instead, for that role's own
draft.

`--only` is the author's partial approval: the places they approved, named
over that same proof, and nothing set anywhere else.

`--to-docket` stops the run at the transcribe and writes the docket there;
`--from-docket` starts a run from such a docket, below the transcribe. They
are the two ends of one flow, so naming both is refused.

This file parses arguments, reads one file, prints, and with `--to-docket`
writes the docket; the order of the chain this command exposes lives in
`flows/revise.py`, and `flows/proof_setter.py` orders the per-page draft steps
`revise.pull` calls into.

`--out` is the revise root: it holds only the pages the docket schedules, as
drafted, and no other file -- the write phase copies only the files it
modifies. `pull` is what stage 7a reads, and its own `into.mkdir` requires
`--out` not to exist yet.
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
    """Read a proof, a copy or a docket, run the chain, report what refused.

    Returns:
        0 when the drafts or the docket were written; 1 when the transcribe
        or the pull refused; 2 when an argument or an input file is wrong, or
        the docket cannot be written.
    """
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--repo", default=".", help="repo root the addresses resolve against"
    )
    # !! The three inputs are exclusive and one is required. `--proof` and
    # `--copy` enter at the top of the flow and transcribe; `--from-docket`
    # enters below the transcribe, at the docket a `--to-docket` run stopped on.
    # Two together would name two inputs for one run, and argparse states that
    # itself rather than leaving it to a hand-written check.
    source = ap.add_mutually_exclusive_group(required=True)

    # !! `--proof` is the write end's input. A closed master proof holds every
    # place the fold decided, so the transcribe reads those places. `--copy`
    # stays for a role's own draft, which is the artifact it was written for.
    source.add_argument(
        "--proof",
        help="JSON: a closed master_proof -- its decided places are what is set",
    )

    # The flow's first step transcribes an `edit_copy` into a docket --
    # `flows.transcribe.docket_of` -- so the input is the artifact the middle
    # actually produces, and the docket is an internal value.
    #
    # !! It takes any copy, not only the copy chief's. That is what lets one
    # stage's output become the revise the next stage reads.
    source.add_argument(
        "--copy",
        help='JSON: an edit_copy -- {"role", "read_from", "sheets"} -- for a'
        " role's own draft",
    )
    source.add_argument(
        "--from-docket",
        help="JSON: a docket a --to-docket run wrote -- skips the transcribe",
    )
    # `--only` is the partial approval. The author approves some decided places
    # and not others, and what they ruled is a set of addresses over the proof
    # rather than a second artifact. Repeatable, and a place it does not name is
    # left as the page has it.
    ap.add_argument(
        "--only",
        action="append",
        default=[],
        metavar="ADDRESS",
        help="set this decided place alone; repeat for each place the author"
        " approved (requires --proof)",
    )
    # !! `--to-docket` stops the run at the transcribe. It is also what gives
    # `Docket.serialize` a production caller, so the format is exercised rather
    # than merely kept.
    ap.add_argument(
        "--to-docket",
        help="write the transcribed docket here and stop -- no revise is pulled",
    )
    # ! Not `required=True`. `--out` is the revise root, and a run that stops at
    # the docket pulls none; requiring it would make the caller name a directory
    # nothing writes to. Asked for below, where it is needed.
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
    out = None
    if not args.to_docket:
        if not args.out:
            print("REFUSED: --out is required unless --to-docket stops the run")
            return 2
        out = Path(args.out).resolve()

        # !! `--out` must be disjoint from `--repo`, and the per-file guard
        # cannot ask this. On an overlap a target lands inside `--out` by way of
        # being the source file itself.
        #
        # !! The rule is `repo.undraftable`'s and is asked in two places. Asking
        # it here as well is what keeps a bad `--out` an input error at exit 2
        # rather than a refusal at exit 1.
        #
        # ! It also answers `--out` naming a regular file, with a reason at exit
        # 2, as every other bad input here is answered.
        #
        # `--out` must not exist yet, and the check below is what refuses it:
        # `pull` makes `--out` itself with `into.mkdir`, which raises
        # `FileExistsError` on a directory that is already there -- even an
        # empty one -- so this turns that into a named reason at exit 2 rather
        # than a traceback out of `pull`. `undraftable` does not ask this: it
        # refuses a non-directory or an overlap, and a pre-existing, disjoint
        # `--out` passes it.
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
    # !! The load is three steps and each fails for its own reason.
    #
    #     read_text     the file is missing, unreadable, undecodable
    #     object_of     the text is not JSON, or is JSON that is not an object
    #     deserialize   it is an object, and not the docket, proof or copy named
    #
    # ! Every input takes the same three steps; only the container differs. The
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

    if args.from_docket:
        held, problems = Docket.deserialize(source, loaded)
    elif args.proof:
        proof, problems = MasterProof.deserialize(source, loaded)

        # The transcribe refuses a proof that has not closed, one whose
        # places will not read back, and a page it cannot open -- so the
        # same console face reports it here as below.
        try:
            held = (
                transcribe.docket_of_proof(proof, repo, only=tuple(args.only) or None)
                if proof is not None
                else None
            )
        # The approval's refusals open with their own sentence. *The proof
        # decided nothing that can be set* is false where the proof decided
        # everything and the list of places could not be honoured, so the two
        # are told apart by the exception rather than by the reader.
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
        # The transcribe folds, so it can refuse. `docket_of` runs the Unit of
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

    # !! The serialize is the container's and the dump is the command's: two-space
    # JSON through `write_raw`, the same dump `flows.proof_io.save_proof` gives
    # the master proof `commands/collate.py` saves. Raw JSON at the save and
    # nowhere between.
    #
    # ! The same fork as the `--out` branch above, and its other side. `out` is
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

    # !! Routed through `revise.pull`, not `proof_setter.run` directly. `pull`
    # writes each draft into the revise root at its page's repo path and runs
    # the address gate over those pages; `proof_setter.run` alone does neither.
    # !! `AddressesMoved` is caught and reported. Letting it escape would end
    # this command on a traceback, while every other failure in this file prints
    # a reason and returns 1 or 2.
    #
    # ! The raise itself stays right, and `flows/revise.py` keeps it: a moved
    # address space is a defect to surface loudly, not a state to paper over.
    # What changes is that the console face of a flow does not hand a user a
    # stack trace -- and this is the rarest input path, which is where a
    # traceback is least actionable. `pull` has already removed the revise
    # root by the time this runs, so there is nothing to clean up here.
    #
    # `revise=1`: this command pulls straight off the checkout (the original,
    # revise 0), and has no record of an earlier revise to number itself after
    # -- the same number `tests/test_revise.py` and
    # `tests/test_revise_addresses.py` use for a pull off the original.
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
