"""`stage open` and `stage close`: a stage's tree, binder and copies, from the jacket.

    open_stage(jacket_file, name, repo) -> (lines, problems)
    close_stage(jacket_file, name, proof) -> problems
    stage_of(jacket_file, name) -> (OpenStage | None, problems)
                            an open stage's row, root, binder and copies,
                            which `collate --jacket` folds
    replay(jacket_file, repo, out, only) -> (lines, problems)
                            every closed proof set over the manuscript, which
                            `proof --jacket` drafts

A stage opens once every stage its `reads` chain names has closed. The first
open copies the manuscript. A stage reading `"original"` is gathered from the
checkout. Any other is gathered from `<run-dir>/root<name>`, built here: a
worktree of the jacket's pre-edit commit, the manuscript over it with the
tracked files the checkout had deleted removed, so the tree is the checkout as
the run started, each earlier
stage's closed proof set over that in chain order through `revise.pull`, so
the docket's sha refusal and the address gate run on every stage tree, and
then each file under `<run-dir>/freeform/draft/`. A root already on disk is
refused and left as it is; a build that refuses removes its root. Once the
stage is recorded, removing its root is the caller's.

The gather is the scope plus every page an earlier docket wrote, so a file
that received moved text is read even when the scope does not name it. Its
`read_from` carries the stage's name. The stage's copies are seeded from the
row the jacket holds, into `<run-dir>/copies/`, and the jacket records the
root, the binder and the copies dispatched.

A stage closes when it is open and the proof is closed, stamped with its name,
and folded every copy the jacket records the stage dispatched. A jacket's
stages form one chain and a stage opens only once the one before it closed,
so one stage is open at a time.
The jacket records the proof's path and the sha256 of its bytes, and a later
`stage open` refuses a proof whose bytes changed since.

A run is set once every stage has closed. `replay` builds a tree as a root is
built, without the freeform drafts, and sets each stage's closed proof over it
in topology order, restricted to the places the author accepted where they
named any. A later stage's place on a page whose replayed text differs from
what that stage read is refused by the docket's sha refusal.
"""

import json
import shutil
import tempfile
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import replace
from functools import partial
from pathlib import Path
from typing import NamedTuple

from comment_review import exceptions
from comment_review.binder.addresses import unaddressed
from comment_review.desk.proof.master_proof import MasterProof
from comment_review.desk.stages import Stage
from comment_review.desk.topology import REVISE, read
from comment_review.docket.docket import Docket
from comment_review.flows import revise
from comment_review.flows.distribute import IncompatibleBinder
from comment_review.flows.fan_out import (
    OverlappingShards,
    UncoveredPage,
    received_binder_of,
    write_dealt,
)
from comment_review.flows.gather import gather, not_gathered, unaddressed_report
from comment_review.flows.jacket import (
    MANUSCRIPT,
    Closed,
    Jacket,
    StageEntry,
    load_jacket,
    manuscript_deleted,
    resolved_path,
    save_jacket,
    snapshot_manuscript,
    stored_path,
)
from comment_review.flows.proof_io import load_proof
from comment_review.flows.proof_setter import Refusal
from comment_review.flows.transcribe import (
    CannotAdmit,
    CannotApprove,
    CannotTranscribe,
    docket_of_proof,
    unclosed,
)
from comment_review.machine.digests import sha256_hex
from comment_review.machine.repo import (
    git_worktree_add,
    git_worktree_remove,
    remove_tree,
    walk_files,
    write_raw,
)
from comment_review.reading.addresser import cue_of, flatten

#: Where the freeform drafts a stage tree takes last sit, under the run dir.
FREEFORM_DRAFTS = ("freeform", "draft")

#: Where a stage's copies are written, under the run dir.
COPIES = "copies"

# Bound to names, for the reason `exceptions.py`'s module docstring gives.
DEAL_REFUSALS = (OverlappingShards, UncoveredPage, IncompatibleBinder)
BUILD_ERRORS = (OSError, exceptions.Refused)


class _Refused(Exception):
    """A stage cannot open or close, with every reason."""

    def __init__(self, reasons: list[str]) -> None:
        super().__init__("; ".join(reasons))
        self.reasons = reasons


class UnreadableInput(Exception):
    """The jacket or a closed proof cannot be read as one, with every reason.

    An input that cannot be read, not a refusal of the stage, so the command
    exits on it with its own code.
    """

    def __init__(self, reasons: list[str]) -> None:
        """Hold every reason and say them in the message too."""
        super().__init__("; ".join(reasons))
        self.reasons = reasons


