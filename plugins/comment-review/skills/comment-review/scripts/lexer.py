"""How each LANGUAGE marks its prose, and the paragraph a reader produces.

Adding a language is a `Language` row -- data, not code. Two readers consume it,
at the tier that language reaches:

  tokenized  a lexer + AST (Python, from the stdlib)   + which declaration a
                                                         docstring documents
  lexical    a comment-syntax record, nothing else     the prose and its kind

!! IT DEFINES WHAT IT PRODUCES, which is why `Paragraph` lives here. A reader
builds one the moment it finds prose, and it knows only what the TEXT says --
where the prose starts and ends, what kind it is, the code beside it. Where that
paragraph SITS is the page's: the path it is on, the place it occupies, and the
empty places where prose could go and does not.

! So the kinds split too, and NOTHING HERE EMITS A PAGE KIND. A reader emits
`comment`, `docstring`, `trailing-comment` and `unparsed` -- prose it found.
`interval`, `margin` and `undocumented` are the page's, because only a page
knows where prose is MISSING. ! What this reports instead is
`declarations()`: which lines declare something documentable, and where its
doc would go. The page turns that into `a` places.

! A LEAF: it imports no sibling. `foliator` is the other one, and neither knows
anything of the other -- a place has no prose in it and prose has no place until
a page puts the two together.
"""

import ast
import io
import re
import sys
import tokenize
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# !! THE ROWS ARE A LEAF AND THIS IS ONE OF ITS TWO IMPORTERS -- see
# `language.py`. Everything a language says about where its documentation sits is
# stated there and read here; no module above this one asks a language anything.
from language import (  # noqa: E402  -- path shim must run first
    BY_EXT,
    LANGUAGES,
    TIER_ANSWERS,
    Language,
    language_for,
    tier_for,
)

__all__ = [
    "BY_EXT",
    "LANGUAGES",
    "TIER_ANSWERS",
    "Language",
    "language_for",
    "tier_for",
]


@dataclass
class Paragraph:
    """The interval between two lines of code -- the unit a reviewer rules on.

    ! An interval holding no prose is a paragraph too, `kind="interval"`. It is the
    only thing an `add` can cite: the finding is that a constraint exists in
    code and NOWHERE in prose, so it is about an empty interval, and the record
    requires a `BLOCK` index. Without one an `add` had to borrow a neighbour's.
    """

    path: str
    start: int
    end: int
    kind: str  # comment | docstring | trailing-comment | interval | undocumented
    lines: int
    text: str  # the run JOINED, so a wrapped claim matches as one string
    # !! WHAT THIS PARAGRAPH IS ATTACHED TO, and it is ONE-TO-MANY THE OTHER WAY:
    # an anchor has MANY addresses -- its own `a`, the `b` above it, the `c`
    # beside it, every `b` and `c` in its body -- and an address has ONE anchor.
    #
    # !! IT IS ALWAYS THE LINE OF CODE, VERBATIM -- never a name, and never a
    # symbol. Roy: *"the anchor isn't the technical symbols and their precise
    # semantic meaning and code use. It is 'the line of code' -- the exact
    # characters in that line of code."* An `a` carries the line that DECLARES
    # it, `def f():` and not `f`; see `_anchor_of`.
    anchor: str = ""
    # !! WHICH DECLARATION THIS DOCUMENTS, as an ordinal: 0 is the module and
    # 1..N its declarations in SOURCE order. -1 says this paragraph documents no
    # declaration -- every comment and every interval.
    #
    # !! STATED HERE BECAUSE ONLY A PARSER KNOWS IT. Python's docstring sits
    # AFTER its `def` and Rust's `///` sits BEFORE its `fn`, so position cannot
    # answer which declaration a doc belongs to and the foliation must not
    # guess. It reads this and names it `@aN`.
    declares: int = -1
    # !! THE LINE THIS PLACE'S ANCHOR SITS ON, so an anchor's OTHER places can
    # be found: the `c` beside its `def`, the `b` above it, its own `a`.
    # Without it a consumer has to infer the line from the prose's position,
    # which is exactly the inference that breaks on the next language --
    # Rust's doc sits BEFORE its `fn` and Python's after.
    #
    # !! IT WAS `declared_at` AND FILLED FOR `a` ALONE, which is why
    # `for_anchor` could only fall back to it with a declaration in hand. The
    # fact was never about declaring: it is the anchor's line, and every
    # series has one. Renamed and filled for all of them 2026-08-20.
    #
    # !! `None` WHERE THE ANCHOR IS A SENTINEL -- `<module>` at the head of the
    # walk, `<eof>` at its foot. Neither sits on a line, and this says so
    # rather than answering 0.
    #
    # ! IT WAS 0 FOR BOTH until 2026-08-22, and the two were not the same fact.
    # Line 0 is genuinely above line 1, so the head sorted first and rendered at
    # the top and both were correct; the foot inherited those behaviours and
    # both were wrong. Roy: *"the end of file getting a 0 is non-functional
    # filling in for a missing value."*
    anchor_line: int | None = None
    # !! THE ORDINAL OF THAT ANCHOR AMONG THE LINES OF CODE, and it is what
    # ORDERS a record now. Roy, 2026-08-21: *"where it is in the original and
    # where it ends up on the resulting page can be two very different things --
    # but a single shift on anchor_num and you know it is all trash after
    # rereading."* This tool edits prose and every prose edit moves the lines
    # below it; the Nth line of code stays the Nth line of code.
    #
    # ! CARRIED ALONGSIDE `anchor`, never instead of it. An ordinal cannot see a
    # rename in place and the text cannot cheaply see an insertion; the pair
    # sees both, which is the whole drift question in two fields.
    anchor_num: int = 0
    tier: str = "lexical"  # which question set this file's census can answer
    # !! WHICH PLACE THIS IS, as against where it sits -- see `foliation.address`.
    # Stamped in the path-normalising loop, the only place holding the file
    # text, the finished paragraph list and the repo-relative path at once.
    address: str = ""
    # !! A LABEL, NOT AN ADDRESS, and only LEADING carries one. Roy, 2026-08-22:
    # *"we need to keep the symbol for the leading, because the page/symbol map
    # has really helped in understanding what each line is, so that we maintain
    # the cover."* `d0` marks a run of blank lines in `scripts/render_page.py`'s
    # margin, so a reader can see that every line on the page belongs to
    # something.
    #
    # !! IT IS NOT AN `address` BECAUSE LEADING IS NOT A PLACE, and putting it
    # in that field is what made `d` fail the substitution the other four series
    # satisfy. Roy: *"it has no anchor, and so by the LSR -- any child class has
    # to be able to answer its parent class's answers as well, correctly -- it
    # breaks that rule."* MEASURED: `a0` and every `f` answer `<module>` and
    # every `b` and `c` answer a line of code; a `d` answered `""`, which is the
    # absence of an answer rather than a different one.
    #
    # ! WHICH FOLLOWS FROM WHERE IT COMES FROM. Every other place exists because
    # the WALK reached a trigger -- and the trigger IS the anchor. A `d` exists
    # because the LEXER found blank lines, so there was never a trigger for it
    # to be anchored to. `foliator.SERIES` holds four series; `LEAD` is a symbol.
    symbol: str = ""
    annotations: set[str] = field(default_factory=set)
    notes: list[str] = field(default_factory=list)

    # !! THE PARAGRAPH'S OWN CHARACTERS, EXACTLY AS THE FILE HOLDS THEM -- its
    # lines whole where it owns them, and from `original_column` onward on the first
    # line where code comes first. With `anchor` holding the code, the two
    # RECONSTRUCT that line: `anchor + raw_lines[0]` is what is on disk.
    #
    # !! THE TWO TIERS DISAGREED, AND FOUR OF SIX SHAPES COULD NOT BE WRITTEN.
    # `paragraphs_lexical` cut at the comment opener and `paragraphs_stdlib` kept the
    # whole physical line, so the retired `paragraph_matches` refused a FRESH census on
    # every lexical trailing comment (`'// note'` against `int b = 2; // note`)
    # and on every paragraph comment not at column 0 (`'/* why */'` against
    # `'    /* why */'` -- the indentation was the cut). Measured 2026-08-19.
    #
    # ! It also fed CODE to the annotators. `prose_numbers` reads this, so a
    # Python `TIMEOUT = 30  # the note says nothing` reported the number 30 as a
    # claim the prose makes. The lexical tier's own comment says that defect was
    # fixed; it was fixed on one tier.
    raw_lines: list[str] = field(default_factory=list)
    # !! THE LINES THIS PARAGRAPH COVERS IN THE FILE AS IT READS NOW. That is
    # the whole definition, and it is NOT always the range that ADDRESSES the
    # paragraph. A prose paragraph is replaced, so the two coincide. An empty
    # INTERVAL covers NOTHING: `start` and `end` are the two lines of CODE that
    # bound it, and it holds none of them, so it reports `(n+1, n)` -- a range
    # whose end precedes its start, which is how "covers nothing" is spelled.
    #
    # !! IT IS NOT WHERE AN EDIT GOES, AND READING IT THAT WAY IS THE DEFECT
    # THIS SYSTEM EXISTS TO REMOVE. Roy, 2026-08-20: *"that is the defect of
    # reading line numbers as the address. They are not. You see edit-lines
    # somewhere and you are assuming that means that is where the edit goes."*
    # The fields were called `edit_start`/`edit_end` until that day, and the
    # name taught the wrong reading -- a session read `(1, 0)` on a `b1` as
    # "inserts at line 1", concluded a shebang would be displaced, and filed a
    # bug against behaviour that was correct.
    #
    # ! WHERE PROSE LANDS IS SETTLED BY THE ADDRESS and the order the galley
    # applies a page's edits in -- `a` before `b` before `c`, so a `b` lands
    # outside the `a` it followed. These numbers say what is there now; the
    # address says which place is being written. ! The galley still derives its
    # splice position from this range, which is what `docs/plans/` A4 changes.
    #
    # !! IT IS COMPUTED HERE BECAUSE ONLY HERE IS IT KNOWABLE. `intervals()`
    # walks edges that carry SENTINELS -- 0 above the first code line, one past
    # the last below it -- and then clamps them, because a citation has to
    # resolve to a real line. The clamp is what says "this gap is at the file
    # boundary", and it destroys which SIDE it is on. Measured 2026-08-17: an
    # `add` citing the gap above the first line of a file landed BELOW that
    # line, and on a one-line file the gap above and the gap below reduced to
    # the same address, so a reviewer could not tell them apart either.
    #
    # !! A CLOSED LIST OF LINES, OR None. Roy, 2026-08-20: *"the original lines
    # for `b`s are specifically the closed list of lines, `[1..7]` -- not
    # `(1..7)` or `[1..7)` -- or it is None, meaning there are currently no
    # lines that have that foliation."* Both ends are INCLUSIVE and both are
    # real lines of the file.
    #
    # ! SO THERE IS NO EMPTY-SLICE SENTINEL. `(n, n - 1)` used to say "holds
    # nothing", which reads as a range, invites arithmetic, and was read once
    # this day as an insertion point. `None` cannot be mistaken for a position.
    #
    # ! Left None by a producer, they mirror `start`/`end` -- see
    # `__post_init__`. That is what makes this safe to add without visiting
    # every construction site.
    original_start: int | None = None
    original_end: int | None = None
    # !! WHERE THE `c` PLACE BEGINS ON `original_start`, 1-based like every other
    # position this census states -- `start`, `end`, `original_start`, `original_end`.
    # Two values:
    #
    #    0      the paragraph owns its lines WHOLE. Not a column: 0 is not one, and
    #           that is what makes it a sentinel rather than an accident. Every
    #           `comment`, `docstring` and `interval`.
    #    1..N   ONE PAST THE LAST CHARACTER OF CODE on that line, which is where
    #           the room beside the code starts. A `trailing-comment`, a
    #           `margin`, a paragraph comment opened after a statement. It is what
    #           lets the galley write one without deleting the code: the splice
    #           keeps `line[: original_column - 1]`.
    #
    # !! IT IS THE END OF THE CODE, NOT THE START OF THE PROSE, and Roy ruled
    # it 2026-08-19: *"c addresses start at the end of the code on the line."*
    # So the whitespace separating a statement from its trailing comment belongs
    # to the `c` place, and one rule covers both kinds -- a `margin` and the
    # `trailing-comment` that would replace it carry the SAME column. Pointing
    # at the `#` instead made them differ, and made a `drop` a special case: the
    # kept head ended in the separator of a comment that was gone.
    #
    # !! IT IS STATED BY THE PRODUCER BECAUSE NO READER CAN INFER IT. Two tried,
    # both by testing whether the stored text is a proper SUFFIX of the physical
    # line, and the test cannot work: `paragraphs_stdlib` stores the WHOLE line for
    # a trailing comment, so the suffix test answers False. Measured 2026-08-18:
    # censusing `z = 3  # trailing` and editing that paragraph produced a galley
    # reading `# reworded trailing` where the statement had been -- a deleted
    # statement, in the one artefact a human is asked to approve.
    #
    # ! IT REPLACED A BOOLEAN, `whole_lines`, which answered only WHETHER code
    # came first. That was enough to REFUSE the write and not enough to make it,
    # and the `c` series exists to be written. Roy, 2026-08-19: *"c needs to be
    # writeable. It is the reason c is not an extension of b."*
    original_column: int = 0

    def __post_init__(self) -> None:
        """Default the covered lines to the addressing range, or to None.

        ! A producer that states neither gets the addressing range when that
        names real lines, and None when it does not -- `start`/`end` of 0 mean
        this paragraph occupies nothing, and None is how that is spelled here.
        """
        if self.original_start is None and self.original_end is None:
            if self.start >= 1 and self.end >= self.start:
                self.original_start, self.original_end = self.start, self.end


