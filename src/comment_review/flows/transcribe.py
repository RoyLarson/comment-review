"""TRANSCRIBE -- decided places, as the docket the write chain reads.

    docket_of(copy, repo)        one edit_copy, folded
    docket_of_proof(proof, repo) one closed master proof, read
    docket_of_proof(proof, repo, only=(...))   the approved places of one

Two inputs, and they differ in where the decision comes from. A copy is
admitted and folded here, by `flows.verify.admit`, and each place the copy's
role proposes a text for becomes one alteration. A closed proof already holds
every place the fold decided, so nothing is folded again -- the places are
read back and each whose text differs from its base becomes one alteration.

Both paths return a `Docket` containing the corrections to apply.

`only` is the author's partial approval. The author approves some decided places
and not others, and what they ruled on is a set of addresses over the proof the
fold closed rather than a second artifact pruned by hand.

The proof is what the write end reads. The chief's copy restated the same
decisions as marks, found or synthesized, and folding those marks a second time
made the docket depend on that restatement reproducing the first fold exactly.
`docket_of` stays for a role's own draft, which is the artifact it was written
for.

Neither path reads a mark's `change` or asks which end of a `move` it is
looking at: the marks table answered both when the fold ran, and a place
carries one text whatever produced it.

A rolled-back fold is a refusal, not an empty docket. `CannotTranscribe`
carries the events' own reasons, and `commands/proof.py` prints them. An empty
docket would say the copy asked for nothing, which is the opposite of a copy
whose marks could not be read.

`CannotApprove`, a `CannotTranscribe`, is the refusal of an approval: an
`only` naming a place the proof does not carry, or one end of an agreed move
without the other. `commands/proof.py` catches it first, so the console says
the approval failed rather than that the proof decided nothing.

!! `docket_of` transcribes any edit copy, not only the copy chief's, so a stage's own
output becomes a revise, which is the mechanism `reads = "revise:<name>"` and stage
`4c` both need.

!! Transcription is its own flow because it is its own act: `flows.revise.pull` never
calls it, and `commands/proof.py` calls both.

!! It is a flow because a flow may reach both ends and neither end may reach the other.
This reads the pages, takes the middle's fold from `flows.verify.admit`, and builds
the write end's `Docket`; `Docket.of(edit_copy)` was offered and declined, because it
would put a middle type in `docket/docket.py`, which imports only the leaves
`constants` and `reading`.
"""

from pathlib import Path

from comment_review.binder.page import Page
from comment_review.desk import report as events
from comment_review.desk.marks.table import INSTRUCTIONS
from comment_review.desk.proof.disposition import CHIEF
from comment_review.desk.proof.edit_copy import EditCopy
from comment_review.desk.proof.master_proof import MasterProof
from comment_review.desk.proof.move import Move, Placement, is_open
from comment_review.desk.proof.place import Place
from comment_review.desk.proof.state import DECIDED
from comment_review.docket.docket import Alteration, Docket, Schedule
from comment_review.flows.on_the_page import PageCache, no_page, page_named
from comment_review.flows.reading_context import admit_proof
from comment_review.flows.verify import admit
from comment_review.reading.addresser import cue_of, flatten
from comment_review.reading.context import Imprint
from comment_review.reading.diagnostics import ReadFailure


class CannotTranscribe(Exception):
    """A refusal to transcribe the input.

    Attributes:
        reasons: messages explaining why transcription was refused.
    """

    def __init__(self, reasons: tuple[str, ...]) -> None:
        """Hold every refusal and say it in the message too."""
        super().__init__("; ".join(reasons))
        self.reasons = reasons


class CannotAdmit(CannotTranscribe):
    """A page identity the copy claims will not admit, and nothing is set.

    It is an input that cannot be read -- regathered, or the invocation
    corrected -- and never a ruling to send back to a role, so
    `commands/proof.py` catches it first and exits 2.
    """


