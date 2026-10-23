"""A PAGE: one file, its paragraphs in order among the code they sit with.

`page_for()` builds one. Every line of the file is classified -- this line is
code, this PART of a line is code, this line is comment, this line is docstring
-- and each line belongs to a PARAGRAPH, which is one unit of prose or the empty
place where prose could go.

`page_for` builds it in steps: the cues are named, `empty_places` gives every
place no prose fills a paragraph of its own, `fill_the_gaps` divides each gap's
lines among its `b` places, and `tie_leading` keys each blank run by the place
it follows. `documentable` turns the declarations into positions in `cue`'s
sequence.

A page is all of the addresses in the file, which is what makes it a page and
not a list.
`places_on` -- or, on a Python page, the read's `code_for` and
`declarations_for` -- hands `cue` its lines of code and which of them declare
something documentable; `addresser` emits every place, filled or not, and
`attach` says which one a given paragraph sits in. A paragraph does not compute
its own cue -- if it did, a place would exist only when prose happened to fill
it.

`Page.serialize` and `RedactedPage` are the page as a binder carries it: the
five fields of each place, and the page read back with its source text and its
empty places struck out.

! The GATHER is every page in scope, put in the form the agents read. One page
is one file, so building one is not its work: its job is to take the output of
every page, and this module is where a page comes from.

!! IT IS A FLAT LIST, AND THAT IS THE SHAPE OF THE THING. Paragraphs run down a
page and do not nest. An address is an ORDINAL over a linear sequence and cannot
express containment, so the two agree by construction rather than by compromise.

!! THE ADDRESSER only needs to know the type of Series (DECLARED, GAP, ON, LEAD,
COVERS): it imports no `Paragraph`. `code_lines` and `attach` read paragraphs,
so they are page questions and live here.
"""

from dataclasses import dataclass
from dataclasses import field as dataclass_field
from itertools import pairwise
from pathlib import Path

from comment_review import constants
from comment_review.reading.addresser import (
    COVERS,
    DECLARED,
    GAP,
    LEAD,
    ON,
    Cues,
    address_for,
    cue,
    cue_of,
)
from comment_review.reading.context import ReadingContext
from comment_review.reading.context_io import context_from_wire, context_to_wire
from comment_review.reading.diagnostics import ReadDiagnostic, ReadFailure, ReadStage
from comment_review.reading.language import INSTALLED_REGISTRY, language_for
from comment_review.reading.lexer import (
    Language,
    declarations,
    document_declarations,
    leading_between,
)
from comment_review.reading.paragraph import Paragraph
from comment_review.reading.proof import SourceRead
from comment_review.reading.python.projection import (
    code_for,
    declarations_for,
    paragraphs_for,
)
from comment_review.reading.python.records import PythonRead
from comment_review.reading.readers import read_source
from comment_review.reading.registry import LanguageRegistry
from comment_review.reading.series import Kind, Series
from comment_review.reading.stripped import StrippedRead

#: The five fields a place is carried by, in the order `Page.serialize` writes
#: them. ! `path` IS NOT AMONG THEM: the page states it once, because repeating
#: it per place is the same string as many times as the file has paragraphs.
WIRE_FIELDS = ("cue", "anchor", "original_start", "original_end", "raw_text")

# !! EVERY LINE HAS AN ADDRESS, AND SO DOES EVERY POTENTIAL LINE. Without an
# empty `c` there is no way to say a comment belongs at the end of a code line,
# and without an empty `b` no way to say code should have lines of comment above
# it. So each series but `d` has an EMPTY kind, and they are what an `add`
# cites:
#
#   a   `undocumented`  a declaration with no docstring
#   b   `interval`      a gap with no prose
#   c   `margin`        a code line with no trailing comment
#   f   `dark-matter`   a file with none of its own prose
#
# !! THE QUESTIONS ARE ASKED OF `Kind`, AND THIS MODULE KEEPS NO SET. There are
# TWO of them and they are not the same question: `Kind.holds_no_prose` is what
# a count or a record asks, and `Kind.occupies_no_lines` is what
# `code_lines` asks. ! They part on exactly `leading`, which holds no prose and
# DOES stand on real lines. Neither is listed; both derive from `Series`.

# !! THE FILE'S OWN PROSE IS A PARAGRAPH TYPE, AND THE READER STATES IT -- see
# `Kind.MATTER`. Stamping it HERE would put a positioning rule in a module that
# may hold none, and make the page reconstruct what "top of the file" meant from
# a run already typed `comment`.
#
# ! ONE TYPE FOR BOTH ENDS. Which end a run sits at is read by `page_for` from
# where it opens -- line 1 takes the first `f` place, any other run the last --
# not stamped as a second fact that could disagree.
#
# Every consumer downstream asks the series, not this -- see `Page.prose`.
# Asking the type would miss the EMPTY place, which has no prose to type.


