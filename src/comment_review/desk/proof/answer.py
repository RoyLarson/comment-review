"""What a role hands back in a turn: one answer to one question, one type per answer.

    Question       the three things a turn asks a role
    Answer         what every answer carries, its wire entry and its read
    Rewrite        an answer that proposes a text, and so carries a `change`
    HoldAnswer .. StetAnswer  one type per answer name, each holding its own
                   fields and naming the questions that take it
    answer_type()  the type an answer's name names -- the one dispatch
    read_answer()  an entry read as the type its name names, or named problems
    read_answers() a record's answers, turn -> role -> answer, each read

An answer's type owns its fields, its wire entry and every check on itself:
reading an entry into its type IS that check. A type is per answer NAME, with
the question a field, because the rows of `desk.answers.table.ANSWERS` that
share a name -- `withdraw`, `correct`, `patch`, `query` -- differ only in what
the answer does, which is the table's; what each owes is the same whichever
question asked it. What an answer does to a side or a move is the table's,
keyed by `(question, name)` as before.
"""

from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Any, ClassVar, Self

from comment_review.desk.proof.mark import QUERY_SHAPES, Shape, as_text, filled


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
    """What every answer carries, whatever its name.

    Never built itself: an answer is one of the types below. The class
    attributes are the facts about an answer its own read needs.

    Attributes:
        address: the slot's address, copied from the slot.
        anchor: the slot's anchor, copied from the slot.
        question: which question this answers -- one of the type's `asked`.
        reason: why, in prose.
        sources: the evidence, each `{cite, verbatim}`; resolved against the
            tree by the flow, never checked here.
    """

    address: str
    anchor: str
    question: Question
    reason: str
    sources: tuple

    #: The answer's name -- `instruction` on the wire.
    name: ClassVar[str]
    #: The questions that take this answer.
    asked: ClassVar[tuple[Question, ...]]
    #: Whether a `change` is owed -- True on every `Rewrite`.
    owes_change: ClassVar[bool] = False
    #: Every key the wire `claim` must carry, filled.
    claim_all: ClassVar[tuple[str, ...]] = ()

    def _change(self) -> str:
        """This answer's `change` as the wire carries it; "" where it takes none."""
        return ""

    def _claim(self) -> dict:
        """This answer's claim as the wire's `claim` object."""
        return {}

    def serialize(self) -> dict:
        """This answer as a turn carries it; its name is `instruction` on the wire."""
        return {
            "address": self.address,
            "anchor": self.anchor,
            "question": str(self.question),
            "reason": self.reason,
            "change": self._change(),
            "claim": self._claim(),
            "sources": list(self.sources),
            "instruction": self.name,
        }

    @classmethod
    def read(
        cls, where: str, data: dict, question: Question
    ) -> "tuple[Self | None, list[str]]":
        """One entry naming this answer, read as this type.

        A field of the wrong type is read as absent, and a field this type does
        not take is ignored, never refused (`decision-log.md Process: #204`).
        An answer its question does not take is one message, and nothing else
        is asked of it.

        Args:
            where: how to name this answer in a message -- its address.
            data: the entry, already an object naming this answer.
            question: the question the entry answers, already one of the three.

        Returns:
            `(answer, [])`, or `(None, [one message per broken rule])`.
        """
        if question not in cls.asked:
            return None, [not_an_answer(where, cls.name, question)]
        address = as_text(data.get("address"))
        reason = as_text(data.get("reason"))
        change = as_text(data.get("change"))
        given = data.get("claim")
        claim: dict = dict(given) if isinstance(given, dict) else {}
        listed = data.get("sources")
        out: list[str] = []
        if not filled(address):
            out.append(f"{where}: {cls.name} needs the `address`")
        if not filled(reason):
            out.append(f"{where}: {cls.name} needs a `reason`")
        if cls.owes_change and not filled(change):
            out.append(f"{where}: {cls.name} needs a `change`")
        out += [
            f"{where}: {cls.name} needs `claim.{key}`"
            for key in cls.claim_all
            if not filled(claim.get(key))
        ]
        out += cls._value_problems(where, claim)
        if out:
            return None, out
        return (
            cls(
                address=address,
                anchor=as_text(data.get("anchor")),
                question=question,
                reason=reason,
                sources=tuple(listed) if isinstance(listed, list) else (),
                **cls._own(claim, change),
            ),
            [],
        )

    @classmethod
    def _own(cls, claim: dict, change: str) -> dict[str, Any]:
        """This type's own fields, from a claim and a change already checked."""
        return {}

    @classmethod
    def _value_problems(cls, where: str, claim: dict) -> list[str]:
        """Whether a claim value from a closed set is one of it. None to ask here."""
        return []


@dataclass(frozen=True)
class Rewrite(Answer):
    """An answer that proposes a text for the role's side, and so carries one.

    Attributes:
        change: the whole updated paragraph, as raw text.
    """

    change: str

    owes_change: ClassVar[bool] = True

    def _change(self) -> str:
        return self.change

    @classmethod
    def _own(cls, claim: dict, change: str) -> dict[str, Any]:
        return {"change": change}


@dataclass(frozen=True)
class HoldAnswer(Answer):
    """`hold`: the role keeps its side as it filed it."""

    name: ClassVar[str] = "hold"
    asked: ClassVar[tuple[Question, ...]] = (Question.ESCALATION,)


@dataclass(frozen=True)
class WithdrawAnswer(Answer):
    """`withdraw`: the role takes back its side, or the move it filed."""

    name: ClassVar[str] = "withdraw"
    asked: ClassVar[tuple[Question, ...]] = (Question.ESCALATION, Question.PLACEMENT)


