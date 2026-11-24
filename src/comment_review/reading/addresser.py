"""The addresser: numbering the places on a page, and reading the number back.

    python comment-review.py addresses find --file m.py --line 12 --series a

Four addressers -- each an `Addresser` -- walk one trigger list, `triggers`: the
`MODULE`, every line of code, then `EOF`. Each holds its own counter and the
places it emitted. `cue()` walks the list and returns a `Cues`, which answers
back which address a line belongs to right now.

!! Both halves of an address are made here, and joined in one place. `flatten`
makes the path half, `emit` makes the cue, `address_for` is the only site that
puts them together, `cue_of` splits one back into an `Address` and `unflatten`
recovers the real path.

`folded` trims and case-folds an address, or either half, so two spellings of
one place compare equal; nothing stores the folded form.

`ON`, `GAP`, `DECLARED`, `COVERS` and `LEAD` are the series letters, read from
`reading.series`; `SERIES` is the four `cue` emits, and `SEPARATOR` the character
`flatten` joins a path with.

!! It addresses every place and every potential place. The empty places are what
an `add` cites, so giving them addresses is what makes `add` expressible at all.

!! An address is not a span of lines. No line has more than one, and a
paragraph is just the lines that share one. ! Read it as a range and every
question a line-numbered address had comes back: which lines a paragraph
"covers", whether two overlap, how wide to make the range. This tool edits
prose, and a prose edit moves the line numbers of everything below it -- so a
page is taken apart into places and set back from the places alone, consulting
no line number anywhere.

! An anchor is the exception that proves it. A declaration carries prose at
several addresses -- the `b` above it, the `c` beside it, its own `a`, the `b`s
in its body -- so an anchor has many addresses. A line still has one.

! The `d` series takes no address at all -- see `LEAD` for why, and `SERIES`
for what it takes instead.

!! This rests entirely on the binder being a hashed static table -- exact,
constant, fully enumerated. Take away any one of those and the scheme collapses
without saying so:

  fully enumerated  a code line missed anywhere above a place shifts its name.
                    Every addresser steps past every line of code, so a partial
                    enumeration does not fail -- it renames every place below
                    the hole, silently and consistently
  constant          the same file must count the same way twice, or two runs
                    cannot be compared, which is the whole point
  exact             a heuristic that is usually right is a table that is
                    occasionally renumbered

! What makes it constant across this tool's own work is stage 7b's code check:
the reader's record compares the code of two reads of a file, so the Nth code
line is still the same statement -- which is exactly what an ordinal counts. The
line numbers move with the prose; the ordinal does not.

!! And it proves nothing at all on an unprovable file, which is the hard
exception this scheme rests on and must name. `prove_unchanged` returns
`UNPROVABLE` for a file with no copy at the base ref -- a new file or a bad
ref -- and for two reads whose reader cannot separate prose from code. Such
a run is reported and counted a failure rather than passed -- so there is no
stage 8 to hand an address to, and the guarantee above is never claimed for a
file it does not cover.

! The numbering is invariant by construction rather than by luck -- but only
while the enumeration underneath it is complete.

Four series, because prose answers to one of exactly four subjects:

    package:core.py@a5    the 5th declaration's documentation
    package:core.py@c3    beside a line of code
    package:core.py@b3    a gap between two lines of code
    package:core.py@f0    the file's own matter, at either end

!! `a` is separate for a different reason: it names a subject, not a position.
A docstring is about its declaration, and `a0` is the module with `a1..aN` its
declarations in source order. The direction question disappears here: Python's
docstring after its `def` and Rust's `///` before its `fn` number alike, because
the number counts declarations rather than positions.

!! So no positioning rule is stated in this module. A language's reader says
where its documentation sits and which declaration a doc belongs to, because
that is language-dependent and a reader knows it while a position does not.
`DocPlace` carries what it states.

!! The `a` number counts declarations, not code lines. Numbered by the `c` of
its own `def` line, all three series would share one count and `a5` would mean
nothing until it was resolved against another series; counted by declaration,
`a5` read directly is "the 5th definition in this file".

!! The same place is the same address whether prose fills it or not, which is
the property line numbers cannot give. A comment paragraph occupying three
lines and an empty interval in the same position are both `b0`; a documented
and an undocumented declaration are both `a5`. So a finding can say where prose
belongs in a file that does not have it yet, and two versions of a file compare
place by place.

!! An address is a single fact, and the `a` series is what makes it one.
With `a` a docstring is named for its declaration and leaves the `b`
series, so it never shares a gap's address with the comment run beneath it.

! So an address alone identifies a place, and a record needs nothing beside it.

!! One naming lives here, and the module is named for owning it.
"""

