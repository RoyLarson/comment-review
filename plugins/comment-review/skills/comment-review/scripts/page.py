"""A PAGE: one file, its paragraphs in order among the code they sit with.

`page_for()` builds one. Every line of the file is classified -- this line is
code, this PART of a line is code, this line is comment, this line is docstring
-- and each line belongs to a PARAGRAPH, which is one unit of prose or the empty
place where prose could go.

!! A PAGE NAMES ITS OWN PLACES, which is what makes it a page and not a list.
`places_on` hands the walk its lines of code and which of them declare something
documentable; `foliator` emits every place, filled or not, and `attach` says
which one a given paragraph sits in. A paragraph does not compute its own folio
-- reversed, a place existed only when prose happened to fill it, and `b0` and
`b1` were mutually exclusive.

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
PARAGRAPH: `code_lines_of` and `attach` were the only two functions of it that
did, and both are page questions wearing an addressing name.

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
    GAP,
    ON,
    Foliation,
    flatten,
    foliate,
)
from lexer import (  # noqa: E402  -- path shim must run first
    Language,
    Paragraph,
    declarations,
    flag_structural_docs,
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
#
# !! KINDS THAT OCCUPY NO LINES OF THEIR OWN. A `trailing-comment` sits on a
# code line, and an `interval` and an `undocumented` declaration are both
# EMPTY -- a place where prose could go and does not. Counting any of them as
# occupied would drop a real code line from the count and renumber every `b`
# below it.
OCCUPIES_NOTHING = ("trailing-comment", "margin", "interval", "undocumented")
# !! HOLDS NO PROSE -- a DIFFERENT set, and the two are not interchangeable. A
# `trailing-comment` occupies no lines of its own but is prose; an `interval`
# and an `undocumented` declaration are places where prose could go and does
# not. This set is what "addressable, not accountable" means: they are cited by
# an `add` and they get no seeded record.
HOLDS_NO_PROSE = ("interval", "undocumented", "margin")

# !! THE FILE'S OWN PROSE, ABOVE ITS DOCSTRING -- a licence header, a shebang, a
# coding line. It is an ANNOTATION rather than a kind, because such a run is an
# ordinary comment in every way but ownership: it belongs to the FILE and not to
# whatever follows it.
#
# ! IT LIVES HERE BECAUSE THE PAGE BOTH STAMPS AND READS IT. `mark_front_matter`
# says which runs are the file's own; `attach` gives them `b0` wherever they sit,
# rather than the gap they happen to occupy.
FRONT_MATTER = "front-matter"


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
        """
        return [
            b
            for b in self.paragraphs
            if b.kind not in HOLDS_NO_PROSE and FRONT_MATTER not in b.annotations
        ]


def code_lines_of(text: str, paragraphs: list[dict]) -> list[int]:
    """Which lines of this file are LINES OF CODE, at the tier the census ran.

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

    !! THE PARAGRAPH SAYS SO, via `edit_column`. This tested whether the stored
    text was a proper SUFFIX of the physical line, which is an inference and
    was wrong in both directions: `paragraphs_stdlib` stores the WHOLE line for a
    trailing comment, so the test never fired for one -- and a paragraph comment
    opened after a statement had its declaration line dropped from the code
    set, moving every interval boundary in the file. Measured 2026-08-18.

    ! It takes DICTS, so it reads a census off disk and a census still being
    built alike -- `code_lines` is this function over its own `Paragraph`s.
    An address counts code lines, so the count has to be the same one the
    census used or the two disagree about what `@b3` means.
    """
    occupied: set[int] = set()
    for b in paragraphs:
        if b.get("kind") in OCCUPIES_NOTHING:
            continue
        start, end = b.get("start"), b.get("end")
        if not isinstance(start, int) or not isinstance(end, int):
            continue
        occupied.update(range(start, end + 1))
        if b.get("edit_column", 0):
            occupied.discard(start)
    return [
        n
        for n, line in enumerate(text.splitlines(), 1)
        if line.strip() and n not in occupied
    ]


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
    # ! FRONT MATTER IS THE FILE'S, so it takes `b0` wherever it sits. Asking
    # `above()` would give it the gap it happens to occupy, which is the gap
    # that introduces the first statement and belongs to that statement.
    if FRONT_MATTER in (paragraph.get("annotations") or ()):
        return foliation.front_matter()
    if paragraph.get("edit_column", 0):
        start = paragraph.get("start")
        return foliation.beside(start) if isinstance(start, int) else ""
    at = paragraph.get("edit_start")
    return foliation.above(at) if isinstance(at, int) else ""


