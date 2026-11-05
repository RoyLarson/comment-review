"""Look a place up on the page it names: by line, or by address.

Both read their page through `on_the_page.page_named`, the reader the write end
uses, after `printed_name` takes the path to the checkout's own spelling and
refuses one that leaves the checkout. No binder is read: an address is looked
up from the page it names, filled or empty.
"""

from dataclasses import dataclass
from pathlib import Path

from comment_review.binder.addresses import resolve
from comment_review.binder.page import Page
from comment_review.constants import text_lines
from comment_review.flows.on_the_page import no_page, page_named, printed_name
from comment_review.flows.read_diagnostics import format_failure
from comment_review.reading.addresser import DECLARED, address_for, cue_of, flatten
from comment_review.reading.diagnostics import ReadFailure


@dataclass(frozen=True)
class Refused:
    """No answer, and why.

    `code` is 1 when the page has no such place, 2 when the question is
    malformed or the file could not be read as a page.
    """

    code: int
    lines: tuple[str, ...]


@dataclass(frozen=True)
class Place:
    """One place: its page, its address, and the line of code it is anchored to.

    `lines` is the span of the file the place's text stands on, or None for an
    empty place, which stands on no line.
    """

    path: str
    address: str
    anchor: str
    lines: tuple[int, int] | None


def _page(repo: Path, name: str) -> Page | Refused:
    """The page a flattened path names in `repo`, as the write end reads it."""
    printed = printed_name(name, [], repo)
    if not printed:
        return Refused(2, (no_page(name),))
    real, page = page_named(printed, [], repo, {})
    if isinstance(page, ReadFailure):
        return Refused(2, (format_failure(page, path=real),))
    return page


def place_at(
    repo: Path, file: str, line: int | str, series: str
) -> list[Place] | Refused:
    """The places one series has at one line of one file.

    `line` is a line number of the file as gathered, or a sentinel naming the
    places at the file's head or foot that no line number reaches -- see
    `Cues.at_line`. At a line number the file's own matter answers twice, head
    and foot, since no line tells them apart; a caller chooses by address.
    """
    given = Path(file)
    if given.is_absolute():
        try:
            given = given.resolve().relative_to(repo.resolve())
        except ValueError:
            return Refused(2, (no_page(file),))
    page = _page(repo, flatten(given.as_posix()))
    if isinstance(page, Refused):
        return page
    rel = page.path
    count = len(text_lines(page.text))
    if isinstance(line, int) and not 1 <= line <= count:
        return Refused(1, (f"{rel} has {count} lines; line {line} is not one of them",))
    found = page.cues.at_line(line, series)
    if not found and isinstance(line, str):
        return Refused(1, (f"{line} of {rel} has no `{series}` place",))
    if not found:
        what = (
            "declares nothing documentable" if series == DECLARED else "holds no code"
        )
        lines = [f"line {line} of {rel} {what}, so it has no `{series}` place"]
        if series == DECLARED and page.cues.documents(None):
            head = address_for(rel, page.cues.documents(None))
            lines.append(f"  the module's own documentation is {head}")
        return Refused(1, tuple(lines))
    return [
        Place(rel, address_for(rel, c), page.cues.anchor_of(c), None) for c in found
    ]


def lines_of(repo: Path, address: str) -> list[Place] | Refused:
    """The paragraphs at one address, read from the file as it is now.

    Every line number a record carried is stale after the write, so stage 8
    turns an address into lines with this. Written text can share a
    neighbour's paragraph and read at another address, and several paragraphs
    can answer to one address, so every match is returned.
    """
    name, where = cue_of(address)
    if not name or not where:
        return Refused(
            2, (f"{address!r} is not an address -- it needs a path and a `@place`",)
        )
    page = _page(repo, name)
    if isinstance(page, Refused):
        return page
    found = [page.paragraphs[i - 1] for i in resolve(address, page.paragraphs)]
    if not found:
        return Refused(1, (f"{address} names no place on {page.path}",))
    return [
        Place(
            page.path,
            address,
            p.anchor,
            None
            if p.original_start is None or p.original_end is None
            else (p.original_start, p.original_end),
        )
        for p in found
    ]
