"""How each LANGUAGE marks its prose, and the paragraph a reader produces.

Adding a language is a `Language` row and a `READER_METADATA` entry -- data, not
code. The reader here reads every language without a reader package of its own
from its row alone: the prose and its kind. Python and Rust are read by
`reading.python` and `reading.rust`, each from its own language definition.

This classifies what the purpose is of each paragraph. `read_lexical` emits
`comment`, `docstring`, `trailing-comment` and `matter` -- prose it found -- and
`leading_between` emits `leading`. `interval`, `margin` and `undocumented` are
the page's, because only a page knows where prose is MISSING.

`read_lexical` also completes the read for the page: `code_text` gives each
line of code its code, `declarations()` marks which lines declare something
documentable and where its doc would go, and `document_declarations` marks the
run that documents a declaration `docstring`, naming that declaration's line --
for Go and Ruby too, whose documentation is an ordinary comment run above the
declaring keyword. It hands back a `LexicalRead`, the paragraphs and their
`CodeLine`s together; `paragraphs_lexical` is its paragraphs alone.

Beside the reader: `comment_form` parses a comment's markers and fragments for
`Paragraph.text` and `desk.marks.rules`.

"""

import ast
import re
from collections.abc import Callable, Collection, Mapping
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from types import MappingProxyType
from typing import NamedTuple

from comment_review import constants
from comment_review.reading.addresser import EOF
from comment_review.reading.comment import Comment, CommentSpan, Fragment
from comment_review.reading.definitions import LanguageDefinition

# !! THE ROWS ARE A LEAF AND THIS IS ONE OF ITS FIVE IMPORTERS -- see
# `language.py`. Everything a language says about where its documentation
# sits is stated there and read here; `binder.page` and `flows.compositor`
# also call `language_for`.
from comment_review.reading.language import (
    BY_EXT,
    INSTALLED_REGISTRY,
    LANGUAGES,
    Language,
    documents_in_literals,
    language_for,
    line_comment_markers,
)
from comment_review.reading.matter import file_matter
from comment_review.reading.paragraph import Paragraph
from comment_review.reading.rust.scanner import comment_scanner
from comment_review.reading.series import Kind, Series
from comment_review.reading.source import CodeLine, DocPlace, lines_of_code

__all__ = [
    "BY_EXT",
    "LANGUAGES",
    "Language",
    "language_for",
]


NAMED_DEFS = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)


MODULE_ANCHOR = "<module>"

# -- Annotations ---------------------------------------------------------------
# This module stamps one -- `unterminated-paragraph-comment`; the citation
# annotations are located and resolved in `concordance/annotate.py`. Locating is
# most of the work; the resolution is what stops a reviewer treating a citation as
# a verified claim. ! These are ANNOTATIONS, never marks -- a MARK is editorial,
# and stage 4 emits those.


def _join(lines: list[str]) -> str:
    """Prose lines, their markers already cut, as ONE normalised string.

    Prose wraps, so every claim-bearing phrase in a real file straddles a line
    break. Matching line-by-line reports the fragment instead of the claim: a
    count reads as absent and `used to say` degrades to a bare `used to`.
    """
    return re.sub(r"\s+", " ", " ".join(ln.strip() for ln in lines)).strip()


#: The readers whose own scanner says where each comment in a paragraph sits
#: and what it is written with, keyed by the reader a definition names. A
#: language read by one of them is split by its reader's grammar alone.
COMMENT_SCANNERS: Mapping[
    str,
    Callable[[LanguageDefinition], Callable[[str], tuple[CommentSpan, ...] | None]],
] = MappingProxyType({"rust-lexical": comment_scanner})


class _Grammar(NamedTuple):
    """What a path's language says about its comments, resolved once per suffix."""

    #: The lexical row, or None for a language defined by its own file.
    lang: Language | None
    #: The installed definition, or None for a path no language covers.
    definition: LanguageDefinition | None
    #: Whether the language documents in string literals, as Python does.
    in_literals: bool
    #: The markers that open a line comment.
    markers: tuple[str, ...]
    #: The reader's comment scanner, or None for a language split by its row.
    scanner: Callable[[str], tuple[CommentSpan, ...] | None] | None


@cache
def _grammar_for(suffix: str) -> _Grammar:
    """The comment grammar of the installed language a suffix selects.

    Selection is by suffix alone, and the installed registry does not change
    while the process runs, so each suffix is resolved once.
    """
    path = Path(f"m{suffix}")
    value = INSTALLED_REGISTRY.for_path(path)
    factory = COMMENT_SCANNERS.get(value.reader) if value is not None else None
    return _Grammar(
        language_for(path),
        value,
        documents_in_literals(path),
        tuple(sorted(line_comment_markers(path), key=len, reverse=True)),
        factory(value) if value is not None and factory is not None else None,
    )


def comment_form(
    path: Path, series: Series | None, raw_text: str, anchor: str = ""
) -> Comment:
    """The assigned paragraph's prose and the form its raw text carries."""
    grammar = _grammar_for(path.suffix.lower())
    lang, value = grammar.lang, grammar.definition
    if grammar.scanner is not None:
        found = grammar.scanner(raw_text)
        return _scanned_form(grammar, series, raw_text, anchor, found)
    chunks: list[str] = []
    if value is not None and grammar.in_literals and series is Series.DECLARED:
        from comment_review.reading.docstring import concatenated

        docstring = concatenated(raw_text, value)
        if docstring is not None:
            return docstring
    pending: list[str] = []
    opened = None
    depth = 1
    line_marker = ""
    if lang is not None:
        for line in raw_text.splitlines(keepends=True):
            if opened is None and not pending and chunks and not line.strip():
                chunks[-1] += line
                continue
            if opened is None and pending and not line.strip():
                pending.append(line)
                continue
            if opened is None:
                pair = next(
                    (
                        pair
                        for pair in lang.block_comment
                        if line.lstrip().startswith(pair[0])
                    ),
                    None,
                )
                if pair is not None:
                    if pending:
                        chunks.append("".join(pending))
                        pending.clear()
                    opened = pair
                    tail = line.lstrip()[len(pair[0]) :]
                    depth = 1
                else:
                    marker = next(
                        (
                            m
                            for m in sorted(lang.line_comment, key=len, reverse=True)
                            if line.lstrip().startswith(m)
                        ),
                        "",
                    )
                    if pending and marker != line_marker:
                        chunks.append("".join(pending))
                        pending.clear()
                    line_marker = marker
                    tail = line
            else:
                tail = line
            pending.append(line)
            if opened is not None:
                ends, depth = run_ends(tail, opened, lang.nests_comments, depth)
                if ends >= 0:
                    chunks.append("".join(pending))
                    pending.clear()
                    opened = None
        if pending:
            chunks.append("".join(pending))
    else:
        chunks = [raw_text]
    parts = tuple(
        _comment_fragment(grammar, series, chunk, anchor if n == 0 else "")
        for n, chunk in enumerate(chunks)
    )
    return Comment(raw_text, parts)