def _rows(jacket_file: Path, name: str) -> tuple[Jacket, list[Stage], Stage]:
    """The jacket, its topology rows and the row named `name`."""
    jacket, problems = load_jacket(jacket_file)
    if jacket is None:
        raise UnreadableInput(problems)
    # The jacket's reader has read the topology, so it reads again.
    rows, _ = read(jacket.topology)
    stage = next((row for row in rows if row.name == name), None)
    if stage is None:
        known = ", ".join(row.name for row in rows)
        raise _Refused(
            [f"stage {name!r} is not a row of the topology -- it holds: {known}"]
        )
    return jacket, rows, stage


def _chain(rows: list[Stage], stage: Stage) -> list[Stage]:
    """The stages `stage` reads after, earliest first; [] if it reads the original."""
    by_name = {row.name: row for row in rows}
    chain: list[Stage] = []
    reads = stage.reads
    # `read` refuses a `reads` naming no earlier row, so every name is a row.
    while reads.startswith(REVISE):
        earlier = by_name[reads[len(REVISE) :]]
        chain.insert(0, earlier)
        reads = earlier.reads
    return chain


def _closed(jacket: Jacket, name: str) -> Closed | None:
    entry = jacket.stages.get(name)
    return entry.closed if entry is not None else None


def open_stage(jacket_file: Path, name: str, repo: Path) -> tuple[list[str], list[str]]:
    """Build stage `name`'s tree, gather it, seed its copies and record it.

    Args:
        jacket_file: the run's `jacket.json`; its directory is the run dir.
        name: the stage to open, a row of the jacket's topology.
        repo: the checkout the run reviews.

    Returns:
        `(the lines to print, [])`, or `([], every reason it did not open)`.

    Raises:
        UnreadableInput: `jacket_file` cannot be read as a jacket, or an
            earlier stage's closed proof cannot be read.
    """
    try:
        return _open(jacket_file, name, repo.resolve()), []
    except _Refused as refused:
        return [], refused.reasons


def _open(jacket_file: Path, name: str, repo: Path) -> list[str]:
    jacket, rows, stage = _rows(jacket_file, name)
    if name in jacket.stages:
        raise _Refused([f"stage {name!r} has already opened"])
    chain = _chain(rows, stage)
    closed = {one.name: _closed(jacket, one.name) for one in chain}
    waiting = [earlier for earlier, proof in closed.items() if proof is None]
    if waiting:
        raise _Refused(
            [
                f"stage {name!r} reads after {', '.join(waiting)}, which has not"
                " closed -- close each earlier stage first"
            ]
        )
    proofs = [
        _closed_proof(jacket_file, earlier, proof)
        for earlier, proof in closed.items()
        if proof is not None
    ]
    run_dir = jacket_file.parent
    if not (run_dir / MANUSCRIPT).exists():
        _, problems = snapshot_manuscript(repo, jacket.scope, run_dir, jacket.ref)
        if problems:
            raise _Refused(problems)
    if not chain:
        return _gather_and_seed(jacket_file, jacket, stage, repo, [], 0)
    root = run_dir / f"root{name}"
    if root.exists() or root.is_symlink():
        raise _Refused(
            [f"{root} already exists -- a leftover root is removed, never reused"]
        )
    why = git_worktree_add(repo, root, jacket.ref)
    if why:
        raise _Refused([why])
    try:
        written = _build(root, run_dir, proofs)
        return _gather_and_seed(
            jacket_file, jacket, stage, root.resolve(), written, len(chain)
        )
    except BaseException:
        # An unrecorded root would be a leftover the next `stage open` refuses.
        git_worktree_remove(repo, root)
        raise


def _closed_proof(jacket_file: Path, name: str, closed: Closed) -> MasterProof:
    """Stage `name`'s closed proof, refused where its bytes changed since it closed."""
    path = resolved_path(closed.proof, jacket_file)
    try:
        sha = sha256_hex(path.read_bytes())
    except OSError as err:
        raise UnreadableInput([f"stage {name!r}'s closed proof {path}: {err}"]) from err
    if sha != closed.sha256:
        raise _Refused(
            [f"stage {name!r}'s closed proof {path} changed since it closed"]
        )
    proof, problems = load_proof(path)
    if proof is None:
        raise UnreadableInput(problems)
    return proof