NAMED_DEFS = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
DOC_ANCHORS = (ast.Module,) + NAMED_DEFS


# !! A sentinel that CANNOT be a line number. `0` is one less than line 1, so
# `paragraph.start == trailing_end[0] + 1` was true for every comment opening a
# file -- stamping `continues-a-trailing-comment` with no trailing comment
# anywhere, on 3 files in this repo's own tree. SKILL.md tells reviewers a
# mid-clause ending on a stamped paragraph "is not a `correct`", so the false stamp
# SUPPRESSED real findings on file headers.
_NO_TRAILING = -2

# The work markers `counted_lines` leaves free of the cap.
# !! THE FILE'S OWN PROSE, AS A PARAGRAPH TYPE. Roy, 2026-08-21: *"if the
# opening/closing line is a comment then the matter continues down/up until there
# is an empty line or the start/end of a docstring"*, and *"It is a matter
# designator, the anchor is the module."* One type for both ends -- which end a
# run sits at is the ORDER the `f` foliator emits, not a fact about the run.
#
# ! IT IS STATED HERE BECAUSE THE LEXER READS THE FILE. It was an ANNOTATION the
# page stamped afterwards, which meant a positioning rule lived in a module that
# may hold none, and the page had to reconstruct what "top of the file" meant
# from a paragraph already typed `comment`.
MATTER = "matter"
# !! THE EMPTY SPACE BETWEEN TWO PARAGRAPHS, as a paragraph of its own. Roy,
# 2026-08-21: *"it covers all empty space between two different types of
# paragraphs. If the new line is internal to the paragraph then the two
# paragraphs + the newlines are in fact one paragraph."* So a blank run the
# lexer does NOT merge into a run is leading, and one it does merge is prose.
#
# !! IT IS THE TRADE WORD. Leading is the strip of lead a compositor puts BETWEEN
# lines of type to space them -- what a compositor inserts and never what an
# author writes, which is exactly this. ! A LEADER is the row of dots carrying
# the eye across a table of contents, a different thing.
#
# !! IT CARRIES NO INFORMATION AND IS NEVER RULED ON. Roy: *"there is no
# information to rule on. It is just there for document preservation."* So it is
# kept out of `Page.prose` and out of record seeding, and its anchor is EMPTY --
# every other series answers to a line of code; this answers to nothing.
#
# ! WHY IT EXISTS: a `b` owned the blanks on BOTH sides of an `a`, and a folio is
# one entry in the reading order, so its two lines emitted together and a file
# came back blank-blank-comment where it was blank-comment-blank. With leading,
# every paragraph is CONTIGUOUS and the straddle cannot arise.
LEADING = "leading"
# ! The anchor a run about the FILE answers to. The same string the foliator
# uses for the module trigger; it is spelled here rather than imported because
# the lexer imports no sibling but `language`.
MODULE_ANCHOR = "<module>"
MARKERS = ("TODO", "FIXME", "HACK", "XXX", "BUG")
WORK_MARKER = re.compile(r"^(" + "|".join(MARKERS) + r")\b")
# ! Every punctuation a language opens a comment with, stripped before the
# marker is matched. Anchored on `#`, the exemption was Python-only: a
# `// TODO:` was charged to the cap in a script that censuses eleven languages.
LEAD_PUNCT = re.compile(r"^[\s#/*\-!=;%<>]+")


def counted_lines(raw: list[str]) -> int:
    """Lines a cap charges for: a marker LINE itself is free.

    A marker points at filed work; the explanation is the rest of the paragraph, and
    the cap measures the explanation. Charge the marker and the quickest route to
    green is deleting the pointer -- which is quick to do and expensive to have
    done: the work is still needed, and nothing names it any more.

    The exemption is one line wide. A run stays one run across a marker, and a
    marker's continuation lines are charged: six lines plus a `TODO:` is six.
    """
    # ! A BLANK LINE IS FREE TOO. It sits inside the paragraph by the interval
    # definition -- only code bounds a paragraph -- and SKILL.md says so directly:
    # "The blank is inside the paragraph and is charged nothing." It reaches here
    # now that a blank no longer ends a lexical run.
    return sum(
        1 for ln in raw if ln.strip() and not WORK_MARKER.match(LEAD_PUNCT.sub("", ln))
    )


# -- Annotations ---------------------------------------------------------------
# Each is located here and RESOLVED in `annotate.py`. Locating is most of the
# work; the resolution is what stops a reviewer treating a citation as a
# verified claim. ! These are ANNOTATIONS, never marks -- a MARK is editorial,
# and stage 4 emits those.


