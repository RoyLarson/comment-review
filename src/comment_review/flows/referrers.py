"""Stage 3, inbound: the git search behind `referrers`."""

from pathlib import Path

# ! The exception tuple is IMPORTED and bound to a name, so no `except` clause
# here holds a tuple literal; `exceptions.py` carries that reason once.
from comment_review import exceptions
from comment_review.machine.repo import git


def files_naming(repo: Path, token: str) -> tuple[list[str] | None, str]:
    """Tracked files containing `token` as a fixed string.

    ! `git grep` exits 1 for a genuine zero-match search; any other nonzero (a
    bad pathspec, a corrupt index, a timeout) means the search never completed.
    Collapsing both into `[]` reads a failed search as "nothing found", so None
    is a third state here, the same as in `git_ls_files`.

    Returns:
        `(files, "")` on a completed search -- `files` is `[]` for a real
        zero-match result. `(None, reason)` when the search itself failed,
        naming why.
    """
    try:
        got = git(repo, "grep", "-l", "-F", "--", token, timeout=60)
    except exceptions.GIT_ERRORS as e:
        return None, type(e).__name__
    if got.returncode == 0:
        return got.stdout.splitlines(), ""
    if got.returncode == 1:
        return [], ""
    return None, f"git grep exit {got.returncode}"
