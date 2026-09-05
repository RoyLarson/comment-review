"""The `check` command: what the fold would refuse, named before a role returns it.

    comment_review check --edit-copy copy.json [--binder B.json] [--repo R]
    comment_review check --answers answers.json --sent batch.json --role block-context
    comment_review check --contract

A role writes its copy or its batch answers with its file-write tool and runs
this over the file. It is the same boundaries the fold runs -- nothing here
decides anything the fold would not -- so a run that exits 0 here is a file
the fold reads whole.

!! A MODULE DOES ONE JOB AND HAS NO CLI; A FLOW CALLS MODULES;
A COMMAND EXPOSES A FLOW. `decision-log.md Process: #12`.

!! IT CHECKS AND DOES NOT WRITE. `TODO/completed/the-record-is-a-parsed-template
-and-should-be-a-value.md` T2, ruled 2026-08-17: a role edits a SEEDED
TEMPLATE in place with its file-write tool, not through a CLI it calls per
record, because no multi-line value may pass through a shell. The safe shape
named there is the file-write plus a CLI that validates; this is that CLI.

! MEASURED 2026-09-04, the game that asked for it: of about fifty submissions
across five hands, ten were refused at the fold and none on substance -- a
slot rewritten without its `question` key, a DiffMark `patch` meant as *keep
my patch*, three batches returned keyed by role instead of as a list, a
citation whose line did not match, addresses in slash form where the seed
was flattened. Each cost a turn. All are named here, before the send.

For a COPY: the envelope (`EditCopy.deserialize`), every place the role left
alone or wrote unreadably (`flows.mark_errors`), and, with `--binder`, source
verification and drift (`desk.collator.verify_report`, `drift_in`). For a
BATCH: every answer paired to the slot the flow SENT, by address
(`flows.turn.parse_answers`, T27), so `--sent` is the batch that went out.
The shape a role hands back is read the way the flow reads it
(`flows.turn.slots_of`): a list of slots, `{role: [slots]}`, or a lone slot.
"""

import argparse
import json
import sys
from pathlib import Path

from comment_review.desk.collator import Cache, base_texts, drift_in, verify_report
from comment_review.desk.containers import EditCopy
from comment_review.flows.mark_errors import mark_errors
from comment_review.flows.proof_io import load_batch, load_binder, load_copy, load_value
from comment_review.flows.turn import contracts, parse_answers, slots_of

#: Exit codes -- `distribute`'s 0/1/2. `BROKEN` is anything the fold would
#: refuse or send back; `UNREADABLE` is a file that is not an object at all.
OK = 0
BROKEN = 1
UNREADABLE = 2


def _refused(why: list[str]) -> int:
    """A file that is not what it says: every reason on stderr, `UNREADABLE`."""
    for line in why:
        print(line, file=sys.stderr)
    return UNREADABLE


def _check_copy(path: str, binder_path: str | None, repo: str | None) -> int:
    loaded, why = load_copy(Path(path))
    if why:
        return _refused(why)
    copy, problems = EditCopy.deserialize(path, loaded)
    if copy is None:
        for line in problems:
            print(line)
        return BROKEN
    found = 0
    for one in mark_errors([copy]):
        for reason in one.reasons:
            print(f"{one.role} {one.where}: {reason}")
            found += 1
    if binder_path:
        binder, why = load_binder(Path(binder_path))
        if binder is None:
            return _refused(why)
        root = Path(repo) if repo else binder.root
        cache: Cache = {}
        for problem in (
            *verify_report(copy, binder, root, cache),
            *drift_in(copy, base_texts(binder)),
        ):
            print(
                f"{problem.role} {problem.address or '(the copy)'}: {problem.message}"
            )
            found += 1
    print(f"{path}: {found} thing(s) the fold would send back")
    return BROKEN if found else OK


def _check_answers(path: str, sent_path: str, role: str) -> int:
    loaded, why = load_value(Path(path))
    if why:
        return _refused(why)
    batch, why = load_batch(Path(sent_path))
    if why:
        return _refused(why)
    sent = slots_of(batch, role)
    if not sent:
        print(f"{sent_path}: no slots were sent to {role}")
        return BROKEN
    answers, revisit = parse_answers(role, sent, slots_of(loaded, role))
    for one in revisit:
        for reason in one.reasons:
            print(f"{one.role} {one.where}: {reason}")
    print(f"{path}: {len(answers)} answered, {len(revisit)} the fold would refuse")
    return BROKEN if revisit else OK


def main() -> int:
    """Check one copy or one batch of answers, and say what the fold would refuse.

    Returns:
        `OK` when nothing would be refused or sent back; `BROKEN` when
        something would, each named on stdout; `UNREADABLE` when the file is
        not a JSON object or list, or the binder is not a binder.
    """
    ap = argparse.ArgumentParser(description=__doc__)
    what = ap.add_mutually_exclusive_group(required=True)
    what.add_argument("--edit-copy", metavar="PATH", help="a role's copy, as it stands")
    what.add_argument(
        "--contract",
        action="store_true",
        help="print the three shapes a role is handed, generated from the code",
    )
    what.add_argument(
        "--answers", metavar="PATH", help="a role's answered batch slots, as a list"
    )
    ap.add_argument("--role", help="whose answers these are (with --answers)")
    ap.add_argument(
        "--sent", metavar="PATH", help="the batch that went out (with --answers)"
    )
    ap.add_argument(
        "--binder",
        help="the binder the copy was seeded from; adds source verification and drift",
    )
    ap.add_argument(
        "--repo",
        help="the checkout a `sources` cite resolves against "
        "(default: the binder's own read_from.root)",
    )
    args = ap.parse_args()

    if args.contract:
        # ! GENERATED, NEVER HAND-WRITTEN -- T19. The game's first brief typed
        # the contract by hand and got `query` wrong.
        print(json.dumps(contracts(), indent=2))
        return OK
    if args.answers:
        if not args.role or not args.sent:
            print("check --answers needs --role and --sent", file=sys.stderr)
            return UNREADABLE
        return _check_answers(args.answers, args.sent, args.role)
    return _check_copy(args.edit_copy, args.binder, args.repo)


if __name__ == "__main__":
    sys.exit(main())
