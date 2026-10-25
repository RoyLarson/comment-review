"""Partition Rust source into comment, code and whitespace regions and their tokens."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import cast

from comment_review import constants
from comment_review.reading.comment import CommentSpan
from comment_review.reading.definitions import LanguageDefinition
from comment_review.reading.diagnostics import ReadDiagnostic, ReadFailure, ReadStage
from comment_review.reading.rust.definition import validate_rust
from comment_review.reading.rust.records import (
    COMMENT_KINDS,
    RustScan,
    RustToken,
    RustTokenKind,
)
from comment_review.reading.source import RegionKind, SourceRegion, SourceSpan

BYTE_ORDER_MARK = "\ufeff"
# The Rust Reference's whitespace: Pattern_White_Space.
WHITESPACE = frozenset("\t\n\v\f\r \x85\u200e\u200f\u2028\u2029")
OPENERS = frozenset("{([")
CLOSERS = frozenset("})]")
# The Rust Reference's CHAR_LITERAL excludes these from an unescaped body.
NOT_A_CHAR_BODY = frozenset("\n\r\t")
# Whitespace that stays on its line.
INDENT = WHITESPACE - frozenset("\r\n")
DECORATED_KINDS = frozenset(
    {RustTokenKind.OUTER_DOC_DELIMITED, RustTokenKind.INNER_DOC_DELIMITED}
)


@dataclass(frozen=True)
class _Comments:
    line: str
    outer_line: str
    inner_line: str
    opener: str
    closer: str
    outer_delimited: str
    inner_delimited: str
    empty: str
    # What may open a continuation line of a delimited doc, after its indent.
    decoration: str

    @classmethod
    def from_definition(cls, definition: LanguageDefinition) -> "_Comments":
        comments = cast(Mapping[str, object], definition.rules["comments"])
        documentation = cast(Mapping[str, object], definition.rules["documentation"])
        opener, closer = cast(tuple[str, str], comments["block_comment"])
        return cls(
            cast(str, comments["line"]),
            cast(str, comments["outer_doc_line"]),
            cast(str, comments["inner_doc_line"]),
            opener,
            closer,
            cast(str, comments["outer_doc_block"]),
            cast(str, comments["inner_doc_block"]),
            cast(str, comments["empty_block_comment"]),
            cast(str, documentation["delimited_decoration"]),
        )

    def markers(self, kind: RustTokenKind) -> tuple[str, str]:
        """The opening and closing markers a comment of `kind` is written with."""
        return {
            RustTokenKind.LINE: (self.line, ""),
            RustTokenKind.OUTER_DOC_LINE: (self.outer_line, ""),
            RustTokenKind.INNER_DOC_LINE: (self.inner_line, ""),
            RustTokenKind.DELIMITED_COMMENT: (self.opener, self.closer),
            RustTokenKind.OUTER_DOC_DELIMITED: (self.outer_delimited, self.closer),
            RustTokenKind.INNER_DOC_DELIMITED: (self.inner_delimited, self.closer),
        }[kind]


@dataclass(frozen=True)
class _Literals:
    string_quote: str
    raw_guard: str
    char_quote: str
    escape: str
    raw_lifetime: str
    raw_identifier: str
    # (prefix, kind) longest prefix first, so `br` is tried before `b`.
    prefixes: tuple[tuple[str, RustTokenKind], ...]

    @classmethod
    def from_definition(cls, definition: LanguageDefinition) -> "_Literals":
        literals = cast(Mapping[str, object], definition.rules["literals"])
        prefixes = [
            (prefix, kind)
            for key, kind in (
                ("raw_prefixes", RustTokenKind.RAW_STRING),
                ("string_prefixes", RustTokenKind.STRING),
                ("char_prefixes", RustTokenKind.CHAR),
            )
            for prefix in cast(tuple[str, ...], literals[key])
        ]
        prefixes.sort(key=lambda entry: -len(entry[0]))
        return cls(
            cast(str, literals["string_quote"]),
            cast(str, literals["raw_guard"]),
            cast(str, literals["char_quote"]),
            cast(str, literals["escape_marker"]),
            cast(str, literals["raw_lifetime_prefix"]),
            cast(str, literals["raw_identifier_prefix"]),
            tuple(prefixes),
        )


@dataclass(frozen=True)
class _Attributes:
    outer: str
    inner: str
    # The bracket that opens an attribute's body and nests inside it.
    open: str
    close: str

    @classmethod
    def from_definition(cls, definition: LanguageDefinition) -> "_Attributes":
        attributes = cast(Mapping[str, object], definition.rules["attributes"])
        return cls(
            cast(str, attributes["outer_open"]),
            cast(str, attributes["inner_open"]),
            cast(str, attributes["open"]),
            cast(str, attributes["close"]),
        )


@dataclass(frozen=True)
class _Directives:
    shebang: str
    line: int
    # What, after the shebang marker, makes the line an inner attribute instead.
    attribute_follows: str

    @classmethod
    def from_definition(cls, definition: LanguageDefinition) -> "_Directives":
        directives = cast(Mapping[str, object], definition.rules["directives"])
        return cls(
            cast(str, directives["shebang"]),
            cast(int, directives["shebang_line"]),
            cast(str, directives["inner_attribute_follows"]),
        )


@dataclass(frozen=True)
class _Grammar:
    comments: _Comments
    literals: _Literals
    attributes: _Attributes
    directives: _Directives


def scan_rust(text: str, definition: LanguageDefinition) -> RustScan | ReadFailure:
    """Partition Rust source, failing at NUL or at anything left unterminated.

    What can be left unterminated is a delimited comment, a string, a raw
    string, a character literal or an attribute.

    Adjacent code tokens share one CODE region, adjacent whitespace one
    WHITESPACE region and adjacent literals one LITERAL region; every comment
    is its own COMMENT region. A lifetime is code.

    Rust's grammar fixes two comment rules: a delimited comment nests, closing
    only when every opener inside it has closed, and an outer doc marker whose
    last character repeats (`////`, `/***`) opens an ordinary comment.

    An attribute is one token from its opener to the close that matches it,
    emitted ahead of the tokens inside it, which are read as anywhere else.

    A shebang is one token and one DIRECTIVE region running from its marker
    to the end of its line; see `_shebang` for when the marker opens one.
    """
    failure = validate_rust(definition)
    if failure is not None:
        return failure
    nul = text.find("\x00")
    if nul >= 0:
        return _failure("source-nul", nul, nul + 1)
    grammar = _Grammar(
        _Comments.from_definition(definition),
        _Literals.from_definition(definition),
        _Attributes.from_definition(definition),
        _Directives.from_definition(definition),
    )
    regions: list[SourceRegion] = []
    tokens: list[RustToken] = []
    start = 0
    while start < len(text):
        shebang = _shebang(text, start, grammar)
        if shebang is not None:
            result = RustTokenKind.SHEBANG, shebang, RegionKind.DIRECTIVE
        else:
            attribute = _attribute(text, start, grammar)
            if isinstance(attribute, ReadFailure):
                return attribute
            if attribute is not None:
                tokens.append(attribute)
            result = _next_token(text, start, grammar)
        if isinstance(result, ReadFailure):
            return result
        kind, end, region_kind = result
        span = SourceSpan(start, end)
        if kind is not None:
            tokens.append(RustToken(kind, span))
        if (
            regions
            and regions[-1].kind is region_kind
            and region_kind is not RegionKind.COMMENT
        ):
            regions[-1] = SourceRegion(
                SourceSpan(regions[-1].span.start, end), region_kind
            )
        else:
            regions.append(SourceRegion(span, region_kind))
        start = end
    prose = tuple(
        _prose(text, token, grammar.comments)
        for token in tokens
        if token.kind in COMMENT_KINDS
    )
    return RustScan(text, tuple(regions), tuple(tokens), prose)


def comments_in(
    text: str, definition: LanguageDefinition
) -> tuple[CommentSpan, ...] | None:
    """Each comment in `text` and the markers it is written with.

    None where `text` does not scan, or holds anything but comments and
    whitespace.
    """
    scan = scan_rust(text, definition)
    if isinstance(scan, ReadFailure):
        return None
    comments = _Comments.from_definition(definition)
    found = []
    for token in scan.tokens:
        if token.kind is RustTokenKind.WHITESPACE:
            continue
        if token.kind not in COMMENT_KINDS:
            return None
        opener, closer = comments.markers(token.kind)
        found.append(CommentSpan(token.span.start, token.span.end, opener, closer))
    return tuple(found)


def _prose(text: str, token: RustToken, comments: _Comments) -> tuple[SourceSpan, ...]:
    """The comment's text inside its markers, one piece per physical line.

    A delimited doc's continuation lines are decorated when every one of them
    opens, after an indent of one width, with the decoration character; a
    last line that holds only indent, before the closer, is not asked. When
    they are, each one's indent and decoration are not prose; otherwise all
    of it is.
    """
    opener, closer = comments.markers(token.kind)
    body = SourceSpan(token.span.start + len(opener), token.span.end - len(closer))
    if token.kind not in DECORATED_KINDS:
        return (body,)
    lines = []
    start = body.start
    for line_break in constants.LINE_BREAK.finditer(text, body.start, body.end):
        lines.append(SourceSpan(start, line_break.start()))
        start = line_break.end()
    lines.append(SourceSpan(start, body.end))
    stripped = [_undecorated(text, line, comments.decoration) for line in lines[1:]]
    asked = list(zip(lines[1:], stripped, strict=True))
    if len(lines) > 1 and all(text[i] in INDENT for i in range(start, body.end)):
        asked = asked[:-1]
    if (
        not asked
        or any(cut is None for _, cut in asked)
        or len({cut.start - line.start for line, cut in asked if cut}) != 1
    ):
        return tuple(lines)
    return (
        lines[0],
        *(
            line if cut is None else cut
            for line, cut in zip(lines[1:], stripped, strict=True)
        ),
    )


def _undecorated(text: str, line: SourceSpan, decoration: str) -> SourceSpan | None:
    """The line past its indent and decoration, or None where it has none."""
    at = line.start
    while at < line.end and text[at] in INDENT:
        at += 1
    end = at + len(decoration)
    if end <= line.end and text.startswith(decoration, at):
        return SourceSpan(end, line.end)
    return None


def _shebang(text: str, start: int, grammar: _Grammar) -> int | None:
    """Where a shebang opening at `start` ends, or None where none opens.

    A shebang opens at the start of its line, after a byte-order mark on the
    first line, unless the first token after its marker that is neither
    whitespace nor a comment begins with the attribute bracket: then the
    marker opens an inner attribute, which is code.
    """
    directives = grammar.directives
    line_start = 0
    for _ in range(directives.line - 1):
        newline = text.find("\n", line_start)
        if newline < 0:
            return None
        line_start = newline + 1
    if line_start == 0 and text.startswith(BYTE_ORDER_MARK):
        line_start = len(BYTE_ORDER_MARK)
    if start != line_start or not text.startswith(directives.shebang, start):
        return None
    at = start + len(directives.shebang)
    while at < len(text):
        result = _next_token(text, at, grammar)
        if isinstance(result, ReadFailure):
            break
        kind, end, _ = result
        if kind is not RustTokenKind.WHITESPACE and kind not in COMMENT_KINDS:
            if text.startswith(directives.attribute_follows, at):
                return None
            break
        at = end
    return _line_end(text, start)


def _attribute(
    text: str, start: int, grammar: _Grammar
) -> RustToken | ReadFailure | None:
    """The attribute opening at `start`, spanning to the close that matches it.

    Its opener's characters are tokens of their own, so whitespace and
    comments may stand between them: `# [derive(Debug)]` is an attribute.
    """
    attributes = grammar.attributes
    if (opened := _opens(text, start, attributes.inner, grammar)) is not None:
        kind = RustTokenKind.INNER_ATTRIBUTE
    elif (opened := _opens(text, start, attributes.outer, grammar)) is not None:
        kind = RustTokenKind.OUTER_ATTRIBUTE
    else:
        return None
    depth = 0
    at = start
    while at < len(text):
        result = _next_token(text, at, grammar)
        if isinstance(result, ReadFailure):
            return result
        token_kind, end, _ = result
        if token_kind is RustTokenKind.OPEN and text[at:end] == attributes.open:
            depth += 1
        elif token_kind is RustTokenKind.CLOSE and text[at:end] == attributes.close:
            depth -= 1
            if depth == 0:
                return RustToken(kind, SourceSpan(start, end))
        at = end
    return _failure("unterminated-attribute", start, opened)


def _opens(text: str, start: int, opener: str, grammar: _Grammar) -> int | None:
    """Where `opener` ends when it opens at `start`, or None where it does not.

    Each of its characters may follow the one before it past whitespace and
    comments.
    """
    at = start
    for index, char in enumerate(opener):
        while index and at < len(text):
            result = _next_token(text, at, grammar)
            if isinstance(result, ReadFailure):
                break
            kind, end, _ = result
            if kind is not RustTokenKind.WHITESPACE and kind not in COMMENT_KINDS:
                break
            at = end
        if not text.startswith(char, at):
            return None
        at += len(char)
    return at


def _next_token(
    text: str, start: int, grammar: _Grammar
) -> tuple[RustTokenKind | None, int, RegionKind] | ReadFailure:
    """The token at `start`: its kind (None for a byte-order mark), end and region."""
    comments = grammar.comments
    char = text[start]
    if start == 0 and char == BYTE_ORDER_MARK:
        return None, 1, RegionKind.WHITESPACE
    if char in WHITESPACE:
        end = start + 1
        while end < len(text) and text[end] in WHITESPACE:
            end += 1
        return RustTokenKind.WHITESPACE, end, RegionKind.WHITESPACE
    if text.startswith(comments.opener, start):
        return _delimited(text, start, comments)
    if text.startswith(comments.line, start):
        return _line(text, start, comments), _line_end(text, start), RegionKind.COMMENT
    # Ahead of the code tokens, which would otherwise split a literal.
    literal = _literal(text, start, grammar.literals)
    if literal is not None:
        return literal
    if char in OPENERS:
        return RustTokenKind.OPEN, start + 1, RegionKind.CODE
    if char in CLOSERS:
        return RustTokenKind.CLOSE, start + 1, RegionKind.CODE
    if char.isidentifier():
        return RustTokenKind.WORD, _identifier_end(text, start), RegionKind.CODE
    return RustTokenKind.PUNCT, start + 1, RegionKind.CODE


def _identifier_end(text: str, start: int) -> int:
    end = start + 1
    while end < len(text) and _continues_identifier(text[end]):
        end += 1
    return end


def _continues_identifier(char: str) -> bool:
    return f"_{char}".isidentifier()


def _literal(
    text: str, start: int, literals: _Literals
) -> tuple[RustTokenKind, int, RegionKind] | ReadFailure | None:
    """A literal, lifetime or raw identifier at `start`, or None for anything else.

    A prefix opens a literal only where the character before it cannot
    continue an identifier, so the `r` ending `bar` never opens a raw string.
    """
    if text.startswith(literals.string_quote, start):
        return _string(text, start, start + len(literals.string_quote), literals)
    if text.startswith(literals.char_quote, start):
        return _char_or_lifetime(
            text, start, start + len(literals.char_quote), literals
        )
    if start > 0 and _continues_identifier(text[start - 1]):
        return None
    for prefix, kind in literals.prefixes:
        if not text.startswith(prefix, start):
            continue
        after = start + len(prefix)
        if kind is RustTokenKind.RAW_STRING:
            raw = _raw_string(text, start, after, literals)
            if raw is not None:
                return raw
        elif kind is RustTokenKind.STRING:
            if text.startswith(literals.string_quote, after):
                body = after + len(literals.string_quote)
                return _string(text, start, body, literals)
        elif text.startswith(literals.char_quote, after):
            body = after + len(literals.char_quote)
            char = _char(text, body, literals)
            if char is None:
                return _failure("unterminated-char", start, body)
            return RustTokenKind.CHAR, char, RegionKind.LITERAL
    name = _past_prefix(text, start, literals.raw_identifier)
    if name > start:
        return RustTokenKind.WORD, _identifier_end(text, name), RegionKind.CODE
    return None


def _string(
    text: str, start: int, body: int, literals: _Literals
) -> tuple[RustTokenKind, int, RegionKind] | ReadFailure:
    """A string whose body begins at `body`; an escape takes the next character."""
    at = body
    while at < len(text):
        if text.startswith(literals.escape, at):
            at += len(literals.escape) + 1
        elif text.startswith(literals.string_quote, at):
            end = at + len(literals.string_quote)
            return RustTokenKind.STRING, end, RegionKind.LITERAL
        else:
            at += 1
    return _failure("unterminated-string", start, body)


def _raw_string(
    text: str, start: int, after: int, literals: _Literals
) -> tuple[RustTokenKind, int, RegionKind] | ReadFailure | None:
    """A raw string after its prefix, or None where no quote follows the guards.

    It closes only at a quote followed by as many guards as opened it.
    """
    quote = after
    while text.startswith(literals.raw_guard, quote):
        quote += len(literals.raw_guard)
    if not text.startswith(literals.string_quote, quote):
        return None
    closer = literals.string_quote + text[after:quote]
    body = quote + len(literals.string_quote)
    end = text.find(closer, body)
    if end < 0:
        return _failure("unterminated-raw-string", start, body)
    return RustTokenKind.RAW_STRING, end + len(closer), RegionKind.LITERAL


def _char_or_lifetime(
    text: str, start: int, body: int, literals: _Literals
) -> tuple[RustTokenKind, int, RegionKind] | ReadFailure:
    """A character, a lifetime, or a failure at the quote that opens neither.

    A valid character body and a closing quote make a character; otherwise an
    identifier after the quote makes a lifetime.
    """
    end = _char(text, body, literals)
    if end is not None:
        return RustTokenKind.CHAR, end, RegionKind.LITERAL
    name = _past_prefix(text, body, literals.raw_lifetime)
    if name < len(text) and text[name].isidentifier():
        return RustTokenKind.LIFETIME, _identifier_end(text, name), RegionKind.CODE
    return _failure("unterminated-char", start, body)


def _past_prefix(text: str, at: int, prefix: str) -> int:
    """Past `prefix` at `at` if an identifier follows it, else `at`."""
    name = at + len(prefix)
    if text.startswith(prefix, at) and name < len(text) and text[name].isidentifier():
        return name
    return at


def _char(text: str, body: int, literals: _Literals) -> int | None:
    """Where a character literal whose body begins at `body` ends, or None.

    An escape takes the character after it and runs to the closing quote on
    the same line, which covers the hex and unicode escape forms.
    """
    if text.startswith(literals.escape, body):
        at = body + len(literals.escape) + 1
        close = text.find(literals.char_quote, at)
        if close < 0 or any(char in NOT_A_CHAR_BODY for char in text[body:close]):
            return None
        return close + len(literals.char_quote)
    if body >= len(text) or text[body] in NOT_A_CHAR_BODY:
        return None
    if text.startswith(literals.char_quote, body):
        return None
    if text.startswith(literals.char_quote, body + 1):
        return body + 1 + len(literals.char_quote)
    return None


def _line(text: str, start: int, comments: _Comments) -> RustTokenKind:
    if text.startswith(comments.inner_line, start):
        return RustTokenKind.INNER_DOC_LINE
    if text.startswith(comments.outer_line, start) and not _repeated(
        text, start, comments.outer_line
    ):
        return RustTokenKind.OUTER_DOC_LINE
    return RustTokenKind.LINE


def _line_end(text: str, start: int) -> int:
    """Where a line comment ends: before its LF or CRLF, or at end of text."""
    end = text.find("\n", start)
    if end < 0:
        return len(text)
    return end - 1 if text[end - 1] == "\r" else end


def _delimited(
    text: str, start: int, comments: _Comments
) -> tuple[RustTokenKind, int, RegionKind] | ReadFailure:
    """Read a delimited comment to the close of its outermost layer."""
    depth = 1
    end = start + len(comments.opener)
    while end < len(text):
        if text.startswith(comments.opener, end):
            depth += 1
            end += len(comments.opener)
        elif text.startswith(comments.closer, end):
            depth -= 1
            end += len(comments.closer)
            if depth == 0:
                return _delimited_kind(text, start, comments), end, RegionKind.COMMENT
        else:
            end += 1
    return _failure("unterminated-comment", start, start + len(comments.opener))


def _delimited_kind(text: str, start: int, comments: _Comments) -> RustTokenKind:
    if text.startswith(comments.empty, start):
        return RustTokenKind.DELIMITED_COMMENT
    if text.startswith(comments.inner_delimited, start):
        return RustTokenKind.INNER_DOC_DELIMITED
    if text.startswith(comments.outer_delimited, start) and not _repeated(
        text, start, comments.outer_delimited
    ):
        return RustTokenKind.OUTER_DOC_DELIMITED
    return RustTokenKind.DELIMITED_COMMENT


def _repeated(text: str, start: int, marker: str) -> bool:
    """Whether an outer doc marker's last character repeats right after it."""
    return text.startswith(marker[-1], start + len(marker))


def _failure(code: str, start: int, end: int) -> ReadFailure:
    return ReadFailure(
        (
            ReadDiagnostic(
                ReadStage.LEX, code, code.replace("-", " "), SourceSpan(start, end)
            ),
        )
    )