from dataclasses import dataclass, field
from functools import cached_property
from typing import NamedTuple

from comment_review.reading.series import ADDRESSED, Series, cue_for
from comment_review.reading.source import CodeLine

# !! THE LETTERS COME FROM THE SERIES DEFINITION, the one source of a series'
# letter and its two kinds.
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
# A series of two places is still a series, so `b` owning every line that is not
# another series' lines needs no clause about which `b` is not really a `b`.
#
# It is counted rather than hardcoded to one place, because a file's matter sits
# at both ends: `cue` emits `f0` at the module and `f1` at EOF.
COVERS = Series.COVERS.value.letter

# !! The space between two paragraphs -- see `Kind.LEADING` for what it is and
# why.
#
# ! `l` was the obvious choice and the worst possible character: `m.py@l0` reads
# as `@10`, and this whole scheme rests on a cue being unmistakable.
#
# !! It is the one series nothing cites: a `d` holds nothing to rule on and is
# there to preserve the document. So a `d` is kept out of the binder and out
# of edit-copy seeding, and no empty `d` is emitted -- the other four series
# exist wherever prose could go, because an `add` cites them; a place no
# instruction can name has no reason to exist unfilled.
#
# !! It is a fence, and fences have no address. ! Every other place is attached
# to a line of code, and that line is what a reviewer measures a claim against.
# A blank run sits between two places and is attached to neither, so the
# ownership question has no answer rather than an unknown one.
#
# !! Unaddressed is not unrecorded, and that is the whole of the arrangement:
# the system knows a fence stood here and puts it back. `Page.leading` keys the
# fence on the place it follows -- `f0 -> d0` -- so what is remembered is a fact
# about a boundary rather than a thing with a location. ! Nobody can cite it,
# nobody can rule on it, and the compositor puts it back exactly where it was.
# ! Which is why the edge shape holds: this system never chooses an amount of
# blank, it replays what it read.
LEAD = Series.LEAD.value.letter
#: The four series `cue` emits. **`LEAD` is not one of them**.
#:
#: !! It fails the substitution the other four satisfy: a `d` has no anchor,
#: and a child class must answer its parent class's questions correctly.
#: `places` is `cue -> the code it is attached to`; `a0` and `f0` answer
#: `<module>`, the closing `b` and `f1` answer `<eof>`, every other `b` and every
#: `c` answer a line, and a `d` would answer `""`. That is the absence of an
#: answer, not a different one, so a consumer could not use a `d` where it
#: expected a place.
#:
#: ! And the cause is where it comes from, which is what makes this a category
#: error rather than a missing field. Every place here exists because `cue`
#: reached a trigger, and the trigger is the anchor. A `d` exists because the
#: page found blank lines -- so it is never anchored to anything, it is
#: found. It also never enters `reading`, so the compositor cannot set from
#: it the way it sets every other place; it is set as an edge, from
#: `Page.leading`.
#:
#: ! What publishing already says: leading is not an object on the page, it is
#: a measurement of the type it accompanies -- "10 on 12". A measurement cannot
#: be anchored; only the thing measured can.
#:
#: ! `LEAD` survives as a symbol, because the page/symbol map is what shows
#: every line is covered -- see `Paragraph.symbol`.
# ! Derived, not listed. Every series whose absence can be cited -- which is
# every series but `d`, and the definition says so by giving `d` no `absent`
# rather than by an exclusion written here.
SERIES = ADDRESSED


#: The FIRST TRIGGER every addresser steps past: the file itself, before any line
#: of code. It is what `a0` and `f0` name, and a trigger neither `b` nor `c` emits
#: for -- a module has front matter and a docstring, and no line to sit beside.
MODULE = "<module>"

#: The LAST TRIGGER, past the final line of code. `b` emits for it -- the gap
#: after the last statement is a place prose can go -- and so does `f`, for the
#: file's own matter at the foot. `a` and `c` skip it.
#:
#: !! IT IS A TRIGGER AND NOT AN ARITHMETIC RULE. `b` emitting N+1 places by
#: definition would put a special rule inside one series, and `f` would need
#: another. So every series meets EOF and decides, exactly as it does at MODULE.
EOF = "<eof>"


