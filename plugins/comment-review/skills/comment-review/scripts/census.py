"""Stage 2, COLLATE: the pCST -- every line of these files classified, in order.

    python census.py [--repo D] [--census-only] [--json] [--out PATH] <paths>

A pCST is a *pseudo* Concrete Syntax Tree: this line is code, this PART of a
line is code, this line is comment, this line is docstring. Pseudo because a real
CST would carry the names and the symbols precisely, and this carries only which
lines are which -- which is what a reviewer of COMMENTS needs and no more.

Every such line belongs to a PARAGRAPH, and a paragraph is addressed by the subject its
prose answers to: an INTERVAL between two lines of code, or a DECLARATION. A
comment is about the code it sits with, so its address counts code lines; a
docstring is about the thing it documents, so its address counts declarations.

The reviewers are handed this list, so it bounds everything they may rule on.
! Most of it holds no prose -- an empty `interval`, an `undocumented`
declaration -- and those are ADDRESSABLE, so an `add` can cite the place its
missing sentence belongs in, and nobody owes them a record. Coverage is over the
paragraphs that HOLD prose.

**Every file handed in is censused, or this errors** -- a file it could not read
or parse, or whose suffix has no language record, is named and the run exits
nonzero, because a paragraph missing from the census is a paragraph nobody reviews.

Read-only. It calls `annotate.py` on each paragraph for stage 3, and `repo.py` for
the facts about the checkout that both need.

A paragraph is built at the TIER available for its file's language. Both tiers find
the same paragraphs, and the tier says what else the file can answer:

  tokenized  a lexer + AST (Python, from the stdlib)   + DOCSTRING anchors
  lexical    a comment-syntax record                   paragraphs

! Only a STRUCTURAL doc carries an anchor, and only Python has one: the doc is a
string inside a declaration's body, so the AST names the declaration. A MARKED
doc (`///`, `/**`) is a comment run like any other. Every other anchor comes from
a reviewer READING the file, so a placement finding is a CANDIDATE in every
language.

! Tier counts are AGGREGATED over the run. A polyglot run reports one total per
tier, so read the per-file tier stamp to see which file reached which.
`--languages` lists the languages known and the tier each reaches.
"""

import argparse
import ast
import io
import json
import re
import sys
import tokenize
from collections import Counter, defaultdict
from contextlib import redirect_stdout
from dataclasses import dataclass
from itertools import pairwise
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from addresser import (  # noqa: E402  -- path shim must run first
    SEPARATOR,
    attach,
    code_lines_of,
    flatten,
    foliate,
)
from annotate import (  # noqa: E402  -- path shim must run first
    SYMBOLISH,
    annotate,
    prose_numbers,
)
from page import (  # noqa: E402  -- path shim must run first
    FRONT_MATTER,
    HOLDS_NO_PROSE,
    OCCUPIES_NOTHING,
    Paragraph,
)
from repo import (  # noqa: E402  -- path shim must run first
    EXCLUDED_DIRS,
    PARSE_ERRORS,
    READ_ERRORS,
    path_index,
    tracked_paths,
)

# Tuples, so `DOC_ANCHORS` is built by concatenation and both go straight to
# `isinstance`.
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


def _walk(root: Path):
    """Every file under `root` this script has a language record for.

    ! Filters on `BY_EXT`, so every language `--languages` advertises is walked.
    Hardcoded to `*.py`, the scan went Python-only, and a file the walk skips is
    absent from the NOT CHECKED list too -- the run then reports a full census of
    a fraction of the tree.
    """
    if root.is_file():
        yield root
        return
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.suffix.lower() in BY_EXT:
            # !! RELATIVE to the root being walked. Matched against `p.parts`
            # this tested every ANCESTOR too, so a checkout living anywhere
            # under a directory called `venv`, `.venv`, `node_modules`,
            # `site-packages`, `__pycache__` or `.git` excluded ITSELF.
            # Measured 2026-08-17: `code_names` harvested 0 names from a repo
            # under `.../venv/myproject`, and nothing joined `unread`, so the
            # NOT CHECKED list stayed empty and the run read as complete --
            # every `names-a-symbol` a false obituary, handed to four reviewers
            # as settled fact.
            if not EXCLUDED_DIRS.intersection(p.relative_to(root).parts):
                yield p