def _scanned_form(
    grammar: _Grammar,
    series: Series | None,
    raw_text: str,
    anchor: str,
    found: tuple[CommentSpan, ...] | None,
) -> Comment:
    """The paragraph cut into fragments at the comments its reader scanned.

    A delimited comment, and a line comment of another form than the one
    before it, starts a fragment: at its line's start when it opens the line,
    or where it opens when something precedes it there. Line comments of one
    form run on as one fragment. Text before the first comment, such as a
    shebang the matter holds, is a fragment of its own with no markers, and so
    is a paragraph its reader finds no comment in.
    """
    if not found:
        return Comment(
            raw_text, (_comment_fragment(grammar, series, raw_text, anchor),)
        )
    leading: list[Fragment] = []
    if raw_text[: found[0].start].strip():
        line_start = raw_text.rfind("\n", 0, found[0].start) + 1
        opens_line = not raw_text[line_start : found[0].start].strip()
        cut = line_start if opens_line else found[0].start
        leading.append(_comment_fragment(grammar, series, raw_text[:cut], anchor))
        raw_text, whole = raw_text[cut:], raw_text
        found = tuple(
            CommentSpan(c.start - cut, c.end - cut, c.opener, c.closer) for c in found
        )
        anchor = ""
    else:
        whole = raw_text
    cuts = [0]
    opening: list[CommentSpan] = []
    for comment in found:
        if opening:
            previous = opening[-1]
            if not comment.closer and not previous.closer:
                if comment.opener == previous.opener:
                    continue
            line_start = raw_text.rfind("\n", 0, comment.start) + 1
            opens_line = not raw_text[line_start : comment.start].strip()
            cuts.append(line_start if opens_line else comment.start)
        opening.append(comment)
    cuts.append(len(raw_text))
    parts = []
    for n, comment in enumerate(opening):
        start = cuts[n]
        close_at = comment.end - len(comment.closer) - start if comment.closer else -1
        parts.append(
            _comment_fragment(
                grammar,
                series,
                raw_text[start : cuts[n + 1]],
                anchor if n == 0 else "",
                marks=(comment.opener, comment.closer, close_at),
            )
        )
    return Comment(whole, (*leading, *parts))


def _comment_fragment(
    grammar: _Grammar,
    series: Series | None,
    raw_text: str,
    anchor: str,
    marks: tuple[str, str, int] | None = None,
) -> Fragment:
    """One comment's prose and markers.

    `marks` is the comment's opener, closer and the closer's offset in
    `raw_text`, as its reader scanned them, with an empty closer and -1 for a
    line comment. Without them the language's row decides the markers.
    """
    lang, definition = grammar.lang, grammar.definition
    in_literals = grammar.in_literals
    physical = raw_text.splitlines(keepends=True)
    while physical and not physical[-1].strip():
        physical.pop()
    content = "".join(physical).rstrip("\r\n")
    ending = raw_text[len(content) :]
    lines = content.splitlines()
    if not lines:
        return Fragment(raw_text, "", (), "", "", "", ending=ending)
    starts = []
    offset = 0
    for line in content.splitlines(keepends=True):
        starts.append(offset)
        offset += len(line)
    indent = lines[0][: len(lines[0]) - len(lines[0].lstrip())]
    body = list(lines)
    first = rest = indent
    last = ""
    head: tuple[str, ...] = ()
    foot: tuple[str, ...] = ()
    suffix = ""
    opened = None
    end_at = -1
    if marks is not None:
        opener, closer, close_at = marks
        if closer:
            opened = opener, closer
            end_at = close_at
    elif lang is not None:
        pairs = [*lang.block_comment]
        pairs += [
            (doc, close)
            for doc in lang.doc_block
            for op, close in lang.block_comment
            if doc.startswith(op)
        ]
        opened = next(
            (
                pair
                for pair in sorted(pairs, key=lambda p: len(p[0]), reverse=True)
                if lines[0].lstrip().startswith(pair[0])
            ),
            None,
        )
    if (
        in_literals
        and definition is not None
        and series is Series.DECLARED
        and re.match(r"(?i)[rub]*(\"\"\"|'''|\"|')", raw_text.lstrip())
    ):
        from comment_review.reading.docstring import first_literal

        spelling = first_literal(raw_text.lstrip(), definition)
        if spelling is not None:
            opening = re.match(r"(?i)[rub]*(\"\"\"|'''|\"|')", spelling)
            if opening is not None:
                op = opening.group(0)
                close = opening.group(1)
                opened = op, close
                end_at = len(indent) + len(spelling) - len(close)
    if opened is not None:
        op, close = opened
        if lang is not None:
            pair = next(p for p in lang.block_comment if op.startswith(p[0]))
            scan_from = len(indent) + len(pair[0])
            ends, _ = run_ends(raw_text[scan_from:], pair, lang.nests_comments)
            if ends >= 0:
                end_at = scan_from + ends - len(close)
                if end_at < len(indent) + len(op):
                    op = pair[0]
        first = indent + op
        body[0] = body[0][len(first) :]
        starts[0] += len(first)
        closing = end_at - starts[-1] if end_at >= 0 else -1
        if closing >= 0:
            last = body[-1][closing:]
            body[-1] = body[-1][:closing]
            after = last[len(close) :]
            if after.strip():
                suffix_indent = lines[-1][: len(lines[-1]) - len(lines[-1].lstrip())]
                if in_literals:
                    suffix_indent = indent
                    after = after.lstrip(" \t")
                    if after.startswith(";"):
                        after = after[1:].lstrip(" \t")
                suffix = (
                    ("\r\n" if "\r\n" in raw_text else "\n") if len(lines) > 1 else ""
                )
                suffix += suffix_indent + after + ending
        if not body[0].strip():
            head = (lines[0],)
            body.pop(0)
            starts.pop(0)
            first = indent
        else:
            space = body[0][: len(body[0]) - len(body[0].lstrip())]
            first += space
        if body and not body[-1].strip() and last:
            foot = (lines[-1],)
            body.pop()
            starts.pop()
            last = ""
        elif body and last:
            trailing = body[-1][len(body[-1].rstrip()) :]
            last = trailing + last
        rest = indent
        if body:
            sample = body[0] if head else next(iter(body[1:]), "")
            prefix = r"^(\s*\*(?:[ \t]+|$)|\s*)" if op.startswith("/*") else r"^\s*"
            found = re.match(prefix, sample)
            if found is not None:
                rest = found.group(0) or indent
            if head:
                first = rest
        if op.startswith("/*"):
            for n, line in enumerate(body):
                if n == 0 and not head:
                    continue
                found = re.match(r"^\s*\*(?:[ \t]+|$)", line)
                if found is not None:
                    body[n] = line[found.end() :]
                    starts[n] += found.end()
    elif markers := (marks[:1] if marks is not None else grammar.markers):
        marker = next((m for m in markers if lines[0].lstrip().startswith(m)), "")
        if marker:
            lead = indent + marker
            following = lines[0][len(lead) :]
            first = lead + following[: len(following) - len(following.lstrip())]
            rest = first
            for line in lines[1:]:
                found = re.match(r"^\s*" + re.escape(marker) + r"[ \t]*", line)
                if found is not None and line[found.end() :].strip():
                    rest = found.group(0)
                    break
            body = []
            for n, line in enumerate(lines):
                stripped = line.lstrip()
                actual = next((m for m in markers if stripped.startswith(m)), "")
                body.append(stripped[len(actual) :] if actual else line)
                if actual:
                    starts[n] += len(line) - len(stripped) + len(actual)
    sections = re.split(r"\n\s*\n", "\n".join(body))
    paragraphs = tuple(
        _join(section.splitlines()) for section in sections if section.strip()
    )
    gaps = []
    blank = []
    seen = False
    for line, at in zip(body, starts, strict=True):
        if not line.strip():
            if seen:
                blank.append(lines[raw_text.count("\n", 0, at)])
        else:
            if blank:
                gaps.append(tuple(blank))
                blank.clear()
            seen = True
    positions = []
    whitespace = None
    for line, at in zip(body, starts, strict=True):
        for n, char in enumerate(line):
            if char.isspace():
                if positions and whitespace is None:
                    whitespace = at + n
            else:
                if whitespace is not None:
                    positions.append(whitespace)
                    whitespace = None
                positions.append(at + n)
        if positions and whitespace is None:
            whitespace = at + len(line)
    return Fragment(
        raw_text,
        " ".join(paragraphs),
        paragraphs,
        first,
        rest,
        last,
        head,
        foot,
        ending,
        len(anchor) if series is Series.ON else 0,
        tuple(positions),
        suffix,
        tuple(gaps),
    )


