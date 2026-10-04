"""A place: the aggregate the middle decides.

    Filed   one role's mark, filed at a place, and where the proof holds it
    Place   one address, its base text, and everything filed or ruled there

A mark is stored once on a master proof, in the edit_copy that carries it. A
place's filed entry points at it -- `{"copy", "sheet", "mark", "touch"}`, each
index counted from 1 as the proof's own messages count them -- and the role is
the copy's.
"""

from dataclasses import dataclass, field

from comment_review.desk.proof.answer import Answer, Question, read_answers
from comment_review.desk.proof.disposition import Disposition, read_disposition
from comment_review.desk.proof.edit_copy import EditCopy
from comment_review.desk.proof.mark import Mark, Touch, read_member
from comment_review.desk.proof.state import State

#: The keys of a filed entry's pointer, in the order they are written.
POINTER = ("copy", "sheet", "mark")


@dataclass
class Filed:
    """One role's mark, filed at a place, and which end of it this is about.

    Attributes:
        role: the role whose copy carries the mark.
        mark: the mark itself.
        touch: which of the places the mark writes this one is.
        source: where the proof holds the mark -- its copy, sheet and mark,
            each counted from 1 -- or None for a mark filed without a proof,
            which a place holding it cannot be written for.
    """

    role: str
    mark: Mark
    touch: Touch
    source: tuple[int, int, int] | None = None


@dataclass
class Place:
    """One address, its base text, and everything filed or ruled against it."""

    address: str
    anchor: str
    base: str
    #: The roles whose edit copies held this place's page. `flows.places.places_of`
    #: fills it from every copy's own sheets, and `desk.work.fold.Fold.run` reads
    #: it -- unioned with `place.sides` -- to name the roles a `CarriedForward`
    #: event sends a place back to when it composes or contests (not an
    #: escalation). Ruling R4, `decision-log.md Process: #116` and `#121`: an
    #: `add` is carried forward for every role that read the page.
    readers: tuple[str, ...] = ()
    filed: list[Filed] = field(default_factory=list)
    answers: dict[int, dict[str, Answer]] = field(default_factory=dict)
    disposition: Disposition | None = None
    state: State | None = None
    text: str | None = None
    sides: dict[str, str] = field(default_factory=dict)
    reasons: tuple[str, ...] = ()
    #: What the chief is told about the marks filed here without any of them
    #: being refused for it, as `"<role>: <note>"` -- the same shape `reasons`
    #: takes, read the same way. `desk.evaluate.passes.marks_pass` fills it
    #: from each row's `notes`, and it never decides a state
    #: (`decision-log.md Process: #177`).
    notes: tuple[str, ...] = ()
    #: The roles this place's text still owes a say to, in role order. A text
    #: settles only once every role that read the place has proposed it or
    #: accepted it (`decision-log.md Process: #180`), so a place carried
    #: forward names here who has not, and `desk.work.fold.asked` sends it to
    #: them. Empty on a place nothing is carried forward for.
    owed: tuple[str, ...] = ()
    question: Question | None = None

    def serialize(self) -> dict:
        """This place's own fields, as a dict keyed by this class's own field names."""
        return {
            "address": self.address,
            "anchor": self.anchor,
            "base": self.base,
            "readers": list(self.readers),
            "filed": [_pointer(self.address, f) for f in self.filed],
            "answers": {
                str(t): {r: a.serialize() for r, a in by.items()}
                for t, by in self.answers.items()
            },
            "disposition": self.disposition.serialize() if self.disposition else None,
            "state": str(self.state) if self.state else None,
            "text": self.text,
            "sides": dict(self.sides),
            "reasons": list(self.reasons),
            "notes": list(self.notes),
            "owed": list(self.owed),
            "question": str(self.question) if self.question else None,
        }

    @classmethod
    def deserialize(
        cls, where: str, entry: object, copies: tuple[EditCopy, ...]
    ) -> "tuple[Place | None, list[str]]":
        """One entry becomes a `Place`, or becomes named problems.

        Each filed entry is resolved to the mark `copies` already hold, which
        is not read again, and takes its role from the copy. Each answer and
        the chief's ruling is read into its own type.

        Args:
            where: how to name this place in a message.
            entry: one place, as `serialize` writes it.
            copies: the proof's edit_copies, already read.
        """
        if not isinstance(entry, dict):
            return None, [f"{where}: a place must be an object"]
        data: dict = entry
        problems: list[str] = []
        if data.get("asking"):
            problems.append(
                f"{where}: retired human-held asking lifecycle is not admitted"
            )
        filed = []
        for i, one in enumerate(data.get("filed") or [], 1):
            got, why = _resolved(f"{where} mark {i}", one, copies)
            if got is None:
                problems += why
            else:
                filed.append(got)
        answers, why = read_answers(where, data.get("answers"))
        problems += why
        disposition = None
        if data.get("disposition") is not None:
            disposition, why = read_disposition(where, data["disposition"])
            problems += why
        state = question = None
        if data.get("state"):
            state, why = read_member(where, "state", data["state"], State)
            problems += why
        if data.get("question"):
            question, why = read_member(where, "question", data["question"], Question)
            problems += why
        if problems:
            return None, problems
        return (
            cls(
                address=str(data.get("address") or ""),
                anchor=str(data.get("anchor") or ""),
                base=str(data.get("base") or ""),
                readers=tuple(data.get("readers") or ()),
                filed=filed,
                answers=answers,
                disposition=disposition,
                state=state,
                text=data.get("text"),
                sides=dict(data.get("sides") or {}),
                reasons=tuple(data.get("reasons") or ()),
                notes=tuple(data.get("notes") or ()),
                owed=tuple(data.get("owed") or ()),
                question=question,
            ),
            [],
        )