# The two gaps in the name corpus that are NOT read failures, named so a caller
# can tell them apart from one. Every row `code_names` returns reads alike --
# `<path> (<reason>)` -- and a reporting caller that treated all of them as
# unreadable files told a polyglot repo that six files "could not be read" and
# then instructed the reader to wait for a list that can never empty.
NO_HARVESTER = "no name harvester for"
WALKED_TREE = "name corpus built by WALKING the tree"


def code_names(
    roots: list[Path], tracked: set[Path] | None = None
) -> tuple[set[str], list[str]]:
    """Every name the tree DEFINES, harvested from the AST.

    A corpus built from raw text contains the comments being checked, so every
    obituary resolves against itself and the check always passes. Unreadable
    files are RETURNED alongside the names: a hole in the corpus turns every
    symbol defined only there into a false obituary, which fails loud and wrong.

    ! TRACKED files only, when git can say which. A vendored, generated or
    gitignored tree under the repo root otherwise donates its whole namespace,
    so a symbol the repo defines nowhere resolves ALIVE. That failure is SILENT
    and one-sided: it can hide an obituary, and manufactures none.

    Args:
        roots: directories or files to harvest.
        tracked: absolute paths git reports as tracked, or None when git could
            not answer -- in which case the whole tree is walked and the caller
            is told, so a change in coverage arrives with the result.

    Returns:
        The set of defined names, and the rows naming every gap in it. A row
        holding `NO_HARVESTER` is a KNOWN hole and a row holding `WALKED_TREE`
        is a caveat about the whole corpus; anything else is a file this
        process genuinely could not read or parse. A caller that tells the
        three apart says so with those two constants -- the three read alike as
        prose, and a caller matching on the prose reclassifies them silently
        the next time this wording changes.
    """
    names: set[str] = set()
    unread: list[str] = []
    if tracked is None:
        unread.append(
            f"{WALKED_TREE} (not a git checkout, or git unavailable) -- "
            "untracked or vendored code may mask an obituary"
        )
    for root in roots:
        for p in _walk(root):
            if tracked is not None and p.resolve() not in tracked:
                continue
            lang = language_for(p)
            # ! A non-Python file is a KNOWN hole, reported as one. Parsed as
            # Python it came back `a.go (SyntaxError)`, which reads as "your
            # file is malformed" and sends a reviewer after an invented defect.
            # Liveness in these languages needs its own harvester; this names
            # the gap until there is one.
            if lang is None or lang.name != "python":
                name = lang.name if lang else "unknown"
                unread.append(f"{p.as_posix()} ({NO_HARVESTER} {name})")
                continue
            try:
                tree = ast.parse(p.read_text(encoding="utf-8"))
            except PARSE_ERRORS as e:
                unread.append(f"{p.as_posix()} ({type(e).__name__})")
                continue
            names.add(p.stem)
            harvest_constants = not (p.name.startswith("test_") or "tests" in p.parts)
            for node in ast.walk(tree):
                if isinstance(node, NAMED_DEFS):
                    names.add(node.name)
                elif isinstance(node, ast.Name):
                    names.add(node.id)
                elif isinstance(node, ast.Attribute):
                    names.add(node.attr)
                elif isinstance(node, ast.arg):
                    names.add(node.arg)
                elif isinstance(node, ast.alias):
                    names.add((node.asname or node.name).split(".")[0])
                elif harvest_constants and isinstance(node, ast.Constant):
                    if isinstance(node.value, str) and SYMBOLISH.match(node.value):
                        names.add(node.value)
    return names, unread


def code_lines(text: str, prose: list[Paragraph]) -> set[int]:
    """The code lines of this file, as a set -- `addresser.code_lines_of`.

    !! ONE IMPLEMENTATION, and it is the addresser's, because an address is
    counted off this set and the two must not be able to disagree. This is the
    same rule over `Paragraph`s rather than dicts; the rule itself is written where
    it runs.
    """
    return set(code_lines_of(text, [vars(b) for b in prose]))


