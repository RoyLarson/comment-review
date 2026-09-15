"""Places from copies, and the chief's copy from decided places.

The flow's half of the middle: it knows EditCopy and Sheet, which desk does
not, and hands desk plain places.
"""

from comment_review.desk.containers import EditCopy, Sheet
from comment_review.desk.evaluate.place import Filed, Place
from comment_review.desk.marks.mark import Mark
from comment_review.desk.marks.table import INSTRUCTIONS, Touch, chief_mark
from comment_review.reading.addresser import cue_of, flatten


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
        bases: `desk.collator.base_texts(binder)`.
        anchors: the page's anchors, by address.

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
    equal to one already placed on that page is skipped.

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
        mark = chief_mark(place)
        placed = by_path.setdefault(cue_of(mark.address).path, [])
        if mark not in placed:
            placed.append(mark)

    out = []
    for sheet in sheets:
        marks = by_path.get(flatten(sheet.path), [])
        if marks:
            out.append(Sheet(path=sheet.path, sha=sheet.sha, marks=tuple(marks)))
    return EditCopy(role=role, read_from={**read_from}, sheets=tuple(out))
