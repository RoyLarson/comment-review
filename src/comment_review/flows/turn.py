"""A PROTOTYPE. The turn: a batch answered, applied to the copies, folded again.

    parse_answers(role, sent, returned) -> (answers, problems)
    apply(copies, role, answers) -> problems
    run_turn(stage, copies, binder, root, sent, answers, turn) -> (Collated, problems)
    rule_at_cap(collated, address, answer, side, reason, turn, prose) -> Determined
    determined_chief(collated, rulings) -> (every Determined, the chief's edit_copy)

!! NOTHING WIRES THIS INTO A COMMAND YET. `docs/the-turn.md` is the source for
what a turn is. This is P17 (the recollate), T20 (the counter -- every
`Determined` carries the turn it landed on, and the caller keeps one record
per turn), T21 (the batch seeded by question, `desk.diff_mark.batch_of`) and
T24 (the chief's copy derived from the Determineds,
`flows.collate._chief_copy`) of `TODO/a-revise-answer-has-no-artifact.md`,
built together so the loop can be run end to end.

=== A DiffMark DOES NOT BECOME A Mark -- `Process: #86`

The collator compares copies, not marks, so applying a role's answer to an
ESCALATION is an edit to that role's copy at the address:

    hold        nothing
    withdraw    the entry becomes a `clean`
    correct     the entry's `change` becomes the DiffMark's `change`
    patch       the same

A COMPOSITION re-read is answered with a fresh `Mark` over the composed text
(`#86`), and the answer set is `clean`, `query`, `correct`, `patch`:

    clean       the role ADOPTS the composition -- its entry becomes a
                `correct` whose `change` is the composed text. A role that
                owed no change here stays clean; a `clean` over the BASE, where
                the sides did not compose, is a withdrawal
    query       the entry becomes the query
    correct     the entry becomes a `correct` over the ORIGINAL base whose
                `change` is the role's. `claim.false` quotes the base because
                source verification measures a claim against the binder, not
                against the text the question was asked over
    patch       the entry becomes a `patch` over the base -- NOT a correct,
                which owes sources a patch never carried. `claim.from` is
                the role's where the base holds it, else the whole base

Then `flows.collate.collate` runs again over the copies, and every place that
agreed comes back as a `stet` Determined at this turn (`Process: #87`). What
did not agree is the next turn's batch, until the task agent's cap
(`Process: #78`), where `rule_at_cap` records the chief's `taken_in` or
`recast` and `determined_chief` derives the chief's copy from the whole set.

! THE COPIES ARE MUTATED IN PLACE. They are the wire dicts `collate` was
handed, and the next fold reads them as they now stand -- which is what a
turn IS. The master proof's record of what each turn sent and got back is the
caller's to keep (`MasterProof.turns`); this module returns what it needs.
"""

from pathlib import Path

from comment_review.binder.binder import Binder
from comment_review.desk.containers import EditCopy
from comment_review.desk.determined import CHIEF, ORIGINAL, Answer, Determined
from comment_review.desk.diff_mark import (
    COMPOSITION,
    ESCALATION,
    QUESTION,
    DiffInstruction,
    DiffMark,
    parse_batch,
)
from comment_review.desk.mark import INSTRUCTIONS, Instruction, Mark, filled, untouched
from comment_review.flows.collate import Collated, _chief_copy, collate

#: What a role may answer a composition re-read with -- `Process: #86`.
COMPOSITION_ANSWERS = (
    Instruction.CLEAN,
    Instruction.QUERY,
    Instruction.CORRECT,
    Instruction.PATCH,
)


