"""Stage 3, inbound: the git search behind `referrers`."""

from pathlib import Path

from comment_review import exceptions
from comment_review.machine.repo import git, nul_separated


def _patterns(token: str) -> list[str]:
    """The `git grep` arguments that find `token` where prose cites it.

    A token that is a bare name -- a stem or a definition -- matches only as a
    citation: `` `run` ``, `run(` or `module.run`. The word in a sentence is not
    a reference. Any other token holds a `/` or a suffix, so it is specific
    already and matches as a fixed string.
    """
    if not token.isidentifier():
        return ["-F", "-e", token]
    word = "[^A-Za-z0-9_]"
    return [
        "-E",
        "-e",
        f"`{token}`",
        "-e",
        f"(^|{word}){token}\\(",
        "-e",
        f"\\.{token}({word}|$)",
    ]


def files_naming(repo: Path, token: str) -> tuple[list[str] | None, str]:
    """Tracked files citing `token`, as `_patterns` matches it.

    ! `git grep` exits 1 for a genuine zero-match search; any other nonzero (a
    bad pathspec, a corrupt index), or a timeout, means the search never completed.
    Collapsing both into `[]` reads a failed search as "nothing found", so None
    is a third state here, the same as in `git_ls_files`.

    Returns:
        `(files, "")` on a completed search -- `files` is `[]` for a real
        zero-match result. `(None, reason)` when the search itself failed,
        naming why.
    """
    try:
        got = git(repo, "grep", "-l", "-z", *_patterns(token), "--", timeout=60)
    except exceptions.GIT_ERRORS as e:
        return None, type(e).__name__
    if got.returncode == 0:
        return nul_separated(got.stdout), ""
    if got.returncode == 1:
        return [], ""
    return None, f"git grep exit {got.returncode}"
