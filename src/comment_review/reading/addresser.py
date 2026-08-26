"""THE ADDRESSER: numbering the places on a page, and reading the number back.

    python addresser.py --census census.json --anchor "def f():" --series a

FOUR ADDRESSERS walk one trigger list -- the MODULE, every line of code, then
EOF -- each holding its own counter and the places it emitted. `cue()` runs
`cue`; `Cues` answers back, which address does this line belong to right
now.

!! BOTH HALVES OF AN ADDRESS ARE MADE HERE, and joined in one place. `flatten`
makes the path half, `emit` makes the cue, `address_for` is the only site that
puts them together, `cue_of` splits one back and `unflatten` recovers the real
path.

!! IT ADDRESSES EVERY PLACE AND EVERY POTENTIAL PLACE. The empty places are what
an `add` cites, so giving them addresses is what makes `add` expressible at all.

!! AN ADDRESS IS NOT A SPAN OF LINES. NO LINE HAS MORE THAN ONE, AND A
PARAGRAPH IS JUST THE LINES THAT SHARE ONE. ! Read it as a range and every
question a line-numbered address had comes back: which lines a paragraph
"covers", whether two overlap, how wide to make the range. This tool EDITS
PROSE, and a prose edit moves the line numbers of everything below it -- so a
page is taken apart into places and set back from the places alone, consulting
no line number anywhere.

! An ANCHOR is the exception that proves it. A declaration carries prose at
several addresses -- the `b` above it, the `c` beside it, its own `a`, the `b`s
in its body -- so an anchor has many addresses. A LINE still has one.

! THE `d` SERIES TAKES NO ADDRESS AT ALL -- see `LEAD` for why, and `SERIES`
for what it takes instead.

!! THIS RESTS ENTIRELY ON THE CENSUS BEING WHAT ROY CALLED IT, 2026-08-18: a
HASHED STATIC TABLE -- exact, constant, FULLY ENUMERATED. Take away any one of
those and the scheme collapses without saying so:

  fully enumerated  a code line missed anywhere above a place SHIFTS ITS NAME.
                    Every addresser steps past every line of code, so a partial
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

!! NO CUE IS COMPUTABLE FROM ANOTHER, OR FROM A LINE'S ORDINAL. Where two
series happen to line up on a file that is a happenstance and may change at any
point. FOUR ADDRESSERS walk one trigger
list -- the MODULE, every line of code, then EOF -- and EACH OWNS ITS RULE about
which triggers are its own. A series that does not emit for a trigger does not
take a number for it either, so **every series starts at 0**: `a` skips what is
not documentable, `b` and `c` skip the MODULE, `f` skips everything that is not
the MODULE or the file's own matter. Two series lining up on a file is an
OUTCOME of `cue`. ! `f0` is the FILE'S OWN MATTER, in its own series -- not
the gap above the first line of code, which is `b0`. The two were one address
until the addressers split them, and one SERIES until 2026-08-20.

!! `a` IS SEPARATE FOR A DIFFERENT REASON: IT NAMES A SUBJECT, NOT A POSITION.
A docstring is about its DECLARATION, and `a0` is the module with `a1..aN` its
declarations in source order. The direction question disappears here: Python's
docstring after its `def` and Rust's `///` before its `fn` number alike, because
the number counts declarations rather than positions.

!! SUPERSEDED 2026-08-21 -- THE REASON GIVEN FOR THAT WAS A RULING, AND IT WAS
WRONG. This paragraph cited Roy, 2026-08-18: *"a docstring is about the thing
above not the thing below."* He struck it the same day it was tested against a
language that does the opposite: *"that was true for python and I messed up. We
have a better discriminator now and the docstring and its position are
determined by the language not my on-off statement."*

!! SO NO POSITIONING RULE IS STATED IN THIS MODULE, OR ANYWHERE BUT ONE PLACE.
Roy: *"All framing about positioning should come from the language and should be
only in either the language definition file, or a reference to the language
definition file in lexer and compositor. The language definition file should be
a leaf separate from everything else and imported only by lexer and
compositor."* So `language.py` says where a language puts its documentation, two
modules read it, and every step after carries what they state. ! Which
declaration a doc belongs to is stated by the LEXER and never inferred by this
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

from dataclasses import dataclass, field
from typing import NamedTuple

from comment_review.reading.series import ADDRESSED, Series

# !! THE LETTERS COME FROM THE SERIES DEFINITION, since 2026-08-25. Roy: *"The
# present absent pairings is effectively what defines the series and the
# identifier we give it should be right there with them."* They were spelled
# here and the pairs were spelled in `lexer` -- two modules that cannot import
# each other, tied only by MEMBER NAME and held equal by a test. That test
# existed because there were two sources; there is one now.
#
# ! `series` IS A LEAF and holds no notion of a place, so taking the letters
# from it acquires no subject: this module still knows nothing about prose.
ON = Series.ON.value.letter
GAP = Series.GAP.value.letter
DECLARED = Series.DECLARED.value.letter
# !! THE FILE'S OWN PROSE, IN ITS OWN SERIES. `b` owns every line that is not
# another series' lines, and typing the file's own matter as an ordinary comment
# breaks that: it would take a `b` cue wherever it sits, making it the one
# paragraph whose cue disagrees with the gap it occupies, and a licence header
# then reads as an `interval` -- a place holding no prose -- because the gap it
# sits in re-cuts it.
#
# ! A SINGLETON SERIES IS STILL A SERIES, and the rule then needs no clause
# about which `b` is not really a `b`.
#
# ! AND IT IS COUNTED RATHER THAN HARDCODED TO ONE PLACE, because it may not stay
# a singleton -- a copyright or another piece in a docs file would want one.
# `f0` today, because `cue` emits it at the module and nowhere else; `f1..fN`
# the day a second front-matter place is emitted.
COVERS = Series.COVERS.value.letter

# !! EVERY SERIES THERE IS, AND THE ONLY LIST OF THEM. Adding one is a row here
# -- the same rule `lexer.LANGUAGES` follows. Roy, 2026-08-20: *"we may find
# another specific type that doesn't match these four's purposes, so keep the
# code generic in how it picks it up even if we don't know the shape."*
#
# !! THE FOURTH COST FOUR EDITS AND TWO BUGS, which is the argument for this
# list. `cue` merged three addressers' places and not the fourth, so `f0` had
# no anchor and no paragraph; `_series_of` inferred the series from two fields
# that a fourth fits neither of, so front matter answered as a `b`; and the CLI's
# `--series` refused `f` outright -- the one route a reviewer has to ask for the
# file's own place.
#
# ! ORDER IS THE ORDER A READER MEETS THEM: the file's own matter, then a
# declaration's documentation, the gap above a line, the room beside it.
# !! THE SPACE BETWEEN TWO PARAGRAPHS -- see `lexer.LEADING` for what it is and
# why. Roy ruled the letter 2026-08-21: *"and d works."*
#
# ! `l` WAS THE OBVIOUS CHOICE AND THE WORST POSSIBLE CHARACTER: `m.py@l0` reads
# as `@10`, and this whole scheme rests on a cue being unmistakable.
#
# !! IT IS THE ONE SERIES NOTHING CITES. Roy: *"there is no information to rule
# on. It is just there for document preservation."* So a `d` is kept out of
# `Page.prose` and out of record seeding, and NO EMPTY `d` IS EMITTED -- the
# other four series exist wherever prose COULD go, because an `add` cites them;
# a place no verdict can name has no reason to exist unfilled.
#
# !! IT IS A FENCE, AND FENCES HAVE NO ADDRESS. Roy, 2026-08-23: *"the `d`
# series doesn't get an address for the same reasons fences in the real world
# don't get addresses. They mark a demarcation boundary and they have the same
# problem as fences -- whose fence is it."* ! Every other place is attached to a
# line of code, and that line is what a reviewer measures a claim against. A
# blank run sits BETWEEN two places and is attached to neither, so the ownership
# question has no answer rather than an unknown one.
#
# ! IT WAS TRIED AND REFUSED THREE TIMES -- `875b0d4` made it a fifth series,
# `b998a60` repaired it as an edge, `c27ea1d` retreated to a symbol. Roy,
# closing it: *"We tried leading getting a place. We tried several different
# ways. The constraints of coding AND editing do not allow it."* Two things stop
# being determinable the moment the slack is addressable: WHERE everything below
# an edit shifted to, and HOW MUCH blank belongs where afterwards -- the second
# being a typographic judgement no rule computes.
#
# !! UNADDRESSED IS NOT UNRECORDED, and that is the whole of the arrangement.
# Roy: *"the system knows hey there was a fence here we should put it back."*
# `Page.leading` keys the fence on the place it FOLLOWS -- `f0 -> d0` -- so what
# is remembered is a fact about a boundary rather than a thing with a location.
# ! Nobody can cite it, nobody can rule on it, and the compositor puts it back
# exactly where it was. ! WHICH IS WHY THE EDGE SHAPE HOLDS: this system never
# chooses an amount of blank, it replays what it read.
LEAD = Series.LEAD.value.letter
#: The four series `cue` emits. **`LEAD` IS NOT ONE OF THEM**, since 2026-08-22.
#:
#: !! IT FAILED THE SUBSTITUTION THE OTHER FOUR SATISFY. Roy: *"it has no
#: anchor, and so by the LSR -- any child class has to be able to answer its
#: parent class's answers as well, correctly -- it breaks that rule."* `places`
#: is `cue -> the line of code it is attached to`; `a0` and every `f` answer
#: `<module>`, every `b` and `c` answer a line, and a `d` answered `""`. That is
#: the absence of an answer, not a different one, so a consumer could not use a
#: `d` where it expected a place.
#:
#: ! AND THE CAUSE IS WHERE IT COMES FROM, which is what makes this a category
#: error rather than a missing field. Every place here exists because `cue`
#: reached a trigger, and the trigger IS the anchor. A `d` exists because the
#: LEXER found blank lines -- so it was never anchored to anything, it was
#: FOUND. It also never entered `reading`, so the compositor could not set from
#: it the way it sets every other place; it is set as an EDGE, from
#: `Page.leading`.
#:
#: ! WHAT PUBLISHING ALREADY SAID: leading is not an object on the page, it is a
#: measurement of the type it accompanies -- "10 on 12". A measurement cannot be
#: anchored; only the thing measured can.
#:
#: ! `LEAD` SURVIVES AS A SYMBOL, on Roy's ruling that the page/symbol map is
#: what shows every line is covered -- see `lexer.Paragraph.symbol`.
# ! DERIVED, NOT LISTED. Every series whose absence can be CITED -- which is
# every series but `d`, and the definition says so by giving `d` no `absent`
# rather than by an exclusion written here.
SERIES = ADDRESSED


#: The FIRST TRIGGER every addresser steps past: the file itself, before any line
#: of code. It is what `a0` and `f0` name, and the one trigger `c` does not emit
#: for -- a module has front matter and a docstring, and no line to sit beside.
MODULE = "<module>"

#: The LAST TRIGGER, past the final line of code. `b` emits for it -- the gap
#: after the last statement is a place prose can go -- and `a`, `c` and `f` skip
#: it today.
#:
#: !! IT IS A TRIGGER AND NOT AN ARITHMETIC RULE. The alternative is `b`
#: emitting N+1 places by definition, which is one line shorter and puts a
#: special rule inside one series. ! `f` will almost certainly want this trigger
#: too -- tail matter, an index or a glossary at the END of a file -- and then
#: two series each carry a different special rule, and a reader has to know why
#: one gets a +1 and the other gets some other treatment.
#:
#: ! So the cost is paid once, here: every series meets EOF and decides, exactly
#: as it does at MODULE, and adding `f`'s tail place later is a row rather than a
#: second arithmetic.
EOF = "<eof>"


def triggers(code: list[int]) -> list[int | str]:
    """What a addresser walks: the MODULE, every line of code, then EOF.

    !! ONE LIST, SO THE FOUR SERIES CANNOT DRIFT APART. Each cue used to be a
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
class Addresser:
    """One series' counter, and every place it emitted.

    !! IT HOLDS BOTH HALVES. A cue and the line of code it is attached to are one
    fact, so they are stated by ONE STEP of `cue` -- not computed here and
    decorated on later, which is what lets an anchor disagree with its address.

    !! A SERIES OWNS ITS OWN RULE ABOUT WHAT IT SKIPS, AND SKIPPING TAKES NO
    NUMBER. Every trigger is offered to every series -- `a` skips what cannot be
    documented, `b` and `c` skip `<module>`, `f` skips everything but the module
    and matter -- and a series that does not emit for a trigger does not advance
    either, so **every series starts at 0**.

    ! A skip that INCREMENTED would burn `b0` and make the first line of code
    `c1`, starting two series at 1 for no reason a reader could derive.

    Attributes:
        series: `a`, `b`, `c` or `f`.
        places: cue -> the LINE OF CODE it is attached to, in emission order.
    """

    series: str
    places: dict[str, str] = field(default_factory=dict)
    #: cue -> WHICH TRIGGER it was emitted at, as an index into `triggers()`:
    #: 0 is the MODULE, 1..N are the lines of code, N+1 is EOF.
    #:
    #: !! `cue` KNOWS THIS AND USED TO THROW IT AWAY, which is the same
    #: mistake the discarded addressers were. `anchor_num` rebuilt it afterwards
    #: with three separate arithmetics -- `n + 1` for a gap, `len(code) + 1` for
    #: the file's foot, `code.index(line) + 1` for the rest -- and each was a
    #: GUESS about which trigger a place had come from.
    #:
    #: ! THE ANCHOR CANNOT ANSWER IT. TWO IDENTICAL LINES OF CODE ARE TWO
    #: TRIGGERS WITH ONE ANCHOR, because lines of code are not unique -- looking
    #: one up returns many candidate places. And a sentinel is shared across
    #: series: `a0` and `f0` both answer `<module>`, the closing gap and `f1`
    #: both answer `<eof>`. Recording the trigger is the only thing that
    #: distinguishes them without inference.
    trigger: dict[str, int] = field(default_factory=dict)
    _step: int = 0

    def emit(self, anchor: str, trigger: int) -> str:
        """Take this trigger's number, record what it is, and return the cue.

        Args:
            anchor: the line of code this place is attached to, or `MODULE`.
            trigger: which trigger this is, indexing `triggers()`.
        """
        got = cue_for(self.series, self._step)
        self.places[got] = anchor
        self.trigger[got] = trigger
        self._step += 1
        return got

    def at(self, step: int) -> str:
        """This series' cue at `step`, or "" if `cue` never emitted one.

        !! THE QUERY THAT REPLACED SIX TABLES. Roy, 2026-08-21: the old fields
        were *"1 object type flattened into a special case with different
        names."* Each held a place keyed its own way -- by the line below a gap,
        by the line beside a `c`, by a declaration's ordinal -- and each was an
        index into this collection. Asking THIS is what the caller wanted.

        ! THE EMPTY ANSWER IS LOAD-BEARING. A page whose reader refused the
        source has emitted nothing, so every position is unfilled; the old
        tables answered "" there by being empty, and this answers it by asking.
        """
        got = cue_for(self.series, step)
        return got if got in self.places else ""


