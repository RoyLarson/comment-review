"""Sets a page as TEXT, in memory, top to bottom.

    python -m comment_review compositor <paths...>  # check the round trip

!! A COMPOSITOR SETS TYPE. Two roles, two sets of rules:
the galley rules on what a paragraph should say, and this puts the page
together.

!! IT SETS FROM THE READING ORDER OF THE CUES AND KNOWS NO LINE NUMBERS. A page
is its places in sequence; `Cues.reading` is that sequence, recorded by the walk
that emitted them. ! A paragraph's stored line numbers are not a position this
step may trust: a paragraph that grows moves every line below it.

!! NOTHING IS WRITTEN OVER THE REAL FILE UNTIL THE DRAFT IS APPROVED. `draft()`
emits the whole page into a file of its own so a reviewer or the author can
compare it against the original; `approve()` copies that over the real file
wholesale, once.

! `draft()` WRITES NO BYTES OF ITS OWN: it hands its text to
`machine.repo.write_raw`; what this module owns is SETTING a page, and where a
page lands is the checkout's business. `approve()` copies with
`shutil.copyfile`.

!! AND THE ROUND TRIP IS A TEST.
For a supplied, unchanged `Page`, `set_page(page) == page.text`, byte for byte,
except where it normalises: front matter that does not open on line 1 (see
`set_page`) and mixed line endings (see `line_endings`). `identity` checks that
round trip byte for byte; `lossless` checks only that no line is lost or
invented, and the `compositor` command fails on that one.
! `prove_unchanged.py` is strictly weaker and answers a different question: it
proves the EXECUTABLE CODE survived an edit, not that the model of a page is
lossless.

Every place has an anchor; only a `c` place's anchor is part of what is set:

    a `c` place    is set as its line of code with its prose beside it, the
                   two concatenated. A comment opened there can close on a
                   later line, which is set verbatim because no code sits on
                   it.
    `a`, `b`, `f`  are set as their prose alone. An empty one sets no line.

! THE LINE ENDING IS A FACT ABOUT THE FILE, NOT ABOUT ITS PARAGRAPHS, and it is
taken from `page.text`, with the two other facts no paragraph holds: whether
the file has text at all, and whether it ends on a line break. Nothing a
paragraph says can state whether the file that held it used CRLF, and a
compositor that guessed would rewrite every line of a Windows checkout.
"""

import collections
import shutil
from pathlib import Path

from comment_review import constants, exceptions
from comment_review.binder.page import Page
from comment_review.machine.repo import write_raw
from comment_review.reading.addresser import DECLARED, GAP, ON, cue_of
from comment_review.reading.series import Kind

CRLF = "\r\n"
LF = "\n"


def line_endings(text: str) -> str:
    """Which ending this text uses: CRLF if any line has one, else LF.

    ! ANY CRLF WINS AND MIXED FILES ARE NORMALISED. A file holding both
    is already inconsistent, and picking per line would preserve a defect the
    author cannot see.
    """
    return CRLF if CRLF in text else LF


def _held(page: Page) -> dict[str, list[str]]:
    """The lines each place holds, by cue -- and each `d` by its symbol.

    ! Empty places hold none.

    !! LEADING IS KEYED BY ITS SYMBOL BECAUSE IT HAS NO ADDRESS. It is not a
    place -- see `addresser.SERIES` -- so it never appears in the reading order
    and is reached only through `Page.leading`, which names it by that symbol.
    """
    out: dict[str, list[str]] = {}
    for paragraph in page.paragraphs:
        # !! ASKED, NOT SPLIT. `galley.reset` keys a place by `cue_of`, so this
        # does too: `cue_of("b3")` answers `""`, because an address is `path@cue`
        # and a bare cue is not one, where `"b3".split("@")[-1]` answers `"b3"`.
        # !! BRANCHED ON THE ADDRESS, NOT ON THE BLANK THAT CAME BACK. A `d` is
        # walked but has no address, so it is keyed by its symbol and never passed
        # through the address reader.
        cue = cue_of(paragraph.address).cue if paragraph.address else paragraph.symbol
        if cue:
            out[cue] = list(paragraph.raw_lines)
    return out


