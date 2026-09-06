"""Stage 3 as a step: what the concordance settles about what a gather carried.

`concordance.annotate` answers one paragraph at a time -- a cited path, a
backticked name, a counted claim. The repeated-literal pass cannot: a number is
a hand-copied value only when it is written in prose at two PLACES, so it reads
the whole set. This step runs both, and it is the one caller of `annotate`;
`tests/test_gather.py` reads the tree to say so.

! `TODO/census-should-be-a-chain-of-producers.md` T1. The command ran both
inline until this landed, which left stage 3 with no name a flow could call.
"""

from collections import Counter, defaultdict
from collections.abc import Sequence
from pathlib import Path

from comment_review.concordance.annotate import annotate, prose_numbers
from comment_review.reading.paragraph import Paragraph


def annotations_for(
    paragraphs: Sequence[Paragraph], known: set[str], paths: set[str], repo: Path
) -> None:
    """Attach every annotation stage 3 can settle, onto the paragraphs themselves.

    ! IN PLACE, AS `annotate` IS. A paragraph carries its own `annotations` and
    `notes`, and the binder reads them there; a returned copy
    would be a second place for the same facts.

    Args:
        paragraphs: what the gather carried, across every page in scope. The
            repeated-literal pass reads across them, so a page at a time would
            miss the pair it looks for.
        known: every symbol the name corpus defines.
        paths: every tracked path, as the repo names it.
        repo: the root a cited path resolves against.
    """
    for b in paragraphs:
        annotate(b, known, paths, repo)
    _repeated_literals(paragraphs)


def _repeated_literals(paragraphs: Sequence[Paragraph]) -> None:
    """A number written in prose at two places is a hand-copied value.

    The copies drift; one written once is just a number. Each paragraph holding
    the pair is annotated and told where the others are, three at most.
    """
    seen: Counter[str] = Counter()
    where: dict[str, set[str]] = defaultdict(set)
    for b in paragraphs:
        for n in prose_numbers(b.text, b.raw_lines):
            seen[n] += 1
            where[n].add(f"{b.path}:{b.start}")
    for b in paragraphs:
        for n in prose_numbers(b.text, b.raw_lines):
            if seen[n] > 1 and len(where[n]) > 1:
                b.annotations.add("repeated-literal")
                others = sorted(where[n] - {f"{b.path}:{b.start}"})[:3]
                b.notes.append(f"{n} also in prose at {', '.join(others)}")
