"""Questions asked of a census BY ADDRESS: which paragraph, and which owe one.

!! IT IS HERE BECAUSE IT READS PARAGRAPHS. `addresser.py` calls itself the leaf
that *"knows nothing about a paragraph"* and these seven functions each take
`paragraphs: list[dict]` -- census rows, which are the binder's material. The
claim and the code disagreed until 2026-08-24, and the code was what moved.

! THE ADDRESSER STILL OWNS THE ADDRESS. Emitting a place, spelling it and
parsing it back are one subject and stay there; asking WHICH PARAGRAPH sits at
one is a different question, and it needs a census to answer.

! THE NAME IS DESCRIPTIVE, NOT A TERM OF ART. It says what the module holds --
addresses, over a census -- and no trade word has been proposed for it.
"""

from comment_review.reading.addresser import cue_of


def resolve(address: str, paragraphs: list[dict]) -> list[int]:
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


def for_anchor(anchor: str, series: str, paragraphs: list[dict]) -> list[dict]:
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
    mine = [b for b in paragraphs if str(b.get("anchor", "")) == anchor]
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


def series_of(paragraph: dict) -> str:
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
    return cue_of(str(paragraph["address"])).series


def stable(paragraph: dict) -> str:
    """The place the census STAMPED on this paragraph, or "" if it carries none.

    !! IT READS; `place` COMPUTES. One implementation, one caller that runs it
    -- `page_for`, which holds the file text and the finished paragraph list at
    once -- and everything downstream reads the result. Two computations that
    agree today is not the property wanted, because only one of them can be
    right tomorrow.

    ! "" means the census predates the field. A caller REPORTS that rather than
    deriving a place from a census that never had one.
    """
    return str(paragraph.get("address", ""))


def _by_path(paragraphs: list[dict]) -> dict[str, list[dict]]:
    """Every paragraph grouped by the file it belongs to, in census order.

    !! ONE PASS, NOT ONE PER FILE. Four sites built the set of paths and then
    filtered the WHOLE census once for each of them -- O(files x paragraphs),
    on a structure that arrives already grouped because a census is stacked one
    page at a time.

    ! The grouping is what every caller actually wanted; the set of paths is
    `.keys()` and the census order inside a file is preserved, which is what
    `entry N` in a report counts.
    """
    out: dict[str, list[dict]] = {}
    for b in paragraphs:
        out.setdefault(str(b.get("path", "")), []).append(b)
    return out


def unaddressed(paragraphs: list[dict]) -> list[str]:
    """Which paragraphs carry NO address, described one per line.

    !! ONE SOURCE OF TRUTH, and the reason is the failure it prevents. Roy,
    2026-08-20: *"one source of truth, else something will parse that something
    else will fail."* Three callers ask this question -- `census.py` before it
    writes, `verdicts.py` before it certifies, and `addresser.py --check` -- and
    a second implementation of "is this addressed" is a second answer waiting to
    disagree with the first.

    !! IT IS ASKED AT BOTH ENDS ON PURPOSE. The census refusing on EMIT catches
    its own degradation where it happens; the gate refusing on READ catches a
    file that reached it some other way -- a census from an older version, one
    edited by hand, one written by a run that crashed. `verdicts.py` takes a
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
            if owes_address(paragraph) and not stable(paragraph):
                start = paragraph.get("original_start")
                end = paragraph.get("original_end")
                out.append(f"{path} entry {i}: lines {start}-{end}")
    return out


def owes_address(paragraph: dict) -> bool:
    """Is this a paragraph an address is REQUIRED of?

    !! LEADING OWED NONE, VIA A `symbol` FIELD NO ROW HAS CARRIED SINCE THE
    ELEVEN-FIELD CUT (`e56bea9`). `bind()` never puts a leading paragraph into
    a row at all: `page_row` runs only over paragraphs with an address, and a
    fence's own address is `""` -- see `binder.py`'s `bind`. MEASURED over a
    real `page_for`/`bind()`: no row this module can ever be handed lacks a
    `symbol` key for any OTHER reason, so `paragraph.get("symbol")` answered
    the same way -- unowed -- for every row, not only the leading ones it was
    written to exempt. The exemption is not merely unreachable; the
    population it existed to name cannot reach this function at all.

    ! ANSWERS `True` UNCONDITIONALLY, and this is a measured fact about the
    current wire format, not a design choice standing in for one: every row
    `unaddressed` or `_check` can be handed already owes an address.

    !! IT IS A FENCE, AND FENCES HAVE NO ADDRESS. Roy, 2026-08-23: *"the `d`
    series doesn't get an address for the same reasons fences in the real world
    don't get addresses. They mark a demarcation boundary and they have the same
    problem as fences -- whose fence is it."* ! Every other place is attached to
    a line of code, and that line is what a reviewer measures a claim against. A
    blank run sits BETWEEN two places and is attached to neither, so the
    ownership question has no answer rather than an unknown one.

    ! IT WAS TRIED AND REFUSED THREE TIMES -- `875b0d4` made it a fifth series,
    `b998a60` repaired it as an edge, `c27ea1d` retreated to a symbol. Roy,
    closing it: *"We tried leading getting a place. We tried several different
    ways. The constraints of coding AND editing do not allow it."* Two things stop
    being determinable the moment the slack is addressable: WHERE everything below
    an edit shifted to, and HOW MUCH blank belongs where afterwards -- the second
    being a typographic judgement no rule computes.

    !! UNADDRESSED IS NOT UNRECORDED, and that is the whole of the arrangement.
    Roy: *"the system knows hey there was a fence here we should put it back."*
    `Page.leading` keys the fence on the place it FOLLOWS -- `f0 -> d0` -- so
    what is remembered is a fact about a boundary rather than a thing with a
    location. ! Nobody can cite it, nobody can rule on it, and the compositor
    puts it back exactly where it was.

    ! WHICH IS WHY THE EDGE SHAPE HOLDS: this system never chooses an amount of
    blank, it replays what it read.

    !! IT IS STILL A FUNCTION, NOT A CONSTANT INLINED AT EACH CALLER, because
    the question it answers stays real: `unaddressed` and `_check` still need
    to ask it, and a future wire format could carry the field again. `unaddressed`
    exempted leading; `_check`'s HEADLINE counted it in both the numerator and
    the denominator, so a census of this repo's own scripts printed `8542 of 8542
    paragraphs addressed` while 392 of them carried no address at all. MEASURED
    2026-08-22, before the row cut -- the population that made the two disagree
    no longer reaches either caller.
    """
    return True
