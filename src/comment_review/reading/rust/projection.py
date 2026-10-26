"""Project a completed Rust read into page paragraphs, code lines and places."""

from bisect import bisect_right
from collections.abc import Iterable
from pathlib import Path

from comment_review import constants
from comment_review.reading.diagnostics import ReadFailure
from comment_review.reading.paragraph import Paragraph
from comment_review.reading.rust.records import (
    RustDocumentation,
    RustRead,
    RustScan,
    RustSectionForm,
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
    other section is MATTER when its form is `matter`, TRAILING when code
    precedes it on its first line, with that code as its anchor, and COMMENT
    when none does.

    A paragraph's raw lines run from the end of the last code or comment
    before it on its first line, or from that line's start, to the end of its
    last line, so `anchor + raw_lines[0]` is the first line.

    The file's opening and closing comments then follow the file-head and
    end-of-file rules, and sections sharing a line are one paragraph -- see
    `_file_edges_and_shared_lines`.
    """
    source = read.source
    text = source.text
    layout = _Layout(read)
    owners = {owner.section: owner.declaration for owner in source.documentation}
    paragraphs: list[Paragraph] = []
    for span in read.protected:
        # The shebang is protected source, not a section, and the file's own
        # matter at line 1: the page files it at the first `f` place.
        line = source.position(span.start).line
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
        elif section.form == RustSectionForm.MATTER:
            kind = Kind.MATTER
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
    return _file_edges_and_shared_lines(paragraphs, set(_code(read)), layout)


def _file_edges_and_shared_lines(
    paragraphs: list[Paragraph], code: set[int], layout: "_Layout"
) -> list[Paragraph]:
    """Apply the file-head and end-of-file rules, then merge paragraphs sharing a line.

    The opening comments follow the file-head rule, see `_opening_matter`,
    and the comments after the last code line the end-of-file rule, see
    `_closing_matter`. Then a paragraph starting on a line the paragraph
    before it ends on is part of that paragraph, which keeps its kind and
    anchor.
    """
    paragraphs = _opening_matter(sorted(paragraphs, key=lambda p: p.start), layout)
    paragraphs = _closing_matter(paragraphs, code, layout)
    out: list[Paragraph] = []
    for paragraph in paragraphs:
        if out and paragraph.start <= out[-1].end:
            out[-1] = _combined([out[-1], paragraph], out[-1].kind, layout)
        else:
            out.append(paragraph)
    return sorted(out, key=lambda p: p.start)


def _opening_matter(paragraphs: list[Paragraph], layout: "_Layout") -> list[Paragraph]:
    """Apply the file-head rule to the opening comments.

    The MATTER paragraphs here are the shebang and the sections that open
    the file, which the documentation stage marks and ends before the first
    ordinary comment below the opening comments. They are one MATTER
    paragraph, at the first `f` place. This is the rule the Python
    projection applies to its opening run.
    """
    matter = [p for p in paragraphs if p.kind == Kind.MATTER]
    if not matter:
        return paragraphs
    kept = [p for p in paragraphs if p.kind != Kind.MATTER]
    kept.append(_combined(matter, Kind.MATTER, layout))
    return sorted(kept, key=lambda p: p.start)


def _closing_matter(
    paragraphs: list[Paragraph], code: set[int], layout: "_Layout"
) -> list[Paragraph]:
    """Apply the end-of-file rule to the comments after the last code line.

    The closing run is the whole-line COMMENT paragraphs after the last code
    line, when the last of them ends on the file's last line. The comments
    after the run's last blank line are one MATTER paragraph, whatever their
    forms; the comments before that blank line stay COMMENT paragraphs, and a
    paragraph that spans the blank line is divided at it. This is the rule
    the Python projection applies to its closing run.
    """
    last_code = max(code, default=0)
    total = len(layout.lines.spans)
    closing = [p for p in paragraphs if p.kind == Kind.COMMENT and p.start > last_code]
    if not closing or closing[-1].end != total:
        return paragraphs
    covered = layout.comment_lines()
    blanks = [n for n in range(closing[0].start, total + 1) if n not in covered]
    matter_from = blanks[-1] + 1 if blanks else closing[0].start
    in_run = {id(p) for p in closing}
    kept = [p for p in paragraphs if id(p) not in in_run]
    parts: list[Paragraph] = []
    for paragraph in closing:
        if paragraph.end < matter_from:
            kept.append(paragraph)
        elif paragraph.start >= matter_from:
            parts.append(paragraph)
        else:
            before, after = _divided(paragraph, matter_from, covered)
            kept.append(before)
            parts.append(after)
    kept.append(_combined(parts, Kind.MATTER, layout))
    return sorted(kept, key=lambda p: p.start)


def _divided(
    paragraph: Paragraph, at: int, covered: set[int]
) -> tuple[Paragraph, Paragraph]:
    """The whole-line paragraph as two, the second starting on line `at`.

    The line above `at` is blank, and the first part ends on the last comment
    line above it.
    """
    end = at - 1
    while end not in covered:
        end -= 1
    halves = []
    for start, stop in ((paragraph.start, end), (at, paragraph.end)):
        raw = paragraph.raw_lines[start - paragraph.start : stop - paragraph.start + 1]
        halves.append(
            Paragraph(
                paragraph.path,
                start,
                stop,
                Kind.COMMENT,
                raw_lines=raw,
            )
        )
    return halves[0], halves[1]


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

    A comment that is code, being in no section, stays. A line left with no
    code is absent, including a line inside a multi-line literal that holds
    only whitespace; the whitespace a literal holds before its line's end
    stays, as it is part of the literal.
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
        line = "".join(
            text[max(start, r.span.start) : min(end, r.span.end)] for r in pieces
        )
        if line.strip():
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
