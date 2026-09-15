"""What a role hands back in a turn: one answer to one question at one place."""

from dataclasses import dataclass, field, fields
from enum import StrEnum, auto

from comment_review.desk.marks.mark import filled


class Question(StrEnum):
    """The two things a turn asks a role about a mark it already filed."""

    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()

    ESCALATION = auto()
    COMPOSITION = auto()


@dataclass(frozen=True)
class Answer:
    """One answer. `name` is the answer's row; `instruction` on the wire."""

    address: str
    anchor: str
    question: Question
    name: str
    reason: str
    change: str = ""
    claim: dict = field(default_factory=dict)
    sources: tuple = ()

    def serialize(self) -> dict:
        """This answer as a turn carries it, keyed by this class's own field names."""
        out = {f.name: getattr(self, f.name) for f in fields(self)}
        out["question"] = str(self.question)
        out["instruction"] = out.pop("name")
        out["sources"] = list(self.sources)
        return out

    @classmethod
    def deserialize(
        cls, where: str, entry: object
    ) -> "tuple[Answer | None, list[str]]":
        """One entry becomes an `Answer`, or becomes named problems."""
        from comment_review.desk.answers.table import ANSWERS

        if not isinstance(entry, dict):
            return None, [f"{where}: an answer must be an object"]
        data: dict = entry
        try:
            question = Question(str(data.get("question")))
        except ValueError:
            return None, [f"{where}: `question` must be one of {', '.join(Question)}"]
        name = data.get("instruction")
        row = ANSWERS.get((question, str(name)))
        if row is None:
            article = "an" if str(question)[:1] in "aeiou" else "a"
            return None, [f"{where}: {name!r} is not an answer to {article} {question}"]
        out = []
        if not filled(data.get("address")):
            out.append(f"{where}: {name} needs the `address`")
        if not filled(data.get("reason")):
            out.append(f"{where}: {name} needs a `reason`")
        if row.owes_change and not filled(data.get("change")):
            out.append(f"{where}: {name} needs a `change`")
        if out:
            return None, out
        claim = data.get("claim")
        sources = data.get("sources")
        return (
            cls(
                address=str(data.get("address") or ""),
                anchor=str(data.get("anchor") or ""),
                question=question,
                name=str(name),
                reason=str(data.get("reason") or ""),
                change=str(data.get("change") or ""),
                claim=dict(claim) if isinstance(claim, dict) else {},
                sources=tuple(sources) if isinstance(sources, list) else (),
            ),
            [],
        )
