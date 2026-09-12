"""The turn: a batch answered, applied to the copies, folded again.

    parse_answers(role, sent, returned) -> (answers, revisit)
    apply(copies, role, sent, answers, root) -> revisit
    take_answers(copies, role, sent, returned, root) -> (answers, revisit)
    run_turn(proof, binder, root, sent, answers) -> Collated
    rule_at_max_turns(collated, address, answer, side, reason, turn, prose)
                                                                  -> Determined
    determined_chief(collated, rulings) -> (every Determined, the chief's edit_copy)
    batch_for(collated) -> the batch that goes out, every slot carrying its diff
    proof_after(collated, turns) -> the master proof as the state between turns
    refold(proof, binder, root) -> the fold over a proof read back, at max turns
    close(collated, rulings, turns) -> (the closed proof, the chief's edit_copy)
    contracts() -> the three shapes a role is handed, generated from the code

! `commands/collate.py` writes the first batch through `batch_for` and the
proof through `proof_after`; `commands/turn.py` runs a turn and
`commands/disposition.py` closes one. `docs/the-turn.md` is the source for what a
turn is, and its *What is BUILT* table is the map from that file to this one.

=== A DiffMark DOES NOT BECOME A Mark -- `Process: #86`

The collator compares copies, not marks, so applying a role's answer to an
ESCALATION is an edit to that role's copy at the address:

    hold        nothing
    withdraw    the entry becomes a `clean`
    correct     the entry's `change` becomes the DiffMark's `change`; on a
                `correct` or `patch` entry the claim becomes the role's own
                proposal replaced by it, so the claim derives the change; on
                a `move` the claim stands, its `to` naming the destination
    patch       the same

The mover's answer at its move's destination end is an edit to the move
(`Process: #129`): the table applies to the `move` entry at the origin, and the
mover's slot at the destination stays as it is.

A COMPOSITION re-read is answered with a fresh `Mark` over the composed text
(`#86`), and the answer set is `clean`, `query`, `correct`, `patch`:

    clean       the role ADOPTS the slot's text -- its entry becomes a
                `correct` whose `change` is that text, whoever owed the change
                (`Process: #89`: a lone mark goes back to the roles that were
                clean, and their clean over it is agreement). The sources are
                the composed side's, from the sent slot. A `clean` over the
                BASE, where nothing composed, is a withdrawal. A mover's
                `clean` at its move's origin, where the slot carries the
                move's own text, keeps the move. Where the base
                is empty -- an `add`'s place -- no `correct` can quote it, so
                a role adopts the `add` the slot carries by holding that add,
                its claim and sources included; an entry already carrying the
                slot's text stays as it is. Where the slot carries no `add`
                there, the entry becomes a `clean`
    query       the entry becomes the query
    correct     the entry becomes the role's own `correct`, its claim quoting
                the slot's text -- the text collate sent -- not the original
                (`Process: #115`); the fold checks the quote against that text
    patch       the same, as a `patch` -- not a correct, which owes sources a
                patch never carried

An answer at a place the role's copy holds no slot for -- an `add`'s empty
place, which `desk.collator._outcome` sends to every role of the stage while
only the adding role's copy holds it -- lands on a slot seeded from the page
and appended to that page's sheet, by `flows.fill.place_on_the_page`: the
"no slot" rows of `flows/fill.py`'s table. A place the page does not carry is
refused there; one the batch did not send to the role is refused before, by
`parse_answers`.

Then `flows.collate.collate` runs again over the copies, and every place that
agreed comes back as a `stet` Determined at this turn (`Process: #87`). The
fold carries every place an `add` touches as a re-read, so where every role of
that re-read now holds the same `add`, `_agreed_adds` records the `stet`
(`Process: #116`). A place the turn asked about that comes back as a re-read
whose roles still hold different texts is an escalation, which `_disagreeing`
records (`Process: #127`). What did not agree is the next turn's batch, until the task
agent's max turns (`Process: #78`), where `rule_at_max_turns` records the
chief's `taken_in` or `recast` and `determined_chief` derives the chief's copy
from the whole set.

!! ONCE STET, ALWAYS STET -- `Process: #91`. A place determined on an earlier
turn keeps that Determined, turn included, whatever the copies say now, and
leaves every later batch. `run_turn` reads the last fold's `determined` off
the proof for exactly that; MEASURED in the game, hands 1 and 4, without it
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

from collections.abc import Iterator, Mapping
from dataclasses import replace
from pathlib import Path

from comment_review.binder.binder import Binder
from comment_review.desk.containers import EditCopy, MasterProof
from comment_review.desk.determined import CHIEF, ORIGINAL, Answer, Determined
from comment_review.desk.diff_mark import (
    COMPOSITION,
    DIFF,
    ESCALATION,
    QUESTION,
    DiffInstruction,
    DiffMark,
    batch_of,
    parse_batch,
)
from comment_review.desk.diff_mark import allowed as diff_allowed
from comment_review.desk.mark import (
    INSTRUCTIONS,
    Instruction,
    Mark,
    allowed,
    filled,
    untouched,
    without_location,
)
from comment_review.flows.collate import Collated, _chief_copy, _identical, collate
from comment_review.flows.fill import place_on_the_page
from comment_review.flows.mark_errors import Revisit
from comment_review.results.differences import diff3

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
                entry["sources"] = list(_composition_of(slot).get("sources") or [])
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


def _composition_of(slot: dict) -> dict:
    """The mark whose text the slot carries, as the slot lists it.

    The composed side's, or the lone mark's. A role adopting it by `clean`
    takes its sources, so the `correct` it then holds parses, and at an empty
    place its claim as well, so the `add` it then holds parses. Empty where no
    mark on the slot carries that text.
    """
    text = slot.get("raw_text")
    for mark in slot.get("marks", []):
        if isinstance(mark, dict) and mark.get("change") == text:
            return mark
    return {}


def _entries_of(copies: list[dict], role: str) -> Iterator[dict]:
    """Every slot on `role`'s copy, the dict objects themselves."""
    for copy in copies:
        if not isinstance(copy, dict) or copy.get("role") != role:
            continue
        for sheet in copy.get("sheets", []):
            if not isinstance(sheet, dict):
                continue
            for entry in sheet.get("marks", []):
                if isinstance(entry, dict):
                    yield entry


