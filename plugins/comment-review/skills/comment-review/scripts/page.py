"""A PAGE: one file, its paragraphs in order among the code they sit with.

`page_for()` builds one. Every line of the file is classified -- this line is
code, this PART of a line is code, this line is comment, this line is docstring
-- and each line belongs to a PARAGRAPH, which is one unit of prose or the empty
place where prose could go.

!! A PAGE NAMES ITS OWN PLACES, which is what makes it a page and not a list.
`places_on` hands the walk its lines of code and which of them declare something
documentable; `foliator` emits every place, filled or not, and `attach` says
which one a given paragraph sits in. A paragraph does not compute its own folio
-- reversed, a place existed only when prose happened to fill it, and the
file's own matter and the gap above the first line of code were mutually
exclusive.

! The CENSUS is every page in scope, formatted for the agents. One page is one
file, so building one was never its work -- Roy, 2026-08-20: *"the census's job
should be to take the output of all of the pages and reformat it into the (most)
usable format for the agents."*

!! IT IS A FLAT LIST, AND THAT IS THE SHAPE OF THE THING. Paragraphs run down a
leaf and do not nest. An address is an ORDINAL over a linear sequence and cannot
express containment, so the two agree by construction rather than by compromise.

! It was called a *pseudo* Concrete Syntax Tree, and the word is retired. Roy,
2026-08-20: *"it never really fit -- using libcst in python made it easy to move
and edit comments and so I thought that was what this was. It isn't."* Naming it
for a syntax tree invited an apology for not being one, and everything the
apology defended is correct for a page.

! Nothing here asks a tree question either. Measured 2026-08-18 across the
shipped scripts: ZERO containment tests, and every consumer is a flat scan by
path, a lookup by line, an ordered walk or a range splice. A tree would be
flattened again at each of them.

! Where hierarchy IS wanted it arrives as a stamped FACT, not a structure: a
paragraph's enclosing declaration, which the Python AST already knows and which 191
of this repo's 266 anchorless prose paragraphs sit inside. Depth is 1 for 182 of
those 191, so a parent link is the shape that fits and a tree is not.

!! TWO LEAVES BENEATH THIS ONE, and the direction inverted 2026-08-20. A page
builds itself, so it needs the foliator -- which had been importing this module
for two constants, a cycle. The cut is that THE FOLIATOR KNOWS NOTHING ABOUT A
PARAGRAPH: `code_lines` and `attach` were the only two functions of it that did,
and both are page questions wearing an addressing name.

! Letting the import graph choose a module's subject is what this keeps undoing.
`Paragraph` first lived in `census.py`, at the top of the graph, so the modules
that READ paragraphs could not import the definition of one -- 21 untyped
`paragraph.get(...)` reads, and two kind sets that ended up in `galley` because
it was the deepest module all three could reach.
"""

import re
import sys
from dataclasses import dataclass
from itertools import pairwise
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from foliator import (  # noqa: E402  -- path shim must run first
    DECLARED,
    FRONT,
    GAP,
    LEAD,
    ON,
    Foliation,
    flatten,
    foliate,
    series_of,
)
from lexer import (  # noqa: E402  -- path shim must run first
    LEADING,
    MATTER,
    Language,
    Paragraph,
    declarations,
    document_declarations,
    flag_structural_docs,
    leading_between,
    paragraphs_lexical,
    paragraphs_stdlib,
    tier_for,
)

# !! EVERY LINE HAS AN ADDRESS, AND SO DOES EVERY POTENTIAL LINE. Roy,
# 2026-08-19: without an empty `c` "you can't specify that the comment belongs
# at the end of the code line", and without an empty `b` "you can't specify that
# the code should have multiple lines of comment above it". So each series has
# an EMPTY kind, and they are what an `add` cites:
#
#   a   `undocumented`  a declaration with no docstring
#   b   `interval`      a gap with no prose
#   c   `margin`        a code line with no trailing comment
#   f   `dark-matter`   a file with none of its own prose
#
# !! KINDS THAT OCCUPY NO LINES AT ALL. A `margin` is the empty room beside a
# code line; an `interval` and an `undocumented` declaration are both EMPTY --
# a place where prose could go and does not. Counting any of them as occupied
# would drop a real code line from the count and renumber every `b` below it.
#
# !! A `trailing-comment` IS NOT ONE OF THEM, and was until 2026-08-20. It
# shares only its FIRST line with code: a WRAPPED one -- `int b = 2; /* opens`
# running on to a second line -- owns every line after that outright. Listing
# it here left those continuation lines counted as code, so `   and runs on */`
# was given a `margin` of its own. The loop below occupies its whole span and
# then discards the first line, which is right for a wrapped one and reduces to
# "occupies nothing" for a single-line one.
OCCUPIES_NOTHING = ("margin", "interval", "undocumented", "dark-matter")
# !! HOLDS NO PROSE -- a DIFFERENT set, and the two are not interchangeable. A
# `trailing-comment` occupies no lines of its own but is prose; an `interval`
# and an `undocumented` declaration are places where prose could go and does
# not. This set is what "addressable, not accountable" means: they are cited by
# an `add` and they get no seeded record.
HOLDS_NO_PROSE = ("interval", "undocumented", "margin", "dark-matter")

