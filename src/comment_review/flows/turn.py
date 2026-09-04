"""A PROTOTYPE. The turn: a batch answered, applied to the copies, folded again.

    parse_answers(role, sent, returned) -> (answers, revisit)
    apply(copies, role, answers) -> revisit
    run_turn(stage, copies, binder, root, sent, answers, turn, earlier)
        -> (Collated, revisit)
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

    clean       the role ADOPTS the slot's text -- its entry becomes a
                `correct` whose `change` is that text, whoever owed the change
                (`Process: #89`: a lone mark goes back to the roles that were
                clean, and their clean over it is agreement). The sources are
                the composed side's, from the sent slot. A `clean` over the
                BASE, where nothing composed, is a withdrawal
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

!! ONCE STET, ALWAYS STET -- `Process: #91`. A place determined on an earlier
turn keeps that Determined, turn included, whatever the copies say now, and
leaves every later batch. `run_turn` takes the last fold's `determined` as
`earlier` for exactly that; MEASURED in the game, hands 1 and 4, without it
a stet at turn 1 read turn 2 after the next fold.

!! A REFUSED ANSWER IS A `Revisit` -- T18, `flows.mark_errors`, the shape the
fold already routes. MEASURED in the game's hand 4: a refused answer was a
problem string, which named nobody a task agent could send it to. Unanswered
is `unreadable=False`; malformed, never sent, or without a home is True.

! THE COPIES ARE MUTATED IN PLACE. They are the wire dicts `collate` was
handed, and the next fold reads them as they now stand -- which is what a
turn IS. The master proof's record of what each turn sent and got back is the
caller's to keep (`MasterProof.turns`); this module returns what it needs.
"""

from dataclasses import replace
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
from comment_review.desk.mark import Instruction, Mark, filled, untouched
from comment_review.flows.collate import Collated, _chief_copy, collate
from comment_review.flows.mark_errors import Revisit

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


def _refused(
    role: str, address: str, where: str, reasons: list[str], unreadable: bool = True
) -> Revisit:
    return Revisit(role, address, where, tuple(reasons), unreadable)


def parse_answers(
    role: str, sent: list, returned: list
) -> tuple[list[tuple[str, DiffMark | Mark]], list[Revisit]]:
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
        `(answers, revisit)`. Every SENT slot contributes to exactly one: an
        `(address, DiffMark | Mark)` pair, or one `Revisit` carrying every
        reason. An unanswered slot -- never returned, or returned untouched --
        is refused by name, never read as a withdrawal or a clean, and is the
        one Revisit that is not `unreadable`. A returned slot at an address
        this role was never sent is a Revisit of its own.
    """
    by_address = {
        slot["address"]: slot
        for slot in sent
        if isinstance(slot, dict) and filled(slot.get("address"))
    }
    answered: dict[str, dict] = {}
    revisit: list[Revisit] = []
    for i, slot in enumerate(returned, 1):
        if not isinstance(slot, dict):
            revisit.append(
                _refused(role, "", f"{role} slot {i}", ["a slot must be an object"])
            )
            continue
        address = slot.get("address")
        if not filled(address):
            revisit.append(_refused(role, "", f"{role} slot {i}", ["names no address"]))
            continue
        if address not in by_address:
            revisit.append(
                _refused(role, address, address, ["never sent to this role -- refused"])
            )
            continue
        answered[address] = slot

    answers: list[tuple[str, DiffMark | Mark]] = []
    for address, slot in by_address.items():
        loc = f"{role} {address}"
        got = answered.get(address)
        entry = {**slot, **(got or {})}
        if got is None or untouched(entry):
            revisit.append(
                _refused(
                    role,
                    address,
                    address,
                    ["unanswered -- refused, not read as a withdrawal"],
                    unreadable=False,
                )
            )
            continue
        question = slot.get(QUESTION)
        if question == ESCALATION:
            marks, why = parse_batch(role, [entry])
            if why:
                revisit.append(_refused(role, address, address, why))
            answers += [(mark.address, mark) for mark in marks]
        elif question == COMPOSITION:
            if entry.get("instruction") == str(Instruction.CLEAN) and not entry.get(
                "sources"
            ):
                entry["sources"] = _sources_of_the_composition(slot)
            mark, why = Mark.deserialize(loc, entry)
            if mark is None:
                revisit.append(_refused(role, address, address, why))
                continue
            if mark.instruction not in COMPOSITION_ANSWERS:
                revisit.append(
                    _refused(
                        role,
                        address,
                        address,
                        [
                            f"`{mark.instruction}` is not a composition answer -- "
                            f"one of {', '.join(COMPOSITION_ANSWERS)} (Process 86)"
                        ],
                    )
                )
                continue
            answers.append((mark.address, mark))
        else:
            revisit.append(
                _refused(role, address, address, ["the sent slot names no question"])
            )
    return answers, revisit


def _sources_of_the_composition(slot: dict) -> list:
    """The sources of the mark whose text the slot carries.

    The composed side's, or the lone mark's, so a role adopting it by `clean`
    can hold a `correct` that parses. Empty where no mark on the slot carries
    that text.
    """
    text = slot.get("raw_text")
    for mark in slot.get("marks", []):
        if isinstance(mark, dict) and mark.get("change") == text:
            return list(mark.get("sources") or [])
    return []


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


def apply(
    copies: list[dict], role: str, answers: list[tuple[str, DiffMark | Mark]]
) -> list[Revisit]:
    """Write one role's answers into its own copy, per the tables above.

    Args:
        copies: the wire copies `collate` was handed. MUTATED.
        role: whose answers these are.
        answers: `parse_answers`' pairs.

    Returns:
        A `Revisit` per address this role's copy carries no slot for.
    """
    revisit: list[Revisit] = []
    for address, answer in answers:
        entry = _entry_at(copies, role, address)
        if entry is None:
            revisit.append(
                _refused(role, address, address, ["no slot on this role's copy"])
            )
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
        sources = entry.get("sources") or list(answer.sources)
        if answer.instruction is Instruction.CLEAN:
            adopts = bool(sources) and answer.raw_text != entry.get("raw_text", "")
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
    return revisit


def run_turn(
    stage: str,
    copies: list[dict],
    binder: Binder,
    root: Path,
    sent: dict[str, list],
    answers: dict[str, list],
    turn: int,
    earlier: dict[str, Determined] | None = None,
) -> tuple[Collated, list[Revisit]]:
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
        earlier: the last fold's `determined`. Every place in it is kept as
            it was -- `Process: #91` -- over whatever this fold makes of it,
            and is dropped from this turn's escalations and re-reads.

    Returns:
        `(Collated, revisit)` -- the fold over the copies as they now stand,
        and a `Revisit` for every slot that was refused, unanswered, never
        sent, or had no home.
    """
    revisit: list[Revisit] = []
    for role in answers:
        if role not in sent:
            revisit.append(
                _refused(
                    role, "", f"{role} (the batch)", ["no slots were sent to this role"]
                )
            )
    for role, slots in sent.items():
        parsed, why = parse_answers(role, slots, slots_of(answers.get(role, []), role))
        revisit += why
        revisit += apply(copies, role, parsed)
    got = collate(stage, copies, binder, root, turn=turn)
    got = _keeping(got, earlier or {})
    contested = {slot["address"] for slots in sent.values() for slot in slots}
    return _withdrawn(got, contested, turn), revisit


