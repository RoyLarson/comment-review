"""Project a completed Rust read into page paragraphs, code lines and places."""

import re
from bisect import bisect_left, bisect_right
from pathlib import Path

from comment_review import constants
from comment_review.reading.diagnostics import ReadFailure
from comment_review.reading.paragraph import Paragraph
from comment_review.reading.rust.records import (
    DETACHED_DOCUMENTATION,
    RustDocumentation,
    RustRead,
    RustScan,
    RustSectionForm,
)
from comment_review.reading.series import Kind
from comment_review.reading.source import (
    RegionKind,
    SourceRegion,
    SourceSpan,
    SourceStructure,
)

# Regions that hold code whenever they are on a line.
CODE_KINDS = frozenset({RegionKind.CODE, RegionKind.LITERAL})


def sections_for(
    scan: RustScan,
    documentation: RustDocumentation,
    protected: tuple[SourceSpan, ...],
) -> RustRead:
    """Assemble the read from the scan, the documentation and the protected spans.

    The documentation stage leaves a comment that is part of its line's code
    out of every section, so here a COMMENT region in no section is code.
    """
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
        scan.prose,
    )


def documented_address(declaration: int | None) -> str:
    """The `a` place documenting a declaration index, `a0` for the module."""
    return f"a{0 if declaration is None else declaration + 1}"


def paragraphs_for(path: Path, read: RustRead) -> list[Paragraph] | ReadFailure:
    """Every section as one paragraph, and the shebang as a MATTER paragraph.

    A documentation section is a DOCSTRING at its owner's `a` place. Any
    other section is MATTER when its form is `matter`, or when it is not
    trailing, ends on the last line and nothing but whitespace follows it.
    The form is not tested there, so an unowned doc that the documentation
    stage made a COMMENT section counts. Otherwise it is TRAILING when code
    precedes it on its first line, with that code as its
    anchor, and COMMENT when none does. A detached run carries the
    `detached-documentation` annotation.

    A paragraph's raw lines run from the end of the last code or comment
    before it on its first line, or from that line's start, to the end of its
    last line, so `anchor + raw_lines[0]` is the first line.

    A place holds one paragraph: sections that would share one become one
    paragraph -- see `_one_per_place`.
    """
    source = read.source
    text = source.text
    layout = _Layout(read)
    owners = {owner.section: owner.declaration for owner in source.documentation}
    detached = {run.span for run in read.detached}
    paragraphs: list[Paragraph] = []
    for span in read.protected:
        # The shebang is protected source, not a section, and the file's own
        # matter at line 1: the page files it at the first `f` place.
        line = source.position(span.start).line
        whole = text[
            layout.lines.start_of(span.start) : layout.lines.end_of(span.start)
        ]
        shebang = text[span.start : span.end]
        paragraphs.append(
            Paragraph(
                path.as_posix(), line, line, Kind.MATTER, 1, shebang, raw_lines=[whole]
            )
        )
    for index, section in enumerate(source.sections):
        span = section.span
        first = source.position(span.start)
        last = source.position(span.end - 1)
        line_start = layout.lines.start_of(span.start)
        line_end = layout.lines.end_of(span.end - 1)
        before = [
            region
            for region in _overlapping(source.regions, line_start, span.start)
            if region.kind is not RegionKind.WHITESPACE
        ]
        code_before = [region for region in before if layout.is_code(region)]
        anchor_end = code_before[-1].span.end if code_before else line_start
        raw_start = before[-1].span.end if before else line_start
        if index in owners:
            kind = Kind.DOCSTRING
            address = documented_address(owners[index])
        elif section.form == RustSectionForm.MATTER or (
            not code_before
            and last.line == len(layout.lines.spans)
            and all(
                region.kind is RegionKind.WHITESPACE
                for region in _overlapping(source.regions, span.end, len(text))
            )
        ):
            kind, address = Kind.MATTER, ""
        else:
            kind = Kind.TRAILING if code_before else Kind.COMMENT
            address = ""
        raw = constants.text_lines(text[raw_start:line_end])
        prose = layout.prose_in(span)
        paragraphs.append(
            Paragraph(
                path.as_posix(),
                first.line,
                last.line,
                kind,
                len(raw),
                re.sub(r"\s+", " ", " ".join(prose)).strip(),
                anchor=text[line_start:anchor_end] if kind == Kind.TRAILING else "",
                address=address,
                annotations={DETACHED_DOCUMENTATION} if span in detached else set(),
                raw_lines=raw,
            )
        )
    shebang = {source.position(span.start).line for span in read.protected}
    return _one_per_place(paragraphs, set(code_for(read)), shebang, text)