def _join(lines: list[str], markers: tuple[str, ...] = ("#",)) -> str:
    """A comment run as ONE normalised string, its comment markers stripped.

    Prose wraps, so every claim-bearing phrase in a real file straddles a line
    break. Matching line-by-line reports the fragment instead of the claim: a
    count reads as absent and `used to say` degrades to a bare `used to`.

    Args:
        lines: the run's raw source lines.
        markers: the language's comment openers, longest first at the call site
            so `///` is stripped before `//` leaves a stray slash in the prose.
    """
    out = []
    for ln in lines:
        s = ln.strip()
        for m in markers:
            if s.startswith(m):
                s = s[len(m) :].strip()
                break
        out.append(s)
    return re.sub(r"\s+", " ", " ".join(out)).strip()


# A docstring's delimiters, and the prefixes that may sit in front of them.
# ! Longest first: `"""` must be tried before `"`, or one quote comes off a
# triple and two are left in the prose.
_QUOTES = ('"""', "'''", '"', "'")
_PREFIXES = ("rb", "br", "r", "b", "f", "u")


def docstring_text(lines: list[str]) -> str:
    """A docstring as ONE normalised string, read from the FILE's lines.

    !! The census never takes this path: it reads a docstring's VALUE from the
    AST, which arrives with no delimiters. Anyone comparing against that value
    starts from the file instead -- delimiters, prefix and all -- and this is
    what makes the two comparable. Measured 2026-08-17: without it a perfect
    transcription kept its CLOSING delimiter, so a paragraph ending `did it` ran
    together with the quotes into one token and was refused against a census
    holding the same sentence.

    Args:
        lines: the paragraph's source lines, as the file reads them.
    """
    text = "\n".join(lines).strip()
    for prefix in _PREFIXES:
        if text[: len(prefix)].lower() == prefix and text[len(prefix) :].startswith(
            _QUOTES
        ):
            text = text[len(prefix) :]
            break
    for quote in _QUOTES:
        if text.startswith(quote):
            text = text[len(quote) :]
            if text.endswith(quote):
                text = text[: -len(quote)]
            break
    return re.sub(r"\s+", " ", text).strip()


def _from_marker(line: str, markers: tuple[str, ...]) -> str:
    """A trailing comment's line, cut back to where its comment starts.

    ! The census stores a trailing comment's PROSE from the comment token and
    its WIDTH from the physical line, so the text a reviewer transcribes -- the
    line as the file reads it -- carries code the census never had. Cutting at
    the marker is what makes the two comparable.

    ! This finds the marker by SEARCH where the census used a lexer, so a
    marker inside a string literal cuts in the wrong place. That is a wrong
    answer on a line the census read correctly; it replaces a guaranteed
    mismatch on every trailing comment.
    """
    at = [i for m in markers if (i := line.find(m)) != -1]
    return line[min(at) :] if at else line


def block_text(
    kind: str,
    lines: list[str],
    markers: tuple[str, ...] = ("#",),
    structural: bool = True,
) -> str:
    """A paragraph's prose as the census stores it, from the file's LINES.

    !! The lines-to-paragraph half of the paragraph protocol, and the ONLY one. It is
    here rather than in a caller because the census defines what a paragraph's text
    IS; a second implementation elsewhere is a second definition, and the two
    drift. Measured 2026-08-17: `verdicts.py` grew its own and disagreed with
    this file three ways at once -- a blank line, a raw-string prefix and a
    closing delimiter -- refusing 83 of 171 paragraphs in one run, ~450 in another.

    ! The inverse, paragraph-to-lines, is stage 7b's and does not exist yet: WRITE
    is prose instructing an agent. When it is built it belongs beside this.

    Args:
        kind: the paragraph's `kind`, as the census records it.
        lines: the paragraph's source lines, as the file reads them.
        markers: the language's comment openers, longest first. ! The
            language's LINE comments only, because that is what the census
            passed -- a set that also stripped `/**` would produce prose the
            census never stored.
        structural: whether this language's doc is a STRING IN A DECLARATION'S
            BODY (Python) rather than a marked comment run (`///`, `/**`).
            `Language.doc_is_structural` records it, and it is the whole
            dispatch: `kind` alone says `docstring` for both.
    """
    # !! Routed on STRUCTURAL, never on `kind` alone. The lexical tier stamps
    # `docstring` on any run opening with a language's doc marker -- `///`,
    # `//!`, `/**` -- and those are comments, not string literals. Reading them
    # as literals leaves the marker in the prose and refuses every doc comment
    # in ten of the eleven languages. Only Python's docstring is a string in a
    # declaration's body, which is what `doc_is_structural` records.
    if kind == "docstring" and structural:
        return docstring_text(lines)
    if kind == "trailing-comment":
        lines = [_from_marker(ln, markers) for ln in lines]
    return _join(lines, markers)


# !! HOW FAR PAST THE OPENING QUOTE AN ESCAPED CHARACTER MAY CLOSE. `'\n'` closes
# at +3 and Rust's widest, `'\u{10FFFF}'`, at +11. An UNESCAPED character needs no
# constant: it is exactly one character wide, so its closer is at +2 and nowhere
# else.
#
# ! IT WAS 10, AND MEASURED WRONG AGAINST ITS OWN WORKED EXAMPLE, 2026-08-21:
# `'\u{10FFFF}'` closes at +11, so the one literal the number was chosen for was
# the one the window never reached.
ESCAPE_WIDTH = 11


def _closes_a_character(line: str, at: int, quote: str) -> bool:
    """Does the quote at `at` open a ONE-CHARACTER literal?

    !! THIS IS WHAT TELLS A CHARACTER FROM A LIFETIME. Rust writes both with
    `'`: `'a'` is a character and `&'a mut T` is a lifetime, and the second
    never closes. Read as a quote it blanks everything after it -- measured
    2026-08-20, a whole trailing comment lost with no refusal and exit 0.

    !! IT ASKS WHERE THE CLOSER IS, NOT WHETHER ONE IS NEARBY. A character is
    one character, so its closer is at a FIXED offset; an escape is the only
    variable-width case and is bounded by `ESCAPE_WIDTH`. ! Scanning a window
    for any closer is what the first version did, and it read TWO LIFETIMES as
    one literal -- measured 2026-08-21, `fn f<'a>(x: &'a T)` came back
    `fn f<         a T)`, blanking real code between them.

    ! ASKED OF THE LINE, NOT OF THE LANGUAGE'S GRAMMAR. What it does not cover
    is a byte or raw literal spelled with a prefix (`b'x'`): the prefix is
    ordinary text and the quote after it reads normally, which is correct.

    Args:
        line: the physical line.
        at: the index of the opening quote.
        quote: the quote character.

    Returns:
        True where this opens a character literal.
    """
    # !! ONE CHARACTER MEANS THE CLOSER IS AT A FIXED OFFSET, not somewhere in a
    # window. Scanning FORWARD for any closer within a character's width read two
    # lifetimes as one literal and blanked the code between them: measured
    # 2026-08-21, `fn f<'a>(x: &'a T) { } // note` came back
    # `fn f<         a T) { } // note` -- 9 characters of real code gone, and a
    # comment opener falling in that span would go with them.
    if line[at + 1 : at + 2] != "\\":
        return line[at + 2 : at + 3] == quote
    # ! An ESCAPE is the one variable-width case, and it is bounded: `'\n'` closes
    # at +3 and Rust's widest, `'\u{10FFFF}'`, at +11. ! The old bound was 10 and
    # never reached that closer, so the literal this constant is SIZED FOR was the
    # one case it did not recognise.
    end = line.find(quote, at + 2)
    return 0 <= end - at <= ESCAPE_WIDTH


def _strip_strings(
    line: str, quotes: tuple[str, ...], char_quotes: tuple[str, ...] = ()
) -> str:
    """Blank out string literals so a marker inside one stays out of the census.

    `url = "http://x"` holds `//` in most C-family languages. It handles
    single-line literals with backslash escapes; raw strings, heredocs and
    template nesting are where this tier stops and the lexer starts.

    Args:
        line: the physical line.
        quotes: this language's string delimiters.
        char_quotes: the subset holding exactly ONE character, which is checked
            for a closer before it is believed. Empty where the language has
            none, and then this behaves exactly as it did.

    Returns:
        The line, its literals blanked, THE SAME LENGTH -- callers cut it at a
        column.
    """
    out, quote, esc = [], "", False
    for i, ch in enumerate(line):
        if esc:
            out.append(" " if quote else ch)
            esc = False
            continue
        if ch == "\\":
            esc = True
            out.append(" " if quote else ch)
            continue
        if quote:
            out.append(" ")
            if ch == quote:
                quote = ""
            continue
        # ! A character's quote is believed only where it CLOSES. Anywhere else
        # it is a sigil the language spells the same way, and the line goes on.
        if ch in char_quotes and not _closes_a_character(line, i, ch):
            out.append(ch)
            continue
        if ch in quotes:
            quote = ch
            out.append(" ")
            continue
        out.append(ch)
    return "".join(out)


