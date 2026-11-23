"""Derive the installed reading context, and admit each page's identity once.

context_for(path)        the reading the installed reader gives a path
admit_pages(*sources)    the identity table of one load, or why it will not admit
Unadmitted               one such reason, with the source it names as data
admit_proof(proof)       a master proof's pages, admitted through `admit_pages`
"""

from collections.abc import Iterable
from pathlib import Path
from typing import NamedTuple, Protocol

from comment_review.desk.proof.master_proof import MasterProof
from comment_review.reading.context import Imprint, ReadingContext, resolve_context
from comment_review.reading.diagnostics import ReadDiagnostic, ReadFailure, ReadStage
from comment_review.reading.language import INSTALLED_REGISTRY
from comment_review.reading.readers import reader_for
from comment_review.reading.registry import LanguageRegistry


class Imprinted(Protocol):
    """What `admit_pages` reads of a page, sheet or schedule."""

    @property
    def path(self) -> str:
        """The page's real relative path."""
        ...

    @property
    def sha(self) -> str:
        """The sha of the source the page was read from."""
        ...

    @property
    def reading(self) -> ReadingContext:
        """The reading the page was read under."""
        ...


class Unadmitted(NamedTuple):
    """One reason a page identity will not admit, and the source that claimed it.

    `source` is the label the caller gave the claimant's records, so the caller
    routes the reason by it; `text` is the reason as printed, and opens with
    the source and the path.
    """

    source: str
    text: str


class _Recorded(NamedTuple):
    """One row of a master proof's `page_readings`, with the sha it records."""

    path: str
    sha: str
    reading: ReadingContext


def admit_pages(
    *sources: tuple[str, Iterable[Imprinted]],
) -> tuple[dict[str, Imprint], list[Unadmitted]]:
    """The identity table of one load: real path -> the sha and reading it was read at.

    Identity is `(sha, reading)` per path. The sources are taken in the order
    given, which is the entry point's order of authority: the first claimant
    of a path is its reference. That claimant's reading is compared once with
    the installed reader's, and each later claim on the path is compared once
    with the first. Nothing here reads a page or the checkout.

    Args:
        sources: `(label, records)` pairs. The label names the artifact in a
            reason.

    Returns:
        `(table, [])`, or `({}, reasons)`: one `Unadmitted` per source and
        path that will not admit. Every reason's text ends in `regather`.
    """
    table: dict[str, Imprint] = {}
    first: dict[str, str] = {}
    refused: set[str] = set()
    reasons: list[Unadmitted] = []
    for label, records in sources:
        for record in records:
            path, reading = record.path, record.reading
            if path in refused:
                continue
            if not isinstance(reading, ReadingContext):
                reasons.append(
                    Unadmitted(
                        label, f"{label}: {path}: reading context is missing; regather"
                    )
                )
                continue
            claim = Imprint(record.sha, reading)
            if path in table:
                held = table[path]
                if claim == held:
                    continue
                differs = "reading context" if reading != held.reading else "sha"
                reasons.append(
                    Unadmitted(
                        label,
                        f"{label}: {path}: {differs} disagrees with {first[path]};"
                        " regather",
                    )
                )
                continue
            current = context_for(Path(path))
            if isinstance(current, ReadFailure):
                reasons.extend(
                    Unadmitted(
                        label, f"{label}: {path}: {diagnostic.message}; regather"
                    )
                    for diagnostic in current.diagnostics
                )
            elif current != reading:
                reasons.append(
                    Unadmitted(
                        label,
                        f"{label}: {path}: reading context differs from the installed"
                        " reader's; regather to save a fresh reading context",
                    )
                )
            else:
                table[path], first[path] = claim, label
                continue
            # Refused once: a later claim on the path is not asked again.
            refused.add(path)
    return ({}, reasons) if reasons else (table, [])


def admit_proof(
    proof: MasterProof, where: str = "master_proof"
) -> tuple[dict[str, Imprint], list[Unadmitted]]:
    """A master proof's pages: its tables first, then its sheets, through `admit_pages`.

    A table row's sha is the one `page_shas` records for the path, or for a
    page a sheet holds, the sheet's.
    """
    sheets = [sheet for copy in proof.edit_copies for sheet in copy.sheets]
    shas = {sheet.path: sheet.sha for sheet in sheets}
    shas.update(proof.page_shas)
    tables = [
        _Recorded(path, shas.get(path, ""), reading)
        for path, reading in proof.page_readings.items()
    ]
    return admit_pages((where, tables), (f"{where} sheets", sheets))


def context_for(
    path: Path,
    *,
    registry: LanguageRegistry = INSTALLED_REGISTRY,
) -> ReadingContext | ReadFailure:
    """Derive the current context from the installed definition and reader."""
    selected = reader_for(path, registry)
    if isinstance(selected, ReadFailure):
        return selected
    if selected is None:
        return ReadFailure(
            (
                ReadDiagnostic(
                    ReadStage.SELECT,
                    "unsupported-language",
                    "No installed code reader for this suffix",
                ),
            )
        )
    return resolve_context(selected[0])
