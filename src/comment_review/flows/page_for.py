"""Acquire a source snapshot and admit it as a complete page."""

from collections.abc import Mapping
from dataclasses import replace
from pathlib import Path

from comment_review.binder.page import Page, page_for
from comment_review.flows.read_diagnostics import (
    ContextAdmissionFailure,
    LocatedReadFailure,
)
from comment_review.flows.reading_context import context_for
from comment_review.flows.source import source_of
from comment_review.machine.repo import Source
from comment_review.reading.context import ReadingContext
from comment_review.reading.diagnostics import ReadDiagnostic, ReadFailure, ReadStage
from comment_review.reading.lexer import language_for


def page_of(
    path: Path,
    rel: str | None = None,
    source: Source | None = None,
    *,
    reading_context: ReadingContext | None = None,
    settings: Mapping[str, str] | None = None,
) -> Page | ReadFailure:
    """Build from the supplied snapshot, retaining available failure context."""
    where = rel if rel is not None else path.as_posix()
    context = context_for(
        path,
        settings
        if settings is not None
        else dict(reading_context.settings)
        if reading_context is not None
        else {},
    )
    if isinstance(context, ReadFailure):
        if reading_context is not None:
            return ContextAdmissionFailure(
                tuple(
                    replace(diagnostic, message=f"{diagnostic.message}; regather")
                    for diagnostic in context.diagnostics
                ),
                where,
                reading_context.language,
                None,
            )
        return LocatedReadFailure(context.diagnostics, where, None, None)
    if reading_context is not None and context != reading_context:
        return ContextAdmissionFailure(
            (
                ReadDiagnostic(
                    ReadStage.SELECT,
                    "reading-context-mismatch",
                    "Supplied reading context differs from installed metadata; "
                    "regather",
                ),
            ),
            where,
            context.language,
            None,
        )
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
    page = page_for(
        path, acquired.text, lang, rel=rel, sha=acquired.sha, reading=context
    )
    if isinstance(page, ReadFailure):
        return LocatedReadFailure(page.diagnostics, where, lang.name, acquired.text)
    return page
