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

from comment_review.desk.answers.table import ANSWERS
from comment_review.desk.collator import Cache, Problem, cited_problems
from comment_review.desk.marks.rules import allowed
from comment_review.desk.proof.answer import (
    Answer,
    CorrectAnswer,
    PatchAnswer,
    Question,
    Rewrite,
    answer_type,
    read_answer,
)
from comment_review.desk.proof.disposition import contract as ruling_contract
from comment_review.desk.proof.mark import QUERY_SHAPES, filled
from comment_review.desk.proof.move import key_of
from comment_review.desk.proof.source import contract as source_contract
from comment_review.differences import CannotCompose, compose

#: What each field of an answer is, in the words an answer's own read
#: checks by. The check asks whether a field is filled and not what it means, so a
#: role handed the names alone has been told half of the contract.
ANSWER_FIELDS = {
    "address": "copied from the slot",
    "anchor": "copied from the slot",
    "to": "copied from the slot where it carries one -- a placement slot's"
    " destination; absent on the others",
    "instruction": "one of the answers this question admits",
    "reason": "owed, prose",
    "change": "the whole updated paragraph as raw text; owed by the answers"
    " `owes_change` names and absent for the others",
    "claim": "the keys `claim` names for this answer, each filled",
    "sources": "the evidence, each `{cite, verbatim}`, resolved against the tree"
    " the slot was read from; at least one is owed by the answers"
    " `owes_sources` names",
}

#: The field whose value is itself a closed set, and that set. The mark's own
#: contract publishes the same one under the same name (`desk.marks.rules.
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

    A role may answer one slot several times (`decision-log.md Process: #308`).
    Each answer is read and its sources verified on its own; rewrites compose
    into one `correct` or `patch` by `differences.compose`, repeats of one
    other answer collapse, and the slot is refused, with no answer, where the
    answers contradict each other (`_one_answer`).

    Args:
        role: whose answers these are.
        sent: slot key -> the slot that went out there (`slot_key`),
            carrying `question` and, where the caller has one, `anchor`, and
            the `raw_text` and `sides` that several rewrites compose against.
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
    answered: dict[str, list[tuple[int, dict]]] = {}
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
        answered.setdefault(address, []).append((i, entry))

    out: dict[str, Answer] = {}
    for address, slot in sent.items():
        entries = [
            (i, entry)
            for i, entry in answered.get(address, [])
            if filled(entry.get("instruction"))
        ]
        if not entries:
            problems.append(Problem(role, address, "unanswered"))
            continue
        read: list[tuple[int, Answer]] = []
        refused: list[Problem] = []
        for i, entry in entries:
            answer, why = _read_one(address, slot, entry, root, cache)
            if answer is None:
                refused += [Problem(role, address, one) for one in why]
            else:
                read.append((i, answer))
        if refused:
            problems += refused
            continue
        answer, contradiction = _one_answer(role, slot, read)
        if answer is None:
            problems.append(Problem(role, address, contradiction))
            continue
        out[address] = answer
    return out, problems


def _read_one(
    address: str, slot: dict, entry: dict, root: Path, cache: Cache
) -> tuple[Answer | None, list[str]]:
    """One entry read against its slot and its sources verified, or the reasons.

    Each reason has the address taken off its front: the `Problem` it goes on
    carries the location in its own two fields.
    """
    answer, why = read_answer(
        address,
        {
            **entry,
            "question": slot.get("question"),
            "anchor": entry.get("anchor") or slot.get("anchor", ""),
        },
    )
    if answer is not None:
        why = cited_problems(address, answer.sources, root, cache)
    return (None if why else answer), [one.removeprefix(f"{address}: ") for one in why]


