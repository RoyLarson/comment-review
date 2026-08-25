"""The proposed text, SET AS FILES, so it can be read and censused like any tree.

! THIS MODULE HAS NO CLI OF ITS OWN. Ruled 2026-08-24 -- `decision-log.md
Process: #12`: *"A library module does one job and has no CLI; a flow calls
libraries; a command exposes a flow."* `commands/galley.py`'s `main()` is the
console face: it resolves `--census`/`--edits` to `(path, cue)` and then calls
`reset` below, followed by `compositor.set_page`.

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

Two things needed it:

  round 2   A re-review ruled on the SYNTHESISED paragraph -- text on no disk
            and in no census -- so `address_problem` refused it and
            `edit_problem` measured one claim against one edit where the
            paragraph held several. Censusing the galley gave that text a real
            address and a real transcription, so every check in `verdicts.py`
            worked on it UNCHANGED. ! `address_problem`, `edit_problem` and
            `verdicts.py` moved to `prototype/` on 2026-08-25 and do not run
            from this tree -- see `prototype/README.md`.
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
staleness check comparing stored text, paragraph by paragraph, against the
file's lines. Roy: *"how do I get you to stop thinking in line numbers? You
keep defaulting to that and it makes a mess."* A page addresses its
paragraphs, so a replacement is an assignment and the arithmetic has nothing
left to be wrong about. See `docs/history.md` for the mechanism that was
removed.

! DID THE FILE SHIFT IS NOT ANSWERED HERE, PARAGRAPH BY PARAGRAPH, ANY MORE.
`proof_setter.run` answers it in one comparison, before anything is parsed --
the sha the binder recorded against the sha the file reads at now. See
`docs/history.md` for `drifted`, the last mechanism that asked this module.

! A CHANGE THAT CANNOT BE MADE IS REPORTED, NEVER GUESSED. An address no page
carries stops that file rather than writing a galley nobody can trust.
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