# !! HOW FAR PAST THE OPENING QUOTE AN ESCAPED CHARACTER MAY CLOSE. `'\n'` closes
# at +3 and Rust's widest, `'\u{10FFFF}'`, at +11. An UNESCAPED character needs no
# constant: it is exactly one character wide, so its closer is at +2 and nowhere
# else.
ESCAPE_WIDTH = 11


def _closes_a_character(line: str, at: int, quote: str) -> bool:
    """Does the quote at `at` open a ONE-CHARACTER literal?

    !! THIS IS WHAT TELLS A CHARACTER FROM A LIFETIME. Rust writes both with
    `'`: `'a'` is a character and `&'a mut T` is a lifetime, and the second
    never closes. Read as a quote it would blank everything after it, losing a
    trailing comment on that line with no refusal and exit 0.

    !! IT ASKS WHERE THE CLOSER IS, NOT WHETHER ONE IS NEARBY. A character is
    one character, so its closer is at a FIXED offset; an escape is the only
    variable-width case and is bounded by `ESCAPE_WIDTH`.

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
    # window.
    if line[at + 1 : at + 2] != "\\":
        return line[at + 2 : at + 3] == quote
    # ! An ESCAPE is the one variable-width case, and it is bounded: `'\n'` closes
    # at +3 and Rust's widest, `'\u{10FFFF}'`, at +11.
    end = line.find(quote, at + 2)
    return 0 <= end - at <= ESCAPE_WIDTH


def _strip_strings(
    line: str, quotes: tuple[str, ...], char_quotes: tuple[str, ...] = ()
) -> str:
    """Blank out string literals so a marker inside one stays out of the binder.

    `url = "http://x"` holds `//` in most C-family languages. It handles
    single-line literals with backslash escapes; raw strings, heredocs and
    template nesting are what this function does not handle.

    Args:
        line: the physical line.
        quotes: this language's string delimiters.
        char_quotes: the subset holding exactly ONE character, which is checked
            for a closer before it is believed. Empty where the language has
            none, and then every quote in `quotes` opens a literal.

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
    loses the WHOLE comment: the scan closes early, sees more comment after it, and
    applies the intermediate-comment rule -- which is about code after a mid-line
    close.

    ! WHERE IT MATTERS IS THE TRAILING COMMENT. A `b` needs no depth -- a gap
    cannot hold a line of code, so the code either side bounds it -- and no language
    here marks documentation with a bare paragraph opener: every doc marker is
    `/**`, `///` or `//!`, and Go and Ruby document by position. So depth cannot
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


def _anchor_of(lines: list[str], line_no: int, column: int) -> str:
    """The line of code a `c` paragraph sits beside -- its ANCHOR, verbatim.

    An anchor is the line of code, not a symbol: the exact characters on that
    line. So it needs no parser, no language server and no build tool: every
    tier already found where the comment opens, which means it already had the
    characters before it.

    It is kept apart from the prose. `read_lexical` cuts `raw_lines` at
    the opener, so the code before it is held here and in no string with the prose.

    It is `""` for a paragraph that owns its lines whole, which has no code on its
    line to be anchored to.

    Args:
        lines: the file's lines, without endings.
        line_no: 1-based line the paragraph opens on.
        column: one past the last character of code on that line, 1-based,
            or 0 when the paragraph owns its line whole.

    Returns:
        The code preceding the paragraph on its first line, right-stripped.
    """
    if not column or not 1 <= line_no <= len(lines):
        return ""
    return lines[line_no - 1][: column - 1]


