"""What a role hands back in a turn: one answer to one question at one place."""

from dataclasses import dataclass, field, fields
from enum import StrEnum, auto

from comment_review.desk.marks.mark import filled


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


def _claim_problems(
    where: str, name: str, owed: tuple[str, ...], claim: object
) -> list[str]:
    """Whether `claim` carries the keys this answer's row demands.

    Args:
        where: how to name this answer in a message -- its address.
        name: the answer's own row name, for the message.
        owed: the row's `claim_all`.
        claim: the entry's `claim`, in whatever shape it arrived.

    Returns:
        One message per missing key, and one where a row owing keys got no
        object at all. Empty for a row that owes none, whatever `claim` is.
    """
    if not owed:
        return []
    if not isinstance(claim, dict):
        return [f"{where}: {name} needs a `claim` carrying {', '.join(owed)}"]
    held: dict = claim
    return [
        f"{where}: {name} needs `claim.{key}`"
        for key in owed
        if not filled(held.get(key))
    ]


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
        # Every key the row's own `effect` reads. A `query` whose `claim.shape`
        # is missing used to fall through to the deferring branch, which is
        # the difference between a place held for a person and one nobody is
        # waiting on -- so the absence is refused where the answer is parsed.
        out += _claim_problems(where, str(name), row.claim_all, data.get("claim"))
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
