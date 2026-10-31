"""The comment-stripped read of a non-Python file, and its code comparison.

The comment lexer removes admitted prose and compares the remaining lines,
right-stripped with blank lines dropped. Ambiguous comment boundaries and
spanning literals make this comparison unprovable. `StrippedRead` is the record
a page carries for every language the lexical reader reads.
"""

import re
from collections.abc import Collection
from dataclasses import dataclass
from pathlib import Path
from typing import Self

from comment_review import constants
from comment_review.reading.diagnostics import ReadDiagnostic, ReadStage
from comment_review.reading.lexer import (
    BLANK,
    Language,
    after_closer,
    language_for,
    paragraphs_lexical,
    scan_strings,
)
from comment_review.reading.proof import UNPROVABLE, PreservationResult

#: Annotations saying a paragraph can hold code the read did not see as code.
_UNPROVABLE_MARKS = {"unterminated-paragraph-comment", "line-ending-in-comment"}


def _delimiter_shares_the_line(line: str, lang: Language) -> bool:
    """A paragraph-comment delimiter with real code beside it, on this ONE line.

    `paragraphs_lexical` stores the WHOLE line for a paragraph comment's opening,
    closing or single-line form -- including any code that sits before the
    opener or after the closer -- so that line is stored identically to a line
    that is comment start to end. Re-scanning the line for the delimiters
    themselves is what separates them.

    ! A raw substring search, where gather's own lexer is string-literal-aware.
    A delimiter spelled inside a string literal on the same line trips this and
    routes a safe line to `unprovable` -- the SAFE direction for a proof to
    fail, so it stands in place of a second copy of gather's quoting logic.

    Comments are not code: text after a closer that `after_closer` reads as
    comments only, and text before an opener that holds a closer -- the tail
    of the comment closing there -- leave the line whole prose.
    """
    for opener, closer in lang.block_comment:
        if opener in line:
            before = line[: line.index(opener)]
            if before.strip() and closer not in before:
                return True
        if closer in line:
            rest = line[line.index(closer) + len(closer) :]
            if rest.strip() and not after_closer(rest, lang).comment:
                return True
    return False


def _continues(line: str, lang: Language) -> bool:
    """Whether the line ends in an odd run of one of the row's continuations."""
    return any((len(line) - len(line.rstrip(c))) % 2 for c in lang.line_continuations)


def _comment_in_a_string(
    kept: dict[int, str | None], partial: set[int], lang: Language
) -> bool:
    """Whether a comment stands where a string literal is still open.

    The gather reads each line with no quote carried from the line above, so a
    line inside a literal that spans lines and begins with the row's comment
    marker is read as a comment. `kept` holds each line as the comparison keeps
    it: whole, as its code prefix (the lines in `partial`), or None for a line
    a comment holds whole. Walking it with the open quote carried finds that
    line: a comment line reached with a quote open is string text, and so is a
    comment trailing a prefix that leaves a quote open.
    """
    quote = ""
    for n, v in kept.items():
        if v is None:
            if quote:
                return True
            continue
        _, quote = scan_strings(v, lang, quote)
        if quote and n in partial:
            return True
    return False


#: An element opens at `<Name` or `<>` and closes at `</` or `/>`. Outside an
#: element a word, `)` or `]` before the `<` makes it a comparison or a type
#: argument; inside one it is text beside a child element.
_ELEMENT_EDGE = re.compile(r"</|/>|<(?:[A-Za-z_$]|>)")
_BEFORE_COMPARISON = re.compile(r"[\w)\]]")


def _comment_in_an_element(
    kept: dict[int, str | None], partial: set[int], lang: Language
) -> bool:
    """Whether a comment stands between the tags of a markup element.

    Text between tags is neither code nor comment, so `// text` there is text.
    The walk counts elements still open over each line's code, string literals
    blanked: a line a comment holds whole answers at the depth it is reached,
    a line trailing one at the depth its code leaves. A count the code never
    closes (an arrow function's `<T>(x)`) refuses the comments below it, which
    is the safe direction.
    """
    depth = 0
    for n, v in kept.items():
        if v is None:
            if depth:
                return True
            continue
        blanked, _ = scan_strings(v, lang)
        for edge in _ELEMENT_EDGE.finditer(blanked):
            if edge[0] in ("</", "/>"):
                depth = max(depth - 1, 0)
            elif depth or not (
                edge.start() and _BEFORE_COMPARISON.match(blanked[edge.start() - 1])
            ):
                depth += 1
        if depth and n in partial:
            return True
    return False


