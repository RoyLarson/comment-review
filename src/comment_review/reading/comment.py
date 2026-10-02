"""Restore a paragraph using the comment form extracted by the reader."""

import re
import textwrap
from dataclasses import dataclass


@dataclass(frozen=True)
class Comment:
    """Unwrapped prose and the original paragraph's markers and layout."""

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

    def wrap(self, text: str) -> str:
        """Wrap prose within the original width and restore its delimiters."""
        if not text.strip():
            return ""
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
        for section in sections:
            if len(out) > len(self.head):
                out.append(self.rest.rstrip())
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

    def without_once(self, snippet: str) -> str | None:
        """Remove one complete occurrence from the unwrapped prose."""
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
        remaining = []
        offset = 0
        for paragraph in self.paragraphs:
            before = max(0, min(len(paragraph), start - offset))
            after = max(0, min(len(paragraph), end - offset))
            kept = re.sub(r"\s+", " ", paragraph[:before] + paragraph[after:]).strip()
            if kept:
                remaining.append(kept)
            offset += len(paragraph) + 1
        return self.wrap("\n\n".join(remaining))
