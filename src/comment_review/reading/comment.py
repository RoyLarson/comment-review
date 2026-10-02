"""Restore a paragraph using the comment form extracted by the reader."""

import re
import textwrap
from dataclasses import dataclass


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

    def without_raw(self, start: int, end: int) -> str:
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

    def _without_range(self, start: int, end: int) -> str:
        rendered = []
        offset = 0
        for part in self.fragments:
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
            rendered.append(part.wrap("\n\n".join(remaining), tuple(kept_indices)))
        found = re.search(r"[\r\n]+$", self.raw_text)
        ending = found.group(0) if found else ""
        return "".join(rendered).rstrip("\r\n") + (ending if any(rendered) else "")