# !! THE FILE'S OWN PROSE IS A PARAGRAPH TYPE, AND THE LEXER STATES IT -- see
# `lexer.MATTER`. It was an ANNOTATION stamped HERE by `mark_matter` until
# 2026-08-21, which put a positioning rule in a module that may hold none and
# made the page reconstruct what "top of the file" meant from a run already
# typed `comment`.
#
# ! ONE TYPE FOR BOTH ENDS. Roy: *"front-matter, back-matter are paragraph type
# matter."* Which end a run sits at is the ORDER the `f` foliator emitted its
# places, counted by `page_for` -- not a second fact that could disagree.
#
# ! EVERY CONSUMER DOWNSTREAM ASKS THE SERIES, not this: the census filter, the
# accountability set, the `query` guard, the record seeding and `Page.prose`.
# Asking the type would miss the EMPTY place, which has no prose to type -- an
# `add` proposing a licence header on a file that has none was never turned into
# a query. Measured 2026-08-20.


@dataclass
class Page:
    """ONE FILE: its paragraphs in order, among the code they sit with.

    !! IT CARRIES WHAT IT WAS BUILT FROM, and that is the whole reason it is a
    type. `page_for` returned a bare list and dropped the text, the foliation,
    the tier and the path -- so every consumer that needed one of them either
    re-derived it from the file, which is a chance to read a file the page no
    longer describes, or asked the caller to carry it alongside.

    ! A page IS its paragraphs in order, so it iterates and indexes as one. That
    is not a convenience: a reviewer reads a page top to bottom, and a consumer
    that wants the list is asking for the page.

    Attributes:
        path: as the REPO sees it. Every citation resolves against that root.
        text: the file, exactly as it reads. What a splice is checked against.
        paragraphs: in order down the page, prose and empty places alike.
        foliation: EVERY place on the page, filled or not -- see
            `foliator.foliate`. It is what makes an `add` citable.
        tier: which questions this file's reader could answer.
    """

    path: str
    text: str
    paragraphs: list[Paragraph]
    foliation: Foliation
    tier: str

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

        ! ASKED BY SERIES, not by the kind. Since 2026-08-20 the file's own
        matter is the `f` series, and every consumer that has to know reads that
        -- `census.py`'s filter, `verdicts.py`'s accountability set and its
        `query` guard, `record.py`'s seeding, and this.

        !! `d` IS OUT FOR A DIFFERENT REASON: leading is not prose at all, it is
        the space BETWEEN two paragraphs. Roy, 2026-08-21: *"there is no
        information to rule on. It is just there for document preservation."* A
        reviewer handed one would be asked to rule on blank lines.
        """
        return [
            b
            for b in self.paragraphs
            if b.kind not in HOLDS_NO_PROSE and series_of(vars(b)) not in (FRONT, LEAD)
        ]


def code_lines(text: str, prose: list[dict]) -> dict[int, str]:
    """Every LINE OF CODE on this page, in order, with the code on it.

    ```python
    {2: "N = 0", 3: "def f():", 5: "    return 1"}
    ```

    !! ONE STRUCTURE, WHERE THERE WERE THREE FUNCTIONS. `code_lines_of` returned
    the numbers, `code_lines` returned them again as a `set` for membership, and
    `lines_of_code` returned them paired with their characters -- two names for
    one question, and a `sorted()` bridging the types that nearly every caller
    wrote to convert the set back into the ascending list the first already
    returned. Roy, 2026-08-20: *"the fact that you said 'sets' leaves me
    thinking we have a sorted-dictionary or it should always be a list."*

    ! A `dict` is insertion-ordered, so ASCENDING BY CONSTRUCTION answers all
    four consumers: iterate it for the walk, `n in code` for occupancy,
    `enumerate` for the ordinals, `code[n]` for one line's anchor.

    A line is code when it holds something that is not blank and not prose. The
    two tiers cannot answer that identically, and the difference is the
    docstring: `tokenized` knows a string literal is a declaration's
    documentation, `lexical` knows only what its comment-syntax record spells.
    So a paragraph's BOUNDS are tier-dependent while its CONTENT is not.

    ! A `trailing-comment` sits ON a code line, so that line stays code. A
    `comment` or `docstring` paragraph occupies its lines entirely, so those lines
    are not. An `interval` occupies nothing, which is what makes this safe to
    run over a census that already holds intervals.

    !! A PARAGRAPH'S FIRST LINE IS STILL CODE WHEN CODE PRECEDES ITS TEXT.
    `int b = 2; /* opens` spans from that line, and taking the whole span
    dropped the statement from the code set, moving every interval boundary
    below it.

    !! THE PARAGRAPH SAYS SO, via `original_column`. This tested whether the stored
    text was a proper SUFFIX of the physical line, which is an inference and
    was wrong in both directions: `paragraphs_stdlib` stores the WHOLE line for a
    trailing comment, so the test never fired for one -- and a paragraph comment
    opened after a statement had its declaration line dropped from the code
    set, moving every interval boundary in the file. Measured 2026-08-18.

    !! THE CHARACTERS COME FROM THAT LINE'S `c`, NEVER RE-CUT HERE. Every code
    line has exactly one `c` -- a `trailing-comment`, or the `margin` standing
    in for one -- and it already states where the code stops. Cutting the line
    again answers `'    return os  # why'` where the `c` for the same line
    answers `'    return os'`: two computations of one fact.

    ! It takes DICTS, so it reads a census off disk and a census still being
    built alike. An address counts code lines, so the count has to be the same
    one the census used or the two disagree about what `@b3` means.
    """
    occupied: set[int] = set()
    beside: dict[int, str] = {}
    for b in prose:
        start, end = b.get("start"), b.get("end")
        # ! The `c` is read BEFORE the occupancy test, because the paragraph
        # standing in for one is a `margin`, which occupies nothing.
        if b.get("original_column") and isinstance(start, int):
            beside[start] = b.get("anchor", "")
        if b.get("kind") in OCCUPIES_NOTHING:
            continue
        if not isinstance(start, int) or not isinstance(end, int):
            continue
        occupied.update(range(start, end + 1))
        if b.get("original_column", 0):
            occupied.discard(start)
    return {
        n: beside.get(n) or line.rstrip()
        for n, line in enumerate(text.splitlines(), 1)
        if line.strip() and n not in occupied
    }


def attach(paragraph: dict, foliation: "Foliation") -> str:
    """Which place this paragraph occupies -- the folio, without the path.

    !! THE PARAGRAPH DOES NOT PRODUCE THE ADDRESS; IT IS TIED TO ONE. The walk
    emitted every place before any prose was looked at, so this only asks which
    of them this prose is sitting in. Reversed -- a paragraph computing its own
    folio -- is how a place could exist only when prose happened to fill it.

    ! Three facts decide it, each stated by a producer and none inferred from
    the kind: a paragraph that DOCUMENTS a declaration takes that declaration's
    `a`, one with a COLUMN sits beside code and takes that line's `c`, and
    everything else holds a gap and takes the `b` for it.

    Args:
        paragraph: one census entry, as a dict.
        foliation: the walk over that paragraph's file.

    Returns:
        The folio, or "" when the paragraph states no position to tie it to.
    """
    declares = paragraph.get("declares", -1)
    if isinstance(declares, int) and declares >= 0:
        return foliation.documents(declares)
    # ! FRONT MATTER IS THE FILE'S, so it takes `f0` wherever it sits. Asking
    # `above()` would give it the gap it happens to occupy, which is the gap
    # that introduces the first statement and belongs to that statement.
    # !! THE LEXER SAYS SO, and this only reads it. Roy, 2026-08-21: *"that makes
    # f trivial and consistent because that paragraph instead of being marked as
    # comment and the page trying to reconstruct what was meant by top of the
    # file and a comment."* It was an ANNOTATION that `mark_matter` stamped here,
    # which is a positioning rule in a module that may hold none.
    #
    # ! WHICH `f` IS A COUNT, NOT A POSITION -- the Nth matter run takes the Nth
    # place the walk emitted, exactly as the Nth declaration takes the Nth `a`.
    # Counting is the PAGE's, so `page_for` hands them out and this says only
    # that the question is not `above()`'s to answer.
    if paragraph.get("kind") == MATTER:
        return ""
    if paragraph.get("original_column", 0):
        start = paragraph.get("start")
        return foliation.beside(start) if isinstance(start, int) else ""
    at = paragraph.get("original_start")
    return foliation.above(at) if isinstance(at, int) else ""


def documentable(
    decls: list[tuple[int, int, bool]], code: dict[int, str]
) -> dict[int, tuple[int, int, str]]:
    """Which code lines DECLARE something documentable, and WHERE the doc sits.

    !! IT CONVERTS; IT DECIDES NOTHING. The lexer states which side a
    language's documentation goes on, because the lexer is one of the two modules
    that touch a file at all. Roy, 2026-08-21: *"The language definition file has
    to state which, not the code"*, and *"the ONLY places that need this are the
    lexer and the compositor ... every other part of the program reads inputs and
    outputs to/from those modules."*

    ! TWO EARLIER VERSIONS PUT THE DECISION HERE, and both were wrong in the same
    way. One compared `insert <= line` and inferred the rule from an arithmetic
    on two line numbers; the next read `lang.doc_inside` in this module, which
    only moved the language out of the lexer. What is left is turning a LINE into
    a position in the walk's own sequence.

    !! THAT POSITION IS AN ORDINAL, which is the other half of the job. The walk
    counts code lines, so handing it a raw line made it compare `insert <= n` to
    place a docstring -- line arithmetic in the one module that must do none.
    Roy: *"how do I get you to stop thinking in line numbers?"*

    Args:
        decls: `(line, insert, above)` per declaration, module first -- see
            `lexer.declarations`, which states all three.
        code: the walk's triggers, `(line, anchor)` in order.

    Returns:
        `index into code -> (the LINE the doc occupies, the code index it is set
        at, WHICH SIDE of that index's gap)`. Three facts, and they were one
        field until 2026-08-21. The line is what `documented_by` walks up from to
        find prose already sitting there. The index and the side are what the
        walk places by: `ON` sets the doc between the gap and the code, `GAP`
        sets it before the gap -- which is where a doc that sits INSIDE its
        declaration lands, because the gap beneath it introduces whatever comes
        next. Empty for a tier that resolves no declarations, and the file then
        has an `a0` and no more.
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


