"""The mark: one role's ruling on one place, and the enums its fields take.

    Instruction        the seven, closed -- a StrEnum, value DERIVED from name
    INSTRUCTION_NAMES  tuple(Instruction) -- what membership is asked of
    Shape              the three a `query` must name, closed -- a StrEnum
    QUERY_SHAPES       tuple(Shape), in the order `docs/the-mark.md` states them
    Touch              which of the places a mark writes is being asked about
    Mark               one role's ruling on one place -- the eight fields
                       `docs/the-mark.md` names, and no others
    Validator          the rule check a parser is handed
    read_mark()        an entry read as a `Mark`, then held to a `Validator`
    untouched()        a seeded slot no role has written in -- the coverage gap,
                       which is NOT a mark that failed to name an instruction
    filled()           a string with something in it
    as_text()          a string field as a record holds it
    read_text()        a string field a record uses, or a problem
    a_type()           a value's type, with its article, for a message
    read_member()      a closed-set field as a record holds it, or a problem
    without_location() one refusal with its `where` prefix removed

`Mark.deserialize` reads an entry's structure and asks nothing of the marks
table. The rules a mark is held to are `desk.marks.rules.validate`, which the
proof's parsers are handed and apply through `read_mark` (`decision-log.md
Process: #203`).

!! A MARK IS THE OBJECT; ITS `instruction` IS ONE OF SEVEN. The word this table
used to carry read as judicial and named the same thing twice, the object a
*finding* and its type the struck word -- `decision-log.md Vocabulary: #17`.
! `instruction` is the trade's: a proof correction has a TEXTUAL mark saying
where and a MARGINAL mark saying what to do, and the second is the instruction --
which is what a compositor executes, and this system has one.

!! `INSTRUCTION` NAMES THE ENUM; THE DATACLASS IS `Row`, NOT `Instruction`.
`decision-log.md Vocabulary: #17` landed the dataclass as `Instruction` before
the seven closed names had an enum of their own -- `T1.15` of
`docs/plans/0.2.4-the-mark-and-the-collator.md` gives the word to the enum, so
the dataclass took `Row`: `docs/the-mark.md` already calls its own subject
"four classifier columns" and "seven row flags", so `Row` is the spec's own
word for what one entry of that table holds. `decision-log.md Process: #46`.

!! EVERY CLOSED SET IN THIS FILE IS A `StrEnum`, following `reading.series.Kind`
-- `T1.15`. Each member's value is DERIVED from its name via
`_generate_next_value_`, never hand-typed. ! `reading.series.Kind` IS NOT ITSELF
AN EXAMPLE OF THAT DERIVATION -- it set the StrEnum precedent T1.15 names, but
its own member values are hand-typed (`TRAILING = "trailing-comment"` is not
`name.lower()`). No site here asks membership of an enum class directly
(`x in SomeEnum` raises `TypeError` on Python 3.11, measured at `lexer.py:87`)
-- `INSTRUCTION_NAMES` is the membership check for `Instruction`, and
`QUERY_SHAPES` is `Shape`'s companion tuple.

!! AND `Mark` REPLACED `problems(where, mark: dict)` ON 2026-08-29. Nothing
parsed a mark, so the seven fields existed as prose plus string literals at
the call sites, and three things were MEASURED off that: ten
`str`-into-`dict[Instruction, Row]` type errors in `desk/collator.py`; a
`flows/distribute.py` skip that dropped a mark carrying no instruction and recounted
it as a place nobody looked at; and `reviewer-brief.md`'s own worked example
passing the per-copy check at exit 0 AS UNRULED, because the brief keys the ruling
`instruction` and the code read `mark`. **A reviewer following the brief
produced findings that vanished in silence.**

! THE RULING FIELD IS `instruction`, AND THE CODE IS WHAT MOVED. Roy,
2026-08-29: *"the agent emits the 'mark', the 'instruction' was ... the action
that turned the mark into an actionable thing."* The enum was already
`Instruction` and the brief already said `instruction`; a `Mark.mark` is the
self-nesting that made this ambiguous.
"""

from collections.abc import Callable
from dataclasses import dataclass, fields
from enum import StrEnum, auto
from typing import TypeGuard, TypeVar


