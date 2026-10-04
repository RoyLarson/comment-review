"""The mark: one role's ruling on one place, one type per instruction.

    Instruction        the seven, closed -- a StrEnum, value DERIVED from name
    INSTRUCTION_NAMES  tuple(Instruction) -- what membership is asked of
    Shape              the three a `query` must name, closed -- a StrEnum
    QUERY_SHAPES       tuple(Shape), in the order `docs/the-mark.md` states them
    Touch              which of the places a mark writes is being asked about
    Mark               what every mark carries, its wire entry and its read
    Amendment          a mark that proposes a text, and so carries a `change`
    CleanMark .. MoveMark  one type per instruction, each holding its own claim
    mark_type()        the type an instruction names -- the one dispatch
    read_mark()        an entry read as the type its instruction names, or
                       named problems
    BlankMark          a seeded slot no role has written in
    untouched()        whether an entry is still exactly a `BlankMark`'s entry
    ANCHOR_NAME        the form an `add`'s anchor is named in, and its example
    filled()           a string with something in it
    as_text()          a string field as a record holds it
    read_text()        a string field a record uses, or a problem
    a_type()           a value's type, with its article, for a message
    read_member()      a closed-set field as a record holds it, or a problem
    without_location() one refusal with its `where` prefix removed

A mark's type owns its fields, its wire entry and every check that needs no
page: reading an entry into its type IS that check, so a mark that exists has
passed it. What a mark does at a place -- the text it sets, what it reads
against the page, how it pairs -- is the marks table's, in `desk.marks`.

The wire entry is the same for every type: `docs/the-mark.md`'s eight fields,
with the per-instruction claim written as one `claim` object. `Mark.FIELDS` is
that list, in order, and `serialize` writes exactly those keys.

! `INSTRUCTION` NAMES THE ENUM. Each member's value is DERIVED from its name
via `_generate_next_value_`, never hand-typed. No site here asks membership of
an enum class directly (`x in SomeEnum` raises `TypeError` on Python 3.11) --
`INSTRUCTION_NAMES` is the membership check for `Instruction`, and
`QUERY_SHAPES` is `Shape`'s companion tuple.
"""

import re
from dataclasses import dataclass, fields
from enum import StrEnum, auto
from typing import Any, ClassVar, Self, TypeGuard, TypeVar

from comment_review.desk.proof.source import problems as source_entry_problems
from comment_review.reading.addresser import cue_of, folded


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


#: What an `add`'s claim must carry: the anchor, NAMED. Backticks are the repo's
#: citation form, so "named" is checkable without guessing which token is an
#: identifier.
ANCHOR_NAME = re.compile(r"`[^`\s][^`]*`")
#: Published with the pattern above, so the example a role is shown and the
#: form it is held to are one string.
ANCHOR_EXAMPLE = "`compute_rates`"


