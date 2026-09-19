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


class HeldMove(NamedTuple):
    """The move an unsettlable place is an end of, for the entry that names it.

    Attributes:
        role: who filed the move.
        reason: the move's own reason, which is what the author is shown.
        origin: the place the paragraph leaves.
        destination: the place it arrives at.
    """

    role: str
    reason: str
    origin: str
    destination: str


class Unsettlable(NamedTuple):
    """One place no turn can resolve, and who put it to the human.

    Attributes:
        address: the place.
        role: who asks the human -- the role whose query holds the place, or
            whose answer did.
        reason: why, in that role's own words.
        partner: the other end, where this place is one end of a move held at
            both (`decision-log.md Process: #155` and `#182`). The two ends
            are one entry, emitted once, so the author rules the move whole.
        move: the move this place is an end of, where it is one.
    """

    address: str
    role: str
    reason: str
    partner: str = ""
    move: HeldMove | None = None


class Advised(NamedTuple):
    """What one role is told about one place without being refused for it.

    It reports and decides nothing: a place carrying notes takes whatever
    state its marks give it, and a fold that emits one still commits
    (`decision-log.md Process: #177`).
    """

    role: str
    address: str
    notes: tuple[str, ...]


class Settled(NamedTuple):
    """One place the fold decided, and the text it settled on, if any."""

    address: str
    text: str | None


class Compacted(NamedTuple):
    """One place whose decided text a compaction replaced, and what it now reads.

    Stage 6 condenses text the fold already decided, so this reports an edit
    to a decided place rather than a decision (`decision-log.md Process:
    #191`). Every place is named, so a capped run can be read against the
    text the author is about to approve.
    """

    address: str
    text: str


class Committed(NamedTuple):
    """The fold committed: every place decided, none refused."""

    places: int


class RolledBack(NamedTuple):
    """The fold rolled back: at least one place refused, nothing saved."""

    reasons: int


Event = (
    Refused
    | CarriedForward
    | Unsettlable
    | Advised
    | Settled
    | Compacted
    | Committed
    | RolledBack
)