class Instruction(StrEnum):
    """The seven, closed. `docs/the-mark.md` is the spec; this only names them.

    ! Value derived from the member name via `_generate_next_value_`: each
    member equals its own name lower-cased, with no hand-typed string beside
    it, so a member renamed cannot keep an older wire value by accident.
    """

    @staticmethod
    def _generate_next_value_(
        name: str, start: int, count: int, last_values: list[str]
    ) -> str:
        return name.lower()

    CLEAN = auto()
    QUERY = auto()
    DROP = auto()
    CORRECT = auto()
    PATCH = auto()
    ADD = auto()
    MOVE = auto()


#: `Instruction`'s companion tuple -- membership is asked of this, never of the
#: `Instruction` class itself.
INSTRUCTION_NAMES = tuple(Instruction)


class Shape(StrEnum):
    """The three shapes a `query`'s claim must name, KEYED ON WHO RESOLVES IT.

    `decision-log.md Process: #33`, Roy 2026-08-27. The set they replaced --
    `outside the checkout`, `outside the code` -- was keyed on WHERE the missing
    evidence lived, and rested on a reviewer in a FRESH CHECKOUT reaching the
    same evidence later. Roy: *"this really is not expected to be a repeatable
    event."*

    ! A cause belongs in `reason`, which a human reads. A SHAPE is read by the
    flow, and the flow can do nothing with a cause.

    ! Value derived from the member name -- `OUTSIDE_MY_ROLE` gives
    `"outside-my-role"` -- so the Python identifier and the wire value stay
    related without either being hand-typed against the other.
    """

    @staticmethod
    def _generate_next_value_(
        name: str, start: int, count: int, last_values: list[str]
    ) -> str:
        return name.lower().replace("_", "-")

    OUTSIDE_MY_ROLE = auto()
    #: ! The one a collate step can ACT on: another role may have settled this place.
    UNABLE_TO_DETERMINE = auto()
    HUMAN_REVIEW_NECESSARY = auto()


#: `Shape`'s companion tuple, in the spec's own order -- membership is asked of
#: this, never of the `Shape` class itself.
QUERY_SHAPES = tuple(Shape)


class Touch(StrEnum):
    """Which of the places a mark writes is being asked about."""

    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()

    OWN = auto()
    ORIGIN = auto()
    DESTINATION = auto()


