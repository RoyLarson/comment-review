"""Read concatenated Python docstring prose with its literal boundaries."""

import ast
import io
import re
import tokenize
from dataclasses import dataclass

from comment_review.reading.comment import Comment, Fragment

_OPEN = re.compile(r"(?i)([ru]*)(\"\"\"|'''|\"|')")
_ATOM = re.compile(
    r"\\(?:\r\n|\n|N\{[^}]*\}|u[0-9a-fA-F]{4}|U[0-9a-fA-F]{8}"
    r"|x[0-9a-fA-F]{2}|[0-7]{1,3}|.)|\r\n|.",
    re.S,
)


@dataclass(frozen=True)
class Docstring(Comment):
    """One docstring's prose mapped to payload spans inside its literals."""

    spans: tuple[tuple[tuple[int, int], ...], ...]
    suffix: str

    def _without_range(self, start: int, end: int) -> str | None:
        remaining = self.text[:start] + self.text[end:]
        if not remaining.strip():
            return self.suffix
        deleted = {
            at
            for spans in self.spans[start:end]
            for left, right in spans
            for at in range(left, right)
        }
        changed = "".join(c for at, c in enumerate(self.raw_text) if at not in deleted)
        reread = concatenated(changed)
        if reread is None or reread.text != re.sub(r"\s+", " ", remaining).strip():
            return None
        return changed

    def without_raw(self, start: int, end: int) -> str | None:
        """Remove payload intersecting a raw range, keeping literal boundaries."""
        selected = [
            at
            for at, spans in enumerate(self.spans)
            if any(left < end and start < right for left, right in spans)
        ]
        if not selected:
            return self.raw_text
        return self._without_range(selected[0], selected[-1] + 1)


def concatenated(raw: str) -> Docstring | None:
    """Read the first string expression when it contains several literals."""
    try:
        return _concatenated(raw)
    except (SyntaxError, ValueError, tokenize.TokenError):
        return None


def _concatenated(raw: str) -> Docstring | None:
    indent = raw[: len(raw) - len(raw.lstrip())]
    source = raw[len(indent) :]
    tree = ast.parse(source)
    if not tree.body or not isinstance(tree.body[0], ast.Expr):
        return None
    expression = tree.body[0]
    if not isinstance(expression.value, ast.Constant) or not isinstance(
        expression.value.value, str
    ):
        return None
    lines = source.splitlines(keepends=True)
    starts = [0]
    for line in lines:
        starts.append(starts[-1] + len(line))

    def at(row: int, column: int, *, byte: bool = False) -> int:
        if byte:
            column = len(lines[row - 1].encode("utf-8")[:column].decode("utf-8"))
        return len(indent) + starts[row - 1] + column

    assert expression.end_lineno is not None and expression.end_col_offset is not None
    first = at(expression.lineno, expression.col_offset, byte=True)
    last = at(expression.end_lineno, expression.end_col_offset, byte=True)
    tokens = [
        token
        for token in tokenize.generate_tokens(io.StringIO(source).readline)
        if token.type == tokenize.STRING
        and first <= at(*token.start)
        and at(*token.end) <= last
    ]
    if len(tokens) < 2:
        return None
    decoded = ""
    spans: list[tuple[int, int]] = []
    for token in tokens:
        opening = _OPEN.match(token.string)
        if opening is None:
            return None
        prefix, close = opening.groups()
        body = token.string[opening.end() : -len(close)]
        origin = at(*token.start) + opening.end()
        raw_literal = "r" in prefix.lower()
        atoms = (
            re.finditer(r"\r\n|.", body, re.S) if raw_literal else _ATOM.finditer(body)
        )
        value = ""
        for atom in atoms:
            piece = atom.group()
            if piece == "\r\n":
                chars = "\n"
            elif piece.startswith("\\") and not raw_literal:
                chars = ast.literal_eval(opening.group() + piece + close)
            else:
                chars = piece
            value += chars
            spans.extend([(origin + atom.start(), origin + atom.end())] * len(chars))
        if value != ast.literal_eval(token.string):
            return None
        decoded += value
    if decoded != expression.value.value:
        return None
    prose = ""
    payloads = []
    for match in re.finditer(r"\s+|\S", decoded):
        if match.group().isspace():
            if not prose or match.end() == len(decoded):
                continue
            prose += " "
        else:
            prose += match.group()
        payloads.append(tuple(spans[match.start() : match.end()]))
    tail = raw[last:].rstrip("\r\n")
    ending = re.search(r"[\r\n]*$", raw)
    suffix = ""
    if tail.strip():
        tail = tail.lstrip(" \t")
        if tail.startswith(";"):
            tail = tail[1:].lstrip(" \t")
        newline = "\r\n" if "\r\n" in raw else "\n"
        suffix = newline if expression.end_lineno > expression.lineno else ""
        suffix += indent + tail + (ending.group() if ending else "")
    fragment = Fragment(raw, prose, (prose,), "", "", "")
    return Docstring(raw, (fragment,), tuple(payloads), suffix)
