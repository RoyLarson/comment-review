"""The old fold and the new, over one real stage, place by place.

The smoke plants one stage of four roles' copies over a real tree; this runs
that plant as far as `mark`, folds the four copies through `flows._collate`
and through `flows.bus`, and compares what each made of every place. Where
they disagree, the address must be in `EXPLAINED` and the message names the
ruling that accounts for it -- anything else is a defect in the new fold.

The comparison reads the new fold's EVENTS rather than its decided places, so
that a rollback is still legible: a rolled-back fold decides nothing, and each
place has already reported what it came to on the way. Over the plant as it
stands the new fold commits, and the events are what it settled.
"""

import json
import shutil
import subprocess
from pathlib import Path

import pytest
from conftest import ROOT

from comment_review.desk.containers import EditCopy
from comment_review.desk.work import events
from comment_review.flows import _collate as old
from comment_review.flows.bus import CopiesReturned, handle
from comment_review.flows.proof_io import load_binder

#: The rulings that account for a difference. Nothing else may.
#:
#: ! `ADD_SHAPE` WAS THE SIXTH ENTRY AND CAME OUT when `flows.fill` began
#: writing an add's `raw_text` as ruling `#176` has it -- the paragraph as it
#: will read. The six adds the plant files now settle to the same text in both
#: folds, so nothing is left for it to explain.
MOVE_ENDS = (
    "rulings #172 and #175: a move's `change` is the snippet it takes and its"
    " `raw_text` is the destination's text as it will stand, so the origin"
    " keeps what the snippet left behind and the destination takes the"
    " paragraph. The old fold carried one mark under both addresses, so it"
    " settled the origin to the text that belongs at the destination"
)
CLEAN_PLACE = (
    "ruling #174: a place every role cleaned is decided and alters nothing, so"
    " the new fold settles it with no text where the old recorded no ruling"
    " for it at all"
)

#: address -> why the two folds differ there. Every entry must actually
#: differ, and every difference must have an entry.
EXPLAINED = {
    "fib.py@b1": MOVE_ENDS,
    "fib.py@c12": CLEAN_PLACE,
}


@pytest.fixture(scope="session")
def smoke_run():
    """One smoke run stopped after `mark`: the run directory it wrote.

    The script prints that directory as its last line and puts it outside the
    repo; everything above it is the stages' own output, which goes to the
    host and so to this process's stdout as well.
    """
    if shutil.which("pwsh") is None:
        pytest.skip("pwsh is not on PATH")
    done = subprocess.run(
        [
            "pwsh",
            "-NoProfile",
            "-File",
            str(ROOT / "scripts" / "smoke_middle.ps1"),
            "-Stop",
            "mark",
        ],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert done.returncode == 0, done.stdout + done.stderr
    lines = [line.strip() for line in done.stdout.splitlines() if line.strip()]
    assert lines, done.stdout + done.stderr
    return Path(lines[-1])


@pytest.fixture(scope="session")
def folded(smoke_run):
    """`(the old fold, the new fold's events)` over the plant's four copies."""
    binder, why = load_binder(smoke_run / "binder.json")
    assert binder is not None, why
    root = smoke_run / "original"
    wire = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((smoke_run / "copies").glob("*.json"))
    ]
    copies = []
    for one in wire:
        parsed, problems = EditCopy.deserialize("copy", one)
        assert parsed is not None, problems
        copies.append(parsed)
    got = old.collate("4", wire, binder, root)
    out, _result = handle(CopiesReturned("4", copies, binder, root, None))
    return got, out


def _settled(out) -> dict:
    return {one.address: one.text for one in out if isinstance(one, events.Settled)}


def _carried(out) -> set:
    return {one.address for one in out if isinstance(one, events.CarriedForward)}


def _refused(out) -> dict:
    return {one.address: one.reasons for one in out if isinstance(one, events.Refused)}


def test_the_plant_reaches_both_folds(folded):
    """Neither fold is comparing an empty stage."""
    got, out = folded
    assert got.problems == []
    assert len(got.determined) == 6
    assert len(out) > 10


def test_every_place_the_old_fold_settled_the_new_settles_to_the_same_text(folded):
    got, out = folded
    settled = _settled(out)
    for address in sorted(got.determined):
        mark = got.determined[address].mark
        want = mark.change if mark is not None else None
        if address in EXPLAINED:
            assert settled.get(address) != want, (
                f"{address} is listed as a difference and is not one"
            )
            continue
        assert settled.get(address) == want, (
            f"{address}: the old fold settled {want!r} and the new settled"
            f" {settled.get(address)!r}, and no ruling explains it"
        )


def test_the_places_carried_forward_are_the_same_set(folded):
    got, out = folded
    was = {entry["address"] for entry in (*got.escalations, *got.rereads)}
    now = _carried(out)
    for address in sorted(was ^ now):
        assert address in EXPLAINED, (
            f"{address}: the old fold carried it forward"
            f" {'and' if address in was else 'but'} the new"
            f" {'did not' if address in was else 'did'}, and no ruling"
            " explains it"
        )


def test_the_unsettlable_place_is_the_same_place(folded):
    got, out = folded
    was = {entry["address"] for entry in got.unsettlable}
    now = {one.address for one in out if isinstance(one, events.Unsettlable)}
    assert was == now


def test_the_new_fold_refuses_nothing_and_commits(folded):
    """Every mark the plant files reads against its page, so the round stands.

    ! IT ASSERTED THE OPPOSITE UNTIL `flows.fill` WROTE AN ADD'S `raw_text` as
    ruling `#176` has it: the six adds came back carrying the seeded paragraph
    and the added text in `change`, which the marks table read as an add
    dropping every word of its own prose, and the fold rolled back over all
    six."""
    _got, out = folded
    assert _refused(out) == {}
    assert not any(isinstance(one, events.RolledBack) for one in out)
    assert any(isinstance(one, events.Committed) for one in out)


def test_the_advisory_notes_name_the_places_the_old_dropped_list_did(folded):
    """`decision-log.md Process: #163` and `#177`, the two folds' own wording
    of one finding: the old fold's `dropped` list and the new fold's `Advised`
    events must name the same role at the same place.

    ! IT IS EMPTY ON BOTH SIDES over the plant as it stands -- no planted
    `correct` drops a word its claim never named. Compared rather than
    asserted empty, so the day the plant grows one this says whether the two
    folds still agree about it."""
    got, out = folded
    was = {(one.role, one.address) for one in got.dropped}
    now = {(one.role, one.address) for one in out if isinstance(one, events.Advised)}
    assert was == now


def test_no_explanation_is_stale(folded):
    """Every address in `EXPLAINED` really differs between the two folds."""
    got, out = folded
    settled = _settled(out)
    carried_was = {entry["address"] for entry in (*got.escalations, *got.rereads)}
    stale = []
    for address in sorted(EXPLAINED):
        mark = got.determined.get(address)
        same_text = address in got.determined and settled.get(address) == (
            mark.mark.change if mark and mark.mark is not None else None
        )
        differs = (
            address in _refused(out)
            or (address in carried_was) != (address in _carried(out))
            or (address in got.determined and not same_text)
            or (address in settled and address not in got.determined)
        )
        if not differs:
            stale.append(address)
    assert stale == [], f"these no longer differ and can leave EXPLAINED: {stale}"
