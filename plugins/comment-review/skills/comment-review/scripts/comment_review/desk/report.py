"""Stage reports rendered by the commands.

Before folding, the stage reports refusals as `Refused` and human questions
as `AsksTheHuman`. A rollback is reported as `RolledBack`.

A committed fold reports settled and carried-forward places, move
placements and advisory notes.
"""

from typing import NamedTuple

from comment_review.desk.proof.answer import Question
from comment_review.desk.proof.disposition import Disposition
from comment_review.desk.proof.move import Placement
from comment_review.desk.proof.state import State


class Refused(NamedTuple):
    """One role's problems with one place, folded to a delta of the mark."""

    role: str
    address: str
    reasons: tuple[str, ...]


class AsksTheHuman(NamedTuple):
    """One question a role put to the human, found before the fold ran.

    `decision-log.md Process: #197`: a human question never folds, so it rolls
    the stage or the turn back like a refusal, and says what is owed next --
    the human's answer where there is none yet (`answer` empty), or, where the
    answers file holds it, the role's replacement for its query.
    """

    role: str
    at: str
    question: str
    answer: str = ""


class CarriedForward(NamedTuple):
    """A place the fold could not settle alone -- asked of `roles` next turn.

    A committed fold's only, as the module docstring says.
    """

    address: str
    state: State
    question: Question | None
    roles: tuple[str, ...]


class PlacementCarried(NamedTuple):
    """A move whose placement the fold could not settle -- asked of `roles` next turn.

    `decision-log.md Process: #195`. `open` is put to the readers who have
    not answered; `contested` to its movers and the roles that stetted it.
    A committed fold's only, as the module docstring says.
    """

    origin: str
    destination: str
    placement: Placement
    roles: tuple[str, ...]


class Advised(NamedTuple):
    """What one role is told about one place without being refused for it.

    It reports and decides nothing: a place carrying notes takes whatever
    state its marks give it, and a fold that emits one still commits
    (`decision-log.md Process: #177`). A committed fold's only, as the module
    docstring says.
    """

    role: str
    address: str
    notes: tuple[str, ...]


class Settled(NamedTuple):
    """One place a fold decided, and the text it settled on, if any.

    A committed fold's only, as the module docstring says.
    """

    address: str
    text: str | None
    disposition: Disposition | None = None


class Committed(NamedTuple):
    """The fold committed: every place decided, none refused."""

    places: int


class RolledBack(NamedTuple):
    """The fold rolled back: at least one refusal or human question, nothing saved.

    `reasons` counts the reasons across the `Refused` events before it and one
    per `AsksTheHuman`, which is what every producer counts: the fold,
    `flows.bus` and the collate command's envelope check.
    """

    reasons: int


Event = (
    Refused
    | AsksTheHuman
    | CarriedForward
    | PlacementCarried
    | Advised
    | Settled
    | Committed
    | RolledBack
)
