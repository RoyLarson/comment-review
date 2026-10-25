"""Find Rust's documentation owners and the line each owner's head starts on."""

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from typing import cast

from comment_review.reading.coordinates import SourceCoordinates
from comment_review.reading.definitions import LanguageDefinition
from comment_review.reading.diagnostics import ReadDiagnostic, ReadFailure, ReadStage
from comment_review.reading.rust.definition import (
    ASSOCIATED_ITEM,
    FIELD,
    ITEM,
    NESTED_ITEM,
    VARIANT,
    validate_rust,
)
from comment_review.reading.rust.records import (
    SEVERAL_DECLARATIONS_CODE,
    RustPlacement,
    RustScan,
    RustToken,
    RustTokenKind,
    significant_tokens,
)
from comment_review.reading.source import SourceDeclaration, SourceSpan

ABI_KINDS = frozenset({RustTokenKind.STRING, RustTokenKind.RAW_STRING})


class _Body(Enum):
    """What an open delimiter holds, and so which owners can begin inside it."""

    CONTAINER = "container"
    FUNCTION = "function"
    MEMBERS = "members"
    VARIANTS = "variants"
    OPAQUE = "opaque"


STATEMENT_BODIES = frozenset({_Body.CONTAINER, _Body.FUNCTION})
MEMBER_BODIES = frozenset({_Body.MEMBERS, _Body.VARIANTS})


@dataclass(frozen=True)
class _Grammar:
    visibility: str
    scopes: frozenset[str]
    qualifiers: tuple[str, ...]
    # Each keyword with the token spellings it is written as: `macro_rules!`
    # is the word `macro_rules` then the punctuation `!`.
    keywords: tuple[tuple[str, tuple[str, ...]], ...]
    contextual: frozenset[str]
    containers: frozenset[str]
    associated: frozenset[str]
    members: frozenset[str]
    variants: frozenset[str]
    functions: frozenset[str]
    macros: frozenset[str]
    abi: str
    macro_marker: str
    body_open: str
    generics_open: str
    generics_close: str
    arrow: str
    terminator: str
    separator: str
    assignment: str
    # The owner kinds that take documentation.
    owners: frozenset[str]

    @classmethod
    def from_definition(cls, definition: LanguageDefinition) -> "_Grammar":
        rules = cast(Mapping[str, object], definition.rules["declarations"])
        documentation = cast(Mapping[str, object], definition.rules["documentation"])

        def words(key: str) -> tuple[str, ...]:
            return cast(tuple[str, ...], rules[key])

        return cls(
            cast(str, rules["visibility"]),
            frozenset(words("visibility_scopes")),
            words("qualifiers"),
            tuple((keyword, _pieces(keyword)) for keyword in words("keywords")),
            frozenset(words("contextual")),
            frozenset(words("item_containers")),
            frozenset(words("associated_containers")),
            frozenset(words("member_lists")),
            frozenset(words("variant_lists")),
            frozenset(words("function_bodies")),
            frozenset(words("macro_definitions")),
            cast(str, rules["abi_qualifier"]),
            cast(str, rules["macro_marker"]),
            cast(str, rules["body_open"]),
            cast(str, rules["generics_open"]),
            cast(str, rules["generics_close"]),
            cast(str, rules["arrow"]),
            cast(str, rules["terminator"]),
            cast(str, rules["separator"]),
            cast(str, rules["assignment"]),
            frozenset(cast(tuple[str, ...], documentation["owners"])),
        )


def _pieces(spelling: str) -> tuple[str, ...]:
    """Split a keyword into the identifier and punctuation tokens that spell it."""
    pieces: list[str] = []
    at = 0
    while at < len(spelling):
        end = at + 1
        if spelling[at].isidentifier():
            while end < len(spelling) and f"_{spelling[end]}".isidentifier():
                end += 1
        pieces.append(spelling[at:end])
        at = end
    return tuple(pieces)


@dataclass
class _Frame:
    """An open delimiter: what it holds and whether an owner may begin next."""

    body: _Body
    owner: str
    opener: str
    start: bool
    # The index of the current member's first token, in a member or variant list.
    member: int = -1
    # How many generic argument lists are open in the current member or item head.
    generics: int = 0
    # Whether the current member's own `=` was read: in its discriminant or
    # default value, `<` and `>` are operators and open no argument list.
    value: bool = False


@dataclass(frozen=True)
class _Pending:
    """An item whose keyword was read and whose body has not opened yet."""

    keyword: str
    depth: int
    name: int


def place_declarations(
    scan: RustScan, definition: LanguageDefinition
) -> RustPlacement | ReadFailure:
    """Give every documentation owner one declaration, in source order.

    An owner's head is its outer attributes, then the token it opens on: the
    first of its visibility, qualifiers and keyword, or a member's first token.
    The header runs from the head's first character to the end of the last code
    token that starts on the keyword's or member's line, and the anchor is the
    head's first character. An owner gets a declaration only when its kind is
    in `[rules.documentation].owners` and its head is the first code on its
    line: the code before it ends on an earlier line. An owner on a line a
    declaration already holds gets none, and that line gets one warning.

    `detached` is empty, and documentation fills it.
    """
    failure = validate_rust(definition)
    if failure is not None:
        return failure
    placer = _Placer(scan, _Grammar.from_definition(definition))
    placer.run()
    return RustPlacement(tuple(placer.declarations), (), tuple(placer.warnings))


