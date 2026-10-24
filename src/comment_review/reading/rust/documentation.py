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
    DETACHED_DOCUMENTATION,
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

    A section is a run of comments of one written form -- ordinary, outer doc
    or inner doc -- with only whitespace between them, blank lines included.
    A comment with code before it on its line is a section of its own. A
    comment followed by code on the line it ends on is part of that line's
    code: it is no section, documents nothing, and ends the run above it. A
    doc above it is separated from its owner, as by an ordinary comment, and
    is detached. A comment followed only by another comment on its line is
    prose, and the two share a place.

    An outer doc section that ends on a line above an owner's head, with only
    whitespace between them and no comment before it on its first line,
    documents that owner. An inner doc section documents the module when
    nothing but opening matter precedes it, or the owner whose body it opens:
    the first comment in that body, on a line of its own. The kinds
    documentation attaches to are `[rules.documentation].owners`.

    Documentation that Rust attaches to an owner but no `a` place can hold is
    detached: a run behind an ordinary comment, outside the owner or in its
    body, a run between an attribute and the item, a run on the head's own
    line, a run that trails code or another comment on its line, a module
    doc with an inner attribute before it, or a second run for one owner, the
    module included. A detached run is a COMMENT section with a DetachedRun
    and a warning. Every other doc section that documents nothing is a
    COMMENT section.

    The file's opening matter is the comments `opening_end` bounds: every
    section starting in it is MATTER, up to the first section documenting an
    owner, which ends the matter. The module's inner doc is detached when
    code or a comment outside the opening matter precedes it; the page sets
    `a0` at the file head, so `insertions[0]` stays 1. An owner documented by
    an inner doc inserts at that doc's first line, inside its body; every
    other owner inserts at its head's first line.
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
        self.bodies = [self._item_start(d) for d in placement.declarations]
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
        # first that documents an owner. A section of one form may run on past
        # the opening comments, across a blank line; the projection divides it
        # where they end.
        if self.opening_end is not None:
            for index, run in enumerate(self.runs):
                if run.code or not self._opens(run):
                    continue
                if index in self.links:
                    break
                self.forms[index] = RustSectionForm.MATTER
        kept = [index for index, run in enumerate(self.runs) if not run.code]
        section_of = {run: section for section, run in enumerate(kept)}
        sections = tuple(
            SourceSection(self.runs[index].span, self.forms[index].value)
            for index in kept
        )
        owners = tuple(
            DocumentationOwner(section_of[index], declaration)
            for index, declaration in sorted(self.links.items())
        )
        # An owner documented by an inner doc is documented inside its body, so
        # its insertion is the inner doc's first line rather than its head's.
        inner = {
            owner: self._line(self.runs[index].span.start)
            for index, owner in self.links.items()
            if owner is not None and self.forms[index] is RustSectionForm.INNER_DOC
        }
        placement = RustPlacement(
            self.placement.declarations,
            (
                self.placement.insertions[0],
                *(
                    inner.get(owner, line)
                    for owner, line in enumerate(self.placement.insertions[1:])
                ),
            ),
            tuple(self.detached),
        )
        return RustDocumentation(sections, owners, placement, tuple(self.warnings))

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
        """Whether a comment before the run ends on the run's first line."""
        return index > 0 and self._line(
            self.runs[index - 1].span.end - 1
        ) == self._line(run.span.start)

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
            alone = not run.trailing and not self._beside(index, run)
            if nearest and above and alone:
                self._attach(index, run, owner)
            else:
                self._detach(index, run, owner)
            return
        owner = bisect_right(self.heads, start) - 1
        if owner >= 0 and start <= self.bodies[owner]:
            self._detach(index, run, owner)
            return
        self.forms[index] = RustSectionForm.COMMENT

    def _inner(self, index: int, run: _Run) -> None:
        """Attach a run to the module or to the owner whose body it opens."""
        before = bisect_left(self.starts, run.span.start) - 1
        # Code before the run -- an inner attribute -- keeps it from `a0`,
        # which the page sets at the file head.
        preceded = before >= 0
        while before >= 0 and self.code[before].kind is RustTokenKind.INNER_ATTRIBUTE:
            before -= 1
        if before < 0:
            # A comment before the run that is not opening matter -- below a
            # blank line, or one a run that opens the file runs on to -- or
            # one ending on the run's first line detaches it.
            end = self.opening_end or 0
            behind = any(
                not r.code and self._line(r.span.end - 1) > end
                for r in self.runs[:index]
            )
            if MODULE not in self.owner_kinds:
                self.forms[index] = RustSectionForm.COMMENT
            elif preceded or behind or self._beside(index, run):
                self._detach(index, run, None)
            else:
                self._attach(index, run, None)
            return
        owner = self._opened_by(before)
        if owner is None:
            self.forms[index] = RustSectionForm.COMMENT
            return
        # The run documents the owner only when it opens the body: nothing but
        # whitespace between the body's opening delimiter and the run, and the
        # run on a line of its own. Behind another comment, or on the head's
        # line, it is detached.
        behind = (
            index > 0 and self.runs[index - 1].span.start > self.code[before].span.start
        )
        if run.trailing or behind:
            self._detach(index, run, owner)
        else:
            self._attach(index, run, owner)

    def _attach(self, index: int, run: _Run, owner: int | None) -> None:
        if owner in self.links.values():
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
                DETACHED_DOCUMENTATION,
                f"documentation on line {self._line(run.span.start)} "
                f"is detached from {named}",
                run.span,
            )
        )

    def _opened_by(self, at: int) -> int | None:
        """The owner whose body the delimiter `self.code[at]` opens, or None.

        An item's body is the first `body_open` outside any other delimiter
        after its keyword, unless a terminator ends the item first.
        """
        opener = self.code[at]
        if opener.kind is not RustTokenKind.OPEN or self._spelled(opener) != (
            self.body_open
        ):
            return None
        owner = bisect_left(self.heads, opener.span.start) - 1
        if owner < 0:
            return None
        depth = 0
        for index in range(bisect_left(self.starts, self.bodies[owner]), at + 1):
            token = self.code[index]
            spelling = self._spelled(token)
            if token.kind is RustTokenKind.OPEN:
                if not depth and spelling == self.body_open:
                    return owner if index == at else None
                depth += 1
            elif token.kind is RustTokenKind.CLOSE:
                depth -= 1
                if depth < 0:
                    return None
            elif not depth and spelling == self.terminator:
                return None
        return None

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
            t
            for t in tokens[at + 1 :]
            if t.kind is not RustTokenKind.WHITESPACE and t.kind not in COMMENT_KINDS
        ),
        None,
    )
    return (
        following is not None
        and coordinates.position(following.span.start).line == end_line
    )