@dataclass
class Cues:
    """Every place in one file, and the line of code each is attached to.

    !! IT ANSWERS BOTH DIRECTIONS, which is why it is one object. `cue`
    assigns them; these read them back -- *which address does this line
    belong to right now*. Roy, 2026-08-19: that second half *"helps the agents
    understand what they are looking at right now in the code -- they need to
    search it anyways."*

    ! Reading back is a LOOKUP, never arithmetic. `above` ITERATES the triggers
    `cue` stepped and returns the cue it EMITTED there; it does not count
    anything. That is the difference between line order driving `cue` and a
    line number computing a number.
    ! It ITERATES rather than SCANS, and the word matters here: scanning is what
    the LEXER does, over characters, looking at what they are. Nothing in this
    module reads a character -- it steps a sequence it was handed.

    !! IT KEEPS ITS ADDRESSERS RATHER THAN FLATTENING THEM. Roy, 2026-08-21:
    *"`_above`, `_beside`, `_declared`, `_front`, `_back`, `_closing` are 1
    object type flattened into a special case with different names."* They were
    six dicts of the same fact -- a place and its anchor -- each keyed
    differently, and every one of them was an index into a `Addresser` `cue`
    had just discarded. The walkers survive now, so an accessor is a QUERY over
    one collection instead of a lookup in a table of its own.

    ! Each of the three fields is documented where it is DECLARED, below. An
    `Attributes:` section here said the same things a second time and drifted from
    both: it described this first field under the name of the second, and said
    `places` flattens "all five" when `SERIES` has four.
    """

    # !! SERIES LETTER -> THE `Addresser` THAT EMITTED IT, holding its places in
    # EMISSION ORDER. `places` flattens all four. ! Keyed by letter because that
    # is what a cue's first character IS -- so a lookup needs no table beside
    # this one, which is the whole reason the walkers survive `cue`.
    addressers: dict[str, Addresser] = field(
        default_factory=lambda: {name: Addresser(name) for name in SERIES}
    )
    # !! WHAT `cue` STEPS THROUGH -- what `triggers()` returned:
    # `[MODULE, *code, EOF]`. Every position a place reports indexes THIS, so
    # holding it is what makes those positions mean something without arithmetic.
    #
    # !! AND IT IS THE ONLY LINE FACT A `Cues` HOLDS. Everything else about
    # a place is read off it: a place's line is the line of the trigger it fired
    # at, and the step it reports is an index here. A field holding the lines, or
    # the code without the sentinels, is half of this written twice -- two facts
    # where there is one, and the copy is what drifts.
    triggers: list[int | str] = field(default_factory=list)
    # !! EVERY PLACE IN READING ORDER, TOP TO BOTTOM, recorded by `cue` that
    # emitted them. It is what a compositor sets from: a page IS its places in
    # sequence, and the sequence is a fact `cue` knows rather than an
    # arithmetic over line numbers -- which shift the moment one paragraph grows.
    #
    # !! WHERE AN `a` FALLS IS THE LANGUAGE'S CALL AND IS SETTLED HERE, ONCE.
    # Rust puts a declaration's documentation ABOVE the declaring line; Python
    # puts it INSIDE the body, which a wrapped signature moves several lines
    # down. `lexer.declarations` states that as the line the doc occupies, and
    # `cue` turns it into a position in this list -- so nothing downstream
    # asks the question again, and no two readers can answer it differently.
    reading: list[str] = field(default_factory=list)
    # ! LEADING IS NOT HERE, and was for one evening. It is `Page.leading` --
    # `cue` never filled it and never read it, because `cue` runs before
    # any prose exists and leading is only where the LEXER found a blank run.
    # Roy, 2026-08-21: *"I kind of expected that to be the pages job."*

    @property
    def places(self) -> dict[str, str]:
        """Every place in the file -> the line of code it is attached to.

        ! DERIVED FROM THE ADDRESSERS, in `SERIES` order. It was a field `cue`
        assigned by flattening the walkers on its last line, which is what made
        every other projection an index into something already discarded.

        !! IT IS A FRESH DICT EACH TIME, so writing into it changes nothing.
        `page.py` used to number the `d` series by assigning here, and numbers
        it with a counter of its own now -- leading is not a place, so nothing
        here makes one. See `SERIES`.
        """
        return {
            cue: anchor
            for name in SERIES
            for cue, anchor in self.addressers[name].places.items()
        }

    def anchor_of(self, cue: str, default: str = "") -> str:
        """The line of code this place is attached to; `default` if no such place.

        !! ONE LOOKUP, NOT A REBUILT DICT. `places` composes the walkers into a
        fresh mapping on every read, so asking it for ONE place inside a loop is
        quadratic -- MEASURED 2026-08-22, a corpus sweep that ran in under three
        minutes did not finish in ten. The two callers that ask per paragraph
        ask here; the ones that want the whole mapping still take `places`.

        ! IT TAKES A DEFAULT because "" is a real anchor: every `d` place has
        one, so absence cannot be spelled the same way as an empty answer.
        """
        walker = self.addressers.get(cue[:1])
        if walker is None:
            return default
        return walker.places.get(cue, default)

    def above(self, line: int) -> str:
        """The `b` whose gap a paragraph inserting at `line` falls into.

        ! The gap above the FIRST code line at or after `line`. Past the last
        one it is the closing gap, which is the place with no line below it --
        the `b` at the ordinal one past every line of code.

        ! IT READS `cue` DIRECTLY. A `b` fires at the trigger BELOW it, so
        the gap above `triggers[i]` is `b` at `i - 1`, and the closing gap is the one
        at the EOF trigger. ! This went through a `_code` PROPERTY for one hour
        on 2026-08-22, which rebuilt the list on every read -- twice here -- in
        the file whose `anchor_of` twenty lines below records fixing exactly that
        quadratic. The property is deleted; `cue` is the list.
        """
        for step, trigger in enumerate(self.triggers):
            if isinstance(trigger, int) and line <= trigger:
                return self.addressers[GAP].at(step - 1)
        return self.addressers[GAP].at(len(self.triggers) - 2)

    def beside(self, line: int) -> str:
        """The `c` on this line of code, or "" if the line holds no code.

        ! ONE ITERATION, and it was two. `.index` iterates the list ONCE; asking
        `line not in self._code` first and then `.index(line)` iterated it TWICE
        to answer one question.
        """
        try:
            return self.addressers[ON].at(self.triggers.index(line) - 1)
        except ValueError:
            # ! A line `cue` never stepped holds no code, which is a real
            # answer -- the sentinels are strings, so no line can match one.
            return ""

    def documents(self, ordinal: int) -> str:
        """The `a` for the nth documentable declaration; 0 is the module."""
        return self.addressers[DECLARED].at(ordinal)

    def anchor_line(self, cue: str) -> int | None:
        """The LINE the anchor of this place sits on. None when it has none.

        !! IT IS THE LINE OF THE TRIGGER THE PLACE FIRED AT, which is one lookup
        and not a table. A `lines` dict held it for an `a` and a `c` alone, and a
        `b` fell through to `gap_bounds` -- two mechanisms answering one
        question, and neither of them a fact `cue` did not already carry.

        !! A SENTINEL HAS NO LINE, AND `None` IS HOW THIS SAYS SO. It answered 0
        for both until 2026-08-22, and Roy named the asymmetry that hid in it:
        *"`<module>` gets somewhat attached to line 0 by accident and because it
        is functional, but the end of file getting a 0 is non-functional filling
        in for a missing value. They either both get None, or they get 0 and
        -1."*

        ! ZERO WAS A POSITION FOR THE HEAD AND A NULL FOR THE FOOT. Line 0 is
        genuinely above line 1, so it sorted first and rendered at the head and
        both were right; the foot inherited those two behaviours and both were
        wrong. One number doing two jobs is what this repo's own `repo.py` warns
        against: *"a caller that reads a non-answer as an empty answer produces
        the failure this whole skill exists to catch."*

        ! MEASURED before choosing between `None` and `0`/`-1`: both branching
        consumers already handle `None` and neither handles `-1`.
        `render_page` tests `if anchored:` -- `-1` is TRUTHY and would draw the
        foot at line -1 -- and `for_anchor` filters on `isinstance(..., int)`,
        which `-1` passes and then wins a `min`. ! `-1` also already means *the
        last line* in Python, which is the borrowed anchor this branch removed.

        ! IT IS NOT WHAT ORDERS A RECORD -- see `anchor_num`. This remains
        because a consumer READING A FILE needs a line to slice it, which is a
        different job from naming or ordering a place.
        """
        if not self.triggers:
            return None
        trigger = self.triggers[self.anchor_num(cue)]
        return trigger if isinstance(trigger, int) else None

    def anchor_num(self, cue: str) -> int:
        """WHICH TRIGGER this place was emitted at, indexing `triggers()`.

        !! A LINE MOVES AND AN ORDINAL DOES NOT, which is the whole reason this
        exists. Roy, 2026-08-21: *"where it is in the original and where it ends
        up on the resulting page can be two very different things -- but a single
        shift on anchor_num and you know it is all trash after rereading."* This
        tool edits prose, and every prose edit moves the line numbers of the code
        below it; the Nth line of code is still the Nth line of code.

        !! IT REPLACES `anchor_line` AS THE ORDER, and the two rank identically:
        lines of code ascend, so their ordinals do. MEASURED 2026-08-21 --
        `anchor_line` had exactly two consumers, `record.py`'s sort key and
        `for_anchor`'s identity lookup, and NEITHER did arithmetic on the line.

        ! CARRIED ALONGSIDE THE ANCHOR, never instead of it. Roy: *"anchor_num
        along with anchor."* An ordinal alone cannot see a rename in place --
        `def f():` becoming `def RENAMED():` shifts nothing -- and the anchor
        text alone cannot cheaply see an insertion. The pair sees both.

        !! IT IS READ FROM `cue`, NOT RECONSTRUCTED. Reconstructing it hardens
        the very mistake it looks like a fix for, because it assumes `cue`
        emitted every anchor. THREE ARITHMETICS ARE GONE:

            b_n         -> n + 1
            f_n         -> 0, or len(code) + 1
            everything  -> code.index(anchor_line) + 1

        ! EACH WAS A GUESS ABOUT WHICH TRIGGER A PLACE CAME FROM, and the anchor
        cannot settle it: two identical lines of code are two triggers with one
        anchor, and a sentinel is shared across series -- `a0` and `f0` both
        answer `<module>`, the closing gap and `f1` both answer `<eof>`.
        `Addresser.emit` records the trigger, so this is a lookup.

        ! THE VALUES ARE UNCHANGED, and that is checkable: 0 for the MODULE,
        1..N for the lines of code, N+1 for EOF, which is what the three
        expressions computed. What changed is that a place now SAYS where it
        came from instead of being asked to prove it afterwards.

        ! 0 IS THE MODULE, which is a real position and not a miss -- the first
        trigger every addresser steps past. `a0` and `f0` answer it because a
        licence header and a module docstring sit above everything the file
        declares.
        """
        walker = self.addressers.get(cue[:1])
        if walker is None:
            return 0
        return walker.trigger.get(cue, 0)

    def gap_bounds(self, cue: str) -> tuple[int, int]:
        """The two lines of CODE around this gap; 0 for the file's own edge.

        !! COMPUTED, NOT STORED. Held as its own dict it is a second object
        inside `Cues`, written at four points and read at two, with nothing
        holding the two in step.

        !! IT IS THE TRIGGER BEFORE THIS GAP AND THE ONE IT FIRED AT, read off
        `cue`. A gap is emitted at the trigger BELOW it -- `b_n` fires with
        `c_n` -- so the pair either side of it is `triggers[at - 1]` and `triggers[at]`,
        and a sentinel on either end answers 0 because the file's own edge is
        not a line of code.

        ! WHICH IS WHY THE CLOSING GAP STILL BOUNDS CORRECTLY while being
        anchored to `EOF`: it fires at the EOF trigger, so its pair is the last
        line of code above it and nothing below. Placement never read an anchor.

        ! A SERIES THAT IS NOT A GAP ANSWERS `(0, 0)`, which is what the `f`
        places were given explicitly before. A file's own matter is bounded by
        the head or the foot of the file, not by code.
        """
        if not cue.startswith(GAP):
            return (0, 0)
        at = self.anchor_num(cue)
        if not 0 < at < len(self.triggers):
            return (0, 0)
        previous, following = self.triggers[at - 1], self.triggers[at]
        return (
            previous if isinstance(previous, int) else 0,
            following if isinstance(following, int) else 0,
        )

    def file_places(self) -> list[str]:
        """Every `f` `cue` emitted, in the order it emitted them.

        !! WHICH ONE A MATTER RUN TAKES IS A COUNT, and the PAGE does the
        counting. `cue` knows only that a file has places for its own prose and
        where they fall in the reading order; it never looks at prose to decide
        which.
        """
        return list(self.addressers[COVERS].places)