def slots_of(loaded: object, role: str) -> list:
    """A role's slots, from any of the shapes a role has handed back.

    ! MEASURED 2026-09-04: three of four roles returned `{role: [slots]}`,
    the batch's own shape, on the first turn they were asked. It is that
    role's slots, and the fold reads it as such rather than refusing the
    envelope; so does `commands/check.py`, which is why this lives here.
    """
    if isinstance(loaded, dict):
        # ! DECLARED, NOT NARROWED -- the same reason `EditCopy.deserialize`
        # gives: `ty` loses an isinstance narrow at the subscript.
        data: dict = loaded
        if role in data:
            slots = data[role]
            return list(slots) if isinstance(slots, list) else []
        if "address" in data:
            return [data]
    return list(loaded) if isinstance(loaded, list) else []


def parse_answers(
    role: str, sent: list, returned: list
) -> tuple[list[tuple[str, DiffMark | Mark]], list[str]]:
    """One role's answered batch, each answer paired to the slot the flow SENT.

    !! THE SENT SLOT IS THE AUTHORITY -- T27. MEASURED in the game's hand 1: a
    role rewrote its slot without the `question` key and the fold refused it.
    The flow handed the slot out, so it knows the question at every address;
    a returned slot contributes its answer fields and nothing else -- the
    answer is the sent slot with the returned fields laid over it.

    Args:
        role: whose batch this is.
        sent: the slots `batch_of` handed this role.
        returned: the slots as they came back, already through `slots_of`.

    Returns:
        `(answers, problems)`. Every SENT slot contributes to exactly one: an
        `(address, DiffMark | Mark)` pair, or one or more named problems. An
        unanswered slot -- never returned, or returned untouched -- is refused
        by name, never read as a withdrawal or a clean. A returned slot at an
        address this role was never sent is a problem of its own.
    """
    by_address = {
        slot["address"]: slot
        for slot in sent
        if isinstance(slot, dict) and filled(slot.get("address"))
    }
    answered: dict[str, dict] = {}
    problems: list[str] = []
    for i, slot in enumerate(returned, 1):
        if not isinstance(slot, dict):
            problems.append(f"{role} slot {i}: a slot must be an object")
            continue
        address = slot.get("address")
        if not filled(address):
            problems.append(f"{role} slot {i}: names no address")
            continue
        if address not in by_address:
            problems.append(f"{role} {address}: never sent to this role -- refused")
            continue
        answered[address] = slot

    answers: list[tuple[str, DiffMark | Mark]] = []
    for address, slot in by_address.items():
        loc = f"{role} {address}"
        got = answered.get(address)
        entry = {**slot, **(got or {})}
        if got is None or untouched(entry):
            problems.append(f"{loc}: unanswered -- refused, not read as a withdrawal")
            continue
        question = slot.get(QUESTION)
        if question == ESCALATION:
            marks, why = parse_batch(role, [entry])
            problems += why
            answers += [(mark.address, mark) for mark in marks]
        elif question == COMPOSITION:
            mark, why = Mark.deserialize(loc, entry)
            if mark is None:
                problems += why
                continue
            if mark.instruction not in COMPOSITION_ANSWERS:
                problems.append(
                    f"{loc}: `{mark.instruction}` is not a composition answer -- "
                    f"one of {', '.join(COMPOSITION_ANSWERS)} (Process 86)"
                )
                continue
            answers.append((mark.address, mark))
        else:
            problems.append(f"{loc}: the sent slot names no question")
    return answers, problems


def _entry_at(copies: list[dict], role: str, address: str) -> dict | None:
    """The slot on `role`'s copy at `address`, the dict object itself."""
    for copy in copies:
        if not isinstance(copy, dict) or copy.get("role") != role:
            continue
        for sheet in copy.get("sheets", []):
            if not isinstance(sheet, dict):
                continue
            for entry in sheet.get("marks", []):
                if isinstance(entry, dict) and entry.get("address") == address:
                    return entry
    return None


def _becomes(entry: dict, new: dict) -> None:
    """Replace the slot's contents in place -- the sheet holds this dict object."""
    entry.clear()
    entry.update(new)


