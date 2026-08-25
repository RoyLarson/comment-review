"""The proposed text, SET AS FILES, so it can be read and censused like any tree.

    python galley.py --repo D --census census.json --edits edits.json --out DIR

`--edits` is `{"<address>": "<the replacement text>"}` -- the address the
record carries. `reset` below does not take that address: resolving it to
`(path, cue)` happens upstream, from the address itself, before a cue and
its replacement ever reach this module.

A galley is the trial impression: the text set, but not yet made into pages, so
that it can be corrected before anything is committed. That is exactly what
this writes -- every paragraph a stage proposes to change, put on a copy of its
page under `--out`. Nothing under `--repo` is touched.

!! "NOT YET MADE INTO PAGES" AND "A COPY OF ITS PAGE" ARE BOTH TRUE HERE, and
reading the first as a contradiction of the second is the wrong inference this
paragraph invites. Roy, 2026-08-22: *"Galley still works because our pages are
infinite lengths, and can be reordered at will to make them look like one
unordered length."* ! A page here is a FILE: unbounded, no verso, and nothing
pushes its last line onto a next sheet. Making up copy into fixed-height sheets
-- the step a galley precedes -- never happens in this system at all, so setting
text onto a page does not stop it being galley copy.

! AND THE STACK IS ORDER-FREE, which is the second half of what makes the word
hold. Every address carries its own path, so nothing downstream depends on which
page precedes which. MEASURED 2026-08-22: three files censused forward and
reversed gave 179 paragraphs whose address, kind, text and anchor were identical
in both orders. ! Order is load-bearing WITHIN a page -- that is what an
address's cue counts -- and free between them.

!! IT RENDERS; IT DOES NOT RULE. A stage that both produced the galley and
judged it would be MARK and APPLY in one actor, which is the separation the
pipeline exists to keep.

Two things need it, and they needed the same thing:

  round 2   A re-review rules on the SYNTHESISED paragraph -- text on no disk and
            in no census -- so `address_problem` refuses it and `edit_problem`
            measures one claim against one edit where the paragraph now holds
            several. Censusing the galley gives that text a real address and a
            real transcription, so every check in `verdicts.py` works on it
            UNCHANGED.
  stage 7a  What lands at 7b is a paragraph set into a page, and the galley is
            the first time anyone sees the two together. `git diff --no-index`
            over it shows the author what will land, including whether a
            neighbour moved -- which a `CHANGE` cannot show, because each one
            carries only its own surrounding context.

!! IT DOES TWO THINGS AND THEY ARE SEPARATE ACTS. Roy, 2026-08-21: *"galley gets
the old page - updates the old page with the verdict/record/marks and then a
page-setter sets the page to rewrite the output text."*

    RESET   the verdicts are put on the page, by CUE
    SET     `compositor.set_page` turns the page back into text

! THIS MODULE OWNS ONLY THE FIRST. Setting belongs to the compositor, which is
the only writer, and it decides nothing.

!! NO LINE NUMBER APPEARS IN THIS FILE. Until 2026-08-21 the whole module was
line arithmetic -- a splice over `(start, end, column)` ranges applied in
descending order so that earlier edits did not shift later ones, with a
staleness check comparing stored text against the file's lines. Roy: *"how do I
get you to stop thinking in line numbers? You keep defaulting to that and it
makes a mess."* A page addresses its paragraphs, so a replacement is an
assignment and the arithmetic has nothing left to be wrong about. See
`docs/history.md` for the mechanism that was removed.

! A CHANGE THAT CANNOT BE MADE IS REPORTED, NEVER GUESSED. An address no page
carries, or an anchor that moved since the census, stops that file rather than
writing a galley nobody can trust.
"""

from comment_review.machine import constants

# !! THE ONE `cue_of`, since 2026-08-22. This module had a second of its own --
# `str(address).split("@")[-1]` -- and the two DISAGREED on a malformed address:
# a bare `b3` with no `@` came back as the cue `b3` here and as *not an
# address* from `addresser`, which returns two blanks when there is no separator.
# Both were live in one process. ! The shared one answers `(path, cue)`, so
# every site here takes `[1]`.
from comment_review.reading.addresser import ON, cue_of


