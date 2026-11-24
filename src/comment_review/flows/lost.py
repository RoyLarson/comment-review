"""Stage 7a: the sentences a write removes that end up in no file.

A sentence is read from a page's prose with its comment markers stripped and
its wrapped lines joined, or from a freeform file's text as it stands, and the
text is split on sentence ends. A removed sentence survives when it appears,
whitespace-normalized, in any file of the tree as written: the tracked files,
with each overlay's drafts laid over them at their repo paths.

A freeform file has no reader, so its markers stay in its text. A sentence
wrapped across its comment lines survives only where it is wrapped the same
way, and one moved into such a file and rewrapped is listed as lost.
"""

import re
from pathlib import Path

from comment_review.binder.page import Page
from comment_review.flows.page_for import page_of
from comment_review.flows.source import source_of
from comment_review.machine.repo import Source, git_ls_files
from comment_review.reading.diagnostics import ReadFailure

_SENTENCE_END = re.compile(r"(?<=[.!?])\s+")


def lost_sentences(repo: Path, overlays: list[Path]) -> list[tuple[str, str]] | None:
    """Each removed sentence no file of the tree as written holds.

    Args:
        repo: the checkout as it stands before the write.
        overlays: directories holding drafts at their repo paths. A file in
            one that the checkout does not hold is not a draft and is skipped.

    Returns:
        `(path, sentence)` pairs in path order, each sentence normalized; or
        None when git cannot list the tracked files.
    """
    tracked = git_ls_files(repo)
    if tracked is None:
        return None
    written = {rel: repo / rel for rel in tracked}
    changed = []
    for overlay in overlays:
        for path in sorted(p for p in overlay.rglob("*") if p.is_file()):
            rel = path.relative_to(overlay).as_posix()
            if (repo / rel).is_file():
                written[rel] = path
                changed.append(rel)

    removed = []
    for rel in sorted(changed):
        before = _source(repo / rel)
        after = _source(written[rel])
        if before is None or (after is not None and before.text == after.text):
            continue
        for chunk in _prose(repo / rel, rel, before):
            removed.extend((rel, s) for s in _sentences(chunk))

    # Raw text first; a file's prose is read only for sentences raw text misses.
    sources = {rel: _source(path) for rel, path in written.items()}
    raw = "\0".join(_normal(s.text) for s in sources.values() if s is not None)
    removed = [(rel, s) for rel, s in removed if s not in raw]
    if removed:
        prose = "\0".join(
            _normal(chunk)
            for rel, source in sources.items()
            if source is not None
            for chunk in _prose(written[rel], rel, source, raw_fallback=False)
        )
        removed = [(rel, s) for rel, s in removed if s not in prose]
    return list(dict.fromkeys(removed))


def _source(path: Path) -> Source | None:
    """The file's source, or None when it does not read as text."""
    got = source_of(path)
    return None if isinstance(got, ReadFailure) else got


def _prose(
    path: Path, rel: str, source: Source, *, raw_fallback: bool = True
) -> list[str]:
    """The page's paragraph texts, or the whole text where no reader reads it."""
    page = page_of(path, rel=rel, source=source)
    if isinstance(page, Page):
        return [p.text for p in page.paragraphs if p.text]
    return [source.text] if raw_fallback else []


def _sentences(text: str) -> list[str]:
    """`text` normalized and split on sentence ends."""
    return [s for s in _SENTENCE_END.split(_normal(text)) if s]


def _normal(text: str) -> str:
    """`text` with every whitespace run collapsed to one space."""
    return " ".join(text.split())
