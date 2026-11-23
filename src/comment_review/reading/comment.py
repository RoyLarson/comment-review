"""A paragraph's comment form: read from its raw text, and restored to it.

`comment_form` parses a comment's markers and fragments for `Paragraph.text`
and `desk.marks.rules`; `Comment` and `Fragment` hold what it found and take
prose out of that form.

`CommentSpan` is one comment as its language's reader scans it --
`reading.rust.scanner` returns them -- and `comment_form` cuts a paragraph into
fragments at them.
"""

import re
import textwrap
from bisect import bisect_left
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
    rest: str
    ending: str = ""
    anchor_width: int = 0
    positions: tuple[int, ...] = ()
    suffix: str = ""

    def cut(self, start: int, end: int) -> str | None:
        """This fragment's raw text with its prose `[start, end)` taken out.

        Only the lines holding the removed prose are rewritten. Each run of them
        between blank lines is set again from its first line's lead, its second
        line's lead for any line after, and its last line's trail, at the
        paragraph's own width; every other line is kept byte for byte. A run
        left with no prose goes, with the blank line it would strand. None where the
        prose cannot be mapped back onto the raw text, where an emptied first
        line's opener has no prose below to come up onto it, or where an emptied
        line's closer has no line above to move onto.
        """
        text, at, raw = self.text, self.positions, self.raw_text
        if len(at) != len(text):
            return None
        marks = [i for i in range(start, end) if not text[i].isspace()]
        if not marks:
            return raw
        lo, hi = at[marks[0]], at[marks[-1]] + 1
        lines = raw.split("\n")
        bounds, offset = [], 0
        for line in lines:
            bounds.append((offset, offset + len(line)))
            offset += len(line) + 1
        first = raw.count("\n", 0, lo)
        last = raw.count("\n", 0, hi - 1)
        # Each line keeps its own `\r`, so a CRLF paragraph stays CRLF.
        cr = "\r" if "\r\n" in raw else ""
        width = max(
            [
                len(lines[0].rstrip("\r")) + self.anchor_width,
                *(len(line.rstrip("\r")) for line in lines[1:]),
            ]
        )

        def prose_on(n: int) -> list[int]:
            begin, finish = bounds[n]
            return [
                i
                for i in range(bisect_left(at, begin), bisect_left(at, finish))
                if not text[i].isspace()
            ]

        out = lines[:first]
        # Whether each line of `out` holds prose, and where an emptied run went.
        held = [bool(prose_on(k)) for k in range(first)]
        emptied: list[int] = []
        run: list[int] = []
        n = first
        while n <= last + 1:
            if n <= last and prose_on(n):
                run.append(n)
                n += 1
                continue
            if run:
                wrapped, lead, trail = self._set_run(
                    run, lines, bounds, prose_on, start, end, width
                )
                trail = trail.removesuffix("\r")
                if not wrapped and run[0] == 0 and lead.strip() != self.rest.strip():
                    # The opener stood on the emptied line: the next line holding
                    # prose comes up onto it, and the blank lines between go.
                    below = range(run[-1] + 1, len(lines))
                    up = next((k for k in below if prose_on(k)), None)
                    if up is None:
                        return None
                    wrapped, _, _ = self._set_run(
                        [*run, up], lines, bounds, prose_on, start, end, width
                    )
                    out.extend(wrapped)
                    held += [True] * len(wrapped)
                    run = []
                    n, last = up + 1, max(last, up)
                    continue
                setting = bool(wrapped)
                if not wrapped:
                    emptied.append(len(out))
                if not wrapped and trail.strip():
                    if not (out and out[-1].strip()):
                        return None
                    # A closer on an emptied line moves up onto the line above,
                    # or stands on a line of its own where that line has no room.
                    joined = out[-1].rstrip() + trail
                    if len(joined.rstrip()) <= width:
                        out[-1] = joined + cr
                    else:
                        wrapped = [lead + trail.lstrip() + cr]
                out.extend(wrapped)
                held += [setting] * len(wrapped)
                run = []
            if n <= last:
                out.append(lines[n])
                held.append(bool(prose_on(n)))
            n += 1
        out.extend(lines[last + 1 :])
        held += [bool(prose_on(k)) for k in range(last + 1, len(lines))]
        return "\n".join(self._without_stray_separators(out, held, emptied))

    def _without_stray_separators(
        self, out: list[str], held: list[bool], emptied: list[int]
    ) -> list[str]:
        """`out` without the blank line an emptied run left stranded.

        A blank line is a line holding no prose and nothing but the
        comment's own continuation marker. Where a run went, the blank above
        it goes when another blank or no more prose follows, and the blank
        below it goes when no prose stands above.
        """
        out, held = list(out), list(held)
        marker = self.rest.strip()

        def blank(i: int) -> bool:
            return 0 <= i < len(out) and not held[i] and out[i].strip() == marker

        for site in reversed(emptied):
            if blank(site - 1) and (blank(site) or not any(held[site:])):
                del out[site - 1], held[site - 1]
            elif blank(site) and not any(held[:site]):
                del out[site], held[site]
        return out

    def _set_run(
        self, run, lines, bounds, prose_on, start, end, width
    ) -> tuple[list[str], str, str]:
        """One run of touched lines set again, with its lead and its trail.

        The lines are `[]` where the run keeps no prose.
        """
        text, at = self.text, self.positions
        b0, b1 = prose_on(run[0])[0], prose_on(run[-1])[-1]
        before = text[b0:start].rstrip() if start > b0 else ""
        after = text[max(end, b0) : b1 + 1].lstrip() if end <= b1 else ""
        kept = re.sub(r"\s+", " ", f"{before} {after}").strip()
        lead = lines[run[0]][: at[b0] - bounds[run[0]][0]]
        tail_line = run[-1]
        trail = lines[tail_line][at[b1] + 1 - bounds[tail_line][0] :]
        if not trail.endswith("\r") and lines[run[0]].endswith("\r"):
            trail += "\r"
        if not kept:
            return [], lead, trail
        if len(run) > 1:
            follow = lines[run[1]][: at[prose_on(run[1])[0]] - bounds[run[1]][0]]
        elif run[0] == 0:
            follow = self.rest
        else:
            follow = lead
        padding = " " * self.anchor_width if run[0] == 0 else ""
        wrapped = textwrap.wrap(
            kept,
            width=max(width - len(trail), len(lead) + 1, len(follow) + 1),
            initial_indent=padding + lead,
            subsequent_indent=follow,
            break_long_words=False,
            break_on_hyphens=False,
        ) or [padding + lead + kept]
        if padding:
            wrapped[0] = wrapped[0][len(padding) :]
        cr = "\r" if trail.endswith("\r") else ""
        trail = trail.removesuffix("\r")
        wrapped = [*(line + cr for line in wrapped[:-1]), wrapped[-1] + trail + cr]
        return wrapped, lead, trail + cr


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
        """The raw text with the one whole-word prose match of `snippet` removed.

        A match that continues a word at either end does not count. None where
        there is not exactly one, or where the match cannot be taken out of the
        raw text.
        """
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
        """The raw text with the prose in a raw-text range removed, or None.

        Only the lines that held the removed prose are set again; see
        `Fragment.cut`.
        """
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
            begun = offset
            remaining = False
            for paragraph in part.paragraphs:
                before = max(0, min(len(paragraph), start - offset))
                after = max(0, min(len(paragraph), end - offset))
                remaining |= bool((paragraph[:before] + paragraph[after:]).strip())
                offset += len(paragraph) + 1
            local = (max(0, start - begun), max(0, min(len(part.text), end - begun)))
            if not remaining:
                text = part.suffix
            elif local[0] < local[1]:
                text = part.cut(*local)
                if text is None:
                    return None
            else:
                text = part.raw_text
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
            # An emptied comment leaves at most its suffix or its line ending, so
            # `rendered[-1]` is always the last text kept, and it ends in a line
            # break unless its line is open.
            if text:
                rendered.append(text)
        found = re.search(r"[\r\n]+$", self.raw_text)
        ending = found.group(0) if found else ""
        return "".join(rendered).rstrip("\r\n") + (ending if rendered else "")