def run_ends(
    text: str, pair: tuple[str, str], nests: bool, depth: int = 1
) -> tuple[int, int]:
    """Where a paragraph comment run ENDS in this text, and the depth left open.

    !! IT DOES NOT CLOSE UNTIL EVERY LAYER DOES, where the language nests.
    `/* a /* b */ c */` is ONE comment in Rust and the `c` is inside it; in C the
    first `*/` closes and ` c */` is code. Reading the nesting one as the flat one
    lost the WHOLE comment: the scan closed early, saw more comment after it, and
    applied the intermediate-comment rule -- which is about code after a mid-line
    close. Measured 2026-08-20, a Rust trailing comment censused as zero prose.

    ! WHERE IT MATTERS IS THE TRAILING COMMENT. Roy, 2026-08-20: *"the only place
    we need to care is if it is a trailing comment."* A `b` needs no depth -- a
    gap cannot hold a line of code, so the code either side bounds it -- and no
    language here marks documentation with a bare paragraph opener -- every one
    of them uses a distinguished `/**` or `///` -- so depth cannot
    change what counts as a doc.

    Args:
        text: what to scan -- the tail after an opener, or a continuation line.
        pair: this language's `(opener, closer)`.
        nests: whether an opener INSIDE the run adds a layer.
        depth: layers already open, 1 on the line that opened the run.

    Returns:
        `(index just past the closer that ended it, 0)` where the run closes in
        this text, or `(-1, depth)` where it does not.
    """
    opener, closer = pair
    i = 0
    while i < len(text):
        # ! The CLOSER is tested first, because `--[[` and `]]` share no prefix
        # but a language whose pair overlapped would otherwise never close.
        if text.startswith(closer, i):
            i += len(closer)
            depth -= 1
            if depth == 0:
                return i, 0
            continue
        if nests and text.startswith(opener, i):
            i += len(opener)
            depth += 1
            continue
        i += 1
    return -1, depth


def _own_characters(span: list[str], column: int) -> list[str]:
    """A paragraph's own characters: its lines, cut at `column` on the first.

    !! ONE RULE FOR BOTH TIERS, which is what B3 is. `paragraphs_lexical` cut at the
    comment OPENER and `paragraphs_stdlib` kept the whole physical line, so the two
    stored different things and the retired `paragraph_matches` could not be written to
    satisfy both -- it refused a FRESH census on four of six comment shapes.

    ! With `anchor` holding the code, `anchor + raw_lines[0]` reconstructs the
    first line exactly. Storing the whole line here instead would put the code
    in two fields, which is the conflation the anchor was added to end.

    Args:
        span: the paragraph's physical lines, without endings.
        column: the paragraph's `original_column`; 0 when it owns its lines whole.

    Returns:
        The same lines, with the first cut at `column`.
    """
    if not span or column <= 0:
        return span
    return [span[0][column - 1 :], *span[1:]]


def _anchor_of(lines: list[str], line_no: int, column: int) -> str:
    """The line of code a `c` paragraph sits beside -- its ANCHOR, verbatim.

    !! AN ANCHOR IS THE LINE OF CODE, NOT A SYMBOL. Roy, 2026-08-19: *"the
    anchor isn't the technical symbols and their precise semantic meaning and
    code use. It is 'the line of code' -- the exact characters in that line of
    code."* So it needs no parser, no language server and no build tool: every
    tier already found where the comment opens, which means it already had the
    characters before it.

    !! WITHOUT IT, STALENESS HAS NOTHING FROM THE CENSUS TO COMPARE THE CODE
    AGAINST. `paragraphs_stdlib` kept the whole physical line in `raw_lines` and so
    checked both halves by accident; `paragraphs_lexical` cuts at the opener and so
    checked only the prose -- measured 2026-08-19, a lexical trailing comment
    storing `['// note']` made the retired `paragraph_matches` answer False on an
    UNTOUCHED file. The fix is not to make both tiers store the whole line,
    which conflates the anchor with the prose in one string -- the conflation
    that produced the suffix-test defect twice. Roy: *"not marking or saving the
    anchor is causing the problem."*

    ! It is `""` for a paragraph that owns its lines whole, which has no code on its
    line to be anchored to.

    Args:
        lines: the file's lines, without endings.
        line_no: 1-based line the paragraph opens on.
        column: that paragraph's `original_column`.

    Returns:
        The code preceding the paragraph on its first line, right-stripped.
    """
    if not column or not 1 <= line_no <= len(lines):
        return ""
    return lines[line_no - 1][: column - 1]


def leading_between(paragraphs: list["Paragraph"], text: str) -> list["Paragraph"]:
    """Every blank run no paragraph holds, as LEADING -- see `LEADING`.

    !! ONE RULE FOR BOTH READERS, and that is the point of it being a pass rather
    than a branch inside each. Written per tier, it was written once: the same
    day, `matter` went into the lexical reader alone and every `.py` file
    reported no front matter at all. Roy: *"which is certainly hiding a lot of
    bugs."*

    ! THE RULE IS SUBTRACTION, so it cannot disagree with either reader about
    what prose is: a blank line a paragraph already holds is INSIDE it and stays
    there, and every other blank line is the space between two paragraphs. Roy,
    2026-08-21: *"if the new line is internal to the paragraph then the two
    paragraphs + the newlines are in fact one paragraph."*

    Args:
        paragraphs: what a reader produced, before any place is assigned.
        text: the file, read for which lines are blank.

    Returns:
        One paragraph per unheld blank run, in order.
    """
    lines = text.splitlines()
    held = set()
    for b in paragraphs:
        if b.original_start:
            held.update(
                range(b.original_start, (b.original_end or b.original_start) + 1)
            )
    out: list[Paragraph] = []
    run: list[int] = []
    for n, line in enumerate(lines, 1):
        if not line.strip() and n not in held:
            run.append(n)
            continue
        if run:
            out.append(_leading(paragraphs, run))
            run = []
    if run:
        out.append(_leading(paragraphs, run))
    return out


def _leading(paragraphs: list["Paragraph"], run: list[int]) -> "Paragraph":
    """One blank run, as a paragraph. Its anchor is EMPTY on purpose.

    ! Every other series answers to a line of code. This answers to nothing --
    Roy accepted that when he took it: *"I like the leading solution even though
    it added another foliation and the anchors are empty."*
    """
    return Paragraph(
        path=paragraphs[0].path if paragraphs else "",
        start=run[0],
        end=run[-1],
        kind=LEADING,
        lines=0,
        text="",
        raw_lines=[""] * len(run),
        tier=paragraphs[0].tier if paragraphs else "lexical",
    )


def _is_doc(line: str, lang: Language) -> bool:
    """Does this line open a run the language treats as DOCUMENTATION?

    ! Two readers ask it and they must agree: `flush` to set the kind, and
    `carry` to decide whether a blank line ends the file's matter. It was
    computed inline in one of them, so the other tested a different thing --
    `eslint.config.ts` opens with `/** */` and had its matter terminated as
    though the run were an ordinary comment.
    """
    opens = line.strip()
    if lang.doc_line and opens.startswith(lang.doc_line):
        return True
    return bool(lang.doc_block and opens.startswith(lang.doc_block))


