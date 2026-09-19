"""TRANSCRIBE -- decided places, as the docket the write chain reads.

    docket_of(copy, repo)        one edit_copy, folded
    docket_of_proof(proof, repo) one closed master proof, read

Two inputs, one output, and they differ in where the decision comes from. A
copy is folded here: its marks are turned into places
(`flows.places.places_of`), the Unit of Work decides every one of them, and
each place the fold settled a text for becomes one alteration. A closed proof
already holds every place the fold decided, so nothing is folded again -- the
places are read back and each whose text differs from its base becomes one
alteration.

The proof is what the write end reads, ruled `decision-log.md Process: #184`.
The chief's copy restated the same decisions as marks, found or synthesized,
and folding those marks a second time made the docket depend on that restatement
reproducing the first fold exactly. `docket_of` stays for a role's own draft,
which is the artifact it was written for.

Neither path reads a mark's `change` or asks which end of a `move` it is
looking at: the marks table answered both when the fold ran, and a place
carries one text whatever produced it.

A rolled-back fold is a refusal, not an empty docket. `CannotTranscribe`
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
are neither they run the steps."* This reads the pages, builds the middle's
places, runs the fold, and builds the write end's `Docket`;
`Docket.of(edit_copy)`
was offered and declined, because it would put a middle type in
`docket/docket.py`, which imports nothing at all.
"""

from pathlib import Path

from comment_review.binder.page import Page
from comment_review.desk.containers import EditCopy, MasterProof
from comment_review.desk.dispositions.disposition import CHIEF
from comment_review.desk.evaluate.place import Place
from comment_review.desk.evaluate.state import CARRIED, State
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


def _touched_by_page(copy: EditCopy) -> dict[str, list[str]]:
    """The flattened page name -> every address this copy's marks write there.

    Sorted within a page, so two runs over one copy name them in one order.
    A mark carrying no address -- the one row that may -- names no page.
    """
    out: dict[str, list[str]] = {}
    for sheet in copy.sheets:
        for mark in sheet.marks:
            for address in _touched(mark):
                name = cue_of(address).path
                if name and address not in out.setdefault(name, []):
                    out[name].append(address)
    return {name: sorted(addresses) for name, addresses in out.items()}


def _pages_of(
    repo: Path, known: list[str], touched: dict[str, list[str]], who: str, noun: str
) -> tuple[dict[str, tuple[str, Page]], list[str]]:
    """Every page a transcription writes at, read from `repo`, and what would not read.

    A page this checkout cannot answer for is a refusal rather than an
    omission: it would get no schedule, and the run would draft as though the
    rulings there had never been made. A page named among `known` and written
    at by nothing is not missed, since nothing was going to be set there.

    Args:
        repo: the checkout every page is read from.
        known: the real relative paths the input records -- a copy's sheets,
            or a proof's. They are what `unflatten` inverts a flattened name
            against, and their order is the order the schedules come out in.
        touched: flattened page name -> the addresses to be set there.
        who: whose transcription this is, for the reasons -- a role, or the
            chief where a fold decided the places.
        noun: what is owed at those addresses, for the reasons.

    Returns:
        `(the flattened page name -> (its real relative path, the page), the
        reasons)`, the pages in `known`'s order and then in the order
        `touched` first names one that is not among them. A reason names
        `who`, the page and every address on it.
    """
    names = [flatten(path) for path in known] + list(touched)
    out: dict[str, tuple[str, Page]] = {}
    refused: list[str] = []
    # A page the copy holds a sheet for and files a mark on is named twice,
    # so what has been read already is tracked rather than tested for on
    # `out` -- which a page that would not read never reaches.
    seen: set[str] = set()
    for name in names:
        if name in seen:
            continue
        seen.add(name)
        rel = _real_path(name, known)
        page = None
        if rel and not can_escape(rel):
            page, _why = page_of(repo / rel, rel=rel)
        if page is not None:
            out[name] = (rel, page)
        elif name in touched:
            refused.append(
                f"{who} {rel or name}: this checkout has no page here, so"
                f" the {noun} at {', '.join(touched[name])} cannot be set"
            )
    return out, refused


