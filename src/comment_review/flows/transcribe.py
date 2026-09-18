"""TRANSCRIBE -- one edit_copy, folded, as the docket the write chain reads.

    docket_of(copy, repo) -> Docket

!! IT FOLDS, AND THAT IS WHAT MAKES IT A TRANSCRIPTION OF DECIDED PLACES. The
copy's marks are turned into places (`flows.places.places_of`), the Unit of
Work decides every one of them, and each place the fold settled a text for
becomes one alteration. Nothing here reads a mark's `change` or asks which end
of a `move` it is looking at: the marks table answered both when the fold ran,
and a place carries one text whatever produced it.

!! A ROLLED-BACK FOLD IS A REFUSAL, NOT AN EMPTY DOCKET. `CannotTranscribe`
carries the events' own reasons, and `commands/proof.py` prints them. An empty
docket would say the copy asked for nothing, which is the opposite of a copy
whose marks could not be read.

!! ANY COPY, NOT ONLY THE COPY CHIEF'S. Roy, 2026-09-02: *"it could also be
ownership contexts edit-copy or any intermediate edit-copy which allows the stage
outputs to run."* A stage's own output therefore becomes a revise, which is the
mechanism `reads = "revise:N"` and stage `4b` both need. `decision-log.md
Process: #76`.

!! IT IS ITS OWN FLOW BECAUSE IT IS ITS OWN ACT. It lived in `flows/revise.py`
until `P55`+, whose docstring describes exactly one job -- *"Pull a revise: a
second proof of the pages one stage's corrections set"* -- which transcription
is not: `pull` never calls this, and `commands/proof.py` calls both. Every other
flow file here -- `distribute.seed`, `fan_out.fan`, `mark_errors.mark_errors`,
`proof_setter.run` -- exposes one act.

!! AND IT IS A FLOW BECAUSE A FLOW MAY REACH BOTH ENDS AND NEITHER END MAY REACH
THE OTHER. Roy, 2026-08-31: *"No direct coupling inside of ends and middle, flows
are neither they run the steps."* This reads the pages, builds the MIDDLE's
places, runs the fold, and builds the WRITE END's `Docket`; `Docket.of(edit_copy)`
was offered and declined, because it would put a middle type in
`docket/docket.py`, which imports nothing at all.
"""

from pathlib import Path

from comment_review.binder.page import Page
from comment_review.desk.containers import EditCopy
from comment_review.desk.marks.mark import Mark
from comment_review.desk.marks.table import INSTRUCTIONS, Touch
from comment_review.desk.work import events
from comment_review.desk.work.fold import Fold
from comment_review.docket.docket import Alteration, Docket, Schedule
from comment_review.flows.page_for import page_of
from comment_review.flows.places import places_of
from comment_review.machine.repo import can_escape
from comment_review.reading.addresser import SEPARATOR, cue_of, flatten, unflatten


class CannotTranscribe(Exception):
    """The fold over this copy rolled back, so it decided nothing to set.

    Attributes:
        reasons: one line per refusal the fold reported, naming the role, the
            place and what the row found there.
    """

    def __init__(self, reasons: tuple[str, ...]) -> None:
        """Hold the fold's own reasons and say them in the message too."""
        super().__init__("; ".join(reasons))
        self.reasons = reasons


def _touched(mark: Mark) -> tuple[str, ...]:
    """Every address this one mark writes at, as its row states them.

    A `move` is the row with two touches, and its destination is `claim.to`;
    every other row writes at the mark's own address alone.
    """
    return tuple(
        str(mark.claim.get("to", "")) if touch is Touch.DESTINATION else mark.address
        for touch in INSTRUCTIONS[mark.instruction].touches
    )


def _real_path(name: str, known: list[str]) -> str:
    """The real relative path a flattened address half names.

    `unflatten` answers from the paths in hand, which is every page the copy
    holds a sheet for. A `move`'s destination may be on a page it holds none
    for -- the chief's copy files a move under its origin's page -- and the
    flattened form is invertible by construction, since `gather` refuses a
    path holding the separator, so the plain substitution answers there.
    """
    return unflatten(name, known) or name.replace(SEPARATOR, "/")