def leading_between(
    paragraphs: list["Paragraph"], text: str, code: Collection[int]
) -> list["Paragraph"]:
    """Every blank run no paragraph holds, as LEADING -- see `LEADING`.

    !! ONE RULE FOR ALL READERS, and that is the point of it being a pass rather
    than a branch inside each.

    ! THE RULE IS SUBTRACTION, so it cannot disagree with either reader about
    what prose or code is: a blank line a paragraph already holds is INSIDE it
    and stays there, a line the reader gave as code is code whatever
    `str.strip` makes of it, and every other blank line is the space between
    two paragraphs.

    Args:
        paragraphs: what a reader produced, before any place is assigned.
        text: the file, read for which lines are blank.
        code: the numbers of the lines the reader gave as code.

    Returns:
        One paragraph per unheld blank run, in order.
    """
    lines = constants.text_lines(text)
    held = set(code)
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
            out.append(_leading(paragraphs, lines, run))
            run = []
    if run:
        out.append(_leading(paragraphs, lines, run))
    return out


def _leading(
    paragraphs: list["Paragraph"], lines: list[str], run: list[int]
) -> "Paragraph":
    """One blank run, as a paragraph. Its anchor is EMPTY on purpose.

    ! Every other series answers to a line of code. This answers to nothing, and
    its anchors are empty by design rather than by omission.

    !! A BLANK LINE IS NOT ALWAYS AN EMPTY ONE, which is why `lines` is passed
    rather than the count. A line holding a tab or three spaces is blank to
    `str.strip` and not blank on disk, and `raw_lines` keeps what is on disk.
    """
    return Paragraph(
        path=paragraphs[0].path if paragraphs else "",
        start=run[0],
        end=run[-1],
        kind=Kind.LEADING,
        raw_lines=[lines[n - 1] for n in run],
    )


def _is_doc(line: str, lang: Language) -> bool:
    """Does this line open a comment the language treats as DOCUMENTATION?

    `read_lexical` asks it of each comment it opens, to record the lines doc
    comments stand on, and `flush` asks it of a run's first line to set the
    run's kind.
    """
    opens = line.strip()
    return _opens_doc(opens, lang.doc_line) or _opens_doc(opens, lang.doc_block)


def _opens_doc(opens: str, markers: tuple[str, ...]) -> bool:
    """Does this line open a DOC run with one of these markers?

    The test is the character after the marker, which is the rule Javadoc and
    Doxygen themselves use: `/**` opens documentation, `/***` does not, and the
    difference is whether the next character repeats the marker. It holds for
    `doc_line` unchanged -- `///` is a Rust doc line and `////` is a rule.

    ! An EMPTY doc opener is still one: `///` with nothing after it, or `/** */`,
    are documentation a reviewer can rule on. Only a REPEAT disqualifies.
    """
    for marker in markers:
        if (
            opens.startswith(marker)
            and opens[len(marker) : len(marker) + 1] != marker[-1:]
        ):
            return True
    return False


def paragraphs_lexical(path: Path, text: str, lang: Language) -> list[Paragraph]:
    """The comment runs `read_lexical` finds, without the code lines."""
    return read_lexical(path, text, lang).found


