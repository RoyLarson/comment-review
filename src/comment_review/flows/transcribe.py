"""TRANSCRIBE -- decided places, as the docket the write chain reads.

    docket_of(copy, repo)        one edit_copy, folded
    docket_of_proof(proof, repo) one closed master proof, read
    docket_of_proof(proof, repo, only=(...))   the approved places of one

Two inputs, and they differ in where the decision comes from. A copy is folded
here: its marks are turned into places (`flows.places.places_of`), the Unit of
Work decides every one of them, and each place the fold settled a text for
becomes one alteration. A closed proof already holds every place the fold
decided, so nothing is folded again -- the places are read back and each whose
text differs from its base becomes one alteration.

They answer differently, and the reason is the filter. `docket_of` hands back
the `Docket`; `docket_of_proof` hands back a `Transcription`, which is that
docket and the approved places it sets nothing at. Only a partial approval
names places, so only that path has anything to say about a place it was
asked for and set nothing at.

`only` is the author's partial approval -- `decision-log.md Process: #192`.
The author approves some decided places and not others, and what they ruled on
is a set of addresses over the proof the fold closed rather than a second
artifact pruned by hand.

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
from typing import NamedTuple

from comment_review.binder.page import Page
from comment_review.desk import report as events
from comment_review.desk.marks.table import INSTRUCTIONS
from comment_review.desk.proof.disposition import CHIEF
from comment_review.desk.proof.edit_copy import EditCopy
from comment_review.desk.proof.master_proof import MasterProof
from comment_review.desk.proof.move import Move, is_open
from comment_review.desk.proof.place import Place
from comment_review.desk.proof.state import SETTLED
from comment_review.desk.work.fold import Fold
from comment_review.docket.docket import Alteration, Docket, Schedule
from comment_review.flows.human import queries_in_copies
from comment_review.flows.on_the_page import PageCache, held_at, no_page, page_named
from comment_review.flows.places import bases_and_anchors, places_of
from comment_review.reading.addresser import cue_of, flatten


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


class CannotApprove(CannotTranscribe):
    """The approval named a place this proof cannot set, and nothing is set.

    It is its own class so the console can say so. Every other refusal here
    is about the proof -- it has not closed, a place will not read back, a
    page cannot be opened -- and the command opens those with *the proof
    decided nothing that can be set*. That sentence is false of an approval
    the proof cannot honour: the proof decided plenty, and what could not be
    honoured is the list of places it was handed (`decision-log.md Process:
    #192`).
    """


class Transcription(NamedTuple):
    """One closed proof transcribed: what the write end sets, and what it does not.

    Attributes:
        docket: one schedule per page a text is to be set on.
        sets_nothing: the approved places this transcription sets nothing at,
            in the order they were named. A place standing on the text
            already there and a place held for the human both come here: the
            author ruled on each, and neither leaves the write end anything
            to do, so a run that said only how many pages it drafted would
            say nothing at all about them. Empty where no filter was given,
            since a blanket approval names no place.
    """

    docket: Docket
    sets_nothing: tuple[str, ...] = ()


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

    Returns:
        `(the flattened page name -> (its real relative path, the page), the
        reasons)`, the pages in `known`'s order and then in the order
        `touched` first names one that is not among them. A reason names
        `who`, the page and every address on it.
    """
    out: dict[str, tuple[str, Page]] = {}
    refused: list[str] = []
    for name in dict.fromkeys([flatten(path) for path in known] + list(touched)):
        rel, page = page_named(name, known, repo, cache)
        if page is not None:
            out[name] = (rel, page)
        elif name in touched:
            refused.append(
                f"{who} {rel or name}: {no_page(rel or name)}, so the {noun} at"
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
                # The recorded sha where the input carries one, since that is
                # the bytes its addresses were taken from. A page only a
                # move's destination names was never gathered and so has no
                # recorded sha; the page read here is the only one there is.
                sha=shas.get(name, page.sha),
                alterations=tuple(
                    Alteration(
                        cue=cue_of(place.address).cue,
                        text=place.text or None,
                        # The place's own anchor, which `bases_and_anchors`
                        # set when the places were built: the role's at a
                        # mark's own address and the page's at a move's
                        # destination. The write end refuses one that is not
                        # the page's (`decision-log.md Process: #134`).
                        anchor=place.anchor,
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
        repo: the checkout whose pages the write end sets. Every base is read
            from it, so what the fold measures a mark against is the page
            rather than the mark's own account of it.

    Returns:
        A `Docket` -- one `Schedule` per page the fold decided a text on, each
        naming that page's own path and sha and the copy's own role. An
        alteration carries the anchor at its place -- the role's at a mark's
        own address, the page's at a move's destination (`decision-log.md
        Process: #134` and `#135`) -- and its text, with an emptied place
        written as the `None` the write end reads as a delete.

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
    questions = queries_in_copies([copy])
    if questions:
        raise CannotTranscribe(
            tuple(f"{one.role} {one.at}: {one.question}" for one in questions)
        )
    known = [sheet.path for sheet in copy.sheets]
    cache: PageCache = {}
    pages, unreadable = _pages_of(
        repo, known, _touched_by_page(copy), copy.role, "marks", cache
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
    bases, anchors = bases_and_anchors(
        [copy], lambda address: held_at(address, known, repo, cache)
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


def _open_moves(moves: list[Move]) -> list[str]:
    """One reason per move whose placement is still to be decided.

    An open move (`desk.proof.move.is_open`) keeps the proof from closing:
    neither end has a text until the placement is decided, by the roles or
    by the chief's placement ruling (`decision-log.md Process: #195` item 4),
    so transcribing around it would set one end of a move and not the other.
    """
    return [
        f"{CHIEF} {move.key}: the placement of this move is {move.placement} and"
        " not ruled on, so this proof is not closed"
        for move in moves
        if is_open(move)
    ]


def _unclosed(places: list[Place]) -> list[str]:
    """One reason per place this proof has not finished deciding.

    A carried-forward text has not settled (`decision-log.md Process: #180`)
    and a refused place rolled its own round back, so neither is the write
    end's to set. A docket holding the settled places beside them would draft
    part of a stage as though the rest had been ruled on.

    `UNSETTLABLE` is neither settled nor unfinished, and that is why it is
    the one state this admits without a text: the place rides to the human
    with its question (`Process: #90`) and carries nothing to set. What is
    settled is `desk.proof.state.SETTLED`, which `commands/collate._counted`
    reads as well -- this named the states it refused until #193's round, and
    a seventh state would have had to be added in both places.
    """
    return [
        f"{CHIEF} {place.address}: {place.state} -- this proof is not closed,"
        " so nothing on it has settled"
        for place in places
        if place.state not in SETTLED
    ]


def _sets(place: Place) -> bool:
    """Whether the write end has anything to set at this place.

    A place the fold decided no text for is nothing to set, and so is one
    whose decided text is the paragraph already there (`decision-log.md
    Process: #174`). Both the docket below and the report of what an approval
    leaves undone read this, so the two cannot come to different answers
    about one place.
    """
    return place.text is not None and place.text != place.base


def _approved(
    places: list[Place], only: tuple[str, ...]
) -> tuple[list[Place], list[str], tuple[str, ...]]:
    """The approved places alone, the reasons a name is refused, and what sets nothing.

    `decision-log.md Process: #192`. One refusal: an address the proof does
    not carry. Nothing was decided there, so nothing was approved there, and
    the name is likelier a mistyped address than a ruling -- transcribing the
    rest would set what was named correctly and say nothing about what was
    not.

    A move's two ends are approved each on its own: an agreed move reaches
    the proof as a `drop` and an `add` (`decision-log.md Process: #195` item
    5), and a held one sets nothing at either end.

    Args:
        places: every place the proof carries, parsed and closed.
        only: the addresses the author approved, in the order they were
            named. A repeat is one approval.

    Returns:
        `(the approved places, the reasons, the approved places that set
        nothing)`. The places keep the proof's own order, since that is the
        order the schedules come out in; a non-empty second half means
        nothing is to be set at all.
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
        return [], problems, ()
    return (
        [place for place in places if place.address in wanted],
        [],
        tuple(address for address in named if not _sets(by_address[address])),
    )


def docket_of_proof(
    proof: MasterProof, repo: Path, only: tuple[str, ...] | None = None
) -> Transcription:
    """One closed master proof, transcribed into the docket the write chain reads.

    `decision-log.md Process: #184`: the proof holds each place's decided
    text, so the write end reads those places. Nothing is folded here and no
    mark is read for what it sets -- the fold has already ruled on that, and
    the place carries the answer.

    Args:
        proof: a closed master proof, already through
            `MasterProof.deserialize`.
        repo: the checkout whose pages the write end sets. Each page is read
            for its own place order; every place on the proof carries the
            anchor the collate handler gave it.
        only: the places the author approved, where they approved some and
            not others (`Process: #192`). None is the blanket approval: every
            place the proof decided.

    Returns:
        A `Transcription`. Its docket holds one `Schedule` per page a text
        was decided on, each naming that page's own path and the sha the run
        read it at, and the chief as the role, since the fold is what decided
        these places. One alteration per place whose decided text differs
        from the paragraph already there, with an emptied place written as
        the `None` the write end reads as a delete.

        A place the fold decided no text for gets none, and neither does one
        standing on the text already there (`Process: #174`): there is
        nothing to set at either. Where `only` named such a place, it is on
        `sets_nothing` instead.

    Raises:
        CannotTranscribe: a place is still carried forward or refused, a
            move's placement is undecided and the chief has not ruled both of
            its ends, `only` names an address the proof does not carry, or a
            page a decided place sits on cannot be read here. Nothing it
            reported can be set, and the reasons are the report. A place or a
            move that will not read never reaches here: `MasterProof.deserialize`
            refuses the proof and names it.
    """
    places = list(proof.places)
    unclosed = _unclosed(places) + _open_moves(list(proof.moves))
    if unclosed:
        raise CannotTranscribe(tuple(unclosed))
    sets_nothing: tuple[str, ...] = ()
    if only is not None:
        places, problems, sets_nothing = _approved(places, only)
        if problems:
            raise CannotApprove(tuple(problems))

    decided: dict[str, list[Place]] = {}
    for place in places:
        if _sets(place):
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
    pages, unreadable = _pages_of(repo, known, touched, CHIEF, "places", {})
    if unreadable:
        raise CannotTranscribe(tuple(unreadable))
    return Transcription(
        Docket(schedules=_schedules_of(pages, decided, shas, CHIEF)), sets_nothing
    )