class CannotApprove(CannotTranscribe):
    """The approval cannot be honoured as it was named, and nothing is set.

    It is its own class so the console can say so. Every other refusal here
    is about the proof -- it has not closed, a place will not read back, a
    page cannot be opened -- and the command opens those with *the proof
    decided nothing that can be set*. That sentence is false of an approval
    the proof cannot honour: the proof decided plenty, and what could not be
    honoured is the list of places it was handed.
    """


def _touched_by_page(copy: EditCopy) -> dict[str, list[str]]:
    """The flattened page name -> every address this copy's marks write there.

    Sorted within a page, so two runs over one copy name them in one order.
    Where a mark writes is its row's answer (`desk.marks.table.Row.places`).
    """
    out: dict[str, list[str]] = {}
    for sheet in copy.sheets:
        for mark in sheet.marks:
            for address, _touch in INSTRUCTIONS[mark.instruction].places(mark):
                name = cue_of(address).path
                if name and address not in out.setdefault(name, []):
                    out[name].append(address)
    return {name: sorted(addresses) for name, addresses in out.items()}


def _pages_of(
    repo: Path,
    known: list[str],
    touched: dict[str, list[str]],
    who: str,
    noun: str,
    cache: PageCache,
    imprints: dict[str, Imprint],
) -> tuple[dict[str, tuple[str, Page]], list[str]]:
    """Every page a transcription writes at, read from `repo`, and what would not read.

    A page this checkout cannot answer for is a refusal rather than an
    omission: it would get no schedule, and the run would draft as though the
    rulings there had never been made. A page named among `known` and written
    at by nothing is not missed, since nothing was going to be set there.

    Args:
        repo: the checkout every page is read from.
        known: the real relative paths the input records -- a copy's sheets,
            or a proof's. They are what a flattened name is turned back into
            a path against (`flows.on_the_page.real_path`), and their order is
            the order the schedules come out in.
        touched: flattened page name -> the addresses to be set there.
        who: whose transcription this is, for the reasons -- a role, or the
            chief where a fold decided the places.
        noun: what is owed at those addresses, for the reasons.
        cache: the pages read, which the caller may read places off again.
        imprints: the identity table admitted for the input, by real path.

    Returns:
        `(the flattened page name -> (its real relative path, the page), the
        reasons)`, the pages in `known`'s order and then in the order
        `touched` first names one that is not among them. A reason names
        `who`, the page and every address on it.
    """
    out: dict[str, tuple[str, Page]] = {}
    refused: list[str] = []
    for name in dict.fromkeys([flatten(path) for path in known] + list(touched)):
        rel, page = page_named(
            name,
            known,
            repo,
            cache,
            imprints=imprints,
        )
        if not isinstance(page, ReadFailure):
            out[name] = (rel, page)
        elif name in touched:
            detail = "; ".join(d.message for d in page.diagnostics)
            refused.append(
                f"{who} {rel or name}: {no_page(rel or name)}: {detail},"
                f" so the {noun} at"
                f" {', '.join(touched[name])} cannot be set"
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
                sha=shas[name],
                alterations=tuple(
                    Alteration(
                        cue=cue_of(place.address).cue,
                        text=place.text or None,
                        # The place's own anchor, which `bases_and_anchors`
                        # set when the places were built: the role's at a
                        # mark's own address and the page's at a move's
                        # destination. The write end refuses one that is not
                        # the page's.
                        anchor=place.anchor,
                    )
                    for place in here
                ),
                role=role,
                reading=page.reading,
            )
        )
    return tuple(schedules)


