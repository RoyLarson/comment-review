"""Questions asked of a binder BY ADDRESS: which paragraph sits at which place.

!! IT IS HERE BECAUSE IT READS PARAGRAPHS. `addresser.py` calls itself the leaf
that *"knows nothing about a paragraph"* and these five functions each take a
list of addressed things -- the rows, which are the binder's material. The
claim and the code disagreed until 2026-08-24, and the code was what moved.

!! THEY TAKE OBJECTS, NOT DICTS, SINCE 2026-08-31 -- `decision-log.md Process:
#67`. The signature was `list[dict]` and the two callers passed two different
dict shapes: a binder's rejoined rows, and `vars(paragraph)` at the page side.
! **`vars()` WAS THE TELL.** `commands/gather.py` carried a comment calling that
call *"a second statement of what a row is"* -- a `Paragraph` turned into a dict
for no reason but this signature.

!! AND THEY TAKE `Paragraph` ITSELF SINCE 2026-08-31 -- `decision-log.md Process:
#68`. For one day they took an `Addressed` PROTOCOL, because a `BinderRow` and a
`Paragraph` both had to satisfy one signature. **That row type is deleted**: a
binder holds pages, and both kinds of page hold paragraphs, so there is one type
here and no structural typing needed to bridge two.

! THE ADDRESSER STILL OWNS THE ADDRESS. Emitting a place, spelling it and
parsing it back are one subject and stay there; asking WHICH PARAGRAPH sits at
one is a different question, and it needs a binder to answer.

! THE NAME IS DESCRIPTIVE, NOT A TERM OF ART. It says what the module holds --
addresses, over a binder -- and no trade word has been proposed for it.
"""

from collections.abc import Sequence

from comment_review.reading.addresser import cue_of
from comment_review.reading.paragraph import Paragraph


def resolve(address: str, paragraphs: Sequence[Paragraph]) -> list[int]:
    """Which binder entries carry this address, as 1-based binder indices.

    !! THE INVERSE IS A LOOKUP, NOT ARITHMETIC. `bN` is "the gap after code line
    N", and which entries sit there is a fact the binder holds -- an empty
    interval, or a comment run filling the same gap, or both. Recomputing a line
    range from N would answer where the gap IS while the question asked which
    entries are THERE.

    ! Several entries can share one address and that is not an error: `c0` and
    `b0` are different places, but a comment run and the interval it occupies
    are the same place seen twice by a binder built before an edit.

    Args:
        address: `pkg:mod.py@b3` or `pkg:mod.py@c3`.
        paragraphs: the binder entries FOR THAT FILE, in binder order.

    Returns:
        The 1-based positions within `paragraphs`, in order. Empty when nothing
        carries it -- which a caller reports rather than treating as "none".
    """
    return [i for i, b in enumerate(paragraphs, 1) if stable(b) == address]


def series_of(paragraph: Paragraph) -> str:
    """Which series this paragraph's own address is in -- `a`, `b` or `c`.

    !! READ OFF THE ADDRESS, which is the one place the series is STATED. It was
    INFERRED from two other fields until 2026-08-20 -- a paragraph that declares
    is an `a`, one with a column is a `c`, everything else a `b` -- and the
    inference had no room for a fourth series. Front matter declares nothing and
    has no column, so it came back `b`, and `--anchor <module> --series b`
    answered with the file's own place.

    ! Inferring was meant to avoid a case per KIND, and reading the address
    avoids that too. It costs nothing: the caller holds a binder row, and an
    entry carrying no address is one no caller could cite anyway.

    !! A `d` IS NOT ASKED, AND ANSWERING IT WAS THE DEFECT. Leading is walked
    because the compositor has to set those lines back, and it names no place --
    Roy, 2026-08-24: *"Series d are walked because they have to be but they are
    not cues."* This defaulted its missing address to `""` and handed back `""`,
    a non-answer every caller then compared against a series letter. Every
    caller but one already tests `address` first; the one that did not is the
    reason this is stated rather than absorbed.

    Args:
        paragraph: a binder row that NAMES A PLACE.

    Raises:
        IndexError: when the row carries no address -- it is not a cue, and
            has no series to report.
    """
    return cue_of(paragraph.address).series


def stable(paragraph: Paragraph) -> str:
    """The place the gather STAMPED on this paragraph, or "" if it carries none.

    !! IT READS; `place` COMPUTES. One implementation, one caller that runs it
    -- `page_for`, which holds the file text and the finished paragraph list at
    once -- and everything downstream reads the result. Two computations that
    agree today is not the property wanted, because only one of them can be
    right tomorrow.

    ! "" means the binder predates the field. A caller REPORTS that rather than
    deriving a place from a binder that never had one.
    """
    return paragraph.address


def _by_path(paragraphs: Sequence[Paragraph]) -> dict[str, list[Paragraph]]:
    """Every paragraph grouped by the file it belongs to, in binder order.

    !! ONE PASS, NOT ONE PER FILE. Four sites built the set of paths and then
    filtered the WHOLE binder once for each of them -- O(files x paragraphs),
    on a structure that arrives already grouped because a binder is stacked one
    page at a time.

    ! The grouping is what every caller actually wanted; the set of paths is
    `.keys()` and the binder order inside a file is preserved, which is what
    `entry N` in a report counts.
    """
    out: dict[str, list[Paragraph]] = {}
    for b in paragraphs:
        out.setdefault(b.path, []).append(b)
    return out


def unaddressed(paragraphs: Sequence[Paragraph]) -> list[str]:
    """Which paragraphs carry NO address, described one per line.

    !! ONE SOURCE OF TRUTH, and the reason is the failure it prevents. Roy,
    2026-08-20: *"one source of truth, else something will parse that something
    else will fail."* Three callers ask this question -- `gather` before it
    writes, the collator before it certifies, and `addresser.py --check` -- and
    a second implementation of "is this addressed" is a second answer waiting to
    disagree with the first.

    !! IT IS ASKED AT BOTH ENDS ON PURPOSE. The gather refusing on EMIT catches
    its own degradation where it happens; the gate refusing on READ catches a
    file that reached it some other way -- a binder from an older version, one
    edited by hand, one written by a run that crashed. The collator takes a
    PATH and trusts what it parses, so nothing but this stands between a stale
    file and a certified review.

    !! WHAT IT COSTS TO SKIP: an unaddressed binder yields an EMPTY
    accountability set, so every paragraph is unaccounted and none is
    ACCOUNTABLE. Measured 2026-08-20 on a 5-paragraph binder with its addresses
    stripped and a report ruling on nothing: `0 findings ... over 0 prose
    paragraphs` and **"Every finding is admissible. Stage 5 may rule."** at exit
    0. The run reads as complete because there was nothing to be incomplete
    about.

    Args:
        paragraphs: the binder, as `gather` emits it.

    Returns:
        One sentence per unaddressed paragraph, naming its file and its lines.
        Empty when every paragraph carries an address.
    """
    out: list[str] = []
    for path, mine in sorted(_by_path(paragraphs).items()):
        for i, paragraph in enumerate(mine, 1):
            if not stable(paragraph):
                start = paragraph.original_start
                end = paragraph.original_end
                out.append(f"{path} entry {i}: lines {start}-{end}")
    return out
