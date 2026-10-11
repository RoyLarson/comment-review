"""Acquire, admit, and set one held source snapshot."""

from dataclasses import dataclass
from pathlib import Path

from comment_review import exceptions
from comment_review.flows.page_for import page_of
from comment_review.flows.read_diagnostics import LocatedReadFailure
from comment_review.flows.source import source_of
from comment_review.reading.diagnostics import ReadDiagnostic, ReadFailure, ReadStage
from comment_review.reading.language import language_for
from comment_review.results import compositor


@dataclass(frozen=True)
class RoundTrip:
    """The exact input and the text set from its page."""

    original: str
    rendered: str


def round_trip(path: Path) -> RoundTrip | ReadFailure:
    """Set one snapshot, retaining known context for expected refusals."""
    source = source_of(path)
    if isinstance(source, ReadFailure):
        return LocatedReadFailure(source.diagnostics, path.as_posix(), None, None)
    page = page_of(path, source=source)
    if isinstance(page, ReadFailure):
        return page
    try:
        rendered = compositor.set_page(page)
    except exceptions.Refused as error:
        language = language_for(path)
        return LocatedReadFailure(
            (ReadDiagnostic(ReadStage.PLACE, "unsupported-placement", str(error)),),
            path.as_posix(),
            language.name if language is not None else None,
            source.text,
        )
    return RoundTrip(source.text, rendered)
