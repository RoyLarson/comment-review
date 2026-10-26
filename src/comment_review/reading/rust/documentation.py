"""Group Rust comments into sections and decide which document which owner."""

from bisect import bisect_left, bisect_right
from collections.abc import Mapping
from dataclasses import dataclass
from typing import cast

from comment_review import constants
from comment_review.reading.coordinates import SourceCoordinates
from comment_review.reading.definitions import LanguageDefinition
from comment_review.reading.diagnostics import (
    DetachedDocumentation,
    ReadFailure,
    ReadStage,
)
from comment_review.reading.matter import file_matter
from comment_review.reading.rust.definition import MODULE, validate_rust
from comment_review.reading.rust.records import (
    ATTRIBUTE_KINDS,
    COMMENT_KINDS,
    DETACHED_DOC_CODE,
    RustDocumentation,
    RustPlacement,
    RustScan,
    RustSectionForm,
    RustToken,
    RustTokenKind,
    significant_tokens,
)
from comment_review.reading.source import (
    DocumentationOwner,
    SourceDeclaration,
    SourceSection,
    SourceSpan,
)

# The form a comment is written in, before anything is known of what it documents.
WRITTEN_FORM = {
    RustTokenKind.LINE: RustSectionForm.COMMENT,
    RustTokenKind.DELIMITED_COMMENT: RustSectionForm.COMMENT,
    RustTokenKind.OUTER_DOC_LINE: RustSectionForm.OUTER_DOC,
    RustTokenKind.OUTER_DOC_DELIMITED: RustSectionForm.OUTER_DOC,
    RustTokenKind.INNER_DOC_LINE: RustSectionForm.INNER_DOC,
    RustTokenKind.INNER_DOC_DELIMITED: RustSectionForm.INNER_DOC,
}


@dataclass
class _Run:
    """Comments of one written form with nothing but whitespace between them."""

    span: SourceSpan
    written: RustSectionForm
    # A comment with code before it on its line stands alone.
    trailing: bool
    # A comment that is part of its line's code: never a section.
    code: bool = False
    # Whether code has been read since the run's last comment.
    closed: bool = False


def documentation_in(
    scan: RustScan, placement: RustPlacement, definition: LanguageDefinition
) -> RustDocumentation | ReadFailure:
    """Section every comment and give each documentation section its owner.

    A run is comments of one written form -- ordinary, outer doc or inner
    doc -- with only whitespace between them, blank lines included. A run
    that documents an owner is a section; the runs that are ordinary
    comments, including the docs detached into them, with no code between
    them are one section. A comment with code before it on its line is a
    section of its own. A comment followed by code on the line it ends on is
    part of that line's code: it is no section, documents nothing, and ends
    the run above it. A doc above it is separated from its owner, as by an
    ordinary comment, and is detached. A comment followed only by another
    comment on its line is prose, and the two share a place.

    An outer doc section that ends on a line above an owner's head, with only
    whitespace between them, documents that owner. An inner doc section
    documents the module when nothing but the opening comments precede it. Either
    is on lines of its own: no other comment shares its first or last line.
    The kinds documentation attaches to are `[rules.documentation].owners`.

    Documentation that Rust attaches to an owner but no `a` place can hold is
    detached: a run behind an ordinary comment, outside the owner or in its
    body, a run between an attribute and the item, a run on the head's own
    line, a run that trails code on its line, a run sharing a line with
    another comment, a module doc with an inner attribute before it, a
    second run for one owner, the module included, and every inner doc
    inside a body, which is detached from the innermost owner whose body
    holds it. A detached run is a COMMENT section with a warning. Every other
    doc section that documents nothing is a COMMENT section.

    The opening comments are the ones `_opening` gives. The module's inner doc
    is detached when code or a comment outside them precedes it; the page sets
    `a0` at the file head. Every other owner inserts at its head's first line.
    Which sections are the file's own matter is the projection's to say.
    """
    failure = validate_rust(definition)
    if failure is not None:
        return failure
    documentation = cast(Mapping[str, object], definition.rules["documentation"])
    declarations = cast(Mapping[str, object], definition.rules["declarations"])
    assigner = _Assigner(
        scan,
        placement,
        frozenset(cast(tuple[str, ...], documentation["owners"])),
        cast(str, declarations["body_open"]),
        cast(str, declarations["terminator"]),
    )
    return assigner.run()