def _entry_at(copies: list[dict], role: str, address: str) -> dict | None:
    """The slot on `role`'s copy at `address`, the dict object itself."""
    return next(
        (e for e in _entries_of(copies, role) if e.get("address") == address), None
    )


def _move_to(copies: list[dict], role: str, address: str) -> dict | None:
    """The one `move` on `role`'s copy whose `claim.to` names `address`.

    None where the copy holds no such move, or more than one.
    """
    moves = [
        entry
        for entry in _entries_of(copies, role)
        if entry.get("instruction") == str(Instruction.MOVE)
        and isinstance(claim := entry.get("claim"), dict)
        and claim.get("to") == address
    ]
    return moves[0] if len(moves) == 1 else None


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


def _as_answered(entry: dict, answer: Mark, sources: list) -> dict:
    """The slot as the role's own `correct` or `patch`, over the text it was sent.

    Its claim is the role's, quoting the slot's text rather than the original
    (`Process: #115`). The address, anchor and `raw_text` stay the slot's, and
    a `correct` cites the role's sources, else the slot's.
    """
    held = {
        **Mark.seed(
            entry["address"], entry.get("anchor", ""), entry.get("raw_text", "")
        ),
        "instruction": str(answer.instruction),
        "claim": dict(answer.claim),
        "reason": answer.reason,
        "change": answer.change,
    }
    if INSTRUCTIONS[answer.instruction].owes_sources:
        held["sources"] = list(answer.sources) or list(sources)
    return held


