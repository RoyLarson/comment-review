"""Look a place up on the page it names: by line, or by address.

Both read the file through `gather.page_in`, the read gather makes, and read no
binder: an address is looked up from the page it names, filled or empty
(`decision-log.md Process: #96`, `#111`, `#279`).
"""

from dataclasses import dataclass
from pathlib import Path

from comment_review.binder.addresses import resolve
from comment_review.binder.page import Page
from comment_review.constants import text_lines
from comment_review.flows.gather import page_in
from comment_review.flows.reading_context import load_settings
from comment_review.reading.addresser import DECLARED, SEPARATOR, address_for, cue_of


@dataclass(frozen=True)
class Refused:
    """No answer, and why.

    `code` is 1 when the page has no such place, 2 when the question is
    malformed or the file could not be read as a page.
    """

    code: int
    lines: tuple[str, ...]


@dataclass(frozen=True)
class Places:
    """The places at one line of one series: each address and its anchor."""

    line: int | str
    series: str
    found: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class Spans:
    """The paragraphs at one address: each file, line span and cue."""

    found: tuple[tuple[str, int | None, int | None, str], ...]


def _page(repo: Path, rel: str, reading_settings: Path | None) -> Page | Refused:
    """The page for `rel` under `repo`, read with the run's reading settings."""
    settings: dict[Path, dict[str, str]] = {}
    if reading_settings is not None:
        settings, problems = load_settings(reading_settings, repo)
        if problems:
            return Refused(2, tuple(problems))
    path = repo / rel
    page, _, why = page_in(path, repo, settings.get(path.resolve(), {}))
    return page if page is not None else Refused(2, (why,))


def place_at(
    repo: Path,
    file: str,
    line: int | str,
    series: str,
    reading_settings: Path | None = None,
) -> Places | Refused:
    """The address of one series' place at one line of one file.

    `line` is a line number, or a sentinel naming the places at the file's head
    or foot that no line number reaches -- see `Cues.at_line`. At a line number
    the file's own matter answers twice, head and foot, since no line tells them
    apart; a caller chooses by address, or asks at a sentinel.
    """
    rel = Path(file).as_posix()
    page = _page(repo, rel, reading_settings)
    if isinstance(page, Refused):
        return page
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
    return Places(
        line,
        series,
        tuple((address_for(rel, c), page.cues.anchor_of(c)) for c in found),
    )


def lines_of(
    repo: Path, address: str, reading_settings: Path | None = None
) -> Spans | Refused:
    """An address in, the lines that cover it now out.

    Stage 8 needs this direction after the write: every line number a record
    carried is stale by then. The address is read as the file now places it,
    which need not be the place the text was written at -- written text can
    share a neighbour's paragraph and read at another address. Several
    paragraphs can answer to one address, so every match is returned.
    """
    path, where = cue_of(address)
    if not where:
        return Refused(2, (f"{address!r} is not an address -- it needs a `@place`",))
    # The separator is a character a path cannot hold, so the flattened path
    # inverts by substitution; see `reading.addresser.flatten`.
    rel = path.replace(SEPARATOR, "/")
    page = _page(repo, rel, reading_settings)
    if isinstance(page, Refused):
        return page
    hits = resolve(address, page.paragraphs)
    if not hits:
        return Refused(1, (f"{address} names no place on {rel}",))
    return Spans(
        tuple(
            (
                rel,
                page.paragraphs[i - 1].original_start,
                page.paragraphs[i - 1].original_end,
                cue_of(page.paragraphs[i - 1].address).cue,
            )
            for i in hits
        )
    )
