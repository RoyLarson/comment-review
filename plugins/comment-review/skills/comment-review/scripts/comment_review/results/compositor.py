"""Sets a page as TEXT, in memory, top to bottom. It decides nothing.

    python compositor.py <paths...>               # prove the identity, file by file

!! A COMPOSITOR SETS TYPE; IT DOES NOT EDIT IT. Roy, 2026-08-21: *"galley gets
the old page - updates the old page with the verdict/record/marks and then a
page-setter sets the page to rewrite the output text."* Two roles, two sets of
rules: the galley rules on what a paragraph should say, and this puts the page
together. A module that did both is what `galley.py` was, and its own vocabulary
said so -- `references/vocabulary.toml`: *"the GALLEY is text set but not yet
made into pages."*

!! IT SETS FROM THE READING ORDER OF THE CUES AND KNOWS NO LINE NUMBERS. Roy,
2026-08-21: *"the compositor forms the whole file top to bottom in the order
defined by the language requirements IN MEMORY."* A page is its places in
sequence; `Cues.reading` is that sequence, recorded by the walk that
emitted them. ! An earlier draft built the file from each paragraph's
`original_start`, which passed the identity by REPLAYING positions -- and would
have set a reset page wrong, because a paragraph that grows moves every line
below it and those stored numbers are the ones the agents read, not a position
this step may trust.

!! NOTHING IS WRITTEN OVER THE REAL FILE HERE. `draft()` emits the whole page
into a file of its own so a reviewer or the author can compare it against the
original; `approve()` copies that over the real file wholesale, once. Roy: *"No
editing on the 'real' file until the draft is fully approved."*

!! AND THE ROUND TRIP IS A TEST BECAUSE THIS IS THE ONLY WRITER.
`set_page(page_for(path, text, lang, sha=read_source(path).sha)) == text`,
byte for byte, in any language.
! `prove_unchanged.py` is strictly weaker and answers a different question: it
proves the EXECUTABLE CODE survived an edit, not that the model of a page is
lossless.

Two shapes, and only the second needs assembling:

    a `c` place    holds the LINE OF CODE. Its anchor is that code and its prose
                   is the room beside it, so the line is the two concatenated --
                   and a comment opened there can close on a later line, which
                   is verbatim because no code sits on it.
    everything     `a`, `b` and `f` hold prose and nothing else. An empty one
                   contributes no line at all, which is what an empty place IS.

! THE LINE ENDING IS A FACT ABOUT THE FILE, NOT ABOUT ITS PARAGRAPHS, and it is
the one thing here taken from `page.text`. Nothing a paragraph says can state
whether the file that held it used CRLF, and a compositor that guessed would
rewrite every line of a Windows checkout.
"""

import collections
import shutil
from pathlib import Path

from comment_review.binder.page import Page, page_for
from comment_review.machine import constants, exceptions
from comment_review.machine.repo import read_source
from comment_review.reading.addresser import GAP, ON, cue_of

# !! THE OTHER DIRECT IMPORTER OF THE ROWS -- see `language.py`. The lexer reads
# a file into paragraphs and this sets a page back into one, so these two are
# where a language's own grammar is applied to text. ! Everywhere else reaches
# `language_for` through the lexer's re-export, which is a lookup rather than a
# reading; taking it from `language` here says which of the two this is.
from comment_review.reading.language import language_for
from comment_review.reading.series import Kind

CRLF = "\r\n"
LF = "\n"


