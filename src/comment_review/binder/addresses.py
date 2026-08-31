"""Questions asked of a census BY ADDRESS: which paragraph sits at which place.

!! IT IS HERE BECAUSE IT READS PARAGRAPHS. `addresser.py` calls itself the leaf
that *"knows nothing about a paragraph"* and these six functions each take a
list of addressed things -- census rows, which are the binder's material. The
claim and the code disagreed until 2026-08-24, and the code was what moved.

!! THEY TAKE OBJECTS, NOT DICTS, SINCE 2026-08-31 -- `decision-log.md Process:
#67`. The signature was `list[dict]` and the two callers passed two different
dict shapes: a binder's rejoined rows, and `vars(paragraph)` at the page side.
! **`vars()` WAS THE TELL.** `commands/census.py` carried a comment calling that
call *"a second statement of what a row is"* -- a `Paragraph` turned into a dict
for no reason but this signature.

!! AND THEY TAKE `Paragraph` ITSELF SINCE 2026-08-31 -- `decision-log.md Process:
#68`. For one day they took an `Addressed` PROTOCOL, because a `BinderRow` and a
`Paragraph` both had to satisfy one signature. **That row type is deleted**: a
binder holds pages, and both kinds of page hold paragraphs, so there is one type
here and no structural typing needed to bridge two.

! THE ADDRESSER STILL OWNS THE ADDRESS. Emitting a place, spelling it and
parsing it back are one subject and stay there; asking WHICH PARAGRAPH sits at
one is a different question, and it needs a census to answer.

! THE NAME IS DESCRIPTIVE, NOT A TERM OF ART. It says what the module holds --
addresses, over a census -- and no trade word has been proposed for it.
"""

from collections.abc import Sequence

from comment_review.reading.addresser import cue_of
from comment_review.reading.lexer import Paragraph


def resolve(address: str, paragraphs: Sequence[Paragraph]) -> list[int]:
    """Which census entries carry this address, as 1-based census indices.

    !! THE INVERSE IS A LOOKUP, NOT ARITHMETIC. `bN` is "the gap after code line
    N", and which entries sit there is a fact the census holds -- an empty
    interval, or a comment run filling the same gap, or both. Recomputing a line
    range from N would answer where the gap IS while the question asked which
    entries are THERE.

    ! Several entries can share one address and that is not an error: `c0` and
    `b0` are different places, but a comment run and the interval it occupies
    are the same place seen twice by a census built before an edit.

    Args:
        address: `pkg:mod.py@b3` or `pkg:mod.py@c3`.
        paragraphs: the census entries FOR THAT FILE, in census order.

    Returns:
        The 1-based positions within `paragraphs`, in order. Empty when nothing
        carries it -- which a caller reports rather than treating as "none".
    """
    return [i for i, b in enumerate(paragraphs, 1) if stable(b) == address]


def for_anchor(
    anchor: str, series: str, paragraphs: Sequence[Paragraph]
) -> list[Paragraph]:
    """The paragraphs of one SERIES belonging to one anchor -- `go`'s `c`, say.

    !! AN ANCHOR OWNS A PLACE IN EVERY SERIES, and asking for one by POSITION
    breaks the moment a language puts it elsewhere. Python's docstring sits
    AFTER its `def` and Rust's `///` BEFORE its `fn`, so "the paragraph above the
    declaration" names the doc in one language and the comment above it in the
    other. This asks the CENSUS, which parsed the file, instead of counting.

    The three, for a declaration:

      a   its documentation -- the docstring, or the place one would go
      c   the room BESIDE its opening line -- a trailing comment, or the place
      b   the gap ABOVE its opening line -- a comment run, or the place

    ! The MODULE has no line to open on, so it has an `a` and an `f` -- its
    own matter, bounded by nothing, which is where a licence header or a
    shebang sits (`f0`, not `b0`). It has neither `b` nor `c`: `cue()` steps
    past the module without emitting either -- `addresser.py`, "`b` AND `c`
    SKIP THE MODULE ENTIRELY".

    ! It returns a LIST because a census may carry none -- a language whose
    tier resolves no anchors at all -- and the caller reports that rather than
    receiving a guess. More than one is a census defect `--check` reports.

    Args:
        anchor: the LINE OF CODE, as the census stamped it -- `def f():`, not `f`.
        series: `a`, `b` or `c`.
        paragraphs: the census entries. Pass the FULL census; a filtered one is
            missing exactly the empty places this is most often asked for.

    Returns:
        The matching entries, in census order.
    """
    mine = [b for b in paragraphs if b.anchor == anchor]
    # !! EVERY SERIES CARRIES THE SAME SPELLING: THE LINE OF CODE. An `a`, the
    # `b` above it and the `c` beside it all answer to `def f():`, never to `f`
    # -- the name is not carried at all. It was two spellings until 2026-08-19,
    # which routed `b`/`c` through `anchor_line` that only an `a` filled, so asking
    # by the LINE found nothing: `--anchor 'def f():' --series c` answered "no
    # `c` place" on a census holding exactly that one.
    #
    # ! The paragraph's OWN series decides which places answer: an `a` declares,
    # a `c` has a column, a `b` has neither. No second field, no inference from
    # kind.
    direct = [b for b in mine if series_of(b) == series]
    # !! THIS IS THE WHOLE ANSWER, since 2026-08-25. A fallback stood below it,
    # resolving by an `anchor_line` field carried on `mine` -- dead since the
    # eleven-field row cut (`e56bea9`) dropped that field: no row carries it,
    # so the fallback's own `at` was always `0` and every branch under it but
    # one was unreachable. MEASURED: `for_anchor('<module>', GAP, rows)`
    # returned `[]` through that dead fallback, reading as an answer where
    # none was computed. `[]` IS the true answer here, not a coincidence --
    # `cue()` never emits a `b` or `c` place for the module at all
    # (`addresser.py`, "`b` AND `c` SKIP THE MODULE ENTIRELY"), so `direct`
    # already covers every place a census can name; nothing was left for a
    # fallback to resolve. Removed rather than reintroduced the field,
    # matching `521e327`'s DECLARED short-circuit. A resolver reading the
    # PAGE instead of a row is the deferred redesign,
    # `TODO/an-empty-place-is-not-citable.md` -- this is not that; it is
    # deleting a branch that could not fire.
    return direct


