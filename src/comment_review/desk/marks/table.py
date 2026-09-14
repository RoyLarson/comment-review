"""The marks table: one row per instruction, and every reader asks the row.

A row says what a mark's claim carries, which places the mark touches, what
text it sets at each, what problems it has against its base, how it pairs
with other marks at a place, and which answers a turn may give on it. Nothing
outside this module names an instruction; a gate holds that.

`sets` returns None where the mark sets nothing (`decision-log.md Process:
#174`), "" for a delete, else the text. `reads` returns the problems the row
finds; `flows.fill` runs it before a mark is placed and the evaluator before
it is folded, so a mark reaching the evaluator has been read.

`rereads` is True on `add` alone: an add is carried forward for every role
that read its page, per `decision-log.md Process: #116` and `#121`.
"""

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Any

from comment_review.desk.marks.mark import Instruction, Shape, first_word_dropped


class Touch(StrEnum):
    """Which of the places a mark writes is being asked about."""

    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()

    OWN = auto()
    ORIGIN = auto()
    DESTINATION = auto()


class Stance(StrEnum):
    """How a mark stands toward the other marks at its place."""

    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()

    PROPOSES = auto()
    ABSTAINS = auto()
    UNSETTLABLE = auto()


Sets = Callable[[Any, Touch, str], str | None]
Reads = Callable[[Any, Touch, str], list[str]]
Pairs = Callable[[Any], Stance]


def _nothing(mark, touch, base):
    return None


def _no_problems(mark, touch, base):
    return []


def _the_change(mark, touch, base):
    return mark.change


def _the_raw_text(mark, touch, base):
    return mark.raw_text


def _without_once(base: str, snippet: str) -> str | None:
    if snippet and base.count(snippet) == 1:
        return base.replace(snippet, "")
    return None


def _move_sets(mark, touch, base):
    if touch is Touch.ORIGIN:
        return _without_once(base, mark.change)
    return mark.raw_text


def _move_reads(mark, touch, base):
    if touch is Touch.ORIGIN:
        if _without_once(base, mark.change) is None:
            return [f"the snippet is not in the origin's paragraph: {mark.change!r}"]
        return []
    dropped = first_word_dropped(base, mark.raw_text)
    if dropped is not None:
        return [f"the destination text does not keep {dropped!r}"]
    dropped = first_word_dropped(mark.change, mark.raw_text)
    if dropped is not None:
        return [f"the destination text does not keep {dropped!r}"]
    return []


def _add_reads(mark, touch, base):
    for held in (base, mark.change):
        dropped = first_word_dropped(held, mark.raw_text)
        if dropped is not None:
            return [f"the text does not keep {dropped!r}"]
    return []


def _proposes(mark):
    return Stance.PROPOSES


def _abstains(mark):
    return Stance.ABSTAINS


def _query_stance(mark):
    if mark.claim.get("shape") == str(Shape.HUMAN_REVIEW_NECESSARY):
        return Stance.UNSETTLABLE
    return Stance.ABSTAINS


ESCALATION_ANSWERS = ("hold", "withdraw", "correct", "patch")


@dataclass(frozen=True)
class Row:
    """One instruction, as every reader sees it."""

    claim_all: tuple[str, ...] = ()
    quotes_original: str = ""
    touches: tuple[Touch, ...] = (Touch.OWN,)
    sets: Sets = _nothing
    reads: Reads = _no_problems
    pairs: Pairs = _proposes
    answers: tuple[str, ...] = ESCALATION_ANSWERS
    owes_change: bool = True
    owes_sources: bool = True
    substantive: bool = True
    may_empty: bool = False
    needs_anchor: bool = False
    #: Set True on `add` alone -- Ruling R4, `decision-log.md Process: #116`
    #: and `#121`: an add is carried forward for every role that read its
    #: page, not only the role that filed it.
    rereads: bool = False
    #: Derived from `touches` in `__post_init__`, below -- never set by a row
    #: literal. The default here is only what a `Row()` with no `touches`
    #: argument gets before the derivation runs.
    owes_destination: bool = False

    def __post_init__(self) -> None:
        """Derive `owes_destination` from `touches`, overwriting any literal.

        The dataclass is frozen, so this is the one place allowed to set a
        field after construction. `owes_destination` is a fact about
        `touches`, not a second fact a row author could state differently --
        deriving it here is what keeps the two from drifting apart, the way
        a stored copy next to its source could.
        """
        object.__setattr__(self, "owes_destination", Touch.DESTINATION in self.touches)


INSTRUCTIONS: dict[Instruction, Row] = {
    Instruction.CLEAN: Row(
        pairs=_abstains,
        answers=(),
        owes_change=False,
        owes_sources=False,
        substantive=False,
    ),
    Instruction.QUERY: Row(
        claim_all=("shape", "attempted", "settles"),
        pairs=_query_stance,
        answers=(),
        owes_change=False,
    ),
    Instruction.DROP: Row(
        claim_all=("drop",), quotes_original="drop", sets=_the_change, may_empty=True
    ),
    Instruction.CORRECT: Row(
        claim_all=("false", "true"), quotes_original="false", sets=_the_change
    ),
    Instruction.PATCH: Row(
        claim_all=("from", "to"),
        quotes_original="from",
        sets=_the_change,
        owes_sources=False,
    ),
    Instruction.ADD: Row(
        claim_all=("missing", "anchor"),
        sets=_the_raw_text,
        reads=_add_reads,
        needs_anchor=True,
        rereads=True,
    ),
    Instruction.MOVE: Row(
        claim_all=("from", "to"),
        touches=(Touch.ORIGIN, Touch.DESTINATION),
        sets=_move_sets,
        reads=_move_reads,
    ),
}
