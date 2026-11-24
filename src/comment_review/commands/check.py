"""The `check` command: what the fold would refuse, named before a role returns it.

    comment_review check --edit-copy copy.json --binder B.json [--repo R]
        [--human answers.toml]
    comment_review check --answers answers.json --sent batch.json --role block-context
        [--human answers.toml]
    comment_review check --contract

A role fills its copy with `mark` or its file-write tool, or writes its batch
answers with its file-write tool, and runs this over the file. It is the same
boundaries the fold runs -- nothing here decides anything the fold would not
-- so a run that exits 0 here is a file the fold reads whole, but for the
three questions below whose inputs this is not given.

!! It checks and does not write. A role places each ruling with `mark`, which
reads any multi-line value from an `@path` file, or writes the copy with its
file-write tool; either way this is the check run over the result.

For a copy: the envelope (`EditCopy.deserialize`), then `flows.verify.admit`
-- the one admission `collate` runs, and its trial fold -- given the copy, its
received binder and the human's answers. Every rule whose input those hold is
asked as `collate` asks it: each page's sha and reading against the binder's,
source verification, whether each address and each move's destination names a
place its page carries, every place the binder deals the role left unruled or
wrote unreadably, coverage, the gathered tree, the instructions the copy's own
`admits` names, and what the fold makes of the marks at each place. It is not
given the stage label, so a copy's own `stage` is not compared with the stage
it is folded in; nor the topology row, so the copy's `admits` is not held to
the row's and the dispatches owed are not counted; nor the other copies of the
stage, so received binders are not compared with each other. `collate` asks
all three.

For a batch: `flows.answers.answers_of`, the call the turn makes for each
role -- every answer paired to the slot that went out at its address, and read against
that slot's own question. So `--sent` is the batch that went out, whose slots
name the checkout their citations resolve against; nothing is saved. A slot left
unanswered, an answer at an address the batch never sent this role, an answer
the question does not admit, and a `cite` that does not resolve are each named
here, which is what the turn refuses the round for.
The shape a role hands back is read the way the fold reads it
(`flows.answers.slots_of`): a list of slots, `{role: [slots]}`, or a lone slot.

In either mode a human question -- a `human-review-necessary` query, filed as
a mark or given as an answer -- is named and counted apart from what the fold
would send back. The reader here is the role that filed it, which cannot ask the
human, so an unanswered one tells it its part is done; where the human questions
are the only findings the exit is `ASKS_THE_HUMAN`, as `collate` and `turn` exit,
and not `BROKEN`, which would invite the role to turn a real question into a
clean. `--human` names the human's answers file; a question it answers is printed
with the answer, as `collate` prints it.

A mark that changes the file's matter, an `f` place, or moves text into one
is counted with the human questions too
(`flows.human.corrections_to_matter`): each waits on the human's approval,
and one the `--human` file answers is not counted.
"""

import argparse
import json
import sys
from pathlib import Path

from comment_review.commands.report import (
    ASKS_THE_HUMAN,
    BROKEN,
    OK,
    UNREADABLE,
    human_answers,
    lines,
    refused,
)
from comment_review.desk.collator import Cache
from comment_review.desk.proof.edit_copy import EditCopy
from comment_review.desk.report import AsksTheHuman, refusal_line
from comment_review.flows.answers import answers_of, contracts, slot_key, slots_of
from comment_review.flows.human import (
    HumanAnswer,
    HumanQuery,
    answered,
    corrections_in_answers,
    queries_in_answers,
)
from comment_review.flows.proof_io import (
    load_batch,
    load_binder,
    load_copy,
    load_value,
)
from comment_review.flows.verify import admit


def _for_the_role(query: HumanQuery) -> str:
    """An unanswered human question, as the role that filed it reads it.

    `collate` and `turn` print the same question for the task agent, whose
    part is to ask it and record the answer (`commands.report.lines`). The
    reader of `check` is the role, which cannot ask the human: its part ends
    at filing the question, so this line says so rather than handing it the
    task agent's instruction.
    """
    return (
        f"asks the human {query.at}: {query.role} -- {query.question}; this is the"
        " role's part done -- hand the copy back, and the task agent asks it"
    )


def _asks_the_human(asks: list[tuple[HumanQuery, HumanAnswer | None]]) -> int:
    """Each human question, printed for the role, and how many there were.

    The stage or the turn rolls back on each one. An unanswered one is the
    role's part done (`_for_the_role`); an answered one is printed as `collate`
    prints it, which is addressed to the role -- it replaces its query with its
    mark or answer.
    """
    for query, answer in asks:
        if answer is None:
            print(_for_the_role(query))
            continue
        event = AsksTheHuman(query.role, query.at, query.question, answer.answer)
        for line in lines(event):
            print(line)
    return len(asks)


