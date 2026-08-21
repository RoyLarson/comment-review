"""THE FOLIATION: numbering the places on a page, and reading the number back.

    python foliator.py --census census.json --repo D

FOUR FOLIATORS walk one trigger list -- the MODULE, every line of code, then
EOF -- each holding its own counter and the places it emitted. `foliate()` runs
the walk; `Foliation` answers back, which address does this line belong to right
now.

!! IT WAS CALLED `addresser.py`, and the name was wrong the way `pCST` was.
Roy, 2026-08-20: *"we have been using that word instead of address all session
... it doesn't cause the system to crash but it also doesn't make the system
work correctly either."* An ADDRESS is `path@folio`, and it is composed on the
PAGE -- this module supplies the folio and flattens the path, and addresses
nothing. Anyone reading the old name looked here for the wrong half.

! FOLIATION, not pagination: the numbering of LEAVES, which is what a place is.
A page is one file and its places are counted against the code, so nothing here
numbers a page.

! The form this replaced named a paragraph by LINE, `a.py:33-34`, which answers
"where is this in the file I just read" and cannot answer "which place is this":
this tool EDITS PROSE, and every prose edit moves the line numbers of the code
below it. ! That form was READ here until 2026-08-20, warning on every call, so
a run already recorded could be parsed. It is DELETED: nothing called it, and
`docs/history.md` says where the reader is in the history.

!! AN ADDRESS IS NOT A SPAN OF LINES. EVERY LINE HAS EXACTLY ONE ADDRESS, AND A
PARAGRAPH IS JUST THE LINES THAT SHARE ONE. Ruled 2026-08-19. ! Read it as a range
and the old system is back under a new name: you start asking which lines a
paragraph "covers", whether two paragraphs overlap, and how wide to make an addressing
range -- all questions a line-numbered address had and an address does not.
Three sessions in one day reached for a range after this was settled; it is
written here because the reflex is strong, not because it is subtle.

! An ANCHOR is the exception that proves it. A declaration carries prose at
several addresses -- the `b` above it, the `c` beside it, its own `a`, the `b`s
in its body -- so an anchor has many addresses. A LINE still has one.

!! THIS RESTS ENTIRELY ON THE CENSUS BEING WHAT ROY CALLED IT, 2026-08-18: a
HASHED STATIC TABLE -- exact, constant, FULLY ENUMERATED. Take away any one of
those and the scheme collapses without saying so:

  fully enumerated  a code line missed anywhere above a place SHIFTS ITS NAME.
                    Every foliator steps past every line of code, so a partial
                    enumeration does not fail -- it renames every place below
                    the hole, silently and consistently
  constant          the same file must count the same way twice, or two runs
                    cannot be compared, which is the whole point
  exact             a heuristic that is usually right is a table that is
                    occasionally renumbered

! What MAKES it constant across this tool's own work is stage 7b's CODE CHECK.
It does NOT prove the code byte-identical, and saying so overstates it: for
Python it compares an `ast.dump`, so the bytes may differ while the statements
and their ORDER do not; elsewhere it compares the stripped text. Either way what
holds is that the Nth code line is still the same statement -- which is exactly
what an ordinal counts. The line numbers move with the prose; the ordinal does
not.

! `ast.dump` would carry every DOCSTRING into that fingerprint, so rewriting one
-- the commonest edit this system makes -- would read as a code change.
`_blank_docstrings` empties each docstring's value before the dump: its CONTENT
is out of the proof, its PRESENCE is not. ! So adding or deleting a docstring
still changes the body's shape and still fails -- filed as
`TODO/the-code-check-refuses-add-and-drop-on-a-docstring.md`, and the reason an
`add` on a declaration cannot be written today.

!! AND IT PROVES NOTHING AT ALL ON AN UNPROVABLE FILE, which is the hard
exception this scheme rests on and must name. `prove_unchanged` returns
`unprovable` for a comment delimiter sharing a line with code, for an
unterminated paragraph comment, and for a census that disagrees with the file. Such
a run is REPORTED and counted a failure rather than passed -- so there is no
stage 8 to hand an address to, and the guarantee above is never claimed for a
file it does not cover.

! The numbering is invariant by construction rather than by luck -- but only
while the enumeration underneath it is complete.

Four series, because prose answers to one of exactly four subjects:

    package:core.py@a5    the 5th DECLARATION's documentation
    package:core.py@c3    BESIDE a line of code
    package:core.py@b3    a GAP between two lines of code
    package:core.py@f0    the FILE'S OWN matter, at either end

!! NO FOLIO IS COMPUTABLE FROM ANOTHER, OR FROM A LINE'S ORDINAL. Roy,
2026-08-19: *"remove any references that indicate anyone can expect that the
next line of code is guaranteed to have the next foliation index ... it is a
happenstance and may change at any point."* FOUR FOLIATORS walk one trigger
list -- the MODULE, every line of code, then EOF -- and EACH OWNS ITS RULE about
which triggers are its own. A series that does not emit for a trigger does not
take a number for it either, so **every series starts at 0**: `a` skips what is
not documentable, `b` and `c` skip the MODULE, `f` skips everything that is not
the MODULE or the file's own matter. Two series lining up on a file is an
OUTCOME of that walk. ! `f0` is the FILE'S OWN MATTER, in its own series -- not
the gap above the first line of code, which is `b0`. The two were one address
until the foliators split them, and one SERIES until 2026-08-20.

!! `a` IS SEPARATE FOR A DIFFERENT REASON: IT NAMES A SUBJECT, NOT A POSITION.
A docstring is about its DECLARATION, and `a0` is the module with `a1..aN` its
declarations in source order. Roy, 2026-08-18: *"a docstring is about the thing
above not the thing below"* -- so the direction question disappears, and Python's
docstring after its `def` and Rust's `///` before its `fn` number alike.

! Which declaration a doc belongs to is the CENSUS's to state and never this
module's to infer, because it is language-dependent and a parser knows it while
a position does not.

!! THE `a` NUMBER COUNTS DECLARATIONS, NOT CODE LINES, AND THAT IS A RULING.
Numbering each declaration by the `c` of its own `def` line would put all three
series on one count and was REJECTED 2026-08-19. Roy: `a` as "the module, class,
function, method definitions in order ... will make it easier for the agents to
use, vs having to cross-reference where cs are and then jump to there to see the
as." `a5` read directly is "the 5th definition in this file"; aligned to code
lines it is a number that means nothing until it is resolved against another
series.

!! THE SAME PLACE IS THE SAME ADDRESS WHETHER PROSE FILLS IT OR NOT, which is
the property line numbers cannot give. A comment paragraph occupying three lines and
an empty interval in the same position are both `b0`; a documented and an
undocumented declaration are both `a5`. So a finding can say where prose belongs
in a file that does not have it yet, and two versions of a file compare place by
place.

!! AN ADDRESS IS A SINGLE FACT, and the `a` series is what makes it one.
Measured 2026-08-18 over 9,975 paragraphs in this repo, 28 places were answered by
two paragraphs -- and 28 of 28 were a docstring sharing a gap with the comment run
beneath it, because a docstring was being named for the gap it sat in rather
than for the declaration it is about. With `a` the docstring leaves the `b`
series: re-measured over 10,744 paragraphs, 0 shared places.

! So an address alone identifies a place, and a record needs nothing beside it.
`--check` re-reads that claim on every run rather than trusting this paragraph.

!! ONE NAMING LIVES HERE, and the module is named for owning it. The LINE form
it replaced was kept beside it for a while, because one owner is what stops two
namings drifting -- they were computed in two modules for an hour and agreed,
which is exactly the property that cannot be relied on. There is nothing left to
drift from.
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from repo import READ_ERRORS  # noqa: E402  -- path shim must run first

ON = "c"
GAP = "b"
DECLARED = "a"
# !! THE FILE'S OWN PROSE, IN ITS OWN SERIES. Roy, 2026-08-20: *"we should have
# just made the front matter its own foliation -- then the rule that `b` owns
# all the lines that are not another foliation's lines would explicitly stay
# true. Treating the front matter as regular comments, even though they are
# not, is the mistake."*
#
# ! IT WAS `b0` UNTIL THEN, and that cost an EXCEPTION in every sweep that
# shares a gap out: `attach` gives front matter `b0` wherever it sits, so it is
# the one paragraph whose folio disagrees with the gap it occupies. Measured
# 2026-08-20 over 662 corpus files -- 51 paragraphs where a licence header was
# reported as an `interval`, a place holding no prose, because the gap it sat
# in re-cut it.
#
# ! A SINGLETON SERIES IS STILL A SERIES. Roy: *"I know it is likely a
# singleton foliation but it fits."* The rule then needs no clause about which
# `b` is not really a `b`.
#
# ! AND IT MAY NOT STAY A SINGLETON. Roy, 2026-08-20: *"maybe it will show up in
# more places for copyright or other pieces in the docs files."* So it is
# COUNTED like any other series rather than hardcoded to one place -- `f0` today
# because the walk emits it at the module and nowhere else, and `f1..fN` the day
# a second front-matter place is emitted.
FRONT = "f"

# !! EVERY SERIES THERE IS, AND THE ONLY LIST OF THEM. Adding one is a row here
# -- the same rule `lexer.LANGUAGES` follows. Roy, 2026-08-20: *"we may find
# another specific type that doesn't match these four's purposes, so keep the
# code generic in how it picks it up even if we don't know the shape."*
#
# !! THE FOURTH COST FOUR EDITS AND TWO BUGS, which is the argument for this
# list. `foliate` merged three foliators' places and not the fourth, so `f0` had
# no anchor and no paragraph; `_series_of` inferred the series from two fields
# that a fourth fits neither of, so front matter answered as a `b`; and the CLI's
# `--series` refused `f` outright -- the one route a reviewer has to ask for the
# file's own place.
#
# ! ORDER IS THE ORDER A READER MEETS THEM: the file's own matter, then a
# declaration's documentation, the gap above a line, the room beside it.
SERIES = (FRONT, DECLARED, GAP, ON)


#: The FIRST TRIGGER every foliator steps past: the file itself, before any line
#: of code. It is what `a0` and `f0` name, and the one trigger `c` does not emit
#: for -- a module has front matter and a docstring, and no line to sit beside.
MODULE = "<module>"

#: The LAST TRIGGER, past the final line of code. `b` emits for it -- the gap
#: after the last statement is a place prose can go -- and `a`, `c` and `f` skip
#: it today.
#:
#: !! IT IS A TRIGGER AND NOT AN ARITHMETIC RULE, ruled by Roy 2026-08-21. The
#: alternative was `b` emitting N+1 places per walk by definition, which is what
#: the code did and is one line shorter. He ruled against it because `f` will
#: almost certainly want this trigger too -- tail matter, an index or a glossary
#: at the END of a file -- and then two series would each carry a different
#: special rule: *"that makes two conditions where you would have to understand
#: to keep the code consistent, and why 1 gets a +1 and the other gets some other
#: treatment -- which is the reason each foliator owns its own rules."*
#:
#: ! So the cost is paid once, here: every series meets EOF and decides, exactly
#: as it does at MODULE, and adding `f`'s tail place later is a row rather than a
#: second arithmetic.
EOF = "<eof>"


def triggers(code: list[int]) -> list[int | str]:
    """What a foliator walks: the MODULE, every line of code, then EOF.

    !! ONE LIST, SO THE THREE SERIES CANNOT DRIFT APART. Each folio used to be a
    different expression computed where it was needed -- `declares` for `a`,
    `code.index(start)` for `c`, `sum(1 for n in code if n < at)` for `b` --
    three mechanisms for one question, *which step am I*. Roy, 2026-08-19:
    *"every adjustment to the rules has to be edited thoroughly in each place ...
    manually indexing clearly causes issues to remember."* Aligning `b` and `c`
    earlier that day took both expressions plus prose in four places, and it was
    still wrong: `b0` named the module's front matter AND the gap above the
    first line of code, so a licence header and the comment introducing the
    first declaration answered to one address.

    ! BOTH ENDS ARE SENTINELS, and neither is a line. The MODULE is the file
    before any code and EOF is the file after all of it, so a series that emits
    for either is naming a place no line of code occupies.

    Args:
        code: the line numbers that hold code, in order.

    Returns:
        `[MODULE, *code, EOF]`. A LINE is an int and each SENTINEL is a str,
        which is how a reader -- and a type checker -- tells the two apart.
    """
    return [MODULE, *code, EOF]


@dataclass
class Foliator:
    """One series' counter, and every place it emitted.

    !! IT HOLDS BOTH HALVES. Roy, 2026-08-19: *"the foliator gets an anchor and
    emits an address and should add the address and the anchor to an internal
    list or dict."* A folio and the line of code it is attached to are one fact,
    so they are stated by one step of one walk -- not computed here and
    decorated on later, which is what let an anchor disagree with its address.

    !! A SERIES OWNS ITS OWN RULE ABOUT WHAT IT SKIPS, AND SKIPPING TAKES NO
    NUMBER. Roy, 2026-08-20: *"the foliations own their own rules on what is
    skipped. `<module>` and its paragraph types get passed to all three, they
    each decide to record and increment independently -- `a` skips
    undocumentables, `b` and `c` skip `<module>`, `f` skips everything but
    `<module>`/matter components."* So a foliator that does not emit for a
    trigger does not advance either, and **every series starts at 0**.

    ! A `skip()` that INCREMENTED is what this replaces. It burned `b0` and made
    the first line of code `c1`, so two series began at 1 for no reason a reader
    could derive -- and nothing tested it, which is how 735 green tests passed
    over it.

    Attributes:
        series: `a`, `b`, `c` or `f`.
        places: folio -> the LINE OF CODE it is attached to, in emission order.
    """

    series: str
    places: dict[str, str] = field(default_factory=dict)
    _step: int = 0

    def emit(self, anchor: str) -> str:
        """Take this trigger's number, record the anchor, and return the folio."""
        got = folio(self.series, self._step)
        self.places[got] = anchor
        self._step += 1
        return got