def read_lexical(path: Path, text: str, lang: Language) -> "LexicalRead":
    """Comment runs and code lines for a language with no parser here -- the FLOOR tier.

    Answers where every paragraph is, its line range, its raw lines and its
    annotations, and each line of code with the documentation it declares.
    ! A paragraph sitting BESIDE code carries an anchor at this tier too -- the
    line of code itself, which needs no parser; see `_anchor_of`. Only a paragraph
    that owns its lines whole has none, because its anchor is a declaration and
    naming one needs the structure this tier lacks.

    ! A paragraph opener with no closer swallows every remaining line into one run,
    so code below it is read as prose. That paragraph is STAMPED
    `unterminated-paragraph-comment`, which is how a consumer tells it from a long
    comment; `prove_unchanged.py` refuses the whole file on that annotation.
    """
    openers = tuple(sorted(lang.line_comment, key=len, reverse=True))
    lines = constants.text_lines(text)
    out: list[Paragraph] = []
    run: list[tuple[int, str]] = []
    # ! Blank lines seen since the last comment line. They belong to the run only if
    # another comment follows; otherwise they are dropped, so a run ends on its
    # last comment line.
    pending: list[tuple[int, str]] = []
    in_block: tuple[str, str] | None = None
    # ! LAYERS STILL OPEN on a run that crossed a line -- see `run_ends`. Always
    # 1 where the language does not nest.
    layers = 1
    # !! WHERE THE RUN'S FIRST LINE STOPS BEING CODE -- one past the last
    # character of code, or 0 when the run owns its lines whole. It cuts
    # `raw_lines[0]` and is not carried on the paragraph.
    #
    # ! `trailing` does not answer it: a MULTI-LINE paragraph comment opened after a
    # statement flushes with `trailing=False`, because by then the run spans
    # several lines. A list because `flush` is a closure and rebinds nothing.
    partial_first = [0]
    # The blank lines a run took in between two of its comments. Every other
    # line of a run has a comment on it; `_file_edges` reads the two apart.
    between: set[int] = set()
    # The lines a doc-marked comment stands on, and whether the delimited
    # comment still open is one. `_file_edges` reads no such line as matter.
    documentation: set[int] = set()
    in_doc = False

    def carry() -> None:
        """Take the blanks held since the last prose line into the run.

        !! ONE RULE FOR BOTH COMMENT SYNTAXES: `/* one */`, a blank and `/* two */`
        are one paragraph, exactly as `// one`, a blank and `// two` are.
        """
        if not run:
            # !! BLANKS ABOVE A RUN THAT HAS NOT STARTED ARE NOT ITS OWN. They
            # separate this prose from whatever precedes it, which is what
            # LEADING is -- and `leading_between` finds them afterwards, for both
            # readers at once.
            pending.clear()
            return
        between.update(n for n, _ in pending)
        run.extend(pending)
        pending.clear()

    def flush(trailing: bool = False) -> None:
        # ! The blanks held since the run's last prose line are LEADING, not the
        # run's -- `leading_between` collects them once every paragraph exists.
        pending.clear()
        if not run:
            partial_first[0] = 0
            return
        # !! `raw_lines` IS THE SOURCE: the file's own characters, which are what
        # a splice is checked against.
        span = lines[run[0][0] - 1 : run[-1][0]]
        if partial_first[0] > 0:
            span = [span[0][partial_first[0] - 1 :], *span[1:]]
        if _is_doc(run[0][1], lang):
            kind = "docstring"
        else:
            # !! CODE ON THE FIRST LINE MAKES IT TRAILING, however many lines it
            # then runs for. A `c` is the room beside a line of code, so prose
            # occupying that room IS a trailing comment and the kind must say
            # so. ! `trailing` alone answers only the single-line case: a
            # paragraph comment opened after a statement flushes with
            # `trailing=False`, because by then the run spans several lines --
            # so `int b = 2; /* opens` would read as a plain `comment` sitting at
            # a `c` place, and kind and series would disagree.
            kind = "trailing-comment" if trailing or partial_first[0] else "comment"
        paragraph = Paragraph(
            path=path.as_posix(),
            start=run[0][0],
            end=run[-1][0],
            kind=kind,
            raw_lines=span,
            # !! THE LEXER ALREADY HAS THIS STRING. It found the opener in order
            # to cut there, so the characters before it are known here.
            anchor=_anchor_of(lines, run[0][0], partial_first[0]),
        )
        partial_first[0] = 0
        out.append(paragraph)
        run.clear()

    # The interpreter line the row names, kept as the file's own matter: it is
    # neither code nor a comment, and the matter rule opens on the line below.
    shebang = None
    interpreter = lang.interpreter_line(lines)
    if interpreter is not None:
        shebang = Paragraph(
            path=path.as_posix(),
            start=1,
            end=1,
            kind=Kind.MATTER,
            raw_lines=[interpreter],
            anchor=MODULE_ANCHOR,
        )

    for n, raw_line in enumerate(lines, 1):
        if shebang is not None and n == 1:
            continue
        if in_block is not None:
            # !! CODE AFTER THE CLOSER KEEPS ITS PROSE AND LOSES ITS CODE LINE.
            # `/* note\n   more */ int x = 5;` gathers the run and leaves
            # `int x = 5;` out of `code_text`, so every interval boundary below
            # it moves.
            #
            # !! AND AN EDIT TO THAT PARAGRAPH DELETES THE STATEMENT. This cut
            # trims the run's own entry and not the paragraph's `raw_lines`, and
            # the galley splices `start..end` wholesale -- it preserves the head of the
            # FIRST line at `column` and has no tail preservation on the last.
            # `prove_unchanged` catches it, but only AFTER 7b has written the
            # file.
            #
            # !! IT IS THE GALLEY'S TO CATCH, NOT THE LEXER'S AND NOT A
            # REVIEWER'S. A reviewer rules on a paragraph and has no view of how
            # the galley splices it, so it cannot know the closing line will
            # delete code. The whole-file composition the galley is heading for
            # is where a write that would drop a line becomes visible BEFORE it
            # happens, which is the same move `prove_unchanged` needs. Filed as
            # `TODO/closing-line-deletes-code.md`.
            #
            # ! NEITHER FIX IS WORTH ITS COST. Dropping the run the way an
            # INTERMEDIATE comment is dropped works on the one-line twin --
            # `/* note */ int x = 5;` is wholly a code line -- and not here,
            # where the opening line is nothing but comment and would belong to
            # nothing. Keeping both needs a field for where the text ENDS, or a
            # kind for comment-then-code; the first re-adds a column the address
            # system replaced, the second teaches every consumer that switches
            # on kind.
            #
            # !! MEASURED OVER THE FETCHED CORPORA: 180,821 lines of C and JS/TS,
            # and the shape occurs **0 times** -- 3 apparent hits were `*/`
            # inside a glob string. The one-line form is ordinary (1,551 hits)
            # and is already right. The style guides agree -- ESLint ships
            # `no-inline-comments`, and the kernel, Google C++ and Java guides
            # all put a paragraph comment on its own line.
            #
            # ! CUT AT THE CLOSER, the way the opening line cuts at the opener,
            # so `   more */ int x = 5;` gives the run only `   more */` and no
            # executable code reaches four reviewers as prose or the annotation
            # regexes.
            # ! CARRIES THE DEPTH, so a nested opener on an earlier line keeps
            # the run open past the closer that matches it.
            if in_doc:
                documentation.add(n)
            ends, layers = run_ends(raw_line, in_block, lang.nests_comments, layers)
            if ends >= 0:
                run.append((n, raw_line[:ends].rstrip()))
                in_block = None
                in_doc = False
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
        # !! ONLY CODE ENDS A PARAGRAPH -- a blank line does not. Split on blanks,
        # a 9-line paragraph would read as `6 + 3` and pass a cap of 6.
        #
        # ! The blank JOINS the run rather than being skipped, so `raw_lines`
        # stays index-aligned with `start..end` -- `prove_unchanged` walks the
        # two together and a gap there makes the file unprovable.
        #
        # !! A blank line INSIDE a run joins it; a blank line AFTER one does
        # NOT extend it. They are held here and committed only when another
        # comment line arrives. A run's `end` must stay on its last comment
        # line, because `document_declarations` counts the blank lines between
        # a run's end and the declaration below it -- extend the paragraph over
        # the gap and a run held off its declaration reads as flush against it.
        if not raw_line.strip():
            # ! HELD WHETHER OR NOT A RUN IS OPEN; `carry` and `flush` decide what
            # becomes of them.
            pending.append((n, ""))
            continue
        code = _strip_strings(raw_line, lang.quotes, lang.char_quotes)
        line_at = min((code.index(o) for o in openers if o in code), default=-1)
        opened = next((p for p in lang.block_comment if p[0] in code), None)
        # !! WHICHEVER OPENER COMES FIRST on the line owns it.
        if opened is not None and -1 < line_at < code.index(opened[0]):
            opened = None
        if opened is not None:
            # !! OPENING A DELIMITED COMMENT DOES NOT END THE RUN BEFORE IT, so
            # `/* one */`, a blank and `/* two */` are one paragraph, as `// one`, a
            # blank and `// two` are. ! It ends the run only when code precedes the
            # opener, which is not known until `opens_at` below -- so that decision is
            # made there.
            opens_at = code.index(opened[0])
            # !! THE OPENER IS FOUND IN THE BLANKED LINE AND THE CLOSER IN THE
            # RAW ONE, and they are different questions. Whether a `/*` OPENS a
            # comment depends on whether it is inside a string, so that is asked
            # of `code`. Once the comment is open, a quote has no meaning at all
            # -- which is why the continuation path above scans `raw_line`.
            tail = raw_line[opens_at + len(opened[0]) :]
            ends_at, layers = run_ends(tail, opened, lang.nests_comments)
            closes_here = ends_at >= 0
            after = tail[ends_at:] if closes_here else ""
            # !! AN INTERMEDIATE COMMENT IS NOT GATHERED -- one that CLOSES on
            # this line with code after it, `int x = /* why */ 5;`.
            #
            # ! Gathered, the paragraph's TEXT would be the whole statement --
            # executable code handed to four reviewers as prose. Cutting at the
            # opener instead loses the `5;`, so `5` and `7` would compare EQUAL
            # and `prove_unchanged` report PROVEN on a changed literal. Neither is
            # available; the line is simply code. It stays a code line, so it
            # keeps its `b` and its `c` like any other.
            if closes_here and after.strip():
                # ! THE LINE IS CODE, so it ends the run like any other.
                flush()
                # !! AND A LINE COMMENT AFTER IT IS STILL A TRAILING COMMENT. The
                # intermediate comment is ignored and the line is then simply code,
                # and a code line carrying a trailing comment is the ordinary case,
                # not an exception to it.
                # ! It must sit past the CLOSER: a `//` before the delimited
                # opener never reaches here, because whichever opener comes
                # first owns the line and `opened` was cleared above.
                closed_at = opens_at + len(opened[0]) + ends_at
                if line_at >= closed_at:
                    partial_first[0] = (
                        len(raw_line[:line_at].rstrip()) + 1
                        if raw_line[:line_at].strip()
                        else 0
                    )
                    run.append((n, raw_line[line_at:].rstrip()))
                    flush(trailing=True)
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
            if _is_doc(raw_line[opens_at:], lang):
                documentation.add(n)
                in_doc = not closes_here

            # !! CUT AT THE OPENER, like the line-comment path below does. Taking the
            # whole raw line would read `int b = 2; /* note */` as one paragraph whose
            # TEXT held the statement -- executable code handed to four reviewers as
            # prose, run through the annotation regexes, and dropped from
            # `code_text`, which moves every interval boundary in the file.
            run.append((n, raw_line[opens_at:].rstrip()))
            if not closes_here:
                in_block = opened
            elif beside_code:
                # !! ONLY CODE ENDS A PARAGRAPH, AND A CLOSER IS NOT CODE. ! Code
                # AFTER the closer cannot reach here -- such a line is not
                # gathered at all, by the intermediate-comment ruling above -- so
                # code BEFORE the opener is the only thing left, and that makes
                # this a trailing comment: prose about the statement on its own
                # line, which must not absorb the prose beneath it.
                flush(trailing=True)
            continue
        # !! ASKED OF THE RAW LINE, NOT THE BLANKED ONE. `_strip_strings` replaces
        # a literal with spaces, which erases the evidence that code came first:
        # `  "b" // the last one` blanks to `      // the last one`, whose strip
        # starts with the opener, so a JS array element would read as a
        # whole-line `comment` whose TEXT held `"b"` -- executable code handed to
        # four reviewers as prose -- and its line would leave `code_text`.
        # ! WHAT THAT COSTS IS NOT THE MISREADING. Every `b` and `c` below the
        # line shifts, so a galley splice over one of those addresses lands
        # somewhere other than where the reviewer cited. ! Whitespace before the
        # opener is not code, which is the case the blanked test got right and
        # this keeps right.
        if line_at >= 0 and not raw_line[:line_at].strip():
            carry()
            run.append((n, raw_line.rstrip()))
            if _is_doc(raw_line, lang):
                documentation.add(n)
            continue
        flush()  # ! CODE ends a paragraph; a blank line does not
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
    flush()
    found, code_lines = _file_edges(out, text, lang, between, documentation, shebang)
    if in_block is not None and found:
        # The loop ended with a paragraph comment still open, so the final flush
        # emitted the run that ate the rest of the file. It is the ONE paragraph
        # that may hold code.
        found[-1].annotations.add("unterminated-paragraph-comment")
        found[-1].notes.append(
            f"UNTERMINATED {in_block[0]}: no closing {in_block[1]} before end of "
            "file, so every line below the opener was swallowed into this run. "
            "Code down there was NOT read as code."
        )
    return LexicalRead(found, code_lines, lang.a_series, lang.closing_docstring)


