r"""The `collate` command: its argument parsing, its report and its exit code.

    comment_review collate --stage 4c --binder B.json --out chief.json \\
        --edit-copy a.json --edit-copy b.json

The work is `flows.collate`; this is only the console face of it.

!! A MODULE DOES ONE JOB AND HAS NO CLI; A FLOW CALLS MODULES;
A COMMAND EXPOSES A FLOW. `decision-log.md Process: #12`.

!! EVERY CARRIED-FORWARD PLACE IS NAMED, NEVER COUNTED. `A-T2` of
`TODO/no-command-for-the-middle.md`: a run that settles 4 of 10 must say what
became of the other 6. ! WHAT IT DOES NOT YET DO is name the command that
CONTINUES them -- `Process: #51`'s other half, which is a later plan's, by
this plan's own scoping.
"""

import argparse
import json
import sys
from pathlib import Path

from comment_review.binder.binder import Binder
from comment_review.desk.proof import MismatchedRoot
from comment_review.flows.collate import CannotCollate, collate
from comment_review.machine import exceptions
from comment_review.machine.json_object import object_of

#: Exit codes, extending `distribute`'s own 0/1/2 with the outcomes a caller
#: branches on. `main` CHECKS `got.escalations`, THEN `got.rereads`, THEN
#: `got.drift`, so a run holding more than one reports the FIRST of those it
#: holds: an escalation is the stronger claim on a person's attention than a
#: re-read, and a re-read is stronger than drift, which never blocks a place
#: from settling -- `desk.collator.drift_in`'s own docstring: "REPORTED, NOT
#: REFUSED".
OK = 0
BROKEN = 1
UNREADABLE = 2
REREADS = 3
ESCALATIONS = 4
#: !! ADDED 2026-08-30. Before this code existed, a run whose every mark
#: parsed but whose `raw_text` disagreed with the seeded base -- drift -- wrote
#: the chief copy and exited `OK`: `main`'s own docstring named only
#: `got.problems` and `RECONCILE_ERRORS` as causes of a non-`OK` outcome, so a
#: caller branching on the exit code alone -- the documented contract -- got no
#: signal that a drifted place fed the written output. `drift_in`'s ruling is
#: that the COPY is never discarded over drift; it says nothing about the exit
#: code, which this closes.
DRIFT = 5
#: !! ADDED 2026-08-31, and it is `Process: #63` reaching the exit codes. A role
#: short of its shard is REPORTED, never a refusal that voids the round -- but
#: `_coverage_problems`' findings rode in `got.problems`, which returns `BROKEN`
#: above and writes no chief copy. Measured: one role, a two-place binder, one
#: place answered -- the chief carried the settled mark and the command threw it
#: away. Its own code lets the caller see a short round WITHOUT losing the work
#: the round did, which is what the ruling asks for.
#: ! IT IS NOT `DRIFT`'s SIBLING. `DRIFT` exists over a check `Process: #62`
#: ruled out, and this one answers whether a ROLE ANSWERED rather than whether
#: the tree moved. Coverage is a fact about the round; drift was a fact about a
#: page, which the middle has no stake in.
COVERAGE = 6

#: The ways a stage cannot be reconciled at all, as against a mark that broke a
#: rule. They mean the SET cannot be read, so none is routable back to one role
#: the way a `Problem` is -- they exit `BROKEN` with the reason on stderr.
#: !! IT HELD THREE UNTIL `P42` AND NOW HOLDS ONE, because two of the three
#: became unconstructable rather than merely unreached. `desk.collator
#: .UnnamedRole` is DELETED -- `places` takes a `MasterProof`, whose copies each
#: carry a `role` `EditCopy.deserialize` already required -- and `gather` no
#: longer subscripts `read_from`, so the `KeyError` added 2026-08-30 has no
#: raiser left. ! THAT `KeyError` WAS REAL WHEN IT WAS ADDED: `gather` raised it
#: by design and, uncaught, it escaped past this module's own promise that "a
#: raise is not a refusal".
#: !! AND `MismatchedRoot` IS STILL UNREACHABLE FROM `collate`, which is a
#: different fact and is why it stays: `flows.collate.collate` wraps its only
#: `gather` call and re-raises it as `CannotCollate`, so both mismatched-root
#: tests go through THAT handler. It remains catchable here because nothing
#: guarantees a future caller cannot reach `gather` another way, and a catch
#: that cannot fire is cheaper than the traceback if one does.
#: ! `CannotCollate` CARRIES ITS OWN `problems` and is handled separately below,
#: which is the whole point of it; it is deliberately NOT in this tuple.
#: ! BOUND TO A NAME because no `except` in a shipped file holds a tuple
#: literal; see `machine/exceptions.py`.
RECONCILE_ERRORS = (MismatchedRoot,)


