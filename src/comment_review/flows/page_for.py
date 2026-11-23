"""Acquire a source snapshot and admit it as a complete page."""

from pathlib import Path

from comment_review.binder.page import Page, page_for
from comment_review.flows.read_diagnostics import LocatedReadFailure
from comment_review.flows.reading_context import context_for
from comment_review.flows.source import source_of
from comment_review.machine.repo import Source
from comment_review.reading.context import ReadingContext
from comment_review.reading.diagnostics import ReadFailure


def page_of(
    path: Path,
    rel: str | None = None,
    source: Source | None = None,
    *,
    reading_context: ReadingContext | None = None,
) -> Page | ReadFailure:
    """Build from the supplied snapshot, retaining available failure context.

    A supplied `reading_context` is one the caller derived or admitted
    (`flows.reading_context.admit_pages`), and the page records it as given.
    Without one, the installed reader's is derived here.
    """
    where = rel if rel is not None else path.as_posix()
    context = reading_context if reading_context is not None else context_for(path)
    if isinstance(context, ReadFailure):
        return LocatedReadFailure(context.diagnostics, where, None, None)
    acquired = source_of(path) if source is None else source
    if isinstance(acquired, ReadFailure):
        return LocatedReadFailure(acquired.diagnostics, where, None, None)
    page = page_for(
        path,
        acquired.text,
        rel=rel,
        sha=acquired.sha,
        reading=context,
    )
    if isinstance(page, ReadFailure):
        return LocatedReadFailure(
            page.diagnostics, where, context.language, acquired.text
        )
    return page
