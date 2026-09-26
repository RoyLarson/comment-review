"""What a checkout's pages hold at an address, each page read once.

    PageCache                             real path -> the page, or None
    real_path(name, paths)                the real path a flattened page name names
    page_named(name, paths, root, cache)  that path, and its page or None
    held_at(address, paths, root, cache)  the text and the anchor at one place
    no_page(real)                         the one sentence for a page that will not read

Every flow that asks what a place holds on the page asks here. The collate
handler reads each place its copies touch for that place's base and anchor
(`decision-log.md Process: #187`, which restores `#125`); the quote and
resolution checks read the place a mark names (`#119`, `#122`); `check` and
`mark` read the places a row measures a mark against; and the transcription
reads the pages it sets. Before this module each of them turned a flattened
name into a path and read the page its own way, and two of the ways
disagreed about a file the run did not gather.

The page is read whether or not the binder holds it. The binder is the seed
for what a role is handed, not every place or file a mark may touch (`#119`):
a move may land in a file the run never gathered, and the paragraph already
there is still what the move is measured against.

Nothing here asks whether a page changed since it was gathered. The middle
does not ask that at any granularity (`#62`, `#185`); it reads the page as the
checkout holds it.
"""

from pathlib import Path
from typing import NamedTuple

from comment_review.binder.page import Page
from comment_review.flows.page_for import page_of
from comment_review.machine.repo import can_escape
from comment_review.reading.addresser import SEPARATOR, cue_of, unflatten

#: One real path -> its page, or None where this checkout holds no readable
#: page there. A caller keeps one per stage and hands it to every read, so a
#: page every role's marks touch is read once. The None is cached too.
PageCache = dict[str, Page | None]


class Held(NamedTuple):
    """What the page holds at one place.

    Attributes:
        text: the paragraph there, or "" where the place holds none, the page
            cannot be read, or the page carries no such place.
        anchor: the line of code the place sits on, or "" on the same terms.
    """

    text: str
    anchor: str


def real_path(name: str, paths: list[str]) -> str:
    """The real relative path a flattened page name names.

    `unflatten` answers from the paths in hand -- a binder's pages, or a
    copy's sheets. A page outside them, such as the file a move lands in that
    the run did not gather, is found by the plain substitution: the flattened
    form is invertible by construction, since `gather` refuses a path holding
    the separator.

    Args:
        name: the path half of an address.
        paths: the real paths the caller's input records.

    Returns:
        The real path. It is not checked against the checkout here.
    """
    return unflatten(name, paths) or name.replace(SEPARATOR, "/")


def page_named(
    name: str, paths: list[str], root: Path, cache: PageCache
) -> tuple[str, Page | None]:
    """One flattened page name's real path, and its page, read at most once.

    A path that would land outside `root` once joined to it -- absolute,
    carrying a drive, or climbing with `..` -- reads as no page and nothing is
    opened. The name comes from an address a role wrote, and
    `desk.collator.source_problems` keeps the same guard for a cited path.

    Args:
        name: the path half of an address.
        paths: the real paths the caller's input records, for `real_path`.
        root: the checkout the page is read from.
        cache: shared by every read the caller makes, keyed by real path.

    Returns:
        `(the real path, the page)`, the page None where none can be read.
    """
    real = real_path(name, paths)
    if real not in cache:
        page = None
        if real and not can_escape(real):
            page, _why = page_of(root / real, rel=real)
        cache[real] = page
    return real, cache[real]


def held_at(address: str, paths: list[str], root: Path, cache: PageCache) -> Held:
    """The text and the anchor the page holds at `address`.

    Args:
        address: `path@cue`.
        paths: the real paths the caller's input records, for `real_path`.
        root: the checkout the page is read from.
        cache: shared by every read the caller makes, keyed by real path.

    Returns:
        The `Held` there. Both halves are "" where the address is not
        `path@cue`, no page can be read at its path, or the page carries no
        such place; a caller that must tell those apart from an empty place
        asks `page_named`.
    """
    addr = cue_of(address)
    if not addr.path or not addr.cue:
        return Held("", "")
    _real, page = page_named(addr.path, paths, root, cache)
    if page is None:
        return Held("", "")
    text = next(
        (
            b.raw_text
            for b in page.paragraphs
            if b.address and cue_of(b.address).cue == addr.cue
        ),
        "",
    )
    return Held(text, page.cues.anchor_of(addr.cue))


def no_page(real: str) -> str:
    """The one sentence for a page this checkout cannot read, naming it."""
    return f"no page can be read at {real}"
