"""The JACKET: the one record of a run, written only by commands.

    Jacket                  the pre-edit ref, the scope, the topology rows and
                            each opened stage's entry
    jacket_to_wire / jacket_from_wire
                            the wire pair; the reader refuses every malformed
                            shape by name
    load_jacket / save_jacket
                            `<run-dir>/jacket.json` off and onto disk
    stored_path / resolved_path
                            a path as the jacket records it, relative to the
                            jacket file, and back
    put_topology            write a built topology's rows into the run's jacket;
                            rows that are not one chain are refused
    snapshot_manuscript     copy the manuscript into `<run-dir>/manuscript/`
    manuscript_deleted      the tracked files the checkout had deleted

A job jacket holds every proof of one job. This one holds references, not
copies: a stage's binder and its closed proof each carry their own pages' shas,
so the jacket names those files and records the closed proof's sha256, and holds
no per-page sha of its own.

Every path the jacket records is relative to the jacket file's directory, so a
run reads the same from any working directory and no home path is written into
the record.

The manuscript is the text the run started from: each file in scope, walked as
`flows.gather` walks it, each untracked file the checkout holds, so text no
commit carries is reviewed and can be cited, and each tracked file whose bytes
differ from a fresh checkout of the pre-edit commit, with the list of tracked
files deleted. A later
stage's tree is built from it rather than from whatever the checkout holds by
then.

Nothing outside `flows` imports `Jacket`; a consumer declares a `Protocol` of
what it reads.
"""

import json
import re
import shutil
import tempfile
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import cast

from comment_review import exceptions
from comment_review.desk.stages import Stage
from comment_review.desk.topology import REVISE, read
from comment_review.flows.proof_io import load_text
from comment_review.machine.json_object import object_of
from comment_review.machine.repo import (
    EXCLUDED_DIRS,
    can_escape,
    commit_of,
    git_ls_files,
    git_untracked,
    git_worktree_add,
    git_worktree_remove,
    relative_to,
    remove_tree,
    walk_files,
    write_raw,
)

#: The jacket's file name under a run directory.
JACKET_FILE = "jacket.json"

#: The directory under a run directory the manuscript is copied into.
MANUSCRIPT = "manuscript"

#: The file under a run directory naming the tracked files the checkout had
#: deleted when the manuscript was copied.
MANUSCRIPT_DELETED = "manuscript-deleted.json"

#: The wire's format number; a reader refuses any other.
FORMAT = 1

_SHA256 = re.compile(r"[0-9a-f]{64}")


@dataclass(frozen=True)
class Closed:
    """A stage's closed proof.

    Attributes:
        proof: the closed proof's path, relative to the jacket file.
        sha256: the hex sha256 of that file's bytes when the stage closed.
    """

    proof: str
    sha256: str


@dataclass(frozen=True)
class StageEntry:
    """One opened stage, as the jacket records it.

    Attributes:
        root: the tree the stage was gathered from, relative to the jacket file.
        binder: the stage's binder, relative to the jacket file.
        dispatched: the names of the edit copies the stage dispatched.
        closed: the stage's closed proof, or None while the stage is open.
    """

    root: str
    binder: str
    dispatched: tuple[str, ...]
    closed: Closed | None = None


@dataclass(frozen=True)
class Jacket:
    """The run's record.

    Attributes:
        ref: the full sha of the pre-edit commit.
        scope: the paths under review, repo-relative, as the gather is given them.
        topology: the topology rows, verbatim -- text `desk.topology.read` accepts,
            forming one chain: the first row reads `"original"` and each
            other row reads `"revise:<the row above it>"`.
        stages: each opened stage's entry, by the stage's name, in opening order.
    """

    ref: str
    scope: tuple[str, ...]
    topology: str
    stages: dict[str, StageEntry] = field(default_factory=dict)


def jacket_to_wire(jacket: Jacket) -> dict:
    """The jacket as its JSON object."""
    return {
        "format": FORMAT,
        "ref": jacket.ref,
        "scope": list(jacket.scope),
        "topology": jacket.topology,
        "stages": {
            name: {
                "root": entry.root,
                "binder": entry.binder,
                "dispatched": list(entry.dispatched),
                "closed": None
                if entry.closed is None
                else {"proof": entry.closed.proof, "sha256": entry.closed.sha256},
            }
            for name, entry in jacket.stages.items()
        },
    }


