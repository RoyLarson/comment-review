"""Stage 3, inbound: which tracked files NAME the files under review.

    python -m comment_review referrers --repo D [--out PATH] <targets...>

The census resolves what a comment CITES. This resolves the other direction --
who cites the code being edited -- and it is the half that decides the
REFERENCE ONLY list. Without it that list is assembled from memory, and a
`target` run has no diff to widen from at all.

Read-only, always exits 0: an INPUT to a review. Every line it prints is a
CANDIDATE -- a file that names a token is a file to READ, and stays outside what
a verdict may target.
"""

import ast
from pathlib import Path

# ! The exception tuples are IMPORTED. Each is bound to a NAME so no `except`
# clause here holds a tuple literal; `exceptions.py` carries that reason once.
from ..machine import exceptions
from ..machine.repo import (
    git,
)

NAMED_DEFS = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)


def tokens_for(path: Path, text: str) -> set[str]:
    """Every name by which prose elsewhere would refer to this file.

    Args:
        path: the file's repo-relative path.
        text: its contents, parsed for top-level names when it is Python.

    Returns:
        The stem, the posix path and each of its trailing suffixes, and the
        PUBLIC top-level definitions. Underscored names are excluded: prose
        cites the public surface, and a private helper's name collides with
        every unrelated private helper spelled the same way.
    """
    out = {path.stem}
    parts = path.as_posix().split("/")
    for i in range(len(parts)):
        out.add("/".join(parts[i:]))
    if path.suffix.lower() in (".py", ".pyi"):
        try:
            tree = ast.parse(text)
        except exceptions.PARSE_ERRORS:
            # !! A file that will not parse yields its PATH and STEM only, and
            # must still reach the length filter below -- an earlier `return`
            # here skipped it, so a two-character stem went to `git grep -l -F`
            # and matched nearly every tracked file. ! `tree = None`, not a bare
            # `pass`: this is not a loop, and falling through left `tree`
            # unbound, so the handler written for a mid-edit file crashed on
            # one. Both shapes measured 2026-08-17.
            tree = None
        for node in tree.body if tree is not None else ():
            if isinstance(node, NAMED_DEFS) and not node.name.startswith("_"):
                out.add(node.name)
    return {t for t in out if len(t) > 2}


def _grep(repo: Path, token: str) -> tuple[list[str] | None, str]:
    """Tracked files containing `token` as a fixed string.

    ! `git grep` exits 1 for a genuine ZERO-MATCH search; any other nonzero (a
    bad pathspec, a corrupt index, a timeout) means the search never completed.
    Collapsing both into `[]` reads a failed search as "nothing found", so None
    is a THIRD state here, the same as in `git_ls_files`.

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