def _report(problems: list) -> None:
    """Every routable `Problem` on stdout, one per line.

    ! ONE SPELLING, FOUR CALLERS -- the refusal path, `problems`, `drift` and
    `coverage`. A second copy of the format string is a place for them to
    disagree about what a reader is shown. ! IT SAID TWO UNTIL 2026-08-31, and
    `drift` kept its own hand-written loop three lines below this function for
    the whole of that day, which is the duplication this exists to prevent.

    ! `(the copy)` STANDS IN FOR AN EMPTY ADDRESS, which is what a problem about
    the whole document carries -- a missing `role`, a bad `read_from`, a sheet
    the envelope refused. There is no place to name, and a blank column reads as
    a missing value rather than as a fact about the copy.
    """
    for problem in problems:
        where = problem.address or "(the copy)"
        print(f"{problem.role} {where}: {problem.message}")


def _load(path: str) -> tuple[dict, str]:
    """Read one edit_copy off disk as a JSON object, or say why it is not one.

    !! THE TWO FAILURES ARE SEPARATE STEPS, `decision-log.md Process: #67`.
    Roy, 2026-08-31: moving the load out *"makes file io errors and malformed
    json load dump errors an explicit different step in the flow so those can
    be done without extra collisions."* The read is this function's; the decode
    is `machine.json_object.object_of`'s; whether the object is an edit_copy is
    `EditCopy.deserialize`'s, one step further along inside `collate`.

    !! IT HELD ITS OWN `json.loads` AND ITS OWN DICT GUARD UNTIL `P43` -- the
    second decode path in this file, beside the `object_of` call the binder
    already went through. That is the duplication `object_of`'s own header
    records being removed from the two readers, re-acquired one module over:
    two spellings of *is this text an object*, in one command, disagreeing on
    the wording of the refusal.

    Returns:
        `(the object, "")`, or `({}, reason)` naming the path.
    """
    try:
        text = Path(path).read_text(encoding="utf-8")
    except exceptions.READ_ERRORS as err:
        return {}, f"cannot read {path}: {err}"
    loaded, why = object_of(text, "edit_copy")
    return ({}, f"{path} is {why}") if why else (loaded, "")