def _without_comments(text: str, path: Path) -> str | None:
    """The file with every comment paragraph removed, or None if unprovable here.

    Exact where the data allows it: a paragraph's `raw_lines` is a literal slice of
    the source, so a line whose stored text matches it exactly is dropped whole,
    and a line whose stored text is only a SUFFIX (the trailing-comment case)
    keeps its code prefix. A line this cannot place -- code sharing a line with
    a paragraph-comment delimiter, see `_delimiter_shares_the_line` -- makes the
    whole file unprovable.

    An UNTERMINATED paragraph comment is refused the same way, on the gather's own
    `unterminated-paragraph-comment` annotation. The lexer swallows every line below
    the opener into that run, so code below it never reaches the comparison and
    the stripped text is merely SHORT -- short, plausible, and equal on two
    files whose executable code differs. A line ending the row states inside a
    comment is refused the same way, on `line-ending-in-comment`: what follows it
    is a line of code to the language. A comment standing where a string literal
    is still open is refused too, see `_comment_in_a_string`, and so is one between
    the tags of a markup element, see `_comment_in_an_element`.

    Text holding a lone CR is refused first: the lexer ends a line there, and a
    shell or compiler may not, so the comment may run on into code.
    """
    lang = language_for(path)
    if lang is None or constants.holds_lone_cr(text):
        return None
    try:
        paragraphs = paragraphs_lexical(path, text, lang)
    except Exception:  # noqa: BLE001  -- an unprovable file is reported, not passed
        return None
    if any(_UNPROVABLE_MARKS & b.annotations for b in paragraphs):
        return None
    lines = constants.text_lines(text)
    scanned = constants.scan_lines(text)
    # Pre-seed every line as itself; a paragraph below either drops its entry
    # (None) or replaces it with the code prefix it proved survives.
    # Blanks after a continuation character keep it from continuing, so a line
    # ending in one keeps them.
    kept: dict[int, str | None] = {
        i + 1: ln if _continues(ln.rstrip(BLANK), lang) else ln.rstrip(BLANK)
        for i, ln in enumerate(lines)
    }
    partial: set[int] = set()  # lines kept as a code prefix before a comment
    for paragraph in paragraphs:
        for offset, n in enumerate(range(paragraph.start, paragraph.end + 1)):
            if n not in kept or offset >= len(paragraph.raw_lines):
                return None  # a paragraph naming a line this text does not have
            # Both sides are right-stripped, as `kept` holds the source lines.
            actual = lines[n - 1].rstrip(BLANK)
            stored = paragraph.raw_lines[offset].rstrip(BLANK)
            if actual == stored:
                if _delimiter_shares_the_line(scanned[n - 1].rstrip(), lang):
                    return None
                kept[n] = None
            elif stored and actual.endswith(stored):
                prefix = actual[: len(actual) - len(stored)].rstrip(BLANK)
                # Blanks between a continuation character and the comment keep
                # it from joining the next line, so they are code.
                gap = stored[: len(stored) - len(stored.lstrip(BLANK))]
                if _continues(prefix, lang):
                    if not gap:
                        # The comment touches the character, so removing it
                        # would make a continuation the stripped text cannot show.
                        return None
                    prefix += gap
                kept[n] = prefix
                partial.add(n)
            else:
                return None  # binder and the file disagree; do not reconcile
    if _comment_in_a_string(kept, partial, lang):
        return None
    if path.suffix.lower() in lang.element_suffixes and _comment_in_an_element(
        kept, partial, lang
    ):
        return None
    code = []
    joined = False
    for n, v in kept.items():
        if joined or (v is not None and v.strip(BLANK)):
            # The line a continuation joins is code whatever it holds.
            code.append(lines[n - 1].rstrip(BLANK) if v is None else v)
        joined = v is not None and n not in partial and _continues(lines[n - 1], lang)
    # !! A LITERAL THAT SPANS LINES THE ROW CANNOT TRACK MAKES THIS FILE
    # UNPROVABLE. The gather carries no quote from line to line, so a line INSIDE
    # a JS template literal or a Java text block that begins with the language's
    # comment marker is read as a comment and deleted from BOTH fingerprints, so
    # a changed literal body compares equal and the file reports PROVEN, where
    # the claim is that executable code is byte-identical.
    # `_comment_in_a_string` catches this for the quotes `scan_strings` tracks;
    # the row's `spanning_quotes` are the ones it does not.
    #
    # ! This refuses on the delimiter's PRESENCE, not on parity: parity is what
    # the per-line lexer already cannot compute, so trusting it here would be
    # the same mistake one layer up. A proof that refuses costs a report; a
    # proof that lies costs the claim.
    #
    # ! A literal opens on a line of code, so a file with none has no literal,
    # and a delimiter spelled in one of its comments is prose.
    if code and any(q in text for q in lang.spanning_quotes):
        return None
    return "\n".join(code)


