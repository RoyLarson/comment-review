"""What a SERIES is: its letter, and the two kinds a place in it can be.

A place in a series is one of two kinds: its `present`, when prose fills it, and
its `absent`, when nothing does.

! WHAT IT COST TO HAVE THE LETTER APART FROM ITS PAIR: the letters were
`addresser`'s constants and the pairs were `lexer`'s enum, tied only by MEMBER
NAME and held equal by a test. `Kind`'s own docstring drew the table --

    a   docstring          undocumented
    b   comment            interval
    c   trailing-comment   margin
    f   matter             dark-matter

-- in PROSE, beside code that did not know a single letter. A reader asking
"which series is `b`" had to find a comment; a caller holding a cue letter and
wanting its kinds had to reach two modules that could not import each other.

!! AND `d` IS A SERIES HERE, WHICH IT WAS NOT BEFORE. It HAD been a kind with no
series and an exclusion written into three other modules; it is now a member
whose `absent` is None, which says the same thing where the thing is defined. ! A
fence has a present and no absence: an empty one could not be cited, and there is
nothing for `absent` to mean.

!! A LEAF. It imports nothing from this package, which is what lets BOTH
`addresser` -- which owns places and knows nothing of prose -- and `lexer` --
which owns prose and spells a declaration's `a` cue with `cue_for` -- take their
halves from one declaration instead of from each other.

`cue_for` spells a cue from a letter and a step, and `ADDRESSED`, `ABSENT`,
`BY_LETTER` and `BY_KIND` are lookups derived from `Series`.
"""

from enum import Enum, StrEnum
from typing import NamedTuple


class Kind(StrEnum):
    """Every kind a paragraph can be.

    ! A `StrEnum` MEMBER IS ITS STRING, so every `paragraph.kind == "docstring"`
    already written keeps working and nothing had to migrate.
    """

    DOCSTRING = "docstring"
    UNDOCUMENTED = "undocumented"
    COMMENT = "comment"
    INTERVAL = "interval"
    TRAILING = "trailing-comment"
    MARGIN = "margin"
    # !! MATTER -- THE FILE'S OWN PROSE, AS A PARAGRAPH TYPE.
    # A licence header, a shebang or a coding line is not an ordinary comment:
    # it answers to the FILE and not to any line of code.
    #
    # Matter runs from the file's opening line down, or from its closing line up,
    # until an empty line or a docstring -- so a shebang, a blank and a comment
    # are two runs, and the comment below the blank is a `b`, not part of `f0`.
    #
    # !! `matter` NAMES THE SPACE AND NOT A POSITION, which is what the `f`
    # series needs: a file can carry its own prose at the head and at the tail.
    # A licence at the BOTTOM of a file answers to the file as one at the top
    # does, so the kind must name both. ! It borrows nothing: `matter` is
    # already the word in `front-matter`.
    MATTER = "matter"
    DARK_MATTER = "dark-matter"
    # ! THE SPACE BETWEEN TWO PLACES. It answers to nothing -- every other
    # series answers to a line of code or to the file -- which is why its series
    # has no absence.
    LEADING = "leading"

    @classmethod
    def holds_no_prose(cls, kind: str) -> bool:
        """Is there nothing here for a reviewer to read?

        !! EVERY ABSENCE, AND `leading`, WHICH IS NOT ONE. An absence is a place
        the walk emitted and no prose filled; `leading` is not a place at all
        and holds no prose for a different reason -- there was never anything to
        hold. Both answer YES here, because holding no prose is what this is
        NAMED for.

        Args:
            kind: a paragraph's kind. A plain `str` is accepted because a binder
                read back from JSON holds strings, not members.
        """
        return kind in ABSENT or kind == cls.LEADING

    @classmethod
    def occupies_no_lines(cls, kind: str) -> bool:
        """Does this paragraph stand on no line of the file?

        !! `leading` IS THE WHOLE REASON THIS IS NOT THE SAME QUESTION AS ABOVE.
        It holds no prose and DOES stand on real blank lines, so it answers NO
        here. Every absence answers YES: `compositor.set_page` reads that as a
        place the walk emitted, which an `add` may fill.
        """
        return kind in ABSENT


