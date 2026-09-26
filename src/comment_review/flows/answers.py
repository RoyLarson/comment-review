"""One role's answers to a turn, read against the slots that went out to it.

    slots_of(loaded, role)                -> the slots, whatever shape they came in
    slot_key(entry)                       -> which slot an entry answers
    answers_of(role, sent, returned, why) -> (slot key -> Answer, the problems)
    contracts()                           -> the shapes a role is handed

`flows.bus` derives what a role was asked from the places the proof carries;
`commands/check.py` reads the same question off the batch that went out. Both
answer one role's file through `answers_of`, so a file the check passes is a
file the turn takes, and a refusal has one wording.

The sent slot carries the question and the returned one never does: an
`Answer` belongs to one of three questions and a role writes none of them. A
returned entry contributes its answer fields alone; the question comes from
the place the turn is asking about, or from the slot the batch sent, which is
the same question written down twice.
"""

from collections.abc import Callable
from pathlib import Path

from comment_review.desk.answers.answer import Answer, Question
from comment_review.desk.answers.table import ANSWERS
from comment_review.desk.collator import Cache, Problem, cited_problems
from comment_review.desk.evaluate.move import key_of
from comment_review.desk.marks.mark import QUERY_SHAPES, allowed, filled

#: What each field of an answer is, in the words `Answer.deserialize` checks
#: by. The parse asks whether a field is filled and not what it means, so a
#: role handed the names alone has been told half of the contract.
ANSWER_FIELDS = {
    "address": "copied from the slot",
    "anchor": "copied from the slot",
    "instruction": "one of the answers this question admits",
    "reason": "owed, prose",
    "change": "the whole updated paragraph as raw text; owed by the answers"
    " `owes_change` names and absent for the others",
    "claim": "the keys `claim` names for this answer, each filled",
    "sources": "the evidence, each `{cite, verbatim}`, resolved against the tree"
    " the slot was read from",
}

#: The field whose value is itself a closed set, and that set. The mark's own
#: contract publishes the same one under the same name (`desk.marks.mark.
#: allowed`), and both read `QUERY_SHAPES` rather than spelling it twice.
ANSWER_VALUES = {"shape": [str(one) for one in QUERY_SHAPES]}


def slot_key(entry: dict) -> str:
    """Which slot an entry answers: its address, or its move where it names one.

    A placement is asked of a move, at its origin's address, so a role can be
    asked a placement and a composition at one address in one turn. The move
    slot carries `to`, and the two are told apart by it.
    """
    address = str(entry.get("address") or "")
    to = entry.get("to")
    return key_of(address, str(to)) if address and to else address


def slots_of(loaded: object, role: str) -> list:
    """A role's slots, from any of the shapes a role has handed back.

    Measured 2026-09-04: three of four roles returned `{role: [slots]}`, the
    batch's own shape, on the first turn they were asked. It is that role's
    slots, and this reads it as such rather than refusing the envelope.

    Args:
        loaded: the file as JSON -- a list of slots, `{role: [slots]}`, or a
            lone slot.
        role: whose answers these are, for the keyed shape.

    Returns:
        The slots, or an empty list where the value is none of the three.
    """
    if isinstance(loaded, dict):
        # Declared, not narrowed -- `ty` loses an isinstance narrow at the
        # subscript, the same reason `EditCopy.deserialize` gives.
        data: dict = loaded
        if role in data:
            slots = data[role]
            return list(slots) if isinstance(slots, list) else []
        if "address" in data:
            return [data]
    return list(loaded) if isinstance(loaded, list) else []


