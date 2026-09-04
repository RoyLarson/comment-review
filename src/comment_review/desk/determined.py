"""A PROTOTYPE. `Determined`: the copy chief's ruling at one resolved place.

!! NOTHING SHIPS THIS YET. `decision-log.md Process: #87` (Roy, 2026-09-04) is
the source: the chief's ruling is its own object, one per resolved place, on
the master proof beside the roles' copies and the turn record. Its three
answers are the chief's and no role's -- `Vocabulary: #29` named them, `#87`
says when each applies -- so this is not a `Mark` (`#22`, `#86`: a different
question gets a different artifact) and not a `DiffMark`. Roy: *"stet,
taken_in, and the third one are not rulings that fit the other roles and so
should not be added to the Mark class. That makes it a different object."*

    stet        the roles agreed, on a turn or at once; the chief lets it
                stand. The program sets this one on the chief's behalf
    taken_in    they never agreed; at the cap the chief takes one side's text
                in. THE ORIGINAL AUTHOR IS A SIDE
    recast      they never agreed; the chief writes its own prose over every
                side

`how` says what the agreement was, or that there was none:

    one         a single owing mark, nothing to agree with
    identical   two or more owing marks, byte-identical
    withdrawn   every mark at a contested place was withdrawn, so the
                original stands -- `side` is ORIGINAL and `mark` None
    cap         no agreement; the chief ruled

The chief's `edit_copy` is DERIVED from these -- `flows.collate._chief_copy`
-- one mark per place, the shape `Process: #30` ruled, so the write end reads
what it read before. `mark` is what stands: a role's mark, the chief's own
`correct` for a recast, or None where the original stands.

! `side` NAMES WHOSE TEXT STANDS: a role, `ORIGINAL`, or `CHIEF` for a
recast. `Mark` carries no role, which is why the name rides here.
"""

from dataclasses import dataclass, fields
from enum import StrEnum, auto

from comment_review.desk.diff_mark import DiffInstruction
from comment_review.desk.mark import INSTRUCTIONS, Mark, filled


class Answer(StrEnum):
    """The chief's three, closed.

    `Vocabulary: #29` names them; `Process: #87` says when each applies.

    ! Value derived from the member name, following `desk.mark.Instruction`'s
    precedent -- `Answer.TAKEN_IN == "taken_in"` holds without a hand-typed
    string.
    """

    @staticmethod
    def _generate_next_value_(
        name: str, start: int, count: int, last_values: list[str]
    ) -> str:
        return name.lower()

    STET = auto()
    TAKEN_IN = auto()
    RECAST = auto()


#: The side whose text stands when the chief takes the ORIGINAL in.
ORIGINAL = "original"
#: The side on a `recast` -- the chief wrote the prose.
CHIEF = "copy-chief"
#: How the place came to its answer, closed.
HOW = ("one", "identical", "withdrawn", "cap")


@dataclass(frozen=True)
class Determined:
    """One resolved place, and how it was resolved.

    Attributes:
        address: `path@cue`. WHICH PLACE.
        answer: one of the three, as an `Answer` member.
        turn: which turn of the stage's collate it landed on -- 0 for the
            first fold. T20's counter is this field over every place.
        side: whose text stands -- a role, `ORIGINAL`, or `CHIEF`.
        how: one of `HOW`.
        reason: the chief's, in prose. Owed for `taken_in` and `recast`;
            empty for a `stet`, which the program sets.
        mark: what stands, as the `Mark` the chief's copy carries at this
            place. None where the original stands.
    """

    address: str
    answer: Answer
    turn: int
    side: str
    how: str
    reason: str
    mark: Mark | None

    def serialize(self) -> dict:
        """This ruling as the wire entry a master proof carries.

        Returns:
            A dict `deserialize` accepts and returns an equal `Determined` from.
        """
        entry = {f.name: getattr(self, f.name) for f in fields(self)}
        entry["answer"] = str(self.answer)
        entry["mark"] = self.mark.serialize() if self.mark is not None else None
        return entry

    @classmethod
    def deserialize(
        cls, where: str, entry: object, roles: frozenset[str] | None = None
    ) -> "tuple[Determined | None, list[str]]":
        """THE BOUNDARY -- one entry becomes a `Determined`, or becomes named problems.

        !! A ROLE'S ANSWER IS REFUSED HERE, BY NAME. An `answer` naming one of
        `Mark`'s seven or `DiffMark`'s four means a role's instruction reached
        the chief's record, and this says so rather than reading it as
        malformed.

        !! `side` AND `mark` ARE HELD TO THE ATTRIBUTES ABOVE -- T31, found by a
        role reviewing this file in the game: a null `mark` stands only for
        `ORIGINAL`, a `recast`'s side is `CHIEF`, and a side is a role where
        the roles are known.

        Args:
            where: how to name this ruling in a message.
            entry: one ruling, as it came off the wire.
            roles: the stage's roles, where the caller knows them; a `side`
                outside them, `ORIGINAL` and `CHIEF` is refused. None admits
                any non-empty name, for a boundary read without a stage.

        Returns:
            `(Determined, [])` or `(None, [one message per broken rule])`.
        """
        if not isinstance(entry, dict):
            return None, [f"{where}: a ruling must be an object"]
        data: dict = entry
        named = data.get("answer")
        if isinstance(named, str) and (
            named in INSTRUCTIONS or named in set(DiffInstruction)
        ):
            return None, [
                f"{where}: `{named}` is a role's answer, not one of "
                f"{', '.join(sorted(Answer))} -- the chief's ruling is owed here"
            ]
        if not isinstance(named, str) or named not in set(Answer):
            return None, [
                f"{where}: `answer` must be one of {', '.join(sorted(Answer))}"
            ]
        answer = Answer(named)
        out: list[str] = []
        if not filled(data.get("address")):
            out.append(f"{where}: {answer} needs the `address`")
        turn = data.get("turn")
        if not isinstance(turn, int) or isinstance(turn, bool) or turn < 0:
            out.append(f"{where}: {answer} needs `turn` as a count from 0")
        side = data.get("side")
        if not filled(side):
            out.append(f"{where}: {answer} needs `side` -- whose text stands")
        elif roles is not None and side not in roles | {ORIGINAL, CHIEF}:
            out.append(
                f"{where}: `side` {side!r} is none of the roles, {ORIGINAL!r} or "
                f"{CHIEF!r}"
            )
        if answer is Answer.RECAST and filled(side) and side != CHIEF:
            out.append(f"{where}: a recast's `side` is {CHIEF!r} -- the chief wrote it")
        if data.get("how") not in HOW:
            out.append(f"{where}: {answer} needs `how` as one of {', '.join(HOW)}")
        if answer is not Answer.STET and not filled(data.get("reason")):
            out.append(f"{where}: {answer} is the chief's and needs a `reason`")
        raw_mark = data.get("mark")
        mark: Mark | None = None
        if raw_mark is not None:
            mark, why = Mark.deserialize(f"{where}: mark", raw_mark)
            out += why
        elif answer is Answer.RECAST:
            out.append(f"{where}: recast needs the chief's own `mark`")
        elif side != ORIGINAL:
            out.append(
                f"{where}: a null `mark` stands only for the original -- `side` is "
                f"{side!r}"
            )
        if out:
            return None, out
        return (
            Determined(
                address=str(data["address"]),
                answer=answer,
                turn=int(turn) if isinstance(turn, int) else 0,
                side=str(data["side"]),
                how=str(data["how"]),
                reason=str(data.get("reason") or ""),
                mark=mark,
            ),
            [],
        )