@dataclass
class Page:
    """ONE FILE: its paragraphs in order, among the code they sit with.

    It carries what it was built from -- the text, the cues and the path.
    A consumer that needed one of them would otherwise re-derive it from the
    file, which is a chance to read a file the page no longer describes, or
    ask the caller to carry it alongside.

    ! A page IS its paragraphs in order, so it iterates and indexes as one. That
    is not a convenience: a reviewer reads a page top to bottom, and a consumer
    that wants the list is asking for the page.

    Attributes:
        path: as the REPO sees it. Every citation resolves against that root.
        text: the file, exactly as it reads. What a splice is checked against.
        sha: of `text`, RECEIVED from the read and never derived here. ! The
            write chain compares it against the one the binder recorded, which
            is the only comparison that can fail -- a sha this module took for
            itself would be asking whether the text equals itself.
        paragraphs: in order down the page, prose and empty places alike.
        cues: EVERY place on the page, filled or not -- see
            `addresser.cue`. It is what makes an `add` citable.
        reading: how the file was read -- its language, reader, compatibility
            digest and settings, which a binder carries beside the sha.
        read: the record the reader made of the file. A proof compares two
            pages' reads to ask whether their code is the same.
        leading: the space below a place, keyed by the place it FOLLOWS --
            `f0 -> d0`. An absent key means nothing blank follows that place,
            which is what most boundaries do.
    """

    path: str
    text: str
    sha: str
    paragraphs: list[Paragraph]
    cues: Cues
    reading: ReadingContext
    read: SourceRead
    # !! `serialize` IS BELOW, AFTER `leading`. It writes what a binder carries
    # for this page -- see `_place` for the five fields and `RedactedPage` for
    # the variant that emits only the places holding prose.
    #
    # ! `leading` IS THE PAGE'S, NOT `cue`'S: `cue` runs before any prose is
    # read, and leading exists only where the LEXER found a blank run. `cue`
    # cannot know a `d` is there, so it cannot be `cue`'s to hold.
    #
    # !! ONE KEY, NOT A PAIR: the place a run follows. A second key naming the
    # place after it goes stale on a `drop`, naming a place the run no longer
    # separates. See `tie_leading`.
    leading: dict[str, str] = dataclass_field(default_factory=dict)

    def __iter__(self):
        """Down the page, in order."""
        return iter(self.paragraphs)

    def __len__(self) -> int:
        """How many paragraphs, prose and empty places alike."""
        return len(self.paragraphs)

    def __getitem__(self, i):
        """The nth paragraph down the page."""
        return self.paragraphs[i]

    @property
    def prose(self) -> list[Paragraph]:
        """The paragraphs a reviewer owes a record on.

        ! The empty places are ADDRESSABLE and not accountable: an `add` cites
        one, and nobody owes it a ruling. Front matter is prose and is not
        accountable either -- no role can settle a licence header.

        ! ASKED BY SERIES, not by the kind. The file's own matter is the `f`
        series, and every consumer that has to know reads that --
        `binder.addresses.handed`, which `flows.distribute.seed` and
        `flows.verify.coverage_problems` read, and this.

        !! `d` IS OUT BECAUSE IT NAMES NO PLACE, and that is the whole test.
        Leading is not prose, it is the space BETWEEN two paragraphs; a reviewer
        handed one would be asked to rule on blank lines. Requiring an ADDRESS
        keeps it out without a list of series to keep current -- a paragraph
        that names no place is owed no record.
        """
        return [
            b
            for b in self.paragraphs
            if b.address
            and not Kind.holds_no_prose(b.kind)
            # ! ASKED OF THE ADDRESS DIRECTLY: `cue_of` is the addresser's,
            # which this module already imports.
            and cue_of(b.address).series != COVERS
        ]

    def serialize(self) -> dict:
        """This page as a binder carries it: its path, its sha, its places.

        !! EVERY ADDRESSED PLACE, FILLED OR NOT. That is what separates a `Page`
        from a `RedactedPage` -- `bind`'s `absent=True`. A place with no address
        names nowhere, so it is carried by neither: leading is the only such
        place and a reviewer handed one would be asked to rule on blank lines.

        ! THE TEXT IS NOT WRITTEN. A binder is what an AGENT reads, and an agent
        gets the places; the compositor reads the file from disk. That is what
        makes everything read back a `RedactedPage` -- see there.
        """
        return {
            "path": self.path,
            "sha": self.sha,
            "reading": context_to_wire(self.reading),
            "rows": [_place(b) for b in self.paragraphs if b.address],
        }


def _place(paragraph: Paragraph) -> dict:
    """One place as an agent receives it -- the five fields of `WIRE_FIELDS`."""
    return {
        "cue": cue_of(paragraph.address).cue,
        "anchor": paragraph.anchor,
        "original_start": paragraph.original_start,
        "original_end": paragraph.original_end,
        "raw_text": "\n".join(paragraph.raw_lines),
    }


def _kind_of(series: "Series | None", raw_text: str) -> str:
    """This place's kind: its series, and whether prose fills it.

    !! BOTH HALVES. A `Definition` holds a PAIR -- `GAP = Definition("b",
    COMMENT, INTERVAL)` -- and taking `.present` unconditionally types every
    empty place as prose.

    Args:
        series: the cue's series, or None for a cue no series names.
        raw_text: the place's prose, as the wire carries it.

    Returns:
        The `present` kind when prose fills the place, the `absent` kind when
        nothing does, and "" when `series` is None. ! `d` HAS NO ABSENCE and
        falls back to its present -- a fence is never carried, so this cannot be
        reached through a binder, and answering "" would be a kind no series
        names.
    """
    if series is None:
        return ""
    if raw_text.strip():
        return series.value.present
    return series.value.absent or series.value.present