def paragraphs_lexical(path: Path, text: str, lang: Language) -> list[Paragraph]:
    """Comment runs for a language with no parser here -- the FLOOR tier.

    Answers where every paragraph is, its line range, its text and its
    annotations. Every paragraph comes back stamped `tier="lexical"`. ! A paragraph
    sitting BESIDE code carries an anchor at this tier too -- the line of code
    itself, which needs no parser; see `_anchor_of`. Only a paragraph that owns its
    lines whole has none, because its anchor is a declaration and naming one
    needs the structure this tier lacks.

    ! A paragraph opener with no closer swallows every remaining line into one run,
    so code below it is censused as prose. That paragraph is STAMPED
    `unterminated-paragraph-comment`, which is how a consumer tells it from a long
    comment; `prove_unchanged.py` refuses the whole file on that annotation.
    """
    openers = tuple(sorted(lang.line_comment, key=len, reverse=True))
    lines = text.splitlines()
    out: list[Paragraph] = []
    run: list[tuple[int, str]] = []
    # ! Blank lines seen since the last comment line. They join the run only if
    # another comment follows; otherwise they are dropped, so a run ends on its
    # last comment line.
    pending: list[tuple[int, str]] = []
    in_block: tuple[str, str] | None = None
    # ! LAYERS STILL OPEN on a run that crossed a line -- see `run_ends`. Always
    # 1 where the language does not nest.
    layers = 1
    # ! The line the last trailing comment ended on. Measured: this tier splits a
    # wrapped trailing comment exactly as `paragraphs_stdlib` does, so it needs the
    # same stamp. A list because `flush` is a closure and rebinds nothing.
    trailing_end = [_NO_TRAILING]

    # !! WHERE THE RUN'S FIRST LINE STOPS BEING CODE -- the `original_column` this
    # tier states, one past the last character of code, or 0 when the run owns
    # its lines whole.
    #
    # ! `trailing` does not answer it: a MULTI-LINE paragraph comment opened after a
    # statement flushes with `trailing=False`, because by then the run spans
    # several lines. A list because `flush` is a closure and rebinds nothing.
    partial_first = [0]

    # !! HAS ANY CODE BEEN SEEN YET -- which is what says a run is still at the
    # HEAD of the file, and therefore whether a blank line ends it. Roy,
    # 2026-08-21: *"Any normal comment section at the top of the file becomes f0
    # until there is either a docstring or a blank line."*
    #
    # ! Everywhere else a blank line does NOT end a run, and that stays true: a
    # licence header and the first function's documentation separated by a blank
    # are two things, while a wrapped sentence with a blank in it is one. Only at
    # the file's own edge does the blank decide. A list because `flush` is a
    # closure and rebinds nothing.
    seen_code = [False]

    def carry() -> None:
        """Take the blanks held since the last prose line into the run.

        !! ONE RULE FOR BOTH COMMENT SYNTAXES, and it was written for the line
        one alone. A delimited comment did not carry them, so `/* one */`, a
        blank and `/* two */` became two paragraphs where `// one`, a blank and
        `// two` became one -- the same language, the same gap, a different
        answer decided by which syntax the author reached for.

        ! The head-of-file split is part of the rule and travels with it: at the
        top of a file a blank ENDS the run, because what sits above the first
        line of code is the file's own matter.

        !! IT ENDS THE FIRST RUN ONLY, which `out` is what says. A file opening
        with THREE comment runs before any code -- measured on
        `meta-package-manager/tests/cli-test-plan.toml` -- split at every blank,
        so the second and third both took `b0` and shared an address. Only the
        first is the file's own matter; the rest are ordinary prose in the gap
        above the first statement, and they merge there like any other.
        """
        # !! IT ENDS THE MATTER, SO IT FIRES ONLY WHEN THERE IS MATTER TO END.
        # Roy's rule is that matter runs from the OPENING LINE down to a blank,
        # so a run that does not start on line 1 -- or that is a docstring, which
        # matter never is -- has nothing here to terminate.
        #
        # ! MEASURED 2026-08-21 without those two conditions: `floatobject.h`
        # opens with a BLANK and `eslint.config.ts` with a `/** */`, and each
        # split into two runs that then SHARED `b0` -- a collision manufactured
        # by a rule protecting a file that had no matter in the first place.
        opens_file = bool(run) and run[0][0] == 1 and not _is_doc(run[0][1], lang)
        if not run:
            # !! BLANKS ABOVE A RUN THAT HAS NOT STARTED ARE NOT ITS OWN. They
            # separate this prose from whatever precedes it, which is what
            # LEADING is -- and `leading_between` finds them afterwards, for both
            # readers at once. ! Extending an EMPTY run with them made the blank
            # the paragraph's first line, so a comment two lines below a
            # statement reported itself as starting at the blank.
            pending.clear()
            return
        if pending and opens_file and not out and not seen_code[0]:
            flush()
        else:
            run.extend(pending)
            pending.clear()

    def flush(trailing: bool = False) -> None:
        # ! The blanks held since the run's last prose line are LEADING, not the
        # run's -- `leading_between` collects them once every paragraph exists.
        pending.clear()
        if not run:
            partial_first[0] = 0
            return
        raw = [t for _, t in run]
        # !! `raw_lines` IS THE SOURCE, `raw` IS THE PROSE. They were one list,
        # so a paragraph comment's own indentation and a trailing comment's code
        # were cut out of the record of what is on disk -- and `paragraph_matches`
        # then refused a census built seconds earlier. The cut text still makes
        # `text` and still counts against the cap; the file's own characters are
        # what a splice is checked against.
        span = lines[run[0][0] - 1 : run[-1][0]]
        if partial_first[0] > 0:
            span = [span[0][partial_first[0] - 1 :], *span[1:]]
        if _is_doc(raw[0], lang):
            kind = "docstring"
        else:
            # !! CODE ON THE FIRST LINE MAKES IT TRAILING, however many lines it
            # then runs for. Roy, 2026-08-20: *"`c`s are trailing comments by
            # definition of how they are placed."* A `c` is the room beside a
            # line of code, so prose occupying that room IS a trailing comment
            # and the kind must say so. ! `trailing` alone answers only the
            # single-line case: a paragraph comment opened after a statement
            # flushes with `trailing=False`, because by then the run spans
            # several lines -- so `int b = 2; /* opens` was censused as a plain
            # `comment` sitting at a `c` place, and kind and series disagreed.
            kind = "trailing-comment" if trailing or partial_first[0] else "comment"
        # !! THE LEXER SAYS WHICH SERIES THIS RUN IS, and matter is the case it
        # can say outright. Roy, 2026-08-21: *"the matter/not matter split is
        # easy and already determined by my ruling that if the opening/closing
        # line is a comment then the matter continues down/up until there is an
        # empty line or the start/end of a docstring ... that makes f trivial and
        # consistent because that paragraph instead of being marked as comment
        # and the page trying to reconstruct what was meant by top of the file
        # and a comment."*
        #
        # !! THE OPENING LINE ITSELF MUST BE A COMMENT. A file whose line 1 is
        # BLANK has no front matter at all -- which is what `page.mark_matter`
        # could not express, since it took the first run of PROSE wherever it
        # sat. MEASURED: 11 CPython headers open with a blank, and each one put
        # an `f0` inside the gap that owned the blank above it, so the gap ran
        # THROUGH the matter and the compositor set the comment above its own
        # blank line.
        #
        # ! A DOCSTRING IS NOT MATTER, and it is what ENDS matter. A file opening
        # with its own documentation has none.
        #
        # !! ONE TYPE, NOT TWO. Roy, 2026-08-21: *"It is a matter designator, the
        # anchor is the module ... front-matter, back-matter are paragraph type
        # matter."* Which END it sits at is not a fact about the paragraph -- it
        # falls out of the order the `f` foliator emits, exactly as `a1` and `a2`
        # fall out of the order declarations are met. Naming the two ends here
        # would state the same fact twice and let them disagree.
        if kind == "comment" and (run[0][0] == 1 or run[-1][0] == len(lines)):
            kind = MATTER
        paragraph = Paragraph(
            path=path.as_posix(),
            start=run[0][0],
            end=run[-1][0],
            kind=kind,
            lines=counted_lines(raw),
            text=_join(raw, openers),
            raw_lines=span,
            tier="lexical",
            original_column=partial_first[0],
            # !! THE LEXER ALREADY HAS THIS STRING. It found the opener in
            # order to cut there, so the characters before it were known one
            # step earlier and were thrown away. Roy, 2026-08-19: *"the lexer
            # either knows what is before the trailing comment and can snag the
            # whole string or it is broken."*
            # !! MATTER IS ANCHORED TO THE MODULE, because that is what it is
            # about. Roy, 2026-08-21: *"It is a matter designator, the anchor is
            # the module."* Every other run answers to the line of code it sits
            # with; the file's own prose answers to the file.
            anchor=(
                MODULE_ANCHOR
                if kind == MATTER
                else _anchor_of(lines, run[0][0], partial_first[0])
            ),
        )
        partial_first[0] = 0
        # !! Same split as the tokenized tier: a trailing comment closes its run,
        # so a sentence wrapped onto the next line becomes a SECOND paragraph anchored
        # to the code below it. Stamped, not re-cut.
        if kind == "comment" and paragraph.start == trailing_end[0] + 1:
            paragraph.annotations.add("continues-a-trailing-comment")
            paragraph.notes.append(
                "opens on the line after a trailing comment, so it may be the"
                " tail of that sentence rather than a note about the code"
                " below. A mid-clause ending here may be the split."
            )
        if kind == "trailing-comment":
            trailing_end[0] = paragraph.end
        out.append(paragraph)
        run.clear()

    for n, raw_line in enumerate(lines, 1):
        if in_block is not None:
            # !! CODE AFTER THE CLOSER KEEPS ITS PROSE AND LOSES ITS CODE LINE.
            # `/* note\n   more */ int x = 5;` censuses the run and leaves
            # `int x = 5;` out of `code_lines`, so every interval boundary below
            # it moves.
            #
            # !! AND AN EDIT TO THAT PARAGRAPH DELETES THE STATEMENT. This cut
            # trims the paragraph's TEXT and not its `raw_lines`, and the galley
            # splices `start..end` wholesale -- it preserves the head of the
            # FIRST line at `column` and has no tail preservation on the last.
            # MEASURED 2026-08-21: a `patch` on that paragraph writes the new
            # prose and `int x = 5;` is gone. `prove_unchanged` catches it, but
            # only AFTER 7b has written the file.
            #
            # !! IT IS THE GALLEY'S TO CATCH, NOT THE LEXER'S AND NOT A
            # REVIEWER'S. Roy, 2026-08-21: a reviewer rules on a paragraph and has
            # no view of how the galley splices it, so *"how do the agents know
            # that the closing line is going to delete code?"* -- they cannot.
            # The whole-file composition the galley is heading for is where a
            # write that would drop a line becomes visible BEFORE it happens,
            # which is the same move `prove_unchanged` needs. Filed as
            # `TODO/closing-line-deletes-code.md`.
            #
            # ! NEITHER FIX WAS WORTH ITS COST. Dropping the run the way an
            # INTERMEDIATE comment is dropped works on the one-line twin --
            # `/* note */ int x = 5;` is wholly a code line -- and not here,
            # where the opening line is nothing but comment and would belong to
            # nothing. Keeping both needs a field for where the text ENDS, or a
            # kind for comment-then-code; the first re-adds a column the address
            # system replaced, the second teaches every consumer that switches
            # on kind.
            #
            # !! MEASURED 2026-08-20 OVER THE FETCHED CORPORA: 180,821 lines of
            # C and JS/TS, and the shape occurs **0 times** -- 3 apparent hits
            # were `*/` inside a glob string. The one-line form is ordinary
            # (1,551 hits) and is already right. Roy: *"it is stupid to break
            # context like that,"* and the style guides agree -- ESLint ships
            # `no-inline-comments`, and the kernel, Google C++ and Java guides
            # all put a paragraph comment on its own line.
            #
            # ! CUT AT THE CLOSER, the way the opening line cuts at the opener.
            # The whole raw line was appended, so `   more */ int x = 5;` gave a
            # paragraph whose TEXT held the statement -- executable code handed to
            # four reviewers as prose and run through the annotation regexes.
            # ! The file recorded this as fixed for the OPENING line; the closing
            # line was never covered. Measured 2026-08-20 on C.
            # ! CARRIES THE DEPTH, so a nested opener on an earlier line keeps
            # the run open past the closer that matches it.
            ends, layers = run_ends(raw_line, in_block, lang.nests_comments, layers)
            if ends >= 0:
                run.append((n, raw_line[:ends].rstrip()))
                in_block = None
                # !! THE SAME RULE AS THE SINGLE-LINE CLOSE BELOW: a closer ends
                # the COMMENT, not the paragraph. This one opened on an earlier
                # line, so code cannot precede it here -- `partial_first` records
                # whether code preceded it THERE, which is what makes the run a
                # `c`. ! Code after the closer does reach this branch, unlike the
                # single-line case, and it is the next statement.
                if partial_first[0] or raw_line[ends:].strip():
                    flush()
                continue
            run.append((n, raw_line.rstrip()))
            continue
        # !! ONLY CODE ENDS A PARAGRAPH -- a blank line does not, and this reached
        # `flush()` because `"".startswith(openers)` is False. SKILL.md names
        # the consequence exactly: "Split on blanks and a 9-line paragraph reads as
        # `6 + 3` and passes a cap of 6 -- the quickest way to fake compliance."
        # Measured 2026-08-17: a six-line run with one blank censused as 3L + 3L
        # in every LEXICAL language, while `paragraphs_stdlib` skips NL tokens and
        # kept it whole. Ten of the eleven languages could evade any cap.
        #
        # ! The blank JOINS the run rather than being skipped, so `raw_lines`
        # stays index-aligned with `start..end` -- `prove_unchanged` walks the
        # two together and a gap there makes the file unprovable.
        #
        # !! A blank line INSIDE a run joins it; a blank line AFTER one does
        # NOT extend it. They are held here and committed only when another
        # comment line arrives. A run's `end` must stay on its last comment
        # line, because `doc-kind-unresolved` asks whether the very next line
        # is a declaration -- extend the paragraph over the gap and an ORPHAN run,
        # held off its declaration by exactly that gap, reads as documenting it.
        if not raw_line.strip():
            # ! HELD WHETHER OR NOT A RUN IS OPEN, since 2026-08-21. A blank with
            # no run above it was dropped outright, so the space between two code
            # lines belonged to nothing the lexer emitted and `fill_the_gaps` had
            # to hand it to a `b` afterwards.
            pending.append((n, ""))
            continue
        code = _strip_strings(raw_line, lang.quotes, lang.char_quotes)
        line_at = min((code.index(o) for o in openers if o in code), default=-1)
        opened = next((p for p in lang.block_comment if p[0] in code), None)
        # !! WHICHEVER OPENER COMES FIRST on the line owns it. The paragraph test
        # ran first unconditionally, so `// see /* the note` opened a paragraph run
        # that swallowed every line up to the next `*/` -- executable code
        # handed to four reviewers as prose, carrying no annotation to say so,
        # and dropped from `code_lines`, which put every interval in that file
        # at the wrong boundary. Measured on a five-line C file: one paragraph
        # spanning lines 2-4 whose text held `int b = 2;`.
        if opened is not None and -1 < line_at < code.index(opened[0]):
            opened = None
        if opened is not None:
            # !! OPENING A DELIMITED COMMENT DOES NOT END THE RUN BEFORE IT, and
            # an unconditional `flush()` here is what made `/* one */`, a blank
            # and `/* two */` two paragraphs where `// one`, a blank and `// two`
            # are one. Same language, same gap, and the answer decided by which
            # syntax the author reached for. ! Whether it ends depends on what is
            # on THIS line, which is not known until `opens_at` below -- so the
            # decision moved down to where the facts are.
            # !! CUT AT THE OPENER, like the line-comment path below does. The
            # whole raw line was appended, so `int b = 2; /* note */` was
            # censused as one `comment` paragraph whose TEXT held the statement --
            # executable code handed to four reviewers as prose, run through the
            # annotation regexes, and dropped from `code_lines`, which moved
            # every interval boundary in the file. Measured 2026-08-17, the same
            # shape as the `//`-before-`/*` case fixed directly above.
            opens_at = code.index(opened[0])
            tail = code[opens_at + len(opened[0]) :]
            ends_at, layers = run_ends(tail, opened, lang.nests_comments)
            closes_here = ends_at >= 0
            after = tail[ends_at:] if closes_here else ""
            # !! AN INTERMEDIATE COMMENT IS NOT CENSUSED -- one that CLOSES on
            # this line with code after it, `int x = /* why */ 5;`. Roy ruled it
            # 2026-08-19, on the same grounds as a Python type annotation: *"they
            # are not comments that can be systemically and completely verified
            # across code bases or written consistently on the same file because
            # of line length rules ... all intermediate comments are ignored.
            # They can be brought up by the agents as code change suggestions."*
            #
            # ! It was censused, and the paragraph's TEXT was the whole statement:
            # measured 2026-08-19, `f.c@c1 comment text='int x = /* why */ 5;'`
            # -- executable code handed to four reviewers as prose. Cutting at
            # the opener instead loses the `5;`, so `5` and `7` would compare
            # EQUAL and `prove_unchanged` report PROVEN on a changed literal.
            # Neither is available; the line is simply code. It stays a code
            # line, so it keeps its `b` and its `c` like any other.
            if closes_here and after.strip():
                # ! THE LINE IS CODE, so it ends the run like any other.
                flush()
                continue
            beside_code = bool(code[:opens_at].strip())
            if beside_code:
                # ! Code before the opener makes this a TRAILING run, which
                # begins here whatever preceded it.
                flush()
            else:
                # ! Nothing but the comment on this line, so the run it may be
                # continuing carries on -- and the blanks held since its last
                # prose line come with it, exactly as for a line comment.
                carry()
            # ! Only the run's FIRST line decides it, and a run continuing from
            # an earlier comment already answered 0 -- which is what this sets
            # when no code precedes the opener, so it stays a no-op there.
            # ! THE RAW LINE, for the reason the whole-line test below gives:
            # a blanked literal is whitespace, so a line whose only prefix is a
            # string reported column 0 and left the code set.
            partial_first[0] = (
                len(raw_line[:opens_at].rstrip()) + 1 if beside_code else 0
            )
            run.append((n, raw_line[opens_at:].rstrip()))
            if not closes_here:
                in_block = opened
            elif beside_code:
                # !! ONLY CODE ENDS A PARAGRAPH, AND A CLOSER IS NOT CODE. This
                # flushed on every close, so `/* one */` alone on a line ended
                # its paragraph and the blank beneath it could not bridge to the
                # next run. ! Code AFTER the closer cannot reach here -- such a
                # line is not censused at all, by the intermediate-comment ruling
                # above -- so code BEFORE the opener is the only thing left, and
                # that makes this a trailing comment: prose about the statement
                # on its own line, which must not absorb the prose beneath it.
                flush(trailing=True)
            continue
        # !! ASKED OF THE RAW LINE, NOT THE BLANKED ONE. `_strip_strings` replaces
        # a literal with spaces, which erases the evidence that code came first:
        # `  "b" // the last one` blanks to `      // the last one`, whose strip
        # starts with the opener, so a JS array element was censused as a
        # whole-line `comment` whose TEXT held `"b"` -- executable code handed to
        # four reviewers as prose -- and its line left `code_lines` entirely.
        # ! WHAT THAT COSTS IS NOT THE MISREADING. Every `b` and `c` below the
        # line shifts, so a galley splice over one of those addresses lands
        # somewhere other than where the reviewer cited. Measured 2026-08-20 on
        # JS and C. ! Whitespace before the opener is not code, which is the case
        # the blanked test got right and this keeps right.
        if line_at >= 0 and not raw_line[:line_at].strip():
            carry()
            run.append((n, raw_line.rstrip()))
            continue
        flush()  # ! CODE ends a paragraph; a blank line does not
        seen_code[0] = True
        at = line_at
        if at >= 0:
            # ! `flush()` above emptied the run, so this line is the first
            # one and the code before `at` is what makes it trailing. A line
            # comment runs to end of line, so there is no other side to test.
            # ! THE RAW LINE, not the blanked one -- same reason as above.
            partial_first[0] = (
                len(raw_line[:at].rstrip()) + 1 if raw_line[:at].strip() else 0
            )
            run.append((n, raw_line[at:].rstrip()))
            flush(trailing=True)  # its own paragraph, anchored to the code on that line
    # !! THE FOOT OF THE FILE, AND THE LOOP IS OVER SO NOTHING FOLLOWS. Roy,
    # 2026-08-21, asked whether the foot needed a rule of its own: *"same answer
    # for the back matter because of the same reason."* Read upward, the run
    # after the LAST blank line is the file's own matter.
    #
    # !! IT NEEDS NO LOOKAHEAD, which is the whole reason it is done here rather
    # than in the loop: at the head, "no code yet" is a fact already in hand; at
    # the foot, "no code after" is only a fact once the loop has ended. Both are
    # the same rule read from opposite ends.
    #
    # ! Only an INTERIOR blank can split -- a run never ends on one, because
    # blanks reach `run` from `pending` and `pending` merges only when another
    # comment follows. The blank itself goes to neither half; `page.fill_the_gaps`
    # gives it to the gap that owns it, exactly as at the head.
    if run:
        blanks = [i for i, (_, held) in enumerate(run) if not held.strip()]
        if blanks:
            tail = run[blanks[-1] + 1 :]
            del run[blanks[-1] :]
            flush()
            run.extend(tail)
    flush()
    if in_block is not None and out:
        # The loop ended with a paragraph comment still open, so the final flush
        # emitted the run that ate the rest of the file. It is the ONE paragraph
        # that may hold code.
        out[-1].annotations.add("unterminated-paragraph-comment")
        out[-1].notes.append(
            f"UNTERMINATED {in_block[0]}: no closing {in_block[1]} before end of "
            "file, so every line below the opener was swallowed into this run. "
            "Code down there was NOT censused as code."
        )
    return out