def _build(root: Path, run_dir: Path, proofs: list[MasterProof]) -> list[str]:
    """Set the manuscript, each proof and the freeform drafts over `root`.

    The tracked files the checkout had deleted when the run started are
    removed after the manuscript is set.

    Returns:
        Every page an earlier docket wrote, repo-relative posix, sorted.
    """
    written: set[str] = set()
    with _setting(root):
        _start(root, run_dir)
        for number, proof in enumerate(proofs, 1):
            docket = docket_of_proof(proof, root)
            refusals = _set(docket, root, run_dir, number)
            if refusals:
                raise _Refused(_refusal_lines(proof.stage, refusals))
            written.update(schedule.path for schedule in docket.schedules)
        _overlay(run_dir.joinpath(*FREEFORM_DRAFTS), root)
    return sorted(written)


@contextmanager
def _setting(root: Path) -> Iterator[None]:
    """Turn what setting a proof over `root` raises into the stage's refusal."""
    try:
        yield
    except CannotTranscribe as refused:
        raise _Refused(list(refused.reasons)) from refused
    except revise.AddressesMoved as moved:
        raise _Refused([f"the address space moved -- {moved}"]) from moved
    except OSError as err:
        raise _Refused([f"cannot build {root}: {err}"]) from err


def _start(root: Path, run_dir: Path) -> None:
    """Set the manuscript over `root` and remove the files the checkout had deleted."""
    deleted, problems = manuscript_deleted(run_dir)
    if problems:
        raise _Refused(problems)
    _overlay(run_dir / MANUSCRIPT, root)
    for rel in deleted:
        (root / rel).unlink(missing_ok=True)


def _set(docket: Docket, root: Path, run_dir: Path, number: int) -> list[Refusal]:
    """Set `docket` over `root` through `revise.pull`; what refused, or [] once set."""
    if not docket.schedules:
        return []
    scratch = Path(tempfile.mkdtemp(prefix="pull-", dir=run_dir))
    try:
        pulled = revise.pull(docket, root, scratch / "revise", revise=number)
        if pulled.refusals:
            return pulled.refusals
        for schedule in docket.schedules:
            shutil.copyfile(pulled.root / schedule.path, root / schedule.path)
        return []
    finally:
        remove_tree(scratch, ignore_errors=True)


def _refusal_lines(
    stage: str, refusals: list[Refusal], why: Callable[[Refusal], str] = lambda _: ""
) -> list[str]:
    """One line per refusal setting stage `stage`'s proof, each with `why` after it."""
    return [
        f"stage {stage!r}: REFUSED at {one.step}: {one.path or '<the set>'}"
        f" -- {one.why}{why(one)}"
        for one in refusals
    ]


def _overlay(source: Path, root: Path) -> None:
    """Copy every file under `source` to the same relative path under `root`."""
    if not source.is_dir():
        return
    for path in walk_files(source):
        target = root / path.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)


def _gather_and_seed(
    jacket_file: Path,
    jacket: Jacket,
    stage: Stage,
    root: Path,
    written: list[str],
    revise_number: int,
) -> list[str]:
    """Gather `root`, seed the stage's copies, record the stage; the lines to print."""
    targets = [root / rel for rel in jacket.scope]
    targets += [root / rel for rel in written if rel not in jacket.scope]
    got = gather(root, targets, revise_number, stage=stage.name)
    if got.unreadable:
        raise _Refused([not_gathered(len(targets), got.unreadable)])
    missing = unaddressed(got.binder.paragraphs)
    if missing:
        raise _Refused([unaddressed_report(missing)])
    run_dir = jacket_file.parent
    binder_path = run_dir / f"binder{stage.name}.json"
    wire = got.binder.serialize()
    try:
        write_raw(binder_path, json.dumps(wire, indent=1, default=str))
        copies = write_dealt(got.binder, stage, run_dir / COPIES)
        entry = StageEntry(
            root=stored_path(root, jacket_file),
            binder=stored_path(binder_path, jacket_file),
            dispatched=tuple(stored_path(path, jacket_file) for path, _ in copies),
        )
        save_jacket(
            jacket_file, replace(jacket, stages={**jacket.stages, stage.name: entry})
        )
    except DEAL_REFUSALS as refused:
        raise _Refused([f"stage {stage.name!r}: {refused}"]) from refused
    except BUILD_ERRORS as err:
        raise _Refused([f"stage {stage.name!r}: {err}"]) from err
    places = sum(len(page["rows"]) for page in wire["pages"])
    return [
        f"stage {stage.name!r} opened: root {root}; binder {binder_path},"
        f" {places} places on {len(wire['pages'])} pages",
        *(line for _, line in copies),
    ]


def close_stage(jacket_file: Path, name: str, proof_path: Path) -> list[str]:
    """Record `proof_path` as stage `name`'s closed proof.

    Returns:
        `[]` once the jacket records it, or every reason it does not.

    Raises:
        UnreadableInput: `jacket_file` cannot be read as a jacket, or
            `proof_path` as a master proof.
    """
    try:
        _close(jacket_file, name, proof_path)
    except _Refused as refused:
        return refused.reasons
    return []


