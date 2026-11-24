"""The bus: the stage transitions as messages, one handler each.

    CopiesReturned       one stage's copies, back from the roles
    AnswersReturned      one turn's answers, back from the roles
    DispositionsWritten  the chief's rulings on what is still carried forward

Each handler checks what its message carries, derives the places, opens a Fold,
and on commit builds the `Result` the stage saves. A command sends one message
through `handle` and prints the events; nothing here writes a file, and nothing
here names a row of the three tables but `recast`, whose prose
`_on_dispositions` compares against a decided text.

`turn_of` reads the turn a proof stands at, for the turn and disposition
handlers and for the `turn` and `disposition` commands that report it.

What each handler reads. The collate handler reads the pages its copies'
marks touch: to check an address and a quote against the page and to take
each place's base text and anchor from it. It and the turn handler read a file
a mark or an answer cites, to verify the citation. The disposition handler
reads nothing. None of them asks whether a page changed since it was
gathered; once the places are built, the fold decides from them alone, and
the turn and the disposition take their places off the proof.

The collate and turn handlers also check for a human question -- a
`human-review-necessary` query filed as a mark or given as an answer -- and
roll back while one stands, until the role replaces it. The human's
answers file rides on the message, and each answer rides on the
`AsksTheHuman` for the question it answers.

Every handler also rolls back while a change to an `f` place -- a mark, an
answer or the chief's recast -- waits on the human's approval, as one
`AsksTheHuman` each.
"""

from collections.abc import Callable, Mapping, Sequence
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from typing import NamedTuple

from comment_review.binder.binder import Binder
from comment_review.binder.page import Page
from comment_review.desk import report as events
from comment_review.desk.collator import Cache, Problem
from comment_review.desk.dispositions.table import DISPOSITIONS
from comment_review.desk.evaluate.move import moves_in
from comment_review.desk.proof.answer import Answer, Question
from comment_review.desk.proof.disposition import (
    CHIEF,
    Disposition,
    RecastRuling,
    read_disposition,
)
from comment_review.desk.proof.edit_copy import EditCopy
from comment_review.desk.proof.master_proof import MasterProof
from comment_review.desk.proof.move import Move, is_open, key_of
from comment_review.desk.proof.place import Place
from comment_review.desk.proof.state import CARRIED, DECIDED, State
from comment_review.desk.stages import Stage
from comment_review.desk.work.fold import Fold, asked, put_to
from comment_review.flows.answers import Slot, answers_of, slots_of
from comment_review.flows.human import (
    HumanAnswer,
    HumanQuery,
    answered,
    corrections_in_answers,
    corrections_in_rulings,
    queries_in_answers,
)
from comment_review.flows.reading_context import admit_proof
from comment_review.flows.verify import admit


class CopiesReturned(NamedTuple):
    """One stage's copies, back from the roles and ready to fold.

    Attributes:
        stage: the label they were dispatched under -- "4a", "4c".
        copies: one parsed copy per role, or per shard under fan-out. The
            envelope parse is the command's, so a document that is not a
            copy never reaches here.
        binder: the stage binder defining each role's collective assignment
            and the page paths an address resolves through.
        root: the checkout a cite and a page are read from, and so where
            each place's base text comes from.
        topology: the stage as the topology declares it, where the caller
            has one. Without it nothing can know a dispatch was owed.
        human: the human's answers file, read -- each answer rides on the
            `AsksTheHuman` for the query it answers.
        binders: each copy's received binder, in the same order as the copies.
        dispatched: the copies the stage dispatched, as the jacket names
            them, recorded on the proof.
        returned: the name of each copy in `copies`, in the same order,
            recorded on the proof.
    """

    stage: str
    copies: list[EditCopy]
    binder: Binder
    root: Path
    topology: Stage | None = None
    human: tuple[HumanAnswer, ...] = ()
    binders: tuple[Binder, ...] | None = None
    dispatched: tuple[str, ...] = ()
    returned: tuple[str, ...] = ()