def reset(page, edits: dict[str, str | None]) -> list[str]:
    """Put each replacement on the page, at the place its cue names.

    !! IT IS HANDED A PAGE AND CUES, AND RESOLVES NEITHER. Roy, 2026-08-25:
    *"the galley shouldn't be resolving the page ... it should get handed the
    page, the cues-new text or a delete."* A page names its own file, so the
    path half of an address is a fact the caller already had.

    !! `None` IS THE DELETE AND `""` IS REFUSED. Roy, 2026-08-25: *"None is
    explicit enough."* ! An empty string was the vacation signal until then,
    which made a failed serialisation upstream indistinguishable from a
    deliberate deletion.

    !! THE ADDRESS IS THE WHOLE OF THE PLACEMENT. A paragraph knows which place
    it sits in, and the compositor sets the places in order, so a replacement is
    an assignment to one paragraph and nothing below it moves. That is the
    difference between this and the splice it replaces: growing a paragraph from
    one line to four used to shift every range below it.

    !! A PLACE IS NEVER REMOVED -- IT IS VACATED. Places are involatile: the
    place takes the empty sentinel and does not itself disappear, so `drop`
    deletes nothing and the paragraph stays, at the same address, holding no
    lines. That is what keeps it citable afterwards --
    an `add` can fill the very place a `drop` emptied.

    !! `drop` AND THE SOURCE HALF OF A `move` ARE THE SAME OPERATION, and both
    go through `_vacate`. A `move` is expressed as two edits -- the destination
    takes the text, the source takes an empty replacement -- and the source is
    vacated exactly as a `drop` vacates, because in both cases the prose is no
    longer there and the space it introduced is no longer owed.

    ! THE LEADING BELOW IT IS VACATED TOO, for the same reason and by the same
    rule -- the live first key keeps its leading, the dropped one loses it. The
    `d` becomes the empty sentinel; it does not cease to exist.
    Without it the blank line the paragraph introduced stands over whatever
    follows.

    !! AND IT IS AN EDITORIAL DECISION MADE HERE, not in the compositor. It read
    as a side-effect there until 2026-08-22 -- the loop skipped a place that set
    nothing, so its edge was never asked for -- which had the module chartered
    to decide NOTHING carrying out a `drop`. ! It could not have been right
    there in any case: an emptied place and an always-empty one hold the SAME
    empty sentinel, so the compositor cannot tell them apart. Only the EDIT
    knows.

    ! A `c` TAKES ONLY THE PROSE. The compositor sets the line of code and joins
    what sits beside it, so the replacement is the comment and its separator --
    never the statement. That is what makes `c` writable without a column.

    Args:
        page: the page to change, built from the file as it reads NOW.
        edits: cue -> the replacement paragraph as text, or None to vacate.

    Returns:
        One sentence per edit that could not be placed. Empty means every one
        landed.
    """
    by_place: dict[str, list] = {}
    # ! The `d` a place owns, so a `drop` can empty it too. Leading carries a
    # SYMBOL and never an address -- it names no place -- so it is found here by
    # that symbol and nowhere by a cue.
    by_symbol = {b.symbol: b for b in page if b.symbol}
    for b in page:
        if b.address:
            by_place.setdefault(cue_of(b.address).cue, []).append(b)
    refused = []
    for where, replacement in edits.items():
        found = by_place.get(where)
        if not found:
            refused.append(f"{where}: this page carries no such place")
            continue
        # !! ONE PLACE, ONE PARAGRAPH. Two paragraphs sharing an address was a
        # real defect until 2026-08-21 -- 157 of them in one tree -- and it is
        # the one shape that would make a replacement ambiguous here. It is
        # reported rather than resolved: picking either would write the author's
        # approved text over prose nobody looked at.
        if len(found) > 1:
            refused.append(
                f"{where}: {len(found)} paragraphs share this place, so no"
                " replacement can be placed against it"
            )
            continue
        if replacement is None:
            owns_leading = not where.startswith(ON)
            _vacate(
                found[0],
                by_symbol.get(page.leading.get(where, "")) if owns_leading else None,
            )
            continue
        if not isinstance(replacement, str):
            refused.append(
                f"{where}: a replacement must be text or None, not"
                f" {type(replacement).__name__}"
            )
            continue
        if not replacement:
            refused.append(f"{where}: an empty string is not a delete -- None is")
            continue
        found[0].raw_lines = constants.text_lines(replacement)
    return refused


def _vacate(paragraph, leading) -> None:
    """Empty this place and the space below it, without removing either.

    !! THE EMPTY SENTINEL IS THE POINT: the place takes it, and does not itself
    disappear. Both paragraphs keep their address, their anchor and their
    position in the reading order; they hold no lines. A place that vanished
    could not be cited
    by the `add` that fills it next.

    Args:
        paragraph: the place being vacated.
        leading: the `d` it owns, or None where nothing blank follows it.
    """
    paragraph.raw_lines = []
    if leading is not None:
        leading.raw_lines = []