def code_fingerprint(text: str, path: Path) -> tuple[str, str]:
    """Compare non-Python code using the language's comment-stripped source.

    Args:
        text: the file's contents.
        path: used only for its suffix, to pick which comparison runs.

    Returns:
        `(kind, fingerprint)`. `kind` is "stripped" or "unprovable". A path no
        lexical row covers -- Python among them -- returns "unprovable". An
        unprovable file carries an empty fingerprint and cannot be proven.

        An empty fingerprint of kind "stripped" is a file its row reads as
        holding no code line. Two of those compare equal because neither holds
        code, whatever their comments say, and `preserved` reads `kind` before
        it compares the strings. "No code line" is the row's reading: a path
        with no row is never "stripped", and neither is a file with an
        unterminated comment or a line ending the row states inside a comment.
        A row sees comment delimiters and nothing a language does before them,
        so a directive held in a comment, or a closer spelled by an escape or a
        line splice, is a comment here.
    """
    stripped = _without_comments(text, path)
    if stripped is None:
        return "unprovable", ""
    return "stripped", stripped


def _shebang(text: str, path: Path) -> str | None:
    """The interpreter line the language row names, with its ending, or None.

    The reader hands it over as matter, which `_without_comments` removes, so
    the comparison checks it here on its own. The ending is part of the line:
    a CRLF interpreter line names a different interpreter than an LF one. A
    lone CR is refused before this runs, so line 1 ends in LF, CRLF or the end
    of the file.
    """
    lang = language_for(path)
    if lang is None:
        return None
    line = lang.interpreter_line(constants.text_lines(text))
    if line is None:
        return None
    return line + constants.line_ending_at(text, len(line))


@dataclass(frozen=True)
class StrippedRead:
    """A lexically read file, compared by its comment-stripped source.

    Its documentation is comment prose, which the comparison removes, so an
    approved docstring alteration needs no owner here.
    """

    text: str
    path: Path

    @property
    def proof(self) -> str:
        """The comparison's name, as a proof report prints it."""
        return "stripped"

    @property
    def warnings(self) -> tuple[ReadDiagnostic, ...]:
        """The read's warnings: a lexical read reports none."""
        return ()

    def preserved(
        self,
        after: Self,
        *,
        documented: Collection[tuple[int | None, int | None]] | None = None,
    ) -> PreservationResult:
        """Whether `after` keeps this read's mark, interpreter line and source.

        The byte-order mark and the interpreter line are compared first,
        exactly, so any change to either, adding it or removing it is
        `protected-source-changed`.
        """
        if constants.mark_of(self.text) != constants.mark_of(after.text) or (
            _shebang(self.text, self.path) != _shebang(after.text, after.path)
        ):
            return PreservationResult(
                False,
                (
                    ReadDiagnostic(
                        ReadStage.PLACE,
                        "protected-source-changed",
                        "the byte-order mark, the interpreter line or their "
                        "presence changed",
                    ),
                ),
            )
        kind, want = code_fingerprint(self.text, self.path)
        got_kind, got = code_fingerprint(after.text, after.path)
        if kind != "stripped" or got_kind != "stripped":
            return PreservationResult(
                False,
                (
                    ReadDiagnostic(
                        ReadStage.PLACE,
                        UNPROVABLE,
                        "prose could not be separated from code",
                    ),
                ),
            )
        if want != got:
            return PreservationResult(
                False,
                (
                    ReadDiagnostic(
                        ReadStage.PLACE,
                        "code-changed",
                        "the comment-stripped source differs",
                    ),
                ),
            )
        return PreservationResult(True, ())