@dataclass
class Foliation:
    """Every place in one file, and the line of code each is attached to.

    !! IT ANSWERS BOTH DIRECTIONS, which is why it is one object. The walk
    assigns the foliation; these read it back -- *which address does this line
    belong to right now*. Roy, 2026-08-19: that second half *"helps the agents
    understand what they are looking at right now in the code -- they need to
    search it anyways."*

    ! Reading back is a LOOKUP, never arithmetic. `above` scans the code lines
    the walk stepped and returns the folio it EMITTED there; it does not count
    anything. That is the difference between line order driving the walk and a
    line number computing a number.

    Attributes:
        places: folio -> the line of code it is attached to. Every place in the
            file, whether or not prose sits in it.
    """

    places: dict[str, str] = field(default_factory=dict)
    # !! EVERY PLACE IN READING ORDER, TOP TO BOTTOM, recorded by the walk that
    # emitted them. It is what a compositor sets from: a page IS its places in
    # sequence, and the sequence is a fact the walk knows rather than an
    # arithmetic over line numbers -- which shift the moment one paragraph grows.
    #
    # !! WHERE AN `a` FALLS IS THE LANGUAGE'S CALL AND IS SETTLED HERE, ONCE.
    # Rust puts a declaration's documentation ABOVE the declaring line; Python
    # puts it INSIDE the body, which a wrapped signature moves several lines
    # down. `lexer.declarations` states that as the line the doc occupies, and
    # the walk turns it into a position in this list -- so nothing downstream
    # asks the question again, and no two readers can answer it differently.
    reading: list[str] = field(default_factory=list)
    # !! WHERE EACH PLACE SITS, recorded by the walk that emitted it. A `b` is
    # bounded by the two lines of CODE around its gap -- 0 for the file's own
    # edge -- and a `c` sits ON one line. Nothing else may work these out: three
    # generators each re-derived them from the file, and that is how a gap held
    # by a comment came to have no place at all.
    #
    # ! They are BOUNDS and not an edit range. Turning one into the other needs
    # the file's own last line, which is the page's to know and not the walk's.
    bounds: dict[str, tuple[int, int]] = field(default_factory=dict)
    lines: dict[str, int] = field(default_factory=dict)
    # ! WHERE AN `a`'s PROSE WOULD GO, which is not its declaration's line:
    # a wrapped signature puts the first statement several lines down. Only
    # a parser knows it, so the lexer states it and the walk carries it.
    inserts: dict[str, int] = field(default_factory=dict)
    # Each keyed by the 1-based LINE the trigger sat on, so a reader with a
    # position can find the place without knowing how the walk numbered it.
    _above: dict[int, str] = field(default_factory=dict)
    _beside: dict[int, str] = field(default_factory=dict)
    _declared: dict[int, str] = field(default_factory=dict)
    _closing: str = ""
    _code: list[int] = field(default_factory=list)
    # ! The file's own places, as the walk emitted them -- see `matter`. TWO of
    # them, because a file carries matter at both ends and neither belongs to a
    # gap: a licence at the foot is the file's, exactly as one at the head is.
    _front: str = ""
    _back: str = ""

    def above(self, line: int) -> str:
        """The `b` whose gap a paragraph inserting at `line` falls into.

        ! The gap above the FIRST code line at or after `line`. Past the last
        one it is the closing gap, which is the place with no line below it.
        """
        for n in self._code:
            if line <= n:
                return self._above[n]
        return self._closing

    def beside(self, line: int) -> str:
        """The `c` on this line of code, or "" if the line holds no code."""
        return self._beside.get(line, "")

    def documents(self, ordinal: int) -> str:
        """The `a` for the nth documentable declaration; 0 is the module."""
        return self._declared.get(ordinal, "")

    def anchor_line(self, folio: str) -> int:
        """The LINE the anchor of this place sits on. 0 when it has none.

        !! THE WALK ALREADY KNOWS IT and it was only ever asked for one series.
        `lines` holds it for an `a` (its declaring line) and a `c` (its own code
        line); a `b` is bounded by two, and the one it is ANCHORED to is the
        line BELOW the gap -- the statement its prose introduces -- or the line
        above when the gap closes the file.

        ! The MODULE has no line, so `a0` and the `f` place answer 0. That is a
        real answer and not a miss: a licence header and a module docstring sit
        above everything the file declares.

        ! WHY IT IS WANTED. Roy, 2026-08-20: records are ordered by anchor line
        and then by series LETTER -- *"I don't want to use foliation number
        because that would imply it would not change."* A sort on the number
        would encode a stability this module explicitly disclaims.
        """
        if folio in self.lines:
            return self.lines[folio]
        previous, following = self.bounds.get(folio, (0, 0))
        return following or previous

    def matter(self) -> str:
        """`f0` -- the file's own prose, above anything it declares.

        ! It is not the gap above the first line of code. That is `b0`, and the
        two were one address until the walk emitted both.

        !! ITS OWN SERIES SINCE 2026-08-20, and it was `b0` before. As a `b` it
        was the one paragraph whose folio disagreed with the gap it sat in --
        `attach` gives it this place WHEREVER IT SITS -- so every sweep that
        shares a gap out needed a clause naming it. Roy: *"treating the front
        matter as regular comments, even though they are not, is the mistake."*

        ! Read from the walk rather than named here, so a second front-matter
        place would answer correctly the day one is emitted.
        """
        return self._front

    def first_code_line(self) -> int:
        """The first line of CODE on this page, or 0 when it holds none.

        ! What says a run of prose is at the TOP of the file rather than merely
        first among the prose. A file whose only comment sits at its foot has a
        first run and a last run that are the same paragraph, and without this it
        was claimed as the head's.
        """
        return self._code[0] if self._code else 0

    def last_code_line(self) -> int:
        """The last line of CODE on this page, or 0 when it holds none.

        ! It is what says a run of prose has nothing below it, which is the one
        extra condition back matter carries over front matter. The walk stepped
        these lines, so it is asked rather than recomputed from the file.
        """
        return self._code[-1] if self._code else 0

    def back_matter(self) -> str:
        """`f1` -- the file's own prose at its FOOT.

        !! THE SAME RULE AS `f0`, READ FROM THE OTHER END. Roy, 2026-08-21, asked
        whether the foot of a file needed a rule of its own: *"same answer for
        the back matter because of the same reason."* A licence at the bottom
        belongs to the FILE, not to the last gap -- which is where it landed
        while this place did not exist, measured 2026-08-21 as `b2`.

        ! IT IS EMITTED AT THE `EOF` TRIGGER, which is why that trigger is
        explicit rather than an N+1 rule. Roy, the same morning: *"f will almost
        certainly get it and so we might as well pick up both now."*
        """
        return self._back


