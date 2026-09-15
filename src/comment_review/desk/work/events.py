"""What a fold says as it runs. The commands print from these and nothing else."""

from typing import NamedTuple

from comment_review.desk.answers.answer import Question
from comment_review.desk.evaluate.state import State


class Refused(NamedTuple):
    """One role's problems with one place, folded to a delta of the mark."""

    role: str
    address: str
    reasons: tuple[str, ...]


class CarriedForward(NamedTuple):
    """A place the fold could not settle alone -- asked of `roles` next turn."""

    address: str
    state: State
    question: Question | None
    roles: tuple[str, ...]


class Unsettlable(NamedTuple):
    """One role's mark at one place that no turn can resolve."""

    address: str
    role: str
    reason: str


class Settled(NamedTuple):
    """One place the fold decided, and the text it settled on, if any."""

    address: str
    text: str | None


class Committed(NamedTuple):
    """The fold committed: every place decided, none refused."""

    places: int


class RolledBack(NamedTuple):
    """The fold rolled back: at least one place refused, nothing saved."""

    reasons: int


Event = Refused | CarriedForward | Unsettlable | Settled | Committed | RolledBack
