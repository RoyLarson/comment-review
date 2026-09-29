"""What the chief rules at a carried-forward place, or on an undecided move.

    ORIGINAL            the `side` that keeps the paragraph as it stands
    CHIEF               the chief's own `side`, and the chief's name as a role
    Disposition         what every ruling carries, its wire entry and its read
    TakenInRuling       `taken_in`: one side's text, or the original, stands
    RecastRuling        `recast`: the chief's own prose stands
    RULINGS             the ruling types, for the message naming them
    disposition_type()  the type a ruling's name names -- the one dispatch
    read_disposition()  an entry read as the type its name names, or problems

A ruling's type owns its fields, its wire entry and every check on itself:
reading an entry into its type IS that check. What a ruling does at a place --
which states it closes, the text it sets -- is `desk.dispositions.table`'s.

A placement ruling is not a type of its own. It is a ruling of either name
that carries `to`, naming the move by its two addresses: the name says whose
text stands and `to` says which record it is for, and the move's own pass
decides what each name means there.
"""

from dataclasses import dataclass
from typing import Any, ClassVar, Self

from comment_review.desk.proof.answer import answer_type
from comment_review.desk.proof.mark import INSTRUCTION_NAMES, as_text, filled

ORIGINAL = "original"
CHIEF = "copy-chief"


@dataclass(frozen=True)
class Disposition:
    """What every chief's ruling carries, at a place or on a move's placement.

    Never built itself: a ruling is one of the types below.

    Attributes:
        address: the place, or a move's origin.
        side: the side named, "" where the entry named none -- `taken_side`
            is the side the ruling takes.
        reason: why, in prose.
        to: a placement ruling's destination, naming the move with `address`
            as a placement answer does. Empty on a ruling at a place.
    """

    address: str
    side: str
    reason: str
    to: str

    #: The ruling's name -- `answer` on the wire.
    name: ClassVar[str]
    #: The fields that must be filled, besides `address` and `reason`.
    owes: ClassVar[tuple[str, ...]]
    #: The side taken where the entry names none -- `CHIEF` on `recast`, ""
    #: where the ruling must name its own.
    default_side: ClassVar[str] = ""

    @property
    def taken_side(self) -> str:
        """The side this ruling takes: its own, or where it names none, its type's."""
        return self.side or self.default_side

    def _prose(self) -> str:
        """This ruling's `prose` as the wire carries it; "" where it takes none."""
        return ""

    def serialize(self) -> dict:
        """This ruling as a docket carries it; its name is `answer` on the wire."""
        return {
            "address": self.address,
            "side": self.side,
            "prose": self._prose(),
            "reason": self.reason,
            "to": self.to,
            "answer": self.name,
        }

    @classmethod
    def read(cls, where: str, data: dict) -> "tuple[Self | None, list[str]]":
        """One entry naming this ruling, read as this type.

        A field of the wrong type is read as absent, and a field this type does
        not take is ignored, never refused (`decision-log.md Process: #204`).

        Returns:
            `(ruling, [])`, or `(None, [one message per broken rule])`.
        """
        values = {
            key: as_text(data.get(key))
            for key in ("address", "side", "prose", "reason", "to")
        }
        out: list[str] = []
        if not filled(values["address"]):
            out.append(f"{where}: {cls.name} needs the `address`")
        if not filled(values["reason"]):
            out.append(f"{where}: {cls.name} needs a `reason`")
        out += [
            f"{where}: {cls.name} needs `{key}`"
            for key in cls.owes
            if not filled(values[key])
        ]
        if out:
            return None, out
        return (
            cls(
                address=values["address"],
                side=values["side"],
                reason=values["reason"],
                to=values["to"],
                **cls._own(values),
            ),
            [],
        )

    @classmethod
    def _own(cls, values: dict[str, str]) -> dict[str, Any]:
        """This type's own fields, from values already checked."""
        return {}


@dataclass(frozen=True)
class TakenInRuling(Disposition):
    """`taken_in`: the side it names -- a role's, or the original -- stands."""

    name: ClassVar[str] = "taken_in"
    owes: ClassVar[tuple[str, ...]] = ("side",)


@dataclass(frozen=True)
class RecastRuling(Disposition):
    """`recast`: the chief's own prose stands.

    Attributes:
        prose: the paragraph as the chief sets it.
    """

    prose: str

    name: ClassVar[str] = "recast"
    owes: ClassVar[tuple[str, ...]] = ("prose",)
    default_side: ClassVar[str] = CHIEF

    def _prose(self) -> str:
        return self.prose

    @classmethod
    def _own(cls, values: dict[str, str]) -> dict[str, Any]:
        return {"prose": values["prose"]}


#: The ruling types, for the message that names what the chief may give.
RULINGS: tuple[type[Disposition], ...] = (TakenInRuling, RecastRuling)


def disposition_type(name: str) -> type[Disposition] | None:
    """The type a ruling named `name` is read as, or None for no ruling."""
    match name:
        case "taken_in":
            return TakenInRuling
        case "recast":
            return RecastRuling
        case _:
            return None


def read_disposition(
    where: str, entry: object
) -> "tuple[Disposition | None, list[str]]":
    """One entry read as the type its name names, or named problems.

    An entry that is not an object is refused, and so is a name that is a
    role's instruction or answer, or no ruling's at all -- each as one message,
    with nothing else asked of it. Every other refusal is the type's own read.
    """
    if not isinstance(entry, dict):
        return None, [f"{where}: a ruling must be an object"]
    data: dict = entry
    name = as_text(data.get("answer"))
    if name in INSTRUCTION_NAMES or answer_type(name) is not None:
        return None, [
            f"{where}: `{name}` is a role's answer; the chief's ruling is owed here"
        ]
    kind = disposition_type(name)
    if kind is None:
        names = ", ".join(sorted(one.name for one in RULINGS))
        return None, [f"{where}: `answer` must be one of {names}"]
    return kind.read(where, data)
