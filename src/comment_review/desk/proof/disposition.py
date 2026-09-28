"""What the chief rules at a carried-forward place, or on an undecided move.

    ORIGINAL            the `side` that keeps the paragraph as it stands
    CHIEF               the chief's own `side`, and the chief's name as a role
    Disposition         one ruling; `name` is its row, `answer` on the wire
    read_disposition()  an entry read as a `Disposition`, then held to a validator

`Disposition.deserialize` reads an entry's structure: it refuses only an entry
that is not an object, and reads a field of the wrong type as absent
(`decision-log.md Process: #204`). Whether the ruling is one the chief may
give, and carries what its row owes, is `desk.dispositions.rules.validate`'s
question, which `read_disposition` asks after it.
"""

from collections.abc import Callable
from dataclasses import dataclass, fields

from comment_review.desk.proof.mark import as_text

ORIGINAL = "original"
CHIEF = "copy-chief"


@dataclass(frozen=True)
class Disposition:
    """One chief's ruling on one carried-forward place, or on one move's placement.

    `side` is "" where the entry named none; `desk.dispositions.rules.side_of`
    reads the side a ruling takes, the row's own where it fixes one.
    """

    address: str
    name: str
    side: str
    prose: str
    reason: str
    #: A placement ruling names the move by its two addresses, as a placement
    #: answer does: `address` is the origin and `to` the destination. Empty on
    #: a ruling at a place.
    to: str = ""

    def serialize(self) -> dict:
        """This ruling as a docket carries it, keyed by this class's own field names."""
        out = {f.name: getattr(self, f.name) for f in fields(self)}
        out["answer"] = out.pop("name")
        return out

    @classmethod
    def deserialize(
        cls, where: str, entry: object
    ) -> "tuple[Disposition | None, list[str]]":
        """One entry read as a `Disposition`, or named problems -- its structure."""
        if not isinstance(entry, dict):
            return None, [f"{where}: a ruling must be an object"]
        data: dict = entry
        return (
            cls(
                address=as_text(data.get("address")),
                name=as_text(data.get("answer")),
                side=as_text(data.get("side")),
                prose=as_text(data.get("prose")),
                reason=as_text(data.get("reason")),
                to=as_text(data.get("to")),
            ),
            [],
        )


#: A check of one ruling against the rules its row states. Returns one message
#: per broken rule, in the order a reader meets them.
DispositionValidator = Callable[[str, Disposition], list[str]]


def read_disposition(
    where: str, entry: object, validate: DispositionValidator
) -> "tuple[Disposition | None, list[str]]":
    """One entry read as a `Disposition` and held to `validate`, or named problems."""
    disposition, why = Disposition.deserialize(where, entry)
    if disposition is None:
        return None, why
    problems = validate(where, disposition)
    if problems:
        return None, problems
    return disposition, []