def jacket_from_wire(where: str, value: object) -> tuple[Jacket | None, list[str]]:
    """The jacket this JSON value holds, or `(None, reasons)` naming `where`."""

    def refused(message: str) -> tuple[None, list[str]]:
        return None, [f"{where}: {message}"]

    why = _keys(value, {"format", "ref", "scope", "topology", "stages"}, "the jacket")
    if why:
        return refused(why)
    wire = cast(dict, value)
    if type(wire["format"]) is not int or wire["format"] != FORMAT:
        return refused(f"format must be the integer {FORMAT}")
    ref = wire["ref"]
    if not isinstance(ref, str) or not ref:
        return refused("ref must name the pre-edit commit")
    scope = wire["scope"]
    if not _strings(scope) or not scope:
        return refused("scope must be a non-empty list of paths")
    escaping = [p for p in scope if can_escape(p)]
    if escaping:
        return refused(f"scope path {escaping[0]!r} is not relative to the checkout")
    topology = wire["topology"]
    if not isinstance(topology, str):
        return refused("topology must be the topology's text")
    rows, why = read(topology)
    if why:
        return refused(why)
    why = _not_a_chain(rows)
    if why:
        return refused(why)
    raw_stages = wire["stages"]
    if not isinstance(raw_stages, dict):
        return refused("stages must be an object of stage name to entry")
    names = {row.name for row in rows}
    stages: dict[str, StageEntry] = {}
    for name, raw in raw_stages.items():
        if name not in names:
            return refused(f"stage {name!r} is not a row of the topology")
        entry, why = _entry(raw)
        if entry is None:
            return refused(f"stage {name!r}: {why}")
        stages[name] = entry
    return Jacket(ref, tuple(scope), topology, stages), []


def _not_a_chain(rows: list[Stage]) -> str:
    """Why these rows are not one chain, naming the stage that breaks it, or "".

    The run is set by replaying each stage's proof over the one before it, so
    the first row reads the original and every other row reads the revise of
    the row above it.
    """
    for before, row in zip([None, *rows], rows, strict=False):
        owed = "original" if before is None else f"{REVISE}{before.name}"
        if row.reads != owed:
            return (
                f"stage {row.name!r} reads {row.reads!r}, and a run's stages form"
                f" one chain, so it reads {owed!r}"
            )
    return ""


def _entry(raw: object) -> tuple[StageEntry | None, str]:
    """One stage's entry, or the reason it is not one."""
    why = _keys(raw, {"root", "binder", "dispatched", "closed"}, "the entry")
    if why:
        return None, why
    wire = cast(dict, raw)
    for key in ("root", "binder"):
        why = _stored(wire[key], key)
        if why:
            return None, why
    if not _strings(wire["dispatched"]):
        return None, "dispatched must be a list of copy names"
    raw_closed = wire["closed"]
    closed = None
    if raw_closed is not None:
        why = _keys(raw_closed, {"proof", "sha256"}, "closed")
        if why:
            return None, why
        why = _stored(raw_closed["proof"], "closed proof")
        if why:
            return None, why
        sha = raw_closed["sha256"]
        if not isinstance(sha, str) or not _SHA256.fullmatch(sha):
            return None, "closed sha256 must be 64 lowercase hex digits"
        closed = Closed(raw_closed["proof"], sha)
    return (
        StageEntry(wire["root"], wire["binder"], tuple(wire["dispatched"]), closed),
        "",
    )


def _keys(value: object, required: set[str], what: str) -> str:
    """Why this is not an object holding exactly these keys, or ""."""
    if not isinstance(value, dict):
        return f"{what} must be an object"
    missing = required - value.keys()
    if missing:
        return f"{what} is missing {', '.join(sorted(missing))}"
    extra = value.keys() - required
    if extra:
        return f"{what} holds unknown keys: {', '.join(sorted(map(str, extra)))}"
    return ""


def _strings(value: object) -> bool:
    return isinstance(value, list) and all(isinstance(one, str) for one in value)