def _an_add_adopting(entry: dict, added: dict) -> dict:
    """The slot as an `add` of the text another role's `add` carries.

    Its claim, sources and change are that add's, as the sent slot lists it;
    its reason names the adoption.
    """
    return {
        **Mark.seed(
            entry["address"], entry.get("anchor", ""), entry.get("raw_text", "")
        ),
        "instruction": str(Instruction.ADD),
        "claim": dict(added.get("claim") or {}),
        "reason": "adopted the composition",
        "sources": list(added.get("sources") or []),
        "change": added.get("change", ""),
    }


def _replacing(instruction: Instruction, proposal: str, change: str) -> dict:
    """A `correct` or `patch` claim that `change` replaces the role's `proposal`.

    The quoted key holds the proposal and the other key the change, so
    `desk.mark.derived_change` over the proposal gives the change. The
    proposal is the entry's own `change`, which the batch sent the role among
    the slot's marks.
    """
    spec = INSTRUCTIONS[instruction]
    key = spec.quotes_original
    other = next(k for k in spec.claim_all if k != key)
    return {key: proposal, other: change}


def _answered(entry: dict, answer: DiffMark | Mark, composition: dict) -> dict | None:
    """What one slot becomes under one answer, per the tables above.

    Args:
        entry: the slot on the role's own copy the answer applies to, as
            `apply` finds it.
        answer: the role's answer there.
        composition: `_composition_of` the slot the answer was sent, which a
            `clean` at an empty place adopts where it is an `add`.

    Returns:
        The entry the slot is to hold, or None where it stays as it is -- a
        `hold`, a mover's `clean` at its move's origin where the slot carries
        the move's own text, or a `clean` at an empty place from the role
        whose entry already carries the slot's text.
    """
    if isinstance(answer, DiffMark):
        if answer.instruction is DiffInstruction.HOLD:
            return None
        if answer.instruction is DiffInstruction.WITHDRAW:
            return _a_clean(entry)
        held = {**entry, "change": answer.change}
        named = entry.get("instruction")
        if named in (str(Instruction.CORRECT), str(Instruction.PATCH)):
            held["claim"] = _replacing(
                Instruction(named), entry.get("change", ""), answer.change
            )
        return held
    sources = entry.get("sources") or list(answer.sources)
    if answer.instruction is Instruction.CLEAN:
        if (
            entry.get("instruction") == str(Instruction.MOVE)
            and entry.get("change") == answer.raw_text
        ):
            return None
        adopts = bool(sources) and answer.raw_text != entry.get("raw_text", "")
        if not adopts:
            return _a_clean(entry)
        if filled(entry.get("raw_text")):
            return _a_correct_over_base(
                entry, answer.raw_text, "adopted the composition", sources
            )
        if entry.get("change") == answer.raw_text:
            return None
        if composition.get("instruction") == str(Instruction.ADD):
            return _an_add_adopting(entry, composition)
        return _a_clean(entry)
    if answer.instruction is Instruction.QUERY:
        return {**answer.serialize(), "raw_text": entry.get("raw_text", "")}
    return _as_answered(entry, answer, sources)


