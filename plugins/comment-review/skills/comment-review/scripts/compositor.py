"""Sets a page as TEXT. It decides nothing.

    python compositor.py --repo D <paths...>      # prove the identity, file by file

!! A COMPOSITOR SETS TYPE; IT DOES NOT EDIT IT. Roy, 2026-08-21: *"galley gets
the old page - updates the old page with the verdict/record/marks and then a
page-setter sets the page to rewrite the output text."* Two roles, two sets of
rules: the galley rules on what a paragraph should say, and this puts the page
on the disk. A module that did both is what `galley.py` was, and its own
vocabulary said so -- `references/vocabulary.toml`: *"the GALLEY is text set but
not yet made into pages."*

!! IT IS THE ONLY THING THAT WRITES, WHICH IS WHAT MAKES THE ROUND TRIP A TEST.
`set_page(page_for(path, text, lang)) == text`, byte for byte, in any language.
Roy: *"we can compare the round trip directly page in page out, page in,
comments removed, page out no comments ... No ambiguity about how the page gets
written."* ! `prove_unchanged.py` is strictly weaker and answers a different
question: it proves the EXECUTABLE CODE survived an edit, not that the model of
a page is lossless.

THE PAGE TILES ITS OWN FILE, which is what makes this total rather than a
best effort. Every line belongs to exactly one paragraph that states its own
lines -- `fill_the_gaps` is what gives a gap its blank lines, so there is no
line left for a fallback to guess at. Measured on an 8-line file: `a0` 1, `b0`
2, `c0` 3, `b1` 4-5, `c1` 6, `b2` 7, `c2` 8.

Two shapes, and the second is the only one that needs assembling:

    a FULL-LINE run    its `raw_lines` ARE those lines, verbatim
    a TRAILING run     `anchor` holds the code and `raw_lines[0]` the room
                       beside it, so the line is the two concatenated

! THE LINE ENDING IS A FACT ABOUT THE FILE, NOT ABOUT ITS PARAGRAPHS, and it is
the one thing here that comes from `page.text` rather than from the model. A
paragraph states what it says; nothing in it can state whether the file that
held it used CRLF, and a compositor that guessed would rewrite every line of a
Windows checkout.
"""

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from lexer import language_for  # noqa: E402
from page import Page, page_for  # noqa: E402

READ_ERRORS = (OSError, UnicodeDecodeError)
CRLF = "\r\n"
LF = "\n"


def line_endings(text: str) -> str:
    """Which ending this text uses: CRLF if any line has one, else LF.

    ! THE FIRST ENDING WINS AND MIXED FILES ARE NORMALISED. A file holding both
    is already inconsistent, and picking per line would preserve a defect the
    author cannot see. `galley.py` has answered it this way since it was
    written.
    """
    return CRLF if CRLF in text else LF


def _line_of(paragraph) -> tuple[int, list[str]]:
    """The first line this paragraph occupies, and the lines it puts there.

    ! A TRAILING RUN IS ASSEMBLED FROM TWO HALVES ON ITS FIRST LINE ONLY. Its
    `anchor` is the code with the room beside it removed and `raw_lines[0]` is
    that room, INCLUDING the whitespace that separates them -- so the line is a
    plain concatenation and never a join with a guessed gap.

    !! AND IT CAN RUN PAST THAT LINE, which is where this dropped ten C files
    before the identity was run over a corpus. A delimited comment opened beside
    code closes where it closes: `PyAsyncMethods *tp_as_async; /* formerly
    known as tp_compare (Python 2)` continues `or tp_reserved (Python 3) */` on
    the next line, which holds no code and is therefore verbatim. Only the
    FIRST line has an anchor to sit beside.
    """
    if paragraph.original_column:
        room = list(paragraph.raw_lines) or [""]
        return paragraph.original_start, [f"{paragraph.anchor}{room[0]}", *room[1:]]
    return paragraph.original_start, list(paragraph.raw_lines)


def set_page(page: Page, newline: str | None = None) -> str:
    """This page, set as the text of a file.

    !! IT READS THE PARAGRAPHS AND NOT `page.text`. Reading the text would make
    the round trip vacuous -- it would prove that a string equals itself, which
    is true of a page whose model has lost half the file.

    Args:
        page: the page to set. Every paragraph that states a line contributes
            it; a place holding no prose states none and contributes nothing.
        newline: the ending to join with. `None` takes it from the page's own
            text, which is the one fact a paragraph cannot state.

    Returns:
        The file's text. A page built from a file that ended in a newline is
        set with one, because the final paragraph's lines end where the file's
        lines end.
    """
    ending = newline if newline is not None else line_endings(page.text)
    lines: dict[int, str] = {}
    for paragraph in page.paragraphs:
        if not paragraph.original_start:
            # ! A place nothing fills states no line. It is still a place a
            # verdict can cite, which is why it is on the page at all.
            continue
        first, held = _line_of(paragraph)
        for offset, line in enumerate(held):
            lines[first + offset] = line
    if not lines:
        # !! NO PARAGRAPH STATED A LINE, SO THE PAGE IS EMPTY -- and returning
        # `page.text` here instead is how this whole instrument would come to
        # lie. A model that had lost every line would set the original file back
        # and the identity would pass over the top of it.
        return ""
    out = [lines.get(n, "") for n in range(1, max(lines) + 1)]
    # ! THE TRAILING NEWLINE IS THE FILE'S, and `splitlines` drops it, so the
    # page cannot state whether it was there. A file that ended in one is set
    # with one; a file that did not is not.
    tail = ending if page.text.endswith(("\n", "\r")) else ""
    return ending.join(out) + tail


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
    got = set_page(page)
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
    broken = 0
    for path in args.paths:
        why = identity(path)
        if why is None:
            print(f"  set    {path}")
        else:
            broken += 1
            print(f"  DIFFERS {path} -- {why}")
    print(f"\n{len(args.paths) - broken} identical, {broken} differ")
    return 1 if broken else 0


if __name__ == "__main__":
    raise SystemExit(main())