@dataclass(frozen=True)
class Mark:
    """What every mark carries, whatever its instruction.

    Never built itself: a mark is one of the seven types below, and each adds
    its own claim fields. The class attributes are the facts about an
    instruction that its own read needs -- the classifiers `docs/the-mark.md`
    states for it -- and each type sets the ones that differ from these.

    Attributes:
        address: `path@cue`. WHICH PLACE -- seeded, copied from the row, never
            built. Empty only on a `clean`, the one type `substantive` is False
            for.
        anchor: the line of code the place sits on -- seeded, and empty where
            the gather resolved none.
        raw_text: the paragraph as it stands -- seeded -- or, on the types the
            marks table says carry their own, the paragraph as it will read.
            ! CARRIED, NEVER TRUSTED AS THE BASE: the page's text at the
            place is.
        reason: WHY, in prose. No checker settles it.
        sources: `{cite, verbatim}` pairs, each optionally carrying `ran`.
            ! TYPED `object` AND NOT `dict` ON PURPOSE: on a type that owes no
            sources an entry that is not a pair is carried, not dropped, so
            `desk.collator.source_problems` can refuse it by name.
    """

    address: str
    anchor: str
    raw_text: str
    reason: str
    sources: tuple[object, ...]

    #: Which of the seven this type is.
    instruction: ClassVar[Instruction]
    #: Every key the wire `claim` must carry, in the order the spec lists them.
    claim_all: ClassVar[tuple[str, ...]] = ()
    #: The one claim key checked word-for-word against the paragraph, or "".
    quotes_original: ClassVar[str] = ""
    #: The claim key naming the address a destination touch writes at, or "".
    names_destination: ClassVar[str] = ""
    #: Whether the destination is asked to be an addressable place other than
    #: this mark's own. Derived from `names_destination`, never set by a type.
    owes_destination: ClassVar[bool] = False
    #: Whether a `change` is owed -- True on every `Amendment`.
    owes_change: ClassVar[bool] = False
    owes_sources: ClassVar[bool] = True
    #: Whether an `address` and a `reason` are owed. False on `clean` alone.
    substantive: ClassVar[bool] = True
    #: Whether an empty `change` is the edit rather than a missing one.
    may_empty: ClassVar[bool] = False
    #: Whether the claim's `anchor` must be named in backticks.
    needs_anchor: ClassVar[bool] = False

    #: The wire entry's keys, in `docs/the-mark.md`'s order. `serialize` writes
    #: exactly these, leaving `change` off a type that carries none.
    #:
    #: ! NOT ANNOTATED, DELIBERATELY: it is a fact about the wire, not a field
    #: of any type, and `dataclasses.fields` sees only annotated names.
    FIELDS = (
        "address",
        "anchor",
        "raw_text",
        "instruction",
        "claim",
        "reason",
        "sources",
        "change",
    )

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Derive `owes_destination`, and refuse a key `claim_all` does not name.

        Raises:
            TypeError: `quotes_original` or `names_destination` names a key
                the type's `claim_all` does not carry.
        """
        super().__init_subclass__(**kwargs)
        cls.owes_destination = bool(cls.names_destination)
        for key in (cls.quotes_original, cls.names_destination):
            if key and key not in cls.claim_all:
                raise TypeError(
                    f"{cls.__name__} names `{key}`, which its claim keys do not carry"
                )

    @property
    def quoted(self) -> str:
        """The clause this mark quotes from the paragraph, or "" for none."""
        return ""

    @property
    def destination(self) -> str:
        """The address this mark sends its paragraph to, or "" for none."""
        return ""

    def _claim(self) -> dict:
        """This mark's claim as the wire's `claim` object."""
        return {}

    def _change(self) -> str | None:
        """This mark's `change`, or None for a type that carries none."""
        return None

    def serialize(self) -> dict:
        """This mark as the wire entry a sheet carries.

        Returns:
            A dict `read_mark` accepts and returns an equal mark from, keyed
            and ordered by `FIELDS`. `instruction` is its string value; a type
            that carries no `change` writes none.
        """
        wire = {
            "address": self.address,
            "anchor": self.anchor,
            "raw_text": self.raw_text,
            "instruction": str(self.instruction),
            "claim": self._claim(),
            "reason": self.reason,
            "sources": list(self.sources),
            "change": self._change(),
        }
        return {name: wire[name] for name in self.FIELDS if wire[name] is not None}

    @classmethod
    def read(cls, where: str, data: dict) -> "tuple[Self | None, list[str]]":
        """One entry naming this type's instruction, read as this type.

        Every field is read as the type the mark holds, and a field of another
        type is read as absent. A field this type does not take is ignored,
        never refused (`decision-log.md Process: #204`). Then every check that
        needs no page is asked, in the order a reader meets the fields.

        What is NOT checked here, because it needs the page the role read:
        whether the address resolves, and whether a quoted clause is really in
        the paragraph. An absent `raw_text` is not refused: it is seeded, and
        the base a mark is measured against is never this field.

        Args:
            where: how to name this mark in a message -- an address, or a
                position. Every message opens with it.
            data: the entry, already known to be an object naming this type's
                instruction -- `read_mark` is the caller.

        Returns:
            `(mark, [])`, or `(None, [one message per broken rule])`.
        """
        address = as_text(data.get("address"))
        anchor = as_text(data.get("anchor"))
        reason = as_text(data.get("reason"))
        given = data.get("claim")
        # ! COPIED, NOT ALIASED -- a mark is frozen, and its fields must not be
        # reachable through the caller's own containers.
        claim: dict = dict(given) if isinstance(given, dict) else {}
        listed = data.get("sources")
        sources = tuple(listed) if isinstance(listed, list) else ()
        written = data.get("change")
        change = written if isinstance(written, str) else None

        out: list[str] = []
        if cls.substantive and not filled(address):
            out.append(
                f"{where}: {cls.instruction} needs the `address`, copied from the row"
            )
        elif cls.substantive and not _names_a_place(address):
            out.append(
                f"{where}: {cls.instruction} needs its full `path@cue` address,"
                f" copied from the row -- {address!r} names a place on no page"
            )
        if cls.substantive and not filled(reason):
            out.append(f"{where}: {cls.instruction} needs a `reason`")
        out += cls._claim_problems(where, claim)
        out += cls._destination_problems(where, address, claim)
        if cls.owes_sources:
            out += _source_problems(where, sources)
        else:
            out += source_entry_problems(where, sources)
        if cls.owes_change:
            out += _change_problems(
                where, cls.instruction, cls.may_empty, change, anchor
            )
        if out:
            return None, out
        own = cls._own(claim, change)
        return (
            cls(
                address=address,
                anchor=anchor,
                raw_text=as_text(data.get("raw_text")),
                reason=reason,
                sources=sources,
                **own,
            ),
            [],
        )

    @classmethod
    def _own(cls, claim: dict, change: str | None) -> dict[str, Any]:
        """This type's own fields, from a claim and a change already checked."""
        return {}

    @classmethod
    def _claim_problems(cls, where: str, claim: dict) -> list[str]:
        """Whether `claim` carries, filled, every key in `claim_all`."""
        if not cls.claim_all:
            return []
        missing = [k for k in cls.claim_all if not filled(claim.get(k))]
        if not missing:
            return []
        return [
            f"{where}: {cls.instruction} needs `claim` to carry "
            f"{', '.join(cls.claim_all)} (missing {', '.join(missing)})"
        ]

    @classmethod
    def _destination_problems(cls, where: str, address: str, claim: dict) -> list[str]:
        """Whether the destination the claim names is a place. None to ask here."""
        return []


