"""The bus: the stage transitions as messages, one handler each.

    CopiesReturned       one stage's copies, back from the roles
    AnswersReturned      one turn's answers, back from the roles
    DispositionsWritten  the chief's rulings on what is still carried forward

Each handler checks what its message carries, derives the places, opens a
Fold, and on commit builds what the stage saves. A command sends one message
and prints the events; nothing here reads or writes a file, and nothing here
names a row of the three tables.

No handler reads a page. A place carries its own base text, so what the fold
decides comes from the record alone (`decision-log.md Process: #62`); the one
file a later message opens is a file an answer cites, which is verified as a
mark's citation is (`Process: #181`).
"""

from collections.abc import Callable, Mapping
from pathlib import Path
from typing import NamedTuple

from comment_review.binder.binder import Binder
from comment_review.desk.answers.answer import Answer
from comment_review.desk.collator import (
    Cache,
    Problem,
    base_texts,
    drift_in,
    verify_report,
)
from comment_review.desk.containers import EditCopy, MasterProof, Sheet
from comment_review.desk.dispositions.disposition import CHIEF, Disposition
from comment_review.desk.evaluate.place import Place
from comment_review.desk.evaluate.state import CARRIED
from comment_review.desk.stages import Stage
from comment_review.desk.work import events
from comment_review.desk.work.fold import Fold, asked
from comment_review.flows.answers import answers_of, slots_of
from comment_review.flows.mark_errors import mark_errors
from comment_review.flows.places import chief_copy_of, places_of
from comment_review.flows.verify import (
    PageCache,
    coverage_problems,
    resolution_problems,
    stage_problems,
    texts_at,
)


