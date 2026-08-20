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

! So the kinds split too. A reader emits `comment`, `docstring`,
`trailing-comment` and `unparsed` -- prose it found. `interval`, `margin` and
`undocumented` are the page's, because only a page knows where prose is MISSING.

! A LEAF: it imports no sibling. `foliation` is the other one, and neither knows
anything of the other -- a place has no prose in it and prose has no place until
a page puts the two together.
"""

import ast
import io
import re
import tokenize
from dataclasses import dataclass, field
from pathlib import Path


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
    # it, `def f():` and not `f`; see `census._anchor_of`.
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
    # !! THE LINE THE DECLARATION ITSELF OPENS ON, so an anchor's OTHER places
    # can be found: the `c` beside its `def` and the `b` above it. Without it a
    # consumer has to infer the line from the docstring's position, which is
    # exactly the kind of inference that breaks on the next language -- Rust's
    # doc sits BEFORE its `fn`, Python's after. 0 where none applies.
    declared_at: int = 0
    tier: str = "lexical"  # which question set this file's census can answer
    # !! WHICH PLACE THIS IS, as against where it sits -- see `foliation.address`.
    # Stamped in the path-normalising loop, the only place holding the file
    # text, the finished paragraph list and the repo-relative path at once.
    address: str = ""
    annotations: set[str] = field(default_factory=set)
    notes: list[str] = field(default_factory=list)

    @property
    def widest(self) -> int:
        """The longest PHYSICAL line this paragraph sits on, in characters.

        ! A width rule measures the line on disk, so the code a `c` paragraph sits
        beside counts: `raw_lines` holds only the paragraph's own characters, and
        `anchor` holds what precedes them on the first line.
        """
        if not self.raw_lines:
            return 0
        first = len(self.anchor) + len(self.raw_lines[0]) if self.edit_column else 0
        return max(first, *(len(ln) for ln in self.raw_lines))

    # !! THE PARAGRAPH'S OWN CHARACTERS, EXACTLY AS THE FILE HOLDS THEM -- its
    # lines whole where it owns them, and from `edit_column` onward on the first
    # line where code comes first. With `anchor` holding the code, the two
    # RECONSTRUCT that line: `anchor + raw_lines[0]` is what is on disk.
    #
    # !! THE TWO TIERS DISAGREED, AND FOUR OF SIX SHAPES COULD NOT BE WRITTEN.
    # `paragraphs_lexical` cut at the comment opener and `paragraphs_stdlib` kept the
    # whole physical line, so `galley.paragraph_matches` refused a FRESH census on
    # every lexical trailing comment (`'// note'` against `int b = 2; // note`)
    # and on every paragraph comment not at column 0 (`'/* why */'` against
    # `'    /* why */'` -- the indentation was the cut). Measured 2026-08-19.
    #
    # ! It also fed CODE to the annotators. `prose_numbers` reads this, so a
    # Python `TIMEOUT = 30  # the note says nothing` reported the number 30 as a
    # claim the prose makes. The lexical tier's own comment says that defect was
    # fixed; it was fixed on one tier.
    raw_lines: list[str] = field(default_factory=list)
    # !! THE LINES AN EDIT TO THIS PARAGRAPH OCCUPIES, which is NOT always the
    # range that ADDRESSES it. A prose paragraph is replaced, so the two coincide.
    # An empty INTERVAL is inserted into: `start` and `end` are the two lines
    # of CODE that bound it, and writing over them would delete code, so its
    # edit range is the gap between them -- `(n+1, n)` for adjacent lines,
    # which is an empty slice and therefore a pure insertion.
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
    # ! Left 0/0 by a producer, they mirror `start`/`end` -- see
    # `__post_init__`. That is what makes this safe to add without visiting
    # every construction site.
    edit_start: int = 0
    edit_end: int = 0
    # !! WHERE THE `c` PLACE BEGINS ON `edit_start`, 1-based like every other
    # position this census states -- `start`, `end`, `edit_start`, `edit_end`.
    # Two values:
    #
    #    0      the paragraph owns its lines WHOLE. Not a column: 0 is not one, and
    #           that is what makes it a sentinel rather than an accident. Every
    #           `comment`, `docstring` and `interval`.
    #    1..N   ONE PAST THE LAST CHARACTER OF CODE on that line, which is where
    #           the room beside the code starts. A `trailing-comment`, a
    #           `margin`, a paragraph comment opened after a statement. It is what
    #           lets the galley write one without deleting the code: the splice
    #           keeps `line[: edit_column - 1]`.
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
    edit_column: int = 0

    def __post_init__(self) -> None:
        """Default the edit range to the addressing range."""
        if not self.edit_start and not self.edit_end:
            self.edit_start, self.edit_end = self.start, self.end


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


@dataclass(frozen=True)
class Language:
    """What the LEXICAL tier needs to find prose in a language it only lexes.

    Adding a language is this record -- data, no code.

    Attributes:
        doc_line: line-comment openers that mean DOC rather than ordinary
            comment (Rust `///`, `//!`). Empty when the language marks docs
            some other way.
        doc_block: paragraph openers that mean DOC (`/**`). Same idea.
        doc_is_structural: the doc is a string in a declaration's body (Python)
            or the run above a declaration (Go). Both need structure to decide,
            so this tier reports `comment` and annotates the paragraph.
        quotes: string delimiters, so a marker inside a literal is skipped.
        spanning_quotes: delimiters whose literal may cross LINES -- a JS
            template literal, a Java text paragraph. ! `_strip_strings` is per-line
            and carries no open-quote state, so a comment marker INSIDE one of
            these reads as a comment; `prove_unchanged` refuses such a file
            rather than proving it. Empty where a language has none.
    """

    name: str
    extensions: tuple[str, ...]
    line_comment: tuple[str, ...]
    block_comment: tuple[tuple[str, str], ...] = ()
    doc_line: tuple[str, ...] = ()
    doc_block: tuple[str, ...] = ()
    doc_is_structural: bool = False
    quotes: tuple[str, ...] = ('"', "'")
    spanning_quotes: tuple[str, ...] = ()


# ! Ordering inside a field is significant: openers are matched longest-first,
# so `///` must precede `//` or every Rust doc line loses one slash into the
# prose and the annotations then run over corrupted text.
LANGUAGES: tuple[Language, ...] = (
    Language(
        "python",
        (".py", ".pyi"),
        ("#",),
        doc_is_structural=True,
        # !! A triple quote spans lines, and Python reaches the LEXICAL
        # path whenever `ast.parse` fails -- syntax newer than the floor,
        # a file mid-edit. Declaring nothing here left the same fail-open
        # that was closed for JS the same day: two files differing only
        # in a `#` line INSIDE a triple-quoted literal fingerprinted
        # identically and the proof reported PROVEN.
        spanning_quotes=('"""', "'''"),
    ),
    Language(
        "rust",
        (".rs",),
        ("///", "//!", "//"),
        (("/*", "*/"),),
        doc_line=("///", "//!"),
    ),
    Language("go", (".go",), ("//",), (("/*", "*/"),), doc_is_structural=True),
    Language(
        "c-family",
        (".c", ".h", ".cpp", ".hpp", ".cc", ".java", ".cs", ".swift", ".kt"),
        ("//",),
        (("/*", "*/"),),
        doc_block=("/**",),
        # ! A Java TEXT BLOCK spans lines the same way, and a `//` inside one is
        # not a comment.
        spanning_quotes=('"""',),
    ),
    Language(
        "js-family",
        (".js", ".jsx", ".ts", ".tsx", ".mjs"),
        ("//",),
        (("/*", "*/"),),
        doc_block=("/**",),
        quotes=('"', "'", "`"),
        spanning_quotes=("`",),
    ),
    Language("ruby", (".rb",), ("#",), (("=begin", "=end"),), doc_is_structural=True),
    Language("shell", (".sh", ".bash", ".zsh"), ("#",)),
    Language("sql", (".sql",), ("--",), (("/*", "*/"),)),
    Language("lua", (".lua",), ("--",), (("--[[", "]]"),)),
    Language("toml-ini", (".toml", ".ini", ".cfg"), ("#",)),
    Language("yaml", (".yaml", ".yml"), ("#",)),
)

