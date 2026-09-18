"""A place: the aggregate the middle decides."""

from dataclasses import dataclass, field

from comment_review.desk.answers.answer import Answer, Question
from comment_review.desk.dispositions.disposition import Disposition
from comment_review.desk.evaluate.state import State
from comment_review.desk.marks.mark import Mark
from comment_review.desk.marks.table import Touch


@dataclass
class Filed:
    """One role's mark, filed at a place, and which end of it this is about."""

    role: str
    mark: Mark
    touch: Touch


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
    partner: str | None = None

    def serialize(self) -> dict:
        """This place's own fields, as a dict keyed by this class's own field names."""
        return {
            "address": self.address,
            "anchor": self.anchor,
            "base": self.base,
            "readers": list(self.readers),
            "filed": [
                {"role": f.role, "touch": str(f.touch), **f.mark.serialize()}
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
            "partner": self.partner,
        }

    @classmethod
    def deserialize(cls, where: str, entry: object) -> "tuple[Place | None, list[str]]":
        """One entry becomes a `Place`, or becomes named problems."""
        if not isinstance(entry, dict):
            return None, [f"{where}: a place must be an object"]
        data: dict = entry
        problems: list[str] = []
        filed = []
        for i, one in enumerate(data.get("filed") or []):
            mark, why = Mark.deserialize(f"{where} mark {i}", one)
            if mark is None:
                problems += why
                continue
            filed.append(
                Filed(str(one.get("role")), mark, Touch(str(one.get("touch"))))
            )
        answers: dict[int, dict[str, Answer]] = {}
        for turn, by in (data.get("answers") or {}).items():
            for role, raw in by.items():
                answer, why = Answer.deserialize(f"{where} turn {turn} {role}", raw)
                if answer is None:
                    problems += why
                else:
                    answers.setdefault(int(turn), {})[role] = answer
        disposition = None
        if data.get("disposition") is not None:
            disposition, why = Disposition.deserialize(where, data["disposition"])
            problems += why
        if problems:
            return None, problems
        state = data.get("state")
        question = data.get("question")
        return (
            cls(
                address=str(data.get("address") or ""),
                anchor=str(data.get("anchor") or ""),
                base=str(data.get("base") or ""),
                readers=tuple(data.get("readers") or ()),
                filed=filed,
                answers=answers,
                disposition=disposition,
                state=State(state) if state else None,
                text=data.get("text"),
                sides=dict(data.get("sides") or {}),
                reasons=tuple(data.get("reasons") or ()),
                notes=tuple(data.get("notes") or ()),
                asking=tuple(data.get("asking") or ()),
                owed=tuple(data.get("owed") or ()),
                question=Question(question) if question else None,
                partner=data.get("partner"),
            ),
            [],
        )