def cue(
    code: dict[int, str],
    documentable: dict[int, tuple[int, int, str]],
    module_insert: int | None = 1,
) -> Cues:
    """Walk the anchors of one file; return every cue and its line of code.

    !! `cue` IS WHAT MAKES EVERY PLACE EXIST. A place is emitted because
    `cue` reached its trigger, not because prose was found sitting there -- which
    is why the file's own matter and the first gap can now both exist. Before
    this, the matter's place came from a BRANCH that fired only when front-matter
    prose had already been stamped, so the two were mutually exclusive: measured
    over five file shapes, the gap above the first line of code was `b1` on a
    file with no licence header and `b0` on a file with one, and adding a module
    docstring renamed it mid-run. ! They are `f0` and `b0` now, in two series.

    ! The four rules differ, and each is measured rather than chosen:

        a   the MODULE, then every documentable declaration. It does not step
            past a line it cannot emit for, so `a1` is the first declaration
            however much code precedes it.
        b   the MODULE, then the gap above every line of code, then the gap
            after the last one.
        c   every line of code. It steps past the module without emitting,
            because a module has no line to sit beside.
        f   the MODULE and the EOF sentinel, and nothing in between. It is
            the file's own matter at either end, so it emits exactly twice on
            every file and steps past every line of code without emitting.

    ! Line ORDER drives `cue`; no line NUMBER is arithmetic here. Nothing
    reads one cue to compute another, and no cue follows from a line's
    ordinal -- see `cue`.

    Args:
        code: `line number -> the exact characters on it`, ascending -- what
            `page.code_lines` returns. The number POSITIONS the trigger; it
            never numbers it, so `cue` reads this in order and counts.
        documentable: index into `code` -> `(the LINE the doc occupies, the code
            index it is set at, WHICH SIDE of that index's gap)` -- what
            `page.documentable` returns, and the body below unpacks all three.
            ! IT WAS ANNOTATED `dict[int, int]` AND DOCUMENTED AS ONE LINE
            NUMBER, which is the shape this had before the three facts were
            split apart 2026-08-21. Honouring either crashed: `{0: 2}` raises
            `cannot unpack non-iterable int object`.
        module_insert: where the MODULE's own doc would go, or None when the
            language has no documentable declaration at all -- then there is no
            `a` series, not an empty one.

    Returns:
        The `Cues`: every place, and both directions between them.
    """
    # ! ONE PER SERIES, AND THEY BELONG TO THE `Cues`. The names below are
    # for `cue`, which is genuinely per-series -- each emits at different
    # triggers -- but nothing downstream has to know how many there are.
    #
    # !! THEY USED TO BE LOCAL AND WERE FLATTENED AWAY at the end of this
    # function, which left every accessor on `Cues` rebuilding an index
    # into a collection that no longer existed. They belong to it now, so
    # `cue` fills the object it returns rather than a set of side tables.
    # ! THE `Cues` KEEPS THE ADDRESSERS IT MADE, so every position a place reports
    # indexes something the object still holds.
    out = Cues(triggers=triggers(list(code)))
    a, b, c, f = (out.addressers[s] for s in (DECLARED, GAP, ON, COVERS))
    # !! NO `a` SERIES AT ALL WHEN THE LANGUAGE HAS NO DOCUMENTABLE
    # DECLARATION. A language with no docstring practice -- YAML, TOML -- would
    # otherwise be given an `a0`, a place for a module docstring it cannot have,
    # and no verdict could ever fill it. `None` says the series does not exist;
    # `1` says it does and the module's own doc would open the file.
    # !! `cue` READS `triggers()`, WHICH IS THE WHOLE POINT OF THERE BEING ONE.
    # A loop written out by hand beside it makes the list that claims *"ONE LIST,
    # SO THE FOUR SERIES CANNOT DRIFT APART"* a list no series walks.
    #
    # ! Each series decides at each trigger, and that rule is now complete --
    # there is no step a place comes from except one of these.
    seen = 0
    # ! Which `a` places are set at which step, filed by `page.documentable` and
    # released in the loop below. For an above-doc language every entry is filed
    # against the declaration's own step; Python's are filed later.
    release: dict[tuple[int, str], list[str]] = {}
    # !! EVERY EMIT NAMES THE TRIGGER IT FIRED AT, and `at` is that position --
    # 0 the MODULE, 1..N the lines of code, N+1 the EOF. `cue` knew it and
    # threw it away until 2026-08-22, leaving `anchor_num` to guess afterwards.
    # ! It cannot be recovered from the anchor: two identical lines of code are
    # two triggers with one anchor, and both sentinels are shared -- `a0` with
    # `f0` at the head, the closing gap with `f1` at the foot.
    # ! ITS OWN LIST, not a second call. `out.triggers` IS what
    # `triggers()` returned above, and building it twice is the drift the
    # function's own docstring forbids -- *"ONE LIST, SO THE FOUR SERIES CANNOT
    # DRIFT APART."* Two calls agree today and are two things that can stop
    # agreeing, which is the whole reason the list exists.
    for at, trigger in enumerate(out.triggers):
        # ! A SENTINEL IS A STRING AND A LINE IS AN INT. Neither sentinel is a
        # line, which is what makes them sentinels.
        if isinstance(trigger, str):
            if trigger == MODULE:
                # ! `f0` is the FILE'S OWN matter, bounded by nothing: the head
                # of the file on both sides. It is not the gap above the first
                # line of code -- that is `b0`, and conflating them made the two
                # exclusive.
                # ! THE HEAD OF THE PAGE, in the order a reader meets it: the
                # file's own matter, then the module's own documentation.
                out.reading.append(f.emit(MODULE, at))
                # ! ONE TEST OF ONE CONDITION. The emit was bound above and then
                # tested for truth here, which is the same question asked twice
                # -- `emit` returns `a0` at the least, so it is never falsy when
                # the language has an `a` series.
                if module_insert is not None:
                    out.reading.append(a.emit(MODULE, at))
                # !! `b` AND `c` SKIP THE MODULE ENTIRELY -- no place, and no
                # number. It has no gap above it and no line to sit beside. Roy,
                # 2026-08-20: *"let's initiate all of them at 0 ... bs and cs
                # will stay aligned until there is some specific reason to split
                # them."*
            else:
                # !! A PLACE'S ANCHOR IS THE TRIGGER IT WAS EMITTED AT. One rule,
                # no series exempt: `MODULE` at the head, the line of code in
                # between, `EOF` at the foot.
                #
                # !! THE CLOSING GAP RECORDS EOF, NOT THE LAST LINE OF
                # CODE. EOF is a trigger so that a place emitted here is a ROW at
                # it, like every other place. Reaching back to the previous
                # trigger for an anchor reinstates, one level down, exactly the
                # special case that making EOF a trigger removes.
                #
                # ! Roy, 2026-08-22: *"the last `b` triggers on EOF and records
                # either `<eof>` or `<module>`, and its anchor and where it is
                # placed becomes a determined fact by the compositor."* WHERE it
                # sets is not `cue`'s business, and `gap_bounds` already
                # answers it from the ordinal without reading an anchor at all.
                closing = b.emit(EOF, at)
                # !! `f` EMITS ITS SECOND PLACE HERE, and this is the reason the
                # EOF trigger is a trigger rather than an N+1 rule. A file's
                # matter sits at BOTH ends and neither end belongs to a gap:
                # `f0` is bounded by the head of the file on both sides, `f1` by
                # the foot. ! Bounded by nothing, exactly as `f0` is -- a licence
                # at the foot is the FILE's, not the last gap's, which is where
                # it landed while this place did not exist.
                # ! THE FOOT OF THE PAGE: the gap after the last statement, then
                # the file's own matter, which is bounded by nothing.
                # ! A doc with no code after it is filed against the step past
                # the last one, which is this gap.
                out.reading.extend(release.pop((len(code), GAP), ()))
                out.reading.append(closing)
                # ! `EOF` FOR THE SAME REASON THE GAP TAKES IT: the anchor names
                # the trigger. `f0` answers `<module>` because that is where it
                # was emitted, not because the file's matter belongs to the
                # module -- and the foot answers `<eof>` on the same rule.
                out.reading.append(f.emit(EOF, at))
            continue
        n = trigger
        line = code[n]
        if seen in documentable:
            # ! 0 is the module, so a declaration's ordinal is its position
            # among the documentable ones, counting from 1.
            declared = a.emit(line, at)
            # !! TWO FACTS, AND `cue` USES ONLY THE SECOND. `page.documentable`
            # states the LINE the doc occupies and the code ordinal it is SET
            # BEFORE, which is the language's rule already resolved. `cue`
            # holds the place until that step and compares nothing.
            _insert_at, at_step, side = documentable[seen]
            release.setdefault((at_step, side), []).append(declared)
        gap = b.emit(line, at)
        beside = c.emit(line, at)
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
        # wrapped one spans. ! No line is compared, which is what keeps `cue`
        # free of arithmetic it would otherwise have to keep right.
        out.reading.extend(release.pop((seen, GAP), ()))
        out.reading.append(gap)
        out.reading.extend(release.pop((seen, ON), ()))
        out.reading.append(beside)
        seen += 1
    # !! NOTHING IS COLLECTED AT THE END ANY MORE. This function closed by
    # flattening the walkers into `out.places` and dropping them, so a
    # place existed twice -- once in the walker that emitted it and once in the
    # flat dict -- and every accessor had to be given its own table because the
    # emitter was gone. `Cues.places` reads the walkers instead.
    return out