def _file_edges(
    paragraphs: list[Paragraph],
    text: str,
    lang: Language,
    between: set[int],
    documentation: set[int],
    shebang: Paragraph | None,
) -> tuple[list[Paragraph], list[CodeLine]]:
    """Say which runs document a declaration, then which are the file's own matter.

    Returns the paragraphs and the file's code lines, which cutting a run at a
    blank line or a docstring's end does not change.

    A prose line, for `reading.matter`, is a line of a whole-line run with a
    comment on it -- not a blank it took in `between` two comments, and not a
    line of `documentation`. The matter opens on line 1, or on line 2 below a
    `shebang`, the MATTER paragraph of the interpreter line the row names; the
    front matter below it joins it as one paragraph.

    !! A RUN IS CUT AT THE MATTER'S EDGES BEFORE DOCUMENTATION IS DECIDED, so
    a licence header and the declaration's documentation below it are two
    runs and only the second documents. A part opening on a doc-marked line is
    a `docstring` run, as `flush` kinds a run. Once documentation is decided,
    the `comment` parts inside the matter are MATTER.

    !! DOCUMENTATION AT EITHER END IS THE MODULE'S, NEVER MATTER -- see
    `_module_documentation`.

    !! MATTER IS ANCHORED TO THE MODULE, because that is what it is about.
    Every other run answers to the line of code it sits with; the file's own
    prose answers to the file.
    """
    total = len(constants.text_lines(text))
    opens = 1 if shebang is None else 2

    def held(p: Paragraph) -> set[int]:
        return {n for n in range(p.start, p.end + 1) if n not in between}

    def cut(found: list[Paragraph], kinds: tuple[str, ...], mark: bool):
        """Cut every run of `kinds` at the matter's edges; MATTER parts if `mark`."""
        prose = {
            n
            for p in found
            if p.kind in kinds
            for n in held(p)
            if n not in documentation
        }
        matter = file_matter(total, opens, prose)
        out: list[Paragraph] = []
        for p in found:
            parts = matter.parts(p.start, p.end, held(p)) if p.kind in kinds else []
            if len(parts) < 2 and not (mark and parts and parts[0][2]):
                out.append(p)
                continue
            for start, end, is_matter in parts:
                if mark:
                    kind = Kind.MATTER if is_matter else p.kind
                else:
                    kind = Kind.DOCSTRING if start in documentation else Kind.COMMENT
                out.append(
                    Paragraph(
                        path=p.path,
                        start=start,
                        end=end,
                        kind=kind,
                        raw_lines=p.raw_lines[start - p.start : end - p.start + 1],
                        anchor=MODULE_ANCHOR if kind == Kind.MATTER else p.anchor,
                    )
                )
        return out

    found = cut(paragraphs, (Kind.COMMENT, Kind.DOCSTRING), mark=False)
    if shebang is not None:
        found.insert(0, shebang)
    code = code_text(text, found)
    code_lines = lines_of_code(code, declarations(lang, code))
    document_declarations(found, code_lines)
    found = cut(found, (Kind.COMMENT,), mark=True)
    if shebang is not None and len(found) > 1:
        below = found[1]
        if below.kind == Kind.MATTER and below.start == opens:
            found[:2] = [
                Paragraph(
                    path=shebang.path,
                    start=1,
                    end=below.end,
                    kind=Kind.MATTER,
                    raw_lines=[*shebang.raw_lines, *below.raw_lines],
                    anchor=MODULE_ANCHOR,
                )
            ]
    if lang.a_series:
        found = _module_documentation(found, set(code), between, documentation)
    return found, code_lines


