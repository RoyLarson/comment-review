"""A place: the aggregate the middle decides."""

from dataclasses import dataclass, field

from comment_review.desk.answers.answer import Answer, Question
from comment_review.desk.dispositions.disposition import Disposition
from comment_review.desk.evaluate.state import State
from comment_review.desk.marks.mark import Mark
from comment_review.desk.marks.table import INSTRUCTIONS, Stance, Touch


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
    question: Question | None = None
    partner: str | None = None

    def proposals(self) -> dict[str, str | None]:
        """Role -> the text that role's proposing mark sets here."""
        out: dict[str, str | None] = {}
        for one in self.filed:
            row = INSTRUCTIONS[one.mark.instruction]
            if row.pairs(one.mark) is Stance.PROPOSES:
                out[one.role] = row.sets(one.mark, one.touch, self.base)
        return out

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
                question=Question(question) if question else None,
                partner=data.get("partner"),
            ),
            [],
        )
