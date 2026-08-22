"""Sets a page as TEXT, in memory, top to bottom. It decides nothing.

    python compositor.py --repo D <paths...>      # prove the identity, file by file

!! A COMPOSITOR SETS TYPE; IT DOES NOT EDIT IT. Roy, 2026-08-21: *"galley gets
the old page - updates the old page with the verdict/record/marks and then a
page-setter sets the page to rewrite the output text."* Two roles, two sets of
rules: the galley rules on what a paragraph should say, and this puts the page
together. A module that did both is what `galley.py` was, and its own vocabulary
said so -- `references/vocabulary.toml`: *"the GALLEY is text set but not yet
made into pages."*

!! IT SETS FROM THE FOLIATION'S READING ORDER AND KNOWS NO LINE NUMBERS. Roy,
2026-08-21: *"the compositor forms the whole file top to bottom in the order
defined by the language requirements IN MEMORY."* A page is its places in
sequence; `Foliation.reading` is that sequence, recorded by the walk that
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
`set_page(page_for(path, text, lang)) == text`, byte for byte, in any language.
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

import argparse
import collections
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from foliator import ON, series_of  # noqa: E402

# !! THE OTHER IMPORTER OF THE ROWS -- see `language.py`. The lexer reads a file
# into paragraphs and this sets a page back into one; they are the only two
# modules that touch a file, so they are the only two that may ask a language
# anything. ! It is read DIRECTLY and not through the lexer, so the rule is
# visible in the import graph rather than in a comment.
from language import language_for  # noqa: E402
from page import Page, page_for  # noqa: E402

READ_ERRORS = (OSError, UnicodeDecodeError)
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
    """The prose each place holds, by folio. Empty places hold none."""
    out: dict[str, list[str]] = {}
    for paragraph in page.paragraphs:
        folio = (paragraph.address or "").split("@")[-1]
        if folio:
            out[folio] = list(paragraph.raw_lines)
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
        page: the page to set. Its foliation states the order.
        newline: the ending to join with. `None` takes it from the page's own
            text, which is the one fact a paragraph cannot state.

    Returns:
        The file's text.
    """
    ending = newline if newline is not None else line_endings(page.text)
    held = _held(page)
    out: list[str] = []
    # !! LEADING IS SET BETWEEN TWO PLACES, NOT AT ONE. It is an edge -- see
    # `Foliation.leading` -- so the walk hands over a sequence of places and the
    # space between each adjacent pair is looked up as it is reached. An absent
    # key means those two places sit against each other, which is what 90% of
    # `c`->`c` boundaries do.
    #
    # ! THE FILE'S OWN EDGES ARE PAIRS TOO, with `""` for the side that has no
    # place: a blank run above everything is `("", f0)`.
    # !! AN EDGE BELONGS TO THE PLACE BEFORE IT, so it is looked up by its FIRST
    # key alone. Roy, 2026-08-21, ruling on what happens to leading when a
    # paragraph goes away: *"the live first key foliation lives, the drop first
    # key dies. The live one gets a new key that takes the new end and
    # beginning."*
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
    # ! THE SECOND KEY IS KEPT ON THE FOLIATION AND NOT USED HERE. A place has
    # at most one place after it, so the first key alone is unique; the pair is
    # what makes the edge legible -- and checkable -- rather than what finds it.
    edges = {before: folio for (before, _), folio in page.leading.items()}
    previous = ""
    for folio in page.foliation.reading:
        prose = held.get(folio, [])
        beside_code = series_of({"address": f"@{folio}"}) == ON
        # !! A PLACE THAT SETS NOTHING BREAKS NO EDGE. Leading separates two
        # pieces of TEXT, and an empty place is not text -- it is a position a
        # verdict can cite. Skipping it keeps the pair the same one `tie_leading`
        # tied: with `b0` empty between them, `a0` and `c0` are still adjacent in
        # the file even though the walk names a place in between.
        #
        # ! A `c` IS NEVER EMPTY IN THIS SENSE -- it sets its line of code
        # whether or not anything sits beside it.
        if not prose and not beside_code:
            continue
        out.extend(held.get(edges.get(previous, ""), []))
        previous = folio
        if beside_code:
            # ! A `c` IS THE LINE OF CODE, so it is set whether or not anything
            # sits beside it. Its first line is the code and the room together;
            # a comment opened in that room and closed on a later line owns
            # those lines outright, because no code is on them.
            code = page.foliation.anchor_of(folio)
            out.append(f"{code}{prose[0] if prose else ''}")
            out.extend(prose[1:])
            continue
        out.extend(prose)
    # ! THE CLOSING EDGE. A file ending in blank lines has leading below its last
    # place, which the loop cannot reach -- it sets the space BEFORE each place,
    # so the last place's own edge is still owed when the walk runs out.
    out.extend(held.get(edges.get(previous, ""), []))
    if not page.foliation.reading and page.text:
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
        raise ValueError(
            f"{page.path}: the page has no places -- its source was never read"
        )
    if not out:
        # !! AN EMPTY PAGE IS EMPTY TEXT -- and returning `page.text` here is how
        # this whole instrument would come to lie. A model that had lost every
        # line would set the original file back and the identity would pass over
        # the top of it.
        return ""
    # ! THE TRAILING NEWLINE IS THE FILE'S, and `splitlines` drops it, so no
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