def _pages_of(copy: EditCopy, repo: Path) -> dict[str, tuple[str, Page]]:
    """Every page this copy's marks touch, read from `repo`.

    Returns:
        The flattened page name -> `(its real relative path, the page)`, in
        the copy's own sheet order and then in the order a destination first
        names a page the copy has no sheet for. A page that cannot be read,
        or whose path would escape the checkout, is left out: it carries no
        base, no anchor and no schedule.
    """
    known = [sheet.path for sheet in copy.sheets]
    names = [flatten(path) for path in known]
    names += [
        cue_of(address).path
        for sheet in copy.sheets
        for mark in sheet.marks
        for address in _touched(mark)
        if cue_of(address).path
    ]
    out: dict[str, tuple[str, Page]] = {}
    for name in names:
        if name in out:
            continue
        rel = _real_path(name, known)
        if not rel or can_escape(rel):
            continue
        page, _why = page_of(repo / rel, rel=rel)
        if page is not None:
            out[name] = (rel, page)
    return out


def docket_of(copy: EditCopy, repo: Path) -> Docket:
    """One edit_copy, folded and transcribed into the docket the write chain reads.

    Args:
        copy: a returned edit_copy, already through `EditCopy.deserialize`.
        repo: the checkout whose pages the write end sets. Every base and
            every anchor is read from it, so what the fold measures a mark
            against is the page rather than the mark's own account of it.

    Returns:
        A `Docket` -- one `Schedule` per page the fold decided a text on, each
        naming that page's own path and sha and the COPY's role. An alteration
        carries the page's anchor at its place (`decision-log.md Process:
        #134` and `#135`) and its text, with an emptied place written as the
        `None` the write end reads as a delete.

        A place the fold decided no text for gets no alteration: a `clean` and
        a `query` propose none, and neither does a place every role left
        alone (`Process: #174`). A page with no alteration gets no schedule,
        since an empty one would tell the write end to set a page from
        nothing.

    Raises:
        CannotTranscribe: the fold rolled back. Nothing it reported can be
            set, and the reasons are the report.
    """
    pages = _pages_of(copy, repo)
    bases: dict[str, str] = {}
    anchors: dict[str, str] = {}
    for name, (_rel, page) in pages.items():
        for paragraph in page.paragraphs:
            if paragraph.address:
                bases[paragraph.address] = paragraph.raw_text
        for cue, anchor in page.cues.places.items():
            anchors[f"{name}@{cue}"] = anchor
    # !! A MARK'S OWN ANCHOR WINS AT ITS OWN ADDRESS, and the page's stands
    # only where no mark names the place -- a move's destination. The write
    # end refuses an alteration whose anchor is not the page's there
    # (`decision-log.md Process: #134`), and that check has something to
    # refuse only while what reaches it is the anchor the ROLE returned: taken
    # from the page here, it would compare the page with itself.
    anchors.update(
        {
            mark.address: mark.anchor
            for sheet in copy.sheets
            for mark in sheet.marks
            if mark.address
        }
    )

    fold = Fold(places_of([copy], bases, anchors)).run()
    if not fold.committed:
        raise CannotTranscribe(
            tuple(
                f"{one.role} {one.address}: {why}"
                for one in fold.events
                if isinstance(one, events.Refused)
                for why in one.reasons
            )
        )

    decided: dict[str, list] = {}
    for address, place in fold.decided.items():
        if place.text is not None:
            decided.setdefault(cue_of(address).path, []).append(place)

    shas = {flatten(sheet.path): sheet.sha for sheet in copy.sheets}
    schedules = []
    for name, (rel, page) in pages.items():
        here = decided.get(name)
        if not here:
            continue
        order = list(page.cues.places)
        here.sort(key=lambda place: order.index(cue_of(place.address).cue))
        schedules.append(
            Schedule(
                path=rel,
                # ! THE SHEET'S SHA WHERE THE COPY CARRIES ONE, since that is
                # the bytes its addresses were taken from. A page only a
                # move's destination names has no sheet and so no recorded
                # sha, and the page read here is the only one there is.
                sha=shas.get(name, page.sha),
                alterations=tuple(
                    Alteration(
                        cue=cue_of(place.address).cue,
                        text=place.text or None,
                        anchor=place.anchor,
                    )
                    for place in here
                ),
                role=copy.role,
            )
        )
    return Docket(schedules=tuple(schedules))