@dataclass(frozen=True)
class Mark:
    """One role's ruling on one place -- `docs/the-mark.md`'s eight fields.

    !! THE FIELD ORDER IS THE CHAIN OF CUSTODY, not alphabetical and not
    convenience -- the ruling, then the claim, the reason, the sources and the
    change it produces, with the three seeded fields (`SEEDED`, below) in
    front of them. `docs/the-mark.md`, "The fields -- eight", holds Roy's own
    sentence for it, in the register that ruling was given in.

    ! `role` IS NOT A FIELD, and `desk.proof.place.Filed` is what carries
    the pair. It belongs to the `edit_copy` a mark came back in, not to the
    mark.

    !! `raw_text` IS THE THIRD SEEDED FIELD AND WAS EXCLUDED UNTIL 2026-08-30.
    It went out on every slot and the mark parse dropped it, so one of the three
    seeded fields could not be written from this class's own names -- which is
    what left a dict literal in `flows/distribute.py` that a rename could not reach.
    ! WHAT COMES BACK IS NOT THE BASE. The page's text at the place is. On a
    row that does not write its own `raw_text` the field is carried back and
    nothing in the desk reads it; no check compares it with what was seeded
    (`decision-log.md Process: #185`).

    Attributes:
        address: `path@cue`. WHICH PLACE -- seeded, copied from the row, never
            built. Empty only for `clean`, the one row `substantive` is False
            for.
        anchor: the line of code the place sits on -- seeded, and empty where
            the gather resolved none.
        raw_text: the paragraph as it stands -- seeded, and what a role's
            `change` is a rewrite of. ! CARRIED, NEVER TRUSTED AS THE BASE:
            a quote is checked against the page's text at the place.
        instruction: one of the seven, as an `Instruction` member, so
            `INSTRUCTIONS[mark.instruction]` resolves with no cast.
        claim: the surgical spec -- structured keys, per instruction. Which
            keys is `INSTRUCTIONS[...].claim_all`; `desk.marks.rules.validate`
            checks that every one of them is there and filled.
        reason: WHY, in prose. No checker settles it.
        sources: `{cite, verbatim}` pairs, each optionally carrying `ran`.
            Empty for the two rows that owe none. ! TYPED `object` AND NOT
            `dict` ON PURPOSE: an entry that is not a pair is CARRIED, not
            dropped, so `collator.source_problems` can refuse it by name. A
            retired reader filtered `sources` to dicts before its own check
            ran, and a bare string vanished instead of being flagged.
        change: the RESULT -- the updated paragraph, as RAW TEXT. Roy,
            2026-08-28: *"`change` needs to be the updated paragraph as raw
            text not lines or sentences. This will make it easier to diff per
            the rest of the stages."* Empty on a `drop` whose claim names the
            whole paragraph, where an empty change IS the edit. None where the
            entry carried no `change`, or one that is not a string -- kept
            apart from "" so a row that owes a change can refuse a missing one
            rather than read it as a deletion.
    """

    address: str
    anchor: str
    raw_text: str
    instruction: Instruction
    claim: dict
    reason: str
    sources: tuple[object, ...]
    change: str | None

    #: The fields SEEDED onto every slot before a role sees it -- written by
    #: `seed`, copied back unchanged, and read here by `deserialize`.
    #:
    #: ! NOT ANNOTATED, DELIBERATELY. `dataclasses.fields` sees only annotated
    #: names, so this stays a plain class attribute and
    #: `tests/gates/test_mark_shape.py` still compares exactly the eight the
    #: spec states.
    SEEDED = ("address", "anchor", "raw_text")

    @classmethod
    def seed(cls, address: str, anchor: str, raw_text: str) -> dict:
        """One fillable slot, keyed by this class's OWN field names.

        !! THE WRITE HALF OF THE ROUND TRIP LIVES WITH THE READ HALF, and did
        not until 2026-08-30. `flows/distribute.py` wrote four keys as literals, so
        renaming a field here left that module writing the old key and nothing
        could notice -- `deserialize` would simply find the field absent.

        Args:
            address: `path@cue`, composed by `reading.addresser.address_for`.
            anchor: the line of code the place sits on, or "".
            raw_text: the paragraph as it stands.

        Returns:
            `{address, anchor, raw_text, instruction: None}` -- the slot as a
            role receives it. `instruction: None` is what `untouched` reads to
            say nobody has written here.

        Raises:
            AttributeError: `SEEDED` names something `Mark` does not declare.
                ! THIS IS THE WHOLE GUARD. A rename breaks HERE, loudly, at the
                point the row is built, rather than silently one module away.
        """
        declared = {f.name for f in fields(cls)}
        row: dict = {}
        for name, value in zip(cls.SEEDED, (address, anchor, raw_text), strict=True):
            if name not in declared:
                raise AttributeError(
                    f"Mark.seed writes `{name}`, which Mark does not declare"
                )
            row[name] = value
        row["instruction"] = None
        return row

    def serialize(self) -> dict:
        """This mark as the wire entry a sheet carries -- its OWN field names.

        ! THE COUNTERPART OF `seed`, AND IT EXISTS FOR THE SAME REASON. A
        caller writing a mark back onto a sheet by hand re-creates the literal
        `seed` removed, one module further along -- which is what the copy
        chief's `edit_copy` would otherwise be built from.

        Returns:
            A dict `deserialize` accepts and returns an equal `Mark` from.
            `instruction` is written as its string value, since that is what
            the wire carries and what `deserialize` reads. A `change` of None
            is left off, which is how a role writes a mark with no change and
            what `deserialize` reads back as None.
        """
        entry = {f.name: getattr(self, f.name) for f in fields(self)}
        entry["instruction"] = str(self.instruction)
        if self.change is None:
            del entry["change"]
        entry["claim"] = dict(self.claim)
        entry["sources"] = list(self.sources)
        return entry

    @classmethod
    def deserialize(cls, where: str, entry: object) -> "tuple[Mark | None, list[str]]":
        """One entry read as a `Mark`, or named problems -- its STRUCTURE only.

        The entry must be an object naming one of the seven instructions. Every
        other field is read as the type the record holds, and a field of another
        type is read as absent -- `""`, `{}` or `()`, and None for `change`. A
        field the instruction's row does not take is read the same way and
        never refused (`decision-log.md Process: #204`). Nothing is asked of
        the row: whether the mark keeps that row's rules is
        `desk.marks.rules.validate`'s question, and `read_mark` asks the two in
        order.

        ! CALL `untouched` FIRST where a coverage gap is legal. This function has
        no reading of a slot nobody ruled on other than a refusal, which is correct
        for a mark and wrong for a seeded row.

        Args:
            where: how to name this mark in a message -- an address, or a position.
            entry: one role's ruling on one place, as it came back.

        Returns:
            `(Mark, [])` or `(None, [one message])`. A `Mark` says the entry is a
            mark of a named instruction and says nothing about its rules.
        """
        if not isinstance(entry, dict):
            return None, [f"{where}: a mark must be an object"]
        data: dict = entry
        if "instruction" not in data:
            return None, [
                f"{where}: carries no `instruction` -- the field naming which of "
                f"{', '.join(sorted(INSTRUCTION_NAMES))} this mark is"
            ]
        named = data["instruction"]
        if not isinstance(named, str) or named not in INSTRUCTION_NAMES:
            return None, [
                f"{where}: `instruction` must be one of "
                f"{', '.join(sorted(INSTRUCTION_NAMES))}"
            ]

        instruction = Instruction(named)
        claim = data.get("claim")
        sources = data.get("sources")
        change = data.get("change")
        return (
            Mark(
                address=as_text(data.get("address")),
                anchor=as_text(data.get("anchor")),
                raw_text=as_text(data.get("raw_text")),
                instruction=instruction,
                # ! COPIED, NOT ALIASED -- a `Mark` is frozen, and sharing the
                # caller's own containers would leave it mutable through them.
                claim=dict(claim) if isinstance(claim, dict) else {},
                reason=as_text(data.get("reason")),
                sources=tuple(sources) if isinstance(sources, list) else (),
                change=change if isinstance(change, str) else None,
            ),
            [],
        )


