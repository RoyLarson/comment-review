"""Does a paragraph's stored text still read the way its file does?

!! IT LIVES IN `tests/` BECAUSE ITS ONLY CALLERS ARE TESTS. It shipped under
`plugins/` for one commit, as `compositor.transcribes`, and had ZERO callers
there -- every mention inside the shipped tree was a comment. Anything under
`plugins/` is copied into a user's `.claude/`, so a function nothing runs is
weight they carry for nobody; `scripts/dead_sweep.py` exists to find exactly
that shape.

! HOW IT GOT THERE. It was `galley.paragraph_matches`, which guarded the splice.
When the splice went, the function went with it -- and ten tests in two other
files broke, because they had been using it as an ORACLE rather than as a guard.
Putting it back under a new name in a shipped module answered the test failure
and not the question the failure asked, which was *where does this belong now
that nothing ships a caller for it*.

!! WHAT THE TESTS ASK OF IT IS THE OPPOSITE OF WHAT THE GALLEY ASKED. The galley
read False as *the file moved since the census*, trusting the census. A census
test reads False as *the lexer stored this wrong*, trusting the file. One
comparison, and which input it indicts is the caller's to decide -- which is
also why no single module obviously owns it.

! THE SHIPPED STALENESS CHECK IS `galley.drifted`, and it is a different
question: whether an address is still tied to the anchor the census recorded.
That one has a caller.
"""


def transcribes(paragraph: dict, lines: list[str]) -> bool:
    """Does this paragraph's stored text still read the way the file does?

    ! A PLACE THAT HOLDS NO LINE IS TRUE, not false. It has no text to disagree
    with the file about; whether prose has appeared there since is the question
    an `add` asks, and it is not this one. Answering False refused every `add` in
    a run, which is the defect this note is here to stop returning.

    Args:
        paragraph: one census entry, as `vars(b)` or from the JSON.
        lines: the file's lines, without endings.

    Returns:
        Whether the file still reads as the census recorded it.
    """
    start = paragraph.get("original_start") or 0
    end = paragraph.get("original_end") or start
    stored = paragraph.get("raw_lines") or []
    if not start or not stored:
        return True
    if start < 1 or end > len(lines) or start > end:
        return False
    here = list(lines[start - 1 : end])
    column = paragraph.get("original_column") or 0
    if column > 0:
        # ! A `c` SHARES ITS FIRST LINE WITH CODE, and the census stores both
        # halves: `anchor` is the statement, `raw_lines` is everything from the
        # column on. Together they are the physical line.
        if here[0][: column - 1] != paragraph.get("anchor", ""):
            return False
        here[0] = here[0][column - 1 :]
    return [ln.rstrip() for ln in here] == [ln.rstrip() for ln in stored]