class _Assigner:
    """One pass over the comment runs, assigning each its form and owner."""

    def __init__(
        self,
        scan: RustScan,
        placement: RustPlacement,
        owner_kinds: frozenset[str],
        body_open: str,
        terminator: str,
    ) -> None:
        self.scan = scan
        self.placement = placement
        self.owner_kinds = owner_kinds
        self.body_open = body_open
        self.terminator = terminator
        self.coordinates = SourceCoordinates(scan.text)
        self.code = significant_tokens(scan.tokens)
        self.starts = [token.span.start for token in self.code]
        self.heads = [
            declaration.header.start for declaration in placement.declarations
        ]
        self.item_starts = [self._item_start(d) for d in placement.declarations]
        # From `_nesting` and `_bodies`, built the first time `_holder` asks.
        self.open_at: list[int | None] | None = None
        self.enclosing: dict[int, int | None] = {}
        self.bodies: dict[int, int] = {}
        self.runs = _runs(scan.tokens, self.coordinates)
        self.forms = [run.written for run in self.runs]
        self.links: dict[int, int | None] = {}
        self.warnings: list[DetachedDocumentation] = []
        self.shebang = next(
            (t for t in scan.tokens if t.kind is RustTokenKind.SHEBANG), None
        )
        # The lines of the comments that open the file.
        self.opening = self._opening()

    def run(self) -> RustDocumentation:
        for index, run in enumerate(self.runs):
            if run.code:
                continue
            if run.written is RustSectionForm.OUTER_DOC:
                self._outer(index, run)
            elif run.written is RustSectionForm.INNER_DOC:
                self._inner(index, run)
        # Each section is [form, start, end, last run]; the last run is what
        # the next run is checked against.
        groups: list[list] = []
        section_of: dict[int, int] = {}
        for index, run in enumerate(self.runs):
            if run.code:
                continue
            if groups and self._continues(groups[-1], index):
                groups[-1][2:] = [run.span.end, index]
            else:
                groups.append([self.forms[index], run.span.start, run.span.end, index])
            section_of[index] = len(groups) - 1
        sections = tuple(
            SourceSection(SourceSpan(start, end), form.value)
            for form, start, end, _ in groups
        )
        owners = tuple(
            DocumentationOwner(section_of[index], declaration)
            for index, declaration in sorted(self.links.items())
        )
        return RustDocumentation(sections, owners, self.placement, tuple(self.warnings))

    def _continues(self, group: list, index: int) -> bool:
        """Whether run `index` is part of the COMMENT section `group`.

        Only code ends a section: the run follows the section's last run
        directly, both are ordinary comments that stand on lines of their own,
        and no code was read between them.
        """
        before = group[3]
        first, second = self.runs[before], self.runs[index]
        return (
            index == before + 1
            and not first.closed
            and group[0] is RustSectionForm.COMMENT
            and self.forms[index] is RustSectionForm.COMMENT
            and not first.trailing
            and not second.trailing
        )

    def _opening(self) -> range:
        """The lines of the comments that open the file, documentation included.

        They are the front matter `reading.matter` gives when every comment,
        documentation or not, counts as prose. They open on line 1, or on the
        line directly below the shebang, which shares the file's own place with
        them. A prose line is one a comment stands on and no code does: a code
        token's first and last lines, and every line of a comment that is part
        of its line's code, are code.
        """
        first = 1 if self.shebang is None else self._line(self.shebang.span.end - 1) + 1
        prose: set[int] = set()
        code: set[int] = set()
        for at, token in enumerate(self.scan.tokens):
            if token.kind not in COMMENT_KINDS:
                continue
            lines = range(
                self._line(token.span.start), self._line(token.span.end - 1) + 1
            )
            followed = _followed_on_its_line(self.scan.tokens, at, self.coordinates)
            (code if followed else prose).update(lines)
        for token in self.code:
            code.update((self._line(token.span.start), self._line(token.span.end - 1)))
        total = len(constants.text_lines(self.scan.text))
        return file_matter(total, first, prose - code).front

    def _beside(self, index: int, run: _Run) -> bool:
        """Whether another comment shares the run's first or last line.

        A doc that does is detached: the comments on that line are one
        paragraph at the line's place, and an `a` place holds its doc alone.
        """
        before = index > 0 and self._line(
            self.runs[index - 1].span.end - 1
        ) == self._line(run.span.start)
        after = index + 1 < len(self.runs) and self._line(
            self.runs[index + 1].span.start
        ) == self._line(run.span.end - 1)
        return before or after

    def _outer(self, index: int, run: _Run) -> None:
        """Attach a run directly above a head; detach one inside or behind it."""
        following = bisect_left(self.starts, run.span.end)
        if following == len(self.code):
            self.forms[index] = RustSectionForm.COMMENT
            return
        start = self.code[following].span.start
        owner = bisect_left(self.heads, start)
        if owner < len(self.heads) and self.heads[owner] == start:
            nearest = index + 1 == len(self.runs) or (
                self.runs[index + 1].span.start > start
            )
            above = self._line(run.span.end - 1) < self._line(start)
            if nearest and above and not run.trailing:
                self._attach(index, run, owner)
            else:
                self._detach(index, run, owner)
            return
        owner = bisect_right(self.heads, start) - 1
        if owner >= 0 and start <= self.item_starts[owner]:
            self._detach(index, run, owner)
            return
        self.forms[index] = RustSectionForm.COMMENT

    def _inner(self, index: int, run: _Run) -> None:
        """Attach a run to the module, or detach one inside an owner's body."""
        before = bisect_left(self.starts, run.span.start) - 1
        # Code before the run -- an inner attribute -- keeps it from `a0`,
        # which the page sets at the file head.
        preceded = before >= 0
        while before >= 0 and self.code[before].kind is RustTokenKind.INNER_ATTRIBUTE:
            before -= 1
        if before < 0:
            # A comment before the run that is not among the opening comments
            # -- below a blank line, or one a run that opens the file runs on
            # to -- detaches it.
            behind = any(
                not r.code and self._line(r.span.end - 1) >= self.opening.stop
                for r in self.runs[:index]
            )
            if MODULE not in self.owner_kinds:
                self.forms[index] = RustSectionForm.COMMENT
            elif preceded or behind:
                self._detach(index, run, None)
            else:
                self._attach(index, run, None)
            return
        # Inside a body an inner doc documents no owner: it stays at the place
        # its position gives it, detached from the owner whose body holds it.
        owner = self._holder(run.span.start)
        if owner is None:
            self.forms[index] = RustSectionForm.COMMENT
        else:
            self._detach(index, run, owner)

    def _attach(self, index: int, run: _Run, owner: int | None) -> None:
        """Link the run to its owner, or detach it.

        An owner that has a doc, or a run sharing a line with another
        comment, detaches the run.
        """
        if owner in self.links.values() or self._beside(index, run):
            self._detach(index, run, owner)
        else:
            self.links[index] = owner

    def _detach(self, index: int, run: _Run, owner: int | None) -> None:
        """Make the run a COMMENT with its warning."""
        self.forms[index] = RustSectionForm.COMMENT
        if owner is None:
            line = None
            named = "the module"
        else:
            line = self._line(self.placement.declarations[owner].header.start)
            named = f"the owner whose head starts on line {line}"
        self.warnings.append(
            DetachedDocumentation(
                ReadStage.PLACE,
                DETACHED_DOC_CODE,
                f"documentation on line {self._line(run.span.start)} "
                f"is detached from {named}",
                run.span,
                owner_line=line,
            )
        )

    def _holder(self, offset: int) -> int | None:
        """The innermost owner whose body holds `offset`, or None at file level.

        It walks out through the delimiters still open at `offset`, innermost
        first, and returns the owner of the first one that is an owner's body.
        """
        if self.open_at is None:
            self.open_at, self.enclosing = _nesting(self.code)
            self.bodies = self._bodies()
        before = bisect_left(self.starts, offset) - 1
        at = self.open_at[before] if before >= 0 else None
        while at is not None:
            owner = self.bodies.get(at)
            if owner is not None:
                return owner
            at = self.enclosing[at]
        return None

    def _bodies(self) -> dict[int, int]:
        """Each owner's body, as the index into `self.code` of its opener.

        An item's body is the first `body_open` outside any other delimiter
        after its keyword, unless a terminator or the close of the delimiter
        holding the item ends it first. Where one opener follows several
        owners, it is the body of the last of them.
        """
        starting: dict[int, list[int]] = {}
        for owner, start in enumerate(self.item_starts):
            starting.setdefault(bisect_left(self.starts, start), []).append(owner)
        bodies: dict[int, int] = {}
        # The owners still waiting for a body, per open delimiter, outermost first.
        waiting: list[list[int]] = [[]]
        for index, token in enumerate(self.code):
            waiting[-1].extend(starting.get(index, ()))
            spelling = self._spelled(token)
            if token.kind is RustTokenKind.OPEN:
                if spelling == self.body_open and waiting[-1]:
                    bodies[index] = waiting[-1][-1]
                    waiting[-1].clear()
                waiting.append([])
            elif token.kind is RustTokenKind.CLOSE:
                if len(waiting) > 1:
                    waiting.pop()
            elif spelling == self.terminator:
                waiting[-1].clear()
        return bodies

    def _item_start(self, declaration: SourceDeclaration) -> int:
        """Where the owner's keyword or member begins, past its outer attributes."""
        at = bisect_left(self.starts, declaration.header.start)
        while self.code[at].kind is RustTokenKind.OUTER_ATTRIBUTE:
            at += 1
        return self.code[at].span.start

    def _line(self, offset: int) -> int:
        return self.coordinates.position(offset).line

    def _spelled(self, token: RustToken) -> str:
        return self.scan.text[token.span.start : token.span.end]


