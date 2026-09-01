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
    #
    # !! AND IT STOPS AT A BLANK, WHICH THIS COMMENT DID NOT SAY UNTIL
    # 2026-08-26. Roy's ruling of 2026-08-21 has two halves and only the first
    # was carried here: *"if the opening/closing line is a comment then the
    # matter continues down/up until there is an empty line or the start/end of
    # a docstring."* The `where it stops` half is the one that decides anything,
    # and the tokenized reader did not implement it -- a shebang, a blank and a
    # comment became ONE matter run, so the comment below the blank took `f0`
    # and an `add` at `b0` re-read as `f0`. See `lexer.paragraphs_stdlib`.
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

    @classmethod
    def of_kind(cls, kind: str) -> "Series | None":
        """The series a KIND belongs to, or None for a kind no series names.

        `margin` and `trailing-comment` are both `ON`.

        !! IT IS WHAT REPLACED `Paragraph.original_column`, 2026-08-31 --
        `decision-log.md Process: #69`. That field was a single `int` read for
        its TRUTHINESS at four sites, each asking *is this paragraph beside
        code*. Roy: *"the Series cue system does it better, more precisely, and
        is more flexible."*

        !! AND THE KIND ALONE IS NOT THE SAME QUESTION, which is the trap this
        exists to close. MEASURED 2026-08-31 over 11,702 paragraphs of this
        repo: `original_column` is truthy for 5,286 places that are NOT
        `trailing-comment` -- every one a `margin`, the EMPTY `c`, which records
        where a comment would go. A `kind == TRAILING` test would have dropped
        all of them. **Both kinds belong to one series, and the series is the
        question.**

        ! DERIVED FROM THE DEFINITIONS, never listed -- the same rule as
        `BY_LETTER` and `ABSENT` above it, so a series added tomorrow answers
        here without anyone remembering to add it.
        """
        return BY_KIND.get(kind)


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

#: The series each KIND belongs to -- both of them, present and absent. `d` has
#: no absent kind and contributes one entry; every other series contributes two.
#:
#: ! DERIVED, NEVER LISTED, matching `BY_LETTER` and `ABSENT`. A hand-kept map
#: is what `ADDRESSED`'s own comment records going stale.
BY_KIND = {
    kind: s
    for s in Series
    for kind in (s.value.present, s.value.absent)
    if kind is not None
}


def cue_for(series: str, step: int) -> str:
    """The cue at one step of a series -- ONE expression, all four series.

    ! NAMED FOR ITS DIRECTION, so it cannot collide with `cue()` again: this
    BUILDS a cue from its parts, and `addresser.cue_of` takes one apart.

    !! IT LIVES HERE, NOT IN `addresser`, SINCE 2026-08-31 -- `decision-log.md
    Process: #69`. A cue is `f"{letter}{step}"`, which is what a SERIES is
    lettered for and holds no notion of a place -- so the LEXER can build one
    without importing the addresser, which this module's own header forbids:
    *the addresser knows nothing of prose, the lexer knows nothing of places*.
    ! That is what let `Paragraph.declares` go: the lexer stamps `a3` where it
    used to stamp the bare ordinal `3` for something else to convert back.

    !! A SKIPPED TRIGGER TAKES NO NUMBER, so every series starts at 0. Each
    series owns its rule about what it skips and records and increments
    independently: `c` does not emit for the MODULE and does not step past it
    either, so its first line of code is `c0`. ! Reading it the other way --
    that a series takes a number at every trigger it is offered -- burns `b0`
    and starts `c` at 1.

    !! NOTHING READS ONE CUE TO COMPUTE ANOTHER, and no cue follows from a
    line's ordinal. Whether two series happen to line up on a given file is not
    stated anywhere, deliberately: the edge cases where it breaks are not known,
    and a reader told the numbers coincide will rely on it whatever the sentence
    around it says.
    """
    return f"{series}{step}"