def _paragraph(place: dict, path: str) -> Paragraph:
    """One place read back into the `Paragraph` it was written from.

    !! A PARAGRAPH, NOT A REDACTED ONE. What a redaction removes is at the PAGE
    -- the source text, and the places holding no prose.

    ! THE FOUR FIELDS THE WIRE DOES NOT CARRY ARE DERIVED, NOT INVENTED:

        kind     `_kind_of`: the series' present kind, or its absent one if empty
        start    the recorded `original_start` -- nothing moves between the
        end      gather and the read back, so the two are the same lines
        lines    0 for an empty place, else the count of `raw_lines`

    ! `start`/`end` FALL BACK TO 0 when the wire carries null line numbers,
    which is this type's own spelling for *occupies nothing* -- see
    `Paragraph.__post_init__`.
    """
    cue_text = str(place["cue"])
    raw_text = str(place["raw_text"])
    raw_lines = raw_text.split("\n") if raw_text else []
    series = Series.of(cue_text)
    start = place.get("original_start")
    end = place.get("original_end")
    return Paragraph(
        path=path,
        start=start if isinstance(start, int) else 0,
        end=end if isinstance(end, int) else 0,
        kind=_kind_of(series, raw_text),
        # ! ZERO WHERE THE PLACE HOLDS NOTHING, which is what an EMPTY place
        # means -- `Kind.occupies_no_lines`. `raw_lines` still holds one entry
        # for it, so `len(raw_lines)` would say 1.
        lines=0 if not raw_text.strip() else len(raw_lines),
        text=raw_text,
        anchor=str(place.get("anchor", "")),
        address=address_for(path, cue_text),
        raw_lines=raw_lines,
        original_start=start if isinstance(start, int) else None,
        original_end=end if isinstance(end, int) else None,
    )


@dataclass(frozen=True)
class RedactedPage:
    """A page with its source struck out: what a binder carries and hands back.

    !! A REDACTION, NOT A PARALLEL DOCUMENT. Both hold the same `Paragraph`s.
    Two things are removed and both are the PAGE's:

        the source text     an agent reads places, not the file; the compositor
                            reads the file from disk and never the binder
        the empty places    a place where prose COULD go but does not

    !! AND AN EMPTY PLACE IS STILL ADDRESSED, WHICH IS WHAT MAKES THE CUT SAFE.
    The walk emits every place, so a reviewer that wants to `add` ASKS the
    addresser for the one it means -- `addresser --file m.py --line N --series b`
    answers `m.py@b1` from the PAGE, not from these rows. The place is citable
    without being carried.

    !! EVERYTHING READ BACK IS ONE OF THESE, WHATEVER WAS WRITTEN. A `Page`
    serializes its text nowhere, so a binder off disk cannot rebuild one --
    and saying it could is the lie a redaction exists to prevent. What differs
    between the two on the way OUT is which places are emitted; on the way IN,
    both are redacted, because the text is gone either way.

    Attributes:
        path: as the REPO sees it, the same field a `Page` carries.
        sha: of the page's text when it was gathered. The write chain compares
            it against the file it is about to set, which is the only
            comparison that can fail.
        paragraphs: the places carried, in order down the page. ORDINARY
            paragraphs -- see `_paragraph`.
    """

    path: str
    sha: str
    paragraphs: list[Paragraph]
    reading: ReadingContext

    @classmethod
    def of(cls, page: Page) -> "RedactedPage":
        """This page with its text and its empty places struck out."""
        return cls(
            path=page.path,
            sha=page.sha,
            reading=page.reading,
            paragraphs=[
                b
                for b in page.paragraphs
                if b.address and not Kind.holds_no_prose(b.kind)
            ],
        )

    def serialize(self) -> dict:
        """This page as a binder carries it -- only the places it kept."""
        return {
            "path": self.path,
            "sha": self.sha,
            "reading": context_to_wire(self.reading),
            "rows": [_place(b) for b in self.paragraphs],
        }

    @classmethod
    def deserialize(
        cls, where: str, data: object
    ) -> "tuple[RedactedPage | None, list[str]]":
        """One page of a binder, checked, with its paragraphs rebuilt.

        ! EVERY BAD PLACE IS REPORTED, not the first: a page handed back with
        two malformed places is two things to fix.

        Returns:
            `(RedactedPage, [])` or `(None, [messages])`.
        """
        if not isinstance(data, dict):
            return None, [f"{where}: a JSON {type(data).__name__}, not a page"]
        checked: dict = data
        path = checked.get("path")
        if not isinstance(path, str) or not path.strip():
            return None, [f"{where}: a page needs the `path` of the file it holds"]
        raw = checked.get("rows", [])
        if not isinstance(raw, list):
            kind = type(raw).__name__
            return None, [f"{where}: {path}: `rows` is a JSON {kind}, not a list"]
        paragraphs: list[Paragraph] = []
        problems: list[str] = []
        for n, one in enumerate(raw):
            place, why = _checked_place(f"{where}: {path} row {n}", one)
            if place is None:
                problems += why
            else:
                paragraphs.append(_paragraph(place, path))
        if problems:
            return None, problems
        reading, why = context_from_wire(f"{where}: {path}", checked.get("reading"))
        if reading is None:
            return None, why
        # ! AN ABSENT OR NULL `sha` IS ADMITTED AS "". `.get("sha", "")` defaults
        # only when the key is ABSENT, so a `"sha": null` arrives PRESENT and
        # holding None, and `str(None)` is the four-character word "None".
        raw_sha = checked.get("sha")
        return (
            cls(
                path=path,
                sha=raw_sha if isinstance(raw_sha, str) else "",
                paragraphs=paragraphs,
                reading=reading,
            ),
            [],
        )


