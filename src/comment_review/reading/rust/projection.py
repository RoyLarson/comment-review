"""Project a completed Rust read into page paragraphs, code lines and places."""

from bisect import bisect_right
from collections.abc import Iterable
from pathlib import Path

from comment_review import constants
from comment_review.reading.diagnostics import ReadFailure
from comment_review.reading.matter import file_matter
from comment_review.reading.paragraph import Paragraph
from comment_review.reading.rust.records import (
    RustDocumentation,
    RustRead,
    RustScan,
)
from comment_review.reading.series import Kind
from comment_review.reading.source import (
    CodeLine,
    DocPlace,
    RegionKind,
    SourceDeclaration,
    SourceRegion,
    SourceSpan,
    SourceStructure,
    lines_of_code,
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
        documentation.warnings,
        placement.detached,
    )


def paragraphs_for(path: Path, read: RustRead) -> list[Paragraph] | ReadFailure:
    """Every section as one paragraph, and the shebang as a MATTER paragraph.

    A documentation section is a DOCSTRING whose `anchor_line` is its owner's
    declaring line, or None when it documents the module. Any
    other section is TRAILING when code precedes it on its first line, with
    that code as its anchor, and COMMENT when none does.

    A paragraph's raw lines run from the end of the last code or comment
    before it on its first line, or from that line's start, to the end of its
    last line, so `anchor + raw_lines[0]` is the first line.

    The COMMENT paragraphs are then cut at the file's own matter, and
    sections sharing a line are one paragraph -- see
    `_file_edges_and_shared_lines`.
    """
    source = read.source
    text = source.text
    layout = _Layout(read)
    owners = {owner.section: owner.declaration for owner in source.documentation}
    paragraphs: list[Paragraph] = []
    # The matter opens on line 1, or on the line below the shebang.
    opens = 1
    for span in read.protected:
        # The shebang is protected source, not a section, and the file's own
        # matter at line 1: the page files it at the first `f` place.
        line = source.position(span.start).line
        opens = line + 1
        whole = text[
            layout.lines.start_of(span.start) : layout.lines.end_of(span.start)
        ]
        paragraphs.append(
            Paragraph(path.as_posix(), line, line, Kind.MATTER, raw_lines=[whole])
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
        declaring = None
        if index in owners:
            kind = Kind.DOCSTRING
            owner = owners[index]
            if owner is not None:
                declaring = _declaring_line(source, source.declarations[owner])
        else:
            kind = Kind.TRAILING if code_before else Kind.COMMENT
        raw = constants.text_lines(text[raw_start:line_end])
        paragraphs.append(
            Paragraph(
                path.as_posix(),
                first.line,
                last.line,
                kind,
                anchor=text[line_start:anchor_end] if kind == Kind.TRAILING else "",
                anchor_line=declaring,
                raw_lines=raw,
            )
        )
    return _file_edges_and_shared_lines(paragraphs, set(_code(read)), opens, layout)


def _file_edges_and_shared_lines(
    paragraphs: list[Paragraph], code: set[int], opens: int, layout: "_Layout"
) -> list[Paragraph]:
    """Cut the COMMENT paragraphs at the file's own matter, then merge shared lines.

    A prose line, for `reading.matter`, is one a COMMENT paragraph's comment
    stands on and no code does; the matter opens on `opens`. The module's
    documentation is the `//!` the documentation stage attached, a DOCSTRING;
    a doc comment that documents no owner is a COMMENT, so its lines are
    prose. Each COMMENT paragraph is cut at the matter's edges, and the parts
    inside the front matter, with the shebang, are one MATTER paragraph, as
    are the parts inside the back matter. Then a paragraph starting on a line
    the paragraph before it ends on is part of that paragraph, which keeps its
    kind and anchor.
    """
    covered = layout.comment_lines()
    prose = {
        n
        for p in paragraphs
        if p.kind == Kind.COMMENT
        for n in range(p.start, p.end + 1)
        if n in covered and n not in code
    }
    matter = file_matter(len(layout.lines.spans), opens, prose)
    cut: list[Paragraph] = []
    for paragraph in paragraphs:
        if paragraph.kind != Kind.COMMENT:
            cut.append(paragraph)
            continue
        for start, end, is_matter in matter.parts(
            paragraph.start, paragraph.end, covered
        ):
            offset = start - paragraph.start
            cut.append(
                Paragraph(
                    paragraph.path,
                    start,
                    end,
                    Kind.MATTER if is_matter else Kind.COMMENT,
                    raw_lines=paragraph.raw_lines[offset : offset + end - start + 1],
                )
            )
    kept = [p for p in cut if p.kind != Kind.MATTER]
    found = sorted((p for p in cut if p.kind == Kind.MATTER), key=lambda p: p.start)
    front = [p for p in found if p.start < matter.front.stop]
    back = [p for p in found if p.start >= matter.front.stop]
    for parts in (front, back):
        if parts:
            kept.append(_combined(parts, Kind.MATTER, layout))
    out: list[Paragraph] = []
    for paragraph in sorted(kept, key=lambda p: p.start):
        if out and paragraph.start <= out[-1].end:
            out[-1] = _combined([out[-1], paragraph], out[-1].kind, layout)
        else:
            out.append(paragraph)
    return sorted(out, key=lambda p: p.start)


def _combined(parts: list[Paragraph], kind: str, layout: "_Layout") -> Paragraph:
    """One paragraph from parts in source order, with the first part's anchors.

    Its raw lines are the physical lines from the first part's first line to
    the last part's last line, blank lines included; the first line starts
    after the anchor, which is empty unless the first part trails code.
    """
    first, last = parts[0], parts[-1]
    raw = [
        layout.physical[first.start - 1][len(first.anchor) :],
        *(layout.physical[n - 1] for n in range(first.start + 1, last.end + 1)),
    ]
    return Paragraph(
        first.path,
        first.start,
        last.end,
        kind,
        anchor=first.anchor,
        anchor_line=first.anchor_line,
        raw_lines=raw,
    )


def code_lines_for(read: RustRead) -> list[CodeLine]:
    """Each code line, with a declaration's documentation place above it.

    Rust documentation goes above the declaring line, so each declaring line's
    place is that line, above.
    """
    source = read.source
    # The placer gives a line at most one declaration, the first on it.
    declaring = (_declaring_line(source, d) for d in source.declarations)
    return lines_of_code(_code(read), {n: DocPlace(n, True) for n in declaring})


def _declaring_line(source: SourceStructure, declaration: SourceDeclaration) -> int:
    """The code line that declares this: the line a doc's `anchor_line` names."""
    return source.position(declaration.anchor).line


def _code(read: RustRead) -> dict[int, str]:
    """Each line's code: the line without its sections, shebang or trailing space.

    A comment that is code, being in no section, stays. The code is
    right-trimmed, a multi-line literal's whitespace at the line's end
    included, so the code plus what follows it on the line is the line. A
    line left with no code is absent, including a line inside a multi-line
    literal that holds only whitespace.
    """
    layout = _Layout(read)
    text = read.source.text
    code: dict[int, str] = {}
    for number, (start, end) in enumerate(layout.lines.spans, 1):
        line = "".join(
            text[max(start, region.span.start) : min(end, region.span.end)]
            for region in _overlapping(read.source.regions, start, end)
            if layout.is_code(region) or region.kind is RegionKind.WHITESPACE
        ).rstrip()
        if line:
            code[number] = line
    return code


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
    """Which regions of a read are code, its lines, and the lines comments hold."""

    def __init__(self, read: RustRead) -> None:
        self.text = read.source.text
        self.lines = _Lines(self.text)
        # Each physical line's text, as `constants.text_lines` cuts it.
        self.physical = constants.text_lines(self.text)
        self.read = read
        self.comments = [
            region.span
            for region in read.source.regions
            if region.kind is RegionKind.COMMENT
        ]

    def is_code(self, region: SourceRegion) -> bool:
        """Whether the region is code: code, a literal, or a comment in no section."""
        if region.kind in CODE_KINDS:
            return True
        return region.kind is RegionKind.COMMENT and not self.read.is_prose(region)

    def comment_lines(self) -> set[int]:
        """Every line a comment stands on, in whole or in part."""
        return self._lines_of(self.comments)

    def _lines_of(self, spans: Iterable[SourceSpan]) -> set[int]:
        return {
            line
            for span in spans
            for line in range(
                self.read.source.position(span.start).line,
                self.read.source.position(span.end - 1).line + 1,
            )
        }


def _overlapping(
    regions: tuple[SourceRegion, ...], start: int, end: int
) -> list[SourceRegion]:
    """The regions that share a character with `[start, end)`, in order."""
    found = []
    for at in range(bisect_right(regions, start, key=_end), len(regions)):
        region = regions[at]
        if region.span.start >= end:
            break
        found.append(region)
    return found


def _end(region: SourceRegion) -> int:
    return region.span.end