def lines_of_code(text: str, prose: list[Paragraph]) -> list[tuple[int, str]]:
    """The file's lines of code, in order, each with the line it sits on.

    ! What the WALK is given. The line positions the trigger and never numbers
    it -- see `addresser.foliate`.

    !! THE CHARACTERS COME FROM THAT LINE'S `c`, NEVER RE-CUT HERE. Every code
    line has exactly one `c` -- a `trailing-comment`, or the `margin` standing
    in for one -- and it already states where the code stops. Cutting the line
    again answers `'    return os  # why'` where the `c` for the same line
    answers `'    return os'`: two computations of one fact, which is what
    `whole_lines` was removed for.
    """
    lines = text.splitlines()
    beside = {b.start: b.anchor for b in prose if b.edit_column}
    return [
        (n, beside.get(n) or lines[n - 1].rstrip())
        for n in sorted(code_lines(text, prose))
        if 1 <= n <= len(lines)
    ]


def documentable(prose: list[Paragraph], text: str) -> set[int]:
    """Which lines of code DECLARE something able to carry documentation.

    !! ONLY A PARSER KNOWS, so the census states it and the walk consumes it.
    `declares` is that answer: 0 for the module and 1..N for its declarations
    in source order, which the AST walk established. A tier that resolves no
    declarations returns an empty set, and the file has an `a0` and no more.

    Returns:
        Indices into `lines_of_code`, so the walk can ask "does this trigger
        emit an `a`" without knowing what a declaration is.
    """
    declaring = {
        b.declared_at
        for b in prose
        if isinstance(b.declares, int) and b.declares >= 1 and b.declared_at
    }
    return {i for i, (n, _) in enumerate(lines_of_code(text, prose)) if n in declaring}


def paragraphs_in(prose: list[Paragraph], prev: int, nxt: int) -> list[Paragraph]:
    """The prose paragraphs OVERLAPPING the gap between two code lines.

    !! OVERLAP, NOT START. A comment opened after a statement begins ON the
    bounding code line and runs into the gap below it, so `prev < b.start` was
    False for it: the gap read as EMPTY, an interval was emitted, and the
    comment's own second line carried two addresses. Measured 2026-08-19 on
    `let b = 2; /* opens` / `and closes */` -- line 3 answered to both.

    ! A trailing comment still holds no gap: it starts and ends on the code
    line, so `prev < b.end` is False.
    """
    return [
        b
        for b in prose
        if b.kind not in OCCUPIES_NOTHING and prev < b.end and b.start < nxt
    ]


def intervals(path: Path, text: str, prose: list[Paragraph]) -> list[Paragraph]:
    """Every gap between two lines of code that holds no prose.

    A gap holding a comment run IS that run's paragraph, so only the empty ones are
    emitted here and the census stays one paragraph per interval either way.

    ! **The file boundary counts as a bound.** There is no code line above a
    module docstring and none below a comment at EOF, so the first and last
    intervals are bounded by the file itself rather than special-cased away. A
    file with no code at all is therefore one interval.

    ! `start` and `end` are the BOUNDING CODE LINES, not the blank lines
    between them, because a zero-width gap has no lines of its own and every
    citation in this system has to resolve. Two adjacent code lines give an
    interval whose range is those two lines.

    !! `edit_start` and `edit_end` are the OTHER range -- the gap itself, which
    is what an edit to this interval occupies. They are set here and nowhere
    else, because the edges walked here carry the file-boundary sentinels that
    `start` and `end` clamp away. See `Paragraph`.
    """
    lines = text.splitlines()
    last = len(lines)
    if last == 0:
        return []
    code = sorted(code_lines(text, prose))
    edges = [0, *code, last + 1]
    out: list[Paragraph] = []
    for prev, nxt in pairwise(edges):
        holders = paragraphs_in(prose, prev, nxt)
        # !! A DOCSTRING DOES NOT HOLD A GAP'S `b`. It has its own `a`, so the
        # gap still needs a `b` place -- otherwise there is nowhere to cite a
        # comment ABOVE a docstring. Measured 2026-08-19 before this: 129 `b`
        # places absent from 13 shipped files, `b0` among them in every one,
        # so no file could be given a comment above its module docstring.
        if any(b.declares < 0 for b in holders):
            continue  # a comment IS this gap's `b`
        # !! THE GAP ITSELF, NOT THE CODE LINES BOUNDING IT. Those are `c`
        # addresses now and a line has ONE address, so including them made a
        # third of this repo's lines answer to two -- 2,305 of 6,775, measured
        # 2026-08-19, every one a code line ending one gap and starting the
        # next. A gap with no lines of its own is at line 0, like an absent
        # docstring: addressable, on no line.
        lo, hi = prev + 1, min(nxt - 1, last)
        # ! A docstring already occupies this gap's LINES, so its `b` is a place
        # with none -- line 0, the same answer an absent docstring gives.
        if holders or lo > hi:
            lo = hi = 0
        out.append(
            Paragraph(
                path=path.as_posix(),
                start=lo,
                end=hi,
                kind="interval",
                lines=0,
                text="",
                # The EDIT: unclamped, so the file boundary keeps its side.
                # `prev + 1 .. nxt - 1` is THE GAP ITSELF -- its own blank
                # lines, not the code lines that bound it. Empty for adjacent
                # code lines, and `1..0` above the first line of a file, which
                # is an empty range and so a pure insertion.
                #
                # ! The gap below the last code line is `last+1..last` only
                # when that line ENDS the file. With trailing blanks it spans
                # them, which is right: they are the gap.
                # !! A DOCSTRING IN THIS GAP MAKES THE EDIT AN INSERTION ABOVE
                # IT, never a replacement of it. The gap's lines are the
                # docstring's, so writing the whole range would overwrite the
                # docstring with a comment -- and `paragraph_matches` reported the
                # place stale on a FRESH census, because those lines are not
                # blank. `prev+1 .. prev` is an empty slice: prose lands above.
                edit_start=prev + 1,
                edit_end=prev if holders else nxt - 1,
            )
        )
    return out


