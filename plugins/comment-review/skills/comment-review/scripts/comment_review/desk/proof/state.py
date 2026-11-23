"""Place evaluation states and the sets carried forward or settled."""

from enum import StrEnum, auto


class State(StrEnum):
    """What evaluation decided at one place."""

    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()

    #: Settled on the base when nobody proposed text, on a lone proposal
    #: when nobody is owed a say, or on the outcome of a chief ruling.
    #: The proof's text and disposition record how it settled.
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

#: The states a place has settled in. Multiple sides holding the same text
#: with nobody left to ask are `agreed`.
SETTLED = frozenset({State.STANDS, State.AGREED})