#: A closed set a record field takes.
E = TypeVar("E", bound=StrEnum)


def read_member(
    where: str, name: str, value: object, kind: type[E]
) -> "tuple[E | None, list[str]]":
    """`value` as the member of `kind` it names, or one problem naming the field.

    Asked member by member, never as `value in kind`, which raises on Python
    3.11 for a value that is not a member.

    Args:
        where: how to name the record in a message.
        name: the field's own name, for the message.
        value: the field as it came back.
        kind: the closed set the field takes.

    Returns:
        `(member, [])`, or `(None, [one message naming the set])`.
    """
    for member in kind:
        if member == value:
            return member, []
    return None, [f"{where}: `{name}` {value!r} is not one of {', '.join(kind)}"]


def a_type(value: object) -> str:
    """`value`'s type name with its article -- "a str", "an int" -- for a message."""
    name = type(value).__name__
    return f"{'an' if name[:1] in 'aeiou' else 'a'} {name}"


def read_text(where: str, name: str, value: object) -> "tuple[str, list[str]]":
    """A string field a record uses: the string, or one problem naming the field.

    Absent or null reads as "", which is what the field says when nothing was
    given. Any other type is refused rather than turned into a string.
    """
    if value is None:
        return "", []
    if isinstance(value, str):
        return value, []
    return "", [f"{where}: `{name}` must be a string, not {a_type(value)}"]


def as_text(value: object) -> str:
    """A string field as a record holds it: the string, or "" for anything else.

    `decision-log.md Process: #204`: a field of the wrong type is read as absent.
    """
    return value if isinstance(value, str) else ""


#: A check of one mark against the rules its instruction's row states. Returns
#: one message per broken rule, in the order a reader meets them.
Validator = Callable[[str, "Mark"], list[str]]