def drifted(page, census: list[dict]) -> list[str]:
    """Addresses whose ANCHOR is no longer the one the census recorded.

    !! THIS IS THE WHOLE STALENESS CHECK, AND IT ASKS THE WHOLE FILE. Roy,
    2026-08-21, ruling on the scope after a narrower reading was measured: *"If
    the file shifted at all it is dead and so are the edits. There is no way we
    can know if we are setting things correctly ... IT failing loudly is the
    'right' call on any modification to the anchors."*

    !! CHECKING ONLY THE ADDRESS BEING WRITTEN IS NOT ENOUGH, MEASURED. Rename
    `def f():` to `def RENAMED():` and edit a comment inside its body: that
    comment's own address is anchored to `    return 1`, which did not move, so
    a per-address check ALLOWS IT -- and the approved text describing `f` is
    written onto a declaration that no longer carries the name. The paragraph a
    reviewer read did not move; the thing it is ABOUT did.

    !! AND RE-ADDRESSING THE EDITS WOULD NOT SAVE THEM, WHICH IS WHY THERE IS NO
    PARTIAL ANSWER. Roy: *"it seems easy just keep applying until it no longer
    applies, but then the edits also no longer apply ... what is stated in the
    edits could be stale and need something else."*

    ! THE STALENESS IS IN THE TEXT, NOT ONLY IN THE PLACEMENT. A replacement is
    prose ABOUT code, approved against the code as it read. Move that code and
    the sentence can become false where it was true -- a comment that described
    `f` is not made correct by finding the right place to put it on `RENAMED`.
    So there is no re-keying shortcut: the shortcut assumes the words still
    hold, and that is the assumption the shift breaks.

    ! WHAT IS OWED IS A NEW REVIEW, not a new address. Re-censusing and
    re-running is the answer, and it is the author's to trigger.

    ! SO AN UNRELATED APPEND AT THE FOOT OF THE FILE REFUSES THE WHOLE PAGE, and
    that is the rule rather than a cost of it -- measured as case D of the sweep
    above: `X = 1` appended below everything moves the closing gap's anchor.

    ! IT REPLACES A COMPARISON OF STORED TEXT AGAINST THE FILE'S LINES. That one
    asked whether the paragraph still reads as it did, which is a fact about
    lines and needed a case for every kind -- a `c` compared in two halves, an
    empty place compared for emptiness, an undocumented declaration exempted.
    The anchor is one comparison and it holds for every series that has one.

    ! A SERIES WITH NO ANCHOR IS NOT CHECKED, and that is not a hole. Leading
    answers to nothing by ruling, and the file's own matter answers to the
    module -- neither can drift against a line of code, because neither is tied
    to one.

    Args:
        page: the page as the file reads NOW.
        census: the paragraphs the reviewers read.

    Returns:
        One sentence per address whose anchor moved.
    """
    now = {}
    prose_now: dict[str, list[str]] = {}
    for b in page:
        if b.address and b.anchor:
            now[cue_of(b.address).cue] = b.anchor
        if b.address:
            prose_now[cue_of(b.address).cue] = list(b.raw_lines)
    out = []
    for b in census:
        address = str(b.get("address", ""))
        # !! THE PROSE IS CHECKED TOO, and only the anchor was. An anchor is a
        # line of CODE, so a comment edited since the census moved nothing the
        # anchor can see -- and the galley wrote the reviewer's approved text
        # over prose nobody had read. MEASURED 2026-08-22 side by side on one
        # census: a code change refused correctly at exit 1 naming three moved
        # anchors, while replacing one comment with two unreviewed lines gave
        # exit 0 and overwrote both.
        #
        # ! IT IS THE RULE THIS FUNCTION ALREADY QUOTES. Roy: *"If the file
        # shifted at all it is dead and so are the edits."* A prose edit is the
        # file shifting; the anchor comparison simply could not see it.
        #
        # ! ONE COMPARISON, EVERY KIND -- which was the objection to the text
        # check this replaced. That one asked whether the paragraph still READS
        # as it did and needed a case per kind; `raw_lines` is the lines
        # themselves, and the census records them for every paragraph it carries.
        #
        # ! IT ALSO COVERS THE SERIES WITH NO ANCHOR. Leading and the file's own
        # matter answer to no line of code, so the anchor test skipped them
        # entirely; their prose can still be edited, and now that is seen.
        # ! NOTHING WITHOUT AN ADDRESS IS COMPARED AT ALL, so it is asked here
        # rather than in each of the two checks below -- which tested it in
        # opposite directions inside one loop body, with nothing between them
        # that could change the answer.
        if not address:
            continue
        # ! THE CENSUS EMITS ONE STRING since 2026-08-24; the PAGE still
        # holds lines, so the comparison joins the page side to match. What
        # a paragraph IS in memory did not change -- see
        # `census.emitted_row`.
        stored = b.get("raw_text")
        if isinstance(stored, str):
            here_lines = prose_now.get(cue_of(address).cue)
            if here_lines is not None and "\n".join(here_lines) != stored:
                out.append(
                    f"{address}: the prose here changed since the census"
                    f" -- {len(stored.splitlines())} line(s) read,"
                    f" {len(here_lines)} now"
                )
        was = str(b.get("anchor", ""))
        if not was:
            continue
        here = now.get(cue_of(address).cue)
        if here is not None and here != was:
            out.append(
                f"{address}: the census read {was!r}, the file now reads {here!r}"
            )
    return out