def main() -> int:
    """Fold one stage's returned copies, report, and say what is left.

    Returns:
        One of `OK`, `BROKEN`, `UNREADABLE`, `REREADS`, `ESCALATIONS`,
        `DRIFT` or `COVERAGE`. `BROKEN` covers both a copy that broke a rule
        (`got.problems`) and a stage that could not be reconciled at all -- a
        raise is not a refusal, so both are caught and named on stderr rather
        than left to escape as a traceback.

        ! NEITHER `COVERAGE` NOR `DRIFT` VOIDS THE ROUND -- both write the
        chief copy first, and both are weaker than either carried-forward
        outcome, so they are checked after `ESCALATIONS` and `REREADS`. A
        drifted place can still settle, and so can the places a short shard
        did answer (`decision-log.md Process: #63`).

        ! `COVERAGE` WAS MISSING FROM THIS LIST UNTIL 2026-08-31, one commit
        after it became reachable. A caller branching on the exit code -- the
        contract `DRIFT` was added to serve -- had no way to learn 6 exists.
    """
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stage", required=True, help="the stage label, e.g. 4c")
    ap.add_argument(
        "--binder", required=True, help="the binder these copies were seeded from"
    )
    ap.add_argument(
        "--edit-copy",
        action="append",
        default=[],
        metavar="PATH",
        help="one role's returned edit_copy; repeat for each",
    )
    ap.add_argument("--out", required=True, help="where to write the chief's edit_copy")
    # !! THE ROOT SOURCE VERIFICATION RESOLVES A `cite` AGAINST -- `P25`. It
    # defaults to the binder's own `read_from.root`, which is the tree the
    # copies were censused from and therefore the one their citations were
    # written against. ! WHY OPENING A CITED FILE IS NOT A PAGE READ is stated
    # once, at the call in `flows.collate.collate`, and not restated here.
    ap.add_argument(
        "--repo",
        help="the checkout a `sources` cite resolves against "
        "(default: the binder's own read_from.root)",
    )
    args = ap.parse_args()

    if not args.edit_copy:
        print("collate needs at least one --edit-copy", file=sys.stderr)
        return UNREADABLE

    try:
        binder_text = Path(args.binder).read_text(encoding="utf-8")
    except exceptions.READ_ERRORS as err:
        print(f"cannot read {args.binder}: {err}", file=sys.stderr)
        return UNREADABLE
    # !! THE LOAD IS THE FLOW'S, THE DESERIALIZE THE CONTAINER'S --
    # `decision-log.md Process: #67`. `object_of` turns the text into an
    # object; `Binder.deserialize` says whether that object is a binder.
    loaded, why = object_of(binder_text, "binder")
    if why:
        print(why, file=sys.stderr)
        return UNREADABLE
    binder, problems = Binder.deserialize(args.binder, loaded)
    if binder is None:
        for line in problems:
            print(line, file=sys.stderr)
        return UNREADABLE

    copies = []
    for path in args.edit_copy:
        copy, problem = _load(path)
        if problem:
            print(problem, file=sys.stderr)
            return UNREADABLE
        copies.append(copy)

    # ! THE BINDER NAMES ITS OWN TREE, so a caller that already passed one does
    # not pass it twice. `read_from` is refused as absent or malformed further
    # up the chain, and `.` is what a binder read from the working directory
    # says, so it is a fallback rather than a guess.
    root = Path(args.repo or binder.read_from.get("root") or ".")

    try:
        got = collate(args.stage, copies, binder, root)
    except CannotCollate as refusal:
        # !! THE ROUTABLE PROBLEMS GO OUT FIRST, THEN THE REFUSAL. A refusal
        # says the SET cannot be folded; it says nothing about the marks the
        # pass already ruled on, and discarding those made one copy's
        # incompatible header block routing for every other role. MEASURED
        # 2026-08-30: exit 1, stdout EMPTY. See `flows.collate.CannotCollate`.
        _report(refusal.problems)
        print(
            f"REFUSED: the proof could not be reconciled -- {refusal}", file=sys.stderr
        )
        return BROKEN
    except RECONCILE_ERRORS as err:
        # ! THE REFUSAL'S OWN MESSAGE IS PRINTED AS IT STANDS. A `KeyError`
        # branch stood here reading `f"a copy carries no {err}"`, because that
        # exception's `str()` is only the missing key, repr'd -- naming the
        # shape of a refusal rather than its cause. `gather` no longer raises
        # one (`P42`), and `MismatchedRoot` already says what went wrong.
        print(f"REFUSED: the proof could not be reconciled -- {err}", file=sys.stderr)
        return BROKEN

    _report(got.problems)
    _report(got.drift)
    # !! COVERAGE IS PRINTED BEFORE THE `problems` GATE AND DOES NOT TRIP IT --
    # `decision-log.md Process: #63`: a missing answer ROUTES back to the role
    # that owes it, and *the places that did come back still settle*. Carried in
    # `got.problems` it returned BROKEN here and wrote no chief copy, which is
    # the one thing that ruling forbids. It has its own list and its own code,
    # the way `drift` already does.
    _report(got.coverage)
    if got.problems:
        return BROKEN

    # !! THE SERIALIZE IS THE CONTAINER'S AND THE DUMP IS THE FLOW'S --
    # `decision-log.md Process: #65`, `#67`. `collate` returns an `EditCopy`
    # since `P42`; the wire dict is made here, at the save, and nowhere between.
    Path(args.out).write_text(
        json.dumps(got.chief.serialize(), indent=2), encoding="utf-8", newline=""
    )
    resolved = sum(len(sheet.marks) for sheet in got.chief.sheets)
    print(f"{args.out}: {resolved} places resolved")

    # !! NAMED, NEVER COUNTED. Each carried-forward place prints its address
    # and every role that ruled there, so a reader can act on one without
    # re-opening the copies.
    for entry in got.escalations:
        print(f"escalated {entry['address']}: {', '.join(entry['roles'])}")
    for entry in got.rereads:
        print(f"re-read {entry['address']}: {', '.join(entry['roles'])}")

    if got.escalations:
        return ESCALATIONS
    if got.rereads:
        return REREADS
    # ! COVERAGE IS OUTRANKED BY BOTH CARRIED-FORWARD OUTCOMES -- a place
    # nobody answered is weaker than a place a person must now rule on.
    #
    # ! IT SITS ABOVE `DRIFT` BY ACCIDENT OF WHAT IS LEFT, NOT BY DESIGN.
    # `Process: #62` ruled `drift_in` out, and its deletion is the move plan's
    # task 2; when it goes this branch goes with it and `COVERAGE` becomes the
    # last check before `OK`. Nothing here should be read as ranking the two.
    if got.coverage:
        return COVERAGE
    if got.drift:
        return DRIFT
    return OK