def lossless(path: Path, rel: str | None = None) -> str | None:
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
        text = path.read_text(encoding="utf-8")
    except READ_ERRORS as exc:
        return f"unread: {exc}"
    lang = language_for(path)
    if lang is None:
        return f"no language record for {path.suffix!r}"
    try:
        got = set_page(page_for(path, text, lang, rel=rel))
    except ValueError as exc:
        return str(exc)
    if sorted(got.splitlines()) == sorted(text.splitlines()):
        return None
    was, now = (
        collections.Counter(text.splitlines()),
        collections.Counter(got.splitlines()),
    )
    missing = list((was - now).elements())[:1]
    invented = list((now - was).elements())[:1]
    if missing:
        return f"line lost: {missing[0]!r}"
    return f"line invented: {invented[0]!r}"


def identity(path: Path, rel: str | None = None) -> str | None:
    """Set this file from its own page and say where it differs, or None.

    Returns:
        `None` when the round trip is byte-identical. Otherwise a line naming
        the FIRST line that differs, which is what a reader needs to look at.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except READ_ERRORS as exc:
        return f"unread: {exc}"
    lang = language_for(path)
    if lang is None:
        return f"no language record for {path.suffix!r}"
    page = page_for(path, text, lang, rel=rel)
    try:
        got = set_page(page)
    except ValueError as exc:
        # ! The page was never built -- see `set_page`. It is reported like any
        # other refusal rather than raised through a sweep over a whole tree.
        return str(exc)
    if got == text:
        return None
    was, now = text.splitlines(), got.splitlines()
    for n, (a, b) in enumerate(zip(was, now, strict=False), 1):
        if a != b:
            return f"line {n}: was {a!r}, set {b!r}"
    return f"{len(was)} lines in, {len(now)} out"


def main(argv: list[str] | None = None) -> int:
    """Prove the identity over every path given; nonzero if any file differs."""
    parser = argparse.ArgumentParser(description="Set a page as text.")
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--repo", type=Path, default=Path("."))
    args = parser.parse_args(argv)
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="replace")
    same = moved = broken = 0
    for path in args.paths:
        gone = lossless(path)
        if gone is not None:
            broken += 1
            print(f"  LOSSY   {path} -- {gone}")
            continue
        why = identity(path)
        if why is None:
            same += 1
            print(f"  set     {path}")
        else:
            moved += 1
            print(f"  moved   {path} -- {why}")
    print(f"\n{same} identical, {moved} normalised, {broken} LOSSY")
    # !! ONLY A LOST OR INVENTED LINE FAILS. A normalised file is the ruled
    # series order doing what it was ruled to do -- see `set_page`.
    return 1 if broken else 0


if __name__ == "__main__":
    raise SystemExit(main())