def cue_for(series: str, step: int) -> str:
    """The cue at one step of a series -- ONE expression, all four series.

    ! NAMED FOR ITS DIRECTION, so it cannot collide with `cue()` again: this
    BUILDS a cue from its parts, and `cue_of` takes one apart.

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
    design, eighteen languages in one run. Roy ruled it 2026-08-18: "we could have
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


def address_for(path: str, cue: str) -> str:
    """`pkg:mod.py@a5` -- the two halves of an address, put together.

    !! THE ONLY PLACE THEY ARE JOINED, and it lives here because this module
    already owns both halves and the whole take-apart: `flatten` makes the path
    half, `emit` makes the cue, `cue_of` splits one back, and `unflatten` recovers
    the real path. The join was the one direction that had leaked.

    ! IT LEAKED TO TWO MODULES, and `record.address_for` -- which this is --
    carried the claim *"the only place the two halves are put back together"*
    while `page.py` composed its own with an f-string at two sites. Ruled by Roy,
    2026-08-23: *"Something else owns addressing -- the Addresser."*

    ! BOTH HALVES OR NOTHING. An address missing either half resolves nowhere,
    so a blank is returned rather than `pkg:mod.py@` or `@a5`, both of which read
    as an address and are not one.

    Args:
        path: the page, as the repo sees it. Flattened here, so a caller never
            has to know whether it already was.
        cue: the `@` half, as `emit` returned it.

    Returns:
        The address, or `""` when either half is missing.
    """
    return f"{flatten(path)}@{cue}" if path and cue else ""


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
        name: the flattened path from an address, without the `@cue`.
        paths: the paths the census carries.

    Returns:
        The one path whose flattened form is `name`, or "" when none or several
        do.
    """
    hits = {p for p in paths if flatten(p) == name}
    return hits.pop() if len(hits) == 1 else ""