def _runs(tokens: tuple[RustToken, ...], coordinates: SourceCoordinates) -> list[_Run]:
    """Group comments of one written form that only whitespace separates.

    A comment followed by code on the line it ends on is part of that line's
    code: it is a run of its own, marked `code`, and it ends the run above
    it. A comment followed only by another comment stays prose.
    """
    runs: list[_Run] = []
    code_end: int | None = None
    for at, token in enumerate(tokens):
        if token.kind in COMMENT_KINDS:
            line = coordinates.position(token.span.start).line
            trailing = (
                code_end is not None and coordinates.position(code_end - 1).line == line
            )
            if _followed_on_its_line(tokens, at, coordinates):
                if runs:
                    runs[-1].closed = True
                runs.append(_Run(token.span, WRITTEN_FORM[token.kind], trailing, True))
                code_end = token.span.end
                continue
            written = WRITTEN_FORM[token.kind]
            last = runs[-1] if runs else None
            if (
                last is not None
                and not last.closed
                and not last.trailing
                and not last.code
                and not trailing
                and last.written is written
            ):
                last.span = SourceSpan(last.span.start, token.span.end)
            else:
                runs.append(_Run(token.span, written, trailing))
        elif token.kind is not RustTokenKind.WHITESPACE:
            if runs:
                runs[-1].closed = True
            if token.kind not in ATTRIBUTE_KINDS:
                code_end = token.span.end
    return runs


