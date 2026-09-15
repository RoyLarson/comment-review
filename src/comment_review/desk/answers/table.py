"""The answers table: eight rows, four per question."""

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Any

from comment_review.desk.answers.answer import Question
from comment_review.desk.marks.mark import Shape


class Effect(StrEnum):
    """What an answer does to its own proposal, once the row reads it."""

    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()

    KEEPS = auto()
    REMOVES = auto()
    REPLACES = auto()
    ACCEPTS = auto()
    ABSTAINS = auto()
    UNSETTLABLE = auto()


def _always(effect: Effect) -> Callable[[Any], Effect]:
    return lambda answer: effect


def _query_effect(answer) -> Effect:
    if answer.claim.get("shape") == str(Shape.HUMAN_REVIEW_NECESSARY):
        return Effect.UNSETTLABLE
    return Effect.ABSTAINS


@dataclass(frozen=True)
class AnswerRow:
    """One answer, as every reader sees it."""

    question: Question
    effect: Callable[[Any], Effect]
    owes_change: bool = False


ANSWERS: dict[tuple[Question, str], AnswerRow] = {
    (Question.ESCALATION, "hold"): AnswerRow(
        Question.ESCALATION, _always(Effect.KEEPS)
    ),
    (Question.ESCALATION, "withdraw"): AnswerRow(
        Question.ESCALATION, _always(Effect.REMOVES)
    ),
    (Question.ESCALATION, "correct"): AnswerRow(
        Question.ESCALATION, _always(Effect.REPLACES), True
    ),
    (Question.ESCALATION, "patch"): AnswerRow(
        Question.ESCALATION, _always(Effect.REPLACES), True
    ),
    (Question.COMPOSITION, "clean"): AnswerRow(
        Question.COMPOSITION, _always(Effect.ACCEPTS)
    ),
    (Question.COMPOSITION, "query"): AnswerRow(Question.COMPOSITION, _query_effect),
    (Question.COMPOSITION, "correct"): AnswerRow(
        Question.COMPOSITION, _always(Effect.REPLACES), True
    ),
    (Question.COMPOSITION, "patch"): AnswerRow(
        Question.COMPOSITION, _always(Effect.REPLACES), True
    ),
}