class AnswersReturned(NamedTuple):
    """One turn's answers, back from the roles and ready to fold.

    Attributes:
        proof: the master proof as the last fold wrote it -- the copies as
            they stand and every place that fold decided. Its places say
            which are still carried forward and who each was put to.
        answers: role -> what that role handed back, in any shape
            `flows.answers.slots_of` reads. A role the batch named and that
            returned nothing is absent, and every slot it owed is refused.
        root: the checkout an answer's `cite` is resolved against. Opening a
            cited file is not a page read: the places are still decided from
            the record alone, and what an answer cites as its evidence is
            held to the check a mark's citation is held to.
        human: the human's answers file, read -- each answer rides on the
            `AsksTheHuman` for the query it answers.
    """

    proof: MasterProof
    answers: Mapping[str, object]
    root: Path
    human: tuple[HumanAnswer, ...] = ()


class DispositionsWritten(NamedTuple):
    """The chief's rulings on the places the roles never decided.

    Attributes:
        proof: the master proof as the last turn wrote it, or as the first
            fold wrote it where no turn ran -- the baseline.
        dispositions: one ruling per place still carried forward, as the
            chief wrote them. A place left unruled is refused by name, and a
            ruling at a place nothing carries forward is refused too, except a
            `recast` of a place the roles decided.
        human: the human's answers file, read -- a `recast` of an `f` place
            waits on the human's approval as a mark there does.
    """

    proof: MasterProof
    dispositions: list
    human: tuple[HumanAnswer, ...] = ()


class Result(NamedTuple):
    """What a committed fold leaves the stage to save.

    Attributes:
        proof: the copies as they stand, carrying every decided place.
        batch: role -> the slots a turn asks it about, or None where the
            fold carried nothing forward.
    """

    proof: MasterProof
    batch: dict | None


def handle(message) -> tuple[list, Result | None]:
    """One message to its handler.

    Args:
        message: a message this module declares.

    Returns:
        `(the events, the result)` -- the result is None where the fold
        rolled back, and the events are then the whole report.
    """
    handler = HANDLERS[type(message)]
    return handler(message)


def _on_copies(message: CopiesReturned) -> tuple[list, Result | None]:
    """The copies admitted, then committed from the trial fold, or rolled back.

    `flows.verify.admit` is given every input the message holds -- the stage
    binder, the received binders, the stage label, the row and the human's
    answers -- and runs each rule and the fold. Each problem becomes one
    `Refused` and each human question one `AsksTheHuman`, and the stage rolls
    back while either stands. A refusal the fold finds is listed beside a
    question still pending, since the trial fold runs over every mark but the
    human queries.

    Otherwise the trial fold is the stage's fold, and the proof records each
    page's sha and reading: the admitted table's, and for a page read only
    because a mark reaches into it -- one no copy holds a sheet for -- the
    reading and sha it was read at under the installed reader.
    """
    copies = message.copies
    admission = admit(
        copies,
        message.root,
        binder=message.binder,
        received=message.binders,
        stage=message.stage,
        row=message.topology,
        human=message.human,
    )
    if admission.unadmitted:
        return _rolled_back(admission.problems, [], unreadable=admission.unadmitted)
    asks = [
        events.AsksTheHuman(q.role, q.at, q.question, a.answer if a else "")
        for q, a in [*admission.asks, *((one, None) for one in admission.approvals)]
    ]
    if admission.problems or asks or admission.fold is None:
        return _rolled_back(admission.problems, asks)
    imprints = admission.imprints
    sheet_paths = {sheet.path for copy in copies for sheet in copy.sheets}
    # A page read only because a mark reaches into it: the page records the
    # sha and reading it was read at.
    extra = {
        path: held.result
        for path, held in admission.pages.items()
        if path not in sheet_paths and isinstance(held.result, Page)
    }
    read_from = copies[0].read_from if copies else {}
    proof = MasterProof(
        stage=message.stage,
        read_from={**read_from},
        edit_copies=tuple(copies),
        page_readings={
            **{path: imprint.reading for path, imprint in imprints.items()},
            **{path: page.reading for path, page in extra.items()},
        },
        page_shas={
            **{
                path: imprint.sha
                for path, imprint in imprints.items()
                if path not in sheet_paths
            },
            **{path: page.sha for path, page in extra.items()},
        },
        dispatched=message.dispatched,
        returned=message.returned,
    )
    return _commit(proof, admission.fold)


def _places_on(proof: MasterProof) -> dict[str, Place]:
    """The proof's places, by address, as copies a fold may write on.

    The fold writes answers, rulings and states onto the places it is handed,
    so it is handed copies: the proof the message carried stays as it was
    written whether this fold commits or rolls back.
    """
    return {place.address: deepcopy(place) for place in proof.places}