def triggers(code: list[int]) -> list[int | str]:
    """What an addresser walks: the MODULE, every line of code, then EOF.

    !! One list for all four series, so a step means the same trigger in every
    series and no series can count its steps by a rule of its own.

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

    !! It holds both halves. A cue and the code it is attached to are one
    fact, so they are stated by one step of `cue` -- not computed here and
    decorated on later, which is what lets an anchor disagree with its address.

    !! A series owns its own rule about what it skips, and skipping takes no
    number. Every trigger is offered to every series -- `a` skips what cannot be
    documented and `EOF`, `b` skips `<module>`, `c` skips both sentinels, `f`
    skips every line of code -- and a series that does not emit for a trigger
    does not advance either, so **every series starts at 0**.

    ! A skip that incremented would burn `b0` and make the first line of code
    `c1`, starting two series at 1 for no reason a reader could derive.

    Attributes:
        series: `a`, `b`, `c` or `f`.
        places: cue -> the line of code it is attached to, or the sentinel it
            fired at, in emission order.
    """

    series: str
    places: dict[str, str] = field(default_factory=dict)
    #: cue -> WHICH TRIGGER it was emitted at, as an index into `triggers()`:
    #: 0 is the MODULE, 1..N are the lines of code, N+1 is EOF.
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
        """Take this series' next number, record what it is, and return the cue.

        Args:
            anchor: the line of code this place is attached to, or a sentinel.
            trigger: which trigger this is, indexing `triggers()`.
        """
        got = cue_for(self.series, self._step)
        self.places[got] = anchor
        self.trigger[got] = trigger
        self._step += 1
        return got

    def at(self, step: int) -> str:
        """This series' cue at `step`, or "" if `cue` never emitted one.

        ! The empty answer is load-bearing. A page whose reader refused the
        source has emitted nothing, so every position is unfilled, and this
        answers it by asking.
        """
        got = cue_for(self.series, step)
        return got if got in self.places else ""