def lines_of_code(text: str, prose: list[dict]) -> list[tuple[int, str]]:
    """The file's lines of code, in order, each with the line it sits on.

    ! What the WALK is given. The line positions the trigger and never numbers
    it -- see `foliator.foliate`.

    !! THE CHARACTERS COME FROM THAT LINE'S `c`, NEVER RE-CUT HERE. Every code
    line has exactly one `c` -- a `trailing-comment`, or the `margin` standing
    in for one -- and it already states where the code stops. Cutting the line
    again answers `'    return os  # why'` where the `c` for the same line
    answers `'    return os'`: two computations of one fact, which is what
    `whole_lines` was removed for.
    """
    lines = text.splitlines()
    beside = {
        b.get("start"): b.get("anchor", "") for b in prose if b.get("edit_column")
    }
    return [
        (n, beside.get(n) or lines[n - 1].rstrip())
        for n in code_lines_of(text, prose)
        if 1 <= n <= len(lines)
    ]


def documentable(
    decls: list[tuple[int, int]], code: list[tuple[int, str]]
) -> dict[int, int]:
    """Which code lines DECLARE something documentable, and where its doc goes.

    ! The lexer states both facts -- see `lexer.declarations`. This only turns a
    LINE into an index into the walk's own trigger list, because that is what
    the walk counts by.

    Args:
        decls: `(line, insert)` per declaration, module first.
        code: the walk's triggers, `(line, anchor)` in order.

    Returns:
        `index into code -> the line that declaration's doc would go on`. Empty
        for a tier that resolves no declarations, and the file then has an `a0`
        and no more.
    """
    at = {n: i for i, (n, _) in enumerate(code)}
    return {at[line]: insert for line, insert in decls[1:] if line in at}


def places_on(
    text: str, prose: list[dict], decls: list[tuple[int, int]] | None = None
) -> "Foliation":
    """Every place on this page, walked.

    !! THE PAGE NAMES ITS OWN PLACES, which is what makes it a page rather than
    a list. It hands the walk its lines of code and which of them declare
    something documentable; the walk emits every place, filled or not, and
    `attach` says which one a given paragraph sits in.

    Args:
        text: the file's source.
        prose: its paragraphs, as dicts.
        decls: `(line, insert)` per documentable declaration, module first --
            `lexer.declarations`. Empty for a tier that resolves none, and the
            page then has an `a0` and no more.

    Returns:
        The `Foliation` for this page.
    """
    decls = decls or []
    code = lines_of_code(text, prose)
    # ! The MODULE's own doc place. A tier that resolves no declarations
    # still has an `a0`, and its prose would open the file.
    return foliate(code, documentable(decls, code), decls[0][1] if decls else 1)


def code_lines(text: str, prose: list[Paragraph]) -> set[int]:
    """The code lines of this file, as a set -- `foliation.code_lines_of`.

    !! ONE IMPLEMENTATION, and it is the foliation's, because an address is
    counted off this set and the two must not be able to disagree. This is the
    same rule over `Paragraph`s rather than dicts; the rule itself is written where
    it runs.
    """
    return set(code_lines_of(text, [vars(b) for b in prose]))