def line_endings(text: str) -> str:
    """Which ending this text uses: CRLF if any line has one, else LF.

    ! THE FIRST ENDING WINS AND MIXED FILES ARE NORMALISED. A file holding both
    is already inconsistent, and picking per line would preserve a defect the
    author cannot see. `galley.py` has answered it this way since it was written.
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
        # !! ASKED, NOT SPLIT. `cue_of` is the one reader of an address, and
        # this re-derived it -- so the two disagreed on the one input that tells
        # them apart. MEASURED 2026-08-22: `cue_of("b3")` answers `""`, because
        # an address is `path@cue` and a bare cue is not one; `"b3".split("@")
        # [-1]` answers `"b3"`. So the compositor SET a place `galley.reset`
        # REFUSES, and the disagreement is invisible until the two are compared.
        # !! BRANCHED ON THE ADDRESS, NOT ON THE BLANK THAT CAME BACK. This read
        # `cue_of(paragraph.address or "").cue or paragraph.symbol` -- sending a
        # `d` through the address reader so the empty answer could signal "go
        # ask the symbol". Roy, 2026-08-24: *"Series d are walked because they
        # have to be but they are not cues."* It never was an address question.
        cue = cue_of(paragraph.address).cue if paragraph.address else paragraph.symbol
        if cue:
            out[cue] = list(paragraph.raw_lines)
    return out


def set_page(page: Page, newline: str | None = None) -> str:
    """This page, set as the text of a file.

    !! IT WALKS THE READING ORDER AND ASKS EACH PLACE WHAT IT HOLDS. That is the
    whole algorithm, and it is why an edit needs no arithmetic: a paragraph that
    grows from one line to four just hands back four lines, and every place after
    it is set where it always was -- next.

    !! THE SERIES ORDER IS FIXED AND `f` COMES FIRST, WHICH IS LOSSY ON ONE
    SHAPE. Roy, 2026-08-21: *"f0 always first, then a0, then b0, then c0. I know
    f0 is going to grab b0 lines. It is a sacrifice I am willing to make."* A
    file whose front matter is NOT on line 1 -- a blank above it, which `b` owns
    -- comes back with the matter above that blank. MEASURED over 699 files: 12
    are set this way, all C headers, and NONE of them loses or invents a line.

    ! THAT IS WHY `lossless` EXISTS BESIDE `identity`. The first is the invariant
    that must never break; the second is the strict form, and the gap between
    them is exactly this normalisation.

    ! AND IT IS HANDED TO A READER RATHER THAN SOLVED. Roy: *"I don't know how to
    do semantic matching thorough enough to catch all of the potential edge
    cases ... ownership-context is partially about this."* Moving an `f0` into a
    `b0` because that is where it fits is a `query` to the human, and it is one
    time per file.

    Args:
        page: the page to set. Its cues states the order.
        newline: the ending each line takes. `None` reads it from the page's own
            text, which is the one fact a paragraph cannot state.

    Returns:
        The file's text.
    """
    ending = newline if newline is not None else line_endings(page.text)
    held = _held(page)
    out: list[str] = []
    # !! LEADING IS SET BETWEEN TWO PLACES, NOT AT ONE. It is an edge -- see
    # `Page.leading` -- so the walk hands over a sequence of places and the
    # space between each adjacent pair is looked up as it is reached. An absent
    # key means those two places sit against each other, which is what 90% of
    # `c`->`c` boundaries do.
    #
    # ! A RUN ABOVE EVERYTHING FOLLOWS NOTHING, and is filed under `""`.
    # !! AN EDGE BELONGS TO THE PLACE BEFORE IT, which is what it is KEYED BY.
    # When a paragraph goes away the live first key keeps its leading and the
    # dropped one loses it; the live one takes a new key covering the new end
    # and beginning.
    #
    # !! IT IS ONE RULE FOR BOTH DIRECTIONS, which is why it is a lookup rather
    # than a rewrite. DROP `P` between X and Y: `P` sets nothing, so it never
    # becomes `previous` and the edge it owned is never asked for -- it dies with
    # it -- while X's edge is found and set before Y, which is the separation
    # that was above `P`. ADD `N` between X and Y: X's edge is found and set
    # before `N`, and `N` owns none, so `N` sits directly against Y.
    #
    # ! MEASURED: that is the shape the corpus has. `b`->`c` holds no blank in
    # 88% of 15,987 boundaries, so a new comment sitting straight on the code it
    # documents is the common case, not a compromise.
    #
    # !! THE SURVIVOR NEEDS NO NEW KEY, which is why this is a lookup and not a
    # rewrite. Dropping `P` between X and Y leaves X's edge keyed on X, and this
    # loop sets it before Y -- the new adjacency, reached without computing
    # anything, because the key that finds it never mentioned `P`.
    #
    # ! IT WAS KEYED BY A PAIR UNTIL 2026-08-22 and this line collapsed it. Roy,
    # shown that nothing read the second half: *"so drop the second edge if it
    # isn't necessary."* MEASURED before the cut over 96,047 edges on 2,792
    # corpus pages in ten languages, C carrying more of them than Python:
    # `before` alone is unique and the collapse lost ZERO. ! The pair was kept
    # for legibility and was the half that could be WRONG -- after a drop it
    # named a place it no longer separated.
    edges = page.leading
    # !! WHICH PLACES WERE EMPTY WHEN THE PAGE WAS READ. `galley.reset` fills
    # `raw_lines` and leaves the KIND saying absence, so a place holding prose
    # under an absent kind is one an `add` just filled -- which is the only case
    # the leading rule below may fire on.
    #
    # ! THE EDGE ALONE DOES NOT SAY IT. Measured 2026-08-26: keying the rule on
    # "no leading was looked up" fired on a MODIFY and on an unedited compose
    # too, because a `b` sitting flush against its code owns no leading either --
    # three tests caught it, `test_a_comment_run_that_swallows_code_is_caught_by
    # _prove` among them.
    absent = {
        cue_of(b.address).cue
        for b in page.paragraphs
        if b.address and Kind.occupies_no_lines(b.kind)
    }
    # !! THE CLOSING GAP IS EXEMPT, AND THE FOOT IS WHY. Back matter is the run
    # AFTER the last blank line, so a leading above an added closing `b` pushes
    # it INTO the matter it was meant to stay clear of. MEASURED 2026-08-26 on
    # `SAMPLE`: `b4` with a leading still re-reads at `f1`, so the blank changes
    # the bytes and not the outcome.
    #
    # ! THAT COLLISION IS ITS OWN FINDING and is not this rule's to solve --
    # `TODO/foot-of-file-two-places.md`, where `cue` emits the closing gap and
    # `f1` at the same `<eof>` trigger. The head pair is separable because front
    # matter ends at the FIRST blank; the foot pair is not, by the same rule read
    # upward.
    reading = list(page.cues.reading)
    last_code = max((i for i, c in enumerate(reading) if c.startswith(ON)), default=-1)
    previous = ""
    for at, cue in enumerate(reading):
        prose = held.get(cue, [])
        # ! ASKED OF THE CUE DIRECTLY. `series_of` reads an ADDRESS and
        # returns its first character, so building one here to take that
        # character back off is the same test twice -- and it is spelled the
        # direct way at five other sites in `galley` and `page`.
        beside_code = cue.startswith(ON)
        # !! EVERY PLACE ADVANCES `previous`, INCLUDING ONE THAT SETS NOTHING,
        # and that is what makes this walk exact. An empty place is still a
        # place -- it is a position a verdict can cite -- so skipping it here
        # made this list disagree with the one `tie_leading` walked.
        #
        # ! IT SKIPPED THEM UNTIL 2026-08-22, and `tie_leading` skipped them
        # too, so the two halves agreed by taking the SAME shortcut rather than
        # by either being right. The visible cost was a dark-matter `f0`: it set
        # nothing, so `previous` stayed `""` past the head of the file and a run
        # of blank lines there was keyed on the empty string.
        #
        # ! THE EDGE IS LOOKED UP BEFORE THE PLACE IS SET, so it lands between
        # what came before and what comes next. A place that sets nothing
        # contributes no lines, so the space still falls exactly where it did.
        #
        # !! A PLACE IS INVIOLABLE -- IT NEVER DISAPPEARS. Roy, 2026-08-22:
        # *"places are involatile; having an empty sentinel is the key, not that
        # the place disappears."* An emptied place still holds its position and
        # still owns the space below it. ! A first attempt made this loop skip a
        # place that had held lines and now set none, so that a `drop` would
        # take its leading with it -- which put an editorial decision inside the
        # compositor, whose whole charter is to decide NOTHING. `galley.reset`
        # empties the leading when it empties the paragraph.
        edge = held.get(edges.get(previous, ""), [])
        out.extend(edge)
        # !! A `b` SET INTO A PLACE THAT OWNED NO LEADING TAKES ONE. Roy,
        # 2026-08-26: *"It needs to add the leading between before any b"*, and
        # on how this tells: *"the leading look up paragraph is not in there,
        # which is admittedly backwards but that will tell."*
        #
        # ! WHY IT IS NEEDED: front matter and the first gap both sit above the
        # first statement, so a comment set flush under an `f0` re-reads as part
        # of that matter run and the `b` loses its address. A blank between them
        # is what keeps the two places separable -- see `lexer.paragraphs_stdlib`.
        #
        # ! ROY RULED THE COST: *"It may not be what all of the projects do but
        # it is generally enough and easy enough to implement and it looks good
        # enough to most humans that I think it is a justifiable editorial
        # decision."* And on the file that opens with the blank: *"the leading on
        # the first line for places that do not have frontmatter will disappear
        # on an automatic format run like ruff or black."*
        # ! IT FIRES AT THE HEAD OF THE FILE TOO, so a `b0` added to a file with
        # no front matter opens with a blank line. Roy, 2026-08-26, ruling on
        # that cost directly: *"The leading on the first line for places that do
        # not have frontmatter will disappear on an automatic format run like
        # ruff or black."* Suppressing it there is what left `b0` re-reading as
        # `f0` -- the defect this rule exists to close.
        #
        # !! AND AT THE FOOT IT GOES ON THE OTHER SIDE. Roy, 2026-08-26: *"still
        # the same rule as the frontmatter in reverse."* Matter is the run that
        # STARTS on line 1 or ENDS on the last one, so what pushes a gap out of
        # it is a blank BEFORE at the head and a blank AFTER at the foot. !
        # MEASURED: `...return y\n# ADDED\n` and `...return y\n\n# ADDED\n` both
        # re-read at `f1`; `...return y\n# ADDED\n\n` re-reads at the closing
        # gap. A leading before the closing gap was the mirror image of the fix
        # and moved nothing.
        adding_a_gap = bool(prose) and cue.startswith(GAP) and cue in absent
        if adding_a_gap and not edge and at < last_code:
            out.append("")
        # ! OWED UNTIL THE PROSE IS SET, which is why it is held rather than
        # written here -- the blank belongs BELOW the paragraph.
        trailing = adding_a_gap and at > last_code and not edges.get(cue)
        previous = cue
        # ! A `c` IS NEVER EMPTY IN THIS SENSE -- it sets its line of code
        # whether or not anything sits beside it.
        if not prose and not beside_code:
            continue
        if beside_code:
            # ! A `c` IS THE LINE OF CODE, so it is set whether or not anything
            # sits beside it. Its first line is the code and the room together;
            # a comment opened in that room and closed on a later line owns
            # those lines outright, because no code is on them.
            code = page.cues.anchor_of(cue)
            out.append(f"{code}{prose[0] if prose else ''}")
            out.extend(prose[1:])
            continue
        out.extend(prose)
        if trailing:
            out.append("")
    # ! THE CLOSING EDGE. A file ending in blank lines has leading below its last
    # place, which the loop cannot reach -- it sets the space BEFORE each place,
    # so the last place's own edge is still owed when the walk runs out.
    out.extend(held.get(edges.get(previous, ""), []))
    if not page.cues.reading and page.text:
        # !! A PAGE WITH NO PLACES OVER A FILE WITH TEXT IS NOT AN EMPTY PAGE --
        # it is a page that was never built, and setting it would EMPTY THE FILE.
        # `page_for` skips the walk when a reader refuses the source, so
        # `reading` is empty and every line of the file is unaccounted for.
        #
        # !! MEASURED 2026-08-21 on `sentry/src/sentry/api/paginator.py`: 884
        # lines in, 0 characters out, silently. It uses `class Paginator[T]:` --
        # PEP 695, which the floor interpreter cannot parse -- and 4 files in
        # `corpora/` are in that state today. Roy: *"we can't use python to parse
        # python files ... the ast to bootstrap the pieces fails on new python
        # syntax."*
        #
        # ! REFUSING IS THE ONLY SAFE ANSWER. `draft()` writes what this returns,
        # and an empty draft approved by anyone not reading the diff is a deleted
        # file. See `TODO/python-cannot-read-python.md`.
        raise exceptions.Refused(
            f"{page.path}: the page has no places -- its source was never read"
        )
    if not out:
        # !! AN EMPTY PAGE IS EMPTY TEXT -- and returning `page.text` here is how
        # this whole instrument would come to lie. A model that had lost every
        # line would set the original file back and the identity would pass over
        # the top of it.
        return ""
    # ! THE TRAILING NEWLINE IS THE FILE'S, and the reader drops it -- see
    # `constants.text_lines`, which states that rule -- so no
    # paragraph can state whether it was there. A file that ended in one is set
    # with one; a file that did not is not.
    tail = ending if page.text.endswith(("\n", "\r")) else ""
    return ending.join(out) + tail


def draft(page: Page, into: Path) -> Path:
    """Write this page to `into` -- a file of its own, never the original.

    !! THE REAL FILE IS NOT TOUCHED HERE. Roy, 2026-08-21: *"it gets emitted into
    a temporary file to be compared to the original by either the reviewing agent
    or the human ... No editing on the 'real' file until the draft is fully
    approved."* So a run that is abandoned, refused or wrong leaves the tree
    exactly as it found it, and `git diff --no-index` against the original is the
    whole review.
    """
    into.parent.mkdir(parents=True, exist_ok=True)
    into.write_text(set_page(page), encoding="utf-8", newline="")
    return into


def approve(drafted: Path, real: Path) -> Path:
    """Put an approved draft over the real file, wholesale.

    ! A COPY, NOT A SPLICE. The draft IS the finished page -- it was set from the
    whole of it -- so there is nothing to merge and no range to get wrong. That
    is the difference this module exists to make.
    """
    shutil.copyfile(drafted, real)
    return real


def lossless(path: Path) -> str | None:
    """Does this file come back with every line it went in with? None if so.

    !! THE WEAKER INVARIANT, AND THE ONE THAT MUST NEVER BREAK. `identity` asks
    for the same bytes in the same order; this asks only that no line was lost
    and none invented. They differ on exactly one shape, and it is RULED rather
    than a defect -- see `set_page` on the series order.

    ! IT IS WHAT SEPARATES A NORMALISATION FROM A BUG. MEASURED 2026-08-21 over
    699 files: 12 fail `identity` and 0 fail this one. A gate that could not tell
    them apart would carry 12 known-acceptable failures, and the thirteenth --
    a real one -- would land among them unnoticed.
    """
    try:
        source = read_source(path)
    except exceptions.READ_ERRORS as exc:
        return f"unread: {exc}"
    text = source.text
    lang = language_for(path)
    if lang is None:
        return f"no language record for {path.suffix!r}"
    try:
        got = set_page(page_for(path, text, lang, sha=source.sha))
    except exceptions.Refused as exc:
        return str(exc)
    if sorted(constants.text_lines(got)) == sorted(constants.text_lines(text)):
        return None
    was, now = (
        collections.Counter(constants.text_lines(text)),
        collections.Counter(constants.text_lines(got)),
    )
    missing = list((was - now).elements())[:1]
    invented = list((now - was).elements())[:1]
    if missing:
        return f"line lost: {missing[0]!r}"
    return f"line invented: {invented[0]!r}"


def identity(path: Path) -> str | None:
    """Set this file from its own page and say where it differs, or None.

    Returns:
        `None` when the round trip is byte-identical. Otherwise a line naming
        the FIRST line that differs, which is what a reader needs to look at.
    """
    try:
        source = read_source(path)
    except exceptions.READ_ERRORS as exc:
        return f"unread: {exc}"
    text = source.text
    lang = language_for(path)
    if lang is None:
        return f"no language record for {path.suffix!r}"
    page = page_for(path, text, lang, sha=source.sha)
    try:
        got = set_page(page)
    except exceptions.Refused as exc:
        # ! The page was never built -- see `set_page`. It is reported like any
        # other refusal rather than raised through a sweep over a whole tree.
        # ! NARROWED from a bare `ValueError`, which also caught anything else
        # that failed inside `page_for` and printed it as our own refusal.
        return str(exc)
    if got == text:
        return None
    was, now = constants.text_lines(text), constants.text_lines(got)
    for n, (a, b) in enumerate(zip(was, now, strict=False), 1):
        if a != b:
            return f"line {n}: was {a!r}, set {b!r}"
    return f"{len(was)} lines in, {len(now)} out"