def places_on(
    text: str, prose: list[dict], lang: "Language | None" = None
) -> "Foliation":
    """Every place on this page, walked.

    !! THE PAGE NAMES ITS OWN PLACES, which is what makes it a page rather than
    a list. It hands the walk its lines of code and which of them declare
    something documentable; the walk emits every place, filled or not, and
    `attach` says which one a given paragraph sits in.

    Args:
        text: the file's source.
        prose: its paragraphs, as dicts.
        lang: its record, so the declarations can be resolved HERE -- the
            keyword path scans the code lines, and this is where they are
            computed. None gives a page with no `a` series.

    Returns:
        The `Foliation` for this page.
    """
    code = code_lines(text, prose)
    decls = declarations(text, lang, code) if lang else []
    # !! `None`, NOT `1`, WHEN THERE ARE NO DECLARATIONS. A language with no
    # documentable declaration has no `a` series at all -- see `foliate`. It is
    # not a series that happens to be empty, and a YAML file carried an `a0`
    # until 2026-08-20 because the two were conflated.
    placed = documentable(decls, code) if lang else {}
    return foliate(code, placed, decls[0][1] if decls else None)


def empty_places(
    text: str, prose: list[Paragraph], foliation: Foliation, occupied: set[str]
) -> list[Paragraph]:
    """A paragraph for every place the walk emitted that no prose fills.

    !! ONE LOOP, WHERE THERE WERE FOUR GENERATORS -- `intervals`, `margins` and
    `paragraphs_in` here, and `lexer._undocumented` for the `a` series. Each
    walked the file again to decide which places of its own series deserved a
    paragraph: 198 lines answering one question four ways, and disagreeing.
    `intervals` skipped a gap a comment held, so once front matter took the
    file's first place nothing occupied the gap above the first line of code,
    and the place an `add` exists to cite was unreachable.

    ! The walk already emitted every place and said where each sits. This asks
    only which of them prose is sitting in, and gives the rest a paragraph.

    ! An empty place OCCUPIES NOTHING -- that is what `OCCUPIES_NOTHING` means,
    and it is why emitting one cannot move a code line or renumber anything
    below it.

    Args:
        text: the page's source.
        prose: the paragraphs a reader found.
        foliation: every place on the page.
        occupied: the folios that prose already sits in.

    Returns:
        The empty paragraphs, in no particular order -- the caller sorts.
    """
    lines = text.splitlines()
    last = len(lines)
    # ! WHICH LINES ARE ALREADY SPOKEN FOR IS NOT ASKED HERE ANY MORE.
    # `fill_the_gaps` runs after every paragraph exists and settles it once, for
    # every gap, against the neighbours each place actually has -- see the
    # `a`/`c`-exact rule there. Asking it twice is how the two answers came to
    # disagree.
    out: list[Paragraph] = []
    for folio, anchor in foliation.places.items():
        if folio in occupied:
            continue
        if folio.startswith(DECLARED):
            # ! A DECLARATION WITH NO DOCSTRING. It occupies NO LINE, because
            # the prose is not written yet -- given the declaration's own range
            # it swallowed whatever sat between the `def` and its first
            # statement.
            #
            # !! SO ITS ORIGINAL LINES ARE None, NOT `insert..insert-1`. Roy,
            # 2026-08-20: a closed list of lines, *"or it is None, meaning there
            # are currently no lines that have that foliation."* WHERE the prose
            # would go is `foliation.inserts[folio]` and was never this field's
            # to say -- an empty slice standing in for a position is what taught
            # a reader to take these numbers for one.
            out.append(
                Paragraph(
                    path="",
                    start=0,
                    end=0,
                    kind="undocumented",
                    lines=0,
                    text="",
                    anchor=anchor,
                    declares=int(folio[1:]),
                    original_start=None,
                    original_end=None,
                    address=folio,
                )
            )
        elif folio.startswith(ON):
            # ! The room BESIDE a line of code: whatever follows the statement,
            # which is nothing unless the line ends in whitespace. The code is
            # the ANCHOR, so storing it here too would put one fact in two
            # fields.
            n = foliation.lines[folio]
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
                    original_column=len(code) + 1,
                    anchor=anchor,
                    address=folio,
                )
            )
        elif folio.startswith(FRONT):
            # !! THE FILE'S OWN PROSE, AND IT HOLDS NO LINE WHEN IT IS EMPTY.
            # A licence header or a shebang goes at the very top, bounded by
            # nothing on either side -- so there is no gap to measure and
            # nothing to divide. ! Its own series since 2026-08-20; as a `b` it
            # took the `(0, 0)` branch of the gap arithmetic below, which is the
            # shape that let a gap re-cut it.
            #
            # !! `matter` NAMES THE SPACE AND NOT A POSITION, which is what the
            # `f` series needs: Roy, 2026-08-20, rejecting `head` -- *"what
            # happens if there is a tail? Many text documents have both."* A
            # licence at the BOTTOM of a file belongs to the file by the same
            # argument that moved front matter out of the `b` series, so the
            # kind must survive one. ! It borrows nothing: `matter` is already
            # the word in `front-matter`.
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
                    address=folio,
                )
            )
        elif not folio.startswith(GAP):
            # !! A SERIES THIS FUNCTION DOES NOT KNOW IS AN ERROR, NOT A SKIP.
            # Every place the walk emitted must get a paragraph; one that
            # falls off the end of these branches gets none, and a place with
            # no paragraph is uncitable and invisible. That is exactly how
            # `f0` behaved for its first hour. ! `census.py` turns a raise
            # here into a REPORTED per-file gap, which is loud; falling
            # through is silent.
            raise ValueError(
                f"no rule for the series of {folio!r} -- every series in"
                " `foliator.SERIES` needs a branch here"
            )
        else:
            previous, following = foliation.bounds[folio]
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
                    address=folio,
                )
            )
    return out