def flag_structural_docs(
    paragraphs: list[Paragraph], text: str, lang: Language
) -> None:
    """Mark each run whose KIND is still an open question at this tier.

    Go and Ruby attach documentation by POSITION -- an ordinary line comment
    directly above a declaration IS that declaration's documentation -- so a
    doc reads like any other run, and telling them apart needs the structure
    this tier lacks.

    The paragraph is annotated as an OPEN QUESTION instead. That matters because
    `compact.md` routes on KIND: a `comment` is governed by LENGTH and may be
    cut to the cap, a `docstring` by FORMAT and stands. Unmarked, a three-line
    Go export doc reads as over a cap of two and is cut by a rule that governs
    comments.

    Args:
        paragraphs: this file's paragraphs, mutated in place.
        text: the file's source, for looking at what follows each run.
        lang: the language record, which decides whether this pass applies.
    """
    if not lang.doc_is_structural:
        return
    lines = text.splitlines()
    for paragraph in paragraphs:
        # Only a leading `comment` run can be a positional doc: a trailing
        # comment annotates the code on its own line.
        if paragraph.kind != "comment":
            continue
        # ! The IMMEDIATELY next line. Both languages require a doc comment to
        # touch its declaration, so a run held off by a blank line is an ORPHAN
        # -- left unmarked here, and charged to the cap.
        nxt = lines[paragraph.end].strip() if paragraph.end < len(lines) else ""
        if not nxt:
            continue
        paragraph.annotations.add("doc-kind-unresolved")
        paragraph.notes.append(
            "KIND UNRESOLVED: this run sits above code and "
            f"{lang.name} attaches docs by position, so it may be documentation "
            "governed by FORMAT rather than a comment governed by LENGTH. "
            "NOT counted against the cap. Confirm the kind before compacting."
        )


