"""Compare two Rust reads' code with every prose comment removed.

A prose comment is a COMMENT region inside one of the read's sections. A
COMMENT region in no section is part of its line's code, so the documentation
stage, not this module, decides which comments may change.
"""

from comment_review import constants
from comment_review.reading.diagnostics import ReadDiagnostic, ReadStage
from comment_review.reading.proof import PreservationResult
from comment_review.reading.rust.records import RustRead
from comment_review.reading.source import RegionKind


def compare_preservation(before: RustRead, after: RustRead) -> PreservationResult:
    """Whether `after` holds `before`'s protected source and code unchanged.

    The byte-order mark and the shebang are compared first, exactly, so any
    change to either, adding it or removing it is `protected-source-changed`.
    Code is then compared as the logical lines `_code_lines` returns, and any
    difference is `code-changed`.
    """
    if constants.mark_of(before.source.text) != constants.mark_of(
        after.source.text
    ) or _protected(before) != _protected(after):
        return _changed(
            "protected-source-changed", "Protected source text or its presence changed"
        )
    if _code_lines(before) != _code_lines(after):
        return _changed("code-changed", "Code outside prose comments changed")
    return PreservationResult(True, ())


def _changed(code: str, message: str) -> PreservationResult:
    return PreservationResult(False, (ReadDiagnostic(ReadStage.PLACE, code, message),))


def _protected(read: RustRead) -> tuple[str, ...]:
    # The scanner ends the shebang span before its line ending, which the
    # interpreter name includes.
    return tuple(
        read.source.slice(span) + constants.line_ending_at(read.source.text, span.end)
        for span in read.protected
    )


def _code_lines(read: RustRead) -> tuple[str, ...]:
    """The read's code as logical lines, each kept exactly but for its end.

    A line break in a WHITESPACE region ends a logical line, and so does each
    prose comment, which is removed: two fragments either side of a removal
    are never joined. The protected shebang is left out, as `_protected`
    compares it. A line break inside a literal or a code comment is part of
    its line. Each logical line loses its trailing whitespace, and a line left
    with no code is dropped, so blank lines, comment-only lines and the
    line-break style are not compared; indentation and the whitespace between
    code on a line are.
    """
    text = read.source.text
    protected = set(read.protected)
    lines: list[str] = []
    # The current logical line, as (is code, text) pieces.
    pieces: list[tuple[bool, str]] = []

    def finish() -> None:
        while pieces and not pieces[-1][0]:
            pieces.pop()
        if pieces:
            lines.append("".join(piece for _, piece in pieces))
        pieces.clear()

    for region in read.source.regions:
        span = region.span
        if read.is_prose(region) or span in protected:
            finish()
            continue
        # The byte-order mark is compared on its own, by `compare_preservation`.
        chunk = text[span.start : span.end]
        if span.start == 0:
            chunk = constants.without_mark(chunk)
        if region.kind is not RegionKind.WHITESPACE:
            pieces.append((True, chunk))
            continue
        layout = constants.LINE_BREAK.split(chunk)
        pieces.append((False, layout[0]))
        for following in layout[1:]:
            finish()
            pieces.append((False, following))
    finish()
    return tuple(lines)