@dataclass
class Cues:
    """Every place in one file, and the code each is attached to.

    !! IT ANSWERS BOTH DIRECTIONS, which is why it is one object. `cue`
    assigns them; these read them back -- *which address does this line
    belong to right now*.

    ! Reading back is a lookup, never arithmetic. `above` iterates the triggers
    `cue` stepped and returns the cue it emitted there; it does not count
    anything. That is the difference between line order driving `cue` and a
    line number computing a number.
    ! It iterates rather than scans, and the word matters here: scanning is what
    a reader does, over characters, looking at what they are. Nothing in `Cues`
    reads a character -- it steps a sequence it was handed.

    ! Each of the three fields is documented where it is DECLARED, below.
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
    reading: list[str] = field(default_factory=list)

    @property
    def places(self) -> dict[str, str]:
        """Every place in the file -> its line of code, or a sentinel.

        ! DERIVED FROM THE ADDRESSERS, in `SERIES` order.

        !! It is a fresh dict each time, so writing into it changes nothing.
        """
        return {
            cue: anchor
            for name in SERIES
            for cue, anchor in self.addressers[name].places.items()
        }

    def anchor_of(self, cue: str, default: str = "") -> str:
        """This place's line of code, or sentinel; else `default`.

        !! One lookup, not a rebuilt dict. `places` composes the walkers into a fresh
        mapping on every read, so asking it for one place inside a loop is quadratic.
        The six callers that ask for one place ask here; the ones that want the whole
        mapping still take `places`.

        It takes a default so a caller can keep the anchor it already holds when
        the cue names no place: `binder/page.py` passes the paragraph's own.
        """
        walker = self.addressers.get(cue[:1])
        if walker is None:
            return default
        return walker.places.get(cue, default)

    def above(self, line: int) -> str:
        """The `b` whose gap a paragraph inserting at `line` falls into.

        ! The gap above the FIRST code line at or after `line`. Past the last
        one it is the closing gap, which is the place with no line below it --
        the `b` fired at the EOF trigger.
        """
        gaps = self._gaps
        for step, trigger in enumerate(self.triggers):
            if isinstance(trigger, int) and line <= trigger:
                return gaps.get(step, "")
        return gaps.get(len(self.triggers) - 1, "")

    @cached_property
    def _gaps(self) -> dict[int, str]:
        """Each trigger a `b` fired at -> that `b`.

        Built on first use. `cue` emits every place before it returns the
        `Cues`, and nothing emits one after.
        """
        return {step: c for c, step in self.addressers[GAP].trigger.items()}

    def beside(self, line: int) -> str:
        """The `c` on this line of code, or "" if the line holds no code."""
        try:
            return self.addressers[ON].at(self.triggers.index(line) - 1)
        except ValueError:
            # ! A line `cue` never stepped holds no code, which is a real
            # answer -- the sentinels are strings, so no line can match one.
            return ""

    def documents(self, line: int | None) -> str:
        """The `a` documenting the declaration on this code line.

        None is the module, whose documentation is `a0`. "" when the line
        declares nothing documentable.
        """
        if line is None:
            return self.addressers[DECLARED].at(0)
        return self._declared.get(line, "")

    @cached_property
    def _declared(self) -> dict[int, str]:
        """Each declaring line -> its `a`, built as `_gaps` is."""
        return {
            line: c
            for c, step in self.addressers[DECLARED].trigger.items()
            if isinstance(line := self.triggers[step], int)
        }

    def at_line(self, line: int | str, series: str) -> list[str]:
        """The places of one series that a line number or a sentinel names.

        !! A line number is how a role asks; an address is how it answers. The
        binder a role reads is filtered to the places holding prose, so the
        place an `add` wants is exactly the one it cannot find there; this
        answers from the file `cue` walked.

        ! Each series is a different question of the same line, and each is a
        lookup this object already answers -- `above`, `beside`, `documents`,
        `file_places` -- never a count.

            b   the gap a paragraph inserting at `line` falls into
            c   the room beside `line`, if it holds code
            a   the documentation of a declaration on `line`
            f   both of the file's own places -- no line tells the head from
                the foot, so the caller chooses by address

        A sentinel, `MODULE` or `EOF`, names the places the series emitted at
        that trigger: `a0` and `f0` at `MODULE`; the closing `b` and the last
        `f` at `EOF`. No line number reaches those.

        Returns:
            The cues, in emission order. Empty when the series has no place at
            that line -- a `c` on a blank line, an `a` on a line that declares
            nothing, a `c` at a sentinel -- which a caller reports rather than
            treating as a place.
        """
        if isinstance(line, str):
            walker = self.addressers[series]
            return [
                c for c, step in walker.trigger.items() if self.triggers[step] == line
            ]
        if series == GAP:
            return [self.above(line)]
        if series == ON:
            return [c for c in (self.beside(line),) if c]
        if series == DECLARED:
            return [c for c in (self.documents(line),) if c]
        if series == COVERS:
            return self.file_places()
        return []

    def anchor_line(self, cue: str) -> int | None:
        """The line this place's anchor opens on. None when it has none.

        !! It is the line of the trigger the place fired at, which is one lookup
        and not a table.

        !! A sentinel has no line, and `None` is how this says so, for both
        sentinels. Line 0 is genuinely above line 1, so it would sort first and
        render at the head, which is right for the head; at the foot it would be
        a null standing in for a position.

        ! Not `0` and `-1` either: both branching consumers handle `None` and
        neither handles `-1`. `scripts/render_page.py` tests `if anchored:` --
        `-1` is truthy and would draw the foot at line -1 -- and `binder/page.py`
        tests a `c`'s line `is None`, which `-1` passes as a line. ! `-1` also
        already means *the last line* in Python, which is a borrowed anchor.

        A consumer reading a file needs a line to slice it, which is a different
        job from naming a place.
        """
        if not self.triggers:
            return None
        trigger = self.triggers[self.anchor_num(cue)]
        return trigger if isinstance(trigger, int) else None

    def anchor_num(self, cue: str) -> int:
        """Which trigger this place was emitted at, indexing `triggers()`.

        !! A line moves and an ordinal does not, which is the whole reason this
        exists. This tool edits prose, and every prose edit moves the line
        numbers of the code below it; the Nth line of code is still the Nth line
        of code.

        ! Carried alongside the anchor, never instead of it. An ordinal alone
        cannot see a rename in place -- `def f():` becoming `def RENAMED():`
        shifts nothing -- and the anchor text alone cannot cheaply see an
        insertion. The pair sees both.

        !! It is read from `cue`, not reconstructed. Reconstructing it hardens
        the very mistake it looks like a fix for, because it assumes `cue`
        emitted every anchor, as each of these arithmetics does:

            b_n         -> n + 1
            f_n         -> 0, or len(code) + 1
            everything  -> code.index(anchor_line) + 1

        ! The values are the ones those expressions compute, and that is
        checkable: 0 for the `MODULE`, 1..N for the lines of code, N+1 for
        `EOF`.

        0 is the module, which is a real position -- and also what a cue no
        addresser emitted answers, so the two cannot be told apart here. It is
        the first trigger every addresser steps past. `a0` and `f0` answer it
        because a licence header and a module docstring sit above everything the
        file declares.
        """
        walker = self.addressers.get(cue[:1])
        if walker is None:
            return 0
        return walker.trigger.get(cue, 0)

    def gap_bounds(self, cue: str) -> tuple[int, int]:
        """The two lines of code around this gap; 0 for the file's own edge.

        !! Computed, not stored. Held as its own dict it is a second object
        inside `Cues`, written at four points and read at two, with nothing
        holding the two in step.

        !! It is the trigger before this gap and the one it fired at, read off
        `cue`. A gap is emitted at the trigger below it, so the pair either
        side of it is `triggers[at - 1]` and `triggers[at]`, and a sentinel on
        either end answers 0 because the file's own edge is not a line of code.

        ! Which is why the closing gap still bounds correctly while being
        anchored to `EOF`: it fires at the EOF trigger, so its pair is the last
        line of code above it and nothing below. Placement never reads an
        anchor.

        ! A series that is not a gap answers `(0, 0)`. A file's own matter is
        bounded by the head or the foot of the file, not by code.
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


