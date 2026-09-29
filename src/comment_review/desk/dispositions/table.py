"""The dispositions table: what the chief may close, and the text it sets.

What a ruling owes, and the side it takes where it names none, are its type's,
in `desk.proof.disposition`; the table is keyed by the ruling's name.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from comment_review.desk.proof.disposition import ORIGINAL, RecastRuling
from comment_review.desk.proof.state import CARRIED, State

Sets = Callable[[Any, str, dict[str, str]], str | None]


def _a_sides_text(disposition, base, sides):
    if disposition.side == ORIGINAL:
        return None
    return sides[disposition.side]


def _the_prose(disposition: RecastRuling, base, sides):
    return disposition.prose


@dataclass(frozen=True)
class DispositionRow:
    """One disposition, as a reader of what it does at a place sees it."""

    closes: frozenset[State]
    sets: Sets


DISPOSITIONS: dict[str, DispositionRow] = {
    "taken_in": DispositionRow(CARRIED, _a_sides_text),
    "recast": DispositionRow(CARRIED, _the_prose),
}