def tie_leading(paragraphs: list[Paragraph], foliation: Foliation) -> None:
    """Tie each run of leading to the PAIR of places it separates.

    !! LEADING IS AN EDGE. Every other series answers to a line of code and has
    a position in the walk's reading order; the space between two paragraphs
    answers to neither of them alone, so it is keyed by both -- `(f0, a0)` reads
    as *the space between the file's matter and the module's doc*. Roy,
    2026-08-21: *"make the pre-post foliation a dictionary look up for the d
    foliation and its associated paragraph."*

    ! WHICH IS WHY THE WALK DOES NOT EMIT ONE. `foliate` runs before any prose
    is read and leading exists only where the lexer found a blank run, so the
    walk cannot know a `d` is there. An edge needs no position in the walk's
    list, so it does not have to.

    ! AN EDGE AT THE FILE'S OWN EDGE HAS ONE END. A blank run above everything
    or below everything is tied with `""` for the missing side, which is a real
    answer: there is no place on that side to separate from.

    Args:
        paragraphs: every paragraph on the page, addressed.
        foliation: the walk's places; `leading` is filled here.
    """
    # ! The places that HOLD LINES, in the order they hold them -- the sequence
    # a run of leading falls between. Read from the original text, which is what
    # this pass is entitled to: it is establishing the edges ONCE, at build.
    set_places = sorted(
        (b for b in paragraphs if b.original_start and b.kind != LEADING),
        key=lambda b: b.original_start or 0,
    )
    for b in sorted(paragraphs, key=lambda b: b.original_start or 0):
        if b.kind != LEADING or not b.address:
            continue
        start = b.original_start or 0
        end = b.original_end or start
        before = ""
        after = ""
        for other in set_places:
            if (other.original_end or 0) < start:
                before = other.address.split("@")[-1]
            elif (other.original_start or 0) > end:
                after = other.address.split("@")[-1]
                break
        foliation.leading[(before, after)] = b.address.split("@")[-1]