def cue(code: list[CodeLine]) -> Cues:
    """Walk the anchors of one file; return every cue and its code.

    !! `cue` is what makes every place exist. A place is emitted because `cue`
    reached its trigger, not because prose was found sitting there -- which is why
    the file's own matter and the first gap both exist. ! They are `f0` and `b0`,
    in two series.

    ! The four rules differ, and each is measured rather than chosen:

        a   the MODULE, then every documentable declaration. A line it cannot
            emit for takes no number, so `a1` is the first declaration however
            much code precedes it.
        b   the gap above every line of code, then the gap after the last one.
        c   every line of code. The module takes no `c`, because a module has
            no line to sit beside.
        f   the MODULE and the EOF sentinel, and nothing in between. It is
            the file's own matter at either end, so it emits exactly twice on
            every file; no line of code takes an `f`.

    ! Line ORDER drives `cue`; no line NUMBER is arithmetic here.

    !! NOTHING READS ONE CUE TO COMPUTE ANOTHER, and no cue follows from a
    line's ordinal. Whether two series happen to line up on a given file is not
    stated anywhere, deliberately: the edge cases where it breaks are not known,
    and a reader told the numbers coincide will rely on it whatever the sentence
    around it says.

    Args:
        code: every line of code, ascending, as its reader states it. The line
            number POSITIONS the trigger; it never numbers it, so `cue` reads
            this in order and counts. A line whose `documents` is set takes
            the next `a`, and its `DocPlace` says where that `a` is set: above
            the line `at` names, between its gap and its code, or after that
            line's `c`.

    Returns:
        The `Cues`: every place, and both directions between them.

    Raises:
        ValueError: when a `DocPlace` names a line `cue` has already passed,
            which would leave its `a` out of the reading order.
    """
    out = Cues(triggers=triggers([line.line for line in code]))

    # ! ONE PER SERIES, AND THEY BELONG TO THE `Cues`. The names below are
    # for `cue`, which is genuinely per-series -- each emits at different
    # triggers -- but nothing downstream has to know how many there are.
    a, b, c, f = (out.addressers[s] for s in (DECLARED, GAP, ON, COVERS))
    # ! Each code line's step, so a `DocPlace` naming a line is filed against it.
    step_of = {line.line: step for step, line in enumerate(code)}
    seen = 0
    # ! Which `a` places are set at which step and on which side, keyed
    # `(step, above)` from each `DocPlace` and released in the loop below. An
    # above-doc language files an `a` against its declaration's own step;
    # Python files it against the step that ends the signature.
    release: dict[tuple[int, bool], list[str]] = {}
    # Every emit names the trigger it fired at, and `at` is that position --
    # 0 the MODULE, 1..N the lines of code, N+1 the EOF.
    #
    # The loop walks `out.triggers`, the list `triggers()` returned above, not a
    # second call: two calls agree today and are two things that can stop
    # agreeing, which is the drift `triggers` exists to prevent.
    #
    # Each series decides at each trigger, and that rule is now complete --
    # there is no step a place comes from except one of these.
    #
    # !! A place's anchor is the trigger it was emitted at. One rule, no series
    # exempt: `MODULE` at the head, the line of code in between, `EOF` at the foot.
    for at, trigger in enumerate(out.triggers):
        # ! A SENTINEL IS A STRING AND A LINE IS AN INT. Neither sentinel is a
        # line, which is what makes them sentinels.
        if isinstance(trigger, str):
            # !! `b` AND `c` SKIP THE MODULE ENTIRELY -- no place, and no
            # number. It has no gap above it and no line to sit beside.
            if trigger == MODULE:
                # ! `f0` is the FILE'S OWN matter, bounded by nothing: the head
                # of the file on both sides. It is not the gap above the first
                # line of code -- that is `b0`, and conflating them made the two
                # exclusive.
                # ! THE HEAD OF THE PAGE, in the order a reader meets it: the
                # file's own matter, then the module's own documentation.
                out.reading.append(f.emit(MODULE, at))
                out.reading.append(a.emit(MODULE, at))
            else:
                # !! THE CLOSING GAP RECORDS EOF, NOT THE LAST LINE OF
                # CODE. EOF is a trigger so that a place emitted here is a ROW at
                # it, like every other place. Reaching back to the previous
                # trigger for an anchor reinstates, one level down, exactly the
                # special case that making EOF a trigger removes.
                #
                # ! Where the closing gap sets is not `cue`'s business:
                # `gap_bounds` answers that from the ordinal without reading an
                # anchor at all.
                closing = b.emit(EOF, at)
                if release:
                    # !! EVERY FILED `a` IS RELEASED BY NOW, unless its
                    # `DocPlace` named a line before its own declaration --
                    # dropping it would leave a place out of the reading order.
                    raise ValueError(
                        "an `a` filed before its declaration: "
                        + ", ".join(name for held in release.values() for name in held)
                    )
                out.reading.append(closing)
                # !! `f` emits its second place here, and this is the reason the
                # EOF trigger is a trigger rather than an N+1 rule. A file's
                # matter sits at both ends and neither end belongs to a gap:
                # `f0` is bounded by the head of the file on both sides, `f1` by
                # the foot. ! Bounded by nothing, exactly as `f0` is -- a licence
                # at the foot is the file's, not the last gap's.
                # ! The foot of the page: the gap after the last statement, then
                # the file's own matter, which is bounded by nothing.
                # ! `EOF` for the same reason the gap takes it: the anchor names
                # the trigger. `f0` answers `<module>` because that is where it
                # was emitted, not because the file's matter belongs to the
                # module -- and the foot answers `<eof>` on the same rule.
                out.reading.append(f.emit(EOF, at))
            continue
        line = code[seen]
        if line.documents is not None:
            # ! 0 is the module, so a declaration's ordinal is its position
            # among the documentable ones, counting from 1.
            declared = a.emit(line.code, at)
            # !! THE READER STATED WHERE THE DOC IS SET, as a code line and a
            # side. `cue` holds the place until that line's step and compares
            # nothing.
            place = line.documents
            release.setdefault((step_of[place.at], place.above), []).append(declared)
        out.reading.append(b.emit(line.code, at))
        beside = c.emit(line.code, at)
        # !! THE ORDER A READER MEETS THEM: the gap above this line, appended
        # above, then any declaration documented above it, then the
        # line itself with the room beside it, then any declaration documented
        # after it.
        #
        # !! THE SIDE IS THE PER-LANGUAGE QUESTION, AND IT IS NOT ASKED HERE.
        # The reader's `DocPlace` already answered it, so this releases
        # whatever was filed against this step. An above-doc language files a
        # declaration above its own line, so its `a` sits above the code;
        # Python files it after the line that ends the signature, so the
        # docstring lands after the signature -- however many code lines a
        # wrapped one spans. ! No line is compared, which is what keeps `cue`
        # free of arithmetic it would otherwise have to keep right.
        out.reading.extend(release.pop((seen, True), ()))
        out.reading.append(beside)
        out.reading.extend(release.pop((seen, False), ()))
        seen += 1
    return out