def set_page(page: Page, newline: str | None = None) -> str:
    """This page, set as the text of a file -- see `_set`."""
    return _set(page, newline)[0]


def spans(page: Page) -> dict[str, tuple[int, int]]:
    """The lines each place holding prose is set on, by cue, first and last.

    Both ends are inclusive and count from 1. A place that sets no prose has no
    entry. These say where the text was written and nothing about what a reader
    finds there, which is `flows.proof_setter._reread`'s question.
    """
    return _set(page, None)[1]


def _set(page: Page, newline: str | None) -> tuple[str, dict[str, tuple[int, int]]]:
    """This page as text, with the lines each place holding prose is set on.

    !! IT WALKS THE READING ORDER AND ASKS EACH PLACE WHAT IT HOLDS. That is the
    whole algorithm, and it is why an edit needs no arithmetic: a paragraph that
    grows from one line to four just hands back four lines, and every place after
    it is set where it always was -- next.

    !! THE SERIES ORDER IS FIXED AND `f` COMES FIRST, WHICH IS LOSSY ON ONE
    SHAPE. A file whose front matter is NOT on line 1 -- a blank above it, which
    `b` owns -- comes back with the matter above that blank. MEASURED over 3,155
    corpus files: 3 are set this way, all in `corpora/pymc`, and none loses or
    invents a line.

    ! THAT IS WHY `lossless` EXISTS BESIDE `identity`. The first is the invariant
    that must never break; the second is the strict form, and the gap between
    them is exactly this normalisation.

    ! AND IT IS HANDED TO A READER RATHER THAN SOLVED. Moving an `f0` into a `b0`
    because that is where it fits is a `query` to the human, and it is one time
    per file.

    Args:
        page: the page to set. Its cues states the order.
        newline: the ending each line takes. `None` reads it from the page's own
            text, which is the one fact a paragraph cannot state.

    Returns:
        `(the file's text, cue -> (first line, last line))`.

    Raises:
        Refused: the page has no places over a file with text -- its source
            was never read, and setting it would empty the file.
    """
    ending = newline if newline is not None else line_endings(page.text)
    held = _held(page)
    out: list[str] = []
    lines_of: dict[str, tuple[int, int]] = {}
    # !! LEADING IS SET BETWEEN TWO PLACES, NOT AT ONE. It is an edge -- see
    # `Page.leading` -- so the walk hands over a sequence of places and the
    # space between each adjacent pair is looked up as it is reached. An absent
    # key means those two places sit against each other, which is what 90% of
    # `c`->`c` boundaries do.
    #
    # A run above everything is keyed under `f0`, the first place `cue` emits,
    # while `f0` holds no lines. Above a filled `f0`, and for a `Cues` with no
    # places, it is keyed under `""`, which is `previous` at the first place --
    # see `tie_leading`. An edge belongs to the place before it, which is what
    # it is keyed by. When a
    # paragraph goes away the place before it keeps its leading and the dropped
    # place's is not set; no key changes.
    #
    # The lookup is the base rule, and each direction adds one check to it. Drop
    # `P` between X and Y: `P` sets nothing but still becomes `previous`, and
    # because it is in `vacated` the edge it owned is not set -- so what
    # separates X from Y is X's own edge, set before `P`. Add `N` between X and
    # Y: X's edge is set before `N`, and where X owns none and `N` is a `b`
    # above the last line of code, `adding_a_gap` supplies one; `N` owns no
    # edge, so it sits directly against Y.
    #
    # ! MEASURED: that is the shape the corpus has. `b`->`c` holds no blank in
    # 88% of 15,987 boundaries, so a new comment sitting straight on the code it
    # documents is the common case, not a compromise.
    #
    # The survivor needs no new key, which is why this is a lookup and not a
    # rewrite. Dropping `P` between X and Y leaves X's edge keyed on X, and this
    # loop sets it where it always was -- the new adjacency, reached without
    # computing anything, because the key that finds it never mentioned `P`.
    edges = page.leading
    # !! WHICH PLACES WERE EMPTY WHEN THE PAGE WAS READ. `galley.reset` fills
    # `raw_lines` and leaves the KIND saying absence, so a place holding prose
    # under an absent kind is one an `add` just filled -- which is the only case
    # the leading rule below may fire on.
    #
    # ! THE EDGE ALONE DOES NOT SAY IT. Keying the rule on "no leading was looked
    # up" would fire on a MODIFY and on an unedited compose too, because a `b`
    # sitting flush against its code owns no leading either.
    absent = {
        cue_of(b.address).cue
        for b in page.paragraphs
        if b.address and Kind.occupies_no_lines(b.kind)
    }
    # Which places once held prose and hold none now -- the mirror of
    # `absent` above, for the drop side of `Addressing: #22`. `galley.reset`
    # empties the paragraph and leaves its `d` alone, so a place whose kind
    # still says prose belongs and whose `raw_lines` are empty is one a
    # `drop` just vacated -- which is the only case the rule below may fire
    # on.
    #
    # Keyed on the place's state, not on the edge or on a lookup: a gate on
    # "no leading was looked up" would fire on a modify and on an unedited
    # compose too. `Addressing: #19` gates the add side the same way, and this
    # is its mirror.
    #
    # `ON` is excluded. A `c` sets its line of code whether or not
    # anything sits beside it, so a comment leaving that line vacates
    # nothing the code itself did not already occupy --
    # `test_a_dropped_c_does_not_lose_the_blank_below_its_code` holds it.
    vacated = {
        cue_of(b.address).cue
        for b in page.paragraphs
        if b.address
        and not cue_of(b.address).cue.startswith(ON)
        and not Kind.occupies_no_lines(b.kind)
        and not b.raw_lines
    }
    reading = list(page.cues.reading)
    last_code = max((i for i, c in enumerate(reading) if c.startswith(ON)), default=-1)
    previous = ""
    closing_gap = False
    for at, cue in enumerate(reading):
        prose = held.get(cue, [])
        # ! ASKED OF THE CUE DIRECTLY. `series_of` reads a paragraph's address
        # and returns its cue's first character, so building one here to take
        # that character back off is the same test twice -- and it is spelled the
        # direct way at five other sites in `binder/page.py`.
        beside_code = cue.startswith(ON)
        # !! EVERY PLACE ADVANCES `previous`, INCLUDING ONE THAT SETS NOTHING, and
        # that is what makes this walk exact. An empty place is still a place --
        # it is a position an instruction can cite -- so skipping it here made
        # this list disagree with the one `tie_leading` walked.
        #
        # ! THE EDGE IS LOOKED UP BEFORE THE PLACE IS SET, so it lands between
        # what came before and what comes next. A place that sets nothing
        # contributes no lines, so the space still falls exactly where it did.
        #
        # !! A PLACE IS INVIOLABLE -- IT NEVER DISAPPEARS. An emptied place still
        # holds its position; whether it still owns the space below it is what
        # `vacated` answers.
        #
        # And the call is this loop's: a fence is a property of the page being
        # laid out, so it is asked here and not by the edit that touched the
        # place. The question is the place's state -- a kind that says prose
        # belongs, and no lines held -- which is what `vacated` reads.
        edge = [] if previous in vacated else held.get(edges.get(previous, ""), [])
        out.extend(edge)
        # !! A `b` SET INTO A PLACE THAT OWNED NO LEADING TAKES ONE: when an
        # added `b` finds no leading looked up before it, a blank line is set
        # above it.
        #
        # ! WHY IT IS NEEDED: front matter and the first gap both sit above the
        # first statement, so a comment set flush under an `f0` re-reads as part
        # of that matter run and the `b` loses its address. A blank between them
        # is what keeps the two places separable -- see `Kind.MATTER`.
        #
        # ! IT FIRES AT THE HEAD OF THE FILE TOO, so a `b0` added to a file with
        # no front matter opens with a blank line, which a formatter such as
        # ruff or black removes. Suppressing it there leaves `b0` re-reading as
        # `f0` -- the defect this rule exists to close.
        adding_a_gap = bool(prose) and cue.startswith(GAP) and cue in absent

        # !! THE CLOSING GAP IS EXEMPT, AND THE FOOT IS WHY. With no closing
        # docstring, back matter is the run AFTER the last blank line -- the rule
        # is `reading.matter`'s -- so a leading above an added closing `b`
        # pushes it INTO the matter it was meant to stay clear of: on `SAMPLE`,
        # `b4` with a leading still re-reads at `f1`, so the blank changes the
        # bytes and not the outcome.
        if adding_a_gap and not edge and at < last_code:
            out.append("")
        # !! AND AT THE FOOT IT GOES ON THE OTHER SIDE -- the head's rule in
        # reverse. With no module or closing docstring, matter is the run that
        # STARTS on line 1 or ENDS on the last one, so what pushes a gap out of it
        # is a blank BEFORE at the head and a blank AFTER at the foot.
        # ! `...return y\n# ADDED\n` and
        # `...return y\n\n# ADDED\n` both re-read at `f1`;
        # `...return y\n# ADDED\n\n` re-reads at the closing gap, so a leading
        # before the closing gap moves nothing.
        #
        # ! OWED UNTIL THE PROSE IS SET, which is why it is held rather than
        # written here -- the blank belongs BELOW the paragraph.
        #
        # ! AND NOT OWED WHEN A CLOSING DOCSTRING IS SET BELOW IT: the gap then
        # does not end on the last line, and the docstring is what parts it
        # from the back matter.
        trailing = (
            adding_a_gap
            and at > last_code
            and not edges.get(cue)
            and not any(
                held.get(c) for c in reading[at + 1 :] if c.startswith(DECLARED)
            )
        )
        previous = cue
        # ! A `c` IS NEVER EMPTY IN THIS SENSE -- it sets its line of code
        # whether or not anything sits beside it.
        if not prose and not beside_code:
            continue
        closing_gap = False
        if prose:
            lines_of[cue] = (len(out) + 1, len(out) + len(prose))
        if beside_code:
            # A `c`'s first line is the code and the room together; a comment
            # opened in that room and closed on a later line owns those lines
            # outright, because no code is on them.
            code = page.cues.anchor_of(cue)
            out.append(f"{code}{prose[0] if prose else ''}")
            out.extend(prose[1:])
            continue
        out.extend(prose)
        if trailing:
            out.append("")
            closing_gap = True
    # ! THE CLOSING EDGE. A file ending in blank lines has leading below its last
    # place, which the loop cannot reach -- it sets the space BEFORE each place,
    # so the last place's own edge is still owed when the walk runs out.
    out.extend(held.get(edges.get(previous, ""), []))
    if not page.cues.reading and page.text:
        # !! A PAGE WITH NO PLACES OVER A FILE WITH TEXT IS NOT AN EMPTY PAGE --
        # it is a page that was never built, and setting it would EMPTY THE FILE.
        # `page_for` returns a `ReadFailure` rather than a page when a reader
        # refuses the source, so a page reaching here with no `reading` was built
        # some other way, and every line of its file is unaccounted for.
        #
        # ! REFUSING IS THE ONLY SAFE ANSWER. `draft()` writes what this returns,
        # and an empty draft approved by anyone not reading the diff is a deleted
        # file.
        raise exceptions.Refused(
            f"{page.path}: the page has no places -- its source was never read"
        )
    if not out:
        # !! AN EMPTY PAGE IS EMPTY TEXT -- and returning `page.text` here is how
        # this whole instrument would come to lie. A model that had lost every
        # line would set the original file back and the identity would pass over
        # the top of it.
        return "", lines_of
    # A closing-gap insertion needs a physical blank below its prose.
    tail = ending if closing_gap or page.text.endswith(("\n", "\r")) else ""
    return ending.join(out) + tail, lines_of