def apply(
    copies: list[dict],
    role: str,
    sent: list,
    answers: list[tuple[str, DiffMark | Mark]],
    root: Path | None,
) -> list[Revisit]:
    """Write one role's answers into its own copy, per the tables above.

    Args:
        copies: the wire copies `collate` was handed. MUTATED.
        role: whose answers these are.
        sent: the slots the batch sent this role, which `parse_answers`
            paired each answer to.
        answers: `parse_answers`' pairs.
        root: the checkout a page is read from, to seed a slot at a place the
            role's copy does not hold.

    An escalation answer at a move's destination end is written to the move
    (`Process: #129`): where the role's own slot there is absent or a
    `clean`, and its copy holds exactly one `move` whose `claim.to` names that
    address, the answer applies to that `move` entry, and the slot at the
    destination stays as it is.

    Returns:
        A `Revisit` per address this role's copy holds no slot for and
        `flows.fill.place_on_the_page` seeds none for -- no sheet for the page,
        no readable page, or no such place on it -- and one per answer whose
        entry would not parse. An entry is written only once
        `Mark.deserialize`, the boundary the fold's `Sheet` runs, accepts it,
        so a refused answer leaves the slot as it stood.
    """
    composed = {
        slot["address"]: _composition_of(slot)
        for slot in sent
        if isinstance(slot, dict) and filled(slot.get("address"))
    }
    revisit: list[Revisit] = []
    for address, answer in answers:
        entry = _entry_at(copies, role, address)
        if isinstance(answer, DiffMark) and (
            entry is None or entry.get("instruction") == str(Instruction.CLEAN)
        ):
            entry = _move_to(copies, role, address) or entry
        sheet = None
        if entry is None:
            mine = [c for c in copies if isinstance(c, dict) and c.get("role") == role]
            sheet, entry, why = place_on_the_page(mine, address, root)
            if sheet is None:
                reasons = [
                    m.removeprefix(f"{address}: ").removeprefix(f"{address} ")
                    for m in why
                ]
                revisit.append(_refused(role, address, address, reasons))
                continue
        held = _answered(entry, answer, composed.get(address, {}))
        if held is None:
            continue
        parsed, why = Mark.deserialize(address, held)
        if parsed is None:
            reasons = [without_location(address, m) for m in why]
            revisit.append(_refused(role, address, address, reasons))
            continue
        if sheet is None:
            _becomes(entry, held)
        else:
            sheet.append(held)
    return revisit


def take_answers(
    copies: list[dict], role: str, sent: list, returned: object, root: Path | None
) -> tuple[list[tuple[str, DiffMark | Mark]], list[Revisit]]:
    """One role's answers, read against what was sent and written into its copy.

    `run_turn` calls this for each role before the fold, and
    `commands/check.py --answers` calls it over the proof's copies, so the two
    refuse the same answers.

    Args:
        copies: the wire copies. MUTATED, as `apply` says.
        role: whose answers these are.
        sent: the slots the batch sent this role.
        returned: what came back, in any shape `slots_of` reads.
        root: the checkout a page is read from, as `apply` takes it.

    Returns:
        `(answers, revisit)` -- `parse_answers`' pairs, and every `Revisit`
        `parse_answers` and `apply` recorded.
    """
    answers, revisit = parse_answers(role, sent, slots_of(returned, role))
    return answers, revisit + apply(copies, role, sent, answers, root)


def _unpacked(proof: MasterProof) -> tuple[list[dict], dict[str, Determined]]:
    """The proof as a fold takes it: its copies as wire dicts, its rulings by address.

    ! THE WIRE DICTS, BECAUSE `apply` MUTATES THEM IN PLACE and the fold parses
    what they then hold -- the header's own contract. The proof's copies are the
    copies as they stood after the last fold, which is what a turn edits.
    """
    copies = [copy.serialize() for copy in proof.edit_copies]
    return copies, {one.address: one for one in proof.determined}


def run_turn(
    proof: MasterProof,
    binder: Binder,
    root: Path,
    sent: dict[str, list],
    answers: Mapping[str, object],
) -> Collated:
    """One turn: every role's answers applied to the proof's copies, then the fold.

    Args:
        proof: the master proof as the last fold left it -- the copies as
            they stand and every Determined so far. This turn's number is
            `proof.turn + 1`, and every `stet` the fold records carries it.
        binder: the binder the copies were seeded from.
        root: the checkout citations resolve against.
        sent: the batch that went out -- role -> its slots, as `batch_of`
            built it. !! THE SENT BATCH DRIVES THE TURN: every role in it owes
            every slot in it, and a role's answers are read against it. It and
            every batch the proof's record holds are what a quote a turn wrote
            is checked against, beside the page (`Process: #119`).
        answers: role -> what came back, in any shape `slots_of` reads.

    Returns:
        The fold over the copies as they now stand. Every place the proof had
        determined is kept as it was -- `Process: #91` -- and dropped from
        this turn's escalations and re-reads; `revisit` holds the fold's own
        beside a `Revisit` for every slot that was refused, unanswered, never
        sent, or had no home.
    """
    copies, earlier = _unpacked(proof)
    turn = proof.turn + 1
    revisit: list[Revisit] = []
    for role in answers:
        if role not in sent:
            revisit.append(
                _refused(
                    role, "", f"{role} (the batch)", ["no slots were sent to this role"]
                )
            )
    for role, slots in sent.items():
        _, why = take_answers(copies, role, slots, answers.get(role, []), root)
        revisit += why
    got = collate(
        proof.stage, copies, binder, root, turn=turn, sent=(*_sent_of(proof), sent)
    )
    got = _keeping(got, earlier)
    contested = _asked(sent)
    got = _withdrawn(got, contested, turn)
    got = _agreed_adds(got, contested, turn)
    got = _disagreeing(got, contested)
    return replace(got, revisit=[*revisit, *got.revisit])


