"""Admit each original and its draft as pages before comparing executable code.

The original is the file as the working tree holds it, and the draft is the
file at the same repo path under the drafts root. Neither side is read from
git, so the work being proven need not be committed.

A docstring may appear or disappear only at an `a` place the imprimatur
`proof` wrote names for that page, which is what stage 7a's proof allowed.
"""

from collections.abc import Collection, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from comment_review.binder.page import Page
from comment_review.flows.page_for import page_of
from comment_review.flows.proof_setter import documented_line
from comment_review.flows.read_diagnostics import format_failure
from comment_review.flows.reading_context import context_for
from comment_review.flows.source import source_of
from comment_review.reading.diagnostics import ReadFailure
from comment_review.reading.language import INSTALLED_REGISTRY
from comment_review.reading.proof import UNIDENTIFIED_OWNER


@dataclass(frozen=True)
class ProofReport:
    """Complete per-path messages and the counts used by the console policy."""

    messages: tuple[str, ...]
    failures: int
    freeform: int = 0


def _documented(
    before: Page, after: Page, cues: Collection[str]
) -> list[tuple[int | None, int | None]] | None:
    """Each approved `a` place's anchor line before and after, for `preserved`.

    None when either page carries no such place.
    """
    pairs = []
    for cue in sorted(cues):
        was, now = documented_line(before, cue), documented_line(after, cue)
        if was is None or now is None:
            return None
        pairs.append((was[0], now[0]))
    return pairs


def run(
    repo: Path,
    drafts: Path,
    paths: Sequence[Path],
    *,
    approved: Mapping[str, Collection[str]],
) -> ProofReport:
    """Prove each draft's code unchanged from the original it was drafted from.

    Args:
        repo: the repository root each path is named relative to; it holds
            the originals.
        drafts: the root holding each draft at its repo path.
        paths: the pages and freeform files to prove, in the repository.
        approved: repo path -> the cues of the `a` places whose docstrings
            may appear or disappear, as `flows.imprimatur` records them. A
            page it does not name may change no docstring's presence.
    """
    repo = repo.resolve()
    messages: list[str] = []
    failures = freeform = 0
    for raw in paths:
        target = raw.resolve()
        try:
            rel = target.relative_to(repo).as_posix()
        except ValueError:
            messages.append(f"FAIL      {raw}: outside --repo")
            failures += 1
            continue
        if INSTALLED_REGISTRY.is_freeform(target):
            messages.append(
                f"UNCHECKED  {rel}: no reader -- formatter and compiler are the check"
            )
            freeform += 1
            continue
        context = context_for(target)
        if isinstance(context, ReadFailure):
            messages.append(f"FAIL      {format_failure(context, path=rel)}")
            failures += 1
            continue
        before = source_of(target)
        if isinstance(before, ReadFailure):
            messages.append(f"FAIL      original: {format_failure(before, path=rel)}")
            failures += 1
            continue
        after = source_of(drafts / rel)
        if isinstance(after, ReadFailure):
            messages.append(f"FAIL      draft: {format_failure(after, path=rel)}")
            failures += 1
            continue
        page_b = page_of(target, rel=rel, source=before, reading_context=context)
        page_a = page_of(target, rel=rel, source=after, reading_context=context)
        failed = False
        for side, page in (("original", page_b), ("draft", page_a)):
            if isinstance(page, ReadFailure):
                messages.append(f"FAIL      {side}: {format_failure(page, path=rel)}")
                failed = True
        if failed:
            failures += 1
            continue
        assert isinstance(page_b, Page) and isinstance(page_a, Page)
        proof = page_b.read.proof
        documented = _documented(page_b, page_a, approved.get(rel, ()))
        result = (
            page_b.read.preserved(page_a.read, documented=documented)
            if proof == page_a.read.proof and documented is not None
            else None
        )
        if documented is None or (
            result is not None
            and any(d.code == UNIDENTIFIED_OWNER for d in result.diagnostics)
        ):
            messages.append(
                f"FAIL      {rel}: an approved docstring's declaration is not"
                " identified"
            )
            failures += 1
        elif result is None:
            messages.append(f"FAIL      {rel}: proof kind changed")
            failures += 1
        elif result.unchanged:
            messages.append(f"PROVEN    {rel}: reads the same ({proof})")
        elif result.unprovable:
            messages.append(
                f"UNPROVABLE {rel}: prose could not be separated from code"
                " -- sameness NOT shown"
            )
            failures += 1
        else:
            messages.append(f"FAIL      {rel}: executable code DIFFERS ({proof} proof)")
            messages.append(format_failure(ReadFailure(result.diagnostics), path=rel))
            failures += 1
    return ProofReport(tuple(messages), failures, freeform)