def _stored(value: object, what: str) -> str:
    """Why this is not a path relative to the jacket file, or ""."""
    if not isinstance(value, str) or not value:
        return f"{what} must be a path"
    path = Path(value)
    if path.is_absolute() or path.drive or path.root:
        return f"{what} {value!r} is not relative to the jacket file"
    return ""


def load_jacket(path: Path) -> tuple[Jacket | None, list[str]]:
    """The jacket at `path`, or every reason it is not one."""
    text, why = load_text(path)
    if text is None:
        return None, why
    loaded, problem = object_of(text, "jacket")
    if problem:
        return None, [f"{path} is {problem}"]
    return jacket_from_wire(str(path), loaded)


def save_jacket(path: Path, jacket: Jacket) -> None:
    """Write the jacket at `path`, refusing one its own reader would refuse.

    Raises:
        exceptions.Refused: the jacket does not read back, with the reasons.
    """
    wire = jacket_to_wire(jacket)
    _, problems = jacket_from_wire(str(path), wire)
    if problems:
        raise exceptions.Refused("; ".join(problems))
    write_raw(path, json.dumps(wire, indent=2))


def stored_path(path: Path, jacket_file: Path) -> str:
    """`path` as the jacket records it: posix, relative to the jacket file.

    Raises:
        exceptions.Refused: `path` and the jacket are on different drives, so
            no relative form exists.
    """
    got = relative_to(path, jacket_file.parent)
    if got.is_absolute():
        raise exceptions.Refused(
            f"{path} has no path relative to {jacket_file}; keep the run's trees"
            " on the jacket's drive"
        )
    return got.as_posix()


def resolved_path(stored: str, jacket_file: Path) -> Path:
    """The absolute path a path the jacket records names."""
    return (jacket_file.parent / stored).resolve()


def put_topology(
    run_dir: Path, topology: str, ref: str, scope: tuple[str, ...], repo: Path
) -> list[str]:
    """Write `topology` into the run's jacket, creating the jacket where none is.

    A new jacket needs `ref` and `scope`. `ref` is resolved in `repo` to the
    full sha of the commit it names, and the sha is what the jacket records,
    so a branch or `HEAD` moving later does not move the run's pre-edit
    commit; a `ref` naming no commit is refused. An existing jacket keeps its
    own: a `ref` resolving to another commit, or a `scope` that differs, is
    refused, and so is any new topology once a stage has opened, because that
    stage's entry was built from the rows already recorded.

    Returns:
        `[]` once the jacket is written, or every reason it was not.
    """
    path = run_dir / JACKET_FILE
    sha = ""
    if ref:
        sha = commit_of(repo, ref) or ""
        if not sha:
            return [f"{ref!r} names no commit in {repo}"]
    if path.exists():
        jacket, problems = load_jacket(path)
        if jacket is None:
            return problems
        if jacket.stages:
            opened = ", ".join(jacket.stages)
            return [f"{path}: stage {opened} has opened, so its topology is fixed"]
        if sha and sha != jacket.ref:
            return [f"{path} records the pre-edit ref {jacket.ref}, not {sha}"]
        if scope and scope != jacket.scope:
            return [f"{path} records the scope {' '.join(jacket.scope)}"]
        jacket = replace(jacket, topology=topology)
    else:
        if not sha or not scope:
            return [
                f"{path} does not exist; a new jacket needs the pre-edit ref"
                " and the scope"
            ]
        jacket = Jacket(sha, scope, topology)
    try:
        save_jacket(path, jacket)
    except exceptions.Refused as refusal:
        return [str(refusal)]
    return []