class Definition(NamedTuple):
    """A series: the letter it is cued by, and the two kinds a place in it takes.

    ! NAMED, because `[0]` and `[1]` say nothing -- the same reason
    `addresser.Address` is a `NamedTuple`, and this repo has the measurement for
    what the alternative costs.

    Attributes:
        letter: the cue letter. `b3` is the fourth place of series `b`.
        present: the kind when prose fills the place.
        absent: the kind when nothing does, or None where absence cannot be
            cited -- which is `d` and only `d`.
    """

    letter: str
    present: Kind
    absent: Kind | None


class Series(Enum):
    """Every series there is, and the only list of them.

    !! ADDING ONE IS A ROW HERE AND A BRANCH IN `page.empty_places`.
    """

    DECLARED = Definition("a", Kind.DOCSTRING, Kind.UNDOCUMENTED)
    GAP = Definition("b", Kind.COMMENT, Kind.INTERVAL)
    ON = Definition("c", Kind.TRAILING, Kind.MARGIN)
    LEAD = Definition("d", Kind.LEADING, None)
    COVERS = Definition("f", Kind.MATTER, Kind.DARK_MATTER)

    @classmethod
    def of(cls, cue: str) -> "Series | None":
        """The series a cue belongs to -- `b3` is `GAP` -- or None for no cue.

        ! IT TAKES THE WHOLE CUE, not a letter, because every caller holds a cue
        and slicing one is the step that gets written differently at each site.
        """
        return BY_LETTER.get(cue[:1])

    @classmethod
    def of_kind(cls, kind: str) -> "Series | None":
        """The series a KIND belongs to, or None for a kind no series names.

        `margin` and `trailing-comment` are both `ON`.

        !! AND THE KIND ALONE IS NOT THE SAME QUESTION, which is the trap this
        exists to close. **Both kinds belong to one series, and the series is
        the question.**

        ! DERIVED FROM THE DEFINITIONS, never listed -- the same rule as
        `BY_LETTER` and `ABSENT` below the class, so a series added tomorrow
        answers here without anyone remembering to add it.
        """
        return BY_KIND.get(kind)


#: Every series a place can be CITED in -- `d` excluded, because a fence names
#: no place. It is what the walk emits addresses for.
#:
#: ! DERIVED, NEVER LISTED.
ADDRESSED = tuple(s.value.letter for s in Series if s.value.absent is not None)

#: Every kind that is a place holding no prose -- the `absent` of each series.
ABSENT = frozenset(s.value.absent for s in Series if s.value.absent is not None)

#: The series each letter names.
BY_LETTER = {s.value.letter: s for s in Series}

#: The series each KIND belongs to -- both of them, present and absent. `d` has
#: no absent kind and contributes one entry; every other series contributes two.
#:
#: ! DERIVED, NEVER LISTED, matching `BY_LETTER` and `ABSENT`.
BY_KIND = {
    kind: s
    for s in Series
    for kind in (s.value.present, s.value.absent)
    if kind is not None
}


def cue_for(series: str, step: int) -> str:
    """The cue at one step of a series -- ONE expression, all four series.

    ! NAMED FOR ITS DIRECTION, so it cannot collide with `cue()`: this BUILDS a
    cue from its parts, and `addresser.cue_of` takes one apart.

    !! IT LIVES HERE, NOT IN `addresser`. A cue is `f"{letter}{step}"`, which is
    what a SERIES is lettered for and holds no notion of a place -- so the LEXER
    can build one without importing the addresser, which this module's own
    header forbids: *the addresser knows nothing of prose, the lexer knows
    nothing of places*.
    """
    return f"{series}{step}"