def _a_clean(entry: dict) -> dict:
    return {
        **Mark.seed(
            entry["address"], entry.get("anchor", ""), entry.get("raw_text", "")
        ),
        "instruction": str(Instruction.CLEAN),
    }


def _a_correct_over_base(entry: dict, change: str, reason: str, sources: list) -> dict:
    base = entry.get("raw_text", "")
    return {
        **Mark.seed(entry["address"], entry.get("anchor", ""), base),
        "instruction": str(Instruction.CORRECT),
        "claim": {"false": base, "true": change},
        "reason": reason,
        "sources": list(sources),
        "change": change,
    }


def _a_patch_over_base(entry: dict, answer: Mark) -> dict:
    base = entry.get("raw_text", "")
    quoted = answer.claim.get("from") if isinstance(answer.claim, dict) else None
    sentence = quoted if isinstance(quoted, str) and quoted in base else base
    to = answer.claim.get("to") if isinstance(answer.claim, dict) else None
    return {
        **Mark.seed(entry["address"], entry.get("anchor", ""), base),
        "instruction": str(Instruction.PATCH),
        "claim": {"from": sentence, "to": to if filled(to) else answer.change},
        "reason": answer.reason,
        "change": answer.change,
    }


def _owes_change(entry: dict) -> bool:
    named = entry.get("instruction")
    if not isinstance(named, str) or named not in INSTRUCTIONS:
        return False
    return INSTRUCTIONS[Instruction(named)].owes_change


def apply(
    copies: list[dict], role: str, answers: list[tuple[str, DiffMark | Mark]]
) -> list[str]:
    """Write one role's answers into its own copy, per the tables above.

    Args:
        copies: the wire copies `collate` was handed. MUTATED.
        role: whose answers these are.
        answers: `parse_answers`' pairs.

    Returns:
        Problems -- an address this role's copy carries no slot for.
    """
    problems: list[str] = []
    for address, answer in answers:
        entry = _entry_at(copies, role, address)
        if entry is None:
            problems.append(f"{role} {address}: no slot on this role's copy")
            continue
        if isinstance(answer, DiffMark):
            if answer.instruction is DiffInstruction.HOLD:
                continue
            if answer.instruction is DiffInstruction.WITHDRAW:
                _becomes(entry, _a_clean(entry))
                continue
            entry["change"] = answer.change
            claim = entry.get("claim")
            if isinstance(claim, dict):
                for key in ("true", "to"):
                    if key in claim:
                        claim[key] = answer.change
            continue
        sources = entry.get("sources") or []
        if answer.instruction is Instruction.CLEAN:
            adopts = (
                _owes_change(entry)
                and bool(sources)
                and answer.raw_text != entry.get("raw_text", "")
            )
            if adopts:
                _becomes(
                    entry,
                    _a_correct_over_base(
                        entry, answer.raw_text, "adopted the composition", sources
                    ),
                )
            else:
                _becomes(entry, _a_clean(entry))
        elif answer.instruction is Instruction.QUERY:
            _becomes(
                entry, {**answer.serialize(), "raw_text": entry.get("raw_text", "")}
            )
        elif answer.instruction is Instruction.PATCH:
            _becomes(entry, _a_patch_over_base(entry, answer))
        else:
            _becomes(
                entry,
                _a_correct_over_base(
                    entry,
                    answer.change,
                    answer.reason,
                    list(answer.sources) or sources,
                ),
            )
    return problems