def foliate(
    code: dict[int, str],
    documentable: dict[int, int],
    module_insert: int | None = 1,
) -> Foliation:
    """Walk the anchors of one file; return every folio and its line of code.

    !! THE WALK IS WHAT MAKES EVERY PLACE EXIST. A place is emitted because the
    walk reached its trigger, not because prose was found sitting there -- which
    is why the file's own matter and the first gap can now both exist. Before
    this, the matter's place came from a BRANCH that fired only when front-matter
    prose had already been stamped, so the two were mutually exclusive: measured
    over five file shapes, the gap above the first line of code was `b1` on a
    file with no licence header and `b0` on a file with one, and adding a module
    docstring renamed it mid-run. ! They are `f0` and `b0` now, in two series.

    ! The three rules differ, and each is measured rather than chosen:

        a   the MODULE, then every documentable declaration. It does not step
            past a line it cannot emit for, so `a1` is the first declaration
            however much code precedes it.
        b   the MODULE, then the gap above every line of code, then the gap
            after the last one.
        c   every line of code. It steps past the module without emitting,
            because a module has no line to sit beside.

    ! Line ORDER drives the walk; no line NUMBER is arithmetic here. Nothing
    reads one folio to compute another, and no folio follows from a line's
    ordinal -- see `folio`.

    Args:
        code: `line number -> the exact characters on it`, ascending -- what
            `page.code_lines` returns. The number POSITIONS the trigger; it
            never numbers it, so the walk reads this in order and counts.
        documentable: index into `code` -> the line that declaration's doc
            would go on. The LEXER states both, because only a parser knows
            which lines declare and where a doc belongs.
        module_insert: where the MODULE's own doc would go, or None when the
            language has no documentable declaration at all -- then there is no
            `a` series, not an empty one.

    Returns:
        The `Foliation`: every place, and both directions between them.
    """
    # ! ONE PER SERIES, BUILT FROM THE LIST. The names below are for the
    # walk, which is genuinely per-series -- each emits at different
    # triggers -- but nothing downstream has to know how many there are.
    walkers = {name: Foliator(name) for name in SERIES}
    a, b, c, f = (walkers[s] for s in (DECLARED, GAP, ON, FRONT))
    out = Foliation(_code=list(code))
    # !! NO `a` SERIES AT ALL WHEN THE LANGUAGE HAS NO DOCUMENTABLE
    # DECLARATION. Roy, 2026-08-20: *"we need to be able to distinguish `a`
    # foliations for as many languages as there are `a` possible foliations.
    # yaml, toml are not ones."* A YAML file was given an `a0` -- a place for a
    # module docstring in a language that has none -- and no verdict could ever
    # fill it. `None` says the series does not exist; `1` says it does and the
    # module's own doc would open the file.
    # !! THE WALK READS `triggers()`, WHICH IS THE WHOLE POINT OF THERE BEING ONE.
    # It did not until 2026-08-21: this loop was written out by hand and
    # `triggers` had a single caller, a test asserting its SHAPE -- so the
    # function claiming *"ONE LIST, SO THE THREE SERIES CANNOT DRIFT APART"* was
    # not the list any series walked. Roy, seeing it: *"WHAT!!!"*
    #
    # ! Each series decides at each trigger, and that rule is now complete --
    # there is no step a place comes from except one of these.
    previous = 0
    seen = 0
    # ! Which `a` places are set at which step, filed by `page.documentable` and
    # released in the loop below. For an above-doc language every entry is filed
    # against the declaration's own step; Python's are filed later.
    release: dict[tuple[int, str], list[str]] = {}
    for trigger in triggers(list(code)):
        # ! A SENTINEL IS A STRING AND A LINE IS AN INT. Neither sentinel is a
        # line, which is what makes them sentinels.
        if isinstance(trigger, str):
            if trigger == MODULE:
                if module_insert is not None:
                    out._declared[0] = a.emit(MODULE)
                    out.inserts[out._declared[0]] = module_insert
                # ! `f0` is the FILE'S OWN matter, bounded by nothing: the head
                # of the file on both sides. It is not the gap above the first
                # line of code -- that is `b0`, and conflating them made the two
                # exclusive.
                out._front = f.emit(MODULE)
                out.bounds[out._front] = (0, 0)
                # ! THE HEAD OF THE PAGE, in the order a reader meets it: the
                # file's own matter, then the module's own documentation.
                out.reading.append(out._front)
                if 0 in out._declared:
                    out.reading.append(out._declared[0])
                # !! `b` AND `c` SKIP THE MODULE ENTIRELY -- no place, and no
                # number. It has no gap above it and no line to sit beside. Roy,
                # 2026-08-20: *"let's initiate all of them at 0 ... bs and cs
                # will stay aligned until there is some specific reason to split
                # them."*
            else:
                # !! `b` ALONE EMITS AT EOF, and it is a TRIGGER rather than an
                # N+1 rule -- ruled 2026-08-21 so that `f`'s tail place becomes a
                # row at this step rather than a second arithmetic. The gap after
                # the last line has no line below it, so it takes the one above;
                # a gap is bounded by code, and that is the bound it has. ! On a
                # file with no code at all this is the gap that IS the file.
                out._closing = b.emit(next(reversed(code.values())) if code else MODULE)
                out.bounds[out._closing] = (previous, 0)
                # !! `f` EMITS ITS SECOND PLACE HERE, and this is the reason the
                # EOF trigger is a trigger rather than an N+1 rule. A file's
                # matter sits at BOTH ends and neither end belongs to a gap:
                # `f0` is bounded by the head of the file on both sides, `f1` by
                # the foot. ! Bounded by nothing, exactly as `f0` is -- a licence
                # at the foot is the FILE's, not the last gap's, which is where
                # it landed while this place did not exist.
                out._back = f.emit(MODULE)
                out.bounds[out._back] = (0, 0)
                # ! THE FOOT OF THE PAGE: the gap after the last statement, then
                # the file's own matter, which is bounded by nothing.
                # ! A doc with no code after it is filed against the step past
                # the last one, which is this gap.
                out.reading.extend(release.pop((len(code), GAP), ()))
                out.reading.append(out._closing)
                out.reading.append(out._back)
            continue
        n = trigger
        line = code[n]
        if seen in documentable:
            # ! 0 is the module, so a declaration's ordinal is its position
            # among the documentable ones, counting from 1.
            declared = a.emit(line)
            out._declared[len(out._declared)] = declared
            out.lines[declared] = n
            # !! TWO FACTS, AND THE WALK USES ONLY THE SECOND. `page.documentable`
            # states the LINE the doc occupies -- which `page.documented_by` walks
            # up from to find prose already there -- and the code ordinal it is
            # SET BEFORE, which is the language's rule already resolved. The walk
            # holds the place until that step and compares nothing.
            out.inserts[declared], at_step, side = documentable[seen]
            release.setdefault((at_step, side), []).append(declared)
        gap = b.emit(line)
        out._above[n] = gap
        out.bounds[gap] = (previous, n)
        beside = c.emit(line)
        out._beside[n] = beside
        out.lines[beside] = n
        # !! THE ORDER A READER MEETS THEM: the gap above this line, then any
        # declaration whose documentation belongs at or before it, then the line
        # itself with the room beside it.
        #
        # !! THE MIDDLE STEP IS THE PER-LANGUAGE QUESTION, AND IT IS NOT ASKED
        # HERE. `page.documentable` already resolved it into a code ordinal, so
        # this releases whatever was filed against this step. An above-doc
        # language files a declaration against its own step and its `a` sits
        # above the code; Python files it against the body's first statement, so
        # the docstring lands after the signature -- however many code lines a
        # wrapped one spans. ! No line is compared, which is what keeps the walk
        # free of arithmetic it would otherwise have to keep right.
        out.reading.extend(release.pop((seen, GAP), ()))
        out.reading.append(gap)
        out.reading.extend(release.pop((seen, ON), ()))
        out.reading.append(beside)
        previous = n
        seen += 1
    # !! EVERY FOLIATOR'S PLACES, COUNTED RATHER THAN LISTED. Naming them was
    # how `f0` came to sit in `bounds` and nowhere else: no anchor, and
    # `page.empty_places` -- which walks `places` -- gave it no paragraph, so a
    # file whose front matter is absent had a line belonging to nothing.
    out.places = {
        folio: anchor
        for name in SERIES
        for folio, anchor in walkers[name].places.items()
    }
    return out


