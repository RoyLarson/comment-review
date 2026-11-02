"""A paragraph's comment form: read from its raw text, and restored to it.

`comment_form` parses a comment's markers and fragments for `Paragraph.text`
and `desk.marks.rules`; `Comment` and `Fragment` hold what it found and rewrap
prose into that form.
"""

import re
import textwrap
from collections.abc import Callable
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import NamedTuple

from comment_review import constants
from comment_review.reading.definitions import LanguageDefinition
from comment_review.reading.language import (
    INSTALLED_REGISTRY,
    documents_in_literals,
    line_comment_marker,
)
from comment_review.reading.series import Series


@dataclass(frozen=True)
class CommentSpan:
    """One comment in a paragraph's raw text, as its language's own reader reads it.

    `start` and `end` are offsets into the raw text; `closer` is empty for a
    line comment.
    """

    start: int
    end: int
    opener: str
    closer: str


@dataclass(frozen=True)
class Fragment:
    """Prose inside one comment form, with its original markers and layout."""

    raw_text: str
    text: str
    paragraphs: tuple[str, ...]
    first: str
    rest: str
    last: str
    head: tuple[str, ...] = ()
    foot: tuple[str, ...] = ()
    ending: str = ""
    anchor_width: int = 0
    positions: tuple[int, ...] = ()
    suffix: str = ""
    gaps: tuple[tuple[str, ...], ...] = ()

    def wrap(self, text: str, kept: tuple[int, ...] = ()) -> str:
        """Rewrap prose using the original width, keeping words intact."""
        if not text.strip():
            return self.suffix
        if text == self.text:
            return self.raw_text
        original = self.raw_text.splitlines()
        width = max(
            [
                len(original[0]) + self.anchor_width,
                *(len(line) for line in original[1:]),
            ]
        )
        out = list(self.head)
        sections = re.split(r"\n\s*\n", text.strip())
        for n, section in enumerate(sections):
            if len(out) > len(self.head):
                original = kept[n] if kept else n
                out.extend(self.gaps[original - 1])
            first = self.first if len(out) == len(self.head) else self.rest
            padding = " " * self.anchor_width if not out else ""
            wrapped = textwrap.wrap(
                section,
                width=max(width - len(self.last), len(first) + 1, len(self.rest) + 1),
                initial_indent=padding + first,
                subsequent_indent=self.rest,
                break_long_words=False,
                break_on_hyphens=False,
            )
            if padding and wrapped:
                wrapped[0] = wrapped[0][len(padding) :]
            out.extend(wrapped)
        if out and self.last:
            out[-1] += self.last
        out.extend(self.foot)
        separator = "\r\n" if "\r\n" in self.raw_text else "\n"
        return separator.join(out) + self.ending