def _checked_place(where: str, data: object) -> tuple[dict | None, list[str]]:
    """One place off the wire, or every rule it breaks.

    !! THE `cue` IS WHAT MAKES A PLACE ADDRESSABLE, so one without it is refused
    rather than folded to `""`. `address_for(path, "")` answers `""`, which is a
    place that names nowhere reaching a reviewer as a question about nothing.
    """
    if not isinstance(data, dict):
        return None, [f"{where}: a JSON {type(data).__name__}, not a row"]
    checked: dict = data
    cue_text = checked.get("cue")
    if not isinstance(cue_text, str) or not cue_text.strip():
        return None, [f"{where}: a row needs the `cue` of the place it holds"]
    problems: list[str] = []
    for name in ("anchor", "raw_text"):
        if not isinstance(checked.get(name), str):
            problems.append(f"{where}: {cue_text} needs a `{name}` string")
    for name in ("original_start", "original_end"):
        # ! `bool` IS AN `int` IN PYTHON and is refused on purpose: a JSON
        # `true` in a line number is a malformed artifact, not a line.
        # ! `None` IS ADMITTED -- an EMPTY place stands on no lines, and a
        # `Page` written with `absent=True` carries exactly that.
        value = checked.get(name)
        wrong = not isinstance(value, int) or isinstance(value, bool)
        if value is not None and wrong:
            problems.append(
                f"{where}: {cue_text} needs an `{name}` line number or null"
            )
    if problems:
        return None, problems
    return checked, []


def code_lines(text: str, prose: list[dict]) -> dict[int, str]:
    """Every LINE OF CODE on this page, in order, with the code on it.

    ```python
    {2: "N = 0", 3: "def f():", 5: "    return 1"}
    ```

    ! A `dict` is insertion-ordered, so ASCENDING BY CONSTRUCTION answers all
    four consumers: iterate it for `cue`, `n in code` for occupancy,
    `enumerate` for the ordinals, `code[n]` for one line's anchor.

    A line is code when it holds something that is not blank and not prose.
    This function knows only what a comment-syntax record spells, so `page_for`
    sends it the lexical reader's pages; a Python page takes its code lines from
    `code_for` over its read, which knows a string literal is a declaration's
    documentation.

    ! A `trailing-comment` sits ON a code line, so that line stays code. A
    `comment` or `docstring` paragraph occupies its lines entirely, so those lines
    are not. An `interval` occupies nothing, which is what makes this safe to
    run over a page that already holds intervals.

    !! A PARAGRAPH'S FIRST LINE IS STILL CODE WHEN CODE PRECEDES ITS TEXT.
    `int b = 2; /* opens` spans from that line, and taking the whole span would
    drop the statement from the code set, moving every interval boundary below
    it.

    !! THE PARAGRAPH SAYS SO, BY ITS SERIES -- a `c` place is the room beside
    code, filled or not.

    !! THE CHARACTERS COME FROM THAT LINE'S `c`, NEVER RE-CUT HERE. Every code
    line has exactly one `c` -- a `trailing-comment`, or the `margin` standing
    in for one -- and it already states where the code stops. Cutting the line
    again answers `'    return os  # why'` where the `c` for the same line
    answers `'    return os'`: two computations of one fact.

    ! It takes DICTS -- `vars()` of each paragraph being built, which is what
    all three callers pass. An address counts code lines, so the count has to be
    the same one the gather used or the two disagree about what `@b3` means.
    """
    occupied: set[int] = set()
    beside: dict[int, str] = {}
    for b in prose:
        start, end = b.get("start"), b.get("end")
        # ! The `c` is read BEFORE the occupancy test, because the paragraph
        # standing in for one is a `margin`, which occupies nothing.
        if Series.of_kind(str(b.get("kind", ""))) is Series.ON and isinstance(
            start, int
        ):
            beside[start] = b.get("anchor", "")
        # ! AN EMPTY PLACE OCCUPIES NOTHING, which is what its kind means. At
        # this point an `interval` still spans the gap between two code lines --
        # `fill_the_gaps` has not recut it yet -- so counting it would take
        # those lines out of the code and renumber every `b` below.
        if Kind.occupies_no_lines(str(b.get("kind", ""))):
            continue
        if not isinstance(start, int) or not isinstance(end, int):
            continue
        occupied.update(range(start, end + 1))
        if Series.of_kind(str(b.get("kind", ""))) is Series.ON:
            occupied.discard(start)
    return {
        n: beside.get(n) or line.rstrip()
        for n, line in enumerate(constants.text_lines(text), 1)
        if line.strip() and n not in occupied
    }


