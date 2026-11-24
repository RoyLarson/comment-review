"""`stage open` and `stage close`: a stage's tree, binder and copies, from the jacket.

    open_stage(jacket_file, name, repo) -> (lines, problems)
    close_stage(jacket_file, name, proof) -> problems

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

A stage closes in topology order: it is open, it is the first row not closed
whose chain has closed, and the proof is closed and stamped with its name.
The jacket records the proof's path and the sha256 of its bytes, and a later
`stage open` refuses a proof whose bytes changed since.
"""

import json
import shutil
import tempfile
from dataclasses import replace
from pathlib import Path

from comment_review import exceptions
from comment_review.binder.addresses import unaddressed
from comment_review.desk.proof.master_proof import MasterProof
from comment_review.desk.stages import Stage
from comment_review.desk.topology import REVISE, read
from comment_review.flows import revise
from comment_review.flows.distribute import IncompatibleBinder
from comment_review.flows.fan_out import OverlappingShards, UncoveredPage, write_dealt
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
from comment_review.flows.transcribe import CannotTranscribe, docket_of_proof, unclosed
from comment_review.machine.digests import sha256_hex
from comment_review.machine.repo import (
    git_worktree_add,
    git_worktree_remove,
    remove_tree,
    walk_files,
    write_raw,
)

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
    deleted, problems = manuscript_deleted(run_dir)
    if problems:
        raise _Refused(problems)
    try:
        _overlay(run_dir / MANUSCRIPT, root)
        for rel in deleted:
            (root / rel).unlink(missing_ok=True)
        for number, proof in enumerate(proofs, 1):
            docket = docket_of_proof(proof, root)
            if not docket.schedules:
                continue
            scratch = Path(tempfile.mkdtemp(prefix="pull-", dir=run_dir))
            try:
                pulled = revise.pull(docket, root, scratch / "revise", revise=number)
                if pulled.refusals:
                    raise _Refused(
                        [
                            f"stage {proof.stage!r}: REFUSED at {one.step}:"
                            f" {one.path or '<the set>'} -- {one.why}"
                            for one in pulled.refusals
                        ]
                    )
                for schedule in docket.schedules:
                    shutil.copyfile(pulled.root / schedule.path, root / schedule.path)
                    written.add(schedule.path)
            finally:
                remove_tree(scratch, ignore_errors=True)
        _overlay(run_dir.joinpath(*FREEFORM_DRAFTS), root)
    except CannotTranscribe as refused:
        raise _Refused(list(refused.reasons)) from refused
    except revise.AddressesMoved as moved:
        raise _Refused([f"the address space moved -- {moved}"]) from moved
    except OSError as err:
        raise _Refused([f"cannot build {root}: {err}"]) from err
    return sorted(written)


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
    jacket, rows, _ = _rows(jacket_file, name)
    entry = jacket.stages.get(name)
    if entry is None:
        raise _Refused([f"stage {name!r} has not opened"])
    if entry.closed is not None:
        raise _Refused([f"stage {name!r} has already closed"])
    after = next(
        (
            row.name
            for row in rows
            if _closed(jacket, row.name) is None
            and all(_closed(jacket, one.name) for one in _chain(rows, row))
        ),
        None,
    )
    if after != name:
        raise _Refused([f"stage {name!r} is not next to close -- {after!r} is"])
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