@dataclass(frozen=True)
class Comment:
    """The addressed paragraph's comment fragments in their original order."""

    raw_text: str
    fragments: tuple[Fragment, ...]

    @property
    def text(self) -> str:
        """The fragments' prose joined in paragraph order."""
        return " ".join(part.text for part in self.fragments if part.text)

    def without_once(self, snippet: str) -> str | None:
        """Return rewrapped text after removing a unique prose match, or None."""
        if not snippet:
            return None
        matches = list(re.finditer(r"(?=" + re.escape(snippet) + r")", self.text))
        matches = [
            found
            for found in matches
            if not (
                snippet[0].isalnum()
                and found.start() > 0
                and self.text[found.start() - 1].isalnum()
            )
            and not (
                snippet[-1].isalnum()
                and found.start() + len(snippet) < len(self.text)
                and self.text[found.start() + len(snippet)].isalnum()
            )
        ]
        if len(matches) != 1:
            return None
        start = matches[0].start()
        end = start + len(snippet)
        return self._without_range(start, end)

    def without_raw(self, start: int, end: int) -> str | None:
        """Remove prose in a raw-text range and rewrap what remains."""
        selected = []
        raw_offset = prose_offset = 0
        for part in self.fragments:
            selected.extend(
                prose_offset + at
                for at, position in enumerate(part.positions)
                if start <= raw_offset + position < end
            )
            raw_offset += len(part.raw_text)
            if part.text:
                prose_offset += len(part.text) + 1
        if not selected:
            return self.raw_text
        return self._without_range(selected[0], selected[-1] + 1)

    def _without_range(self, start: int, end: int) -> str | None:
        rendered = []
        offset = 0
        # The space an emptied comment stood on, owed to the next comment on its
        # line.
        carried = ""
        for at, part in enumerate(self.fragments):
            # The comment ends its line: a line break follows it, or nothing.
            ends_line = at == len(self.fragments) - 1 or part.raw_text.endswith(
                ("\n", "\r")
            )
            remaining = []
            kept_indices = []
            for n, paragraph in enumerate(part.paragraphs):
                before = max(0, min(len(paragraph), start - offset))
                after = max(0, min(len(paragraph), end - offset))
                kept = re.sub(
                    r"\s+", " ", paragraph[:before] + paragraph[after:]
                ).strip()
                if kept:
                    remaining.append(kept)
                    kept_indices.append(n)
                offset += len(paragraph) + 1
            text = part.wrap("\n\n".join(remaining), tuple(kept_indices))
            previous = rendered[-1] if rendered else ""
            shares_line = bool(previous) and not previous.endswith(("\n", "\r"))
            if not text and shares_line and ends_line:
                # The comment shared its line with the one before it and ended
                # the line, so the line stays and keeps its end; only the space
                # before the removed comment goes.
                rendered[-1] = rendered[-1].rstrip(" \t")
                text = part.ending
            elif not text and not shares_line and not ends_line:
                # The comment shared its line with the one after it, which takes
                # the indent or the space after code the removed one stood on.
                leading = part.raw_text[
                    : len(part.raw_text) - len(part.raw_text.lstrip(" \t"))
                ]
                carried = carried or leading
            elif text and carried:
                text = carried + text
                carried = ""
            if ends_line:
                carried = ""
            # An emptied comment leaves nothing, so `rendered[-1]` is always the
            # last text kept, and it ends in a line break unless its line is open.
            if text:
                rendered.append(text)
        found = re.search(r"[\r\n]+$", self.raw_text)
        ending = found.group(0) if found else ""
        return "".join(rendered).rstrip("\r\n") + (ending if rendered else "")


def _join(lines: list[str]) -> str:
    """Prose lines, their markers already cut, as ONE normalised string.

    Prose wraps, so every claim-bearing phrase in a real file straddles a line
    break. Matching line-by-line reports the fragment instead of the claim: a
    count reads as absent and `used to say` degrades to a bare `used to`.
    """
    return re.sub(r"\s+", " ", " ".join(ln.strip() for ln in lines)).strip()


class _Grammar(NamedTuple):
    """What a path's language says about its comments, resolved once per suffix."""

    #: The installed definition, or None for a path no language covers.
    definition: LanguageDefinition | None
    #: Whether the language documents in string literals, as Python does.
    in_literals: bool
    #: The marker that opens a line comment, or "" where the definition has none.
    marker: str
    #: The reader's comment scanner, or None where the reader offers none.
    scanner: Callable[[str], tuple[CommentSpan, ...] | None] | None


@cache
def _grammar_for(suffix: str) -> _Grammar:
    """The comment grammar of the installed language a suffix selects.

    Selection is by suffix alone, and the installed registry does not change
    while the process runs, so each suffix is resolved once.
    """
    path = Path(f"m{suffix}")
    value = INSTALLED_REGISTRY.for_path(path)
    scanner = None
    if value is not None and value.reader == "rust-lexical":
        # Imported here: the Rust scanner imports this module for `CommentSpan`.
        from comment_review.reading.rust.scanner import comment_scanner

        scanner = comment_scanner(value)
    return _Grammar(
        value,
        documents_in_literals(path),
        line_comment_marker(path),
        scanner,
    )


