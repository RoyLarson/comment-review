"""Read addressed pages once per caller-owned snapshot cache.

Each held result retains its acquired source and requested reading context.
Requests admit installed compatibility before consulting places, and refuse
different settings or supplied source versions without replacing the first
reading. Extra paths derive defaults at acquisition and retain that context.
"""

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple

from comment_review.binder.page import Page
from comment_review.flows.page_for import page_of
from comment_review.flows.reading_context import context_for
from comment_review.flows.source import source_of
from comment_review.machine.repo import Source, can_escape
from comment_review.reading.addresser import (
    SEPARATOR,
    cue_of,
    flatten,
    folded,
    unflatten,
)
from comment_review.reading.context import ReadingContext
from comment_review.reading.diagnostics import ReadDiagnostic, ReadFailure, ReadStage


@dataclass(frozen=True)
class HeldPage:
    """One acquired snapshot, requested context, and retained read outcome."""

    context: ReadingContext | None
    source: Source | ReadFailure | None
    result: Page | ReadFailure


PageCache = dict[str, HeldPage]


def _refusal(code: str, message: str) -> ReadFailure:
    return ReadFailure((ReadDiagnostic(ReadStage.SELECT, code, message),))


class Held(NamedTuple):
    """What the page holds at one place.

    Attributes:
        text: the paragraph there, or "" where the place holds none.
        anchor: the line of code the place sits on, or "" if absent.
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


def printed_name(name: str, paths: list[str], root: Path) -> str:
    """A flattened page name as the binder or the checkout prints it.

    The binder's own spelling answers first: a name it holds exactly is
    returned as it is, and otherwise the one binder path that folds alike
    (`reading.addresser.folded`). A page the binder lacks is found in the
    checkout, one directory at a time, preferring an entry spelled exactly.

    Args:
        name: the path half of an address, as a role wrote it.
        paths: the binder's own page paths.
        root: the checkout a page outside the binder is looked for in.

    Returns:
        The flattened path as printed, or "" where neither the binder nor the
        checkout holds exactly one path that folds to `name`, or the path
        would land outside `root`.
    """
    printed = [flatten(p) for p in paths]
    if name in printed:
        return name
    alike = {one for one in printed if folded(one) == folded(name)}
    if alike:
        return alike.pop() if len(alike) == 1 else ""
    real = name.strip().replace(SEPARATOR, "/")
    if not real or can_escape(real):
        return ""
    here, spelled = root, []
    for part in real.split("/"):
        try:
            entries = os.listdir(here)
        except OSError:
            return ""
        hits = (
            [part]
            if part in entries
            else [e for e in entries if folded(e) == folded(part)]
        )
        if len(hits) != 1:
            return ""
        spelled.append(hits[0])
        here = here / hits[0]
    return flatten("/".join(spelled))


def page_named(
    name: str,
    paths: list[str],
    root: Path,
    cache: PageCache,
    *,
    reading_context: ReadingContext | None = None,
    contexts: Mapping[str, ReadingContext] | None = None,
    source: Source | None = None,
    settings: Mapping[str, str] | None = None,
) -> tuple[str, Page | ReadFailure]:
    """Return a real path and its page or retained expected failure.

    The caller owns a cache for one checkout snapshot. Installed metadata is
    admitted on every request; a supplied source is compared with the held
    source rather than reacquired. A changed context or source is refused
    without replacing the first result. Unsafe paths never acquire source.
    A supplied contexts map must contain every recorded path requested;
    only paths outside those records may acquire fresh default readings.
    """
    real = real_path(name, paths)
    previous = cache.get(real)
    if not real or can_escape(real):
        failure = _refusal("unsafe-page-path", no_page(real))
        if previous is None:
            cache[real] = HeldPage(None, None, failure)
        return real, cache[real].result
    if contexts is not None and real in paths and real not in contexts:
        return real, _refusal(
            "missing-reading-context",
            f"{real}: saved reading context is missing; regather",
        )
    requested = (
        reading_context
        if reading_context is not None
        else contexts.get(real)
        if contexts is not None
        else None
    )
    if requested is None and settings is None and previous is not None:
        requested = previous.context
    context = context_for(
        root / real,
        settings
        if settings is not None
        else dict(requested.settings)
        if requested
        else {},
    )
    if isinstance(context, ReadFailure):
        if previous is None:
            cache[real] = HeldPage(requested, source, context)
        if previous is not None and source is not None and source != previous.source:
            return real, _refusal(
                "held-source-mismatch", "Supplied source differs from held snapshot"
            )
        return (
            real,
            previous.result
            if previous
            and previous.context == requested
            and isinstance(previous.result, ReadFailure)
            and previous.result.diagnostics == context.diagnostics
            else context,
        )
    if requested is not None and context != requested:
        failure = _refusal(
            "reading-context-mismatch",
            "Reading context differs from installed metadata; regather",
        )
        if previous is None:
            cache[real] = HeldPage(requested, source, failure)
        elif (
            previous.context == requested
            and isinstance(previous.result, ReadFailure)
            and previous.result.diagnostics == failure.diagnostics
        ):
            failure = previous.result
        return real, failure
    if previous is not None:
        if previous.context != context:
            return real, _refusal(
                "held-context-mismatch",
                "Requested reading context differs from held page; regather",
            )
        if source is not None and source != previous.source:
            return real, _refusal(
                "held-source-mismatch", "Supplied source differs from held snapshot"
            )
        return real, previous.result
    acquired = source_of(root / real) if source is None else source
    result = (
        acquired
        if isinstance(acquired, ReadFailure)
        else page_of(
            root / real,
            rel=real,
            source=acquired,
            reading_context=context,
        )
    )
    cache[real] = HeldPage(context, acquired, result)
    return real, result


def held_at(
    address: str,
    paths: list[str],
    root: Path,
    cache: PageCache,
    *,
    reading_context: ReadingContext | None = None,
    contexts: Mapping[str, ReadingContext] | None = None,
    source: Source | None = None,
    settings: Mapping[str, str] | None = None,
) -> Held | ReadFailure:
    """Return text and anchor at an address, or an explicit read failure.

    Saved contexts are keyed by real path. A missing extra path uses explicit
    defaults on its first acquisition. A malformed address or absent place
    yields empty text and anchor; unreadable or incompatible pages fail.
    """
    addr = cue_of(address)
    if not addr.path or not addr.cue:
        return Held("", "")
    _real, page = page_named(
        addr.path,
        paths,
        root,
        cache,
        reading_context=reading_context,
        contexts=contexts,
        source=source,
        settings=settings,
    )
    if isinstance(page, ReadFailure):
        return page
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
