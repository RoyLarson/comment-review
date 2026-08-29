"""Make the binder CARRY a place it dropped, so an `add` can cite it.

    binder + a page + one lookup  ->  the empty row, and a binder holding it

!! WHY IT EXISTS. `bind()` drops every place holding no prose -- 91% of them,
measured -- and `bind`'s own docstring justifies the cut by saying an empty
place stays CITABLE: *"the walk emits every place, filled or not, so a reviewer
that wants to `add` ASKS for the one it means."* This is that ask. Without it a
role can see only what already holds prose, and `add` -- whose whole finding is
that a constraint exists in code and NOWHERE in prose -- has no place to name.

!! THE PAGE IS READ AGAIN, BECAUSE THE BINDER DOES NOT CARRY WHAT IS WANTED.
The row has to be built from the walk, and the walk lives on the page. ! So the
sha is checked first: a binder taken over a file that has since changed would
otherwise gain a row describing a page nobody reviewed, and every cue below the
edit could have shifted.

! THREE LOOKUPS, because three things are known at different moments. Roy,
2026-08-26: *"look up by anchor_num, line_num, and cue."*

    cue         the agent already knows the place -- `b1`
    line        a line of the file, plus which series of it
    anchor_num  the ORDINAL of the anchor, plus which series

!! `anchor_num` IS THE ONE THAT SURVIVES AN EDIT, which is why it is here beside
the line. Roy, 2026-08-21: *"where it is in the original and where it ends up on
the resulting page can be two very different things -- but a single shift on
anchor_num and you know it is all trash after rereading."* This tool edits
prose, and every prose edit moves the line numbers below it.
"""

from comment_review.binder.binder import page_row
from comment_review.reading.addresser import SERIES, cue_of


def cue_for(
    cues, *, cue: str = "", line: int = 0, anchor_num: int = -1, series: str = ""
) -> tuple[str, str]:
    """Which place these coordinates name, or the reason they name none.

    ! IT RESOLVES ONLY. Whether that place is EMPTY, and whether the binder
    already carries it, are the caller's questions -- this one has no binder.

    Args:
        cues: the page's `Cues`.
        cue: a cue, used as given.
        line: a line of the file. Needs `series`.
        anchor_num: the ordinal of an anchor, indexing `triggers()`. Needs
            `series`.
        series: which place OF that line or anchor.

    Returns:
        `(cue, "")`, or `("", reason)`.
    """
    if cue:
        return (
            (cue, "")
            if cue in cues.places
            else ("", f"{cue}: this page has no such place")
        )
    # !! ASKED BEFORE THE SERIES, and it was asked after until a test caught it.
    # With no lookup at all the series check fired first and answered "needs
    # --series" -- naming the missing HALF of a lookup nobody had given -- which
    # left the sentence below unreachable.
    if not line and anchor_num < 0:
        return "", "give one of --cue, --line or --anchor-num"
    if series not in SERIES:
        return (
            "",
            f"a lookup by line or anchor needs --series, one of {', '.join(SERIES)}",
        )
    if line:
        # ! EACH SERIES ANSWERS A LINE ITS OWN WAY, and `Cues` states each --
        # `above` walks the triggers for the gap a line falls into, `beside`
        # asks whether the line holds code at all. There is no `a` or `f` by
        # line: a declaration's documentation is found by its ORDINAL, and the
        # file's own matter answers to the file rather than to any line.
        if series == "b":
            got = cues.above(line)
        elif series == "c":
            got = cues.beside(line)
        else:
            return "", f"--line does not name an `{series}` place; use --anchor-num"
        return (got, "") if got else ("", f"line {line}: no `{series}` place there")
    if anchor_num >= 0:
        # !! THE REVERSE OF `anchor_num`, and it is a lookup rather than
        # arithmetic. The addresser records which trigger each cue fired at, so
        # this asks that table instead of recomputing a step -- the mistake
        # `anchor_num`'s own docstring records three of.
        addresser = cues.addressers.get(series)
        if addresser is None:
            return "", f"no `{series}` addresser on this page"
        for got, trigger in addresser.trigger.items():
            if trigger == anchor_num:
                return got, ""
        return "", f"anchor {anchor_num}: no `{series}` place was emitted there"
    # ! UNREACHABLE BY CONSTRUCTION: the guard above returns when neither `line`
    # nor `anchor_num` was given, and both branches above return. It is here so
    # a future lookup added without its own branch fails loudly.
    return "", "give one of --cue, --line or --anchor-num"


def carry(binder: dict, page, path: str, **lookup) -> tuple[dict, str, str]:
    """The binder, the cue added, and the reason it was not.

    !! IT REFUSES A PLACE THAT ALREADY HOLDS PROSE. Such a place is not an
    absence to be cited; the binder is already carrying it, and adding a second
    row would put two rows on one address -- the shape `galley.reset` refuses by
    name, 157 of them measured in one tree.

    Args:
        binder: as `binder.read` returned it.
        page: the page, read fresh from the checkout.
        path: the page's path, as the binder names it.
        **lookup: passed to `cue_for`.

    Returns:
        `(binder, cue, "")` -- the same binder, mutated -- or `({}, "", reason)`.
        ! THE CUE IS RETURNED because the caller may not have supplied one: a
        `--line` or `--anchor-num` lookup resolves it here, and a caller that
        went looking for it in the rows afterwards would be re-deriving what
        this function already knew.
    """
    for held in binder.get("pages", []):
        if str(held.get("path", "")) == path:
            break
    else:
        return {}, "", f"{path}: the binder carries no such page"
    # !! THE SHA FIRST. The row is built from a page read NOW; if the file has
    # moved on, its walk describes prose nobody reviewed and the cues below any
    # edit may have shifted. Refusing is the only safe answer -- the caller
    # re-censuses and asks again.
    if str(held.get("sha", "")) != page.sha:
        return (
            {},
            "",
            (
                f"{path}: the binder records {held.get('sha') or '<nothing>'} and the"
                f" file reads now as {page.sha} -- re-run the census"
            ),
        )
    got, why = cue_for(page.cues, **lookup)
    if why:
        return {}, "", f"{path}: {why}"
    if any(str(row.get("cue", "")) == got for row in held.get("rows", [])):
        return {}, "", f"{path}@{got}: the binder already carries this place"
    for paragraph in page.paragraphs:
        if paragraph.address and cue_of(paragraph.address).cue == got:
            break
    else:
        return {}, "", f"{path}@{got}: the page has no paragraph at this place"
    if any(line.strip() for line in paragraph.raw_lines):
        return (
            {},
            "",
            (
                f"{path}@{got}: this place holds prose, so it is not an absence."
                " A filled place is already in the binder"
            ),
        )
    # !! INSERTED IN READING ORDER, not appended. A binder's rows are the page
    # top to bottom -- that is what a reviewer reads -- and a row on the end
    # would put the file's first gap after its last comment.
    order = list(page.cues.reading)
    rows = held.setdefault("rows", [])
    rows.append(page_row(paragraph))
    rows.sort(
        key=lambda row: (
            order.index(str(row.get("cue", "")))
            if str(row.get("cue", "")) in order
            else len(order)
        )
    )
    return binder, got, ""