def tier_for(lang: Language) -> str:
    """The highest rung reachable for this language, here and now.

    One definition, read by the dispatcher and by `--languages`, so the listing
    and the run report the same tier.
    """
    return "tokenized" if lang.name == "python" else "lexical"


def _repo_relative(path: Path, repo: Path) -> str:
    """`path` as `repo` sees it: posix, relative, no `..`.

    Args:
        path: the file censused.
        repo: the root every citation resolves against.

    Returns:
        The posix path relative to `repo`. ! A file NOT under `repo` keeps the
        path AS IT WAS PASSED, which may itself be relative -- run from a
        subdirectory, `--repo /r ../other/x.py` records `../other/x.py`. There
        is no relative-to-`repo` form of such a file and inventing one with
        `..` would hand a consumer a path that escapes the root it was given,
        so it is passed through unresolved and the consumers refuse it:
        `galley.py` writes nothing that lands outside `--out`.
    """
    try:
        return path.resolve().relative_to(repo).as_posix()
    except ValueError:
        return path.as_posix()


def census_for(
    path: Path, text: str, lang: Language, rel: str | None = None
) -> list[Paragraph]:
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
    if not any(b.kind == "unparsed" for b in got):
        got = got + intervals(path, text, got) + margins(path, text, got)
        fill_the_gaps(text, got)
        # ! AFTER the gaps are filled, so every paragraph's place in its gap is
        # settled before it is told what it sits above.
        # ! BEFORE the anchors, because a run that is FRONT MATTER is anchored
        # to the module rather than to the code below it, and this is what says
        # which runs those are.
        mark_front_matter(got)
        # !! THE WALK EMITS EVERY PLACE, AND THE PARAGRAPHS ARE TIED TO THEM.
        # Reversed -- each paragraph computing its own folio -- a place existed
        # only when prose happened to fill it, which is how `b0` and `b1` came
        # to be mutually exclusive. `addresser` owns both halves: the foliation
        # assigns the numbering, `attach` reads which place this prose sits in,
        # and the anchor comes from the walk that emitted it rather than from a
        # second pass that could disagree with the first.
        foliation = foliate(lines_of_code(text, got), documentable(got, text))
        flat = flatten(rel if rel is not None else path.as_posix())
        for b in got:
            place = attach(vars(b), foliation)
            b.address = f"{flat}@{place}" if place else ""
            b.anchor = foliation.places.get(place, b.anchor)
    for b in got:
        b.tier = tier_for(lang)
    return sorted(got, key=lambda b: (b.start, b.end))


