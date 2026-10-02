from enum import StrEnum, auto


class State(StrEnum):
    """What evaluation decided at one place."""

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
#: `commands.collate._counted` and `flows.transcribe._unclosed` read this
#: same set to count settled places and refuse an unfinished proof.
SETTLED = frozenset({State.STANDS, State.AGREED})