class _Placer:
    """One pass over the scan's code tokens with a stack of open bodies."""

    def __init__(self, scan: RustScan, grammar: _Grammar) -> None:
        self.text = scan.text
        self.grammar = grammar
        self.tokens = significant_tokens(scan.tokens)
        self.spelling = [
            scan.text[token.span.start : token.span.end] for token in self.tokens
        ]
        self.coordinates = SourceCoordinates(scan.text)
        self.lines = [self._line(t.span.start) for t in self.tokens]
        self.closes = _closes(self.tokens)
        self.stack = [_Frame(_Body.CONTAINER, ITEM, "", True)]
        self.pending: _Pending | None = None
        self.attributes: list[int] = []
        self.declarations: list[SourceDeclaration] = []
        self.warnings: list[ReadDiagnostic] = []
        # Lines already warned of, so a line holding several items warns once.
        self.crowded: set[int] = set()

    def run(self) -> None:
        at = 0
        while at < len(self.tokens):
            at = self._step(at)

    def _step(self, at: int) -> int:
        token = self.tokens[at]
        frame = self.stack[-1]
        if token.kind is RustTokenKind.CLOSE:
            self._close()
            return at + 1
        if token.kind is RustTokenKind.OUTER_ATTRIBUTE:
            if frame.start:
                self.attributes.append(at)
            return at + 1
        if token.kind is RustTokenKind.INNER_ATTRIBUTE:
            return at + 1
        if frame.start:
            frame.start = False
            if frame.body in STATEMENT_BODIES:
                item = self._item(at)
                if item is not None:
                    keyword, keyword_at, after = item
                    self._own(frame.owner, at, keyword_at)
                    self.pending = _Pending(keyword, len(self.stack), after)
                    return after
            else:
                frame.member = at
                self._own(frame.owner, at, at)
            self.attributes.clear()
        spelling = self.spelling[at]
        if token.kind is RustTokenKind.OPEN:
            self.stack.append(self._open(at, frame))
        elif spelling == self.grammar.terminator and frame.body in STATEMENT_BODIES:
            frame.start = True
            frame.generics = 0
            if self._heading():
                self.pending = None
        elif (
            spelling == self.grammar.separator
            and frame.body in MEMBER_BODIES
            and not frame.generics
        ):
            frame.start = True
            frame.value = False
        elif frame.body in MEMBER_BODIES:
            if spelling == self.grammar.assignment and not frame.generics:
                frame.value = True
            elif not frame.value:
                self._generics(at, frame)
        elif self._heading():
            self._generics(at, frame)
        return at + 1

    def _heading(self) -> bool:
        """Whether an item's head is being read in the innermost body."""
        return self.pending is not None and self.pending.depth == len(self.stack)

    def _generics(self, at: int, frame: _Frame) -> None:
        """Count generic argument lists; the `>` that ends an arrow closes none."""
        grammar = self.grammar
        spelling = self.spelling[at]
        if spelling == grammar.generics_open:
            frame.generics += 1
        elif spelling == grammar.generics_close and frame.generics:
            previous = self.tokens[at - 1]
            arrow = (
                previous.span.end == self.tokens[at].span.start
                and self.spelling[at - 1] + spelling == grammar.arrow
            )
            if not arrow:
                frame.generics -= 1

    def _close(self) -> None:
        """Pop a body; after a closing brace a new statement may begin."""
        self.attributes.clear()
        if len(self.stack) == 1:
            return
        closed = self.stack.pop()
        if self.pending is not None and len(self.stack) < self.pending.depth:
            self.pending = None
        top = self.stack[-1]
        if (
            closed.opener == self.grammar.body_open
            and top.body in STATEMENT_BODIES
            and not self._heading()
        ):
            top.start = True

    def _open(self, at: int, frame: _Frame) -> _Frame:
        """The body a delimiter opens, read from the item it belongs to."""
        grammar = self.grammar
        spelling = self.spelling[at]
        if frame.body is _Body.OPAQUE:
            return _Frame(_Body.OPAQUE, "", spelling, False)
        if frame.generics:
            # Braces in generic arguments hold a constant expression.
            return _Frame(_Body.OPAQUE, "", spelling, False)
        pending = self.pending
        if pending is not None and pending.depth == len(self.stack):
            keyword = pending.keyword
            if keyword in grammar.macros:
                self.pending = None
                return _Frame(_Body.OPAQUE, "", spelling, False)
            if spelling == grammar.body_open:
                self.pending = None
                if keyword in grammar.containers:
                    owner = ASSOCIATED_ITEM if keyword in grammar.associated else ITEM
                    return _Frame(_Body.CONTAINER, owner, spelling, True)
                if keyword in grammar.members:
                    return _Frame(_Body.MEMBERS, FIELD, spelling, True)
                if keyword in grammar.variants:
                    return _Frame(_Body.VARIANTS, VARIANT, spelling, True)
                if keyword in grammar.functions:
                    return _Frame(_Body.FUNCTION, NESTED_ITEM, spelling, True)
            elif keyword in grammar.members and (
                at - 1 == pending.name
                or self.spelling[at - 1] == grammar.generics_close
            ):
                # A tuple struct's fields open right after its name or generics.
                self.pending = None
                return _Frame(_Body.MEMBERS, FIELD, spelling, True)
        if self._invocation(at):
            return _Frame(_Body.OPAQUE, "", spelling, False)
        if spelling == grammar.body_open:
            if frame.body is _Body.VARIANTS and frame.member == at - 1:
                return _Frame(_Body.MEMBERS, FIELD, spelling, True)
            if frame.body in STATEMENT_BODIES:
                return _Frame(_Body.FUNCTION, NESTED_ITEM, spelling, True)
        return _Frame(_Body.OPAQUE, "", spelling, False)

    def _invocation(self, at: int) -> bool:
        """Whether the delimiter at `at` follows `name!`, a macro invocation."""
        return (
            at >= 2
            and self.spelling[at - 1] == self.grammar.macro_marker
            and self.tokens[at - 2].kind is RustTokenKind.WORD
        )

    def _item(self, at: int) -> tuple[str, int, int] | None:
        """The item opening at `at`: its keyword, where it is, and the token after."""
        if self._spelled(at) == self.grammar.visibility:
            at += 1
            if (
                at < len(self.tokens)
                and self.tokens[at].kind is RustTokenKind.OPEN
                and self._spelled(at + 1) in self.grammar.scopes
                and at in self.closes
            ):
                at = self.closes[at] + 1
        return self._qualified(at, -1)

    def _qualified(self, at: int, rank: int) -> tuple[str, int, int] | None:
        """Read qualifiers in definition order; one counts only if an item follows.

        So `const fn` is a function and `const X` is a constant.
        """
        grammar = self.grammar
        word = self._spelled(at)
        if word in grammar.qualifiers and grammar.qualifiers.index(word) > rank:
            after = at + 1
            if (
                word == grammar.abi
                and after < len(self.tokens)
                and self.tokens[after].kind in ABI_KINDS
            ):
                after += 1
            item = self._qualified(after, grammar.qualifiers.index(word))
            if item is not None:
                return item
        return self._keyword(at)

    def _keyword(self, at: int) -> tuple[str, int, int] | None:
        grammar = self.grammar
        for keyword, pieces in grammar.keywords:
            after = at + len(pieces)
            if any(self._spelled(at + i) != piece for i, piece in enumerate(pieces)):
                continue
            following = self.tokens[after] if after < len(self.tokens) else None
            if keyword in grammar.contextual and (
                following is None or following.kind is not RustTokenKind.WORD
            ):
                continue
            # `const { ... }` is an inline constant expression; `extern { ... }`
            # is an item.
            if (
                keyword in grammar.qualifiers
                and keyword not in grammar.containers
                and self._spelled(after) == grammar.body_open
            ):
                continue
            return keyword, at, after
        return None

    def _own(self, owner: str, first: int, line_token: int) -> None:
        """Record an owner whose kind takes documentation and whose head leads its line.

        The code before the head is measured at its last character, so a
        literal spanning lines ends on the line it closes on.
        """
        head = self.attributes[0] if self.attributes else first
        self.attributes.clear()
        if owner not in self.grammar.owners:
            return
        head_line = self.lines[head]
        if head > 0 and self._line(self.tokens[head - 1].span.end - 1) == head_line:
            self._several(head)
            return
        start = self.tokens[head].span.start
        line = self.lines[line_token]
        end = line_token
        while end + 1 < len(self.tokens) and self.lines[end + 1] == line:
            end += 1
        header = SourceSpan(start, self.tokens[end].span.end)
        self.declarations.append(SourceDeclaration(header, start, owner))

    def _several(self, head: int) -> None:
        """Warn, once per line, of an owner on a line a declaration already holds."""
        line = self.lines[head]
        if not self.declarations or line in self.crowded:
            return
        # A declaration's header ends on the line its keyword or member is on.
        if self._line(self.declarations[-1].header.end - 1) != line:
            return
        self.crowded.add(line)
        self.warnings.append(
            ReadDiagnostic(
                ReadStage.PLACE,
                SEVERAL_DECLARATIONS_CODE,
                f"line {line} declares several items; the first takes its"
                " documentation",
                self.tokens[head].span,
            )
        )

    def _line(self, offset: int) -> int:
        return self.coordinates.position(offset).line

    def _spelled(self, at: int) -> str | None:
        return self.spelling[at] if at < len(self.tokens) else None


def _closes(tokens: list[RustToken]) -> dict[int, int]:
    """Each opening delimiter's index mapped to the index that closes it."""
    closes: dict[int, int] = {}
    opened: list[int] = []
    for at, token in enumerate(tokens):
        if token.kind is RustTokenKind.OPEN:
            opened.append(at)
        elif token.kind is RustTokenKind.CLOSE and opened:
            closes[opened.pop()] = at
    return closes
