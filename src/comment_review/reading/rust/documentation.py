"""Group Rust comments into sections and decide which document which owner."""

from bisect import bisect_left, bisect_right
from collections.abc import Collection, Mapping
from dataclasses import dataclass
from typing import cast

from comment_review.reading.coordinates import SourceCoordinates
from comment_review.reading.definitions import LanguageDefinition
from comment_review.reading.diagnostics import ReadDiagnostic, ReadFailure, ReadStage
from comment_review.reading.rust.definition import MODULE, validate_rust
from comment_review.reading.rust.records import (
    ATTRIBUTE_KINDS,
    COMMENT_KINDS,
    DETACHED_DOC_CODE,
    DetachedRun,
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
    documents the module when nothing but opening matter precedes it. Either
    is on lines of its own: no other comment shares its first or last line.
    The kinds documentation attaches to are `[rules.documentation].owners`.

    Documentation that Rust attaches to an owner but no `a` place can hold is
    detached: a run behind an ordinary comment, outside the owner or in its
    body, a run between an attribute and the item, a run on the head's own
    line, a run that trails code on its line, a run sharing a line with
    another comment, a module doc with an inner attribute before it, a
    second run for one owner, the module included, and every inner doc
    inside a body, which is detached from the innermost owner whose body
    holds it. A detached run is a COMMENT section with a DetachedRun and a
    warning. Every other doc section that documents nothing is a COMMENT
    section.

    The file's opening matter is the comments `opening_end` bounds: every
    section starting in it is MATTER, up to the first section documenting an
    owner, which ends the matter. The module's inner doc is detached when
    code or a comment outside the opening matter precedes it; the page sets
    `a0` at the file head. Every other owner inserts at its head's first line.
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
        self.detached: list[DetachedRun] = []
        self.warnings: list[ReadDiagnostic] = []
        self.shebang = next(
            (t for t in scan.tokens if t.kind is RustTokenKind.SHEBANG), None
        )
        # The last line of the comments that open the file, or None.
        self.opening_end = self._opening_end()

    def run(self) -> RustDocumentation:
        for index, run in enumerate(self.runs):
            if run.code:
                continue
            if run.written is RustSectionForm.OUTER_DOC:
                self._outer(index, run)
            elif run.written is RustSectionForm.INNER_DOC:
                self._inner(index, run)
        # Every section starting in the opening comments is matter, up to the
        # first that documents an owner. A run may run on past the
        # opening comments, across a blank line; the sections divide it where
        # they end.
        if self.opening_end is not None:
            for index, run in enumerate(self.runs):
                if run.code or not self._opens(run):
                    continue
                if index in self.links:
                    break
                self.forms[index] = RustSectionForm.MATTER
        # Each section is [form, start, end, last run]; the last run is what
        # the next run is checked against.
        groups: list[list] = []
        section_of: dict[int, int] = {}
        for index, run in enumerate(self.runs):
            if run.code:
                continue
            form, start = self.forms[index], run.span.start
            tail = self._past_the_opening(index, run)
            if tail is not None:
                # The opening matter ends before the run does: the comments
                # from `tail` on are ordinary and section with what follows.
                groups.append([form, start, self._comment_end(start, tail), index])
                section_of[index] = len(groups) - 1
                form, start = RustSectionForm.COMMENT, tail
            elif groups and self._continues(groups[-1], index):
                groups[-1][2:] = [run.span.end, index]
                section_of[index] = len(groups) - 1
                continue
            groups.append([form, start, run.span.end, index])
            section_of[index] = len(groups) - 1
        sections = tuple(
            SourceSection(SourceSpan(start, end), form.value)
            for form, start, end, _ in groups
        )
        owners = tuple(
            DocumentationOwner(section_of[index], declaration)
            for index, declaration in sorted(self.links.items())
        )
        placement = RustPlacement(
            self.placement.declarations,
            tuple(self.detached),
        )
        return RustDocumentation(sections, owners, placement, tuple(self.warnings))

    def _past_the_opening(self, index: int, run: _Run) -> int | None:
        """Where the ordinary comments start, if matter ends inside the run.

        A matter run runs on past the opening comments when a blank line
        ends them and a comment of the same form follows; the first comment
        below the opening comments starts the ordinary ones.
        """
        if (
            self.forms[index] is not RustSectionForm.MATTER
            or self.opening_end is None
            or self._line(run.span.end - 1) <= self.opening_end
        ):
            return None
        return next(
            token.span.start
            for token in self.scan.tokens
            if token.kind in COMMENT_KINDS
            and token.span.start >= run.span.start
            and self._line(token.span.start) > self.opening_end
        )

    def _comment_end(self, start: int, stop: int) -> int:
        """The end of the last comment in `[start, stop)`."""
        return max(
            token.span.end
            for token in self.scan.tokens
            if token.kind in COMMENT_KINDS and start <= token.span.start < stop
        )

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

    def _opening_end(self) -> int | None:
        """The last line of the comments that open the file, or None.

        The lines handed to `opening_end` are the ones a prose comment stands
        on and the ones code stands on: a code token's first and last lines,
        and every line of a comment that is part of its line's code.
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
        return opening_end(first, prose, code)

    def _opens(self, run: _Run) -> bool:
        """Whether the run starts among the comments that open the file."""
        return (
            self.opening_end is not None
            and self._line(run.span.start) <= self.opening_end
        )

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
            # A comment before the run that is not opening matter -- below a
            # blank line, or one a run that opens the file runs on to --
            # detaches it.
            end = self.opening_end or 0
            behind = any(
                not r.code and self._line(r.span.end - 1) > end
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
        """Make the run a COMMENT with a DetachedRun and its warning."""
        self.forms[index] = RustSectionForm.COMMENT
        self.detached.append(DetachedRun(run.span, owner))
        if owner is None:
            named = "the module"
        else:
            head = self.placement.declarations[owner].header.start
            named = f"the owner whose head starts on line {self._line(head)}"
        self.warnings.append(
            ReadDiagnostic(
                ReadStage.PLACE,
                DETACHED_DOC_CODE,
                f"documentation on line {self._line(run.span.start)} "
                f"is detached from {named}",
                run.span,
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


def opening_end(
    first: int, prose_lines: Collection[int], code_lines: Collection[int]
) -> int | None:
    """The last line of the comments that open the file, or None.

    They start on `first` -- line 1, or the line directly below the shebang,
    which shares the file's own place with them -- and run while each line
    holds a prose comment and no code. A blank line, a line with code on it
    or the end of the file ends them. A comment below a blank line is not
    opening matter: filed as front matter it would be set above the blank
    line it sits under. The documentation stage and the projection both
    decide the opening matter here, from the lines each knows to hold prose
    and to hold code.
    """
    end = None
    line = first
    while line in prose_lines and line not in code_lines:
        end = line
        line += 1
    return end


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
