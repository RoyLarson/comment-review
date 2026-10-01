"""Twelve answer rows, with separate effects for a side and a placement.

Escalation and composition answers act on the answering role's side at a
place. Placement answers act on its vote about a move. A deferring query
relinquishes that position; a human query requires the author's answer before
the production fold (`decision-log.md Process: #197`).
"""

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum, auto
from typing import TypeVar

from comment_review.desk.proof.answer import Answer, QueryAnswer, Question
from comment_review.desk.proof.mark import Shape


class SideEffect(Enum):
    """The complete set of operations on the answering role's side."""

    KEEPS = auto()
    REMOVES = auto()
    REPLACES = auto()
    ACCEPTS = auto()
    DEFERS = auto()
    HUMAN_QUERY = auto()


class PlacementEffect(Enum):
    """The complete set of operations on a role's placement position."""

    ACCEPTS = auto()
    CONTESTS = auto()
    REMOVES = auto()
    DEFERS = auto()
    HUMAN_QUERY = auto()


_Effect = TypeVar("_Effect", SideEffect, PlacementEffect)


def _always(effect: _Effect) -> Callable[[Answer], _Effect]:
    return lambda answer: effect


def _side_query_effect(answer: Answer) -> SideEffect:
    """Classify a typed query as a deferral or a question for the author."""
    if not isinstance(answer, QueryAnswer):
        raise ValueError("a side query effect requires QueryAnswer")
    if answer.shape is Shape.HUMAN_REVIEW_NECESSARY:
        return SideEffect.HUMAN_QUERY
    return SideEffect.DEFERS


def _placement_query_effect(answer: Answer) -> PlacementEffect:
    """Classify a typed placement query without giving it a side effect."""
    if not isinstance(answer, QueryAnswer):
        raise ValueError("a placement query effect requires QueryAnswer")
    if answer.shape is Shape.HUMAN_REVIEW_NECESSARY:
        return PlacementEffect.HUMAN_QUERY
    return PlacementEffect.DEFERS


@dataclass(frozen=True)
class SideAnswerRow:
    """An escalation or composition answer's operation on its role's side."""

    effect: Callable[[Answer], SideEffect]


@dataclass(frozen=True)
class PlacementAnswerRow:
    """A placement answer's operation on a move, never on its end's text."""

    effect: Callable[[Answer], PlacementEffect]


ANSWERS: dict[tuple[Question, str], SideAnswerRow | PlacementAnswerRow] = {
    (Question.ESCALATION, "hold"): SideAnswerRow(_always(SideEffect.KEEPS)),
    (Question.ESCALATION, "withdraw"): SideAnswerRow(_always(SideEffect.REMOVES)),
    (Question.ESCALATION, "correct"): SideAnswerRow(_always(SideEffect.REPLACES)),
    (Question.ESCALATION, "patch"): SideAnswerRow(_always(SideEffect.REPLACES)),
    (Question.COMPOSITION, "clean"): SideAnswerRow(_always(SideEffect.ACCEPTS)),
    (Question.COMPOSITION, "query"): SideAnswerRow(_side_query_effect),
    (Question.COMPOSITION, "correct"): SideAnswerRow(_always(SideEffect.REPLACES)),
    (Question.COMPOSITION, "patch"): SideAnswerRow(_always(SideEffect.REPLACES)),
    (Question.PLACEMENT, "agree"): PlacementAnswerRow(_always(PlacementEffect.ACCEPTS)),
    (Question.PLACEMENT, "stet"): PlacementAnswerRow(_always(PlacementEffect.CONTESTS)),
    (Question.PLACEMENT, "withdraw"): PlacementAnswerRow(
        _always(PlacementEffect.REMOVES)
    ),
    (Question.PLACEMENT, "query"): PlacementAnswerRow(_placement_query_effect),
}


def asks_human(answer: Answer) -> bool:
    """Whether the answer's row requires a human reply before the fold."""
    row = ANSWERS.get((answer.question, answer.name))
    if row is None:
        return False
    effect = row.effect(answer)
    if isinstance(row, SideAnswerRow):
        if not isinstance(effect, SideEffect):
            raise ValueError("a side row requires a side effect")
        return effect is SideEffect.HUMAN_QUERY
    if not isinstance(effect, PlacementEffect):
        raise ValueError("a placement row requires a placement effect")
    return effect is PlacementEffect.HUMAN_QUERY
