"""What a role hands back in a turn: one answer to one question at one place.

    Question       the three things a turn asks a role
    Answer         one answer; `name` is its row, `instruction` on the wire
    read_answer()  an entry read as an `Answer`, then held to a validator

`Answer.deserialize` reads an entry's structure: it refuses an entry that is
not an object or asks no `Question`, and reads a field of the wrong type as
absent (`decision-log.md Process: #204`). Whether the answer is one its
question takes, and carries what that row owes, is
`desk.answers.rules.validate`'s question, which `read_answer` asks after it.
"""

from collections.abc import Callable
from dataclasses import dataclass, field, fields
from enum import StrEnum, auto

from comment_review.desk.proof.mark import as_text


class Question(StrEnum):
    """The three things a turn asks a role.

    An `escalation` and a `composition` are asked of a place, about the text
    there. A `placement` is asked of a move, about the pair of addresses, once
    per open move to every role that read either page -- `decision-log.md
    Process: #195`. Its answers act on the move and none of them rewrites a
    paragraph.
    """

    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()

    ESCALATION = auto()
    COMPOSITION = auto()
    PLACEMENT = auto()


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
        """One entry read as an `Answer`, or named problems -- its STRUCTURE only.

        Refused only where it cannot be read: an entry that is not an object,
        or a `question` that is not one of the three.
        """
        if not isinstance(entry, dict):
            return None, [f"{where}: an answer must be an object"]
        data: dict = entry
        try:
            question = Question(str(data.get("question")))
        except ValueError:
            return None, [f"{where}: `question` must be one of {', '.join(Question)}"]
        claim = data.get("claim")
        sources = data.get("sources")
        return (
            cls(
                address=as_text(data.get("address")),
                anchor=as_text(data.get("anchor")),
                question=question,
                name=as_text(data.get("instruction")),
                reason=as_text(data.get("reason")),
                change=as_text(data.get("change")),
                claim=dict(claim) if isinstance(claim, dict) else {},
                sources=tuple(sources) if isinstance(sources, list) else (),
            ),
            [],
        )


#: A check of one answer against the rules its row states. Returns one message
#: per broken rule, in the order a reader meets them.
AnswerValidator = Callable[[str, Answer], list[str]]


def read_answer(
    where: str, entry: object, validate: AnswerValidator
) -> "tuple[Answer | None, list[str]]":
    """One entry read as an `Answer` and held to `validate`, or named problems."""
    answer, why = Answer.deserialize(where, entry)
    if answer is None:
        return None, why
    problems = validate(where, answer)
    if problems:
        return None, problems
    return answer, []