class Address(NamedTuple):
    """An address in its two halves, so a caller names the one it wants.

    !! IT WAS A BARE TUPLE AND EVERY CALLER SUBSCRIPTED `[1]` -- fifteen of them
    after `galley`'s second `cue_of` was consolidated onto this one. Roy,
    2026-08-22, reading that diff: *"interesting sentinel as a number."* The `1`
    means *the cue* and nothing in it says so; a reader has to know the
    tuple's order to know what was asked for.

    ! IT IS THE `0`-FOR-A-MISSING-LINE DEFECT ONE FIELD OVER, and I wrote fifteen
    of them an hour after recording that one -- a bare number carrying a meaning
    the number does not hold.

    ! ADDITIVE, NOT A MIGRATION. A `NamedTuple` unpacks and subscripts exactly
    as the tuple did, so nothing that already worked had to change; the sites
    that read better by name were changed and the rest are free to follow.
    """

    path: str
    cue: str

    @property
    def series(self) -> str:
        """Which series this address is in -- `a`, `b`, `c` or `f`.

        !! IT IS A NAMED READER FOR THE SAME REASON THIS IS A `NamedTuple`.
        Callers wrote `.cue[:1]`, which is a slice carrying a meaning the slice
        does not hold -- the defect recorded above, one field down. Roy,
        2026-08-24: *"cue.series is the Right answer."*

        !! IT RAISES ON A STRING THAT NAMES NO PLACE, and that is deliberate.
        It was `self.cue[:1]` for one commit, which answered `""` -- and the
        only thing that ever reached it blank was LEADING. Roy, 2026-08-24:
        *"Series d are walked because they have to be but they are not cues."*
        A `d` is walked because the compositor has to set those lines back, and
        it names no place; asking it which series it is in is a category error,
        not a case to absorb.

        ! THE BLANK WAS THE MACHINERY THAT LET IT PRETEND. Two sites sent a `d`
        through here and read the empty answer as their signal to go ask
        `symbol` instead -- a round trip that bought nothing, since both already
        knew. `galley.py` and `page.py` never did: they test `b.address` and
        branch, which is the idiom this now requires of everyone.

        Raises:
            IndexError: when the address names no place. The caller asked a
                question about a cue of something that is not one.
        """
        return self.cue[0]


def cue_of(address: str) -> Address:
    """An address split into its flattened path and its cue, or two blanks."""
    path, sep, where = address.rpartition("@")
    return Address(path, where) if sep else Address("", "")
