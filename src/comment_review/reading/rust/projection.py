"""Project a completed Rust read into page paragraphs, code lines and places."""

import re
from bisect import bisect_left, bisect_right
from collections.abc import Mapping
from pathlib import Path
from typing import cast

from comment_review import constants
from comment_review.reading.definitions import LanguageDefinition
from comment_review.reading.diagnostics import ReadFailure
from comment_review.reading.paragraph import Paragraph
from comment_review.reading.rust.definition import validate_rust
from comment_review.reading.rust.records import (
    COMMENT_KINDS,
    DETACHED_DOCUMENTATION,
    RustDocumentation,
    RustRead,
    RustScan,
    RustSectionForm,
    RustTokenKind,
)
from comment_review.reading.series import Kind
from comment_review.reading.source import RegionKind, SourceSpan, SourceStructure

# The characters a line may hold that are not code.
LAYOUT = " \t\f\ufeff"
# Regions whose text is not code: prose, and the protected shebang line.
NOT_CODE = frozenset({RegionKind.COMMENT, RegionKind.DIRECTIVE})


def sections_for(
    scan: RustScan,
    documentation: RustDocumentation,
    protected: tuple[SourceSpan, ...],
    definition: LanguageDefinition,
) -> RustRead | ReadFailure:
    """Assemble the read from the scan, the documentation and the protected spans.

    Each comment's prose is its text inside the markers `[rules.comments]`
    names for its form.
    """
    failure = validate_rust(definition)
    if failure is not None:
        return failure
    comments = cast(Mapping[str, object], definition.rules["comments"])
    opener, closer = cast(tuple[str, str], comments["block_comment"])
    openers = {
        RustTokenKind.LINE: cast(str, comments["line"]),
        RustTokenKind.OUTER_DOC_LINE: cast(str, comments["outer_doc_line"]),
        RustTokenKind.INNER_DOC_LINE: cast(str, comments["inner_doc_line"]),
        RustTokenKind.DELIMITED_COMMENT: opener,
        RustTokenKind.OUTER_DOC_DELIMITED: cast(str, comments["outer_doc_block"]),
        RustTokenKind.INNER_DOC_DELIMITED: cast(str, comments["inner_doc_block"]),
    }
    delimited = {
        RustTokenKind.DELIMITED_COMMENT,
        RustTokenKind.OUTER_DOC_DELIMITED,
        RustTokenKind.INNER_DOC_DELIMITED,
    }
    prose = []
    for token in scan.tokens:
        if token.kind not in COMMENT_KINDS:
            continue
        start = token.span.start + len(openers[token.kind])
        end = token.span.end - (len(closer) if token.kind in delimited else 0)
        prose.append(SourceSpan(min(start, end), max(start, end)))
    placement = documentation.placement
    source = SourceStructure(
        scan.text,
        scan.regions,
        documentation.sections,
        placement.declarations,
        documentation.owners,
    )
    return RustRead(
        source,
        protected,
        placement.insertions,
        documentation.warnings,
        placement.detached,
        tuple(prose),
    )


def documented_address(declaration: int | None) -> str:
    """The `a` place documenting a declaration index, `a0` for the module."""
    return f"a{0 if declaration is None else declaration + 1}"


def paragraphs_for(path: Path, read: RustRead) -> list[Paragraph] | ReadFailure:
    """Every comment section as one paragraph.

    A documentation section is a DOCSTRING at its owner's `a` place. Any
    other section is MATTER when it is the opening matter, or when it ends
    the file on its own lines; TRAILING when code precedes it on its first
    line, with that code as its anchor; else a COMMENT. A detached run
    carries the `detached-documentation` annotation. A paragraph's raw lines
    run from its first line's start, or from the end of the code before it,
    to the end of its last comment.
    """
    source = read.source
    text = source.text
    lines = constants.text_lines(text)
    code = _Code(read)
    owners = {owner.section: owner.declaration for owner in source.documentation}
    detached = {run.span for run in read.detached}
    comment_starts = [
        region.span.start
        for region in source.regions
        if region.kind is RegionKind.COMMENT
    ]
    paragraphs: list[Paragraph] = []
    for index, section in enumerate(source.sections):
        span = section.span
        first = source.position(span.start)
        last = source.position(span.end - 1)
        line_start = span.start - first.column
        before = text[line_start : span.start]
        trailing = bool(code.between(line_start, span.start).strip(LAYOUT))
        raw_start = line_start + len(before.rstrip(LAYOUT))
        joined = " ".join(
            text[prose.start : prose.end]
            for prose in read.prose[
                bisect_left(comment_starts, span.start) : bisect_left(
                    comment_starts, span.end
                )
            ]
        )
        if index in owners:
            kind = Kind.DOCSTRING
            address = documented_address(owners[index])
        elif section.form == RustSectionForm.MATTER or (
            not trailing
            and last.line == len(lines)
            and not text[span.end :].strip(LAYOUT + "\r\n")
        ):
            kind, address = Kind.MATTER, ""
        else:
            kind = Kind.TRAILING if trailing else Kind.COMMENT
            address = ""
        raw = constants.text_lines(text[raw_start : span.end])
        paragraphs.append(
            Paragraph(
                path.as_posix(),
                first.line,
                last.line,
                kind,
                len(raw),
                re.sub(r"\s+", " ", joined).strip(),
                anchor=before.rstrip(LAYOUT) if kind == Kind.TRAILING else "",
                address=address,
                annotations={DETACHED_DOCUMENTATION} if span in detached else set(),
                raw_lines=raw,
            )
        )
    return paragraphs


def code_for(read: RustRead) -> dict[int, str]:
    """Each line's code with every comment and the shebang removed, right-stripped.

    Code on both sides of a delimited comment stays code; a line left with
    no code is absent.
    """
    text = read.source.text
    found = _Code(read)
    code: dict[int, str] = {}
    offset = 0
    for number, line in enumerate(constants.text_lines(text), 1):
        end = offset + len(line)
        kept = found.between(offset, end).rstrip()
        if kept.strip(LAYOUT):
            code[number] = kept
        offset = end
        if text.startswith("\r\n", offset):
            offset += 2
        elif offset < len(text) and text[offset] in "\r\n":
            offset += 1
    return code


def declarations_for(read: RustRead) -> list[tuple[int, int, bool]]:
    """The module's place, then each declaration's at its head's first line.

    Rust documentation goes above the line it documents, so every entry is
    above.
    """
    source = read.source
    return [
        (0, read.insertions[0], True),
        *(
            (source.position(declaration.anchor).line, insertion, True)
            for declaration, insertion in zip(
                source.declarations, read.insertions[1:], strict=True
            )
        ),
    ]


class _Code:
    """The read's text outside its comment and directive regions."""

    def __init__(self, read: RustRead) -> None:
        self.text = read.source.text
        self.spans = [
            region.span for region in read.source.regions if region.kind not in NOT_CODE
        ]
        self.ends = [span.end for span in self.spans]

    def between(self, start: int, end: int) -> str:
        """The code in `[start, end)`, its pieces joined in source order."""
        kept = []
        for span in self.spans[bisect_right(self.ends, start) :]:
            if span.start >= end:
                break
            kept.append(self.text[max(start, span.start) : min(end, span.end)])
        return "".join(kept)
