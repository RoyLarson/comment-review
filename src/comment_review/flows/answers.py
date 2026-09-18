"""One role's answers to a turn, read against the slots that went out to it.

    slots_of(loaded, role)                -> the slots, whatever shape they came in
    answers_of(role, sent, returned, why) -> (address -> Answer, the problems)

`flows.bus` derives what a role was asked from the places the proof carries;
`commands/check.py` reads the same question off the batch that went out. Both
answer one role's file through `answers_of`, so a file the check passes is a
file the turn takes, and a refusal has one wording.

! THE SENT SLOT CARRIES THE QUESTION, NEVER THE RETURNED ONE -- `Answer`
belongs to one of two questions and a role writes neither. A returned entry
contributes its answer fields alone; the question comes from the place the
turn is asking about, or from the slot the batch sent, which is the same
question written down twice.
"""

from collections.abc import Callable

from comment_review.desk.answers.answer import Answer
from comment_review.desk.collator import Problem
from comment_review.desk.marks.mark import filled


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
) -> tuple[dict[str, Answer], list[Problem]]:
    """One role's answers, paired to the slots it was sent, or the problems.

    Every sent slot contributes to exactly one of the two: an `Answer` at its
    address, or a `Problem`. An unanswered slot is refused by name and never
    read as a withdrawal -- the null answer must be written by a hand
    (`decision-log.md Process: #22`). A slot handed back as it was sent,
    carrying no instruction, is unanswered as surely as one never returned.

    Args:
        role: whose answers these are.
        sent: address -> the slot that went out there, carrying `question`
            and, where the caller has one, `anchor`.
        returned: the entries as they came back, through `slots_of`.
        unsent: given an address outside `sent`, the reason an entry there is
            refused. Only the caller knows why the address is not this role's
            to answer, so only the caller can word it.

    Returns:
        `(address -> Answer, the problems)`, the problems in slot order after
        the entries that named no slot.
    """
    answered: dict[str, dict] = {}
    problems: list[Problem] = []
    for i, entry in enumerate(returned, 1):
        if not isinstance(entry, dict):
            problems.append(Problem(role, "", f"answer {i} is not an object"))
            continue
        address = str(entry.get("address") or "")
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
        out[address] = answer
    return out, problems