#: A declaring line's first word, ignoring indentation. Stops at anything that
#: cannot be part of a keyword, so `macro_rules!` and `async def` both reach the
#: match while `func(x)` yields `func` and `x=1` yields `x`.
_FIRST_WORD = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*!?)")


def _declares_here(line: str, declares: tuple[str, ...]) -> bool:
    """Does this line of code introduce something documentable?

    !! IT MATCHES THE FIRST WORD, NEVER A SUBSTRING. `deffered = 1` opens with
    `deffered`, and a substring test would call it a `def`; `x = my_func()`
    holds `func` and declares nothing.

    ! TWO WORDS ARE TRIED, so a modifier does not hide the keyword: Python's
    `async def`, and a c-family `public static void f()` whose own keyword is
    `public`. Either word matching is enough, because the list already says
    which words this language uses for the purpose.
    """
    m = _FIRST_WORD.match(line)
    if not m:
        return False
    first = m.group(1)
    if first in declares:
        return True
    rest = line[m.end() :].lstrip()
    second = _FIRST_WORD.match(rest)
    return bool(second and f"{first} {second.group(1)}" in declares)


def document_declarations(
    paragraphs: list["Paragraph"],
    decls: list[tuple[int, int, bool]],
    code: dict[int, str],
) -> None:
    """Say which prose run documents which declaration, at the LEXICAL tier.

    !! IT LIVES HERE BECAUSE POSITIONING IS THE LANGUAGE'S, and the lexer is one
    of the two modules allowed to ask a language anything. Roy, 2026-08-21: *"All
    framing about positioning should come from the language and should be only in
    either the language definition file, or a reference to the language
    definition file in lexer and compositor."* It was in `page.py`, which is
    neither. ! `paragraphs_stdlib` already states this for Python from its parse;
    this is the same fact for a language the parser cannot read.

    !! PROSE BELONGS TO WHICHEVER SIDE IT IS NEARER TO, and a TIE goes to the
    side the language documents on. That is the whole rule, and it replaced
    "the nearest run above the declaration", which could not tell a
    declaration's documentation from a note about the statement above it.

    ! MEASURED 2026-08-21 on `meta-package-manager`'s `mpm.js`:

        export const MPM_MIN_VERSION = [6, 4, 0];
        /* mpm 6.4.0 renamed `--output-format` back to `--table-format` ... */

        export const MPM_TIMEOUT = 60;

    The comment explains why the MINIMUM VERSION is 6.4.0 -- it is about the line
    it sits under. The old rule walked up from `MPM_TIMEOUT`, skipped the blank
    and claimed it, so four reviewers would have measured that prose against
    `= 60`. It is flush under the code above (0 blank lines) and one blank from
    the declaration below, so it is nearer to what it is about.

    ! A TIE IS FLUSH ON BOTH SIDES, and it goes to the declaration, which is the
    convention every above-doc language writes by. MEASURED over the corpora: of
    23 ties in above-doc languages, 20 sit flush above their declaration and are
    unaffected, 1 has a blank on both sides and is unaffected, and 2 change --
    both of them the shape above.

    ! WHAT IT CANNOT DO is read the prose. A comment flush under one statement
    and about the next is indistinguishable by position, which is why
    `ownership-context` reads every placement rather than trusting one.

    Args:
        paragraphs: this file's prose, mutated in place -- `declares` is set on
            the run that documents each declaration.
        decls: `(line, insert, above)` per declaration, module first.
        code: `line -> the code on it`, in order.
    """
    # ! LEADING IS NOT PROSE AND CANNOT DOCUMENT ANYTHING. It became a paragraph
    # on 2026-08-21, and without this the walk up from a declaring line stopped
    # at the blank above it and tied THAT -- so a doc comment separated from its
    # declaration by one blank line, the shape 38% of CPython's use, was left
    # undocumented and the blank took the `a`.
    ends = {
        b.original_end: b
        for b in paragraphs
        if b.original_end and not b.original_column and b.kind != LEADING
    }
    if not ends:
        return
    above_code = sorted(code)
    for ordinal, (line, _insert, above) in enumerate(decls[1:], 1):
        if not above:
            # ! Python states this from its parse; nothing positional to do.
            continue
        # ! UP FROM THE DECLARING LINE, past blanks, stopping at CODE -- prose
        # above that code is about that code and cannot reach across it.
        held = None
        at = line - 1
        while at >= 1:
            if at in code:
                break
            if at in ends:
                held = ends[at]
                break
            at -= 1
        if held is None:
            continue
        # ! THE TWO DISTANCES, counted in blank lines. Nothing above the run
        # means there is nothing for it to belong to, so the declaration takes
        # it -- `over` is set past `below` to say so.
        below = line - held.original_end - 1
        previous = [n for n in above_code if n < held.original_start]
        over = held.original_start - previous[-1] - 1 if previous else below + 1
        if below <= over:
            held.declares = ordinal


def declarations(
    text: str, lang: Language, code: dict[int, str] | None = None
) -> list[tuple[int, int, bool]]:
    """Every DOCUMENTABLE declaration in source order: its line, and where its doc goes.

    !! ENTRY 0 IS THE MODULE, whose line is 0 -- a module has no line of code
    declaring it. Entries 1..N are its declarations in the order a reader meets
    them down the page, which is the order the `a` series counts.

    !! AN EMPTY LIST MEANS THIS LANGUAGE HAS NO `a` SERIES, not "none found
    here". Roy, 2026-08-20: *"we need to be able to distinguish `a` foliations
    for as many languages as there are `a` possible foliations. yaml, toml are
    not ones."* A YAML file carried an `a0` -- a place for a module docstring in
    a language with no such thing -- which no verdict could ever fill.

    !! THE KEYWORDS ARE DATA, AND THAT IS THE WHOLE POINT. Roy: *"the easy way
    is to supply the lexer with the list of keywords that a language/practice
    uses to say this can get a docstring. Then the lexer matches on that instead
    of having to have independent tooling."* Before this, `a` resolved for
    Python alone, because Python is the one language the stdlib parses. An LSP
    or the build tooling can VERIFY the result; neither is needed to get one.

    ! PYTHON STILL USES ITS PARSER, because its doc goes INSIDE the body --
    `lang.doc_inside`. Where the body starts is not the declaring line and is
    not `line + 1`: a wrapped signature moves it several lines down. Every other
    language puts the doc on the declaring line's own line, so the line the
    keyword is on is the whole answer.

    ! It REPORTS; it does not emit a paragraph. `undocumented` is a PAGE kind,
    because only a page knows where prose is missing.

    Args:
        text: the file's source.
        lang: its record. `declares` decides whether there is an `a` series.
        code: `line -> the code on it`, from `page.code_lines`. The keyword path
            scans ONLY these, so a keyword inside a comment or a string cannot
            declare anything. Required for a language that is not Python.

    Returns:
        `(line, insert, above)` per declaration, module first, or `[]` when the
        language has no `a` series. !! `above` IS THE ROW SPEAKING, not a
        comparison of the two numbers -- Roy, 2026-08-21: *"The language
        definition file has to state which, not the code."* It is `doc_inside`
        read back out, and it is stated HERE because the lexer is one of the two
        modules that touch a file at all; every step below carries it.
    """
    if not lang.declares:
        return []
    if lang.doc_inside:
        try:
            tree = ast.parse(text)
        except SyntaxError:
            # ! A file the parser refused declares nothing this can state. Its
            # one `unparsed` paragraph reports the refusal.
            return []
        # ! SOURCE ORDER, which `ast.walk` does not give -- the same sort
        # `paragraphs_stdlib` makes, so the ordinals line up by construction.
        declared = sorted(
            (n for n in ast.walk(tree) if isinstance(n, NAMED_DEFS)),
            key=lambda n: n.lineno,
        )
        # ! ABOVE is False for every entry here: this is the `doc_inside`
        # path, and the row that sent us down it is the statement.
        out: list[tuple[int, int, bool]] = []
        for node in [tree, *declared]:
            body = getattr(node, "body", [])
            # ! An empty module has no first statement; its doc would open the file.
            out.append(
                (getattr(node, "lineno", 0), body[0].lineno if body else 1, False)
            )
        return out
    # !! THE MODULE FIRST, AND ITS DOC OPENS THE FILE. `a0` is the file's own
    # documentation, which in an above-doc language is the run at the top --
    # Rust's `//!`, Go's package comment.
    out = [(0, 1, True)]
    # ! The doc goes ON the declaring line, pushing it down, so `insert` IS that
    # line. Ordered because `code` is.
    out += [
        (n, n, True)
        for n, line in (code or {}).items()
        if _declares_here(line, lang.declares)
    ]
    return out


