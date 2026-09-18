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
verification, drift, and whether each address and each move's destination
names a place its page carries (`desk.collator.verify_report`, `drift_in`,
`flows.collate.resolution_problems` -- the fold's own). For a
BATCH: `flows.answers.answers_of`, the call the turn makes for each role --
every answer paired to the slot that went out at its address, and read against
that slot's own question. So `--sent` is the batch that went out, whose slots
name the checkout their citations resolve against; nothing is saved. A slot left
unanswered, an answer at an address the batch never sent this role, an answer
the question does not admit, and a `cite` that does not resolve are each named
here, which is what the turn refuses the round for.
The shape a role hands back is read the way the fold reads it
(`flows.answers.slots_of`): a list of slots, `{role: [slots]}`, or a lone slot.
"""

import argparse
import json
import sys
from pathlib import Path

from comment_review.desk.collator import (
    Cache,
    Problem,
    base_texts,
    drift_in,
    verify_report,
)
from comment_review.desk.containers import EditCopy
from comment_review.flows._collate import resolution_problems, texts_at
from comment_review.flows._turn import contracts
from comment_review.flows.answers import answers_of, slots_of
from comment_review.flows.fill import (
    composition_problems,
    page_text_at,
    row_problems,
)
from comment_review.flows.mark_errors import mark_errors
from comment_review.flows.proof_io import (
    load_batch,
    load_binder,
    load_copy,
    load_value,
)

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


def _row_problems(
    copy: EditCopy, loaded: dict, texts: dict, root: Path
) -> list[Problem]:
    """What each mark's own row finds against the pages -- `mark`'s own check.

    It is the same call `flows.fill` makes, over a whole copy. A role may
    write its copy with its file-write tool rather than placing each ruling
    through `mark`, and the rows are what decide a `move`'s snippet and an
    `add`'s paragraph (`decision-log.md Process: #172`, `#175`, `#176`), so
    a hand-written copy is held to what `mark` enforces on the way in.

    Args:
        copy: one parsed edit_copy.
        loaded: the same copy as its wire dict, which `place_on_the_page`
            reads a sheet off for a place no mark's own address names.
        texts: `flows._collate.texts_at`'s map, whose first text at each
            address is the page's own -- already read once for the stage.
        root: the checkout every page is read from.

    Returns:
        One `Problem` per finding, in sheet then mark order.
    """
    bases = {address: held[0] for address, held in texts.items()}

    def base_at(address: str) -> str:
        if address not in bases:
            bases[address] = page_text_at([loaded], address, root)
        return bases[address]

    out = [
        Problem(copy.role, mark.address, why)
        for sheet in copy.sheets
        for mark in sheet.marks
        for why in row_problems(mark, base_at)
    ]
    # And what this role's own marks make of each other: two at one place
    # compose or are refused back to it (`decision-log.md Process: #179`),
    # which `mark` asks of one ruling as it is placed and this asks of the
    # copy as it stands.
    marks = [mark for sheet in copy.sheets for mark in sheet.marks]
    return out + [
        Problem(copy.role, address, why)
        for address, why in composition_problems(copy.role, marks, base_at)
    ]


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
        paths = [page.path for page in binder.pages]
        texts = texts_at(copy, paths, root, {})
        for problem in (
            *verify_report(copy, texts, root, cache),
            *drift_in(copy, base_texts(binder)),
            *resolution_problems(copy, paths, root, {}),
            *_row_problems(copy, loaded, texts, root),
        ):
            print(
                f"{problem.role} {problem.address or '(the copy)'}: {problem.message}"
            )
            found += 1
    print(f"{path}: {found} thing(s) the fold would send back")
    return BROKEN if found else OK


def _never_sent(address: str) -> str:
    """Why an answer at an address outside the batch is refused, for `answers_of`.

    The batch is all this command reads, so it can say only that the address
    is not among the slots this role was handed. The turn, which has the
    places in hand, says which of the two it is -- a place nothing carries
    forward, or one put to other roles.
    """
    return "never sent to this role"


def _root_of(repo: str | None, sent: dict[str, dict]) -> Path:
    """The checkout an answer's citations resolve against.

    A slot carries the tree the copies were read from, as an edit_copy and a
    master proof do, so a role checking its answers names no tree of its own.
    `--repo` still wins, and a batch written before a slot carried one leaves
    the directory this is run from.

    Args:
        repo: what `--repo` said, or None.
        sent: the slots this role was handed, by address.

    Returns:
        The root, which is what every `cite` is resolved against.
    """
    if repo:
        return Path(repo)
    for slot in sent.values():
        read_from = slot.get("read_from")
        if isinstance(read_from, dict) and read_from.get("root"):
            return Path(str(read_from["root"]))
    return Path(".")


def _check_answers(path: str, sent_path: str, role: str, repo: str | None) -> int:
    loaded, why = load_value(Path(path))
    if why:
        return _refused(why)
    batch, why = load_batch(Path(sent_path))
    if why:
        return _refused(why)
    slots = slots_of(batch, role)
    if not slots:
        print(f"{sent_path}: no slots were sent to {role}")
        return BROKEN
    sent = {
        str(slot["address"]): slot
        for slot in slots
        if isinstance(slot, dict) and slot.get("address")
    }
    cache: Cache = {}
    answers, problems = answers_of(
        role, sent, slots_of(loaded, role), _never_sent, _root_of(repo, sent), cache
    )
    for one in problems:
        print(f"{one.role} {one.address or '(the batch)'}: {one.message}")
    print(f"{path}: {len(answers)} answered, {len(problems)} the fold would refuse")
    return BROKEN if problems else OK


def main() -> int:
    """Check one copy or one batch of answers, and say what the fold would refuse.

    Returns:
        `OK` when nothing would be refused or sent back; `BROKEN` when
        something would, each named on stdout; `UNREADABLE` when the file is
        not a JSON object or list, or the binder or the batch is not one.
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
        help="the checkout a `sources` cite resolves against -- with --binder"
        " the binder's own read_from.root by default, and with --answers the"
        " one the sent slots name",
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
        return _check_answers(args.answers, args.sent, args.role, args.repo)
    return _check_copy(args.edit_copy, args.binder, args.repo)


if __name__ == "__main__":
    sys.exit(main())