def attach(paragraph: dict, cues: "Cues") -> str:
    """Which place this paragraph occupies -- the cue, without the path.

    !! THE PARAGRAPH DOES NOT PRODUCE THE ADDRESS; IT IS TIED TO ONE. `cue`
    emitted every place before any prose was looked at, so this only asks which
    of them this prose is sitting in. Reversed -- a paragraph computing its own
    cue -- is how a place could exist only when prose happened to fill it.

    ! TWO FACTS DECIDE IT, and neither is inferred from the kind alone: a
    paragraph in the `c` SERIES sits beside code and takes that line's place,
    and everything else holds a gap and takes the `b` for it. A paragraph that
    documents a declaration never reaches here: the reader stamps its `a` when
    it tags it, and `page_for` keeps a stamped cue.

    Args:
        paragraph: `vars()` of one paragraph `page_for` is building.
        cues: `cue` over that paragraph's file.

    Returns:
        The cue, or "" when the paragraph states no position to tie it to.
    """
    # ! FRONT MATTER IS THE FILE'S, so it takes an `f` place wherever it sits.
    # Asking `above()` would give it the gap it happens to occupy, which is the
    # gap that introduces the first statement and belongs to that statement.
    # !! THE READER SAYS SO, and this only reads it. Stamping it here instead
    # would be a positioning rule in a module that may hold none.
    #
    # ! WHICH `f` IS A POSITION -- `page_for` gives a run opening on line 1 the
    # first `f` place `cue` emitted and any other run the last. This says only
    # that the question is not `above()`'s to answer.
    if paragraph.get("kind") == Kind.MATTER:
        return ""
    if Series.of_kind(str(paragraph.get("kind", ""))) is Series.ON:
        start = paragraph.get("start")
        return cues.beside(start) if isinstance(start, int) else ""
    at = paragraph.get("original_start")
    return cues.above(at) if isinstance(at, int) else ""


def documentable(
    decls: list[tuple[int, int, bool]], code: dict[int, str]
) -> dict[int, tuple[int, int, str]]:
    """Which code lines DECLARE something documentable, and WHERE the doc sits.

    !! IT CONVERTS. The reader states which side a language's documentation goes on,
    as the `above` of each declaration it returns -- `lexer.declarations`, or
    `declarations_for` on a Python page. What is left here is turning a LINE into a
    position in `cue`'s own sequence.

    !! THAT POSITION IS AN ORDINAL, which is the other half of the job. `cue`
    counts code lines, so handing it a raw line would make it compare
    `insert <= n` to place a docstring -- line arithmetic in the one module that
    must do none.

    Args:
        decls: `(line, insert, above)` per declaration, module first -- see
            `lexer.declarations`, which states all three.
        code: `cue`'s triggers, `(line, anchor)` in order.

    Returns:
        `index into code -> (the LINE the doc occupies, the code index it is set
        at, WHICH SIDE of that index's gap)`. `lexer.document_declarations` is
        what walks up from a declaration to find prose already sitting there.
        The index and the side are what the walk places by: `ON` sets the doc
        between the gap and the code, `GAP` sets it before the gap -- which is
        where a doc that sits INSIDE its declaration lands, because the gap
        beneath it introduces whatever comes next. Empty when `decls` holds the
        module alone, and the file then has an `a0` and no more; with no `decls`
        at all `places_on` passes `cue` no module place and the file has no `a`
        series.
    """
    at = {n: i for i, n in enumerate(code)}
    ordered = sorted(at)
    out: dict[int, tuple[int, int, str]] = {}
    for line, insert, above in decls[1:]:
        if line not in at:
            continue
        if above:
            # ! ABOVE THE DECLARING LINE, which is that line's own place: the doc
            # is set after the gap and before the code.
            out[at[line]] = (insert, at[line], ON)
            continue
        # ! INSIDE THE DECLARATION -- so it is set after whatever code the
        # declaration spans, before the gap that introduces the body. A wrapped
        # signature moves that several code lines down, which is why the LINE is
        # what the parser states and the ordinal is worked out here.
        follows = [n for n in ordered if n >= insert]
        out[at[line]] = (insert, at[follows[0]] if follows else len(code), GAP)
    return out


def places_on(text: str, prose: list[dict], lang: "Language | None" = None) -> "Cues":
    """Every place on this page, walked.

    !! THE PAGE NAMES ITS OWN PLACES, which is what makes it a page rather than
    a list. It hands `cue` its lines of code and which of them declare
    something documentable; `cue` emits every place, filled or not, and
    `attach` says which one a given paragraph sits in.

    Args:
        text: the file's source.
        prose: its paragraphs, as dicts.
        lang: its record, so the declarations can be resolved HERE -- the
            keyword path scans the code lines, and this is where they are
            computed. None gives a page with no `a` series.

    Returns:
        The `Cues` for this page.
    """
    code = code_lines(text, prose)
    decls = declarations(lang, code) if lang else []
    placed = documentable(decls, code) if lang else {}

    # !! `None`, NOT `1`, WHEN THERE ARE NO DECLARATIONS. A language with no
    # documentable declaration has no `a` series at all -- see `cue`. It is
    # not a series that happens to be empty.
    return cue(code, placed, decls[0][1] if decls else None)


