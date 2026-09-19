"""The six states a place can be in once evaluated."""

from enum import StrEnum, auto


class State(StrEnum):
    """The six a place can be in once evaluated."""

    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()

    STANDS = auto()
    AGREED = auto()
    COMPOSED = auto()
    CONTESTED = auto()
    UNSETTLABLE = auto()
    REFUSED = auto()


#: The states a fold carries forward for a turn or the chief.
CARRIED = frozenset({State.COMPOSED, State.CONTESTED})

#: The states a place is settled in. One side's proposal that every reader
#: accepted stands; several roles' identical proposals are agreed. A place in
#: either may hold a decided text, and `desk.evaluate.compaction` is what
#: reads this: a later edit to a decided text -- a compaction -- may be
#: written only where the fold settled one (`decision-log.md Process: #191`).
SETTLED = frozenset({State.STANDS, State.AGREED})