def _module_documentation(
    paragraphs: list[Paragraph],
    code: set[int],
    between: set[int],
    documentation: set[int],
) -> list[Paragraph]:
    """Give the module the doc-marked runs at either end that document nothing.

    A run is at an end when no code and no prose but matter lies between it and
    the file's first or last line. The run at the head documents the module at
    `a0` when it opens on a line of `documentation`, and its docstring ends at
    its last doc-marked line: the comments after it stay a `comment` run,
    starting on the next line it has a comment on, past any blank it took in
    `between`. The run at the foot, a different run, is the same rule read
    upward: it documents the module at the `a` emitted at EOF, which its
    `<eof>` anchor names, when it ends on a line of `documentation`, and its
    docstring starts at its first doc-marked line, the comments before it
    staying a `comment` run that ends on the last line it has a comment on.
    """
    prose = sorted(
        (p for p in paragraphs if p.kind not in (Kind.MATTER, Kind.LEADING)),
        key=lambda p: p.start,
    )
    ends: list[tuple[Paragraph, str]] = []
    if prose and not any(n < prose[0].start for n in code):
        ends.append((prose[0], ""))
    if prose and not any(n > prose[-1].end for n in code):
        if not ends or ends[0][0] is not prose[-1]:
            ends.append((prose[-1], EOF))
    out = list(paragraphs)
    for p, anchor in ends:
        opens = p.end if anchor == EOF else p.start
        if p.kind != Kind.COMMENT or opens not in documentation:
            continue
        doc = [n for n in range(p.start, p.end + 1) if n in documentation]
        first, last = (doc[0], p.end) if anchor == EOF else (p.start, doc[-1])
        comment = [
            n
            for n in range(p.start, p.end + 1)
            if not first <= n <= last and n not in between
        ]
        docstring = Paragraph(
            path=p.path,
            start=first,
            end=last,
            kind=Kind.DOCSTRING,
            raw_lines=p.raw_lines[first - p.start : last - p.start + 1],
            anchor=anchor,
        )
        rest = (
            [
                Paragraph(
                    path=p.path,
                    start=comment[0],
                    end=comment[-1],
                    kind=Kind.COMMENT,
                    raw_lines=p.raw_lines[
                        comment[0] - p.start : comment[-1] - p.start + 1
                    ],
                )
            ]
            if comment
            else []
        )
        at = out.index(p)
        out[at : at + 1] = [*rest, docstring] if anchor == EOF else [docstring, *rest]
    return out


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
    `public`. The first word matching, or the first two as one entry, is enough,
    because the list already says which words this language uses for the purpose.
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


def document_declarations(paragraphs: list["Paragraph"], lines: list[CodeLine]) -> None:
    """Say which prose run documents which declaration, at the LEXICAL tier.

    !! IT LIVES HERE BECAUSE POSITIONING IS THE LANGUAGE'S, and the lexer is where
    a row's `declares` and `doc_inside` are read. ! Python's own reader states the
    same fact for Python.

    !! PROSE BELONGS TO WHICHEVER SIDE IT IS NEARER TO, and a TIE -- the same
    number of blank lines on both sides -- goes to the side the language
    documents on, which for every above-doc language is the declaration. That is
    the whole rule. "The nearest run above
    the declaration" is not: it cannot tell a declaration's documentation from a
    note about the statement above it.

    ! A worked example, from `meta-package-manager`'s `mpm.js`:

        export const MPM_MIN_VERSION = [6, 4, 0];
        /* mpm 6.4.0 renamed `--output-format` back to `--table-format` ... */

        export const MPM_TIMEOUT = 60;

    The comment explains why the MINIMUM VERSION is 6.4.0 -- it is about the line
    it sits under. It is flush under the code above (0 blank lines) and one blank
    from the declaration below, so it is nearer to what it is about, and no
    reviewer measures that prose against `= 60`.

    ! WHAT IT CANNOT DO is read the prose. A comment flush under one statement
    and about the next is indistinguishable by position, which is why
    `ownership-context` reads every placement rather than trusting one.

    ! A run opened with a doc marker that documents no declaration is a
    `comment`: `Kind.DOCSTRING` says a paragraph documents something, and this
    one documents nothing the page can place.

    Args:
        paragraphs: this file's prose, mutated in place -- each run that
            documents a declaration becomes `Kind.DOCSTRING` with that
            declaration's line as its `anchor_line`.
        lines: the file's code lines, in order; a line whose `documents` is set
            declares something documentable.
    """
    # ! LEADING IS NOT PROSE AND CANNOT DOCUMENT ANYTHING, and MATTER -- a
    # shebang, here -- is the file's own.
    ends = {
        b.original_end: b
        for b in paragraphs
        # ! ASKED OF THE KIND. No margin exists yet here: the walk has not
        # synthesised the empty places.
        if b.original_end and b.kind not in (Kind.TRAILING, Kind.LEADING, Kind.MATTER)
    }
    documenting: set[int] = set()
    above_code = [c.line for c in lines]
    code = set(above_code)
    declaring = [c.line for c in lines if c.documents is not None] if ends else []
    for line in declaring:
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
        # ! BOTH ENDS ARE TESTED, not just `held`. A paragraph reaches `ends`
        # KEYED BY ITS OWN END LINE, so it holds lines and both fields are set --
        # but they are typed `int | None`, and the three lines below do
        # arithmetic on them. The test costs nothing and says which invariant
        # the arithmetic is standing on.
        if held is None or held.original_start is None or held.original_end is None:
            continue
        # ! THE TWO DISTANCES, counted in blank lines. Nothing above the run
        # means there is nothing for it to belong to, so the declaration takes
        # it -- `over` is set past `below` to say so.
        below = line - held.original_end - 1
        previous = [n for n in above_code if n < held.original_start]
        over = held.original_start - previous[-1] - 1 if previous else below + 1
        if below <= over:
            # ! THE LINE, NOT A CUE. The page gives it the `a` of that line.
            held.kind = Kind.DOCSTRING
            held.anchor_line = line
            documenting.add(id(held))
    for b in paragraphs:
        if b.kind == Kind.DOCSTRING and id(b) not in documenting:
            b.kind = Kind.COMMENT