#: The character that joins path segments in an address. A path may not hold it
#: -- Windows forbids it outright, and `gather` refuses a POSIX path that
#: does -- which is what makes `flatten` invertible. See `flatten`.
SEPARATOR = ":"


def flatten(path: str) -> str:
    """`pkg/sub/mod.py` as `pkg:sub:mod.py` -- the whole path, extension kept.

    !! The address is the full path from the runner's root, not the file name.
    Files form a tree, so two complete paths differ somewhere, and the
    separator below carries that difference through into the address.

    !! The extension stays. Dropping it reads better and reintroduces collisions
    the moment a repo holds `b.py` beside `b.rs`, and one gather reads both.

    !! The separator is a character a path cannot hold, and that is what makes
    this invertible. A dot is ordinary in a filename -- `app.test.js`,
    `types.d.ts` -- so with `.` as the separator `a/b.py` and `a.b.py` would
    both read `a.b.py`.

    ! `:` is the one Windows forbids that is not shell-special, so an address is
    safe as a bare command-line argument where `<`, `>`, `|`, `?` and `*` are
    not. ! POSIX forbids only `/` and NUL, so a POSIX path can hold a colon and
    this would be ambiguous again -- `gather` refuses such a file rather than
    addressing it.
    """
    return str(path).replace("\\", "/").replace("/", SEPARATOR)


