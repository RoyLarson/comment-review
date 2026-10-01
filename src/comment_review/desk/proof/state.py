"""The seven states a place can be in once evaluated."""

from enum import StrEnum, auto


class State(StrEnum):
    """The seven a place can be in once evaluated."""

    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()

    STANDS = auto()
    AGREED = auto()
    COMPOSED = auto()
    CONTESTED = auto()
    REFUSED = auto()
    #: An end of a move whose placement is undecided. Its text waits on the
    #: placement: it decides none, asks no role anything, and takes no ruling,
    #: and once the placement is decided the end is evaluated as any place.
    TO_COME = "to-come"


#: The states a fold carries forward for a turn or the chief.
CARRIED = frozenset({State.COMPOSED, State.CONTESTED})

#: The states a place has settled in. One side's proposal that every reader
#: accepted `stands`; several roles' identical proposals are `agreed`, and a
#: place the roles left alone stands on the paragraph already there.
#:
#: It is the one statement of settled, and there were three. `_counted` in
#: `commands/collate.py` counted it by subtracting the carried and the
#: unsettlable from the whole, and `flows.transcribe._unclosed` named the two
#: carried states and `REFUSED` -- so a seventh state would have had to be
#: added to three places that never mention each other. Both read this now,
#: and `UNSETTLABLE` is the one state that is neither settled nor unfinished:
#: it rides to the human with its question and carries no text.
SETTLED = frozenset({State.STANDS, State.AGREED})