def answers_of(
    role: str,
    sent: dict[str, dict],
    returned: list,
    unsent: Callable[[str], str],
    root: Path,
    cache: Cache,
) -> tuple[dict[str, Answer], list[Problem]]:
    """One role's answers, paired to the slots it was sent, or the problems.

    Every sent slot contributes to exactly one of the two: an `Answer` at its
    address, or a `Problem`. An unanswered slot is refused by name and never
    read as a withdrawal -- the null answer must be written by a hand
    (`decision-log.md Process: #22`). A slot handed back as it was sent,
    carrying no instruction, is unanswered as surely as one never returned.

    Args:
        role: whose answers these are.
        sent: slot key -> the slot that went out there (`slot_key`),
            carrying `question` and, where the caller has one, `anchor`.
        returned: the entries as they came back, through `slots_of`.
        unsent: given an address outside `sent`, the reason an entry there is
            refused. Only the caller knows why the address is not this role's
            to answer, so only the caller can word it.
        root: the checkout each answer's `cite` is resolved against. An
            answer's evidence is verified as a mark's is
            (`decision-log.md Process: #181`), by the same checks.
        cache: path -> lines, shared across the roles of one turn so a file
            several answers cite is read once.

    Returns:
        `(slot key -> Answer, the problems)`, the problems in slot order after
        the entries that named no slot.
    """
    answered: dict[str, dict] = {}
    problems: list[Problem] = []
    for i, entry in enumerate(returned, 1):
        if not isinstance(entry, dict):
            problems.append(Problem(role, "", f"answer {i} is not an object"))
            continue
        address = slot_key(entry)
        if not address:
            problems.append(Problem(role, "", f"answer {i} names no address"))
            continue
        if address not in sent:
            problems.append(Problem(role, address, unsent(address)))
            continue
        answered[address] = entry

    out: dict[str, Answer] = {}
    for address, slot in sent.items():
        entry = answered.get(address)
        if entry is None or not filled(entry.get("instruction")):
            problems.append(Problem(role, address, "unanswered"))
            continue
        answer, why = Answer.deserialize(
            address,
            {
                **entry,
                "question": slot.get("question"),
                "anchor": entry.get("anchor") or slot.get("anchor", ""),
            },
        )
        if answer is None:
            # The location is the `Problem`'s own two fields, so it is taken
            # off the front of each reason rather than printed twice.
            problems += [
                Problem(role, address, one.removeprefix(f"{address}: ")) for one in why
            ]
            continue
        cited = [
            Problem(role, address, one.removeprefix(f"{address}: "))
            for one in cited_problems(address, answer.sources, root, cache)
        ]
        if cited:
            problems += cited
            continue
        out[address] = answer
    return out, problems


def contracts() -> dict:
    """The shapes a role is handed, generated from the tables, never hand-typed.

    A stage-4c `Mark`, from the marks table, and one entry per question a turn
    asks, from the answers table -- the same rows `Answer.deserialize` reads an
    answer against, so the contract cannot say a thing the parse does not.
    `commands/check.py --contract` prints them; publishing them in the brief is
    the agents lane's.

    ! GENERATED BECAUSE A HAND-TYPED ONE WAS WRONG. The game's first brief
    typed the contract by hand and got `query` wrong, which cost a turn.

    !! IT PUBLISHES EVERY KEY THE PARSE READS, AND THAT IS THE WHOLE POINT.
    `claim` is derived from each row's `claim_all`, so an answer whose effect
    turns on a claim key -- a `query`'s `shape`, which decides whether the
    place is held for a person -- is handed to the role that must write it. A
    contract naming an answer without naming what it owes has published half
    a rule, and the half it leaves out is the one a role cannot guess.

    Returns:
        `stage_4c_mark` -> the mark's own shape; one entry per question,
        naming the answers that question admits, which of them owe a `change`,
        the `claim` keys each owes, the closed value sets, and what each field
        is. An answer owing no claim keys carries an empty list, so a reader
        can tell "none" from "not published".
    """
    out: dict = {"stage_4c_mark": allowed()}
    for question in Question:
        rows = {
            name: row for (asked, name), row in ANSWERS.items() if asked is question
        }
        claims = {name: list(row.claim_all) for name, row in rows.items()}
        named = {key for keys in claims.values() for key in keys}
        out[str(question)] = {
            "instruction": sorted(rows),
            "owes_change": sorted(
                name for name, row in rows.items() if row.owes_change
            ),
            "claim": claims,
            "values": {
                key: value for key, value in ANSWER_VALUES.items() if key in named
            },
            "fields": ANSWER_FIELDS,
        }
    return out
