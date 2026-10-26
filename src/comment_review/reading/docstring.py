"""Read Python docstring prose with its literal boundaries, by the Python scanner."""

import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import cast

from comment_review.reading.comment import Comment, Fragment
from comment_review.reading.definitions import LanguageDefinition
from comment_review.reading.diagnostics import ReadFailure
from comment_review.reading.python.documentation import decode_escape
from comment_review.reading.python.records import PythonScan, PythonToken
from comment_review.reading.python.scanner import scan_python


@dataclass(frozen=True)
class Docstring(Comment):
    """One docstring's prose mapped to payload spans inside its literals."""

    spans: tuple[tuple[tuple[int, int], ...], ...]
    suffix: str
    definition: LanguageDefinition

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
        reread = concatenated(changed, self.definition)
        if reread is None or reread.text != re.sub(r"\s+", " ", remaining).strip():
            return None
        return changed

    def without_raw(self, start: int, end: int) -> str | None:
        """Remove prose in a raw range.

        Preserve literal boundaries while prose remains. Remove an emptied
        expression, or return None if the edit cannot be set.
        """
        selected = [
            at
            for at, spans in enumerate(self.spans)
            if any(left < end and start < right for left, right in spans)
        ]
        if not selected:
            return self.raw_text
        return self._without_range(selected[0], selected[-1] + 1)


def _scan_line(raw: str, definition: LanguageDefinition) -> PythonScan | ReadFailure:
    """Scan a paragraph's raw text as the physical lines it stands on.

    A docstring paragraph runs to the end of its closing line, which may end in
    a continuation marker; the line break after it, which the paragraph does
    not hold, is what completes the marker, so the scan is given one.
    """
    return scan_python(raw + "\n", definition)


def first_literal(raw: str, definition: LanguageDefinition) -> str | None:
    """The spelling of the first string literal in `raw`, or None where none scans."""
    scan = _scan_line(raw, definition)
    if isinstance(scan, ReadFailure):
        return None
    token = next((one for one in scan.tokens if one.kind == "string"), None)
    return None if token is None else raw[token.span.start : token.span.end]


def concatenated(raw: str, definition: LanguageDefinition) -> Docstring | None:
    """Read the first statement when it is two or more adjacent string literals.

    The statement is the literals alone, in parentheses or not, followed by
    nothing, a line break, a comment or a statement separator. None where it
    is anything else, holds one literal, or does not scan or decode.
    """
    indent = raw[: len(raw) - len(raw.lstrip())]
    source = raw[len(indent) :]
    scan = _scan_line(source, definition)
    if isinstance(scan, ReadFailure):
        return None
    expression = _expression(source, scan.tokens, definition)
    if expression is None:
        return None
    strings, last = expression
    if len(strings) < 2:
        return None
    literals = cast(Mapping[str, object], definition.rules["literals"])
    decoding = cast(Mapping[str, object], literals["decoding"])
    prefixes = cast(Mapping[str, tuple[str, ...]], literals["prefixes"])
    quotes = cast(tuple[str, ...], literals["short_quotes"])
    triples = cast(tuple[str, ...], literals["triple_quotes"])
    escape = cast(str, literals["escape_marker"])
    decoded = ""
    spans: list[tuple[int, int]] = []
    for token in strings:
        quote_start = next(
            at for at in range(token.span.start, token.span.end) if source[at] in quotes
        )
        prefix = source[token.span.start : quote_start]
        if literals["case_insensitive_prefixes"]:
            prefix = prefix.lower()
        quote = next(
            (one for one in triples if source.startswith(one, quote_start)),
            source[quote_start],
        )
        raw_literal = prefix in prefixes["raw"]
        at = quote_start + len(quote)
        end = token.span.end - len(quote)
        while at < end:
            if source[at] in "\r\n":
                following = at + (2 if source.startswith("\r\n", at, end) else 1)
                chars = "\n"
            elif not raw_literal and source.startswith(escape, at):
                result = decode_escape(source, at, end, escape, decoding)
                if isinstance(result, ReadFailure):
                    return None
                chars, following = result
            else:
                following = at + 1
                chars = source[at]
            decoded += chars
            spans.extend([(len(indent) + at, len(indent) + following)] * len(chars))
            at = following
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
    tail = source[last:].rstrip("\r\n")
    ending = re.search(r"[\r\n]*$", raw)
    suffix = ""
    if tail.strip():
        tail = tail.lstrip(" \t")
        if tail.startswith(";"):
            tail = tail[1:].lstrip(" \t")
        newline = "\r\n" if "\r\n" in raw else "\n"
        suffix = newline if re.search(r"[\r\n]", source[:last]) else ""
        suffix += indent + tail + (ending.group() if ending else "")
    fragment = Fragment(raw, prose, (prose,), "", "", "")
    return Docstring(raw, (fragment,), tuple(payloads), suffix, definition)


def _expression(
    source: str, tokens: tuple[PythonToken, ...], definition: LanguageDefinition
) -> tuple[list[PythonToken], int] | None:
    """The first statement's string literals and where the expression ends.

    None where the statement holds anything but documentation literals and
    the parentheses around them.
    """
    literals = cast(Mapping[str, object], definition.rules["literals"])
    documentation = cast(Mapping[str, object], definition.rules["documentation"])
    layout = cast(Mapping[str, object], definition.rules["layout"])
    prefixes = cast(Mapping[str, tuple[str, ...]], literals["prefixes"])
    quotes = cast(tuple[str, ...], literals["short_quotes"])
    groups = cast(tuple[str, ...], documentation["literal_groups"])
    allowed = {prefix for group in groups for prefix in prefixes[group]}
    closer = dict(cast(tuple[tuple[str, str], ...], layout["implicit_pairs"]))["("]
    separator = cast(str, layout["statement_separator"])
    strings: list[PythonToken] = []
    depth = 0
    joined = closed = False
    end = 0
    follower: PythonToken | None = None
    for token in tokens:
        spelling = source[token.span.start : token.span.end]
        if closed:
            follower = token
            break
        if token.kind == "boundary" and spelling == "(" and not strings:
            depth += 1
            end = token.span.end
        elif token.kind == "string":
            quote = next(at for at, char in enumerate(spelling) if char in quotes)
            prefix = spelling[:quote]
            if literals["case_insensitive_prefixes"]:
                prefix = prefix.lower()
            if prefix not in allowed:
                return None
            strings.append(token)
            end = token.span.end
        elif token.kind == "continuation":
            joined = True
        elif token.kind == "newline" and (depth or joined):
            joined = False
        elif token.kind == "comment" and depth:
            pass
        elif token.kind == "boundary" and spelling == closer and depth and strings:
            depth -= 1
            end = token.span.end
            closed = not depth
        else:
            follower = token
            break
    if depth or not strings:
        return None
    if follower is not None and not (
        follower.kind in ("newline", "comment")
        or source[follower.span.start : follower.span.end] == separator
    ):
        return None
    return strings, end