def _sent_of(proof: MasterProof) -> tuple[dict, ...]:
    """Every batch the proof's turn record says was sent, oldest first."""
    return tuple(
        record["sent"]
        for record in proof.turns
        if isinstance(record, dict) and isinstance(record.get("sent"), dict)
    )


def _asked(sent: dict) -> set[str]:
    """Every address one batch sent to any role: the places that turn asked about."""
    return {slot["address"] for slots in sent.values() for slot in slots}


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


def _agreed_adds(got: Collated, contested: set[str], turn: int) -> Collated:
    """A contested `add` that every role of its re-read now holds is a `stet`.

    `Process: #116`: at an add's empty place every other role's `clean` is
    agreement, and `apply` writes that role as holding the same `add`. The
    fold carries every place an `add` touches as a re-read whatever the roles
    hold, so the agreement is read here: every owing mark is an `add`, every
    role of the re-read holds one, and all carry one text (`Process: #88`).
    At a place holding text a `clean` adopts by a `correct` instead, which the
    fold settles as an escalation.

    Returns:
        The fold with each such place out of `rereads`, a `stet` Determined at
        `turn` for it -- `how` "identical", or "one" where one role is left
        to hold it -- and the chief's copy derived again.
    """
    agreed: dict[str, Determined] = {}
    for entry in got.rereads:
        address, marks = entry["address"], entry["marks"]
        if address not in contested:
            continue
        if any(placed.mark.instruction is not Instruction.ADD for placed in marks):
            continue
        if not set(entry["roles"]) <= {placed.role for placed in marks}:
            continue
        one = _identical(marks)
        if one is not None:
            how = "identical" if len(marks) > 1 else "one"
            agreed[address] = Determined(
                address, Answer.STET, turn, one.role, how, "", one.mark
            )
    if not agreed or got.proof is None:
        return got
    determined = {**got.determined, **agreed}
    return replace(
        got,
        determined=determined,
        rereads=[e for e in got.rereads if e["address"] not in agreed],
        chief=_chief_copy(got.proof.read_from, determined, got.proof),
    )


def _disagreeing(got: Collated, contested: set[str]) -> Collated:
    """A contested re-read whose owing marks carry more than one text escalates.

    `Process: #124` and `#127`: two roles holding different texts at one place
    disagree, and after a turn that is decided here, not in the collator, so
    the first fold is unchanged. It covers a composition `correct` or `patch`
    beside another role's `clean` adoption, an escalation where one role
    answers with a new text and another holds, and an `add` beside another
    role's answer to it, which stays carried forward (`Process: #123`).

    Returns:
        The fold with each such place out of `rereads` and at the end of
        `escalations`, without the `composed` mark only a re-read carries.
    """
    moved = [
        entry
        for entry in got.rereads
        if entry["address"] in contested
        and len({placed.mark.change for placed in entry["marks"]}) > 1
    ]
    if not moved:
        return got
    gone = {entry["address"] for entry in moved}
    return replace(
        got,
        escalations=[
            *got.escalations,
            *({k: v for k, v in e.items() if k != "composed"} for e in moved),
        ],
        rereads=[e for e in got.rereads if e["address"] not in gone],
    )


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


