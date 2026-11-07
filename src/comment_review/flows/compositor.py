"""Acquire, admit, and set one held source snapshot."""

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from comment_review import exceptions
from comment_review.flows.page_for import page_of
from comment_review.flows.read_diagnostics import LocatedReadFailure
from comment_review.flows.reading_context import context_for
from comment_review.flows.source import source_of
from comment_review.reading.context import ReadingContext
from comment_review.reading.diagnostics import ReadDiagnostic, ReadFailure, ReadStage
from comment_review.results import compositor


@dataclass(frozen=True)
class RoundTrip:
    """The exact input and the text set from its page."""

    original: str
    rendered: str
    reading_context: ReadingContext | None = None


def round_trip(
    path: Path, *, settings: Mapping[str, str] | None = None
) -> RoundTrip | ReadFailure:
    """Set one snapshot, retaining known context for expected refusals."""
    context = context_for(path, settings if settings is not None else {})
    if isinstance(context, ReadFailure):
        return LocatedReadFailure(context.diagnostics, path.as_posix(), None, None)
    source = source_of(path)
    if isinstance(source, ReadFailure):
        return LocatedReadFailure(source.diagnostics, path.as_posix(), None, None)
    page = page_of(path, source=source, reading_context=context)
    if isinstance(page, ReadFailure):
        return page
    try:
        rendered = compositor.set_page(page)
    except exceptions.Refused as error:
        return LocatedReadFailure(
            (ReadDiagnostic(ReadStage.PLACE, "unsupported-placement", str(error)),),
            path.as_posix(),
            page.reading.language,
            source.text,
        )
    return RoundTrip(source.text, rendered, context)
