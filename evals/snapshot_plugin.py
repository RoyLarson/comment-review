"""B1 -- ISOLATE: take the plugin at a ref, so a run scores the tree it names.

A directory marketplace POINTS rather than copies, so an installed plugin is
whatever the working tree holds at run time -- measured 2026-08-22, when a run
believed pinned to `v0.2.3` traced back to the commit just finished. The harness
never installs: it extracts a ref into a directory and hands a subagent that
path.

! THE WHOLE PLUGIN TRAVELS, not `skills/comment-review/` alone. Arm A of
`isolate-the-codes-contribution` is "v0.2.3 code with v0.2.3 agents exactly as
tagged", so `agents/` and `scripts/` have to be captured at ONE ref or the two
things that split exists to separate are mixed at the point of capture.

!! IT WRITES CHECKOUT FORM, WHICH IS WHAT A PLUGIN IS. `git archive` applies the
same eol filter a checkout does -- MEASURED 2026-08-29 on this repo, where it
returned CRLF under `core.autocrlf=true` for a blob stored with LF. That is the
right form here: this tree is the plugin a run EXECUTES, and an installed plugin
is checkout form.

! IT IS THE OPPOSITE CHOICE FROM `stage_case.py`, DELIBERATELY. What B2 stages is
the tree UNDER REVIEW, graded byte-for-byte against `git show`, so it reads the
stored blob instead. Two artifacts, two questions -- what the skill runs, and what
the skill reads.

!! THIS PARAGRAPH SAID THE REVERSE WHEN B1 LANDED, and the claim went in
uncontradicted because `verify` re-digests the files it just wrote: the snapshot
is compared against ITSELF, so no eol form could ever fail it. `docs/gates.md`
names that exactly -- a gate green because it shares the defect. It was B2's
first byte-identity test, which compares against a SECOND command, that
disagreed.
"""

from __future__ import annotations

import hashlib
import io
import json
import pathlib
import subprocess
import tarfile
from dataclasses import dataclass

PLUGIN_PATH = "plugins/comment-review"


@dataclass(frozen=True)
class Manifest:
    """What a run records so a reader can say which tree was scored.

    `files` maps each path AS GIT NAMES IT to the sha256 of the bytes written,
    which is what makes a later disagreement nameable rather than merely
    detectable -- `verify` returns the paths, not a boolean.
    """

    ref: str
    commit: str
    root: pathlib.Path
    files: dict[str, str]


def _digest(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve(repo: pathlib.Path, ref: str) -> str:
    """Return the COMMIT `ref` names, peeling an annotated tag.

    `git rev-parse v0.2.3` returns the tag object; every tag in this repo is
    annotated, so a provenance record taken without `^{commit}` names something
    that cannot be diffed.
    """
    out = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", f"{ref}^{{commit}}"],
        capture_output=True,
        text=True,
        check=True,
    )
    return out.stdout.strip()


def snapshot(repo: pathlib.Path, ref: str, dest: pathlib.Path) -> Manifest:
    """Extract the plugin at `ref` into `dest`, and record what was taken."""
    commit = resolve(repo, ref)
    archive = subprocess.run(
        ["git", "-C", str(repo), "archive", "--format=tar", commit, "--", PLUGIN_PATH],
        capture_output=True,
        check=True,
    )
    dest.mkdir(parents=True, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(archive.stdout)) as tar:
        tar.extractall(dest, filter="data")
        written = [m.name for m in tar.getmembers() if m.isfile()]
    files = {name: _digest(dest / name) for name in written}
    return Manifest(ref=ref, commit=commit, root=dest, files=files)


def write_manifest(manifest: Manifest, path: pathlib.Path) -> pathlib.Path:
    """Write the provenance beside the run, and return where it went.

    ! THE ROOT IS STORED ABSOLUTE. A later reader opens this file from somewhere
    else entirely, so a path relative to the writer's cwd would resolve against
    the wrong tree -- and `verify` would then report every file missing, which
    reads as a tampered snapshot rather than as a bad path.
    """
    path.write_text(
        json.dumps(
            {
                "ref": manifest.ref,
                "commit": manifest.commit,
                "root": str(manifest.root.resolve()),
                "files": manifest.files,
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    return path


def read_manifest(path: pathlib.Path) -> Manifest:
    """Rebuild a manifest a previous run wrote."""
    held = json.loads(path.read_text(encoding="utf-8"))
    return Manifest(
        ref=held["ref"],
        commit=held["commit"],
        root=pathlib.Path(held["root"]),
        files=held["files"],
    )


def verify(manifest: Manifest) -> list[str]:
    """Return the snapshot's paths that no longer match what was taken.

    ! IT TAKES BOTH WALKS, AND NEITHER ONE ALONE ANSWERS THE QUESTION. Walking
    the MANIFEST catches a file changed or gone; only walking the DIRECTORY
    catches one that was added, where every recorded path still matches. The
    question is "is this the tree I took", not "is what I took still here".
    """
    moved = []
    for name, digest in manifest.files.items():
        path = manifest.root / name
        if not path.is_file() or _digest(path) != digest:
            moved.append(name)

    for path in manifest.root.rglob("*"):
        name = path.relative_to(manifest.root).as_posix()
        if path.is_file() and name not in manifest.files:
            moved.append(name)

    return sorted(moved)