def turn_of(proof: MasterProof) -> int:
    """The turn a proof stands at -- the last one any place or move answered.

    0 fresh from the first fold, and one more for each turn folded over it.
    The next turn is this plus one, derived from the record so that nothing
    counts turns of its own.

    Args:
        proof: a master proof, as a fold wrote it.

    Returns:
        The highest turn any place or move records an answer at, 0 where
        none does. A turn may ask only placements, so a move's answers count.
    """
    return max(
        (at for record in (*proof.places, *proof.moves) for at in record.answers),
        default=0,
    )


def _on_answers(message: AnswersReturned) -> tuple[list, Result | None]:
    """One turn's answers written onto the places, then folded again.

    Every role the fold asked owes an answer at every place it was asked
    about, and nothing else may answer: an entry at a place no turn carries
    forward, or at one this role was not asked about, is refused, and so is a
    slot left unanswered. Each refusal voids the round, as a copy's does, so
    a proof is never written over an answer that was not read. A human
    question given as an answer rolls the turn back too, as one
    `AsksTheHuman` each.

    A move whose placement is undecided, and which the chief has not ruled at
    both ends, is asked of each role in its `owed` as one slot keyed by the
    move (`flows.answers.slot_key`); the answer is written onto the move, not
    onto either end.
    """
    _, why = admit_proof(message.proof)
    if why:
        return _rolled_back([], unreadable=[Problem("", "", one.text) for one in why])
    places = _places_on(message.proof)
    moves = moves_in(places, _moves_on(message.proof))
    problems: list[Problem] = []
    carried = [place for place in places.values() if place.state in CARRIED]
    open_moves = [move for move in moves.values() if is_open(move)]
    slots = _turn_slots(carried, open_moves, places)
    turn = turn_of(message.proof) + 1
    given: dict[str, dict[str, Answer]] = {}
    # One cache for the whole turn, as the collate handler keeps one for the
    # whole stage: the roles answer at the same places and cite the same
    # evidence, so a per-role cache reads one file once per answering role.
    cache: Cache = {}
    for role in sorted(slots.keys() | message.answers.keys()):
        sent = {slot.key: slot for slot in slots.get(role, [])}
        returned = slots_of(message.answers.get(role, []), role)
        # A file handed in for a role this turn asked nothing of, holding
        # nothing: every other case names a place, and this one has none to
        # name, so it is reported against the file itself.
        if not sent and not returned:
            problems.append(Problem(role, "", "no slots were sent to this role"))
            continue
        answers, why = answers_of(
            role, sent, returned, _unsent(places, moves, role), message.root, cache
        )
        problems += why
        given[role] = answers
    asks = _asks(queries_in_answers(given), message.human)
    asks += _asks(corrections_in_answers(given, message.human), ())
    if problems or asks:
        return _rolled_back(problems, asks)
    for role, answers in given.items():
        for key, answer in answers.items():
            target = moves[key].answers if key in moves else places[key].answers
            target.setdefault(turn, {})[role] = answer
    return _commit(message.proof, Fold(places, moves, turn=turn).run())


def _unsent(
    places: dict[str, Place], moves: dict[str, Move], role: str
) -> Callable[[str], str]:
    """Why an answer at a slot key is not this role's to write, for `answers_of`."""

    def why(address: str) -> str:
        move = moves.get(address)
        if move is not None:
            if not is_open(move):
                return "not an open move"
            return (
                f"not put to {role} -- this move is put to"
                f" {', '.join(put_to(move.owed))}"
            )
        place = places.get(address)
        if place is None or place.state not in CARRIED:
            return "not carried forward"
        return (
            f"not put to {role} -- this place is put to"
            f" {', '.join(put_to(asked(place)))}"
        )

    return why