# The annotation, and the two shapes that earn it.
# ! DEFINED IN `page.py`, the leaf, because `addresser` reads it too and
# cannot import this module. Re-exported here so the many readers that
# already say `census.FRONT_MATTER` keep working.
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


def margins(path: Path, text: str, prose: list[Paragraph]) -> list[Paragraph]:
    """A `c` place for every code line that carries no trailing comment.

    !! WITHOUT IT THERE IS NOWHERE TO PUT ONE. Roy, 2026-08-19: without the
    empty `c`s "you can't specify that the comment belongs at the end of the
    code line". An `add` cites the place its missing prose belongs, so a code
    line with no trailing comment needs a place exactly as a gap with no prose
    does -- which is what `intervals` already gives the `b` series.

    ! It occupies no line of its OWN: the line is CODE and stays code. What it
    holds is the room after the statement.

    ! `raw_lines` holds the room itself -- whatever follows the code, which is
    nothing unless the line ends in whitespace. The code it sits beside is the
    ANCHOR, and `galley.paragraph_matches` checks that half against the file.
    """
    lines = text.splitlines()
    # ! THE SAME FACT `address` reads. A line already carrying prose that SHARES
    # it has no room left -- and that is any paragraph with `whole_lines` False, not
    # only a `trailing-comment`. Keyed on the kind, a paragraph comment opened after
    # a statement got a margin for room it already occupies.
    taken = {b.start for b in prose if b.edit_column}
    return [
        Paragraph(
            path=path.as_posix(),
            start=n,
            end=n,
            kind="margin",
            lines=0,
            text="",
            # ! ITS OWN CHARACTERS, which is whatever follows the code --
            # nothing, for a line with no trailing comment. The code is in
            # `anchor`; storing it here too would put one fact in two fields.
            raw_lines=[lines[n - 1][len(lines[n - 1].rstrip()) :]],
            edit_start=n,
            edit_end=n,
            # !! ONE PAST THE LAST CHARACTER OF CODE -- the same rule a
            # trailing comment on this line would follow, so the two are the
            # same place whether or not prose is in it. The prose supplied for
            # an `add` here carries its own leading separator, exactly as an
            # `add` on an `interval` carries its own indentation.
            edit_column=len(lines[n - 1].rstrip()) + 1,
            # ! The whole line, because the whole line is code. A `margin` and
            # the trailing comment that would replace it are the same place, so
            # they carry the same anchor as well as the same column.
            anchor=lines[n - 1].rstrip(),
        )
        for n in sorted(code_lines(text, prose))
        if n not in taken
    ]


def _not_censused(files: list[Path], unreadable: list[str]) -> str:
    """The refusal, worded ONCE for both output modes.

    !! The reviewers are handed the census, so a file missing from it is paragraphs
    nobody reviews and nothing downstream notices. `--json` used to return 0
    with a SHORT array on exactly the input the text path refused -- and
    `--json --out` is the route `SKILL.md` mandates for the census stage 5
    parses, so the coverage check then certified every paragraph accounted for over
    paragraphs that were never collected.
    """
    listed = "\n".join(f"    {u}" for u in unreadable)
    return (
        f"NOT CENSUSED -- these are gaps, not passes:\n{listed}\n"
        f"ERROR: {len(unreadable)} of {len(files)} files handed in were not"
        " censused. Every file is censused or this errors."
    )