def _schedules_of(
    pages: dict[str, tuple[str, Page]],
    decided: dict[str, list[Place]],
    shas: dict[str, str],
    role: str,
) -> tuple[Schedule, ...]:
    """One schedule per page a text was decided on, each page's places in order.

    Args:
        pages: what `_pages_of` returned -- the flattened name -> (the real
            relative path, the page).
        decided: flattened page name -> the places to set there, in any order.
        shas: flattened page name -> the sha recorded for it, where one was.
        role: the role written onto every schedule -- the copy a docket was
            pulled from, or the chief where a fold decided the places.

    Returns:
        The schedules, in `pages`' own order. A page with nothing to set gets
        none, since an empty schedule would tell the write end to set a page
        from nothing.
    """
    schedules: list[Schedule] = []
    for name, (rel, page) in pages.items():
        here = decided.get(name)
        if not here:
            continue
        # Set in the page's own place order. A cue the page does not carry
        # sorts last rather than raising: the write end is what refuses it,
        # by name, and a console face here would hand over a traceback.
        order = list(page.cues.places)
        here.sort(
            key=lambda place: (
                order.index(cue_of(place.address).cue)
                if cue_of(place.address).cue in order
                else len(order)
            )
        )
        schedules.append(
            Schedule(
                path=rel,
                # The recorded sha where the input carries one, since that is
                # the bytes its addresses were taken from. A page only a
                # move's destination names was never gathered and so has no
                # recorded sha; the page read here is the only one there is.
                sha=shas.get(name, page.sha),
                alterations=tuple(
                    Alteration(
                        cue=cue_of(place.address).cue,
                        text=place.text or None,
                        # The anchor the role returned wins, and the page's
                        # stands where the place holds none -- a move's
                        # destination, which no mark is addressed to. The
                        # write end refuses an alteration whose anchor is not
                        # the page's there (`decision-log.md Process: #134`),
                        # and that check has something to refuse only while
                        # what reaches it is the anchor the role returned.
                        anchor=place.anchor
                        or page.cues.places.get(cue_of(place.address).cue, ""),
                    )
                    for place in here
                ),
                role=role,
            )
        )
    return tuple(schedules)


def docket_of(copy: EditCopy, repo: Path) -> Docket:
    """One edit_copy, folded and transcribed into the docket the write chain reads.

    Args:
        copy: a returned edit_copy, already through `EditCopy.deserialize`.
        repo: the checkout whose pages the write end sets. Every base and
            every anchor is read from it, so what the fold measures a mark
            against is the page rather than the mark's own account of it.

    Returns:
        A `Docket` -- one `Schedule` per page the fold decided a text on, each
        naming that page's own path and sha and the copy's own role. An alteration
        carries the page's anchor at its place (`decision-log.md Process:
        #134` and `#135`) and its text, with an emptied place written as the
        `None` the write end reads as a delete.

        A place the fold decided no text for gets no alteration: a `clean` and
        a `query` propose none, and neither does a place every role left
        alone (`Process: #174`). A page with no alteration gets no schedule,
        since an empty one would tell the write end to set a page from
        nothing.

    Raises:
        CannotTranscribe: a page a mark writes at cannot be read here, or the
            fold rolled back. Nothing it reported can be set, and the reasons
            are the report.
    """
    pages, unreadable = _pages_of(
        repo,
        [sheet.path for sheet in copy.sheets],
        _touched_by_page(copy),
        copy.role,
        "marks",
    )
    if unreadable:
        raise CannotTranscribe(tuple(unreadable))
    # A mark the envelope could not read is a decision nobody can write, and
    # the fold below never sees it -- `Sheet.refused` holds it instead of
    # `Sheet.marks`. Transcribing the rest would drop that place from the
    # docket without a word, which is how a landing goes missing from a run
    # that reports nothing wrong.
    refused = [
        f"{copy.role} {one.where}: {why}"
        for sheet in copy.sheets
        for one in sheet.refused
        for why in one.reasons
    ]
    if refused:
        raise CannotTranscribe(tuple(refused))
    bases: dict[str, str] = {}
    anchors: dict[str, str] = {}
    for name, (_rel, page) in pages.items():
        for paragraph in page.paragraphs:
            if paragraph.address:
                bases[paragraph.address] = paragraph.raw_text
        for cue, anchor in page.cues.places.items():
            anchors[f"{name}@{cue}"] = anchor
    # A mark's own anchor wins at its own address, and the page's stands only
    # where no mark names the place -- a move's destination. The write end
    # refuses an alteration whose anchor is not the page's there
    # (`decision-log.md Process: #134`), and that check has something to
    # refuse only while what reaches it is the anchor the role returned:
    # taken from the page here, it would compare the page with itself.
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

    decided: dict[str, list[Place]] = {}
    for address, place in fold.decided.items():
        if place.text is not None:
            decided.setdefault(cue_of(address).path, []).append(place)

    shas = {flatten(sheet.path): sheet.sha for sheet in copy.sheets}
    return Docket(schedules=_schedules_of(pages, decided, shas, copy.role))


