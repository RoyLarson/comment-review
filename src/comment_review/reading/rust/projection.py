"""Project a completed Rust read into page paragraphs, code lines and places."""

from bisect import bisect_right
from collections.abc import Iterable
from pathlib import Path

from comment_review import constants
from comment_review.reading.diagnostics import ReadFailure
from comment_review.reading.paragraph import Paragraph
from comment_review.reading.rust.documentation import opening_end
from comment_review.reading.rust.records import (
    DETACHED_DOCUMENTATION,
    RustDocumentation,
    RustRead,
    RustScan,
    RustSectionForm,
)
from comment_review.reading.series import Kind
from comment_review.reading.source import (
    DocumentationPlace,
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
        documentation.warnings,
        placement.detached,
    )


def paragraphs_for(path: Path, read: RustRead) -> list[Paragraph] | ReadFailure:
    """Every section as one paragraph, and the shebang as a MATTER paragraph.

    A documentation section is a DOCSTRING that `documents` its owner. Any
    other section is MATTER when its form is `matter`, TRAILING when code
    precedes it on its first line, with that code as its anchor, and COMMENT
    when none does. A detached run carries the `detached-documentation`
    annotation.

    A paragraph's raw lines run from the end of the last code or comment
    before it on its first line, or from that line's start, to the end of its
    last line, so `anchor + raw_lines[0]` is the first line.

    The comments after the last code line then follow the end-of-file rule,
    and a place holds one paragraph: sections that would share one, on one
    line or in one gap, become one paragraph -- see `_one_per_place`.
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
        documents = None
        if index in owners:
            kind = Kind.DOCSTRING
            owner = owners[index]
            documents = 0 if owner is None else owner + 1
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
                documents=documents,
                annotations={DETACHED_DOCUMENTATION} if span in detached else set(),
                raw_lines=raw,
            )
        )
    return _one_per_place(paragraphs, set(code_for(read)), layout)


def _one_per_place(
    paragraphs: list[Paragraph], code: set[int], layout: "_Layout"
) -> list[Paragraph]:
    """Make the paragraphs that would share a place one paragraph.

    The opening comments follow the file-head rule first, see
    `_opening_matter`, and the comments after the last code line the
    end-of-file rule, see `_closing_matter`. Then a paragraph starting on a
    line the paragraph before it ends on is part of that paragraph, which
    keeps its kind and anchor: comments sharing a line share its place. Then
    the COMMENT paragraphs in one gap -- the lines between the same two code
    lines -- are one COMMENT paragraph there, whatever sits between them:
    blank lines, or the module's inner doc, whose lines stay its own.
    """
    paragraphs = _opening_matter(
        sorted(paragraphs, key=lambda p: p.start), code, layout
    )
    paragraphs = _closing_matter(paragraphs, code, layout)
    held = {
        n
        for p in paragraphs
        if p.kind == Kind.DOCSTRING
        for n in range(p.start, p.end + 1)
    }
    boundaries = sorted(code)
    out: list[Paragraph] = []
    gaps: dict[int, int] = {}
    for paragraph in paragraphs:
        if out and paragraph.start <= out[-1].end:
            out[-1] = _combined([out[-1], paragraph], out[-1].kind, layout, held)
            continue
        if paragraph.kind != Kind.COMMENT:
            out.append(paragraph)
            continue
        # A COMMENT holds no code line, so the count of code lines above it
        # names its gap.
        gap = bisect_right(boundaries, paragraph.end)
        at = gaps.get(gap)
        if at is None:
            gaps[gap] = len(out)
            out.append(paragraph)
        else:
            out[at] = _combined([out[at], paragraph], Kind.COMMENT, layout, held)
    return sorted(out, key=lambda p: p.start)


def _opening_matter(
    paragraphs: list[Paragraph], code: set[int], layout: "_Layout"
) -> list[Paragraph]:
    """Apply the file-head rule to the opening comments.

    The MATTER paragraphs here are the shebang and the sections that open
    the file, which the documentation stage marks; every one starts in the
    opening comments `opening_end` bounds, from the lines holding a prose
    comment and the lines holding code. The ones ending in them are one
    MATTER paragraph, at the first `f` place; a paragraph that runs on past
    them, across a blank line, is divided at the first comment line below
    it, and the part below stays a COMMENT. This is the rule the Python
    projection applies to its opening run.
    """
    matter = [p for p in paragraphs if p.kind == Kind.MATTER]
    if not matter:
        return paragraphs
    first = 1
    for span in layout.read.protected:
        first = layout.read.source.position(span.end - 1).line + 1
    end = opening_end(first, layout.prose_lines(), code)
    covered = layout.comment_lines()
    kept = [p for p in paragraphs if p.kind != Kind.MATTER]
    parts: list[Paragraph] = []
    for paragraph in matter:
        if end is None or paragraph.end <= end:
            parts.append(paragraph)
        else:
            at = next(n for n in range(end + 1, paragraph.end + 1) if n in covered)
            before, after = _divided(paragraph, at, covered)
            parts.append(before)
            kept.append(after)
    kept.append(_combined(parts, Kind.MATTER, layout, set()))
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
    kept.append(_combined(parts, Kind.MATTER, layout, set()))
    return sorted(kept, key=lambda p: p.start)


def _divided(
    paragraph: Paragraph, at: int, covered: set[int]
) -> tuple[Paragraph, Paragraph]:
    """The whole-line paragraph as two, the second starting on line `at`.

    The line above `at` is blank, and the first part ends on the last comment
    line above it. The first part keeps the annotations: a detached run's
    warning names the line it starts on, which is in that part.
    """
    end = at - 1
    while end not in covered:
        end -= 1
    halves = []
    for start, stop, notes in (
        (paragraph.start, end, paragraph.annotations),
        (at, paragraph.end, set()),
    ):
        raw = paragraph.raw_lines[start - paragraph.start : stop - paragraph.start + 1]
        halves.append(
            Paragraph(
                paragraph.path,
                start,
                stop,
                Kind.COMMENT,
                annotations=set(notes),
                raw_lines=raw,
            )
        )
    return halves[0], halves[1]


def _combined(
    parts: list[Paragraph], kind: str, layout: "_Layout", held: set[int]
) -> Paragraph:
    """One paragraph from parts in source order, with the first part's anchor.

    It documents what the first part documents.

    Its raw lines are the physical lines from the first part's first line to
    the last part's last line, blank lines included and the lines in `held`
    left out; the first line starts after the anchor, which is empty unless
    the first part trails code. Its annotations are the parts' together.
    """
    first, last = parts[0], parts[-1]
    raw = [
        layout.physical[first.start - 1][len(first.anchor) :],
        *(
            layout.physical[n - 1]
            for n in range(first.start + 1, last.end + 1)
            if n not in held
        ),
    ]
    return Paragraph(
        first.path,
        first.start,
        last.end,
        kind,
        anchor=first.anchor,
        documents=first.documents,
        annotations=set().union(*(p.annotations for p in parts)),
        raw_lines=raw,
    )


def code_for(read: RustRead) -> dict[int, str]:
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


def declarations_for(read: RustRead) -> list[DocumentationPlace]:
    """Each declaration's place, anchored at its head.

    Rust documentation goes above the declaring line, so every entry is above
    and is inserted at its anchor's line.
    """
    source = read.source
    places = []
    for declaration in source.declarations:
        line = source.position(declaration.anchor).line
        places.append(DocumentationPlace(line, line, True))
    return places


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

    def prose_lines(self) -> set[int]:
        """Every line a comment in a section stands on, in whole or in part."""
        return self._lines_of(
            region.span
            for region in self.read.source.regions
            if self.read.is_prose(region)
        )

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