def comment_form(
    path: Path, series: Series | None, raw_text: str, anchor: str = ""
) -> Comment:
    """The assigned paragraph's prose and the form its raw text carries.

    A byte-order mark opening the raw text is the file's encoding, and the form
    is read without it.
    """
    raw_text = constants.without_mark(raw_text)
    grammar = _grammar_for(path.suffix.lower())
    if grammar.scanner is not None:
        found = grammar.scanner(raw_text)
        return _scanned_form(grammar, series, raw_text, anchor, found)
    value = grammar.definition
    if value is not None and grammar.in_literals and series is Series.DECLARED:
        # Imported here: `docstring` imports this module for `Comment`.
        from comment_review.reading.docstring import concatenated

        docstring = concatenated(raw_text, value)
        if docstring is not None:
            return docstring
    return Comment(raw_text, (_comment_fragment(grammar, series, raw_text, anchor),))


def _scanned_form(
    grammar: _Grammar,
    series: Series | None,
    raw_text: str,
    anchor: str,
    found: tuple[CommentSpan, ...] | None,
) -> Comment:
    """The paragraph cut into fragments at the comments its reader scanned.

    A delimited comment, and a line comment of another form than the one
    before it, starts a fragment: at its line's start when it opens the line,
    or where it opens when something precedes it there. Line comments of one
    form run on as one fragment. Text before the first comment, such as a
    shebang the matter holds, is a fragment of its own with no markers, and so
    is a paragraph its reader finds no comment in.
    """
    if not found:
        return Comment(
            raw_text, (_comment_fragment(grammar, series, raw_text, anchor),)
        )
    leading: list[Fragment] = []
    if raw_text[: found[0].start].strip():
        line_start = raw_text.rfind("\n", 0, found[0].start) + 1
        opens_line = not raw_text[line_start : found[0].start].strip()
        cut = line_start if opens_line else found[0].start
        leading.append(_comment_fragment(grammar, series, raw_text[:cut], anchor))
        raw_text, whole = raw_text[cut:], raw_text
        found = tuple(
            CommentSpan(c.start - cut, c.end - cut, c.opener, c.closer) for c in found
        )
        anchor = ""
    else:
        whole = raw_text
    cuts = [0]
    opening: list[CommentSpan] = []
    for comment in found:
        if opening:
            previous = opening[-1]
            if not comment.closer and not previous.closer:
                if comment.opener == previous.opener:
                    continue
            line_start = raw_text.rfind("\n", 0, comment.start) + 1
            opens_line = not raw_text[line_start : comment.start].strip()
            cuts.append(line_start if opens_line else comment.start)
        opening.append(comment)
    cuts.append(len(raw_text))
    parts = []
    for n, comment in enumerate(opening):
        start = cuts[n]
        close_at = comment.end - len(comment.closer) - start if comment.closer else -1
        parts.append(
            _comment_fragment(
                grammar,
                series,
                raw_text[start : cuts[n + 1]],
                anchor if n == 0 else "",
                marks=(comment.opener, comment.closer, close_at),
            )
        )
    return Comment(whole, (*leading, *parts))