def folio(series: str, step: int) -> str:
    """The folio at one step of the walk -- ONE expression, all three series.

    !! A SKIPPED TRIGGER TAKES NO NUMBER, so every series starts at 0. Roy,
    2026-08-20: *"the foliations own their own rules on what is skipped ... they
    each decide to record and increment independently."* `c` does not emit for
    the MODULE and does not step past it either, so its first line of code is
    `c0`.

    ! IT READ THE OTHER WAY UNTIL 2026-08-20, on the earlier half of the same
    ruling -- *"each gets its own counter and each gets passed the lines of code
    and the module, and the `c` knows it is supposed to skip it"* (2026-08-19),
    which said which triggers each series walks and was read as saying it takes
    a number at all of them. That burned `b0` and started `c` at 1.

    !! NOTHING READS ONE FOLIO TO COMPUTE ANOTHER, and no folio follows from a
    line's ordinal. Whether two series happen to line up on a given file is not
    stated anywhere, deliberately: Roy, 2026-08-19, *"I don't want to make that
    promise -- I don't know the edge cases where that might break yet,"* and
    *"remove any references that indicate anyone can expect that the next line
    of code is guaranteed to have the next foliation index."* A reader told the
    numbers coincide will rely on it whatever the sentence around it says.
    """
    return f"{series}{step}"