def _nesting(
    code: list[RustToken],
) -> tuple[list[int | None], dict[int, int | None]]:
    """Which delimiters are open around each code token, by index into `code`.

    The first list gives, for each token, the innermost delimiter still open
    after it: the token itself for an opener, None at file level. The mapping
    gives, for each opener, the delimiter enclosing it.
    """
    open_at: list[int | None] = []
    enclosing: dict[int, int | None] = {}
    stack: list[int] = []
    for index, token in enumerate(code):
        if token.kind is RustTokenKind.OPEN:
            enclosing[index] = stack[-1] if stack else None
            stack.append(index)
        elif token.kind is RustTokenKind.CLOSE and stack:
            stack.pop()
        open_at.append(stack[-1] if stack else None)
    return open_at, enclosing


def _followed_on_its_line(
    tokens: tuple[RustToken, ...], at: int, coordinates: SourceCoordinates
) -> bool:
    """Whether a code token starts on the line `tokens[at]` ends on.

    Whitespace and comments are not code, so a comment followed by a comment
    alone is not followed.
    """
    end_line = coordinates.position(tokens[at].span.end - 1).line
    following = next(
        (
            tokens[index]
            for index in range(at + 1, len(tokens))
            if tokens[index].kind is not RustTokenKind.WHITESPACE
            and tokens[index].kind not in COMMENT_KINDS
        ),
        None,
    )
    return (
        following is not None
        and coordinates.position(following.span.start).line == end_line
    )
