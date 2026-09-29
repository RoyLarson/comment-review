"""A place: the aggregate the middle decides."""

from dataclasses import dataclass, field

from comment_review.desk.proof.answer import Answer, Question, read_answers
from comment_review.desk.proof.disposition import Disposition, read_disposition
from comment_review.desk.proof.mark import Mark, Touch, read_mark, read_member
from comment_review.desk.proof.state import State
from comment_review.desk.proof.validators import Validators


@dataclass
class Filed:
    """One role's mark, filed at a place, and which end of it this is about."""

    role: str
    mark: Mark
    touch: Touch
    #: The origin address of the agreed move this mark is a half of, set by
    #: `desk.evaluate.move.settle_ends` when it splits the move. A reason names
    #: the move the role filed rather than a half it never wrote. Empty for a
    #: mark the role filed itself.
    split_from: str = ""


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
    #: Who put this place to the human and why, as `"<role>: <reason>"` -- the
    #: shape `reasons` and `notes` take. The pass that sets `UNSETTLABLE` fills
    #: it, from the query that asked or from the answer that did, and
    #: `desk.work.fold.Fold.run` reports one entry per line
    #: (`decision-log.md Process: #90`).
    asking: tuple[str, ...] = ()
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
            "filed": [
                {
                    "role": f.role,
                    "touch": str(f.touch),
                    "split_from": f.split_from,
                    **f.mark.serialize(),
                }
                for f in self.filed
            ],
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
            "asking": list(self.asking),
            "owed": list(self.owed),
            "question": str(self.question) if self.question else None,
        }

    @classmethod
    def deserialize(
        cls, where: str, entry: object, validators: Validators
    ) -> "tuple[Place | None, list[str]]":
        """One entry becomes a `Place`, or becomes named problems.

        Each filed mark and each answer is read into its own type, and the
        chief's ruling by its own reader, held to `validators.disposition`.
        """
        if not isinstance(entry, dict):
            return None, [f"{where}: a place must be an object"]
        data: dict = entry
        problems: list[str] = []
        filed = []
        for i, one in enumerate(data.get("filed") or [], 1):
            mark, why = read_mark(f"{where} mark {i}", one)
            if mark is None:
                problems += why
                continue
            touch, why = read_member(
                f"{where} mark {i}", "touch", one.get("touch"), Touch
            )
            if touch is None:
                problems += why
                continue
            filed.append(
                Filed(
                    str(one.get("role")),
                    mark,
                    touch,
                    str(one.get("split_from") or ""),
                )
            )
        answers, why = read_answers(where, data.get("answers"))
        problems += why
        disposition = None
        if data.get("disposition") is not None:
            disposition, why = read_disposition(
                where, data["disposition"], validators.disposition
            )
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
                asking=tuple(data.get("asking") or ()),
                owed=tuple(data.get("owed") or ()),
                question=question,
            ),
            [],
        )