def empty_places(
    text: str, prose: list[Paragraph], foliation: Foliation, occupied: set[str]
) -> list[Paragraph]:
    """A paragraph for every place the walk emitted that no prose fills.

    !! ONE LOOP, WHERE THERE WERE THREE GENERATORS. `intervals`, `margins` and
    `_undocumented` each walked the file again to decide which places of their
    own series deserved a paragraph -- 206 lines answering one question three
    ways, and disagreeing. `intervals` skipped a gap a comment held, so once
    front matter took `b0` nothing occupied `b1` and the place an `add` exists
    to cite was unreachable.

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
    # !! EVERY LINE PROSE OCCUPIES, not just the line it starts on. A comment
    # opened after a statement SPANS from that line -- `let b = 2; /* opens` and
    # `and closes */` is one paragraph over two lines -- so a start-only test
    # left the gap below it looking empty and gave line 3 a second address.
    # `paragraphs_in` tested OVERLAP for exactly this reason.
    filled = {n for b in prose if b.start for n in range(b.start, b.end + 1)}
    out: list[Paragraph] = []
    for folio, anchor in foliation.places.items():
        if folio in occupied:
            continue
        if folio.startswith(DECLARED):
            # ! A DECLARATION WITH NO DOCSTRING. It occupies no line, because
            # the prose is not written yet -- given the declaration's own range
            # it swallowed whatever sat between the `def` and its first
            # statement. Its EDIT range still says where the prose would go, and
            # `insert..insert-1` is an empty slice, so writing it INSERTS.
            insert = foliation.inserts.get(folio, 1)
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
                    declared_at=foliation.lines.get(folio, 0),
                    edit_start=insert,
                    edit_end=insert - 1,
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
                    edit_start=n,
                    edit_end=n,
                    edit_column=len(code) + 1,
                    anchor=anchor,
                    address=folio,
                )
            )
        elif folio.startswith(GAP):
            previous, following = foliation.bounds[folio]
            if (previous, following) == (0, 0):
                # !! THE FILE'S OWN FRONT MATTER, and it is bounded by nothing:
                # a licence header or a shebang goes at the very top. `1..0` is
                # an empty slice, so writing it INSERTS rather than replaces.
                low, high = 1, 0
            else:
                low = previous + 1
                high = following - 1 if following else last
            # !! A DOCSTRING IN THIS GAP MAKES THE EDIT AN INSERTION ABOVE IT.
            # The gap's lines are the docstring's, so writing the whole range
            # would overwrite a docstring with a comment.
            if any(low <= n <= high for n in filled):
                high = low - 1
            out.append(
                Paragraph(
                    path="",
                    start=low if low <= high else 0,
                    end=high if low <= high else 0,
                    kind="interval",
                    lines=0,
                    text="",
                    edit_start=low,
                    edit_end=high,
                    anchor=anchor,
                    address=folio,
                )
            )
    return out


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
    foliation = Foliation()
    if not any(b.kind == "unparsed" for b in got):
        # ! BEFORE the walk, because a run that is FRONT MATTER takes `b0` and
        # this is what says which runs those are.
        mark_front_matter(got)
        # !! THE WALK EMITS EVERY PLACE, AND THE PARAGRAPHS ARE TIED TO THEM.
        # Reversed -- each paragraph computing its own folio -- a place existed
        # only when prose happened to fill it, which is how `b0` and `b1` came
        # to be mutually exclusive. `foliator` owns both halves: the foliation
        # assigns the numbering, `attach` reads which place this prose sits in,
        # and the anchor comes from the walk that emitted it rather than from a
        # second pass that could disagree with the first.
        foliation = places_on(text, [vars(b) for b in got], declarations(text, lang))
        flat = flatten(rel if rel is not None else path.as_posix())
        for b in got:
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
            # answered `b1` for the `b0` paragraph: the front-matter place is
            # not the gap above the first line of code, and position cannot
            # tell them apart. That is the whole defect, one layer up.
            empty.address = f"{flat}@{empty.address}"
            got.append(empty)
        # ! AFTER every paragraph exists, so each one's share of its gap is
        # settled against the neighbours it actually has.
        fill_the_gaps(text, got)
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


def mark_front_matter(paragraphs: list[Paragraph]) -> None:
    """Stamp the prose that sits ABOVE a module's own docstring.

    !! WHAT IT IS. A licence header, a shebang, a coding declaration -- the
    matter a file carries before it begins. Measured 2026-08-19 over 1,500 files
    in five corpora: 12 carried prose above the module docstring, and 10 of the
    12 were the Apache header repeated identically in every file of the project.
    Inside a declaration it never happens -- 0 of 2,579 docstrings.

    !! WHY IT IS FILTERED OUT OF WHAT A REVIEWER READS. It is not a claim about
    the code, so no role can settle it:

      block-context     has nothing to resolve the claim against -- a copyright
                        line states no constraint the code could contradict
      function-context  it documents no function
      module-context    it is not the module announcing its subject
      ownership-context it belongs where it is, by law or by convention, and
                        that is not a placement this system may rule on

    ! So every role would return `clean` on it, every run, on prose that is
    identical in every file of the project -- a cost paid per file per role for
    an answer that was settled before the run started.

    !! AND IT IS THE ONE PLACE A WRONG EDIT IS EXPENSIVE OUTSIDE THIS SYSTEM.
    A licence header is a legal instrument and a shebang is how the file runs;
    both are the human's to change and neither is an editorial question. A
    finding here is therefore turned into a `query` -- ask -- rather than
    admitted as work. `verdicts.py` does that; this only says which paragraph.

    ! The rule is POSITIONAL and deliberately narrow: prose in the gap before
    the first code line, sitting above a module docstring that EXISTS -- or
    opening with a shebang or a coding declaration, which need no docstring to
    be recognisable. A leading comment in a file with no module docstring is
    about whatever follows it, and is reviewed like any other.
    """
    doc = next(
        (b for b in paragraphs if b.kind == "docstring" and b.declares == 0),
        None,
    )
    for b in paragraphs:
        if b.kind not in ("comment", "trailing-comment") or b.start < 1:
            continue
        opens = (b.raw_lines or [""])[0].strip()
        if _SHEBANG.match(opens) or _CODING.search(opens):
            b.annotations.add(FRONT_MATTER)
        elif doc is not None and b.end < doc.start:
            b.annotations.add(FRONT_MATTER)


def fill_the_gaps(text: str, paragraphs: list[Paragraph]) -> None:
    """Give every line of a gap to the paragraph it belongs to, blanks included.

    !! EVERY LINE HAS AN ADDRESS. Ruled 2026-08-19. A prose paragraph was addressed
    by the lines its prose occupied, so a blank line beside it belonged to
    nothing -- 81 lines of this repo, every one at the edge of a gap, and a
    reviewer asking the locator about one got "no entry holds this line".

    ! A paragraph runs to the next paragraph, or to the end of its gap. Leading blanks
    go to the first paragraph in the gap and trailing blanks to the last, which is
    the same rule read from either end.

    ! It moves the ADDRESSING range only. `edit_start`/`edit_end` were fixed at
    construction and still name the prose, so WRITE replaces what it replaced
    before -- widening those would let a `change` swallow the blank line that
    separates a comment run from the code beneath it.
    """
    code = sorted(code_lines(text, paragraphs))
    last = len(text.splitlines())
    edges = [0, *code, last + 1]
    for prev, nxt in pairwise(edges):
        lo, hi = prev + 1, min(nxt - 1, last)
        if lo > hi:
            continue
        here = sorted(
            (b for b in paragraphs if b.start >= 1 and lo <= b.start <= hi),
            key=lambda b: b.start,
        )
        if not here:
            continue
        here[0].start = lo
        for a, nxt_block in zip(here, here[1:], strict=False):
            a.end = nxt_block.start - 1
        here[-1].end = hi
