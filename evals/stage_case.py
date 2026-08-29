r"""B2 -- STAGE: put a case's paths, at its START hash, into the tree to be graded.

A case pins a START and an END (`decision-log.md Vocabulary: #29`). What a role
reads is START, and it must read the case rather than the repository: everything
the case did not name stays behind, or a role can resolve a reference the case
never handed it and the grade stops being about the case.

!! IT WRITES THE STORED BLOB, AND `git archive` DOES NOT. MEASURED 2026-08-29 on
this repo: `git archive` applies the checkout filter, so with `core.autocrlf=true`
it returned CRLF where `git show` returned LF -- the first byte-identity test
failed at index 3, `b'\r' != b'\n'`. B2 is graded against `git show`, so the
staging has to read the object store itself.

! AND THE STAGED TREE IS THEN THE SAME BYTES ON EVERY MACHINE, which a checkout
filter cannot promise: two runs of one case on two platforms would otherwise
stage different files and be graded as though they had not.

! THE READ AND THE CHECK USE DIFFERENT COMMANDS ON PURPOSE -- `git cat-file blob`
here, `git show` in the test. A check that issued the same command as the code it
checks could only agree with itself, which is `docs/gates.md`'s whole subject.
"""

from __future__ import annotations

import pathlib
import subprocess


class PathNotAtCommit(Exception):
    """A case named a path that does not exist at the commit being staged."""


def _exists_at(repo: pathlib.Path, commit: str, path: str) -> bool:
    return (
        subprocess.run(
            ["git", "-C", str(repo), "cat-file", "-e", f"{commit}:{path}"],
            capture_output=True,
        ).returncode
        == 0
    )


def stage(
    repo: pathlib.Path, commit: str, paths: list[str], dest: pathlib.Path
) -> list[str]:
    """Write `paths` as they stood at `commit` into `dest`, and nothing else.

    ! EVERY PATH IS CHECKED BEFORE ANY IS WRITTEN, so a case that names one bad
    path leaves no half-staged tree behind -- and the refusal names all of them
    at once rather than one per re-run.

    ! THE REFUSAL NAMES THE COMMIT. The likely mistake is a case written today
    against an older START, where the path exists on disk and on HEAD and simply
    was not there yet; "no such file" would send a reader to the wrong question.
    """
    absent = [path for path in paths if not _exists_at(repo, commit, path)]
    if absent:
        raise PathNotAtCommit(
            f"not in {commit[:7]}: {', '.join(sorted(absent))}"
        )

    for path in paths:
        blob = subprocess.run(
            ["git", "-C", str(repo), "cat-file", "blob", f"{commit}:{path}"],
            capture_output=True,
            check=True,
        )
        written = dest / path
        written.parent.mkdir(parents=True, exist_ok=True)
        written.write_bytes(blob.stdout)

    return sorted(paths)