def _close(jacket_file: Path, name: str, proof_path: Path) -> None:
    jacket, _, _ = _rows(jacket_file, name)
    entry = jacket.stages.get(name)
    if entry is None:
        raise _Refused([f"stage {name!r} has not opened"])
    if entry.closed is not None:
        raise _Refused([f"stage {name!r} has already closed"])
    proof, problems = load_proof(proof_path)
    if proof is None:
        raise UnreadableInput(problems)
    if proof.stage != name:
        raise _Refused(
            [f"{proof_path} is stage {proof.stage!r}'s proof, not stage {name!r}'s"]
        )
    still_open = unclosed(proof)
    if still_open:
        raise _Refused([f"{proof_path} has not closed", *still_open])
    if proof.returned != entry.dispatched:
        missing = [one for one in entry.dispatched if one not in proof.returned]
        raise _Refused(
            [
                f"{proof_path} folded {len(proof.returned)} of the"
                f" {len(entry.dispatched)} copies stage {name!r} dispatched"
                + (f"; not returned: {', '.join(missing)}" if missing else "")
            ]
        )
    try:
        closed = Closed(
            stored_path(proof_path, jacket_file),
            sha256_hex(proof_path.read_bytes()),
        )
        save_jacket(
            jacket_file,
            replace(
                jacket, stages={**jacket.stages, name: replace(entry, closed=closed)}
            ),
        )
    except BUILD_ERRORS as err:
        raise _Refused([f"stage {name!r}: {err}"]) from err


def replay(
    jacket_file: Path, repo: Path, out: Path, only: tuple[str, ...] | None = None
) -> tuple[list[str], list[str]]:
    """Set every stage's closed proof over the manuscript; draft each page written.

    The tree is built as `stage open` builds a root, and each stage's proof is
    set over it in topology order through `revise.pull`, so a stage's place on
    a page whose replayed text differs from the text that stage read is
    refused by the docket's sha refusal.

    Args:
        jacket_file: the run's `jacket.json`.
        repo: the checkout the run reviews.
        out: where the drafts are written, one per page a proof set, at its
            repo path. Must not exist yet.
        only: the places the author accepted, each `<stage>:<address>`; None
            accepts every place.

    Returns:
        `(the lines to print, [])`, or `([], every reason nothing was drafted)`.
        A sha refusal names each place an earlier stage set on that page that
        the author did not accept.

    Raises:
        UnreadableInput: `jacket_file` cannot be read as a jacket, a closed
            proof cannot be read, or a page identity it claims will not admit.
    """
    try:
        return _replay(jacket_file, repo.resolve(), out, only), []
    except _Refused as refused:
        return [], refused.reasons