def draft(page: Page, into: Path) -> Path:
    """Write this page to `into` -- a file of its own, never the original.

    !! THE REAL FILE IS NOT TOUCHED HERE. The page is emitted into a file of its
    own, so a run that is abandoned, refused or wrong leaves the tree exactly as
    it found it, and `git diff --no-index` against the original is the whole
    review.

    !! IT REACHES DISK THROUGH `machine.repo.write_raw`. This module SETS a page;
    where the bytes land and how they are written is the checkout's business,
    which is `machine`'s.

    ! `write_raw` CARRIES the one-writer property `flows.proof_setter._one`
    depends on, and the untranslated write `results/prove_unchanged.py`'s byte
    comparison depends on, and says so.
    """
    return write_raw(into, set_page(page))


def approve(drafted: Path, real: Path) -> Path:
    """Put an approved draft over the real file, wholesale.

    ! A COPY, NOT A SPLICE. The draft IS the finished page -- it was set from the
    whole of it -- so there is nothing to merge and no range to get wrong. That
    is the difference this module exists to make.

    ! IT HAS NO CALLER, in `src/` or in `tests/`.
    """
    shutil.copyfile(drafted, real)
    return real


def lossless(original: str, rendered: str) -> str | None:
    """Compare supplied text for retained lines; return None if all remain.

    !! THE WEAKER INVARIANT, AND THE ONE THAT MUST NEVER BREAK. `identity` asks
    for the same bytes in the same order; this compares line multisets, including
    duplicate counts, without line endings. Reordering lines or changing their
    endings can preserve this invariant while failing byte identity.

    ! IT IS WHAT SEPARATES A NORMALISATION FROM A BUG. A gate that could not tell
    them apart would carry the known-acceptable failures, and the next one -- a
    real one -- would land among them unnoticed.

    !! MEASURED over ten of the 18 corpora `corpora/corpora.toml` pins, 3,155
    files carrying a language record: **3 fail `identity` and 0 lose or invent a
    line**. The three are the `f`-before-`b` ordering above, all in
    `corpora/pymc`. A further 4, all in `corpora/sentry`, are REFUSED by both
    checks before either can measure anything -- the unparsed page, whose source
    the reader never established.

    Returns:
        None when both texts hold the same lines, each as often; otherwise a
        message naming the first lost line (`line lost: ...`), or failing that
        the first invented one (`line invented: ...`).
    """
    if sorted(constants.text_lines(rendered)) == sorted(constants.text_lines(original)):
        return None
    was, now = (
        collections.Counter(constants.text_lines(original)),
        collections.Counter(constants.text_lines(rendered)),
    )
    missing = list((was - now).elements())[:1]
    invented = list((now - was).elements())[:1]
    if missing:
        return f"line lost: {missing[0]!r}"
    return f"line invented: {invented[0]!r}"


def identity(original: str, rendered: str) -> str | None:
    """Compare supplied strict UTF-8 bytes and report the first difference.

    Returns:
        `None` when the round trip is byte-identical. Otherwise name the first
        differing physical line with its ending, or report changed line counts
        when one text has extra lines after the shared prefix.
    """
    if original.encode("utf-8") == rendered.encode("utf-8"):
        return None
    was: list[str] = []
    now: list[str] = []
    for text, lines in ((original, was), (rendered, now)):
        start = 0
        for ending in constants.LINE_BREAK.finditer(text):
            lines.append(text[start : ending.end()])
            start = ending.end()
        if start < len(text):
            lines.append(text[start:])
    for n, (a, b) in enumerate(zip(was, now, strict=False), 1):
        if a != b:
            return f"line {n}: was {a!r}, set {b!r}"
    return f"{len(was)} lines in, {len(now)} out"