@dataclass(frozen=True)
class Amendment(Mark):
    """A mark that proposes a text for its place, and so carries a `change`.

    Attributes:
        change: the RESULT -- the updated paragraph, as RAW TEXT. Empty on a
            `drop` whose claim names the whole paragraph, where an empty
            change IS the edit. On a `move` it is the snippet that leaves the
            origin, and on an `add` the text that arrives.
    """

    change: str

    owes_change: ClassVar[bool] = True

    def _change(self) -> str | None:
        return self.change


@dataclass(frozen=True)
class CleanMark(Mark):
    """`clean`: the role read the paragraph and has nothing to report.

    The one type that owes no address, no reason, no claim and no sources.
    """

    instruction: ClassVar[Instruction] = Instruction.CLEAN
    owes_sources: ClassVar[bool] = False
    substantive: ClassVar[bool] = False


@dataclass(frozen=True)
class QueryMark(Mark):
    """`query`: the role could not settle the place, and says who can.

    Attributes:
        shape: who resolves it -- one of `QUERY_SHAPES`.
        attempted: what the role did before it asked.
        settles: what would settle the place.
    """

    shape: Shape
    attempted: str
    settles: str

    instruction: ClassVar[Instruction] = Instruction.QUERY
    claim_all: ClassVar[tuple[str, ...]] = ("shape", "attempted", "settles")

    def _claim(self) -> dict:
        return {
            "shape": str(self.shape),
            "attempted": self.attempted,
            "settles": self.settles,
        }

    @classmethod
    def _own(cls, claim: dict, change: str | None) -> dict[str, Any]:
        return {
            "shape": Shape(claim["shape"]),
            "attempted": claim["attempted"],
            "settles": claim["settles"],
        }

    @classmethod
    def _claim_problems(cls, where: str, claim: dict) -> list[str]:
        """The keys, and `shape` one of the three -- a flow routes on it."""
        out = super()._claim_problems(where, claim)
        if claim.get("shape") not in QUERY_SHAPES:
            out.append(
                f"{where}: {cls.instruction} needs `claim.shape` to be one of "
                + ", ".join(QUERY_SHAPES)
            )
        return out