def _replay(
    jacket_file: Path, repo: Path, out: Path, only: tuple[str, ...] | None
) -> list[str]:
    jacket, problems = load_jacket(jacket_file)
    if jacket is None:
        raise UnreadableInput(problems)
    rows, _ = read(jacket.topology)
    closed = {row.name: _closed(jacket, row.name) for row in rows}
    waiting = [name for name, proof in closed.items() if proof is None]
    if waiting:
        raise _Refused(
            [
                f"stage {', '.join(waiting)} has not closed -- every stage of the"
                " topology closes before the run is set"
            ]
        )
    accepted = _accepted(only, list(closed))
    proofs = [
        (name, _closed_proof(jacket_file, name, proof))
        for name, proof in closed.items()
        if proof is not None
    ]
    run_dir = jacket_file.parent
    scratch = Path(tempfile.mkdtemp(prefix="replay-", dir=run_dir))
    tree = scratch / "tree"
    try:
        why = git_worktree_add(repo, tree, jacket.ref)
        if why:
            raise _Refused([why])
        written = _replayed(tree, run_dir, proofs, accepted)
        try:
            for rel in written:
                (out / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(tree / rel, out / rel)
        except OSError as err:
            remove_tree(out, ignore_errors=True)
            raise _Refused([f"cannot write the drafts into {out}: {err}"]) from err
    finally:
        git_worktree_remove(repo, tree)
        remove_tree(scratch, ignore_errors=True)
    return [
        *(f"{rel} -> {out / rel}" for rel in written),
        f"{len(written)} page(s) drafted for review",
    ]


def _accepted(
    only: tuple[str, ...] | None, names: list[str]
) -> dict[str, tuple[str, ...]] | None:
    """Each stage's accepted addresses, from `<stage>:<address>`; None accepts all."""
    if only is None:
        return None
    by_stage: dict[str, list[str]] = {name: [] for name in names}
    bad = []
    for one in only:
        name, colon, address = one.partition(":")
        if colon and address and name in by_stage:
            by_stage[name].append(address)
        else:
            bad.append(
                f"{one!r} names no stage's place -- name each as <stage>:<address>,"
                f" the stage one of {', '.join(names)}"
            )
    if bad:
        raise _Refused(bad)
    return {name: tuple(addresses) for name, addresses in by_stage.items()}


def _replayed(
    tree: Path,
    run_dir: Path,
    proofs: list[tuple[str, MasterProof]],
    accepted: dict[str, tuple[str, ...]] | None,
) -> list[str]:
    """Set the manuscript and each stage's accepted places over `tree`.

    Returns:
        Every page a proof set, repo-relative posix, sorted.
    """
    written: set[str] = set()
    # The flattened page name -> each `<stage>:<address>` set there that the
    # author did not accept.
    declined: dict[str, list[str]] = {}

    def unaccepted(name: str, one: Refusal) -> str:
        names = declined.get(flatten(one.path), []) if one.step == "verify" else []
        if not names:
            return ""
        return (
            f"; stage {name!r} read {one.path} with {', '.join(names)} set, and the"
            f" author did not accept {'it' if len(names) == 1 else 'them'} -- accept"
            f" {'it' if len(names) == 1 else 'them'} too, or decline stage"
            f" {name!r}'s places on {one.path}"
        )

    with _setting(tree):
        _start(tree, run_dir)
        for number, (name, proof) in enumerate(proofs, 1):
            only = None if accepted is None else accepted[name]
            try:
                docket = docket_of_proof(proof, tree, only=only)
            except CannotAdmit as unread:
                raise UnreadableInput(list(unread.reasons)) from unread
            except CannotApprove as refused:
                raise _Refused(
                    [
                        f"stage {name!r}: the approval names a place this proof"
                        " cannot set",
                        *refused.reasons,
                    ]
                ) from refused
            refusals = _set(docket, tree, run_dir, number)
            if refusals:
                raise _Refused(
                    _refusal_lines(name, refusals, partial(unaccepted, name))
                )
            written.update(schedule.path for schedule in docket.schedules)
            if only is not None:
                for place in proof.places:
                    if place.changed and place.address not in only:
                        declined.setdefault(cue_of(place.address).path, []).append(
                            f"{name}:{place.address}"
                        )
    return sorted(written)


class Dispatched(NamedTuple):
    """One copy an open stage dispatched.

    Attributes:
        name: the copy as the jacket records it, relative to the jacket file.
        copy: the copy's path.
        binder: its received binder's path.
        role: the role its dispatch names.
    """

    name: str
    copy: Path
    binder: Path
    role: str


class OpenStage(NamedTuple):
    """What `collate` folds an open stage from, all of it off the jacket.

    Attributes:
        row: the stage's topology row.
        root: the tree the stage was gathered from.
        binder: the stage's binder.
        dispatched: each copy the stage dispatched, in dispatch order.
    """

    row: Stage
    root: Path
    binder: Path
    dispatched: tuple[Dispatched, ...]


def stage_of(jacket_file: Path, name: str) -> tuple[OpenStage | None, list[str]]:
    """Stage `name` as the jacket records it, while it is open.

    Returns:
        `(the stage, [])`, or `(None, reasons)` where it is not a row, has not
        opened, has closed, or records another count of copies than its row
        dispatches.

    Raises:
        UnreadableInput: `jacket_file` cannot be read as a jacket.
    """
    try:
        jacket, _, row = _rows(jacket_file, name)
    except _Refused as refused:
        return None, refused.reasons
    entry = jacket.stages.get(name)
    if entry is None:
        return None, [f"stage {name!r} has not opened -- open it with `stage open`"]
    if entry.closed is not None:
        return None, [f"stage {name!r} has already closed"]
    if len(entry.dispatched) != len(row.dispatches):
        return None, [
            f"{jacket_file} records {len(entry.dispatched)} copies for stage"
            f" {name!r}, and its row dispatches {len(row.dispatches)}"
        ]
    dispatched = []
    for stored, dispatch in zip(entry.dispatched, row.dispatches, strict=True):
        copy = resolved_path(stored, jacket_file)
        dispatched.append(
            Dispatched(stored, copy, received_binder_of(copy), str(dispatch.role))
        )
    return (
        OpenStage(
            row,
            resolved_path(entry.root, jacket_file),
            resolved_path(entry.binder, jacket_file),
            tuple(dispatched),
        ),
        [],
    )