def _places_on(proof: MasterProof) -> tuple[list[Place], list[str]]:
    """Every place this proof carries, parsed, and every reason one would not.

    A place is read back the way a returned copy's marks are, and one that
    will not parse is named rather than dropped: transcribing the rest would
    take that place out of the docket without a word, which is how a landing
    goes missing from a run that reports nothing wrong.

    Returns:
        `(the places, the reasons)`, the places in the proof's own order.
    """
    places: list[Place] = []
    problems: list[str] = []
    for i, entry in enumerate(proof.places, 1):
        where = str(entry.get("address") or "") or f"place {i}"
        place, why = Place.deserialize(f"{CHIEF} {where}", entry)
        if place is None:
            problems += why
        else:
            places.append(place)
    return places, problems


def _unclosed(places: list[Place]) -> list[str]:
    """One reason per place this proof has not finished deciding.

    A carried-forward text has not settled (`decision-log.md Process: #180`)
    and a refused place rolled its own round back, so neither is the write
    end's to set. A docket holding the settled places beside them would draft
    part of a stage as though the rest had been ruled on.
    """
    return [
        f"{CHIEF} {place.address}: {place.state} -- this proof is not closed,"
        " so nothing on it has settled"
        for place in places
        if place.state in CARRIED or place.state is State.REFUSED
    ]


def docket_of_proof(proof: MasterProof, repo: Path) -> Docket:
    """One closed master proof, transcribed into the docket the write chain reads.

    `decision-log.md Process: #184`: the proof holds each place's decided
    text, so the write end reads those places. Nothing is folded here and no
    mark is read for what it sets -- the fold has already ruled on that, and
    the place carries the answer.

    Args:
        proof: a closed master proof, already through
            `MasterProof.deserialize`.
        repo: the checkout whose pages the write end sets. Each page is read
            for its own place order and for the anchor at a place carrying
            none.

    Returns:
        A `Docket` -- one `Schedule` per page a text was decided on, each
        naming that page's own path and the sha the run read it at, and the
        chief as the role, since the fold is what decided these places. One
        alteration per place whose decided text differs from the paragraph
        already there, with an emptied place written as the `None` the write
        end reads as a delete.

        A place the fold decided no text for gets none, and neither does one
        standing on the text already there (`Process: #174`): there is
        nothing to set at either.

    Raises:
        CannotTranscribe: a place will not parse, a place is still carried
            forward or refused, or a page a decided place sits on cannot be
            read here. Nothing it reported can be set, and the reasons are
            the report.
    """
    places, problems = _places_on(proof)
    if problems:
        raise CannotTranscribe(tuple(problems))
    unclosed = _unclosed(places)
    if unclosed:
        raise CannotTranscribe(tuple(unclosed))

    decided: dict[str, list[Place]] = {}
    for place in places:
        if place.text is not None and place.text != place.base:
            decided.setdefault(cue_of(place.address).path, []).append(place)
    touched = {
        name: sorted(place.address for place in here) for name, here in decided.items()
    }
    # The pages the run recorded, in the order it recorded them, with the sha
    # each was read at. A page every copy holds a sheet for is named once.
    known: list[str] = []
    shas: dict[str, str] = {}
    for copy in proof.edit_copies:
        for sheet in copy.sheets:
            if sheet.path not in known:
                known.append(sheet.path)
                shas[flatten(sheet.path)] = sheet.sha
    pages, unreadable = _pages_of(repo, known, touched, CHIEF, "places")
    if unreadable:
        raise CannotTranscribe(tuple(unreadable))
    return Docket(schedules=_schedules_of(pages, decided, shas, CHIEF))