def empty_places(
    text: str, cues: Cues, occupied: set[str]
) -> list[Paragraph] | ReadFailure:
    """A paragraph for every place `cue` emitted that no prose fills.

    ! `cue` already emitted every place and said where each sits. This asks
    only which of them prose is sitting in, and gives the rest a paragraph.

    ! An empty place occupies no lines -- that is what the ABSENT half of a series
    means, see `Series` -- and it is why emitting one cannot move a code
    line or renumber anything below it.

    Args:
        text: the page's source.
        cues: every place on the page.
        occupied: the cues that prose already sits in.

    Returns:
        The empty paragraphs, in no particular order -- the caller sorts --
        or a `ReadFailure` when a `c` has no line or a series has no branch.
    """
    lines = constants.text_lines(text)
    last = len(lines)
    out: list[Paragraph] = []
    for cue_name, anchor in cues.places.items():
        if cue_name in occupied:
            continue
        if cue_name.startswith(DECLARED):
            # ! A DECLARATION WITH NO DOCSTRING. It occupies NO LINE, because the
            # prose is not written yet.
            #
            # !! SO ITS ORIGINAL LINES ARE None, NOT `insert..insert-1`. The
            # field holds a closed list of lines, or None when no line currently
            # holds the place. WHERE the prose would go is the insert line
            # `documentable` hands to `cue`, and is not this field's to say -- an
            # empty slice standing in for a position teaches a reader to take
            # these numbers for one.
            out.append(
                Paragraph(
                    path="",
                    start=0,
                    end=0,
                    kind="undocumented",
                    lines=0,
                    text="",
                    anchor=anchor,
                    original_start=None,
                    original_end=None,
                    address=cue_name,
                )
            )
        elif cue_name.startswith(ON):
            # ! The room BESIDE a line of code: whatever follows the statement,
            # which is nothing unless the line ends in whitespace. The code is
            # the ANCHOR, so storing it here too would put one fact in two
            # fields.
            n = cues.anchor_line(cue_name)
            if n is None:
                # !! A `c` ANSWERS TO A LINE OF CODE BY CONSTRUCTION. The `ON`
                # series emits at code triggers and never at the `<module>` or
                # `<eof>` sentinels, which are the only triggers with no line --
                # so None here is the cues disagreeing with the page that
                # built it, and not a shape any file can produce.
                # ! IT IS NAMED RATHER THAN SKIPPED. Continuing would drop a
                # place out of the reading order, which the compositor sets
                # from, so the file would come back missing a line and every
                # gate would still be green.
                return ReadFailure(
                    (
                        ReadDiagnostic(
                            ReadStage.PLACE,
                            "unsupported-placement",
                            f"{cue_name}: a `c` place whose anchor has no line",
                        ),
                    )
                )
            code = lines[n - 1].rstrip()
            out.append(
                Paragraph(
                    path="",
                    start=n,
                    end=n,
                    kind="margin",
                    lines=0,
                    text="",
                    raw_lines=[lines[n - 1][len(code) :]],
                    original_start=n,
                    original_end=n,
                    anchor=anchor,
                    address=cue_name,
                )
            )
        elif cue_name.startswith(COVERS):
            # !! THE FILE'S OWN PROSE, AND IT HOLDS NO LINE WHEN IT IS EMPTY.
            # A licence header or a shebang goes at the very top, bounded by
            # nothing on either side -- so there is no gap to measure and
            # nothing to divide.
            out.append(
                Paragraph(
                    path="",
                    start=0,
                    end=0,
                    kind="dark-matter",
                    lines=0,
                    text="",
                    original_start=None,
                    original_end=None,
                    anchor=anchor,
                    address=cue_name,
                )
            )
        elif not cue_name.startswith(GAP):
            return ReadFailure(
                (
                    ReadDiagnostic(
                        ReadStage.PLACE,
                        "unsupported-placement",
                        f"no rule for the series of {cue_name!r} -- every series in"
                        " `addresser.SERIES` needs a branch here",
                    ),
                )
            )
        else:
            previous, following = cues.gap_bounds(cue_name)
            low = previous + 1
            high = following - 1 if following else last
            # ! THE WHOLE GAP, PROVISIONALLY. `fill_the_gaps` runs after every
            # paragraph exists and is what divides a gap between the places in
            # it; deciding a share here would decide it against neighbours that
            # are still being built.
            out.append(
                Paragraph(
                    path="",
                    start=low if low <= high else 0,
                    end=high if low <= high else 0,
                    kind="interval",
                    lines=0,
                    text="",
                    # ! A CLOSED LIST OR None -- see `Paragraph`. `low > high`
                    # here says the gap holds no line of its own, which is not
                    # a range and is not written as one.
                    original_start=low if low <= high else None,
                    original_end=high if low <= high else None,
                    anchor=anchor,
                    address=cue_name,
                )
            )
    return out


