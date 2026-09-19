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