BY_EXT = {ext: lang for lang in LANGUAGES for ext in lang.extensions}

# The ladder is named by the QUESTION each rung answers, not by the library
# that happens to answer it. Only the top rung knows which declaration a paragraph
# belongs to.
TIER_ANSWERS = {
    "tokenized": "paragraphs, annotations, and DOCSTRING anchors",
    "lexical": "paragraphs and annotations only",
}


def language_for(path: Path) -> Language | None:
    """The language record for a path, or None when the suffix is unknown."""
    return BY_EXT.get(path.suffix.lower())


def _strip_strings(line: str, quotes: tuple[str, ...]) -> str:
    """Blank out string literals so a marker inside one stays out of the census.

    `url = "http://x"` holds `//` in most C-family languages. It handles
    single-line literals with backslash escapes; raw strings, heredocs and
    template nesting are where this tier stops and the lexer starts.
    """
    out, quote, esc = [], "", False
    for ch in line:
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
        if ch in quotes:
            quote = ch
            out.append(" ")
            continue
        out.append(ch)
    return "".join(out)


def _own_characters(span: list[str], column: int) -> list[str]:
    """A paragraph's own characters: its lines, cut at `column` on the first.

    !! ONE RULE FOR BOTH TIERS, which is what B3 is. `paragraphs_lexical` cut at the
    comment OPENER and `paragraphs_stdlib` kept the whole physical line, so the two
    stored different things and `galley.paragraph_matches` could not be written to
    satisfy both -- it refused a FRESH census on four of six comment shapes.

    ! With `anchor` holding the code, `anchor + raw_lines[0]` reconstructs the
    first line exactly. Storing the whole line here instead would put the code
    in two fields, which is the conflation the anchor was added to end.

    Args:
        span: the paragraph's physical lines, without endings.
        column: the paragraph's `edit_column`; 0 when it owns its lines whole.

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
    storing `['// note']` made `galley.paragraph_matches` answer False on an
    UNTOUCHED file. The fix is not to make both tiers store the whole line,
    which conflates the anchor with the prose in one string -- the conflation
    that produced the suffix-test defect twice. Roy: *"not marking or saving the
    anchor is causing the problem."*

    ! It is `""` for a paragraph that owns its lines whole, which has no code on its
    line to be anchored to.

    Args:
        lines: the file's lines, without endings.
        line_no: 1-based line the paragraph opens on.
        column: that paragraph's `edit_column`.

    Returns:
        The code preceding the paragraph on its first line, right-stripped.
    """
    if not column or not 1 <= line_no <= len(lines):
        return ""
    return lines[line_no - 1][: column - 1]


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
    # ! The line the last trailing comment ended on. Measured: this tier splits a
    # wrapped trailing comment exactly as `paragraphs_stdlib` does, so it needs the
    # same stamp. A list because `flush` is a closure and rebinds nothing.
    trailing_end = [_NO_TRAILING]

    # !! WHERE THE RUN'S FIRST LINE STOPS BEING CODE -- the `edit_column` this
    # tier states, one past the last character of code, or 0 when the run owns
    # its lines whole.
    #
    # ! `trailing` does not answer it: a MULTI-LINE paragraph comment opened after a
    # statement flushes with `trailing=False`, because by then the run spans
    # several lines. A list because `flush` is a closure and rebinds nothing.
    partial_first = [0]

    def flush(trailing: bool = False) -> None:
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
        stripped = raw[0].strip()
        is_doc = stripped.startswith(lang.doc_line) if lang.doc_line else False
        if lang.doc_block and stripped.startswith(lang.doc_block):
            is_doc = True
        if is_doc:
            kind = "docstring"
        else:
            kind = "trailing-comment" if trailing else "comment"
        paragraph = Paragraph(
            path=path.as_posix(),
            start=run[0][0],
            end=run[-1][0],
            kind=kind,
            lines=counted_lines(raw),
            text=_join(raw, openers),
            raw_lines=span,
            tier="lexical",
            edit_column=partial_first[0],
            # !! THE LEXER ALREADY HAS THIS STRING. It found the opener in
            # order to cut there, so the characters before it were known one
            # step earlier and were thrown away. Roy, 2026-08-19: *"the lexer
            # either knows what is before the trailing comment and can snag the
            # whole string or it is broken."*
            anchor=_anchor_of(lines, run[0][0], partial_first[0]),
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
            run.append((n, raw_line.rstrip()))
            if in_block[1] in raw_line:
                in_block = None
                flush()
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
            if run:
                pending.append((n, ""))
            continue
        code = _strip_strings(raw_line, lang.quotes)
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
            flush()
            # !! CUT AT THE OPENER, like the line-comment path below does. The
            # whole raw line was appended, so `int b = 2; /* note */` was
            # censused as one `comment` paragraph whose TEXT held the statement --
            # executable code handed to four reviewers as prose, run through the
            # annotation regexes, and dropped from `code_lines`, which moved
            # every interval boundary in the file. Measured 2026-08-17, the same
            # shape as the `//`-before-`/*` case fixed directly above.
            opens_at = code.index(opened[0])
            tail = code[opens_at + len(opened[0]) :]
            closes_here = opened[1] in tail
            after = (
                tail[tail.index(opened[1]) + len(opened[1]) :] if closes_here else ""
            )
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
                continue
            # ! Only the run's FIRST line decides it -- `flush()` above emptied
            # the run, so this is that line. A continuation line of a paragraph
            # comment is entirely prose whatever surrounds the run.
            partial_first[0] = (
                len(code[:opens_at].rstrip()) + 1 if code[:opens_at].strip() else 0
            )
            run.append((n, raw_line[opens_at:].rstrip()))
            if closes_here:
                # ! Code BEFORE the opener makes it a trailing comment, which is
                # what it is: prose about the statement on its own line.
                flush(trailing=bool(code[:opens_at].strip()))
            else:
                in_block = opened
            continue
        if code.strip().startswith(openers):
            run.extend(pending)
            pending.clear()
            run.append((n, raw_line.rstrip()))
            continue
        flush()  # ! CODE ends a paragraph; a blank line does not
        at = line_at
        if at >= 0:
            # ! `flush()` above emptied the run, so this line is the first
            # one and the code before `at` is what makes it trailing. A line
            # comment runs to end of line, so there is no other side to test.
            partial_first[0] = len(code[:at].rstrip()) + 1 if code[:at].strip() else 0
            run.append((n, raw_line[at:].rstrip()))
            flush(trailing=True)  # its own paragraph, anchored to the code on that line
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
            out.append(
                paragraph := Paragraph(
                    path=path.as_posix(),
                    start=run[0][0],
                    end=run[-1][0],
                    kind="trailing-comment" if run[0][3] else "comment",
                    # ! ONE PAST THE LAST CHARACTER OF CODE on the line, or
                    # 0 for a leading comment. NOT the `#`: the whitespace
                    # between a statement and its comment belongs to the `c`
                    # place, so a `margin` and the trailing comment that would
                    # replace it carry the same column.
                    edit_column=run[0][3],
                    lines=counted_lines(prose),
                    text=_join(prose),
                    # !! THE LINES THE PARAGRAPH SPANS, not the lines that carry a
                    # comment token. A blank line inside a run has no token, so
                    # taking them from `run` skipped it while `start..end`
                    # still spanned it -- `raw_lines` was then SHORTER than the
                    # paragraph, and anything comparing the two disagreed on an
                    # untouched file. Measured 2026-08-18: 4 paragraphs in this
                    # repo, each refused by `galley.paragraph_matches` as stale,
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
                declared_at=getattr(node, "lineno", 0),
                raw_lines=raw,
            )
        )
    out.extend(_undocumented(path, tree, declared, ordinal))
    return sorted(out, key=lambda b: b.start)


def _undocumented(
    path: Path, tree: ast.AST, declared: list, ordinal: dict[int, int]
) -> list[Paragraph]:
    """An `a` entry for every declaration that has NO docstring.

    !! THE EMPTY ONES ARE THE POINT OF THE SERIES. An `add` says a constraint
    holds in code and appears in no prose, so it has to cite the place the prose
    is missing from -- and until this ran, a function with no docstring had no
    such place. Measured 2026-08-18 on a four-declaration file: the census
    emitted two docstring paragraphs and left three declarations with nowhere to
    cite. This is the same hole `intervals` closed for gaps.

    ! It occupies NO LINES, exactly like an empty interval, and `OCCUPIES_NOTHING`
    says so. Its `start`-`end` span the declaration and its first statement so a
    citation resolves to real lines; its EDIT range is the empty slice before
    that statement, which is a pure insertion.

    ! The `a` address and the `b` gap at the same spot are both real and are not
    a collision: `a4` is the declaration's documentation and `bN` is the gap
    between two code lines. An `add` on the first writes a docstring, on the
    second a comment run.
    """
    out: list[Paragraph] = []
    for node in [tree, *declared]:
        if not isinstance(node, DOC_ANCHORS) or ast.get_docstring(node, clean=False):
            continue
        body = getattr(node, "body", [])
        if not body:
            continue
        first = body[0].lineno
        out.append(
            Paragraph(
                path=path.as_posix(),
                # !! LINE 0 -- IT OCCUPIES NO LINE, because the docstring is not
                # written yet. Roy ruled the empty case 2026-08-19. Given the
                # declaration's own range it swallowed whatever sat between the
                # `def` and its first statement: a module with no docstring
                # spanned lines 1-4 and the locator answered `a0` for the
                # comment at 3 and the `def` at 4, both of which belong to other
                # paragraphs. Its EDIT range still says where the prose would go.
                start=0,
                end=0,
                kind="undocumented",
                lines=0,
                text="",
                anchor=getattr(node, "name", "<module>"),
                declares=ordinal.get(id(node), 0),
                declared_at=getattr(node, "lineno", 0),
                # The EDIT: `first..first-1` is empty, so writing it INSERTS
                # above the first statement rather than overwriting it.
                edit_start=first,
                edit_end=first - 1,
            )
        )
    return out


def tier_for(lang: Language) -> str:
    """The highest rung reachable for this language, here and now.

    One definition, read by the dispatcher and by `--languages`, so the listing
    and the run report the same tier.
    """
    return "tokenized" if lang.name == "python" else "lexical"