def address_for(path: str, cue: str) -> str:
    """`pkg:mod.py@a5` -- the two halves of an address, put together.

    !! THE ONLY PLACE THEY ARE JOINED, and it lives here because this module
    already owns both halves and the whole take-apart: `flatten` makes the path
    half, `emit` makes the cue, `cue_of` splits one back, and `unflatten` recovers
    the real path.

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
    """The real path a flattened one names, or "" if the binder cannot say.

    ! It resolves against the binder rather than by string surgery, because the
    binder is what knows which paths exist. With `:` as the separator the form
    is invertible, so this answers for exactly one path or none.

    ! Ambiguity is refused rather than resolved by preferring one. `gather`'s
    refusal is what makes it unreachable, and a reader here should not have to
    know that to trust the answer.

    Args:
        name: the flattened path from an address, without the `@cue`.
        paths: the paths the binder carries.

    Returns:
        The one path whose flattened form is `name`, or "" when none or several
        do.
    """
    hits = {p for p in paths if flatten(p) == name}
    return hits.pop() if len(hits) == 1 else ""


class Address(NamedTuple):
    """An address in its two halves, so a caller names the one it wants.

    !! A bare tuple's `[1]` means *the cue* and nothing in it says so; a reader
    has to know the tuple's order to know what was asked for.

    ! A `NamedTuple` unpacks and subscripts exactly as a tuple does, so a caller
    may index it or name the field.
    """

    path: str
    cue: str

    @property
    def series(self) -> str:
        """Which series this address is in -- `a`, `b`, `c` or `f`.

        !! It is a named reader for the same reason this is a `NamedTuple`:
        `.cue[:1]` is a slice carrying a meaning the slice does not say.

        It raises on an address with no cue, and that is deliberate.
        A `d` is walked because the compositor has to set those lines back, and
        it names no place; asking it which series it is in is a category error,
        not a case to absorb.

        Raises:
            IndexError: when the address has no cue. The caller asked a
                question about a cue of something that is not one.
        """
        return self.cue[0]


def cue_of(address: str) -> Address:
    """An address split into its flattened path and its cue, or two blanks."""
    path, sep, where = address.rpartition("@")
    return Address(path, where) if sep else Address("", "")


def folded(address: str) -> str:
    """`address`, or either half of one, trimmed and case-folded.

    Two spellings that fold alike name one place on a checkout whose file
    system ignores case, and a role that retypes an address rather than
    copying it differs from the printed one in exactly these ways. It is for
    comparing two spellings, never for storing one: an address is held to the
    spelling the binder or its page prints (`flows.verify.resolution_problems`),
    and this is how a misspelling of one place is told from another place.
    """
    return address.strip().casefold()
