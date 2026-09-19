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
    """One answer, as every reader sees it.

    Attributes:
        question: which of the two this answer answers.
        effect: what it does to the role's own proposal.
        owes_change: whether it owes a `change`.
        claim_all: every key its `claim` must carry, as the marks table's own
            `Row.claim_all` states it for a mark. Empty for a row whose claim
            is nothing to this table.

            !! IT IS WHAT `effect` READS, STATED WHERE A READER CAN FIND IT.
            `_query_effect` asks a `query`'s `claim["shape"]` to tell a place
            held for the human from a role standing aside, and a missing key
            fell to the second silently -- the difference between a review
            that stops for a person and one that does not. The parse refuses
            the absence now, and `flows.answers.contracts` publishes the keys
            off this field, so nothing hand-types them.
        reaches_partner: whether this answer, given by the role that filed a
            two-place mark, takes effect at the mark's other place as well as
            at the one it was written at. A move is one mark at two places and
            an answer at either end reaches the move whole
            (`decision-log.md Process: #129`, `#152`, `#153`), so the
            withdrawal carries: the mark is off, and the role holds no side at
            either place it wrote. A replacement does not carry a text across,
            because the two ends hold different texts -- the origin its
            paragraph with the snippet gone and the destination its paragraph
            with the snippet in -- so it lands at the end it was written at,
            which is what `#129` rules it does there. One of each in one turn
            leaves the move half done and is refused back to the role
            (`#189`, `desk.evaluate.passes.refuse_half_moves`).
    """

    question: Question
    effect: Callable[[Any], Effect]
    owes_change: bool = False
    claim_all: tuple[str, ...] = ()
    reaches_partner: bool = False


ANSWERS: dict[tuple[Question, str], AnswerRow] = {
    (Question.ESCALATION, "hold"): AnswerRow(
        Question.ESCALATION, _always(Effect.KEEPS)
    ),
    (Question.ESCALATION, "withdraw"): AnswerRow(
        Question.ESCALATION, _always(Effect.REMOVES), reaches_partner=True
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
    (Question.COMPOSITION, "query"): AnswerRow(
        Question.COMPOSITION,
        _query_effect,
        claim_all=("shape", "attempted", "settles"),
    ),
    (Question.COMPOSITION, "correct"): AnswerRow(
        Question.COMPOSITION, _always(Effect.REPLACES), True
    ),
    (Question.COMPOSITION, "patch"): AnswerRow(
        Question.COMPOSITION, _always(Effect.REPLACES), True
    ),
}