@dataclass(frozen=True)
class DropMark(Amendment):
    """`drop`: a clause comes out of the paragraph.

    Attributes:
        drop: the clause removed, verbatim -- the whole paragraph where the
            `change` is empty.
    """

    drop: str

    instruction: ClassVar[Instruction] = Instruction.DROP
    claim_all: ClassVar[tuple[str, ...]] = ("drop",)
    quotes_original: ClassVar[str] = "drop"
    may_empty: ClassVar[bool] = True

    @property
    def quoted(self) -> str:
        """`claim.drop`."""
        return self.drop

    def _claim(self) -> dict:
        return {"drop": self.drop}

    @classmethod
    def _own(cls, claim: dict, change: str | None) -> dict[str, Any]:
        return {"drop": claim["drop"], "change": change}


@dataclass(frozen=True)
class CorrectMark(Amendment):
    """`correct`: a false clause is replaced by a true one.

    Attributes:
        false: the clause as it stands, verbatim.
        true: the clause as it should read.
    """

    false: str
    true: str

    instruction: ClassVar[Instruction] = Instruction.CORRECT
    claim_all: ClassVar[tuple[str, ...]] = ("false", "true")
    quotes_original: ClassVar[str] = "false"

    @property
    def quoted(self) -> str:
        """`claim.false`."""
        return self.false

    def _claim(self) -> dict:
        return {"false": self.false, "true": self.true}

    @classmethod
    def _own(cls, claim: dict, change: str | None) -> dict[str, Any]:
        return {"false": claim["false"], "true": claim["true"], "change": change}


@dataclass(frozen=True)
class PatchMark(Amendment):
    """`patch`: a true clause is reworded. It owes no sources.

    Attributes:
        from_: the clause as it stands, verbatim -- the wire's `claim.from`.
        to: the rewording.
    """

    from_: str
    to: str

    instruction: ClassVar[Instruction] = Instruction.PATCH
    claim_all: ClassVar[tuple[str, ...]] = ("from", "to")
    quotes_original: ClassVar[str] = "from"
    owes_sources: ClassVar[bool] = False

    @property
    def quoted(self) -> str:
        """`claim.from`."""
        return self.from_

    def _claim(self) -> dict:
        return {"from": self.from_, "to": self.to}

    @classmethod
    def _own(cls, claim: dict, change: str | None) -> dict[str, Any]:
        return {"from_": claim["from"], "to": claim["to"], "change": change}


@dataclass(frozen=True)
class AddMark(Amendment):
    """`add`: text the place is missing arrives there.

    `change` is the text that arrives and `raw_text` the paragraph as it will
    read, with that text in.

    Attributes:
        missing: what the place is missing.
        named_anchor: the anchor the text belongs to, NAMED in backticks --
            the wire's `claim.anchor`, which is not the mark's own `anchor`.
    """

    missing: str
    named_anchor: str

    instruction: ClassVar[Instruction] = Instruction.ADD
    claim_all: ClassVar[tuple[str, ...]] = ("missing", "anchor")
    needs_anchor: ClassVar[bool] = True

    def _claim(self) -> dict:
        return {"missing": self.missing, "anchor": self.named_anchor}

    @classmethod
    def _own(cls, claim: dict, change: str | None) -> dict[str, Any]:
        return {
            "missing": claim["missing"],
            "named_anchor": claim["anchor"],
            "change": change,
        }

    @classmethod
    def _claim_problems(cls, where: str, claim: dict) -> list[str]:
        """The keys, and the anchor named in the form `ANCHOR_NAME` states."""
        out = super()._claim_problems(where, claim)
        if not ANCHOR_NAME.search(str(claim.get("anchor", ""))):
            out.append(
                f"{where}: {cls.instruction} needs the anchor NAMED in backticks,"
                f" e.g. {ANCHOR_EXAMPLE}"
            )
        return out


