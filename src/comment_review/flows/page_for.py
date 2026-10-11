"""Acquire a source snapshot and admit it as a complete page."""

from pathlib import Path

from comment_review.binder.page import Page, page_for
from comment_review.flows.read_diagnostics import LocatedReadFailure
from comment_review.flows.source import source_of
from comment_review.machine.repo import Source
from comment_review.reading.diagnostics import ReadDiagnostic, ReadFailure, ReadStage
from comment_review.reading.lexer import language_for


def page_of(
    path: Path, rel: str | None = None, source: Source | None = None
) -> Page | ReadFailure:
    """Build from the supplied snapshot, retaining available failure context."""
    where = rel if rel is not None else path.as_posix()
    acquired = source_of(path) if source is None else source
    if isinstance(acquired, ReadFailure):
        return LocatedReadFailure(acquired.diagnostics, where, None, None)
    lang = language_for(path)
    if lang is None:
        return LocatedReadFailure(
            (
                ReadDiagnostic(
                    ReadStage.SELECT,
                    "unsupported-language",
                    "no language record for its suffix",
                ),
            ),
            where,
            None,
            acquired.text,
        )
    page = page_for(path, acquired.text, lang, rel=rel, sha=acquired.sha)
    if isinstance(page, ReadFailure):
        return LocatedReadFailure(page.diagnostics, where, lang.name, acquired.text)
    return page