def read_mark(
    where: str, entry: object, validate: Validator
) -> "tuple[Mark | None, list[str]]":
    """One entry read as a `Mark` and held to `validate`, or named problems.

    The structural read runs first, so an entry that is not an object or names
    no instruction is refused before any rule is asked.

    Args:
        where: how to name this mark in a message -- an address, or a position.
        entry: one role's ruling on one place, as it came back.
        validate: the rule check -- `desk.marks.rules.validate` wherever a
            flow or a command reads a copy or a proof.

    Returns:
        `(Mark, [])` or `(None, [one message per broken rule])`.
    """
    mark, why = Mark.deserialize(where, entry)
    if mark is None:
        return None, why
    problems = validate(where, mark)
    if problems:
        return None, problems
    return mark, []


#: The four fields a ROLE fills that `untouched` looks at. `address` and
#: `anchor` are seeded onto every slot, so neither says whether anyone wrote
#: here; `instruction` is the field being ruled on and is read separately.
ROLE_FIELDS = ("claim", "reason", "sources", "change")


def filled(value: object) -> TypeGuard[str]:
    """A string with something in it. ! An empty string is NOT an answer.

    Measured: a claim key present and empty passed every check that would have
    caught it missing, and each of those checks then skipped.

    ! RETURNS `TypeGuard[str]`, NOT A BARE `bool`, so a caller writing
    `if filled(x): use(x)` gets the same narrowing an inline
    `isinstance(x, str) and x.strip()` would have given it. `TypeGuard` is
    `typing`'s own, in the standard library since Python 3.10 -- this module's
    floor is 3.11 -- so this is not a third-party import.
    """
    return isinstance(value, str) and bool(value.strip())


def without_location(where: str, message: str) -> str:
    """One refusal with the `where` prefix this module put on it removed.

    !! EVERY MESSAGE HERE OPENS `f"{where}: "` -- fifteen sites -- so a caller
    with nowhere else to say which mark it is reads a self-describing sentence.
    A caller that records the location as its OWN FIELD does not, and printing
    both gave `block-context m.py@b1: m.py@b1: correct needs a reason`.
    `collate-command-defects` T3, measured on every line of the report the task
    agent reads.

    !! IT REMOVES WHAT THIS MODULE ADDED, which is what makes it a fact rather
    than a guess: the caller passes `where` in and hands the same `where` back,
    so the prefix is known rather than sniffed. A message that does not carry it
    is returned untouched.

    ! AND `tests/test_mark.py::TestAStoredReasonDoesNotRepeatItsLocator` is what
    keeps it true. Either half can rot silently -- a sixteenth message site
    spelling the prefix by hand, or this function drifting from the format --
    and the gate asks the only question that matters: does a reason a container
    stored begin with the locator that container already carries.

    Args:
        where: exactly what was handed to `Mark.deserialize` or
            `desk.collator.source_verification`.
        message: one refusal from that call.

    Returns:
        The message without its leading `f"{where}: "`, or unchanged.
    """
    prefix = f"{where}: "
    return message[len(prefix) :] if where and message.startswith(prefix) else message


def untouched(entry: object) -> bool:
    """A seeded slot no role has written in -- the COVERAGE GAP.

    !! THIS IS NOT "HAS NO INSTRUCTION", AND THE DIFFERENCE IS THE DEFECT THIS
    FUNCTION EXISTS FOR. `flows/distribute.py` read `mark.get("mark") is None` and
    skipped, so an entry a role HAD filled in but that named no instruction --
    or named it under a key the code did not read -- was dropped before any
    check saw it and recounted as a place nobody looked at. MEASURED
    2026-08-29: `reviewer-brief.md`'s own worked example, which keys the ruling
    `instruction`, passed the per-copy check at exit 0 as UNRULED.

    ! So an untouched slot is BOTH things at once: `instruction` present and
    null -- the key `seed()` writes -- AND none of `ROLE_FIELDS` filled. An
    entry that fails either half is a ruling, and goes to `read_mark`, which
    refuses it by name.

    Args:
        entry: one entry of a sheet's `marks`, as it came back.

    Returns:
        True only for a slot that is still exactly as `seed()` handed it out.
    """
    if not isinstance(entry, dict):
        return False
    data: dict = entry
    if "instruction" not in data or data["instruction"] is not None:
        return False
    return not any(data.get(key) for key in ROLE_FIELDS)