def _pointer(address: str, filed: Filed) -> dict:
    """One filed entry as the proof writes it: where its mark is, and the touch.

    Raises:
        ValueError: the mark was filed without a place on a proof to point at.
    """
    if filed.source is None:
        raise ValueError(
            f"{address}: {filed.role}'s {filed.mark.instruction} was filed with no"
            " place on the proof to point at"
        )
    return {**dict(zip(POINTER, filed.source, strict=True)), "touch": str(filed.touch)}


def _index(where: str, name: str, value: object) -> "tuple[int | None, list[str]]":
    """One pointer index: a whole number from 1, or one problem naming it."""
    if isinstance(value, int) and not isinstance(value, bool) and value >= 1:
        return value, []
    return None, [f"{where}: `{name}` {value!r} is not a whole number from 1"]


def _resolved(
    where: str, entry: object, copies: tuple[EditCopy, ...]
) -> "tuple[Filed | None, list[str]]":
    """One filed entry resolved against the proof's copies, or named problems.

    A mark written inline -- the whole mark on the place -- is refused by name:
    the copies are its one home.
    """
    if not isinstance(entry, dict):
        return None, [f"{where}: a filed entry must be an object"]
    data: dict = entry
    if "instruction" in data and not any(key in data for key in POINTER):
        return None, [
            f"{where}: a filed mark is written inline; a proof names its copy's"
            " mark by `copy`, `sheet` and `mark`"
        ]
    problems: list[str] = []
    indices: list[int] = []
    for key in POINTER:
        got, why = _index(where, key, data.get(key))
        problems += why
        if got is not None:
            indices.append(got)
    touch, why = read_member(where, "touch", data.get("touch"), Touch)
    problems += why
    if problems or touch is None:
        return None, problems
    c, s, m = indices
    try:
        copy = copies[c - 1]
        mark = copy.sheets[s - 1].marks[m - 1]
    except IndexError:
        return None, [
            f"{where}: copy {c}, sheet {s}, mark {m} names no mark on this proof"
        ]
    return Filed(copy.role, mark, touch, (c, s, m)), []