class CopiesReturned(NamedTuple):
    """One stage's copies, back from the roles and ready to fold.

    Attributes:
        stage: the label they were dispatched under -- "4a", "4c".
        copies: one parsed copy per role, or per shard under fan-out. The
            envelope parse is the command's, so a document that is not a
            copy never reaches here.
        binder: the binder they were seeded from -- the base each place is
            measured against, and the page paths an address resolves through.
        root: the checkout a cite and a page are read from.
        topology: the stage as the topology declares it, where the caller
            has one. Without it nothing can know a dispatch was owed.
    """

    stage: str
    copies: list[EditCopy]
    binder: Binder
    root: Path
    topology: Stage | None = None


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
            held to the check a mark's citation is held to
            (`decision-log.md Process: #181`).
    """

    proof: MasterProof
    answers: Mapping[str, object]
    root: Path


class DispositionsWritten(NamedTuple):
    """The chief's rulings on the places the roles never settled.

    Attributes:
        proof: the master proof as the last turn wrote it, or as the first
            fold wrote it where no turn ran -- the baseline.
        dispositions: one ruling per place still carried forward, as the
            chief wrote them. A place left unruled is refused by name, and a
            ruling at a place nothing carries forward is refused too.
    """

    proof: MasterProof
    dispositions: list


class Result(NamedTuple):
    """What a committed fold leaves the stage to save.

    Attributes:
        proof: the copies as they stand, carrying every decided place.
        chief: the copy chief's own edit_copy, one mark per decided place.
        batch: role -> the slots a turn asks it about, or None where the
            fold carried nothing forward.
    """

    proof: MasterProof
    chief: EditCopy | None
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
    """The copies checked, then folded: a commit with a result, or a rollback.

    Everything a copy can be wrong about on its own -- a quote that is not in
    its paragraph, a cite that resolves against nothing, an address no page
    carries, a place a role left unruled, a role short of its shard, a tree
    the other copies were not gathered from -- is found before the fold
    opens, because none of it is a question about how the roles' rulings
    meet. Each becomes one `Refused`, and the fold never runs.
    """
    binder, root, copies = message.binder, message.root, message.copies
    paths = [page.path for page in binder.pages]
    bases = base_texts(binder)
    out: list = []
    # ! ONE CACHE OF EACH FOR THE WHOLE STAGE, not one per copy: the roles cite
    # the same evidence and mark the same pages, so a per-copy cache reads one
    # file once per citing role.
    cache: Cache = {}
    page_cache: PageCache = {}
    problems: list[Problem] = []
    for copy in copies:
        texts = texts_at(copy, paths, root, page_cache)
        problems += verify_report(copy, texts, root, cache)
        problems += resolution_problems(copy, paths, root, page_cache)
        problems += drift_in(copy, bases)
    # ! `where` RATHER THAN `address`, and the two differ in one case only:
    # an entry that named no place. `where` is that entry's own address
    # wherever it has one, and the page and the entry's position where it has
    # none -- so a reader always has somewhere to look. A `Refused` carrying
    # "" would print as a finding about the whole copy, which is a different
    # fact (`collate-command-defects`, measured 2026-09-01).
    problems += [
        Problem(one.role, one.where, "; ".join(one.reasons))
        for one in mark_errors(copies)
    ]
    problems += coverage_problems(copies, binder, message.topology)
    problems += _root_problems(copies)
    if message.topology is not None:
        problems += stage_problems(message.topology, copies)
    if problems:
        for one in problems:
            out.append(events.Refused(one.role, one.address, (one.message,)))
        out.append(events.RolledBack(len(problems)))
        return out, None

    fold = Fold(places_of(copies, bases, _anchors_of(copies)), turn=0).run()
    out += fold.events
    if not fold.committed:
        return out, None
    read_from = copies[0].read_from if copies else {}
    proof = MasterProof(
        stage=message.stage,
        read_from={**read_from},
        edit_copies=tuple(copies),
        places=tuple(place.serialize() for place in fold.decided.values()),
    )
    chief = chief_copy_of(fold.decided, "copy-chief", read_from, _pages_of(copies))
    carried = [place for place in fold.decided.values() if place.state in CARRIED]
    batch = _batch_of(carried, read_from) if carried else None
    return out, Result(proof, chief, batch)


def _root_problems(copies: list[EditCopy]) -> list[Problem]:
    """One `Problem` per copy gathered from a tree the first copy disagrees with.

    Two copies from different trees have no fold between them: their
    addresses answer to different address spaces, so an `a0` in one tells
    nothing about the `a0` in the other. `desk.proof.master_proof_of` raised
    `MismatchedRoot` for this and the handler reaches no `master_proof_of`,
    so the comparison is here -- ruled back in as `decision-log.md Process:
    #178`.

    Reported rather than raised, like everything else the handler finds: a
    refusal that raises empties the report for every other role, measured
    2026-08-30 as exit 1 with an empty stdout.

    Returns:
        One `Problem` per odd copy, naming both `read_from` values, with no
        address -- the finding is about the document. Empty where the copies
        agree, and for a stage with fewer than two.
    """
    if not copies:
        return []
    first = copies[0].read_from
    return [
        Problem(
            copy.role,
            "",
            f"was gathered from {copy.read_from!r}, disagreeing with the first"
            f" edit_copy's {first!r} -- copies from different trees share no"
            " address space",
        )
        for copy in copies[1:]
        if copy.read_from != first
    ]


def _pages_of(copies: list[EditCopy]) -> list[Sheet]:
    """One sheet per page the stage holds, in the order the copies name them.

    Every role was seeded from one binder, so four copies carry four sheets
    for one page. `chief_copy_of` writes one output sheet per sheet it is
    handed, so handing it all of them would write that page's marks once per
    role; the first sheet for a path is kept, with that path's real `path`
    and `sha`.
    """
    out: list[Sheet] = []
    seen: set[str] = set()
    for copy in copies:
        for sheet in copy.sheets:
            if sheet.path not in seen:
                seen.add(sheet.path)
                out.append(sheet)
    return out


def _anchors_of(copies: list[EditCopy]) -> dict[str, str]:
    """The anchor each address's marks carry, for the places built from them."""
    return {
        mark.address: mark.anchor
        for copy in copies
        for sheet in copy.sheets
        for mark in sheet.marks
    }


