"""Questions asked of a binder BY ADDRESS: which paragraph sits at which place.

`handed` is the set of rows a role is dealt and its coverage is counted over,
and `unaddressed` names the rows that carry no address; `gather` asks it of
`Binder.paragraphs`, which holds none.

!! IT IS HERE BECAUSE IT READS PARAGRAPHS. `addresser.py` says it *"still knows
nothing about prose"*, and four of these six functions take a list of addressed
things and two take one -- the rows, which are the binder's material.

! THE ADDRESSER STILL OWNS THE ADDRESS. Emitting a place, spelling it and
parsing it back are one subject and stay there; asking WHICH PARAGRAPH sits at
one is a different question, and it needs a binder to answer.

! THE NAME IS DESCRIPTIVE, NOT A TERM OF ART. It says what the module holds --
addresses, over a binder -- and no trade word has been proposed for it.
"""

from collections.abc import Sequence

from comment_review.reading.addresser import COVERS, cue_of
from comment_review.reading.paragraph import Paragraph


def resolve(address: str, paragraphs: Sequence[Paragraph]) -> list[int]:
    """Which binder entries carry this address, as 1-based binder indices.

    The inverse is a lookup, not arithmetic. `bN` is "the gap after code line
    N", and which entry sits there is a fact the binder holds -- an empty
    interval or a comment run filling that gap. Recomputing a line range from N
    would answer where the gap is while the question asked which entry is there.

    No two entries share an address: `page_of` refuses a page in which two
    paragraphs hold one (`held_twice`), and an empty place is emitted only where
    no filled paragraph stands.

    Args:
        address: `pkg:mod.py@b3` or `pkg:mod.py@c3`.
        paragraphs: one file's paragraphs, in order -- `flows.addresses.lines_of`,
            the only caller, passes a page read from disk.

    Returns:
        The 1-based positions within `paragraphs`, in order. Empty when nothing
        carries it -- which a caller reports rather than treating as "none".
    """
    return [i for i, b in enumerate(paragraphs, 1) if stable(b) == address]


def series_of(paragraph: Paragraph) -> str:
    """Which series this paragraph's own address is in -- `a`, `b`, `c` or `f`.

    Read off the address, which is the one place the series is stated.

    Inferring the series from other fields was meant to avoid a case per kind,
    and reading the address avoids that too. It costs nothing: the caller holds
    a binder row, and an entry carrying no address is one no caller could cite
    anyway.

    A `d` is not asked, and answering it was the defect. Leading is walked
    because the compositor has to set those lines back, and it names no place --
    Roy, 2026-08-24: *"Series d are walked because they have to be but they are
    not cues."* Its one caller, `handed`, tests `address` first.

    Args:
        paragraph: a binder row that NAMES A PLACE.

    Raises:
        IndexError: when the row carries no address -- it is not a cue, and
            has no series to report.
    """
    return cue_of(paragraph.address).series


def stable(paragraph: Paragraph) -> str:
    """The place the gather STAMPED on this paragraph, or "" if it carries none.

    "" means the paragraph is leading, which takes no address: a page read
    from disk carries leading, and `Binder.paragraphs` drops it. A caller
    reports that rather than deriving a place from a paragraph that has none.
    """
    return paragraph.address


def _by_path(paragraphs: Sequence[Paragraph]) -> dict[str, list[Paragraph]]:
    """Every paragraph grouped by the file it belongs to, in binder order.

    One pass, not one per file.

    The grouping is what its one caller, `unaddressed`, wants; the set of
    paths is `.keys()` and the binder order inside a file is preserved, which is
    what `entry N` in a report counts.
    """
    out: dict[str, list[Paragraph]] = {}
    for b in paragraphs:
        out.setdefault(b.path, []).append(b)
    return out


def handed(paragraphs: Sequence[Paragraph]) -> list[Paragraph]:
    """The paragraphs a role is handed: addressed, and not the file's own matter.

    One definition, three readers. `flows.distribute.seed` builds a role's
    slots from this, `flows.distribute.assigned_binder` cuts a stage's binder
    with it, and `flows.verify.required_places` names the places a returned
    copy's coverage is counted against.

    ! The `f` series -- a licence header, a shebang, an index -- states no
    constraint the code could contradict, so no role rules on it and the brief
    says a role will not be shown one. It keeps its address in the binder, so
    a `move` may still cite it.

    Args:
        paragraphs: a binder's or a page's rows.

    Returns:
        The rows a role is accountable for, in the order given.
    """
    return [b for b in paragraphs if b.address and series_of(b) != COVERS]


def unaddressed(paragraphs: Sequence[Paragraph]) -> list[str]:
    """Which paragraphs carry NO address, described one per line.

    `gather` runs it over `Binder.paragraphs`, which already drops every row
    without an address, so there it finds none. A paragraph with no address
    cannot be cited, so a review over it would rule on nothing and report itself
    complete.
    """
    out: list[str] = []
    for path, mine in sorted(_by_path(paragraphs).items()):
        for i, paragraph in enumerate(mine, 1):
            if not stable(paragraph):
                start = paragraph.original_start
                end = paragraph.original_end
                out.append(f"{path} entry {i}: lines {start}-{end}")
    return out
