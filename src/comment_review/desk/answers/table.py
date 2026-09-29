"""The answers table: twelve rows, four per question.

The escalation and composition rows act on the answering role's own side at a
place. The placement rows act on a move (`decision-log.md Process: #195`):
`agree` accepts where the paragraph goes, `stet` refuses it and the move is
contested for the chief, `withdraw` takes the move off both of its ends, and
`query` holds both ends for the author or abstains, by its shape.
"""

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Any

from comment_review.desk.proof.answer import QueryAnswer, Question
from comment_review.desk.proof.mark import Shape


class Effect(StrEnum):
    """What an answer does to the thing it answers about, once the row reads it.

    On an escalation or a composition that thing is the role's own side at the
    place. On a placement it is the move: `ACCEPTS` and `REMOVES` read the
    same way there, and `CONTESTS` is the placement's own -- the paragraph
    stays where it is by this role's reading, so the move is carried forward
    for the chief rather than agreed (`decision-log.md Process: #195`).
    """

    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()

    KEEPS = auto()
    REMOVES = auto()
    REPLACES = auto()
    ACCEPTS = auto()
    ABSTAINS = auto()
    UNSETTLABLE = auto()
    CONTESTS = auto()


def _always(effect: Effect) -> Callable[[Any], Effect]:
    return lambda answer: effect


def _query_effect(answer: QueryAnswer) -> Effect:
    """Held for the author on `human-review-necessary`; standing aside otherwise.

    The answer's read refuses a shape outside the three, so a mistyped
    `human-review-necessary` never reaches here to be read as standing aside.
    """
    if answer.shape is Shape.HUMAN_REVIEW_NECESSARY:
        return Effect.UNSETTLABLE
    return Effect.ABSTAINS


@dataclass(frozen=True)
class AnswerRow:
    """One answer to one question, as a reader of what it does sees it.

    What the answer owes -- its `change`, its claim keys -- is its type's, in
    `desk.proof.answer`; the type's read refuses an answer missing one, which
    is what `_query_effect` relies on to tell a place held for the human from
    a role standing aside.

    Attributes:
        question: which of the three this answer answers.
        effect: what it does to the role's own proposal, or to the move.
    """

    question: Question
    effect: Callable[[Any], Effect]


ANSWERS: dict[tuple[Question, str], AnswerRow] = {
    (Question.ESCALATION, "hold"): AnswerRow(
        Question.ESCALATION, _always(Effect.KEEPS)
    ),
    (Question.ESCALATION, "withdraw"): AnswerRow(
        Question.ESCALATION, _always(Effect.REMOVES)
    ),
    (Question.ESCALATION, "correct"): AnswerRow(
        Question.ESCALATION, _always(Effect.REPLACES)
    ),
    (Question.ESCALATION, "patch"): AnswerRow(
        Question.ESCALATION, _always(Effect.REPLACES)
    ),
    (Question.COMPOSITION, "clean"): AnswerRow(
        Question.COMPOSITION, _always(Effect.ACCEPTS)
    ),
    (Question.COMPOSITION, "query"): AnswerRow(Question.COMPOSITION, _query_effect),
    (Question.COMPOSITION, "correct"): AnswerRow(
        Question.COMPOSITION, _always(Effect.REPLACES)
    ),
    (Question.COMPOSITION, "patch"): AnswerRow(
        Question.COMPOSITION, _always(Effect.REPLACES)
    ),
    (Question.PLACEMENT, "agree"): AnswerRow(
        Question.PLACEMENT, _always(Effect.ACCEPTS)
    ),
    (Question.PLACEMENT, "stet"): AnswerRow(
        Question.PLACEMENT, _always(Effect.CONTESTS)
    ),
    (Question.PLACEMENT, "withdraw"): AnswerRow(
        Question.PLACEMENT, _always(Effect.REMOVES)
    ),
    (Question.PLACEMENT, "query"): AnswerRow(Question.PLACEMENT, _query_effect),
}