def page_for(path: Path, text: str, lang: Language, rel: str | None = None) -> Page:
    """The census for one file, at the highest tier available for its language.

    The ladder is by QUESTION ANSWERED. Python reaches TOKENIZED through the
    stdlib, which buys docstring anchors; every other language has the LEXICAL
    floor.

    !! IT RETURNS A COMPLETE CENSUS -- addressed and anchored. Both used to be
    stamped in two different places: anchors here, addresses in the run loop,
    so a caller that used this function directly got half a census and no
    error. Every test of the census does exactly that.

    Args:
        path: the file, used for its suffix and as the address's path.
        text: its contents.
        lang: the language record for its suffix.
        rel: the path as the REPO sees it, when a caller has one. It is what
            every citation resolves against; `path` stands in when a caller has
            no repo, which is what the tests are.
    """
    if lang.name == "python":
        got = paragraphs_stdlib(path, text)
    else:
        got = paragraphs_lexical(path, text, lang)
        flag_structural_docs(got, text, lang)
    # ! A file the parser refused is NOT enumerated into intervals. Its one
    # `unparsed` paragraph reports the refusal, and the code lines below it were
    # never established, so any interval drawn there would be invented.
    # !! THE SPACE BETWEEN PARAGRAPHS, FOR WHICHEVER READER RAN. It is a pass
    # rather than a branch inside each, so the two cannot disagree about it --
    # which is what happened to `matter` when it was written on one tier.
    got.extend(leading_between(got, text))
    foliation = Foliation()
    if not any(b.kind == "unparsed" for b in got):
        # !! THE WALK EMITS EVERY PLACE, AND THE PARAGRAPHS ARE TIED TO THEM.
        # Reversed -- each paragraph computing its own folio -- a place existed
        # only when prose happened to fill it, which is how the file's own
        # matter and the first gap came to be mutually exclusive -- one address
        # for two places. `foliator` owns both halves: the foliation
        # assigns the numbering, `attach` reads which place this prose sits in,
        # and the anchor comes from the walk that emitted it rather than from a
        # second pass that could disagree with the first.
        foliation = places_on(text, [vars(b) for b in got], lang)
        # !! THE LEXER STATES WHICH PROSE DOCUMENTS WHAT, and this only asks.
        # It was decided in this module until 2026-08-21, which may hold no
        # positioning rule -- Roy: *"the ONLY places that need this are the lexer
        # and the compositor."* `paragraphs_stdlib` has always stated it for
        # Python from its parse; `document_declarations` is the same fact for a
        # language the parser cannot read, and answers nothing for Python.
        code = code_lines(text, [vars(b) for b in got])
        document_declarations(got, declarations(text, lang, code), code)
        flat = flatten(rel if rel is not None else path.as_posix())
        # !! THE PAGE MAKES THE MAPPING. Roy, 2026-08-21: *"the page makes the
        # mapping between foliator and paragraph."* The lexer types a run
        # `matter` and the walk emits the places a file has for its own prose;
        # neither counts, so the Nth matter run takes the Nth place here --
        # which is what makes `f0` the head and `f1` the foot without either
        # word appearing anywhere.
        files = foliation.file_places()
        # ! THE `d` SERIES IS NUMBERED HERE AND NOWHERE ELSE. The walk emits no
        # `d`, because nothing cites one and a place exists unfilled only so a
        # verdict can name it -- see `foliator.LEAD`. So leading is numbered in
        # the order it occurs, which is the order the lexer found it.
        leads = iter(range(10**9))
        for b in sorted(got, key=lambda b: b.original_start or 0):
            if b.kind == LEADING:
                place = f"{LEAD}{next(leads)}"
                foliation.places[place] = ""
            elif b.kind == MATTER:
                # ! HEAD OR FOOT, which is the whole of the mapping. The lexer
                # types a run `matter` when it opens the file or closes it; the
                # walk emits a place for each end; this says which is which, and
                # it is the only comparison either side needs.
                place = files[0] if b.original_start == 1 else files[-1]
            else:
                place = attach(vars(b), foliation)
            b.address = f"{flat}@{place}" if place else ""
            b.anchor = foliation.places.get(place, b.anchor)
        # !! EVERY PLACE PROSE DOES NOT FILL GETS A PARAGRAPH, in one loop over
        # what the walk emitted. Three generators used to answer this one
        # question a series at a time, each walking the file again.
        occupied = {b.address.split("@")[-1] for b in got if "@" in b.address}
        for empty in empty_places(text, got, foliation, occupied):
            # ! IT ALREADY KNOWS ITS PLACE -- the emitter filled that folio and
            # said so. Asking `attach` again re-derives it from position, which
            # answered the FIRST GAP for the file's own matter: the two are
            # different places at the same position, and position cannot tell
            # them apart. That is the whole defect, one layer up.
            empty.address = f"{flat}@{empty.address}"
            got.append(empty)
        # !! ONE PASS FOR `anchor_line`, OVER EVERYTHING. Stamped per branch it
        # was filled on the prose and on ONE of the four empty kinds, so every
        # `interval` and every `margin` read 0 -- the same shape as a series
        # list that names its members: a branch that forgets is silent.
        for b in got:
            folio = b.address.split("@")[-1]
            b.anchor_line = foliation.anchor_line(folio) if folio else 0
        # ! AFTER every paragraph exists, so each one's share of its gap is
        # settled against the neighbours it actually has.
        fill_the_gaps(text, got)
        # !! THE READING ORDER IS THE WALK'S, AND THIS MODULE DOES NOT BUILD ONE.
        # `foliate` emits every place in sequence and says so at the field --
        # *"a fact the walk knows rather than an arithmetic over line numbers"* --
        # including WHERE AN `a` FALLS, which is the language's call and is
        # settled there once.
        #
        # !! IT WAS OVERWRITTEN HERE UNTIL 2026-08-21, by a sort on
        # `original_start` filtered to paragraphs that hold a line. Two comments
        # in two modules then stated opposite rules for one field and the later
        # write won. What it cost: a place holding no prose has no line, so it
        # fell out of the order, and `compositor.set_page` -- which walks this
        # list -- could not emit one. An `add` names exactly such a place, so its
        # approved text was DISCARDED IN SILENCE: no error, and a page identical
        # to the one before the edit. Roy: *"how do I get you to stop thinking in
        # line numbers?"*
        #
        # ! SO LEADING IS TIED TO THE PAIR IT SEPARATES, not inserted into the
        # sequence -- see `Foliation.leading`. The walk cannot emit a `d`,
        # because it runs before any prose is read and leading exists only where
        # the lexer found a blank run; an edge needs no position in the walk's
        # list, so the walk does not have to know.
        tie_leading(got, foliation)
    # ! THE PAGE STATES ITS OWN PATH on every paragraph, empty places included.
    # `empty_places` builds them without one -- it is handed the text, not the
    # file -- and a paragraph with no path is one no consumer can place.
    where = rel if rel is not None else path.as_posix()
    for b in got:
        b.path = where
        b.tier = tier_for(lang)
    # ! An UNPARSED file never reached the walk, so it has no foliation. An empty
    # one is the honest answer: the page carries no places, and a consumer that
    # asks gets nothing rather than a table built over code lines that were
    # never established.
    return Page(
        path=rel if rel is not None else path.as_posix(),
        text=text,
        paragraphs=sorted(got, key=lambda b: (b.start, b.end)),
        foliation=foliation,
        tier=tier_for(lang),
    )


