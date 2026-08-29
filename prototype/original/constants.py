"""What every entry point needs before it prints, and nothing else owns.

!! A LEAF WITH NO SIBLINGS. Ruled by Roy, 2026-08-22: *"the guard lives in a
constants.py file. The test verifies no readers or printers are missing the
guard."* It imports nothing from this package, so any module may take it without
acquiring a dependency on anything else.

!! IT EXISTS BECAUSE THERE WAS NOWHERE ELSE TO PUT IT. The console guard was
copy-pasted into TEN `main()` functions -- byte-identical in all ten while its
RATIONALE drifted into three wordings, five copies carrying none. The only
shared leaf was `repo.py`, whose first line states its subject as *"facts about
the checkout: git, the filesystem, and the exception tuples"*; stdout encoding
is not one of those, so deduplicating into it would have widened a module's
remit -- the defect `module-context` is chartered to catch. A module of its own
costs a file and keeps both rules.

! WHAT THE DRIFT LOOKED LIKE, since it is the reason this is one definition now:
`vocabulary.py`'s copy carried *"what it defends has CHANGED ... since the tree
went ASCII there are none"* -- a per-copy fact, sitting on three lines that were
identical in all ten. A comment true of one copy and false of nine cannot be
maintained.
"""

import re
import sys

#: The three things that end a line of a FILE: CRLF, CR, LF. Nothing else.
LINE_BREAK = re.compile(r"\r\n|\r|\n")


def text_lines(text: str) -> list[str]:
    """This text as lines, split ONLY where a file's line actually ends.

    !! `str.splitlines()` SPLITS ON ELEVEN THINGS, and eight of them are not line
    endings. It breaks on the vertical tab, the form feed, the three ASCII file
    and record separators, the next-line control, and Unicode's own line and
    paragraph separators -- every one of which a file may hold INSIDE A STRING
    LITERAL, where it is data and not a line break at all.

    !! WHAT THAT COSTS IS A CORRUPTED FILE, PAST BOTH GATES. MEASURED 2026-08-22
    on a two-line Python file whose first line held a Unicode line separator
    inside a string: the reader saw THREE lines, the compositor rejoined them
    with newlines, and the file came back with the literal broken across two --
    an unterminated string, a `SyntaxError`. `identity` reported *3 lines in, 3
    out* and `lossless` returned None. **Both gates passed on a file that no
    longer compiles**, because both were counting the reader's own idea of a
    line rather than the file's.

    ! IT IS THE ONE SPLIT THE MODEL RESTS ON. A page is its lines; if the reader
    and the file disagree about what a line IS, every address, every anchor and
    every set-back line inherits that disagreement. So it is defined once, in
    the leaf, and nothing in the reading or setting path calls `splitlines`.

    ! A TRAILING BREAK ENDS THE LAST LINE; it does not begin another. A file
    ending in a newline holds as many lines as it has text on -- which is what
    `splitlines` answers too, and what the compositor's own trailing-newline
    rule assumes.
    """
    out = LINE_BREAK.split(text)
    if out and out[-1] == "":
        out.pop()
    return out


def utf8_console() -> None:
    """Print UTF-8 with replacement, whatever the terminal's encoding is.

    !! IT DEFENDS AGAINST TEXT THIS TOOL DID NOT WRITE. Every entry point prints
    prose read out of somebody's file, and a console encoding that lacks a
    character in it raises `UnicodeEncodeError` mid-report -- so the run dies
    holding findings it has already made. `errors="replace"` prints a
    substitute; the report survives.

    ! GUARDED BY `getattr`, because `sys.stdout` is not always a real stream. A
    caller that redirects it -- `contextlib.redirect_stdout` to a `StringIO`, as
    several `--out` paths and most of the tests do -- hands over an object with
    no `reconfigure`, and asking for it directly would raise there instead.
    """
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="replace")
