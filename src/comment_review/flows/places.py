"""Places from copies, and the chief's copy from decided places.

The flow's half of the middle: it knows EditCopy and Sheet, which desk does
not, and hands desk plain places.
"""

from collections.abc import Callable

from comment_review.desk.marks.table import INSTRUCTIONS, chief_mark
from comment_review.desk.proof.edit_copy import EditCopy
from comment_review.desk.proof.mark import Mark
from comment_review.desk.proof.place import Filed, Place
from comment_review.desk.proof.sheet import Sheet
from comment_review.desk.proof.state import SETTLED
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
        for address, _touch in INSTRUCTIONS[mark.instruction].places(mark):
            if address not in bases:
                bases[address], anchors[address] = held(address)
    anchors.update({mark.address: mark.anchor for mark in marks if mark.address})
    return bases, anchors


def places_of(
    copies: list[EditCopy], bases: dict[str, str], anchors: dict[str, str]
) -> dict[str, Place]:
    """One place per address any copy's mark touches, readers filled in.

    A mark is filed at every place its row says it writes at
    (`desk.marks.table.Row.places`), with the touch it has there and its
    position in `copies` -- copy, sheet and mark, each counted from 1 -- which
    is where a master proof holding these copies in this order stores it.
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
    for c, copy in enumerate(copies, 1):
        pages_by_role.setdefault(copy.role, set()).update(
            flatten(sheet.path) for sheet in copy.sheets
        )
        for s, sheet in enumerate(copy.sheets, 1):
            for m, mark in enumerate(sheet.marks, 1):
                # A `clean` may carry no address, and `places` then returns
                # none, so the mark opens no place here. That is deliberate:
                # there is no place to open, and `Row.places` is also why
                # `flows.verify.resolution_problems` never sees one to resolve.
                for address, touch in INSTRUCTIONS[mark.instruction].places(mark):
                    at(address).filed.append(Filed(copy.role, mark, touch, (c, s, m)))

    for address, place in places.items():
        page = cue_of(address).path
        place.readers = tuple(
            sorted(role for role, pages in pages_by_role.items() if page in pages)
        )
    return places


def chief_copy_of(
    decided: dict[str, Place], role: str, read_from: dict, sheets: list[Sheet]
) -> EditCopy:
    """The copy chief's edit_copy, one mark per SETTLED place the fold decided.

    An agreed move reaches this as its two ends, each an ordinary settled
    place (`decision-log.md Process: #205`): `chief_mark` writes each end from
    its own decided text, on its own page.

    !! A COMPOSED OR CONTESTED PLACE CARRIES NO MARK HERE. Its working text is
    the proof's, not the chief's copy's: the write end reads the closed
    proof's places (`decision-log.md Process: #184`), so filtering this copy
    to `SETTLED` places changes no docket, and it is what the field this
    function fills is answerable for -- a place still owed a say from some
    role is not the chief's ruling to publish as one.

    Args:
        decided: address -> the `Place` the fold settled it at.
        role: the role this copy is written for -- "copy-chief".
        read_from: `{root, revise}`, carried onto the copy.
        sheets: the pages a mark here may land on; matched to a mark's page
            by `flatten(sheet.path) == cue_of(mark.address).path`, and the
            output sheet keeps the input sheet's real `path` and `sha`.

    Returns:
        The chief's `EditCopy`, one sheet per page that holds a mark, for
        every place whose `state` is in `SETTLED` and whose `text` is not
        None.
    """
    by_path: dict[str, list[Mark]] = {}
    for address in sorted(decided):
        place = decided[address]
        if place.state not in SETTLED or place.text is None:
            continue
        mark = chief_mark(place)
        by_path.setdefault(cue_of(mark.address).path, []).append(mark)

    out = []
    for sheet in sheets:
        marks = by_path.get(flatten(sheet.path), [])
        if marks:
            out.append(Sheet(path=sheet.path, sha=sheet.sha, marks=tuple(marks)))
    return EditCopy(role=role, read_from={**read_from}, sheets=tuple(out))
