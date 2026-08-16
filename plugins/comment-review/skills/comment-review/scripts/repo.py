"""Facts about the checkout: git, the filesystem, and what they refuse to answer.

Every function here answers a question about the tree the review runs in, and
says so in its return type when the answer is unavailable -- `None` for "git
could not tell me", a named list for "these files were not read". A caller that
treats a non-answer as an empty answer produces the failure this whole skill
exists to catch, so none of them return a bare empty collection.

Imported by `census.py`, `annotate.py`, `referrers.py` and `prove_unchanged.py`.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

# ⚠ Bound to a NAME so no `except` clause here holds a tuple LITERAL. Under
# `target-version = "py314"` a formatter rewrites `except (A, B):` into PEP
# 758's unparenthesised form, a SyntaxError on every older interpreter. This
# file ships into other repositories and is formatted by THEIR config, so a
# floor in our own pyproject cannot protect it -- only writing code that has
# nothing to rewrite can. A `noqa` does not hold here.
READ_ERRORS = (OSError, UnicodeDecodeError)

# ⚠ ValueError included: `ast.parse` raises it (not SyntaxError) on a source
# string containing a NUL byte -- a file that decoded as valid UTF-8 and so
# passed `READ_ERRORS` cleanly. `code_names` walks the whole repo, so one such
# file would crash the entire census rather than degrade one file's harvest.
PARSE_ERRORS = (OSError, UnicodeDecodeError, SyntaxError, ValueError)

# ⚠ UnicodeDecodeError included, on purpose, not an oversight: `git()` pins
# `encoding="utf-8"` with the default `errors="strict"`, so a tracked path or
# a blob that is not valid UTF-8 raises OUT OF `subprocess.run` itself, before
# any caller sees a return code. Every caller of `git()` already treats
# `GIT_ERRORS` as "git could not produce this" and degrades accordingly
# (`None`, or `(None, reason)` where a reason is threaded through) -- a decode
# failure is the same kind of non-answer and is declared here rather than left
# to crash `git_ls_files` / `_grep` / `_show` on the first non-UTF-8 path.
GIT_ERRORS = (OSError, subprocess.SubprocessError, UnicodeDecodeError)

# A virtualenv in the tree POISONS the name corpus: every installed package's
# methods become "known", so a real obituary is suppressed because some library
# happens to define that name. It also makes the count depend on what is
# installed, so the same file censuses differently on two machines.
EXCLUDED_DIRS = frozenset(
    {"__pycache__", ".venv", "venv", "site-packages", "node_modules", ".git"}
)


def git(repo: Path, *args: str, timeout: int = 30) -> subprocess.CompletedProcess:
    r"""Every git invocation this plugin makes. ONE place, on purpose.

    ⚠ `core.quotePath` DEFAULTS TO TRUE, so git renders a non-ASCII path as
    octal escapes -- `"caf\303\251.py"`, quotes included. Measured: a tracked
    `café.py` defining `helper_name` dropped out of the live-name corpus with
    NOTHING appended to `unread`, so every symbol defined only there became a
    false obituary and the coverage hole was silent. The same escaping makes
    `path_index` report a comment citing that file as UNRESOLVED -- a false
    finding handed to four reviewers as settled fact.

    ⚠ The encoding is PINNED for the same reason: git writes UTF-8, and
    `text=True` alone decodes with the machine's locale, so a non-ASCII path
    arrives corrupted on this repo's own cp1252 machine.

    Both are one-line fixes, and both were applied to some call sites and not
    others -- three scripts each received the encoding fix independently and
    none received the quoting fix. Routing every call through here is what
    makes the NEXT git-decoding hazard a one-place fix.

    Exceptions are NOT caught here: `GIT_ERRORS` and a nonzero return code mean
    different things at each call site (None as a third state, a real
    zero-match search), and collapsing them here would erase that.

    Args:
        repo: the repository root, passed as `-C`.
        *args: the git subcommand and its arguments.
        timeout: seconds before `subprocess.TimeoutExpired`.

    Returns:
        The completed process, with `check=False` -- the caller reads
        `returncode` itself.
    """
    return subprocess.run(
        ["git", "-c", "core.quotePath=false", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=timeout,
        check=False,
    )


def git_ls_files(repo: Path) -> list[str] | None:
    """Tracked, repo-relative posix paths — or None when git cannot answer.

    None is a THIRD state, not an empty list: "this is not a git checkout" and
    "this checkout tracks nothing" lead to different fallbacks, and collapsing
    them lets a working tree with no index silently produce an empty corpus.

    Args:
        repo: the repository root.

    Returns:
        The tracked paths, or None if this is not a git repo or git is absent.
    """
    if not repo.is_dir():
        return None
    try:
        listed = git(repo, "ls-files")
    except GIT_ERRORS:
        return None
    if listed.returncode != 0:
        return None
    return listed.stdout.splitlines()


def tracked_paths(repo: Path) -> set[Path] | None:
    """`git_ls_files` as resolved absolute paths, for membership tests."""
    rels = git_ls_files(repo)
    if rels is None:
        return None
    return {(repo / rel).resolve() for rel in rels}


def path_index(repo: Path) -> set[str]:
    """Every tracked path, plus every suffix of it, for citation resolution.

    Prose cites package-relative (`summary.py`, `billing/rates.py`) far more
    often than repo-relative, and a run's working directory is not guaranteed
    to be the repo root.
    Resolving only against the repo root was measured at 80/84, 18/20 and 2/2
    FALSE dangling reports on one repository — an annotation handed to four
    reviewers as settled fact.

    A suffix set answers "is this citation ANY file in the tree" in one lookup,
    which is the question prose is actually asking. Walking the tree once and
    indexing beats trying N candidate roots per citation.

    ⚠ TRACKED files only, via `git ls-files`. That is faster than walking a tree
    full of generated data, and it is also more correct: a citation into
    gitignored runtime state is UNVERIFIABLE (absent from every fresh checkout),
    which is a different finding from a citation that resolves nowhere. Measured
    on one repo, 6 of 20 "dangling" reports were gitignored state.
    """
    out: set[str] = set()
    if not repo.is_dir():
        return out
    rels = git_ls_files(repo)
    # ⚠ Written out rather than collapsed to `if not rels`. The two states DO
    # take the same fallback here -- an index that tracks nothing indexes the
    # same set as no index at all -- but `git_ls_files` documents None as a
    # THIRD state, and a reader who sees them collapsed learns the opposite of
    # what that docstring says.
    if rels is None or not rels:  # not a git repo, git unavailable, or empty
        rels = [
            p.relative_to(repo).as_posix()
            for p in repo.rglob("*")
            if p.is_file() and not EXCLUDED_DIRS.intersection(p.parts)
        ]
    for rel in rels:
        parts = rel.split("/")
        for i in range(len(parts)):
            out.add("/".join(parts[i:]))
    return out