@dataclass(frozen=True)
class MoveMark(Amendment):
    """`move`: a snippet leaves this place and arrives at another.

    `change` is the snippet subtracted from the origin, and `raw_text` the
    destination paragraph as it will read, with the snippet in.

    Attributes:
        from_: the wire's `claim.from`.
        to: the destination -- a `path@cue` place other than this mark's own.
    """

    from_: str
    to: str

    instruction: ClassVar[Instruction] = Instruction.MOVE
    claim_all: ClassVar[tuple[str, ...]] = ("from", "to")
    names_destination: ClassVar[str] = "to"

    @property
    def destination(self) -> str:
        """`claim.to`."""
        return self.to

    def _claim(self) -> dict:
        return {"from": self.from_, "to": self.to}

    @classmethod
    def _own(cls, claim: dict, change: str | None) -> dict[str, Any]:
        return {"from_": claim["from"], "to": claim["to"], "change": change}

    @classmethod
    def _destination_problems(cls, where: str, address: str, claim: dict) -> list[str]:
        """WHERE the paragraph goes, checked against where it already IS.

        A destination equal to the origin is refused: its two ends are one
        address, so the delete at the origin lands with no write to put the
        paragraph back. A destination is a `path@cue` place, for now
        (`decision-log.md Process: #173`); whether the page carries that place
        needs the page, and is `flows.verify.resolution_problems`'.

        A destination that is not a string says nothing here --
        `_claim_problems` refuses a missing one, and there is nothing to
        compare.
        """
        key = cls.names_destination
        destination = claim.get(key)
        if not isinstance(destination, str):
            return []
        # Folded, not compared as typed: a destination differing from the origin
        # only in case or surrounding whitespace names the same paragraph on a
        # file system that ignores case.
        if folded(destination) and folded(destination) == folded(address):
            return [
                f"{where}: `claim.{key}` is this mark's own `address` -- a move to "
                "where the paragraph already is deletes it and writes nothing back"
            ]
        # PROVISIONAL, `decision-log.md Process: #173`: a destination that is not
        # a `path@cue` place is carried by neither the fold nor the write end.
        if destination.strip() and not _names_a_place(destination):
            return [
                f"{where}: `claim.{key}` {destination!r} is not a `path@cue` place"
                " -- a destination on a gathered page is its full address, as the"
                " addresser prints it, and one outside the code is not carried yet"
                " (`decision-log.md Process: #173`): file a `human-review-necessary`"
                " query here naming it instead"
            ]
        return []


def mark_type(instruction: Instruction) -> type[Mark]:
    """The type a mark of `instruction` is read as and built as."""
    match instruction:
        case Instruction.CLEAN:
            return CleanMark
        case Instruction.QUERY:
            return QueryMark
        case Instruction.DROP:
            return DropMark
        case Instruction.CORRECT:
            return CorrectMark
        case Instruction.PATCH:
            return PatchMark
        case Instruction.ADD:
            return AddMark
        case Instruction.MOVE:
            return MoveMark