def _comment_fragment(
    grammar: _Grammar,
    series: Series | None,
    raw_text: str,
    anchor: str,
    marks: tuple[str, str, int] | None = None,
) -> Fragment:
    """One comment's prose and markers.

    `marks` is the comment's opener, closer and the closer's offset in
    `raw_text`, as its reader scanned them, with an empty closer and -1 for a
    line comment. Without them the language's line-comment marker applies.
    """
    definition, in_literals = grammar.definition, grammar.in_literals
    physical = raw_text.splitlines(keepends=True)
    while physical and not physical[-1].strip():
        physical.pop()
    content = "".join(physical).rstrip("\r\n")
    ending = raw_text[len(content) :]
    lines = content.splitlines()
    if not lines:
        return Fragment(raw_text, "", (), "", "", "", ending=ending)
    starts = []
    offset = 0
    for line in content.splitlines(keepends=True):
        starts.append(offset)
        offset += len(line)
    indent = lines[0][: len(lines[0]) - len(lines[0].lstrip())]
    body = list(lines)
    first = rest = indent
    last = ""
    head: tuple[str, ...] = ()
    foot: tuple[str, ...] = ()
    suffix = ""
    opened = None
    end_at = -1
    if marks is not None:
        opener, closer, close_at = marks
        if closer:
            opened = opener, closer
            end_at = close_at
    if (
        in_literals
        and definition is not None
        and series is Series.DECLARED
        and re.match(r"(?i)[rub]*(\"\"\"|'''|\"|')", raw_text.lstrip())
    ):
        from comment_review.reading.docstring import first_literal

        spelling = first_literal(raw_text.lstrip(), definition)
        if spelling is not None:
            opening = re.match(r"(?i)[rub]*(\"\"\"|'''|\"|')", spelling)
            if opening is not None:
                op = opening.group(0)
                close = opening.group(1)
                opened = op, close
                end_at = len(indent) + len(spelling) - len(close)
    if opened is not None:
        op, close = opened
        first = indent + op
        body[0] = body[0][len(first) :]
        starts[0] += len(first)
        closing = end_at - starts[-1] if end_at >= 0 else -1
        if closing >= 0:
            last = body[-1][closing:]
            body[-1] = body[-1][:closing]
            after = last[len(close) :]
            if after.strip():
                suffix_indent = lines[-1][: len(lines[-1]) - len(lines[-1].lstrip())]
                if in_literals:
                    suffix_indent = indent
                    after = after.lstrip(" \t")
                    if after.startswith(";"):
                        after = after[1:].lstrip(" \t")
                suffix = (
                    ("\r\n" if "\r\n" in raw_text else "\n") if len(lines) > 1 else ""
                )
                suffix += suffix_indent + after + ending
        if not body[0].strip():
            head = (lines[0],)
            body.pop(0)
            starts.pop(0)
            first = indent
        else:
            space = body[0][: len(body[0]) - len(body[0].lstrip())]
            first += space
        if body and not body[-1].strip() and last:
            foot = (lines[-1],)
            body.pop()
            starts.pop()
            last = ""
        elif body and last:
            trailing = body[-1][len(body[-1].rstrip()) :]
            last = trailing + last
        rest = indent
        if body:
            sample = body[0] if head else next(iter(body[1:]), "")
            prefix = r"^(\s*\*(?:[ \t]+|$)|\s*)" if op.startswith("/*") else r"^\s*"
            found = re.match(prefix, sample)
            if found is not None:
                rest = found.group(0) or indent
            if head:
                first = rest
        if op.startswith("/*"):
            for n, line in enumerate(body):
                if n == 0 and not head:
                    continue
                found = re.match(r"^\s*\*(?:[ \t]+|$)", line)
                if found is not None:
                    body[n] = line[found.end() :]
                    starts[n] += found.end()
    else:
        marker = marks[0] if marks is not None else grammar.marker
        if marker and lines[0].lstrip().startswith(marker):
            lead = indent + marker
            following = lines[0][len(lead) :]
            first = lead + following[: len(following) - len(following.lstrip())]
            rest = first
            for line in lines[1:]:
                found = re.match(r"^\s*" + re.escape(marker) + r"[ \t]*", line)
                if found is not None and line[found.end() :].strip():
                    rest = found.group(0)
                    break
            body = []
            for n, line in enumerate(lines):
                stripped = line.lstrip()
                if stripped.startswith(marker):
                    body.append(stripped[len(marker) :])
                    starts[n] += len(line) - len(stripped) + len(marker)
                else:
                    body.append(line)
    sections = re.split(r"\n\s*\n", "\n".join(body))
    paragraphs = tuple(
        _join(section.splitlines()) for section in sections if section.strip()
    )
    gaps = []
    blank = []
    seen = False
    for line, at in zip(body, starts, strict=True):
        if not line.strip():
            if seen:
                blank.append(lines[raw_text.count("\n", 0, at)])
        else:
            if blank:
                gaps.append(tuple(blank))
                blank.clear()
            seen = True
    positions = []
    whitespace = None
    for line, at in zip(body, starts, strict=True):
        for n, char in enumerate(line):
            if char.isspace():
                if positions and whitespace is None:
                    whitespace = at + n
            else:
                if whitespace is not None:
                    positions.append(whitespace)
                    whitespace = None
                positions.append(at + n)
        if positions and whitespace is None:
            whitespace = at + len(line)
    return Fragment(
        raw_text,
        " ".join(paragraphs),
        paragraphs,
        first,
        rest,
        last,
        head,
        foot,
        ending,
        len(anchor) if series is Series.ON else 0,
        tuple(positions),
        suffix,
        tuple(gaps),
    )