def docket_of(copy: EditCopy, repo: Path) -> Docket:
    """One edit_copy, folded and transcribed into the docket the write chain reads.

    Args:
        copy: a returned edit_copy, already through `EditCopy.deserialize`.
        repo: the checkout whose pages the write end sets. Every base is read
            from it, so what the fold measures a mark against is the page
            rather than the mark's own account of it.

    Returns:
        A `Docket` -- one `Schedule` per page the fold decided a text on, each
        naming that page's own path and sha and the copy's own role. An
        alteration carries the anchor at its place -- the role's at a mark's own
        address, the page's at a move's destination -- and its text, with an
        emptied place written as the `None` the write end reads as a delete.

        Each place carries the text the copy's role proposes there, whether
        the fold decided it or carried it to the chief. A place the role
        proposed no text for gets no alteration: a `clean` and a `query`
        propose none. A page with no alteration gets no schedule, since an
        empty one would tell the write end to set a page from nothing.

    Raises:
        CannotAdmit: a page identity the copy claims will not admit.
        CannotTranscribe: `flows.verify.admit` refuses the copy or holds a
            human query, or an edited page is unreadable.
    """
    # The copy is admitted as `collate` admits one, given no binder: nothing
    # is required of it, so a partial draft transcribes. A human question is
    # refused, as nothing answers it here; no answers file is given, so a
    # change to the file's matter is drafted as filed, and `collate` asks it.
    admission = admit([copy], repo)
    if admission.unadmitted:
        raise CannotAdmit(tuple(one.message for one in admission.unadmitted))
    refused = [
        events.refusal_line(one.role, one.address or "(the copy)", one.message)
        for one in admission.problems
    ]
    refused += [
        f"{query.role} {query.at}: {query.question}" for query, _ in admission.asks
    ]
    if refused or admission.fold is None:
        raise CannotTranscribe(tuple(refused))
    fold = admission.fold
    known = [sheet.path for sheet in copy.sheets]
    pages, unreadable = _pages_of(
        repo,
        known,
        _touched_by_page(copy),
        copy.role,
        "marks",
        admission.pages,
        admission.imprints,
    )
    if unreadable:
        raise CannotTranscribe(tuple(unreadable))

    decided: dict[str, list[Place]] = {}
    for address, place in fold.decided.items():
        # A copy is its role's draft: each place reads as that role's marks
        # set it, though a change no other role read is carried to the chief
        # and a move it alone filed waits on the chief's placement ruling.
        place.text = place.sides.get(copy.role, place.text)
        if place.text is not None:
            decided.setdefault(cue_of(address).path, []).append(place)

    shas = {name: page.sha for name, (_rel, page) in pages.items()}
    shas.update({flatten(sheet.path): sheet.sha for sheet in copy.sheets})
    return Docket(schedules=_schedules_of(pages, decided, shas, copy.role))


def _open_moves(moves: list[Move]) -> list[str]:
    """One reason per move whose placement is still to be decided.

    An open move (`desk.proof.move.is_open`) keeps the proof from closing:
    neither end has a text until the placement is decided, by the roles or by
    the chief's placement ruling, so transcribing around it would set one end of
    a move and not the other.
    """
    return [
        f"{CHIEF} {move.key}: the placement of this move is {move.placement} and"
        " not ruled on, so this proof is not closed"
        for move in moves
        if is_open(move)
    ]


def _unclosed(places: list[Place]) -> list[str]:
    """Refusal reasons for undecided places.

    Each place must have a state in `DECIDED` for the proof to close.
    """
    return [
        f"{CHIEF} {place.address}: {place.state} -- this proof is not closed,"
        " so nothing on it is decided"
        for place in places
        if place.state not in DECIDED
    ]


def _approved(
    places: list[Place], only: tuple[str, ...]
) -> tuple[list[Place], list[str]]:
    """The approved places and the reasons an address is refused.

    One refusal: an address the proof does not carry. Nothing was decided there,
    so nothing was approved there, and the name is likelier a mistyped address
    than a ruling -- transcribing the rest would set what was named correctly
    and say nothing about what was not.

    Args:
        places: every place the proof carries, parsed and closed.
        only: the addresses the author approved, in the order they were
            named. A repeat is one approval.

    Returns:
        `(the approved places, the reasons)`. The places keep the proof's own
        order, though the schedules come out in the order the run recorded the
        pages; a non-empty second half means nothing is to be set at all.
    """
    by_address = {place.address: place for place in places}
    named = list(dict.fromkeys(only))
    wanted = set(named)
    problems = [
        f"{CHIEF} {address}: this proof carries no place here, so nothing"
        " was decided to approve"
        for address in named
        if address not in by_address
    ]
    if problems:
        return [], problems
    return (
        [place for place in places if place.address in wanted],
        [],
    )