def run_turn(
    stage: str,
    copies: list[dict],
    binder: Binder,
    root: Path,
    sent: dict[str, list],
    answers: dict[str, list],
    turn: int,
) -> tuple[Collated, list[str]]:
    """One turn: every role's answers applied, then the fold again.

    Args:
        stage: the label the copies were dispatched under.
        copies: the wire copies as they stand. MUTATED.
        binder: the binder they were seeded from.
        root: the checkout citations resolve against.
        sent: the batch that went out -- role -> its slots, as `batch_of`
            built it. !! THE SENT BATCH DRIVES THE TURN: every role in it owes
            every slot in it, and a role's answers are read against it.
        answers: role -> what came back, in any shape `slots_of` reads.
        turn: this turn's number, from 1. Every `stet` the fold records
            carries it.

    Returns:
        `(Collated, problems)` -- the fold over the copies as they now stand,
        and every slot that was refused, unanswered, never sent, or had no
        home.
    """
    problems: list[str] = []
    for role in answers:
        if role not in sent:
            problems.append(f"{role}: no slots were sent to this role -- refused")
    for role, slots in sent.items():
        parsed, why = parse_answers(role, slots, slots_of(answers.get(role, []), role))
        problems += why
        problems += apply(copies, role, parsed)
    return collate(stage, copies, binder, root, turn=turn), problems


def rule_at_cap(
    collated: Collated,
    address: str,
    answer: Answer,
    side: str,
    reason: str,
    turn: int,
    prose: str = "",
) -> Determined:
    """The chief's own ruling on a place the roles never agreed on.

    Args:
        collated: the last fold -- the place must still be carried forward in
            its `escalations` or `rereads`.
        address: which place.
        answer: `TAKEN_IN` or `RECAST`. `STET` is the program's, not the
            chief's to rule.
        side: for `TAKEN_IN`, the role whose text is taken in, or `ORIGINAL`.
            Ignored for a `RECAST`, whose side is `CHIEF`.
        reason: the chief's, owed.
        turn: the turn the cap fell on.
        prose: for a `RECAST`, the chief's own paragraph as raw text.

    Returns:
        The `Determined`, its `mark` being what the chief's copy will carry:
        the side's mark, None for the original, or a synthesized `correct`
        over the base for a recast, citing every side's sources so it parses
        as an ordinary mark the way `flows.collate._composition`'s does.

    Raises:
        ValueError: the place is not carried forward, the side has no mark
            there, `STET` was asked for, or a recast has no prose.
    """
    entry = next(
        (
            e
            for e in (*collated.escalations, *collated.rereads)
            if e["address"] == address
        ),
        None,
    )
    if entry is None:
        raise ValueError(f"{address} is not carried forward -- nothing to rule on")
    if answer is Answer.STET:
        raise ValueError("stet is the program's: the roles agreed, or they did not")
    marks = entry["marks"]
    if answer is Answer.TAKEN_IN:
        if side == ORIGINAL:
            return Determined(address, answer, turn, ORIGINAL, "cap", reason, None)
        placed = next((p for p in marks if p.role == side), None)
        if placed is None:
            raise ValueError(f"{side} has no mark at {address} to take in")
        return Determined(address, answer, turn, side, "cap", reason, placed.mark)
    if not filled(prose):
        raise ValueError("a recast needs the chief's own prose")
    first = marks[0].mark
    return Determined(
        address,
        answer,
        turn,
        CHIEF,
        "cap",
        reason,
        Mark(
            address=address,
            anchor=first.anchor,
            raw_text=first.raw_text,
            instruction=Instruction.CORRECT,
            claim={"false": first.raw_text, "true": prose},
            reason=reason,
            sources=tuple(s for p in marks for s in p.mark.sources),
            change=prose,
        ),
    )


def determined_chief(
    collated: Collated, rulings: list[Determined]
) -> tuple[dict[str, Determined], EditCopy]:
    """Every Determined of the stage, and the chief's copy derived from them.

    Args:
        collated: the last fold, carrying the program's `stet`s.
        rulings: the chief's own, from `rule_at_cap`.

    Returns:
        `(address -> Determined, the chief's edit_copy)`.

    Raises:
        ValueError: the fold returned early and holds no proof.
    """
    if collated.proof is None:
        raise ValueError("the fold returned early -- no proof to derive a copy from")
    every = {**collated.determined, **{d.address: d for d in rulings}}
    return every, _chief_copy(collated.proof.read_from, every, collated.proof)