def _one_answer(
    role: str, slot: dict, read: list[tuple[int, Answer]]
) -> tuple[Answer | None, str]:
    """Several answers a role gave at one slot, as the one answer they compose to.

    Rewrites compose against the text the role was asked about: at an
    escalation its own side, which a single rewrite there replaces, and
    otherwise the slot's `raw_text`. Repeats of one other answer with one
    claim collapse to the first. Anything else -- rewrites whose edits meet,
    two different answers beside each other, or repeats whose claims differ --
    is a contradiction, and nothing is answered.

    Returns:
        `(answer, "")`, or `(None, the contradiction)`.
    """
    if len(read) == 1:
        return read[0][1], ""
    names = sorted({answer.name for _, answer in read})
    rewrites = [(i, answer) for i, answer in read if isinstance(answer, Rewrite)]
    if len(rewrites) < len(read):
        if len(names) > 1:
            return None, f"{' and '.join(names)} contradict each other at one slot"
        # A repeat says the same thing only when its claim does; its reason
        # and sources may differ without changing the answer.
        claims = [answer.serialize()["claim"] for _, answer in read]
        if any(claim != claims[0] for claim in claims):
            return None, f"two {names[0]} answers at one slot say different things"
        return read[0][1], ""
    base = str(slot.get("raw_text") or "")
    if slot.get("question") == str(Question.ESCALATION):
        sides = slot.get("sides")
        if isinstance(sides, dict) and role in sides:
            base = str(sides[role])
    try:
        change = compose(base, {f"answer {i}": one.change for i, one in rewrites})
    except CannotCompose as refused:
        return None, f"the rewrites contradict each other: {refused}"
    cited = [source for _, one in rewrites for source in one.sources]
    kind = CorrectAnswer if "correct" in names else PatchAnswer
    first = rewrites[0][1]
    return (
        kind(
            address=first.address,
            anchor=first.anchor,
            question=first.question,
            reason="; ".join(one.reason for _, one in rewrites),
            sources=tuple(s for i, s in enumerate(cited) if s not in cited[:i]),
            change=change,
        ),
        "",
    )


def contracts() -> dict:
    """The shapes a role is handed, generated from the tables, never hand-typed.

    A stage-4c `Mark`, from the marks table, and one entry per question a turn
    asks, from the answers table and each answer's type -- the same facts an
    answer's own read holds it to, so the contract cannot say a thing the
    check does not.
    `commands/check.py --contract` prints them; publishing them in the brief is
    the agents lane's.

    ! GENERATED BECAUSE A HAND-TYPED ONE WAS WRONG. The game's first brief
    typed the contract by hand and got `query` wrong, which cost a turn.

    !! IT PUBLISHES EVERY KEY THE PARSE READS, AND THAT IS THE WHOLE POINT.
    `claim` is derived from each type's `claim_all`, so an answer whose effect
    turns on a claim key -- a `query`'s `shape`, which decides whether the
    place is held for a person -- is handed to the role that must write it. A
    contract naming an answer without naming what it owes has published half
    a rule, and the half it leaves out is the one a role cannot guess.

    Returns:
        `stage_4c_mark` -> the mark's own shape; `chief` -> the chief's
        rulings, from `desk.proof.disposition.contract`; one entry per question,
        naming the answers that question admits, which of them owe a `change`
        and which a source, the `claim` keys each owes, the closed value
        sets, and what each field is. An answer owing no claim keys carries an
        empty list, so a reader can tell "none" from "not published".
    """
    out: dict = {"stage_4c_mark": allowed(), "chief": ruling_contract()}
    for question in Question:
        kinds = {
            name: kind
            for (asked, name) in ANSWERS
            if asked is question and (kind := answer_type(name)) is not None
        }
        claims = {name: list(kind.claim_all) for name, kind in kinds.items()}
        named = {key for keys in claims.values() for key in keys}
        out[str(question)] = {
            "instruction": sorted(kinds),
            "owes_change": sorted(
                name for name, kind in kinds.items() if kind.owes_change
            ),
            "owes_sources": sorted(
                name for name, kind in kinds.items() if kind.owes_sources
            ),
            "claim": claims,
            "values": {
                key: value for key, value in ANSWER_VALUES.items() if key in named
            },
            "fields": ANSWER_FIELDS,
            "source_keys": source_contract(),
        }
    return out
