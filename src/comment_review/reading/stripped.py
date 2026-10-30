"""The comment-stripped read of a non-Python file, and its code comparison.

The comment lexer removes admitted prose and compares the remaining lines,
right-stripped with blank lines dropped. Ambiguous comment boundaries and
spanning literals make this comparison unprovable. `StrippedRead` is the record
a page carries for every language the lexical reader reads.
"""

from collections.abc import Collection
from dataclasses import dataclass
from pathlib import Path
from typing import Self

from comment_review import constants
from comment_review.reading.diagnostics import ReadDiagnostic, ReadStage
from comment_review.reading.lexer import (
    Language,
    after_closer,
    language_for,
    paragraphs_lexical,
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
    is a line of code to the language.
    """
    lang = language_for(path)
    if lang is None:
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
    kept: dict[int, str | None] = {i + 1: ln.rstrip() for i, ln in enumerate(lines)}
    for paragraph in paragraphs:
        for offset, n in enumerate(range(paragraph.start, paragraph.end + 1)):
            if n not in kept or offset >= len(paragraph.raw_lines):
                return None  # a paragraph naming a line this text does not have
            # Both sides are right-stripped, as `kept` holds the source lines.
            actual = lines[n - 1].rstrip()
            stored = paragraph.raw_lines[offset].rstrip()
            if actual == stored:
                if _delimiter_shares_the_line(scanned[n - 1].rstrip(), lang):
                    return None
                kept[n] = None
            elif stored and actual.endswith(stored):
                kept[n] = actual[: len(actual) - len(stored)].rstrip()
            else:
                return None  # binder and the file disagree; do not reconcile
    survivors = [v for v in kept.values() if v is not None]
    code = [v for v in survivors if v.strip()]
    # !! A LITERAL THAT SPANS LINES MAKES THIS FILE UNPROVABLE. `_strip_strings`
    # is per-line and carries no open-quote state, so a line INSIDE a JS
    # template literal or a Java text block that begins with the language's
    # comment marker is read as a comment and deleted from BOTH
    # fingerprints. Measured 2026-08-17: a template literal whose body changed
    # from `// alpha` to `// omega` produced identical fingerprints and the file
    # was reported PROVEN -- a fail-OPEN in the one gate whose whole claim is
    # that executable code is byte-identical.
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
    """The interpreter line the language row names, exactly, or None.

    The reader hands it over as matter, which `_without_comments` removes, so
    the comparison checks it here on its own.
    """
    lang = language_for(path)
    return None if lang is None else lang.interpreter_line(constants.text_lines(text))


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
        """Whether `after` keeps this read's interpreter line and stripped source.

        The interpreter line is compared first, exactly, so any change to it,
        adding it or removing it is `protected-source-changed`.
        """
        if _shebang(self.text, self.path) != _shebang(after.text, after.path):
            return PreservationResult(
                False,
                (
                    ReadDiagnostic(
                        ReadStage.PLACE,
                        "protected-source-changed",
                        "the interpreter line or its presence changed",
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