#: Who a problem with the proof itself is filed against. It is not a role and
#: not the chief: the file was written by a fold, so nobody is being asked to
#: correct a ruling -- the document is being refused.
THE_PROOF = "the master proof"


def _places_on(proof: MasterProof) -> tuple[dict[str, Place], list[Problem]]:
    """The proof's places, read back, or one `Problem` per reason they are not.

    Args:
        proof: the master proof a turn or the chief is folding again.

    Returns:
        `(address -> Place, the problems)`. An entry that will not read back
        is named by its own address where it has one, and by its position
        where it does not; the proof is nobody's copy, so the problem is
        filed against the document rather than against a role.
    """
    places: dict[str, Place] = {}
    problems: list[Problem] = []
    for i, entry in enumerate(proof.places):
        where = str(entry.get("address") or "") if isinstance(entry, dict) else ""
        where = where or f"place {i}"
        place, why = Place.deserialize(where, entry)
        if place is None:
            problems += [
                Problem(THE_PROOF, where, one.removeprefix(f"{where}: ")) for one in why
            ]
        else:
            places[place.address] = place
    return places, problems


def turn_of(proof: MasterProof) -> int:
    """The turn a proof stands at -- the last one any of its places answered.

    0 fresh from the first fold, and one more for each turn folded over it.
    The next turn is this plus one, derived from the record so that nothing
    counts turns of its own.

    Args:
        proof: a master proof, as a fold wrote it.

    Returns:
        The highest turn any place records an answer at, 0 where none does.
    """
    return max(
        (
            int(at)
            for entry in proof.places
            if isinstance(entry, dict)
            for at in (entry.get("answers") or {})
        ),
        default=0,
    )


def _on_answers(message: AnswersReturned) -> tuple[list, Result | None]:
    """One turn's answers written onto the places, then folded again.

    Every role the fold asked owes an answer at every place it was asked
    about, and nothing else may answer: an entry at a place no turn carries
    forward, or at one this role was not asked about, is refused, and so is a
    slot left unanswered. Each refusal voids the round, as a copy's does, so
    a proof is never written over an answer that was not read.
    """
    places, problems = _places_on(message.proof)
    carried = {a: p for a, p in places.items() if p.state in CARRIED}
    turn = turn_of(message.proof) + 1
    given: dict[str, dict[str, Answer]] = {}
    roles = {role for place in carried.values() for role in asked(place)}
    # One cache for the whole turn, as the collate handler keeps one for the
    # whole stage: the roles answer at the same places and cite the same
    # evidence, so a per-role cache reads one file once per answering role.
    cache: Cache = {}
    for role in sorted(roles | set(message.answers)):
        sent = {
            address: {"question": str(place.question), "anchor": place.anchor}
            for address, place in carried.items()
            if role in asked(place)
        }
        returned = slots_of(message.answers.get(role, []), role)
        # A file handed in for a role this turn asked nothing of, holding
        # nothing: every other case names a place, and this one has none to
        # name, so it is reported against the file itself.
        if not sent and not returned:
            problems.append(Problem(role, "", "no slots were sent to this role"))
            continue
        answers, why = answers_of(
            role, sent, returned, _unsent(places, role), message.root, cache
        )
        problems += why
        given[role] = answers
    if problems:
        return _rolled_back(problems)
    for role, answers in given.items():
        for address, answer in answers.items():
            places[address].answers.setdefault(turn, {})[role] = answer
    return _commit(message.proof, places, turn)


def _unsent(places: dict[str, Place], role: str) -> Callable[[str], str]:
    """Why an answer at `address` is not this role's to write, for `answers_of`."""

    def why(address: str) -> str:
        place = places.get(address)
        if place is None or place.state not in CARRIED:
            return "not carried forward"
        return f"not put to {role} -- this place is put to {', '.join(asked(place))}"

    return why