def refold(proof: MasterProof, binder: Binder, root: Path) -> Collated:
    """The fold over the proof's copies as they stand, every Determined kept.

    What max turns reads: `rule_at_max_turns` needs the places still carried forward
    and `determined_chief` the program's stets, and neither is on the wire --
    the proof carries the copies and the rulings, and the fold is re-derived
    from them at the turn the proof stands at, `proof.turn`. A quote a turn
    wrote is checked against the batches the proof's record holds, beside the
    page (`Process: #119`).

    Args:
        proof: the master proof as the last turn wrote it.
        binder: the binder the copies were seeded from.
        root: the checkout citations resolve against.

    Returns:
        The `Collated`, with `proof.determined` kept over this fold's (`#91`),
        and every place the last recorded turn sent whose roles still hold
        different texts an escalation, as `run_turn` returned it (`#127`).
    """
    copies, earlier = _unpacked(proof)
    sent = _sent_of(proof)
    got = collate(proof.stage, copies, binder, root, turn=proof.turn, sent=sent)
    got = _keeping(got, earlier)
    return _disagreeing(got, _asked(sent[-1]) if sent else set())


def _recast_claim(first: Mark, prose: str) -> dict:
    """The claim a recast's synthesized mark owes, shaped to `first`'s instruction.

    `correct` and `patch` are the only rows this quotes an original text for;
    `add`, `move` and `drop` keep `first.claim` unmodified.

    Args:
        first: the first owing mark at the place being recast -- whose
            `instruction` the synthesized mark carries forward.
        prose: the chief's own paragraph.

    Returns:
        `INSTRUCTIONS[first.instruction].claim_all`, filled. For the two rows
        that quote an existing sentence (`correct`, `patch`) the quoted key
        (`false`, `from`) takes `first.raw_text` and the other key takes
        `prose`. A row that quotes nothing (`add`, `move`) or whose claim
        IS the quoted key (`drop`) keeps `first.claim` as filed -- `prose`
        has no slot in that shape to fill; it becomes `change`, not `claim`.
    """
    spec = INSTRUCTIONS[first.instruction]
    key = spec.quotes_original
    others = [k for k in spec.claim_all if k != key]
    if key and others:
        return {key: first.raw_text, others[0]: prose}
    return dict(first.claim)