def tie_leading(paragraphs: list[Paragraph], cues: Cues) -> dict[str, str]:
    """Tie each run of leading to the place it FOLLOWS.

    !! LEADING IS AN EDGE, AND AN EDGE BELONGS TO THE PLACE BEFORE IT -- so on a
    `drop` the live first key keeps its leading and the dropped one loses it.
    Every other series answers to a line of code and has a position in the
    walk's reading order; a run of blanks answers to neither, so it is filed
    under the place it comes after -- `f0 -> d0` reads as *the space below the
    file's matter*.

    !! ONE KEY, NOT A PAIR. A key naming the place AFTER the run goes stale on a
    drop: dropping `P` between X and Y leaves `(X, P)` alive and sets it between
    X and **Y**, so the stored pair would name a place it no longer separates.

    ! WHICH IS WHY `cue` DOES NOT EMIT ONE. `cue` runs before any prose
    is read and leading exists only where the lexer found a blank run, so the
    walk cannot know a `d` is there. An edge needs no position in `cue`'s
    list, so it does not have to.

    ! A RUN ABOVE EVERYTHING FOLLOWS THE FILE'S HEAD, and is tied under the first
    place `cue` emitted -- `f0` -- or `""` only for a `Cues` with no places.

    Args:
        paragraphs: every paragraph on the page, addressed.
        cues: `cue`'s places, to name what sits before each run.

    Returns:
        The edge map: the cue a run of leading follows -> its own cue. An
        absent key means that place is followed by no blank line.
    """
    edges: dict[str, str] = {}
    # ! The places that HOLD LINES, in the order they hold them -- the sequence
    # a run of leading falls between. Read from the original text, which is what
    # this pass is entitled to: it is establishing the edges ONCE, at build.
    set_places = sorted(
        (b for b in paragraphs if b.original_start and b.kind != Kind.LEADING),
        key=lambda b: b.original_start or 0,
    )
    # !! THE HEAD OF THE FILE IS A PLACE, NOT AN ABSENCE: `cue` emits `f0` at
    # the MODULE on EVERY file, filled or not.
    head = cues.reading[0] if cues.reading else ""
    for b in sorted(paragraphs, key=lambda b: b.original_start or 0):
        if b.kind != Kind.LEADING or not b.symbol:
            continue
        start = b.original_start or 0
        # !! IT IS THE LAST PLACE THAT HELD LINES, never merely the last place
        # SEEN. The last place seen below a docstring is the EMPTY gap under it,
        # and tying the space to that gap would set an `add` into it ABOVE the
        # blank line and away from the code it documents.
        before = head
        for other in set_places:
            if (other.original_end or 0) >= start:
                break
            before = other.address.split("@")[-1]
        edges[before] = b.symbol
    return edges


def page_for(
    path: Path,
    text: str,
    rel: str | None = None,
    *,
    sha: str,
    reading: ReadingContext,
    registry: LanguageRegistry = INSTALLED_REGISTRY,
) -> Page | ReadFailure:
    """Build one file's `Page`, or the `ReadFailure` that stopped it.

    Reads the file, addresses every paragraph and empty place, divides the gaps
    and ties the leading.
    """
    result = read_source(path, text, registry=registry)
    if isinstance(result, ReadFailure):
        return result
    if not isinstance(result, PythonRead) and not isinstance(result, list):
        # A reader record other than Python's has no page builder yet.
        return ReadFailure(
            (
                ReadDiagnostic(
                    ReadStage.LEX,
                    "reader-unfinished",
                    "The Rust reader is not finished and reads no source",
                ),
            )
        )
    recognized = result if isinstance(result, PythonRead) else None
    if recognized is not None:
        # The read may have broken a docstring's shared line; the page is that text.
        text = recognized.source.text
    got = paragraphs_for(path, recognized) if recognized is not None else result
    assert not isinstance(got, PythonRead)
    if isinstance(got, ReadFailure):
        return got
    got.extend(leading_between(got, text))
    cues = Cues()
    edges: dict[str, str] = {}
    prose = [vars(b) for b in got]
    if recognized is not None:
        code = code_for(recognized)
        decls = declarations_for(recognized)
        cues = cue(code, documentable(decls, code), decls[0][1])
    else:
        lang = language_for(path)
        assert lang is not None, "a lexical read comes only from a lexical row"
        cues = places_on(text, prose, lang)
        code = code_lines(text, prose)
        document_declarations(got, declarations(lang, code), code)
    here = rel if rel is not None else path.as_posix()
    files = cues.file_places()
    leads = iter(range(10**9))
    for b in sorted(got, key=lambda b: b.original_start or 0):
        if b.kind == Kind.LEADING:
            b.symbol = f"{LEAD}{next(leads)}"
            b.address = ""
            continue
        if b.kind == Kind.MATTER and b.address.startswith(DECLARED):
            b.kind = Kind.COMMENT
        if b.kind == Kind.MATTER:
            place = files[0] if b.original_start == 1 else files[-1]
        else:
            stamped = b.address if b.address in cues.places else ""
            place = stamped or attach(vars(b), cues)
        b.address = address_for(here, place)
        b.anchor = cues.anchor_of(place, b.anchor)
    occupied = {b.address.split("@")[-1] for b in got if "@" in b.address}
    empty_paragraphs = empty_places(text, cues, occupied)
    if isinstance(empty_paragraphs, ReadFailure):
        return empty_paragraphs
    for empty in empty_paragraphs:
        empty.address = address_for(here, empty.address)
        got.append(empty)
    for b in got:
        place_name = b.address.split("@")[-1]
        b.anchor_line = cues.anchor_line(place_name) if place_name else None
        b.anchor_num = cues.anchor_num(place_name) if place_name else 0
    fill_the_gaps(text, got, code=code if recognized is not None else None)
    edges = tie_leading(got, cues)

    where = rel if rel is not None else path.as_posix()
    for b in got:
        b.path = where
    return Page(
        path=rel if rel is not None else path.as_posix(),
        text=text,
        sha=sha,
        reading=reading,
        paragraphs=sorted(got, key=lambda b: (b.start, b.end)),
        cues=cues,
        read=recognized if recognized is not None else StrippedRead(text, path),
        leading=edges,
    )