def _exit(found: int, asked: int) -> int:
    """The exit code for what was found and how many human questions were asked.

    `BROKEN` where anything but a human question was found, `ASKS_THE_HUMAN`
    where only human questions were, and `OK` where nothing was.
    """
    if found:
        return BROKEN
    return ASKS_THE_HUMAN if asked else OK


def _check_copy(
    path: str,
    binder_path: str | None,
    repo: str | None,
    human: tuple[HumanAnswer, ...] = (),
) -> int:
    loaded, why = load_copy(Path(path))
    if why:
        return refused(why)
    copy, problems = EditCopy.deserialize(path, loaded)
    if copy is None:
        for line in problems:
            print(line)
        return BROKEN
    if not binder_path:
        return refused(["check --edit-copy needs --binder to check required rulings"])
    binder, why = load_binder(Path(binder_path))
    if binder is None:
        return refused(why)
    root = Path(repo) if repo else binder.root
    admission = admit([copy], root, binder=binder, human=human)
    if admission.unadmitted:
        return refused(
            [
                refusal_line(one.role, "(the copy)", one.message)
                for one in admission.unadmitted
            ]
        )
    for one in admission.problems:
        print(refusal_line(one.role, one.address or "(the copy)", one.message))
    asked = _asks_the_human(admission.asks)
    asked += _asks_the_human([(one, None) for one in admission.approvals])
    found = len(admission.problems)
    print(
        f"{path}: {found} thing(s) the fold would send back, {asked} question(s)"
        " for the human"
    )
    return _exit(found, asked)


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


def _check_answers(
    path: str,
    sent_path: str,
    role: str,
    repo: str | None,
    human: tuple[HumanAnswer, ...] = (),
) -> int:
    loaded, why = load_value(Path(path))
    if why:
        return refused(why)
    batch, why = load_batch(Path(sent_path))
    if why:
        return refused(why)
    slots = slots_of(batch, role)
    if not slots:
        print(f"{sent_path}: no slots were sent to {role}")
        return BROKEN
    sent = {
        slot_key(slot): slot
        for slot in slots
        if isinstance(slot, dict) and slot.get("address")
    }
    cache: Cache = {}
    answers, problems = answers_of(
        role, sent, slots_of(loaded, role), _never_sent, _root_of(repo, sent), cache
    )
    for one in problems:
        where = one.address or "(the batch)"
        print(refusal_line(one.role, where, one.message))
    given = {role: answers}
    asked = _asks_the_human(answered(queries_in_answers(given), list(human)))
    # As the turn asks them: `corrections_in_answers` already left out the answered.
    asked += _asks_the_human(
        [(query, None) for query in corrections_in_answers(given, human)]
    )
    print(
        f"{path}: {len(answers)} answered, {len(problems)} the fold would refuse,"
        f" {asked} question(s) for the human"
    )
    return _exit(len(problems), asked)


def main() -> int:
    """Check one copy or one batch of answers, and say what the fold would refuse.

    Returns:
        `OK` when nothing would be refused or sent back; `BROKEN` when
        something would, each named on stdout; `ASKS_THE_HUMAN` when the only
        findings are human questions, each named on stdout -- the role's part
        is done; `UNREADABLE` when the file is not a JSON object or list, or
        the binder or the batch is not one, or the mode is missing a
        flag it needs (`--binder`, or `--role` and `--sent`).
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
        help="the received binder defining required rulings "
        "(required with --edit-copy)",
    )
    ap.add_argument(
        "--repo",
        help="the checkout a `sources` cite resolves against -- with --binder"
        " the binder's own read_from.root by default, and with --answers the"
        " one the sent slots name",
    )
    ap.add_argument(
        "--human",
        metavar="PATH",
        help="the human's answers file, TOML, one [[answer]] per question"
        " (Process 198); with it, a human question it answers is named with"
        " the answer",
    )
    args = ap.parse_args()

    if args.contract:
        # ! Generated from `contracts()`, never hand-written: a contract typed
        # by hand can disagree with the tables the checks read.
        print(json.dumps(contracts(), indent=2))
        return OK
    human, why = human_answers(args.human)
    if why:
        return refused(why)
    if args.answers:
        if not args.role or not args.sent:
            print("check --answers needs --role and --sent", file=sys.stderr)
            return UNREADABLE
        return _check_answers(args.answers, args.sent, args.role, args.repo, human)
    return _check_copy(args.edit_copy, args.binder, args.repo, human)


if __name__ == "__main__":
    sys.exit(main())