def _withdrawn(got: Collated, contested: set[str], turn: int) -> Collated:
    """A contested place no mark is left at is a `stet` of the original.

    Every mark there was withdrawn this turn, so nothing owes a change and
    the fold has no entry for it in any list -- `Process: #87` says every
    resolved place carries a Determined, so this writes one: `side`
    ORIGINAL, `mark` None, `how` "withdrawn". T15's withdraw / withdraw.
    """
    carried = (
        {e["address"] for e in got.escalations}
        | {e["address"] for e in got.rereads}
        | {u["address"] for u in got.unsettlable}
        | set(got.determined)
    )
    gone = sorted(contested - carried)
    if not gone:
        return got
    determined = dict(got.determined)
    for address in gone:
        determined[address] = Determined(
            address, Answer.STET, turn, ORIGINAL, "withdrawn", "", None
        )
    return replace(got, determined=determined)


def _keeping(got: Collated, earlier: dict[str, Determined]) -> Collated:
    """The fold with every earlier Determined kept over this turn's -- `#91`.

    The chief's copy is derived again from the kept set, so a place stet on
    turn 1 carries turn 1's mark whatever a role wrote there since.
    """
    if not earlier or got.proof is None:
        return got
    determined = {**got.determined, **earlier}
    return replace(
        got,
        determined=determined,
        escalations=[e for e in got.escalations if e["address"] not in earlier],
        rereads=[e for e in got.rereads if e["address"] not in earlier],
        chief=_chief_copy(got.proof.read_from, determined, got.proof),
    )


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
    if any(u["address"] == address for u in collated.unsettlable):
        raise ValueError(
            f"{address} is unsettlable -- the human's query rides with the set and "
            "is asked last (Process 90)"
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
        ValueError: the fold returned early and holds no proof; or a place
            still carried forward -- an escalation or a re-read -- has no
            ruling among `rulings`. !! NOTHING SURVIVES THE CAP UNRULED, T17:
            the refusal names every such place and its roles. An unsettlable
            place is not among them; it is the human's (`Process: #90`).
    """
    if collated.proof is None:
        raise ValueError("the fold returned early -- no proof to derive a copy from")
    ruled = {d.address for d in rulings}
    unruled = [
        entry
        for entry in (*collated.escalations, *collated.rereads)
        if entry["address"] not in ruled
    ]
    if unruled:
        named = "; ".join(
            f"{entry['address']} ({', '.join(entry['roles'])})" for entry in unruled
        )
        raise ValueError(f"unruled at the cap: {named}")
    every = {**collated.determined, **{d.address: d for d in rulings}}
    return every, _chief_copy(collated.proof.read_from, every, collated.proof)