def _on_dispositions(message: DispositionsWritten) -> tuple[list, Result | None]:
    """The chief's rulings written onto the places, then folded to a close.

    Nothing survives the chief's ruling unruled, and nothing is ruled on
    twice: a place carried forward with no ruling is refused by name and with
    the roles it was put to, and a ruling at a place the roles settled, or
    that rides to the human, is refused as well.
    """
    places, problems = _places_on(message.proof)
    for i, entry in enumerate(message.dispositions, 1):
        named = str(entry.get("address") or "") if isinstance(entry, dict) else ""
        where = named or f"ruling {i}"
        disposition, why = Disposition.deserialize(where, entry)
        if disposition is None:
            problems += [
                Problem(CHIEF, where, one.removeprefix(f"{where}: ")) for one in why
            ]
            continue
        place = places.get(disposition.address)
        if place is None or place.state not in CARRIED:
            problems.append(Problem(CHIEF, disposition.address, "not carried forward"))
            continue
        place.disposition = disposition
    for address in sorted(places):
        place = places[address]
        if place.state in CARRIED and place.disposition is None:
            problems.append(
                Problem(
                    CHIEF,
                    address,
                    "carried forward and not ruled on -- it was put to "
                    f"{', '.join(asked(place))}",
                )
            )
    if problems:
        return _rolled_back(problems)
    return _commit(message.proof, places, turn_of(message.proof))


def _rolled_back(problems: list[Problem]) -> tuple[list, None]:
    """Every problem as its own `Refused`, then the rollback -- nothing saved."""
    out: list = [
        events.Refused(one.role, one.address, (one.message,)) for one in problems
    ]
    out.append(events.RolledBack(len(problems)))
    return out, None


def _commit(
    proof: MasterProof, places: dict[str, Place], turn: int
) -> tuple[list, Result | None]:
    """The fold over the places as they now stand, and what a commit saves.

    Args:
        proof: the proof these places were read from. Its stage, its
            `read_from` and its copies are carried onto the next one; what
            the fold decided replaces its places.
        places: the places, each carrying whatever this message wrote onto
            it. `Fold` evaluates every one of them from its own record.
        turn: the turn the fold stands at -- every answer up to it is applied.

    Returns:
        `(the events, the result)`, the result being None on a rollback.
    """
    out: list = []
    fold = Fold(places, turn=turn).run()
    out += fold.events
    if not fold.committed:
        return out, None
    next_proof = MasterProof(
        stage=proof.stage,
        read_from={**proof.read_from},
        edit_copies=proof.edit_copies,
        places=tuple(place.serialize() for place in fold.decided.values()),
    )
    chief = chief_copy_of(
        fold.decided, CHIEF, proof.read_from, _pages_of(list(proof.edit_copies))
    )
    carried = [place for place in fold.decided.values() if place.state in CARRIED]
    batch = _batch_of(carried, proof.read_from) if carried else None
    return out, Result(next_proof, chief, batch)


def _batch_of(carried: list[Place], read_from: dict) -> dict[str, list[dict]]:
    """Role -> one slot per carried-forward place that role is asked about.

    Every slot carries the tree the copies were read from, as an edit_copy and
    a master proof each carry their own: a role hands the slot back as it was
    sent and adds only its answer, so the file its answers arrive in says what
    its citations are resolved against, and `check --answers` defaults its
    root from the file it is handed rather than from the directory it stands
    in.

    Args:
        carried: the places this fold is carrying forward.
        read_from: the proof's own, copied onto each slot rather than aliased.

    Returns:
        role -> its slots. A role nothing is asked of is absent.
    """
    batch: dict[str, list[dict]] = {}
    for place in carried:
        for role in asked(place):
            batch.setdefault(role, []).append(
                {
                    "address": place.address,
                    "anchor": place.anchor,
                    "question": str(place.question),
                    "raw_text": place.text if place.text is not None else place.base,
                    "sides": dict(place.sides),
                    "instruction": None,
                    "read_from": {**read_from},
                }
            )
    return batch


HANDLERS = {
    CopiesReturned: _on_copies,
    AnswersReturned: _on_answers,
    DispositionsWritten: _on_dispositions,
}