def _one_per_place(
    paragraphs: list[Paragraph], code: set[int], shebang: set[int], text: str
) -> list[Paragraph]:
    """Make the paragraphs that would share a place one paragraph.

    Two COMMENT paragraphs with no code line between them sit in one gap, so
    in one `b` place: they are sections of different written forms, and the
    place holds them as one COMMENT paragraph. The opening matter on the line
    directly below the shebang becomes one MATTER paragraph with the shebang,
    at `f0`. The combined paragraph's raw lines are the physical lines from
    its first line to its last, blank lines included; its text is the parts'
    text in source order, and its annotations are theirs together.
    """
    lines = constants.text_lines(text)
    out: list[Paragraph] = []
    for paragraph in sorted(paragraphs, key=lambda p: p.start):
        previous = out[-1] if out else None
        same_place = previous is not None and (
            (
                previous.kind == paragraph.kind == Kind.COMMENT
                and not any(n in code for n in range(previous.end + 1, paragraph.start))
            )
            or (
                previous.kind == paragraph.kind == Kind.MATTER
                and previous.start == previous.end
                and previous.start in shebang
                and paragraph.start == previous.end + 1
            )
        )
        if previous is None or not same_place:
            out.append(paragraph)
            continue
        raw = [*previous.raw_lines, *lines[previous.end : paragraph.end]]
        out[-1] = Paragraph(
            previous.path,
            previous.start,
            paragraph.end,
            previous.kind,
            len(raw),
            " ".join(t for t in (previous.text, paragraph.text) if t),
            address=previous.address,
            annotations=previous.annotations | paragraph.annotations,
            raw_lines=raw,
        )
    return out


def code_for(read: RustRead) -> dict[int, str]:
    """Each line's code: the line without its sections, shebang or trailing space.

    A comment that is code, being in no section, stays; a line left with no
    code is absent.
    """
    layout = _Layout(read)
    text = read.source.text
    code: dict[int, str] = {}
    for number, (start, end) in enumerate(layout.lines.spans, 1):
        pieces = [
            region
            for region in _overlapping(read.source.regions, start, end)
            if layout.is_code(region) or region.kind is RegionKind.WHITESPACE
        ]
        while pieces and pieces[-1].kind is RegionKind.WHITESPACE:
            pieces.pop()
        if pieces:
            code[number] = "".join(
                text[max(start, r.span.start) : min(end, r.span.end)] for r in pieces
            )
    return code


def declarations_for(read: RustRead) -> list[tuple[int, int, bool]]:
    """The module's place, then each declaration's, anchored at its head.

    Rust documentation goes above its insertion line, so every entry is above.
    The insertion is the anchor line, or the first line of the inner doc that
    documents the declaration inside its body.
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


class _Lines:
    """Each physical line's start and end, its line break excluded."""

    def __init__(self, text: str) -> None:
        self.spans: list[tuple[int, int]] = []
        offset = 0
        for line_break in constants.LINE_BREAK.finditer(text):
            self.spans.append((offset, line_break.start()))
            offset = line_break.end()
        # As `constants.text_lines`: text after the last break is a line.
        if offset < len(text):
            self.spans.append((offset, len(text)))
        self.starts = [start for start, _ in self.spans]

    def _at(self, offset: int) -> tuple[int, int]:
        return self.spans[max(0, bisect_right(self.starts, offset) - 1)]

    def start_of(self, offset: int) -> int:
        return self._at(offset)[0]

    def end_of(self, offset: int) -> int:
        return self._at(offset)[1]


class _Layout:
    """Which regions of a read are code, its lines, and each comment's prose."""

    def __init__(self, read: RustRead) -> None:
        self.text = read.source.text
        self.lines = _Lines(self.text)
        self.read = read
        comments = [
            region.span
            for region in read.source.regions
            if region.kind is RegionKind.COMMENT
        ]
        self.comment_starts = [span.start for span in comments]
        self.prose = read.prose

    def is_code(self, region: SourceRegion) -> bool:
        """Whether the region is code: code, a literal, or a comment in no section."""
        if region.kind in CODE_KINDS:
            return True
        return region.kind is RegionKind.COMMENT and not self.read.is_prose(region)

    def prose_in(self, span: SourceSpan) -> list[str]:
        """The prose pieces of every comment inside `span`, in order."""
        first = bisect_left(self.comment_starts, span.start)
        last = bisect_left(self.comment_starts, span.end)
        return [
            self.text[piece.start : piece.end]
            for pieces in self.prose[first:last]
            for piece in pieces
        ]


def _overlapping(
    regions: tuple[SourceRegion, ...], start: int, end: int
) -> list[SourceRegion]:
    """The regions that share a character with `[start, end)`, in order."""
    found = []
    for region in regions[bisect_right(regions, start, key=_end) :]:
        if region.span.start >= end:
            break
        found.append(region)
    return found


def _end(region: SourceRegion) -> int:
    return region.span.end
