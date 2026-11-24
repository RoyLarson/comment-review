"""Stage 7a: the sentences a write removes that end up at no place they were sent.

A sentence is read from a page's prose with its comment markers stripped, or
from a freeform file's text as it stands, and split at every line end and every
sentence end. So each one is at most one line, and an `Args:` line or a heading
is not joined to the text after it.

A removed sentence survives when it appears, whitespace-normalized, in its own
file as written, or when a move a closed proof agreed took it from its place
and it appears in the file the move's destination names. The match is at file
granularity: an address holds for one reading of a file, and the drafts are
read afresh. A sentence removed any other way -- a drop, a correct, a patch --
is listed, so the author can give it a home.

A freeform file has no reader, so its markers stay in its text.
"""

import re
from collections.abc import Sequence
from pathlib import Path

from comment_review.binder.page import Page
from comment_review.desk.proof.master_proof import MasterProof
from comment_review.desk.proof.move import Placement
from comment_review.flows.page_for import page_of
from comment_review.flows.source import source_of
from comment_review.machine.repo import Source, git_ls_files
from comment_review.reading.addresser import cue_of, unflatten
from comment_review.reading.comment import Fragment
from comment_review.reading.diagnostics import ReadFailure

_SENTENCE_END = re.compile(r"(?<=[.!?])\s+")


def lost_sentences(
    repo: Path, overlays: list[Path], proofs: Sequence[MasterProof] = ()
) -> list[tuple[str, str]] | None:
    """Each removed sentence found neither in its own file nor where a move sent it.

    Args:
        repo: the checkout as it stands before the write.
        overlays: directories holding drafts at their repo paths. A file in
            one that the checkout does not hold is not a draft and is skipped.
        proofs: the run's closed proofs, read for the moves they agreed.

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
        removed.extend((rel, s) for s in _lines(repo / rel, rel, before))

    sources: dict[str, tuple[Source, str] | None] = {}
    proses: dict[str, str] = {}

    def holds(rel: str, sentence: str) -> bool:
        """Whether `rel` as written holds `sentence`: raw text first, then prose.

        A file is parsed only for a sentence its raw text does not hold.
        """
        if rel not in written:
            return False
        if rel not in sources:
            got = _source(written[rel])
            sources[rel] = (got, _normal(got.text)) if got else None
        held = sources[rel]
        if held is None:
            return False
        source, raw = held
        if sentence in raw:
            return True
        if rel not in proses:
            proses[rel] = "\0".join(
                _normal(t) for t in _prose(written[rel], rel, source)
            )
        return sentence in proses[rel]

    moves = _moves(proofs)
    return list(
        dict.fromkeys(
            (rel, s)
            for rel, s in removed
            if not holds(rel, s)
            and not any(
                holds(to, s)
                for origin, base, to in moves
                if origin == rel and s in base
            )
        )
    )


def _moves(proofs: Sequence[MasterProof]) -> list[tuple[str, str, str]]:
    """Each agreed move: its origin's path and base text, its destination's path."""
    out = []
    for proof in proofs:
        paths = list(proof.page_readings)
        bases = {place.address: place.base for place in proof.places}
        for move in proof.moves:
            if move.placement is not Placement.AGREED:
                continue
            origin = unflatten(cue_of(move.origin).path, paths)
            to = unflatten(cue_of(move.destination).path, paths)
            if origin and to:
                out.append((origin, _normal(bases.get(move.origin, "")), to))
    return out


def _source(path: Path) -> Source | None:
    """The file's source, or None when it does not read as text."""
    got = source_of(path)
    return None if isinstance(got, ReadFailure) else got


def _prose(path: Path, rel: str, source: Source) -> list[str]:
    """The page's paragraph texts, or none where no reader reads it."""
    page = page_of(path, rel=rel, source=source)
    return [p.text for p in page.paragraphs if p.text] if isinstance(page, Page) else []


def _lines(path: Path, rel: str, source: Source) -> list[str]:
    """The file's prose split at line ends and sentence ends, each piece normalized."""
    page = page_of(path, rel=rel, source=source)
    if isinstance(page, Page):
        lines = [
            line
            for p in page.paragraphs
            if p.text
            for fragment in p.comment.fragments
            for line in _fragment_lines(fragment)
        ]
    else:
        lines = source.text.splitlines()
    return [s for line in lines for s in _SENTENCE_END.split(_normal(line)) if s]


def _fragment_lines(fragment: Fragment) -> list[str]:
    """The fragment's prose cut wherever its raw text breaks a line.

    `positions` maps each prose character to its raw one; where the two do not
    line up the prose is returned whole.
    """
    text, at, raw = fragment.text, fragment.positions, fragment.raw_text
    if len(at) != len(text):
        return [text]
    out, start, prev = [], 0, None
    for i, ch in enumerate(text):
        if ch.isspace():
            continue
        if prev is not None and "\n" in raw[at[prev] : at[i]]:
            out.append(text[start:i])
            start = i
        prev = i
    out.append(text[start:])
    return out


def _normal(text: str) -> str:
    """`text` with every whitespace run collapsed to one space."""
    return " ".join(text.split())