#: The character that joins path segments in an address. A path may not hold it
#: -- Windows forbids it outright, and `census.py` refuses a POSIX path that
#: does -- which is what makes `flatten` invertible. See `flatten`.
SEPARATOR = ":"


def flatten(path: str) -> str:
    """`pkg/sub/mod.py` as `pkg:sub:mod.py` -- the whole path, extension kept.

    !! THE ADDRESS IS THE FULL PATH from the runner's root, not the file name.
    Roy, 2026-08-18: "the address is the full thing not just `__init__@b0`".
    Files form a tree, so two complete paths differ somewhere, and the
    separator below carries that difference through into the address.

    !! THE EXTENSION STAYS. Dropping it reads better and reintroduces collisions
    the moment a repo holds `b.py` beside `b.rs` -- which this census supports by
    design, eleven languages in one run. Roy ruled it 2026-08-18: "we could have
    mixed languages in the system with the same names that without that we are
    back to collisions."

    !! THE SEPARATOR IS A CHARACTER A PATH CANNOT HOLD, and that is what makes
    this INVERTIBLE. It was `.` until 2026-08-19, and a dot is ordinary in a
    filename -- `app.test.js`, `types.d.ts` -- so `a/b.py` and `a.b.py` both read
    `a.b.py` and every one of their addresses collided. Roy: *"lets use an
    illegal symbol for the separator then."*

    ! `:` is the one Windows forbids that is NOT shell-special, so an address is
    safe as a bare command-line argument where `<`, `>`, `|`, `?` and `*` are
    not. Measured 2026-08-19 over 2,472 source paths in seven corpora: zero hold
    any of the seven. ! POSIX forbids only `/` and NUL, so a POSIX path CAN
    hold a colon and this would be ambiguous again -- `census.py` refuses such a
    file rather than addressing it.
    """
    return str(path).replace("\\", "/").replace("/", SEPARATOR)