# The two shapes that earn FRONT MATTER without a module docstring to sit above:
# a shebang says how the file RUNS and a coding line how it is READ, and both are
# the file's own whatever follows them.
_SHEBANG = re.compile(r"^#!")
_CODING = re.compile(r"coding[:=]\s*[-\w.]+")


def fill_the_gaps(text: str, paragraphs: list[Paragraph]) -> None:
    """Give every line of a gap to the paragraph it belongs to, blanks included.

    !! EVERY LINE HAS AN ADDRESS. Ruled 2026-08-19. A prose paragraph was addressed
    by the lines its prose occupied, so a blank line beside it belonged to
    nothing -- 81 lines of this repo, every one at the edge of a gap, and a
    a reviewer asking which place held one got no answer at all.

    ! A paragraph runs to the next paragraph, or to the end of its gap. Leading blanks
    go to the first paragraph in the gap and trailing blanks to the last, which is
    the same rule read from either end.

    !! IT MOVES THE ORIGINAL RANGE WITH IT, since 2026-08-20, and `raw_lines`
    with that. Roy: *"the original lines need to be marked as `b`s because it
    has this flexibility that the others do not."* The two ranges disagreeing
    left 105 blank lines -- 16 of 16 shipped scripts -- addressed by a paragraph
    and covered by none, so the invariant held on one range and not the other.

    ! THE OBJECTION IT OVERRIDES, kept because it is real: widening the original
    range lets a `change` swallow the blank line that separates a comment run
    from the code beneath it. Roy's answer is a galley rule -- *"strips empty
    lines at the ends of `b`s and then puts one back in to make the spacing
    nice"* -- which is why the lines must be MARKED even though writing them
    verbatim would be wrong.

    !! AN `a` IS NOT WIDENED. A declaration's documentation has none of that
    flexibility: its lines are the docstring's and a blank beside it belongs to
    the gap. 25 of the 105 were going to an `a` because this extended whichever
    paragraph opened the gap.
    """
    source = text.splitlines()
    code = list(code_lines(text, [vars(b) for b in paragraphs]))
    last = len(source)
    edges = [0, *code, last + 1]

    # !! EVERY OTHER SERIES OWNS ITS LINES EXACTLY, AND `b` TAKES WHAT IS LEFT.
    # Roy, 2026-08-20: *"a's and c's own their lines exactly, b's own all the
    # other lines."*
    #
    # ! `f` IS IN THAT LIST BECAUSE IT IS A SERIES, not because it is front
    # matter. While front matter was `b0` this needed a clause naming it -- the
    # one paragraph whose folio disagreed with the gap it sat in -- and the
    # clause was missing. Measured over 662 corpus files: 51 paragraphs where a
    # licence header was reported as an `interval`. Roy: *"we should have just
    # made the front matter its own foliation; then the rule that `b` owns all
    # the lines that are not another foliation's lines would explicitly stay
    # true."*
    exact: set[int] = set()
    for b in paragraphs:
        series = b.address.split("@")[-1][:1]
        if series and series != GAP and b.original_start:
            exact.update(range(b.original_start, b.original_end + 1))

    def recut(b: Paragraph, mine: set[int] | None = None) -> None:
        """Give this paragraph its share of the gap, on both ranges.

        !! A `b` TAKES THE FREE LINES AND ONLY THOSE. Roy, 2026-08-21, ruling on
        a blank line above front matter: *"b owns the blank line -- same answer
        as the blanks around a's and c's for the same reason. it is the flex in
        the system. it makes the covering precise and full."* ! The span was
        sliced whole, so a `b` whose free lines are not contiguous took the
        paragraph sitting inside it as well: `cpython/Include/floatobject.h`
        opens with a BLANK, `f0` holds line 2, and `b0` held 1-7 -- the comment
        set twice.
        """
        if b.end >= b.start >= 1:
            b.original_start, b.original_end = b.start, b.end
            # ! `raw_lines` is what `compositor.transcribes` compares against
            # the file, over exactly this range. Leaving it as the prose alone
            # made a FRESH census read as stale on every widened paragraph.
            own = [n for n in range(b.start, b.end + 1) if mine is None or n in mine]
            b.raw_lines = [source[n - 1] for n in own]
        else:
            # ! NO LINE CARRIES THIS FOLIATION, and that is the whole
            # answer. Where prose would GO is not recorded: Roy,
            # 2026-08-20, on dropping the tool that asked -- *"which
            # lines to edit is no longer helpful"*. A record names the
            # PLACE and says what changes in it.
            b.original_start = b.original_end = None
            b.raw_lines = []

    for prev, nxt in pairwise(edges):
        lo, hi = prev + 1, min(nxt - 1, last)
        if lo > hi:
            continue
        free = [n for n in range(lo, hi + 1) if n not in exact]
        # ! ONLY THE `b`s SHARE IT. An `a` in this gap keeps the lines it has --
        # it has none of the flexibility a `b` has, and extending whichever
        # paragraph opened the gap handed 25 blank lines in this repo to a
        # module docstring.
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
            # how the original lines do -- there is no line with this foliation.
            for b in here:
                b.start, b.end = 0, 0
                recut(b)
            continue
        here[0].start = free[0]
        for a, nxt_block in zip(here, here[1:], strict=False):
            a.end = nxt_block.start - 1
        here[-1].end = free[-1]
        owned = set(free)
        for b in here:
            recut(b, owned)