def fill_the_gaps(
    text: str, paragraphs: list[Paragraph], *, code: dict[int, str] | None = None
) -> None:
    """Give every line of a gap to the paragraph it belongs to, blanks included.

    !! EVERY LINE HAS AN ADDRESS. A paragraph addressed only by the lines its
    prose occupies leaves a blank line beside it belonging to nothing, and a
    reviewer asking which place holds one gets no answer at all.

    ! A paragraph runs to the next paragraph, or to the end of its gap. Leading
    blanks go to the first paragraph in the gap and trailing blanks to the last,
    which is the same rule read from either end.

    !! IT MOVES THE ORIGINAL RANGE WITH IT, and `raw_lines` with that. With the
    two ranges disagreeing, a blank line is addressed by a paragraph and covered
    by none, so the invariant holds on one range and not the other.

    ! THE OBJECTION IT OVERRIDES, kept because it is real: widening the original
    range lets a `change` swallow the blank line that separates a comment run
    from the code beneath it. Whether a blank still belongs is
    `compositor.set_page`'s question, which is why the lines must be MARKED even
    though writing them verbatim would be wrong.

    !! AN `a` IS NOT WIDENED. A declaration's documentation has none of that
    flexibility: its lines are the docstring's and a blank beside it belongs to
    the gap.

    Args:
        text: the page's source.
        paragraphs: every paragraph on the page, addressed; the `b`s are recut
            in place.
        code: the code lines the page's `Cues` were walked from -- Python pages
            pass `projection.code_for`. None recomputes them with `code_lines`,
            and the two must agree or every gap boundary moves.
    """
    source = constants.text_lines(text)
    code_lines_in_order = list(
        code if code is not None else code_lines(text, [vars(b) for b in paragraphs])
    )
    last = len(source)
    edges = [0, *code_lines_in_order, last + 1]

    # !! EVERY OTHER SERIES OWNS ITS LINES EXACTLY, AND `b` TAKES WHAT IS LEFT.
    #
    # ! `f` IS IN THAT LIST BECAUSE IT IS A SERIES, not because it is front
    # matter. `b` owns every line that is not another series' lines, and that
    # rule stays true without a clause naming front matter only because front
    # matter has a series of its own -- otherwise it is the one paragraph whose
    # cue disagrees with the gap it sits in, and a licence header reads as an
    # `interval`.
    #
    # !! LEADING IS IN THAT LIST BY ITS SYMBOL, not by an address, because it
    # HAS none -- see `addresser.SERIES`. It owns its lines exactly for the same
    # reason an `a` does: the lexer found them and said which they are. ! Read
    # from `address` alone a `d` answers "", and the gap would take the blank
    # lines a run of leading already holds -- setting them TWICE.
    exact: set[int] = set()
    for b in paragraphs:
        series = (b.address.split("@")[-1] or b.symbol)[:1]
        # ! BOTH ENDS ARE TESTED because both are `int | None` and they are set
        # as a PAIR -- a paragraph that holds lines holds both, one that holds
        # none holds neither. Testing the start alone narrowed half the range
        # and left the other half to fail on `None + 1`.
        if series and series != GAP and b.original_start and b.original_end:
            exact.update(range(b.original_start, b.original_end + 1))

    def recut(b: Paragraph, mine: set[int] | None = None) -> None:
        """Give this paragraph its share of the gap, on both ranges.

        !! A `b` TAKES THE FREE LINES AND ONLY THOSE. When its free lines are
        not contiguous its span runs over the paragraph sitting inside it, so
        slicing the span whole would set that paragraph twice.
        """
        if b.end >= b.start >= 1:
            b.original_start, b.original_end = b.start, b.end
            # ! `raw_lines` is what `compositor.set_page` SETS, over exactly
            # this range.
            own = [n for n in range(b.start, b.end + 1) if mine is None or n in mine]
            b.raw_lines = [source[n - 1] for n in own]
        else:
            # ! NO LINE CARRIES THIS PLACE, and that is the whole
            # answer. Where prose would GO is not recorded: a record
            # names the PLACE and says what changes in it.
            b.original_start = b.original_end = None
            b.raw_lines = []

    for prev, nxt in pairwise(edges):
        lo, hi = prev + 1, min(nxt - 1, last)
        if lo > hi:
            continue
        free = [n for n in range(lo, hi + 1) if n not in exact]
        # ! ONLY THE `b`s SHARE IT. An `a` in this gap keeps the lines it has --
        # it has none of the flexibility a `b` has.
        here = sorted(
            (
                b
                for b in paragraphs
                if b.start >= 1
                and lo <= b.start <= hi
                and b.address.split("@")[-1][:1] == GAP
            ),
            key=lambda b: b.start,
        )
        if not here:
            continue
        if not free:
            # ! Every line here is spoken for, so each `b` holds NONE. `0/0` is
            # how the addressing range spells "occupies nothing" and `None` is
            # how the original lines do -- no line is in this place.
            for b in here:
                b.start, b.end = 0, 0
                recut(b)
            continue
        here[0].start = free[0]
        for a, nxt_b in zip(here, here[1:], strict=False):
            a.end = nxt_b.start - 1
        here[-1].end = free[-1]
        owned = set(free)
        for b in here:
            recut(b, owned)