def docket_of_proof(
    proof: MasterProof, repo: Path, only: tuple[str, ...] | None = None
) -> Docket:
    """One closed master proof, transcribed into the docket the write chain reads.

    The proof holds each place's decided text, so the write end reads those
    places. Nothing is folded here and no mark is read for what it sets -- the
    fold has already ruled on that, and the place carries the answer.

    Args:
        proof: a closed master proof, already through
            `MasterProof.deserialize`.
        repo: the checkout whose pages the write end sets. Each page is read
            for its own place order; every place on the proof carries the
            anchor the collate handler gave it.
        only: the places the author approved, where they approved some and not
            others. None is the blanket approval: every place the proof decided.

    Returns:
        A `Docket` holding one `Schedule` per page with an approved correction,
        each naming that page's own path and the sha the run read it at,
        and the chief as the role, since the fold is what decided
        these places. One alteration per place whose decided text differs
        from the paragraph already there, with an emptied place written as
        the `None` the write end reads as a delete.

        A place the fold decided no text for gets none, and neither does one
        standing on the text already there: there is nothing to set at either.

    Raises:
        CannotAdmit: a page identity the proof claims will not admit.
        CannotTranscribe: a place is still carried forward or refused, a move's
            placement is undecided and the chief has not ruled both of its ends,
            `only` names an address the proof does not carry or approves one end
            of an agreed move alone, a decided page has no recorded sha, or a
            page a decided place sits on cannot be read here. Nothing it
            reported can be set, and the reasons are the report. A place or a
            move that will not read never reaches here:
            `MasterProof.deserialize` refuses the proof and names it.
    """
    imprints, problems = admit_proof(proof)
    if problems:
        raise CannotAdmit(tuple(one.text for one in problems))
    places = list(proof.places)
    unclosed = _unclosed(places) + _open_moves(list(proof.moves))
    if unclosed:
        raise CannotTranscribe(tuple(unclosed))
    if only is not None:
        places, problems = _approved(places, only)
        approved = set(only)
        problems.extend(
            f"{CHIEF} {move.key}: approve both ends of this move together"
            for move in proof.moves
            if move.placement is Placement.AGREED
            and len(approved.intersection((move.origin, move.destination))) == 1
        )
        if problems:
            raise CannotApprove(tuple(problems))

    decided: dict[str, list[Place]] = {}
    for place in places:
        if place.changed:
            decided.setdefault(cue_of(place.address).path, []).append(place)
    touched = {
        name: sorted(place.address for place in here) for name, here in decided.items()
    }
    # The pages the run recorded, in the order it recorded them, with the sha
    # each was read at. A page every copy holds a sheet for is named once.
    known: list[str] = list(proof.page_readings)
    shas = {flatten(path): sha for path, sha in proof.page_shas.items()}
    for copy in proof.edit_copies:
        for sheet in copy.sheets:
            if sheet.path not in known:
                known.append(sheet.path)
            shas[flatten(sheet.path)] = sheet.sha
    missing = [
        f"{CHIEF} {name}: no recorded page sha; gather and collate this page again"
        for name in decided
        if name not in shas
    ]
    if missing:
        raise CannotTranscribe(tuple(missing))
    pages, unreadable = _pages_of(repo, known, touched, CHIEF, "places", {}, imprints)
    if unreadable:
        raise CannotTranscribe(tuple(unreadable))
    return Docket(schedules=_schedules_of(pages, decided, shas, CHIEF))