def main() -> int:
    """Build the census, resolve its annotations, print both."""
    # UTF-8 with replacement, so an em-dash in someone's docstring still prints
    # on a console whose encoding lacks it.
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--repo", default=".", help="repo root for citation resolution")
    ap.add_argument("--census-only", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument(
        "--filtered",
        action="store_true",
        help="the reviewer's view: prose paragraphs, and one line per run of intervals",
    )
    ap.add_argument(
        "--out", metavar="PATH", help="write the report to PATH, not stdout"
    )
    ap.add_argument(
        "--languages",
        action="store_true",
        help="list known languages and the tier each reaches, then exit",
    )
    args = ap.parse_args()

    # ! WRITES ITS OWN FILE. A shell redirect is refused outright by a
    # worktree-isolated harness -- "too complex to verify that it stays inside
    # the worktree" -- and the JSON census is what the stage-5 join parses, so
    # the only documented route to it was unrunnable there.
    if args.out:
        with open(args.out, "w", encoding="utf-8", newline="") as fh:
            with redirect_stdout(fh):
                return _report(args)
    return _report(args)


def _report(args: argparse.Namespace) -> int:
    """Everything the run prints, so `--out` can wrap it in one place."""
    if args.languages:
        print(f"{'language':<10} {'tier':<11} extensions")
        for lang in LANGUAGES:
            exts = " ".join(lang.extensions)
            print(f"{lang.name:<10} {tier_for(lang):<11} {exts}")
        print("\nA suffix not listed is named, and the census exits nonzero.")
        return 0

    repo = Path(args.repo).resolve()
    targets = [Path(p) for p in args.paths]
    files = sorted({f for t in targets for f in _walk(t)})
    known, unread = code_names([repo], tracked_paths(repo))
    paths = path_index(repo)

    census: list[Paragraph] = []
    # A path argument that matched no file joins `unreadable`, so a typo errors
    # on the same rule every other gap does.
    unreadable: list[str] = [
        f"{t.as_posix()} (matched no files)" for t in targets if not any(_walk(t))
    ]
    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
        except READ_ERRORS as e:
            unreadable.append(f"{path.as_posix()} ({type(e).__name__})")
            continue
        lang = language_for(path)
        if lang is None:
            unreadable.append(f"{path.as_posix()} (no language record for its suffix)")
            continue
        # !! EVERY PARAGRAPH'S PATH IS REPO-RELATIVE. It is what `--repo` is for:
        # the census, the file lists and every citation a reviewer writes all
        # resolve against that root, so a paragraph carrying an absolute path is a
        # paragraph no consumer can place. It happened whenever the run was handed
        # absolute file arguments, which is how a task agent that resolved its
        # own paths would call this.
        #
        # !! Measured 2026-08-17: `galley.py` joins `out / paragraph["path"]`, and
        # in Python an absolute right-hand side WINS a join -- so the galley
        # wrote over the source file, put nothing under `--out`, and printed
        # that it had succeeded. The module whose one promise is "nothing under
        # `--repo` is touched" was editing the tree under review.
        #
        # ! A file outside the repo keeps the path AS IT WAS PASSED -- see
        # `_repo_relative`, which says what that means. `galley.py` refuses to
        # write such a paragraph rather than guessing where it belongs.
        # ! HOISTED. `_repo_relative` calls `Path.resolve()`, a filesystem
        # call, and both arguments are the same for every paragraph of a file.
        # Measured 2026-08-18: 120 us a call, so one 793-paragraph file spent
        # 95 ms resolving one path 793 times.
        rel = _repo_relative(path, repo)
        # !! A PATH HOLDING THE SEPARATOR CANNOT BE ADDRESSED, so it is a GAP
        # and not a paragraph with a broken name. `flatten` joins segments on `:`,
        # which Windows forbids in a filename; POSIX forbids only `/` and NUL,
        # so a POSIX checkout can hold `a:b.py`, whose address would be the
        # address of `a/b.py`. That is the collision the separator was chosen to
        # end -- it was `.` until 2026-08-19, and `a/b.py` and `a.b.py` shared
        # every address they had.
        #
        # ! IT READS THE REPO-RELATIVE PATH, WHICH IS THE ONE ADDRESSED. The
        # absolute path holds a colon on every Windows run -- the drive letter
        # -- so checking `path` here refuses the whole tree.
        if SEPARATOR in rel:
            unreadable.append(f"{rel} (a path may not hold '{SEPARATOR}')")
            continue
        # ! THE REPO-RELATIVE PATH GOES IN, so the census comes back addressed
        # against the root every citation resolves to. It was stamped afterwards
        # for as long as `census_for` returned an unaddressed census, which is
        # the split that let a direct caller receive half a census.
        try:
            got = census_for(path, text, lang, rel)
        except Exception as e:  # a parse failure is REPORTED, as a gap
            unreadable.append(f"{path.as_posix()} ({type(e).__name__}: {e})")
            continue
        for b in got:
            b.path = rel
        census.extend(got)

    for b in census:
        annotate(b, known, paths, repo)

    # repeated-literal needs the whole census, so it is a second pass. A number
    # written twice is a hand-copied value, and the copies drift; one written
    # once is just a number.
    seen: Counter[str] = Counter()
    where: dict[str, set[str]] = defaultdict(set)
    for b in census:
        for n in prose_numbers(b.text, b.raw_lines):
            seen[n] += 1
            where[n].add(f"{b.path}:{b.start}")
    for b in census:
        for n in prose_numbers(b.text, b.raw_lines):
            if seen[n] > 1 and len(where[n]) > 1:
                b.annotations.add("repeated-literal")
                others = sorted(where[n] - {f"{b.path}:{b.start}"})[:3]
                b.notes.append(f"{n} also in prose at {', '.join(others)}")

    if args.json:
        # !! THE GATE FIRST. `--json --out` is the route SKILL.md mandates for
        # the census stage 5 parses, and this returned 0 with a SHORT array for
        # a file that could not be read -- so a file with no language record,
        # or one that failed to parse, vanished, and the coverage check then
        # certified "every paragraph accounted for" over paragraphs never collected.
        # The text path errored on exactly the same input.
        if unreadable:
            print(_not_censused(files, unreadable), file=sys.stderr)
            return 1
        print(
            json.dumps(
                [vars(b) | {"annotations": sorted(b.annotations)} for b in census],
                indent=1,
                default=str,
            )
        )
        return 0

    # ! A tier is per FILE: a polyglot repo mixes them in one census. Reported
    # as one global mode, a finding from the lexical floor read like one from
    # the tokenized tier.
    tiers = Counter(b.tier for b in census)
    langs = Counter(lang.name for f in files if (lang := language_for(f)) is not None)
    deferred = [b for b in census if "doc-kind-unresolved" in b.annotations]

    print(f"comment-review stages 2-3 - {len(files)} files, {len(census)} paragraphs")
    print(f"  languages: {', '.join(f'{k} {v}' for k, v in sorted(langs.items()))}")
    for name in ("tokenized", "lexical"):
        if tiers.get(name):
            print(f"  tier {name}: {tiers[name]} paragraphs - {TIER_ANSWERS[name]}")
    print(
        "  ! EVERY address carries an anchor -- the LINE OF CODE it attaches\n"
        "    to, at both tiers. What still needs READING is whether the prose\n"
        "    belongs to it, so a placement finding is a CANDIDATE."
    )
    if deferred:
        print(
            f"  kind unresolved: {len(deferred)} -- a positional doc comment."
            " Confirm the kind before compacting; a cap governs one and not"
            " the other"
        )
    print()

    if args.filtered:
        # !! A PROJECTION, NEVER A RENUMBERING. Each paragraph keeps the index it
        # has in the full census, because that index is what the join resolves
        # and what a record cites -- renumber and every citation from a filtered
        # reviewer resolves to the wrong paragraph, with nothing able to tell.
        print("CENSUS - the paragraphs holding prose, numbered as in the full census.")
    else:
        print("CENSUS - every paragraph, numbered.")
    # !! THE FILE IS STATED ONCE, not on every row. Measured 2026-08-18 over
    # the 13 shipped scripts: 778 rows repeated their path 1,556 times, 80,912
    # of the listing's 205,753 bytes -- 39% -- and every reviewer gets an
    # identical copy of it. A place and a line range mean nothing without a
    # file, so the file heads its own rows instead.
    seen_path = ""
    run: list[int] = []

    def heading(path: str) -> None:
        """Announce the file these rows belong to, once."""
        nonlocal seen_path
        if path != seen_path:
            seen_path = path
            print(f"\n== {path}")

    def flush_run() -> None:
        """One line for a stretch of code no prose sits in."""
        if not run:
            return
        first, last = census[run[0] - 1], census[run[-1] - 1]
        heading(first.path)
        span = f"{first.start}-{last.end}"
        # ! The FIRST index sits in the same column a paragraph's does, so the
        # numbering reads down the page as one sequence -- a run carries census
        # indices, not a different kind of row. `1-interval` and not
        # `1-intervals`, because this is prose a reviewer reads.
        where = f"{run[0]:4d}" if len(run) == 1 else f"{run[0]:4d}-{run[-1]}"
        # ! A run spans several PLACES, so it names its ends. Each is still
        # cited singly -- `locator.py` answers which one holds a given line.
        at = first.address.split("@")[-1]
        seat = at if len(run) == 1 else f"{at}..{last.address.split('@')[-1]}"
        # !! THE SAME COLUMNS AS A PARAGRAPH ROW -- index, address, KIND, lines,
        # notes -- because this listing is pasted into a reviewer's prompt and
        # is read down its columns. Written as prose (`no prose (5 intervals)`)
        # the third column read `no`, which is where a paragraph states its kind,
        # so a run and a paragraph could not be told apart by anything mechanical.
        # ! The notes column names what it counts, in the hyphenated form the
        # annotations use, so the row is readable without the header.
        # ! It names WHAT it collapsed rather than assuming one kind. A run
        # mixes `interval`, `margin` and `undocumented` -- the gap above a line
        # of code, the room beside it, and a declaration with no docstring --
        # and a reviewer citing into one needs to know which are in there.
        kinds = Counter(census[n - 1].kind for n in run)
        counted = ", ".join(
            f"{n}-{kind}" + ("" if n == 1 else "s") for kind, n in sorted(kinds.items())
        )
        print(f"{where}  @{seat}  {span}  no-prose  0L  {counted}")
        run.clear()

    for i, b in enumerate(census, 1):
        # !! FILTERED, and every place that HOLDS NO PROSE becomes one line per
        # run rather than vanishing. It collapsed `interval` alone until
        # 2026-08-19, which was the whole set when it was written and is now a
        # third of it: `margin` and `undocumented` arrived with the `c` and `a`
        # series and were listed one row each. **Measured over this repo's own
        # 15 shipped scripts: 3,282 bare `margin` rows against 484 rows of
        # prose -- 87% of what a reviewer reads, four times over.**
        #
        # ! Collapsing rather than dropping keeps what an `add` is about
        # visible: a stretch of code carrying no commentary. A reviewer needing
        # a spot outside its set asks `locator.py`, which answers from the FULL
        # census.
        # !! FRONT MATTER IS DROPPED FROM WHAT A REVIEWER READS, not collapsed
        # into a run. A licence header or a shebang is not a claim about the
        # code, so no role can settle it and every role would return `clean` on
        # it every run -- see `mark_front_matter`. It keeps its address and its
        # index, so `locator.py` still finds it and a `move` may still cite it;
        # what it loses is a reviewer's attention and a record it owes.
        if args.filtered and FRONT_MATTER in b.annotations:
            continue
        if args.filtered and b.kind in HOLDS_NO_PROSE:
            run.append(i)
            continue
        flush_run()
        notes = ",".join(sorted(b.annotations)) or "-"
        anchor = f"  ({b.anchor})" if b.anchor else ""
        heading(b.path)
        # !! THE PLACE COMES FIRST because it is what a record CITES. The line
        # range beside it is the reader's cursor into the file as it stands
        # now, and it is stale the moment this run edits anything above it.
        at = b.address.split("@")[-1]
        span = f"{b.start}-{b.end}"
        print(f"{i:4d}  @{at}  {span}  {b.kind}  {b.lines}L  {notes}{anchor}")
        if not args.census_only:
            for note in b.notes:
                print(f"        -> {note}")
    flush_run()
    print()

    if unread or unreadable:
        print("NOT CHECKED -- these are gaps, not passes:")
        for u in unread + unreadable:
            print(f"    {u}")
        print(
            "    !! A file missing from the name corpus turns every symbol defined\n"
            "      only there into a false obituary. Treat symbol notes as weaker\n"
            "      until this list is empty."
        )
        print()

    print(
        f"{len(census)} paragraphs censused. `names-a-symbol` and `counted` are\n"
        "CANDIDATES a reviewer confirms; a resolved path is a fact about the\n"
        "filesystem, already settled. The whole list is printed every run."
    )
    # The reviewers are handed the CENSUS, so a file missing from it is paragraphs
    # nobody reviews and there is nothing downstream that notices. Exit on it.
    if unreadable:
        print("\n" + _not_censused(files, unreadable))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