def unflatten(name: str, paths: list[str]) -> str:
    """The real path a flattened one names, or "" if the census cannot say.

    ! It resolves against the CENSUS rather than by string surgery, because the
    census is what knows which paths exist. With `:` as the separator the form
    is invertible, so this now answers for exactly one path or none.

    ! Ambiguity is still REFUSED rather than resolved by preferring one. It was
    reachable while the separator was `.`; it is kept because `census.py`'s
    refusal is what makes it unreachable, and a reader here should not have to
    know that to trust the answer.

    Args:
        name: the flattened path from an address, without the `@folio`.
        paths: the paths the census carries.

    Returns:
        The one path whose flattened form is `name`, or "" when none or several
        do.
    """
    hits = {p for p in paths if flatten(p) == name}
    return hits.pop() if len(hits) == 1 else ""


def folio_of(address: str) -> tuple[str, str]:
    """An address split into its flattened path and its folio, or two blanks."""
    path, sep, where = address.rpartition("@")
    return (path, where) if sep else ("", "")


def resolve(address: str, paragraphs: list[dict]) -> list[int]:
    """Which census entries carry this address, as 1-based census indices.

    !! THE INVERSE IS A LOOKUP, NOT ARITHMETIC. `bN` is "the gap after code line
    N", and which entries sit there is a fact the census holds -- an empty
    interval, or a comment run filling the same gap, or both. Recomputing a line
    range from N would answer where the gap IS while the question asked which
    entries are THERE.

    ! Several entries can share one address and that is not an error: `c0` and
    `b0` are different places, but a comment run and the interval it occupies
    are the same place seen twice by a census built before an edit.

    Args:
        address: `pkg:mod.py@b3` or `pkg:mod.py@c3`.
        paragraphs: the census entries FOR THAT FILE, in census order.

    Returns:
        The 1-based positions within `paragraphs`, in order. Empty when nothing
        carries it -- which a caller reports rather than treating as "none".
    """
    return [i for i, b in enumerate(paragraphs, 1) if stable(b) == address]


def for_anchor(anchor: str, series: str, paragraphs: list[dict]) -> list[dict]:
    """The paragraphs of one SERIES belonging to one anchor -- `go`'s `c`, say.

    !! AN ANCHOR OWNS A PLACE IN EVERY SERIES, and asking for one by POSITION
    breaks the moment a language puts it elsewhere. Python's docstring sits
    AFTER its `def` and Rust's `///` BEFORE its `fn`, so "the paragraph above the
    declaration" names the doc in one language and the comment above it in the
    other. This asks the CENSUS, which parsed the file, instead of counting.

    The three, for a declaration:

      a   its documentation -- the docstring, or the place one would go
      c   the room BESIDE its opening line -- a trailing comment, or the place
      b   the gap ABOVE its opening line -- a comment run, or the place

    ! The MODULE has no line to open on, so it has an `a` and no `c`; its `b`
    is the gap before the first code line, which is where a licence header or
    a shebang sits.

    ! It returns a LIST because a census may carry none -- a language whose
    tier resolves no anchors at all -- and the caller reports that rather than
    receiving a guess. More than one is a census defect `--check` reports.

    Args:
        anchor: the LINE OF CODE, as the census stamped it -- `def f():`, not `f`.
        series: `a`, `b` or `c`.
        paragraphs: the census entries. Pass the FULL census; a filtered one is
            missing exactly the empty places this is most often asked for.

    Returns:
        The matching entries, in census order.
    """
    mine = [b for b in paragraphs if str(b.get("anchor", "")) == anchor]
    if series == DECLARED:
        return [
            b for b in mine if isinstance(b.get("declares"), int) and b["declares"] >= 0
        ]
    # !! EVERY SERIES CARRIES THE SAME SPELLING: THE LINE OF CODE. An `a`, the
    # `b` above it and the `c` beside it all answer to `def f():`, never to `f`
    # -- the name is not carried at all. It was two spellings until 2026-08-19,
    # which routed `b`/`c` through `anchor_line` that only an `a` filled, so asking
    # by the LINE found nothing: `--anchor 'def f():' --series c` answered "no
    # `c` place" on a census holding exactly that one.
    #
    # ! The paragraph's OWN series decides which places answer: an `a` declares,
    # a `c` has a column, a `b` has neither. No second field, no inference from
    # kind.
    direct = [b for b in mine if series_of(b) == series]
    if direct:
        return direct
    at = next(
        (b.get("anchor_line") for b in mine if isinstance(b.get("anchor_line"), int)),
        0,
    )
    path = {str(b.get("path", "")) for b in mine}
    here = [b for b in paragraphs if str(b.get("path", "")) in path]
    if not at:
        # !! THE MODULE HAS NO OPENING LINE, so it has no `c`, and the `b` it
        # answers with is `b0` -- the gap ABOVE THE FIRST LINE OF CODE.
        #
        # ! IT IS NOT THE FILE'S OWN MATTER. A licence header or a shebang is
        # `f0`, in its own series since 2026-08-20 -- and this comment said
        # otherwise until 2026-08-21, which is the exact reading `series_of`
        # below records as the defect the `f` series ended. Two comments in one
        # module gave contradictory accounts of what `b0` names.
        #
        # ! Every other anchor without a line is a tier that resolved no
        # declaration, and has neither.
        if series == GAP and any(b.get("declares") == 0 for b in mine):
            return [b for b in here if stable(b).endswith(f"@{GAP}0")]
        return []
    if series == ON:
        return [b for b in here if b.get("start") == at and b.get("end") == at]
    if series == GAP:
        # ! The gap ABOVE the declaration: the paragraph whose lines end just before
        # it. An empty gap holds no line, so it answers by its EDIT range.
        return [
            b
            for b in here
            if str(b.get("address", "")).split("@")[-1].startswith(GAP)
            and (b.get("end") == at - 1 or b.get("original_end") == at - 1)
        ]
    return []