def _join(lines: list[str]) -> str:
    """Prose lines, their markers already cut, as ONE normalised string.

    Prose wraps, so a claim-bearing phrase in a real file often straddles a
    line break. Matching line-by-line reports the fragment instead of the claim: a
    count reads as absent, and so does `used to say`, since `annotate` matches
    `used to` only before a verb of saying.
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
        # Imported here: `docstring` imports this module for `Comment` and `Fragment`.
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
        return Fragment(raw_text, "", (), "", ending=ending)
    starts = []
    offset = 0
    for line in content.splitlines(keepends=True):
        starts.append(offset)
        offset += len(line)
    indent = lines[0][: len(lines[0]) - len(lines[0].lstrip())]
    body = list(lines)
    rest = indent
    last = ""
    opener_alone = False
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
        body[0] = body[0][len(indent + op) :]
        starts[0] += len(indent + op)
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
            opener_alone = True
            body.pop(0)
            starts.pop(0)
        if body and not body[-1].strip() and last:
            body.pop()
            starts.pop()
        rest = indent
        if body:
            sample = body[0] if opener_alone else next(iter(body[1:]), "")
            prefix = r"^(\s*\*(?:[ \t]+|$)|\s*)" if op.startswith("/*") else r"^\s*"
            found = re.match(prefix, sample)
            if found is not None:
                rest = found.group(0) or indent
        if op.startswith("/*"):
            for n, line in enumerate(body):
                if n == 0 and not opener_alone:
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
        rest,
        ending,
        len(anchor) if series is Series.ON else 0,
        tuple(positions),
        suffix,
    )