def read_mark(where: str, entry: object) -> "tuple[Mark | None, list[str]]":
    """One entry read as the type its instruction names, or named problems.

    An entry that is not an object, or names none of the seven, cannot be read
    at all and is refused here; every other refusal is the type's own read.

    ! CALL `untouched` FIRST where a coverage gap is legal. A seeded slot names
    no instruction, and this function has no reading of it other than a
    refusal -- correct for a mark and wrong for a slot nobody ruled on.

    Args:
        where: how to name this mark in a message -- an address, or a position.
        entry: one role's ruling on one place, as it came back.

    Returns:
        `(mark, [])` or `(None, [one message per broken rule])`.
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
    return mark_type(Instruction(named)).read(where, data)


@dataclass(frozen=True)
class BlankMark:
    """A slot seeded for a role and not yet ruled on -- it names no instruction.

    Its fields are the three every mark is seeded with, under the same names,
    so a role that fills the slot in hands back an entry `read_mark` reads
    those three from.

    Attributes:
        address: `path@cue`, composed by `reading.addresser.address_for`.
        anchor: the line of code the place sits on, or "".
        raw_text: the paragraph as it stands.
    """

    address: str
    anchor: str
    raw_text: str

    def serialize(self) -> dict:
        """The slot as a role receives it, with `instruction: None`.

        `instruction: None` is what `untouched` reads to say nobody has
        written here.
        """
        row: dict = {f.name: getattr(self, f.name) for f in fields(self)}
        row["instruction"] = None
        return row


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


#: The four fields a ROLE fills that `untouched` looks at. `address` and
#: `anchor` are seeded onto every slot, so neither says whether anyone wrote
#: here; `instruction` is the field being ruled on and is read separately.
ROLE_FIELDS = ("claim", "reason", "sources", "change")


def filled(value: object) -> TypeGuard[str]:
    """A string with something in it. ! An empty string is NOT an answer.

    A claim key present and empty would otherwise pass every check that asks
    whether it is there.

    ! RETURNS `TypeGuard[str]`, NOT A BARE `bool`, so a caller writing
    `if filled(x): use(x)` gets the same narrowing an inline
    `isinstance(x, str) and x.strip()` would have given it.
    """
    return isinstance(value, str) and bool(value.strip())


def without_location(where: str, message: str) -> str:
    """One refusal with the `where` prefix a mark's read put on it removed.

    Every message a read here produces opens `f"{where}: "`, so a caller with
    nowhere else to say which mark it is reads a self-describing sentence. A
    caller that records the location as its OWN FIELD does not want it twice.

    It removes what the read added, which is what makes it a fact rather than a
    guess: the caller passes `where` in and hands the same `where` back, so the
    prefix is known rather than sniffed. A message that does not carry it is
    returned untouched. `tests/test_mark.py::TestAStoredReasonDoesNotRepeatItsLocator`
    holds the two halves together.

    Args:
        where: exactly what was handed to `read_mark` or
            `desk.collator.source_verification`.
        message: one refusal from that call.

    Returns:
        The message without its leading `f"{where}: "`, or unchanged.
    """
    prefix = f"{where}: "
    return message[len(prefix) :] if where and message.startswith(prefix) else message


def untouched(entry: object) -> bool:
    """A seeded slot no role has written in -- the COVERAGE GAP.

    !! THIS IS NOT "HAS NO INSTRUCTION". An entry a role HAS filled in but that
    names no instruction -- or names it under a key the code does not read --
    is a ruling, and goes to `read_mark`, which refuses it by name. Reading it
    as untouched would drop it before any check saw it and count it as a place
    nobody looked at.

    ! So an untouched slot is BOTH things at once: `instruction` present and
    null -- the key `BlankMark.serialize` writes -- AND none of `ROLE_FIELDS`
    filled.

    Args:
        entry: one entry of a sheet's `marks`, as it came back.

    Returns:
        True only for a slot that is still exactly as it was seeded.
    """
    if not isinstance(entry, dict):
        return False
    data: dict = entry
    if "instruction" not in data or data["instruction"] is not None:
        return False
    return not any(data.get(key) for key in ROLE_FIELDS)


def _names_a_place(value: object) -> bool:
    """Whether `value` is a `path@cue` address -- a page, and a place on it.

    `reading.addresser.cue_of` is the one parse of an address, and it answers
    two blanks for anything that is not one, a bare cue included. Whether it is
    spelled as the page prints it is `flows.verify.resolution_problems`'
    question.
    """
    if not isinstance(value, str):
        return False
    got = cue_of(value)
    return bool(got.path.strip() and got.cue.strip())


def _source_problems(where: str, sources: tuple[object, ...]) -> list[str]:
    """Each source is a `{cite, verbatim}` pair, and may carry `ran`.

    !! PAIRS, NOT STRINGS. A `path:line | text` string reads for a human and
    cannot be checked -- nothing can confirm the verbatim string sits near the
    cited line.

    ! `ran` is the command that SETTLED the claim, for a claim settled by
    running something; `sources` otherwise records WHAT was seen and never HOW.
    """
    if not sources:
        return [f"{where}: needs at least one source"]
    return source_entry_problems(where, sources)


def _change_problems(
    where: str,
    instruction: Instruction,
    may_empty: bool,
    change: str | None,
    anchor: str,
) -> list[str]:
    """Whether `change` is the updated paragraph, as RAW TEXT.

    A `change` that is absent or not a string -- a line array among them -- is
    refused with the one message that names what is owed: the paragraph as
    RAW TEXT. An empty string is the edit only where `may_empty`; whitespace
    alone is never content. A `change` holding a line equal to the mark's
    `anchor`, whitespace aside, is refused: the anchor is the line of code the
    place sits on, and a change is the paragraph alone.
    """
    if change is None:
        return [
            f"{where}: {instruction} needs `change` as the updated paragraph in "
            "RAW TEXT"
        ]
    if not filled(change) and not may_empty:
        return [f"{where}: {instruction} needs `change` to hold the new text"]
    if filled(anchor) and anchor.strip() in (
        line.strip() for line in change.splitlines()
    ):
        return [
            f"{where}: {instruction}'s `change` carries the anchor's own line of "
            f"code, {anchor.strip()!r} -- `change` is the paragraph alone"
        ]
    return []
