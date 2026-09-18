"""The bus: the stage transitions as messages, one handler each.

Each handler checks what its message carries, derives the places, opens a
Fold, and on commit builds what the stage saves. A command sends one message
and prints the events; nothing here reads or writes a file, and nothing here
names a row of the three tables.
"""

from pathlib import Path
from typing import NamedTuple

from comment_review.binder.binder import Binder
from comment_review.desk.collator import (
    Cache,
    Problem,
    base_texts,
    drift_in,
    verify_report,
)
from comment_review.desk.containers import EditCopy, MasterProof, Sheet
from comment_review.desk.evaluate.place import Place
from comment_review.desk.evaluate.state import CARRIED
from comment_review.desk.stages import Stage
from comment_review.desk.work import events
from comment_review.desk.work.fold import Fold, asked
from comment_review.flows import _collate as old
from comment_review.flows.mark_errors import mark_errors
from comment_review.flows.places import chief_copy_of, places_of


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
    carries, a place a role left unruled, a role short of its shard -- is
    found before the fold opens, because none of it is a question about how
    the roles' rulings meet. Each becomes one `Refused`, and the fold never
    runs.
    """
    binder, root, copies = message.binder, message.root, message.copies
    paths = [page.path for page in binder.pages]
    bases = base_texts(binder)
    out: list = []
    # ! ONE CACHE OF EACH FOR THE WHOLE STAGE, not one per copy: the roles cite
    # the same evidence and mark the same pages, so a per-copy cache reads one
    # file once per citing role.
    cache: Cache = {}
    page_cache: old.PageCache = {}
    problems: list[Problem] = []
    for copy in copies:
        texts = old.texts_at(copy, paths, root, page_cache)
        problems += verify_report(copy, texts, root, cache)
        problems += old.resolution_problems(copy, paths, root, page_cache)
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
    problems += old._coverage_problems(copies, binder)
    if message.topology is not None:
        problems += old._stage_problems(message.topology, copies)
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
    return out, Result(proof, chief, _batch_of(carried) if carried else None)


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


def _batch_of(carried: list[Place]) -> dict[str, list[dict]]:
    """Role -> one slot per carried-forward place that role is asked about."""
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
                }
            )
    return batch


HANDLERS = {CopiesReturned: _on_copies}