def snapshot_manuscript(
    repo: Path, scope: tuple[str, ...], run_dir: Path, ref: str
) -> tuple[list[str], list[str]]:
    """Copy the manuscript from the checkout into `<run-dir>/manuscript/`.

    Each file in scope, walked as the gather walks it, each untracked file git
    does not ignore, and each tracked file whose bytes differ from a fresh
    checkout of `ref`, at its repo path, byte for byte. Each tracked file the
    checkout deleted is listed in `<run-dir>/manuscript-deleted.json`, so a
    worktree of `ref` with the manuscript over it and those files removed is
    the checkout as the run started, byte for byte. A manuscript already on
    disk is refused and left as it is; any other refusal leaves none.

    Returns:
        `(the repo-relative paths copied, sorted, [])`, or `([], reasons)`.
    """
    repo = repo.resolve()
    into = run_dir / MANUSCRIPT
    if into.exists() or into.is_symlink():
        return [], [f"{into} already exists; a run's manuscript is copied once"]
    rels: set[str] = set()
    problems: list[str] = []
    for target in scope:
        if can_escape(target):
            problems.append(f"{target} (not relative to the checkout)")
            continue
        found = [p.relative_to(repo).as_posix() for p in walk_files(repo / target)]
        if not found:
            problems.append(f"{target} (matched no files)")
        rels.update(found)
    untracked = git_untracked(repo)
    if untracked is None:
        problems.append(f"git could not list the untracked files in {repo}")
    if problems:
        return [], problems
    rels.update(
        rel
        for rel in cast(list[str], untracked)
        if not EXCLUDED_DIRS.intersection(Path(rel).parts)
    )
    present, deleted, problems = _differs_from_ref(repo, run_dir, ref)
    if problems:
        return [], problems
    rels.update(present)
    copied = sorted(rels)
    try:
        for rel in copied:
            (into / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(repo / rel, into / rel)
        write_raw(run_dir / MANUSCRIPT_DELETED, json.dumps(sorted(deleted), indent=2))
    except OSError as err:
        remove_tree(into, ignore_errors=True)
        return [], [f"cannot copy the manuscript into {into}: {err}"]
    return copied, []


def _differs_from_ref(
    repo: Path, run_dir: Path, ref: str
) -> tuple[list[str], list[str], list[str]]:
    """The tracked paths whose checkout bytes differ from a checkout of `ref`.

    `ref` is checked out once, as a worktree under `run_dir` that is removed
    before this returns, and each path is compared byte for byte, so a line
    ending `core.autocrlf` or `.gitattributes` writes differently counts as a
    difference. A path tracked in `ref` or in the index is asked; one that is
    not a file in the checkout is deleted there.

    Returns:
        `(paths whose checkout file differs, paths the checkout deleted, [])`,
        each repo-relative posix, or `([], [], reasons)`.
    """
    run_dir.mkdir(parents=True, exist_ok=True)
    scratch = Path(tempfile.mkdtemp(prefix="ref-", dir=run_dir))
    fresh = scratch / "ref"
    try:
        why = git_worktree_add(repo, fresh, ref)
        if why:
            return [], [], [why]
        in_ref = git_ls_files(fresh)
        in_index = git_ls_files(repo)
        if in_ref is None or in_index is None:
            return [], [], [f"git could not list the tracked files of {ref}"]
        present: list[str] = []
        deleted: list[str] = []
        for rel in sorted({*in_ref, *in_index}):
            mine = repo / rel
            if not mine.is_file():
                # A tracked directory -- a submodule -- is not a file to copy.
                if not mine.exists():
                    deleted.append(rel)
                continue
            theirs = fresh / rel
            if not theirs.is_file() or not _same_bytes(mine, theirs):
                present.append(rel)
        return present, deleted, []
    except OSError as err:
        return [], [], [f"cannot compare {repo} with {ref}: {err}"]
    finally:
        git_worktree_remove(repo, fresh)
        remove_tree(scratch, ignore_errors=True)


def _same_bytes(one: Path, other: Path) -> bool:
    return one.stat().st_size == other.stat().st_size and (
        one.read_bytes() == other.read_bytes()
    )


def manuscript_deleted(run_dir: Path) -> tuple[list[str], list[str]]:
    """The tracked files the checkout had deleted when the run started.

    Returns:
        `(repo-relative paths, [])`, or `([], the reason they cannot be read)`.
    """
    path = run_dir / MANUSCRIPT_DELETED
    text, why = load_text(path)
    if text is None:
        return [], why
    try:
        value = json.loads(text)
    except ValueError:
        value = None
    if not _strings(value) or any(can_escape(rel) for rel in cast(list, value)):
        return [], [f"{path} is not a list of repo-relative paths"]
    return cast(list[str], value), []
