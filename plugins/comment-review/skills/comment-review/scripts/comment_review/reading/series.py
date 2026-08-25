"""What a SERIES is: its letter, and the two kinds a place in it can be.

!! THE LETTER SITS WITH THE PAIR, AND THAT IS THE WHOLE POINT OF THIS MODULE.
Roy, 2026-08-25, retracting his own earlier decision: *"I feel I messed up ...
when I made the decision not pairing cue letter and the present absent pairings
together. The present absent pairings is effectively what defines the series and
the identifier we give it should be right there with them."*

! WHAT IT COST TO HAVE THEM APART: the letters were `addresser`'s constants and
the pairs were `lexer`'s enum, tied only by MEMBER NAME and held equal by a
test. `Kind`'s own docstring drew the table --

    a   docstring          undocumented
    b   comment            interval
    c   trailing-comment   margin
    f   matter             dark-matter

-- in PROSE, beside code that did not know a single letter. A reader asking
"which series is `b`" had to find a comment; a caller holding a cue letter and
wanting its kinds had to reach two modules that could not import each other.

!! AND `d` IS A SERIES HERE, WHICH IT WAS NOT BEFORE. Roy, same ruling: *"the
remaining Kind.LEADING gets its own series d separately which I think it already
kind of does but the logic should be where that is defined not a layer
removed."* It HAD been a kind with no series and an exclusion written into three
other modules; it is now a member whose `absent` is None, which says the same
thing where the thing is defined. ! A fence has a present and no absence: an
empty one could not be cited, and there is nothing for `absent` to mean.

!! A LEAF. It imports nothing from this package, which is what lets BOTH
`addresser` -- which owns places and knows nothing of prose -- and `lexer` --
which owns prose and knows nothing of places -- take their halves from one
declaration instead of from each other.
"""

from enum import Enum, StrEnum
from typing import NamedTuple


class Kind(StrEnum):
    """Every kind a paragraph can be.

    !! THE TWO HALVES WERE SET IN DIFFERENT MODULES AND NOTHING TIED THEM. The
    lexer writes a positive because it found prose; `page.py` writes a negative
    because the walk emitted a place nothing filled. Which strings paired up was
    known only to a hand-kept tuple in a third file -- so when
    `trailing-comment` left one of those tuples on 2026-08-20, nothing
    structural noticed, and the two tuples drifted into holding the same four
    kinds while claiming to answer different questions.

    ! A `StrEnum` MEMBER IS ITS STRING, so every `paragraph.kind == "docstring"`
    already written keeps working and nothing had to migrate.
    """

    DOCSTRING = "docstring"
    UNDOCUMENTED = "undocumented"
    COMMENT = "comment"
    INTERVAL = "interval"
    TRAILING = "trailing-comment"
    MARGIN = "margin"
    # !! THE FILE'S OWN PROSE, AS A PARAGRAPH TYPE. A licence header, a shebang
    # or a coding line is not an ordinary comment: it answers to the FILE and
    # not to any line of code.
    MATTER = "matter"
    DARK_MATTER = "dark-matter"
    # ! THE SPACE BETWEEN TWO PLACES. It answers to nothing -- every other
    # series answers to a line of code -- which is why its series has no
    # absence. A `b` owned the blanks on BOTH sides of an `a` before it existed,
    # and a file came back blank-blank-comment where it was blank-comment-blank.
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
            kind: a paragraph's kind. A plain `str` is accepted because a census
                read back from JSON holds strings, not members.
        """
        return kind in ABSENT or kind == cls.LEADING

    @classmethod
    def occupies_no_lines(cls, kind: str) -> bool:
        """Does this paragraph stand on no line of the file?

        !! `leading` IS THE WHOLE REASON THIS IS NOT THE SAME QUESTION AS ABOVE.
        It holds no prose and DOES stand on real blank lines. `code_lines` skips
        a paragraph that occupies nothing, so answering YES here would take
        those blanks out of `occupied`, read them as CODE, and renumber every
        `b` and `c` below them.
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

    !! ADDING ONE IS A ROW HERE. Roy, 2026-08-20: *"we may find another specific
    type that doesn't match these four's purposes, so keep the code generic in
    how it picks it up even if we don't know the shape."*

    ! THE FOURTH COST FOUR EDITS AND TWO BUGS before the list existed: the walk
    merged three addressers' places and not the fourth, so `f0` had no anchor
    and no paragraph; the series was INFERRED from two fields a fourth fits
    neither of, so front matter answered as a `b`.
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


#: Every series a place can be CITED in -- `d` excluded, because a fence names
#: no place. It is what the walk emits addresses for.
#:
#: ! DERIVED, NEVER LISTED. It was a hand-kept tuple in `addresser` while the
#: letters lived there.
ADDRESSED = tuple(s.value.letter for s in Series if s.value.absent is not None)

#: Every kind that is a place holding no prose -- the `absent` of each series.
ABSENT = frozenset(s.value.absent for s in Series if s.value.absent is not None)

#: The series each letter names.
BY_LETTER = {s.value.letter: s for s in Series}