def rule_at_max_turns(
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
        turn: the turn max turns fell on.
        prose: for a `RECAST`, the chief's own paragraph as raw text.

    Returns:
        The `Determined`, its `mark` being what the chief's copy will carry:
        the side's mark, None for the original, or a synthesized mark for a
        recast -- carrying the instruction the roles filed, `claim` shaped to
        it by `_recast_claim`, and citing every side's sources -- so it
        parses as an ordinary mark the way `flows.collate._composition`'s
        does.

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
            return Determined(
                address, answer, turn, ORIGINAL, "max-turns", reason, None
            )
        placed = next((p for p in marks if p.role == side), None)
        if placed is None:
            raise ValueError(f"{side} has no mark at {address} to take in")
        return Determined(address, answer, turn, side, "max-turns", reason, placed.mark)
    if not filled(prose):
        raise ValueError("a recast needs the chief's own prose")
    first = marks[0].mark
    return Determined(
        address,
        answer,
        turn,
        CHIEF,
        "max-turns",
        reason,
        Mark(
            address=address,
            anchor=first.anchor,
            raw_text=first.raw_text,
            instruction=first.instruction,
            claim=_recast_claim(first, prose),
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
        rulings: the chief's own, from `rule_at_max_turns`.

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
        raise ValueError(f"unruled at max turns: {named}")
    every = {**collated.determined, **{d.address: d for d in rulings}}
    return every, _chief_copy(collated.proof.read_from, every, collated.proof)


def batch_for(collated: Collated) -> dict[str, list[dict]]:
    """The batch that goes out -- `batch_of`, with every slot's diff attached.

    !! THE RENDERER LIVES AT THE FLOW -- T11, P13. `results.differences.diff3`
    is the write end, which `desk/` may not reach, so `desk.diff_mark.batch_of`
    sends a slot with no rendered text and this fills `DIFF` on each: the base
    against every side at the place, in diff3 form, the same string for every
    role that owes the place.

    Args:
        collated: the last fold.

    Returns:
        role -> its slots, as `batch_of` shapes them, each carrying `DIFF`.
    """
    batch = batch_of(collated.escalations, collated.rereads)
    for entry in (*collated.escalations, *collated.rereads):
        marks = entry["marks"]
        base = marks[0].mark.raw_text if marks else ""
        sides = {placed.role: placed.mark.change for placed in marks}
        rendered = "".join(diff3(base, sides))
        for role in entry["roles"]:
            for slot in batch.get(role, []):
                if slot["address"] == entry["address"]:
                    slot[DIFF] = rendered
    return batch


def proof_after(got: Collated, turns: tuple[dict, ...] = ()) -> MasterProof:
    """The master proof as the state between turns, from a fold -- `Process: #87`.

    Args:
        got: the fold. Its `proof` is the copies AS THEY STAND, which is what
            the next turn mutates and folds again.
        turns: the record so far. The caller keeps it; a fold does not know it.

    Returns:
        `got.proof` carrying `turns`, every Determined in address order, and
        each unsettlable place without its `Placed` marks -- `{address, roles,
        query}`, the shape the wire holds and the human is asked.

    Raises:
        ValueError: the fold returned early and holds no proof.
    """
    if got.proof is None:
        raise ValueError("the fold returned early -- no proof to carry forward")
    return replace(
        got.proof,
        turns=tuple(turns),
        determined=tuple(got.determined[a] for a in sorted(got.determined)),
        unsettlable=tuple(
            {k: v for k, v in u.items() if k != "marks"} for u in got.unsettlable
        ),
    )


def close(
    got: Collated, rulings: list[Determined], turns: tuple[dict, ...]
) -> tuple[MasterProof, EditCopy]:
    """The proof closed at max turns, and the chief's copy from the whole set.

    Args:
        got: the last fold, as `refold` returns it.
        rulings: the chief's own, from `rule_at_max_turns`, one per place still
            carried forward.
        turns: the record as the proof stood; max turns adds no turn.

    Returns:
        `(the closed proof, the chief's edit_copy)`. The proof carries every
        Determined -- the program's stets and the chief's rulings -- in
        address order, and its unsettlable places as `proof_after` shapes them.

    Raises:
        ValueError: as `determined_chief` -- a place still carried forward
            has no ruling, or the fold holds no proof.
    """
    every, chief = determined_chief(got, rulings)
    proof = proof_after(got, turns)
    closed = replace(proof, determined=tuple(every[a] for a in sorted(every)))
    return closed, chief


def contracts() -> dict:
    """The three shapes a role is handed, generated from the code -- T19, P2.

    A stage-4c `Mark` (`desk.mark.allowed`), an ESCALATION answer
    (`desk.diff_mark.allowed`), and a COMPOSITION answer: the `Mark` shape
    narrowed to `COMPOSITION_ANSWERS`, over the slot's `raw_text` -- the
    composed text, or the lone mark's -- rather than the base. Publishing them
    in the brief is the agents lane's; `commands/check.py --contract` prints
    them so nobody hand-types one.
    """
    mark = allowed()
    composition = {
        **mark,
        "instruction": sorted(str(one) for one in COMPOSITION_ANSWERS),
        "claim": {str(one): mark["claim"][str(one)] for one in COMPOSITION_ANSWERS},
        "over": "the slot's `raw_text` -- the composed text, or the one mark's; "
        "a `clean` accepts it, a `correct`'s `claim.false` quotes a sentence of it",
    }
    return {
        "stage_4c_mark": mark,
        "escalation": diff_allowed(),
        "composition": composition,
    }