def _on_dispositions(message: DispositionsWritten) -> tuple[list, Result | None]:
    """The chief's rulings written onto the moves and places, then folded.

    Nothing survives the chief's ruling unruled, and each place and each move
    takes one ruling: a second ruling at the same place or on the same move,
    identical or not, is refused by name and neither is applied, since the
    chief has not said which one stands. A ruling naming a move (`to`) rules
    its placement, and every move still undecided takes one. A
    place carried forward takes a ruling on its words, and one with none is
    refused by name and with the roles it was put to. A place the roles
    decided takes a recast and no other ruling, so the chief can bring its
    text into line with the style sheet; a
    recast whose prose is the decided text changes nothing and is refused. A
    ruling at a place that rides to the human, or that waits on its move, is
    refused as well. Which states each ruling closes is its row's `closes`,
    in `desk.dispositions.table`. A recast of an `f` place the human has not
    approved rolls the message back as one `AsksTheHuman`.

    A placement ruling agrees or withdraws its move, and an end that then
    needs words is carried forward in what this commits, for the chief to
    rule on the proof it writes.
    """
    _, why = admit_proof(message.proof)
    if why:
        return _rolled_back(
            [], unreadable=[Problem(CHIEF, "", one.text) for one in why]
        )
    places = _places_on(message.proof)
    moves = moves_in(places, _moves_on(message.proof))
    problems: list[Problem] = []
    # A place's address and a move's key never coincide, so one set holds both.
    ruled: set[str] = set()
    applied: list[Disposition] = []
    for i, entry in enumerate(message.dispositions, 1):
        named = str(entry.get("address") or "") if isinstance(entry, dict) else ""
        where = named or f"ruling {i}"
        disposition, why = read_disposition(where, entry)
        if disposition is None:
            problems += [
                Problem(CHIEF, where, one.removeprefix(f"{where}: ")) for one in why
            ]
            continue
        slot = (
            key_of(disposition.address, disposition.to)
            if disposition.to
            else disposition.address
        )
        if slot in ruled:
            problems.append(
                Problem(CHIEF, slot, "ruled more than once in this message")
            )
            continue
        ruled.add(slot)
        if disposition.to:
            key = slot
            move = moves.get(key)
            if move is None or not is_open(move):
                problems.append(Problem(CHIEF, key, "not an open move"))
                continue
            move.disposition = disposition
            continue
        place = places.get(disposition.address)
        if place is not None and place.state is State.TO_COME:
            problems.append(
                Problem(
                    CHIEF,
                    disposition.address,
                    "an end of an undecided move -- rule the move's placement,"
                    " and this end's words once it is placed",
                )
            )
            continue
        if place is None or not DISPOSITIONS[disposition.name].can_close(place.state):
            why = "not carried forward"
            if place is not None and place.state in DECIDED:
                why += " -- a place the roles decided takes only a recast"
            problems.append(Problem(CHIEF, disposition.address, why))
            continue
        if (
            place.state in DECIDED
            and isinstance(disposition, RecastRuling)
            and disposition.prose == (place.base if place.text is None else place.text)
        ):
            problems.append(
                Problem(
                    CHIEF,
                    disposition.address,
                    "nothing to recast -- the prose is the text the roles decided",
                )
            )
            continue
        place.disposition = disposition
        applied.append(disposition)
    for key in sorted(moves):
        move = moves[key]
        if is_open(move) and move.disposition is None:
            problems.append(
                Problem(
                    CHIEF,
                    key,
                    f"the placement of this move is {move.placement} and not ruled on",
                )
            )
    for address in sorted(places):
        place = places[address]
        if place.state in CARRIED and place.disposition is None:
            problems.append(
                Problem(
                    CHIEF,
                    address,
                    "carried forward and not ruled on -- it was put to "
                    f"{', '.join(put_to(asked(place)))}",
                )
            )
    asks = _asks(corrections_in_rulings(applied, message.human), ())
    if problems or asks:
        return _rolled_back(problems, asks)
    turn = turn_of(message.proof)
    return _commit(message.proof, Fold(places, moves, turn=turn).run())


def _rolled_back(
    problems: list[Problem],
    asks: Sequence[events.AsksTheHuman] = (),
    *,
    unreadable: Sequence[Problem] = (),
) -> tuple[list, None]:
    """Every problem as its own `Refused`, then `asks`, then the rollback.

    `unreadable` problems are page identities that will not admit, each
    refused as `unreadable`. Nothing is saved.
    """
    refusals = [
        *(
            events.Refused(one.role, one.address, (one.message,), unreadable=True)
            for one in unreadable
        ),
        *(events.Refused(one.role, one.address, (one.message,)) for one in problems),
    ]
    return events.rollback([*refusals, *asks]), None