def series_of(paragraph: Paragraph) -> str:
    """Which series this paragraph's own address is in -- `a`, `b` or `c`.

    !! READ OFF THE ADDRESS, which is the one place the series is STATED. It was
    INFERRED from two other fields until 2026-08-20 -- a paragraph that declares
    is an `a`, one with a column is a `c`, everything else a `b` -- and the
    inference had no room for a fourth series. Front matter declares nothing and
    has no column, so it came back `b`, and `--anchor <module> --series b`
    answered with the file's own place.

    ! Inferring was meant to avoid a case per KIND, and reading the address
    avoids that too. It costs nothing: `for_anchor` is given a census, and an
    entry carrying no address is one no caller could cite anyway.

    !! A `d` IS NOT ASKED, AND ANSWERING IT WAS THE DEFECT. Leading is walked
    because the compositor has to set those lines back, and it names no place --
    Roy, 2026-08-24: *"Series d are walked because they have to be but they are
    not cues."* This defaulted its missing address to `""` and handed back `""`,
    a non-answer every caller then compared against a series letter. Every
    caller but one already tests `address` first; the one that did not is the
    reason this is stated rather than absorbed.

    Args:
        paragraph: a census row that NAMES A PLACE.

    Raises:
        IndexError: when the row carries no address -- it is not a cue, and
            has no series to report.
    """
    return cue_of(paragraph.address).series


def stable(paragraph: Paragraph) -> str:
    """The place the census STAMPED on this paragraph, or "" if it carries none.

    !! IT READS; `place` COMPUTES. One implementation, one caller that runs it
    -- `page_for`, which holds the file text and the finished paragraph list at
    once -- and everything downstream reads the result. Two computations that
    agree today is not the property wanted, because only one of them can be
    right tomorrow.

    ! "" means the census predates the field. A caller REPORTS that rather than
    deriving a place from a census that never had one.
    """
    return paragraph.address


def _by_path(paragraphs: Sequence[Paragraph]) -> dict[str, list[Paragraph]]:
    """Every paragraph grouped by the file it belongs to, in census order.

    !! ONE PASS, NOT ONE PER FILE. Four sites built the set of paths and then
    filtered the WHOLE census once for each of them -- O(files x paragraphs),
    on a structure that arrives already grouped because a census is stacked one
    page at a time.

    ! The grouping is what every caller actually wanted; the set of paths is
    `.keys()` and the census order inside a file is preserved, which is what
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
    else will fail."* Three callers ask this question -- `census.py` before it
    writes, the collator before it certifies, and `addresser.py --check` -- and
    a second implementation of "is this addressed" is a second answer waiting to
    disagree with the first.

    !! IT IS ASKED AT BOTH ENDS ON PURPOSE. The census refusing on EMIT catches
    its own degradation where it happens; the gate refusing on READ catches a
    file that reached it some other way -- a census from an older version, one
    edited by hand, one written by a run that crashed. The collator takes a
    PATH and trusts what it parses, so nothing but this stands between a stale
    file and a certified review.

    !! WHAT IT COSTS TO SKIP: an unaddressed census yields an EMPTY
    accountability set, so every paragraph is unaccounted and none is
    ACCOUNTABLE. Measured 2026-08-20 on a 5-paragraph census with its addresses
    stripped and a report ruling on nothing: `0 findings ... over 0 prose
    paragraphs` and **"Every finding is admissible. Stage 5 may rule."** at exit
    0. The run reads as complete because there was nothing to be incomplete
    about.

    Args:
        paragraphs: the census, as `census.py --json` emits it.

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
