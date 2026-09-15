"""The dispositions table: what the chief may close, and the text it sets."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from comment_review.desk.dispositions.disposition import CHIEF, ORIGINAL
from comment_review.desk.evaluate.state import CARRIED, State

Sets = Callable[[Any, str, dict[str, str]], str | None]


def _a_sides_text(disposition, base, sides):
    if disposition.side == ORIGINAL:
        return None
    return sides[disposition.side]


def _the_prose(disposition, base, sides):
    return disposition.prose


@dataclass(frozen=True)
class DispositionRow:
    """One disposition, as every reader sees it."""

    closes: frozenset[State]
    owes: tuple[str, ...]
    sets: Sets
    #: The side this row fixes -- `CHIEF` on the recast row, "" where the
    #: ruling names its own side. `Disposition.deserialize` reads this as the
    #: default so the row, not a hand-typed check on `name`, is the one place
    #: that names "recast" outside this table.
    side: str = ""


DISPOSITIONS: dict[str, DispositionRow] = {
    "taken_in": DispositionRow(CARRIED, ("side",), _a_sides_text),
    "recast": DispositionRow(CARRIED, ("prose",), _the_prose, side=CHIEF),
}