@dataclass(frozen=True)
class CorrectAnswer(Rewrite):
    """`correct`: the role's side becomes the text it gives, a claim corrected."""

    name: ClassVar[str] = "correct"
    asked: ClassVar[tuple[Question, ...]] = (Question.ESCALATION, Question.COMPOSITION)


@dataclass(frozen=True)
class PatchAnswer(Rewrite):
    """`patch`: the role's side becomes the text it gives, a wording mended."""

    name: ClassVar[str] = "patch"
    asked: ClassVar[tuple[Question, ...]] = (Question.ESCALATION, Question.COMPOSITION)


@dataclass(frozen=True)
class CleanAnswer(Answer):
    """`clean`: the role accepts the composed text."""

    name: ClassVar[str] = "clean"
    asked: ClassVar[tuple[Question, ...]] = (Question.COMPOSITION,)


@dataclass(frozen=True)
class QueryAnswer(Answer):
    """`query`: the role cannot settle it, and says who can.

    Attributes:
        shape: who resolves it -- one of `QUERY_SHAPES`, as a query mark's is.
        attempted: what the role did before it asked.
        settles: what would settle it.
    """

    shape: Shape
    attempted: str
    settles: str

    name: ClassVar[str] = "query"
    asked: ClassVar[tuple[Question, ...]] = (Question.COMPOSITION, Question.PLACEMENT)
    claim_all: ClassVar[tuple[str, ...]] = ("shape", "attempted", "settles")

    def _claim(self) -> dict:
        return {
            "shape": str(self.shape),
            "attempted": self.attempted,
            "settles": self.settles,
        }

    @classmethod
    def _own(cls, claim: dict, change: str) -> dict[str, Any]:
        return {
            "shape": Shape(claim["shape"]),
            "attempted": claim["attempted"],
            "settles": claim["settles"],
        }

    @classmethod
    def _value_problems(cls, where: str, claim: dict) -> list[str]:
        """`shape` one of the three.

        The table reads it to tell a place held for the author from a role
        standing aside.
        """
        if claim.get("shape") in QUERY_SHAPES:
            return []
        return [
            f"{where}: {cls.name} needs `claim.shape` to be one of "
            + ", ".join(QUERY_SHAPES)
        ]


@dataclass(frozen=True)
class AgreeAnswer(Answer):
    """`agree`: the role accepts where the move sends the paragraph."""

    name: ClassVar[str] = "agree"
    asked: ClassVar[tuple[Question, ...]] = (Question.PLACEMENT,)


@dataclass(frozen=True)
class StetAnswer(Answer):
    """`stet`: the role refuses the move; the paragraph stays where it is."""

    name: ClassVar[str] = "stet"
    asked: ClassVar[tuple[Question, ...]] = (Question.PLACEMENT,)


def answer_type(name: str) -> type[Answer] | None:
    """The type an answer named `name` is read as, or None for no answer."""
    match name:
        case "hold":
            return HoldAnswer
        case "withdraw":
            return WithdrawAnswer
        case "correct":
            return CorrectAnswer
        case "patch":
            return PatchAnswer
        case "clean":
            return CleanAnswer
        case "query":
            return QueryAnswer
        case "agree":
            return AgreeAnswer
        case "stet":
            return StetAnswer
        case _:
            return None


def not_an_answer(where: str, name: str, question: Question) -> str:
    """The refusal for a name its question does not take."""
    article = "an" if str(question)[:1] in "aeiou" else "a"
    return f"{where}: {name!r} is not an answer to {article} {question}"


def read_answer(where: str, entry: object) -> "tuple[Answer | None, list[str]]":
    """One entry read as the type its name names, or named problems.

    An entry that is not an object, or asks no `Question`, cannot be read and
    is refused here, and so is a name no answer has; every other refusal is
    the type's own read.
    """
    if not isinstance(entry, dict):
        return None, [f"{where}: an answer must be an object"]
    data: dict = entry
    try:
        question = Question(str(data.get("question")))
    except ValueError:
        return None, [f"{where}: `question` must be one of {', '.join(Question)}"]
    name = as_text(data.get("instruction"))
    kind = answer_type(name)
    if kind is None:
        return None, [not_an_answer(where, name, question)]
    return kind.read(where, data, question)


def read_answers(
    where: str, raw: object
) -> "tuple[dict[int, dict[str, Answer]], list[str]]":
    """A place's or a move's answers, turn -> role -> answer, each read.

    Args:
        where: how to name the record in a message.
        raw: the record's `answers` as it came back; absent or empty is none.

    Returns:
        `(turn -> role -> Answer, the problems)`. A turn key that is not a
        number, a turn that is not an object, and an answer that will not read
        are each named; the answers that read are kept either way.
    """
    answers: dict[int, dict[str, Answer]] = {}
    if not raw:
        return answers, []
    if not isinstance(raw, dict):
        return answers, [
            f"{where}: `answers` must be an object of turn -> role -> answer"
        ]
    problems: list[str] = []
    for turn, by in raw.items():
        # A JSON key is a string; one written from memory may be an int.
        try:
            at = int(str(turn))
        except ValueError:
            problems.append(f"{where}: answers at turn {turn!r} -- a turn is a number")
            continue
        if not isinstance(by, dict):
            problems.append(
                f"{where}: answers at turn {turn} must be an object of role -> answer"
            )
            continue
        for role, one in by.items():
            answer, why = read_answer(f"{where} turn {turn} {role}", one)
            if answer is None:
                problems += why
            else:
                answers.setdefault(at, {})[str(role)] = answer
    return answers, problems
