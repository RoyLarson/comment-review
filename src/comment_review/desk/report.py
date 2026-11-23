"""Stage reports rendered by the commands.

The stage reports refusals as `Refused`, from the fold or before it, and human
questions as `AsksTheHuman`. A rollback is reported as `RolledBack`.

A committed fold reports settled and carried-forward places, move
placements and advisory notes.

`refusal_line` is the one wording of a refusal line, printed by the
commands and by `flows.transcribe`. `rollback` reports the blockers and
then the `RolledBack` they cause, for the fold, the bus and
`commands/collate.py`.
"""

from collections.abc import Iterable
from typing import NamedTuple

from comment_review.desk.proof.answer import Question
from comment_review.desk.proof.disposition import Disposition
from comment_review.desk.proof.move import Placement
from comment_review.desk.proof.state import State


class Refused(NamedTuple):
    """One role's problems at one place or one move, as the messages that refused it."""

    role: str
    address: str
    reasons: tuple[str, ...]


def refusal_line(role: str, where: str, reason: str) -> str:
    """Render one refusal using the location label supplied by its caller."""
    return f"{role} {where}: {reason}"


class AsksTheHuman(NamedTuple):
    """One question a role put to the human, found before the fold ran.

    A human question never folds, so it rolls the stage or the turn back like
    a refusal, and says what is owed next -- the human's answer where there is
    none yet (`answer` empty), or, where the answers file holds it, the role's
    replacement for its query.
    """

    role: str
    at: str
    question: str
    answer: str = ""


class CarriedForward(NamedTuple):
    """A place the fold could not settle alone -- asked of `roles` next turn."""

    address: str
    state: State
    question: Question | None
    roles: tuple[str, ...]


class PlacementCarried(NamedTuple):
    """A move whose placement the fold could not settle -- asked of `roles` next turn.

    `open` is put to the readers of either page that did not file it and have
    neither agreed nor deferred; `contested` to its movers and the roles that
    stetted it, less those that defer.
    """

    origin: str
    destination: str
    placement: Placement
    roles: tuple[str, ...]


class Advised(NamedTuple):
    """What one role is told about one place without being refused for it.

    It reports and decides nothing: a place carrying notes takes whatever
    state its marks give it, and a fold that emits one still commits.
    """

    role: str
    address: str
    notes: tuple[str, ...]


class Settled(NamedTuple):
    """One place a fold decided, with the chief's ruling where there is one."""

    address: str
    disposition: Disposition | None = None


class Committed(NamedTuple):
    """The fold committed: every place decided, none refused."""


class RolledBack(NamedTuple):
    """The fold rolled back: at least one refusal or human question, nothing saved."""


def rollback(
    blockers: Iterable[Refused | AsksTheHuman],
) -> list[Refused | AsksTheHuman | RolledBack]:
    """Report the blockers in order, then the rollback they caused."""
    return [*blockers, RolledBack()]


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