def paragraphs_stdlib(path: Path, text: str) -> list[Paragraph]:
    """Comment paragraphs (bounded by CODE) and docstrings, via tokenize + ast."""
    out: list[Paragraph] = []
    source_lines = text.splitlines()
    # (line, physical source line, the comment token alone, is it trailing)
    run: list[tuple[int, str, str, bool]] = []
    # ! The line the last trailing comment ended on. A comment opening on the
    # VERY NEXT line continues that sentence, and the flush below has already
    # split them. A list because `flush` is a closure and rebinds nothing.
    trailing_end = [_NO_TRAILING]

    def flush() -> None:
        if run:
            # ! PROSE comes from the comment token; WIDTH from the physical
            # line, which is the whole line a width rule measures. Using the
            # physical line for both fed a trailing comment's own code to the
            # annotation regexes -- reviewers saw
            # `models.Index(fields=(...)),  # note` as the note's text.
            prose = [c for _, _, c, _ in run]
            # !! THE SAME MATTER RULE AS THE LEXICAL TIER -- see `MATTER`. Both
            # readers state it, because a paragraph's TYPE is the lexer's to say
            # and a file's own prose is not a different thing in Python. ! It was
            # written on one tier first, and `.py` fixtures then reported NO
            # matter at all while `.c` ones reported it correctly.
            whole = not run[0][3]
            kind = "comment" if whole else "trailing-comment"
            if whole and (run[0][0] == 1 or run[-1][0] == len(source_lines)):
                kind = MATTER
            out.append(
                paragraph := Paragraph(
                    path=path.as_posix(),
                    start=run[0][0],
                    end=run[-1][0],
                    kind=kind,
                    # ! ONE PAST THE LAST CHARACTER OF CODE on the line, or
                    # 0 for a leading comment. NOT the `#`: the whitespace
                    # between a statement and its comment belongs to the `c`
                    # place, so a `margin` and the trailing comment that would
                    # replace it carry the same column.
                    original_column=run[0][3],
                    lines=counted_lines(prose),
                    text=_join(prose),
                    # !! THE LINES THE PARAGRAPH SPANS, not the lines that carry a
                    # comment token. A blank line inside a run has no token, so
                    # taking them from `run` skipped it while `start..end`
                    # still spanned it -- `raw_lines` was then SHORTER than the
                    # paragraph, and anything comparing the two disagreed on an
                    # untouched file. Measured 2026-08-18: 4 paragraphs in this
                    # repo, each refused by the retired `paragraph_matches` as stale,
                    # and each one a splice that would have deleted the blank
                    # line it did not know about.
                    raw_lines=_own_characters(
                        source_lines[run[0][0] - 1 : run[-1][0]], run[0][3]
                    ),
                    # !! Same string, same reason -- see `paragraphs_lexical`. The
                    # tokenizer states the column, so the code before it is a
                    # slice and not an inference.
                    anchor=_anchor_of(source_lines, run[0][0], run[0][3]),
                )
            )
            # !! A trailing comment CLOSES its run, so a sentence wrapped onto
            # the next line becomes a SECOND paragraph and re-anchors to the
            # declaration below it. That is correct by the paragraph definition --
            # the continuation sits between two lines of code -- and wrong about
            # the prose, which is one sentence. STAMPED rather than re-cut:
            # merging would change paragraph boundaries and renumber every census,
            # and the harm is a reviewer filing `correct` against a mid-clause
            # ending the census manufactured.
            if paragraph.kind == "comment" and paragraph.start == trailing_end[0] + 1:
                paragraph.annotations.add("continues-a-trailing-comment")
                paragraph.notes.append(
                    "opens on the line after a trailing comment, so it may be"
                    " the tail of that sentence rather than a note about the"
                    " code below. A mid-clause ending here may be the split."
                )
            if paragraph.kind == "trailing-comment":
                trailing_end[0] = paragraph.end
            run.clear()

    for raw in tokenize.generate_tokens(io.StringIO(text).readline):
        if raw.type == tokenize.COMMENT:
            # ! The COLUMN when code precedes it, 0 otherwise -- one fact,
            # and its truthiness is still "this is a trailing comment".
            before = raw.line[: raw.start[1]]
            trailing = len(before.rstrip()) + 1 if before.strip() else 0
            run.append((raw.start[0], raw.line.rstrip("\n"), raw.string, trailing))
            # ! A trailing comment CLOSES its run. Its code sits before it, so
            # the next token to arrive is the following leading comment, and the
            # two merged across two blank lines -- gluing `raise original
            # DoesNotExist` to an unrelated `TODO` four lines down and handing a
            # reviewer one paragraph built from two comments.
            if trailing:
                flush()
        elif raw.type in (
            tokenize.NL,
            tokenize.NEWLINE,
            tokenize.INDENT,
        ) or raw.type in (tokenize.ENDMARKER, tokenize.DEDENT):
            continue
        else:
            flush()
    flush()

    try:
        tree = ast.parse(text)
    except SyntaxError as e:
        out.append(
            Paragraph(
                path=path.as_posix(),
                start=getattr(e, "lineno", 1) or 1,
                end=getattr(e, "lineno", 1) or 1,
                kind="unparsed",
                lines=0,
                text=f"UNPARSED ({e.msg}) -- no docstrings, no names harvested",
            )
        )
        return out

    # !! SOURCE ORDER, WHICH `ast.walk` DOES NOT GIVE. The walk is breadth
    # first, so a method nested in a class comes back after every top-level
    # declaration rather than where a reader meets it. `lineno` is the order
    # down the page, and it is the only one a human can check.
    declared = sorted(
        (n for n in ast.walk(tree) if isinstance(n, NAMED_DEFS)),
        key=lambda n: n.lineno,
    )
    # `id()`, because two declarations can be equal as AST nodes and are never
    # the same declaration. Module is 0; its declarations count from 1.
    ordinal = {id(n): i for i, n in enumerate(declared, 1)}

    for node in ast.walk(tree):
        if not isinstance(node, DOC_ANCHORS):
            continue
        doc = ast.get_docstring(node, clean=False)
        if not doc:
            continue
        stmt = node.body[0]
        start = stmt.lineno
        end = getattr(stmt, "end_lineno", stmt.lineno) or stmt.lineno
        # !! `raw_lines` IS THE FILE'S LINES, sliced, and never the AST value.
        # `ast.get_docstring` returns the string CONTENT: no quote delimiters,
        # and no indent on the first line. Stored, it made every consumer that
        # compares a paragraph to the file compare unlike things -- measured
        # 2026-08-17 on `galley.py`'s own census, `paragraph_matches` returned False
        # for all six docstring paragraphs of an UNMODIFIED file and True for all
        # five comment paragraphs, so a docstring edit was refused as stale and the
        # galley could not be set for it at all. `text` is the whole source and
        # the node carries 1-based inclusive lines, so the slice is exact.
        raw = source_lines[start - 1 : end]
        out.append(
            Paragraph(
                path=path.as_posix(),
                start=start,
                end=end,
                kind="docstring",
                # ! The PHYSICAL count, which is what `end - start` spans. The
                # AST value is one line short of a multi-line docstring, having
                # no closing-delimiter line, so `lines` and `len(raw_lines)`
                # disagreed by one on every one of them.
                lines=len(raw),
                text=re.sub(r"\s+", " ", doc).strip(),
                anchor=getattr(node, "name", "<module>"),
                declares=ordinal.get(id(node), 0),
                anchor_line=getattr(node, "lineno", 0),
                raw_lines=raw,
            )
        )
    return sorted(out, key=lambda b: b.start)