def _asks(
    queries: list[HumanQuery], human: tuple[HumanAnswer, ...]
) -> list[events.AsksTheHuman]:
    """One `AsksTheHuman` per human question, with the human's answer where given."""
    return [
        events.AsksTheHuman(q.role, q.at, q.question, a.answer if a else "")
        for q, a in answered(queries, list(human))
    ]


def _commit(proof: MasterProof, fold: Fold) -> tuple[list, Result | None]:
    """A fold that has run, and what its commit saves.

    Args:
        proof: the stage metadata prepared at collate, or the proof read by
            a later message. The fold replaces its places and moves.
        fold: the fold, run -- the collate handler's trial fold, or one over
            the places and moves as a later message wrote onto them, each
            evaluated from its own record.

    Returns:
        `(the events, the result)`, the result being None on a rollback.
    """
    out: list = list(fold.events)
    if not fold.committed:
        return out, None
    next_proof = replace(
        proof,
        read_from=dict(proof.read_from),
        places=tuple(fold.decided.values()),
        moves=tuple(move.recorded() for move in fold.decided_moves.values()),
    )
    return out, Result(next_proof, _batch_or_none(fold, proof.read_from))


def _undecided(fold: Fold) -> list[Move]:
    """The moves this fold carries forward, in key order.

    Only an open move is carried (`desk.proof.move.is_open`), as the fold
    reports a `PlacementCarried` for an open move alone.
    """
    return [
        fold.decided_moves[key]
        for key in sorted(fold.decided_moves)
        if is_open(fold.decided_moves[key])
    ]


def _batch_or_none(fold: Fold, read_from: dict) -> dict[str, list[dict]] | None:
    """The committed fold's batch, or None where it carries nothing forward.

    It is empty where everything carried is put to the copy chief alone, who
    has no slot.
    """
    carried = [place for place in fold.decided.values() if place.state in CARRIED]
    moves = _undecided(fold)
    if not carried and not moves:
        return None
    return _batch_of(carried, moves, fold.decided, read_from)


def _moves_on(proof: MasterProof) -> dict[str, Move]:
    """The proof's recorded moves, by key, as copies a fold may write on."""
    return {move.key: deepcopy(move) for move in proof.moves}


def _batch_of(
    carried: list[Place],
    moves: list[Move],
    places: dict[str, Place],
    read_from: dict,
) -> dict[str, list[dict]]:
    """Role -> one slot per carried-forward place that role is asked about.

    And one slot per move whose placement is undecided, for each role it is
    put to: the move's two addresses and, for every role that filed it, the
    snippet and the paragraph it arrives as -- the roles may have moved
    different text.

    Every slot carries the tree the copies were read from, as an edit_copy and
    a master proof each carry their own: a role hands the slot back as it was
    sent and adds only its answer, so the file its answers arrive in says what
    its citations are resolved against, and `check --answers` defaults its
    root from the file it is handed rather than from the directory it stands
    in.

    Args:
        carried: the places this fold is carrying forward.
        moves: the moves this fold is carrying forward (`_undecided`).
        places: the fold's places, where a move's origin anchor is read.
        read_from: the proof's own, copied onto each slot rather than aliased.

    Returns:
        role -> its slots. A role nothing is asked of is absent.
    """
    return {
        role: [slot.serialize(read_from) for slot in sent]
        for role, sent in _turn_slots(carried, moves, places).items()
    }


def _turn_slots(
    carried: list[Place], moves: list[Move], places: dict[str, Place]
) -> dict[str, list[Slot]]:
    """Build each question once and share it among the roles it was put to."""
    slots: dict[str, list[Slot]] = {}
    for place in carried:
        slot = Slot(
            place.address,
            place.anchor,
            str(place.question),
            raw_text=place.text if place.text is not None else place.base,
            sides=dict(place.sides),
        )
        for role in asked(place):
            slots.setdefault(role, []).append(slot)
    for move in moves:
        origin = places.get(move.origin)
        slot = Slot(
            move.origin,
            origin.anchor if origin else "",
            str(Question.PLACEMENT),
            to=move.destination,
            movers=tuple(sorted(move.movers.items())),
        )
        for role in move.owed:
            slots.setdefault(role, []).append(slot)
    return slots


HANDLERS = {
    CopiesReturned: _on_copies,
    AnswersReturned: _on_answers,
    DispositionsWritten: _on_dispositions,
}
