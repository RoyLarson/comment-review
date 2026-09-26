"""Places from copies, and the chief's copy from decided places.

The flow's half of the middle: it knows EditCopy and Sheet, which desk does
not, and hands desk plain places.
"""

from collections.abc import Callable

from comment_review.desk.containers import EditCopy, Sheet
from comment_review.desk.evaluate.place import Filed, Place
from comment_review.desk.marks.mark import Mark
from comment_review.desk.marks.table import INSTRUCTIONS, Touch, chief_mark
from comment_review.flows.fill import touched_by
from comment_review.flows.on_the_page import Held
from comment_review.reading.addresser import cue_of, flatten


def bases_and_anchors(
    copies: list[EditCopy], held: Callable[[str], Held]
) -> tuple[dict[str, str], dict[str, str]]:
    """The base text and the anchor of every place the copies' marks touch.

    The base is the page's text at the place, whether or not the binder holds
    it (`decision-log.md Process: #187`, `#125`), so a move into a file the
    run did not gather is measured against the paragraph already there.

    The anchor is the page's, except at a mark's own address, where it is the
    one the role returned: the write end checks an alteration's anchor
    against the page's and refuses one that differs (`Process: #134`), which
    it can only do while what reaches it is the role's. A move's destination
    has no mark of its own, so it takes the page's.

    Args:
        copies: the roles' returned copies, or the one copy a draft folds.
        held: address -> what the page holds there, through the caller's own
            page cache (`flows.on_the_page.held_at`).

    Returns:
        `(address -> base, address -> anchor)`, for `places_of`.
    """
    marks = [mark for copy in copies for sheet in copy.sheets for mark in sheet.marks]
    bases: dict[str, str] = {}
    anchors: dict[str, str] = {}
    for mark in marks:
        for address, _touch in touched_by(mark):
            if address not in bases:
                bases[address], anchors[address] = held(address)
    anchors.update({mark.address: mark.anchor for mark in marks if mark.address})
    return bases, anchors


def places_of(
    copies: list[EditCopy], bases: dict[str, str], anchors: dict[str, str]
) -> dict[str, Place]:
    """One place per address any copy's mark touches, readers filled in.

    A move files at its origin with `Touch.ORIGIN` and at `claim["to"]` with
    `Touch.DESTINATION`, and the two places name each other as `partner`.
    `readers` is every role whose copy holds a sheet for the address's page
    (Ruling R4: an add is carried forward for every role that read the page).

    Args:
        copies: the roles' returned copies for this stage.
        bases: each touched place's text, as `bases_and_anchors` reads it.
        anchors: each touched place's anchor, the same way.

    Returns:
        address -> the `Place` built there.
    """
    places: dict[str, Place] = {}

    def at(address: str) -> Place:
        if address not in places:
            places[address] = Place(
                address=address,
                anchor=anchors.get(address, ""),
                base=bases.get(address, ""),
            )
        return places[address]

    pages_by_role: dict[str, set[str]] = {}
    for copy in copies:
        pages_by_role.setdefault(copy.role, set()).update(
            flatten(sheet.path) for sheet in copy.sheets
        )
        for sheet in copy.sheets:
            for mark in sheet.marks:
                row = INSTRUCTIONS[mark.instruction]
                if row.touches == (Touch.OWN,):
                    at(mark.address).filed.append(Filed(copy.role, mark, Touch.OWN))
                    continue
                destination = str(mark.claim.get("to", ""))
                origin, other = at(mark.address), at(destination)
                origin.filed.append(Filed(copy.role, mark, Touch.ORIGIN))
                other.filed.append(Filed(copy.role, mark, Touch.DESTINATION))
                origin.partner, other.partner = destination, mark.address

    for address, place in places.items():
        page = cue_of(address).path
        place.readers = tuple(
            sorted(role for role, pages in pages_by_role.items() if page in pages)
        )
    return places


def chief_copy_of(
    decided: dict[str, Place], role: str, read_from: dict, sheets: list[Sheet]
) -> EditCopy:
    """The copy chief's edit_copy, one mark per place the fold decided a text for.

    A move reached from both of its places (its origin and its destination)
    contributes one entry: `chief_mark` returns the same taken-in `Mark` --
    whose own `address` is always the origin -- from either place, so a mark
    equal to one already placed on that page is skipped. It is taken in only
    where both ends closed on what it sets, which is why the partner is
    handed over: a move whose destination the chief recast is not what
    happened, and each end is then written from its own decided text.

    Args:
        decided: address -> the `Place` the fold settled it at.
        role: the role this copy is written for -- "copy-chief".
        read_from: `{root, revise}`, carried onto the copy.
        sheets: the pages a mark here may land on; matched to a mark's page
            by `flatten(sheet.path) == cue_of(mark.address).path`, and the
            output sheet keeps the input sheet's real `path` and `sha`.

    Returns:
        The chief's `EditCopy`, one sheet per page that holds a mark.
    """
    by_path: dict[str, list[Mark]] = {}
    for address in sorted(decided):
        place = decided[address]
        if place.text is None:
            continue
        mark = chief_mark(place, decided.get(place.partner or ""))
        placed = by_path.setdefault(cue_of(mark.address).path, [])
        if mark not in placed:
            placed.append(mark)

    out = []
    for sheet in sheets:
        marks = by_path.get(flatten(sheet.path), [])
        if marks:
            out.append(Sheet(path=sheet.path, sha=sheet.sha, marks=tuple(marks)))
    return EditCopy(role=role, read_from={**read_from}, sheets=tuple(out))