def series_of(paragraph: dict) -> str:
    """Which series this paragraph's own address is in -- `a`, `b` or `c`.

    !! READ OFF THE ADDRESS, which is the one place the series is STATED. It was
    INFERRED from two other fields until 2026-08-20 -- a paragraph that declares
    is an `a`, one with a column is a `c`, everything else a `b` -- and the
    inference had no room for a fourth series. Front matter declares nothing and
    has no column, so it came back `b`, and `--anchor <module> --series b`
    answered with the file's own place.

    ! Inferring was meant to avoid a case per KIND, and reading the address
    avoids that too. It costs nothing: `for_anchor` is given a census, and an
    entry carrying no address is one no caller could cite anyway.
    """
    return folio_of(str(paragraph.get("address", "")))[1][:1]


def stable(paragraph: dict) -> str:
    """The place the census STAMPED on this paragraph, or "" if it carries none.

    !! IT READS; `place` COMPUTES. One implementation, one caller that runs it
    -- `page_for`, which holds the file text and the finished paragraph list at
    once -- and everything downstream reads the result. Two computations that
    agree today is not the property wanted, because only one of them can be
    right tomorrow.

    ! "" means the census predates the field. A caller REPORTS that rather than
    deriving a place from a census that never had one.
    """
    return str(paragraph.get("address", ""))


def main() -> int:
    """Print every census entry's ADDRESS and the kind of place it names.

    ! One address column, not two. The LINE form it once printed beside this one
    was deleted 2026-08-20; see `docs/history.md`.

    Returns:
        0 when every entry was addressed, 1 when any could not be, 2 when the
        census could not be read. ! This module reads no source file -- the
        census is the only input.
    """
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--census", required=True, help="the census JSON")
    ap.add_argument(
        "--check",
        action="store_true",
        help="verify every address resolves back to its own paragraph, and stop",
    )
    ap.add_argument(
        "--anchor",
        metavar="LINE",
        help="a LINE OF CODE, verbatim -- with --series, the address of that place",
    )
    ap.add_argument(
        "--series",
        choices=SERIES,
        help="which place OF that anchor: a its documentation, b the gap above"
        " its opening line, c the room beside it, f the file's own matter",
    )
    ap.add_argument(
        "--resolve",
        metavar="ADDRESS",
        help="an address in, the LINES that cover it out -- read it against a "
        "census of the file as it is NOW",
    )
    args = ap.parse_args()

    try:
        loaded = json.loads(Path(args.census).read_text(encoding="utf-8"))
    except READ_ERRORS as e:
        print(f"CANNOT READ {args.census} ({type(e).__name__})")
        return 2
    except json.JSONDecodeError as e:
        print(f"{args.census} is not JSON ({e})")
        return 2
    paragraphs = loaded.get("paragraphs", []) if isinstance(loaded, dict) else loaded
    if not isinstance(paragraphs, list) or not paragraphs:
        print(f"{args.census} carries no paragraphs")
        return 2

    # !! NO STALENESS SWEEP. This module answers about the CENSUS IT WAS GIVEN,
    # and every question it takes is census-internal: does each address resolve
    # to one paragraph, what lines does this census say an address names, which
    # place is this anchor's `c`. None of them reads the tree.
    #
    # !! CHECKING THE FILE WOULD ASSERT THAT LINE NUMBERS STILL MATTER, which is
    # the thing an address exists to stop mattering. Roy, 2026-08-19: *"not
    # necessary for foliation to do the staleness sweep as long as the original
    # census is still an available document ... it doesn't matter that the file
    # changed lines underneath it. In a small way it is the foliation stating
    # the line numbers matter still."*
    #
    # ! A sweep WAS here, added after four artifacts three edits old were each
    # read as a defect in the code. That failure was real and the guard was in
    # the wrong module: staleness matters where a file is WRITTEN, and
    # `galley.paragraph_matches` already refuses a stale range before it splices.
    # Here it refused a census built seconds earlier on every non-Python file
    # carrying a trailing comment, with a message that re-running never fixed --
    # and it masked a genuine collision `--check` exists to report.
    #
    # ! THE CALLER CHOOSES THE CENSUS, which is what makes this safe. Stage 8
    # censuses the file as it now stands and resolves against that, so the two
    # agree by construction rather than by inspection.

    if args.anchor:
        if not args.series:
            print("--anchor needs --series: a, b, c or f")
            return 2
        return _for_anchor(args.anchor, args.series, paragraphs)
    if args.resolve:
        return _resolve_one(args.resolve, paragraphs)
    if args.check:
        return _check(paragraphs)

    unplaced = 0
    for i, paragraph in enumerate(paragraphs, 1):
        where = stable(paragraph)
        if not where:
            unplaced += 1
        kind = paragraph.get("kind", "")
        print(f"{i:4d}  {stable(paragraph) or 'UNPLACED':<34} {kind}")
    if unplaced:
        print(f"\n{unplaced} entries could not be addressed.")
    return 1 if unplaced else 0


def _resolve_one(address: str, paragraphs: list[dict]) -> int:
    """An address in, the LINES that now cover it out.

    !! THIS IS THE DIRECTION STAGE 8 NEEDS, and it needs it because 7b has
    already written. Roy, 2026-08-18: *"in goes an address out comes the line
    numbers that cover that address ... particularly important after 7b and
    stage 8 wants to look something up to double check."* Every line number a
    record carried is stale by then; the ADDRESS is not, so a census of the
    file AS IT IS NOW turns it back into lines to read.

    ! Census the CURRENT file, not the one the run started from. The address is
    what survives an edit; the lines are what moved, and reading a pre-edit
    census here would hand back exactly the numbers 7b invalidated.

    ! Several entries can answer to one address -- a docstring and the comment
    run beneath it sit in the same gap -- so every match is printed. Measured
    2026-08-18: 12 such places in this repo's own 13 shipped scripts.

    Returns:
        0 when the address named something, 1 when nothing carries it.
    """
    path, where = folio_of(address)
    if not where:
        print(f"{address!r} is not an address -- it needs a `@place`")
        return 2
    real = unflatten(path, sorted({str(b.get("path", "")) for b in paragraphs}))
    if not real:
        print(f"no file in this census flattens to {path!r}")
        return 1
    mine = [b for b in paragraphs if str(b.get("path", "")) == real]
    hits = resolve(address, mine)
    if not hits:
        print(f"{address} names no entry in this census")
        return 1
    for i in hits:
        paragraph = mine[i - 1]
        span = f"{paragraph.get('start')}-{paragraph.get('end')}"
        print(f"{real}:{span}\t{paragraph.get('kind', '')}")
    return 0