def declarations(lang: Language, code: Mapping[int, str]) -> dict[int, DocPlace]:
    """Every DOCUMENTABLE declaration in source order: its line, and where its doc goes.

    !! THE ORDER A READER MEETS THEM down the page, which is the order the `a`
    series counts from `a1`. The module is not among them: a module has no line
    of code declaring it, and its `a0` exists whenever the language has an `a`
    series at all -- see `Language.a_series`.

    !! THE KEYWORDS ARE DATA. Each language row lists the keywords that say a
    line can get a docstring, and the lexer matches on that list instead of on
    independent tooling. An LSP or the build tooling can VERIFY the result;
    neither is needed to get one.

    ! A LANGUAGE WHOSE DOC GOES INSIDE THE BODY IS REFUSED -- `lang.doc_inside`,
    Python. Where its body starts is not the declaring line, so its own reader
    states its declarations. Every other installed language documents a
    declaration with the run directly above its declaring line, so the line the
    keyword is on is the whole answer.

    ! It REPORTS; it does not emit a paragraph. `undocumented` is a PAGE kind,
    because only a page knows where prose is missing.

    Args:
        lang: its record; `declares` holds the keywords.
        code: `line -> the code on it`, from `code_text`. The keyword path
            scans ONLY these, so a keyword inside a comment or a string cannot
            declare anything.

    Returns:
        Each declaring line -> its `DocPlace`. !! `above` IS THE ROW SPEAKING:
        it is `doc_inside` read back out, and it is stated HERE because the
        lexer is where a row's `declares` and `doc_inside` are read.
    """
    if lang.doc_inside:
        raise ValueError(f"{lang.name} declarations come from its own reader")
    # ! The doc goes ON the declaring line, pushing it down, so the place is set
    # against that line. Ordered because `code` is.
    return {
        n: DocPlace(n, True)
        for n, line in code.items()
        if _declares_here(line, lang.declares)
    }


def code_text(text: str, paragraphs: list[Paragraph]) -> dict[int, str]:
    """Every LINE OF CODE on a lexically read page, in order, with the code on it.

    ```python
    {2: "N = 0", 3: "def f():", 5: "    return 1"}
    ```

    A line is code when it holds something that is not blank and not prose.
    This knows only what a comment-syntax record spells, so it reads the
    lexical reader's paragraphs; the Python and Rust readers state their own
    code lines from what they parsed.

    ! A `trailing-comment` sits ON a code line, so that line stays code. A
    `comment`, `docstring` or `matter` paragraph occupies its lines entirely,
    so those lines are not. Every paragraph here is prose the reader found; no
    empty place exists yet.

    !! A PARAGRAPH'S FIRST LINE IS STILL CODE WHEN CODE PRECEDES ITS TEXT.
    `int b = 2; /* opens` spans from that line, and taking the whole span would
    drop the statement from the code set, moving every interval boundary below
    it.

    !! THE PARAGRAPH SAYS SO, BY ITS SERIES -- a `c` paragraph is the prose
    beside code.

    !! THE CHARACTERS COME FROM THAT LINE'S `c` PARAGRAPH, NEVER RE-CUT HERE. A
    `trailing-comment`'s anchor already states where the code stops; cutting
    the line again answers `'    return os  # why'` where the paragraph for the
    same line answers `'    return os'`: two computations of one fact.

    Args:
        text: the file's source.
        paragraphs: the prose the lexical reader found in it.
    """
    occupied: set[int] = set()
    beside: dict[int, str] = {}
    for b in paragraphs:
        on = Series.of_kind(b.kind) is Series.ON
        if on:
            beside[b.start] = b.anchor
        occupied.update(range(b.start, b.end + 1))
        if on:
            occupied.discard(b.start)
    return {
        n: beside.get(n) or line.rstrip()
        for n, line in enumerate(constants.text_lines(text), 1)
        if line.strip() and n not in occupied
    }


@dataclass(frozen=True)
class LexicalRead:
    """What the generic lexical reader hands the page: its prose and code lines.

    It answers the page with the two calls a reader record answers it with,
    `paragraphs` and `code_lines`, so the page reads every reader one way.
    """

    #: The prose the reader found, each documenting run naming its declaration.
    found: list[Paragraph]
    #: Each line holding code, in order, with the documentation it declares.
    lines: list[CodeLine]
    #: Whether the page has an `a` series: the row declares a documentation
    #: practice -- see `Language.a_series`.
    a_series: bool
    #: Whether the module's documentation can sit at the file's foot, so the
    #: `a` series meets `<eof>` -- see `Language.closing_docstring`.
    closing_docstring: bool

    def paragraphs(self, path: Path) -> list[Paragraph]:
        """Every prose run of the file as a page paragraph, in a new list."""
        return list(self.found)

    def code_lines(self) -> list[CodeLine]:
        """Each line holding code, in order, with the documentation it declares."""
        return self.lines