def _for_anchor(anchor: str, series: str, paragraphs: list[dict]) -> int:
    """Print the address of one anchor's place in one series.

    Returns:
        0 when a place was named, 1 when the census carries none for that
        anchor and series -- which is a fact about the run, not a fault: a
        language whose tier resolves no anchors has none to give.
    """
    found = for_anchor(anchor, series, paragraphs)
    if not found:
        known = sorted({str(b.get("anchor")) for b in paragraphs if b.get("anchor")})
        print(f"no `{series}` place for anchor {anchor!r}")
        if known:
            print(f"  anchors this census carries: {', '.join(known[:12])}")
        return 1
    for b in found:
        where = stable(b)
        span = f"{b.get('start')}-{b.get('end')}"
        print(f"{where}	{span}	{b.get('kind', '')}	{b.get('anchor', '')}")
    # !! AN ANCHOR HAS MANY ADDRESSES, so this direction is not a lookup that
    # returns one. Roy, 2026-08-19, on two identical statements in one file:
    # *"for the addresses this is still exact -- for looking up the anchors to
    # get the addresses, not so exact."* `X=2  # initial` and `X=2  # reseting
    # X` are two anchors spelled the same, and the census carries five places
    # under that spelling. Every match is printed and the CALLER picks by
    # address; taking the first would silently rule on the wrong statement.
    if len(found) > 1:
        print(
            f"\n{len(found)} places answer to anchor {anchor!r} in `{series}`."
            " An anchor has many addresses and an address has one anchor, so"
            " two identical lines of code are two anchors spelled alike."
            " Choose by ADDRESS."
        )
    return 0


def unaddressed(paragraphs: list[dict]) -> list[str]:
    """Which paragraphs carry NO address, described one per line.

    !! ONE SOURCE OF TRUTH, and the reason is the failure it prevents. Roy,
    2026-08-20: *"one source of truth, else something will parse that something
    else will fail."* Three callers ask this question -- `census.py` before it
    writes, `verdicts.py` before it certifies, and `foliator.py --check` -- and
    a second implementation of "is this addressed" is a second answer waiting to
    disagree with the first.

    !! IT IS ASKED AT BOTH ENDS ON PURPOSE. The census refusing on EMIT catches
    its own degradation where it happens; the gate refusing on READ catches a
    file that reached it some other way -- a census from an older version, one
    edited by hand, one written by a run that crashed. `verdicts.py` takes a
    PATH and trusts what it parses, so nothing but this stands between a stale
    file and a certified review.

    !! WHAT IT COSTS TO SKIP: an unaddressed census yields an EMPTY
    accountability set, so every paragraph is unaccounted and none is
    ACCOUNTABLE. Measured 2026-08-20 on a 5-paragraph census with its addresses
    stripped and a report ruling on nothing: `0 findings ... over 0 prose
    paragraphs` and **"Every finding is admissible. Stage 5 may rule."** at exit
    0. The run reads as complete because there was nothing to be incomplete
    about.

    Args:
        paragraphs: the census, as `census.py --json` emits it.

    Returns:
        One sentence per unaddressed paragraph, naming its file and its lines.
        Empty when every paragraph carries an address.
    """
    out: list[str] = []
    for path in sorted({str(b.get("path", "")) for b in paragraphs}):
        mine = [b for b in paragraphs if str(b.get("path", "")) == path]
        for i, paragraph in enumerate(mine, 1):
            if not stable(paragraph):
                out.append(
                    f"{path} entry {i}: lines"
                    f" {paragraph.get('start')}-{paragraph.get('end')}"
                )
    return out


def _check(paragraphs: list[dict]) -> int:
    """Does every address resolve back to the one paragraph that carries it?

    !! THE REFERENCE HAS TO MATCH THE ANCHOR, and that is the whole worth of an
    address. Roy, 2026-08-18: an agent will grep and read the file anyway, so
    the lookup is convenience -- what a citation buys is that it names the place
    it claims. An address two paragraphs answer to resolves to the wrong prose, and
    nothing downstream can tell.

    ! THE SAME SHAPE `source_problem` ALREADY ENFORCES ON `SOURCES`. Roy: "same
    on the sources". There a citation carries `file:line | verbatim` and the
    check resolves the line and looks for the words; here an address carries a
    place and the check resolves it back to the entry. Both say: the reference
    is only worth what re-reading it proves.

    ! Two reports, and only the first is a fault. UNADDRESSED means the census
    cannot name the place at all -- no `original_start`, or no position -- and
    nothing can cite it.

    !! SHARED IS NOW A FAULT TOO, AND ITS OLD REMEDY IS GONE. It meant several
    paragraphs sat in one gap, and the advice was to cite the census INDEX
    alongside the address -- a field retired 2026-08-19, so a record carries an
    address and an anchor and nothing that tells two such paragraphs apart. The
    one shape that produced it is fixed: a licence header and the run below the
    module docstring both answered to `b0`, and `b0` is now the file's own front
    matter alone.

    Returns:
        1 when anything is UNADDRESSED, 0 otherwise. ! A shared place does not
        fail the check -- it is a fact about the file, and refusing it would
        refuse every docstring with a comment beneath it.
    """
    # ! ASKED, NOT RE-DERIVED. `unaddressed` is the one implementation, and
    # `census.py` and `verdicts.py` ask the same one.
    missing = unaddressed(paragraphs)
    shared: dict[str, list[str]] = {}
    for path in sorted({str(b.get("path", "")) for b in paragraphs}):
        mine = [b for b in paragraphs if str(b.get("path", "")) == path]
        for paragraph in mine:
            where = stable(paragraph)
            if where and len(resolve(where, mine)) > 1:
                shared.setdefault(where, []).append(
                    f"{paragraph.get('start')}-{paragraph.get('end')}"
                    f" {paragraph.get('kind', '')}"
                )
    for line in missing:
        print(f"UNADDRESSED  {line}")
    for where, rows in sorted(shared.items()):
        print(f"SHARED       {where}  <- {' | '.join(rows)}")
    named = len(paragraphs) - len(missing)
    files = len({str(b.get("path", "")) for b in paragraphs})
    print(f"\n{named} of {len(paragraphs)} paragraphs addressed over {files} files.")
    if shared:
        # ! Advice only where it applies. Printing it against zero shared places
        # tells a reader to guard something that did not happen.
        print(
            f"{len(shared)} places hold more than one paragraph"
            f" ({sum(len(v) for v in shared.values())} paragraphs) -- cite the census"
            f" index alongside the address for those."
        )
    if missing:
        print(
            f"{len(missing)} paragraphs could not be addressed at all."
            " A census with no `original_start` cannot name a gap; re-run census.py."
        )
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
