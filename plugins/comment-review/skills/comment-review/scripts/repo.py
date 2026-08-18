"""Facts about the checkout: git, the filesystem, and the exception tuples.

Every function here answers a question about the tree the review runs in, and
carries the NON-ANSWER in its return type -- `None` for "git could not tell me",
a named list for "these files were unread". A caller that reads a non-answer as
an empty answer produces the failure this whole skill exists to catch.

Imported by `census.py`, `annotate.py`, `referrers.py` and `prove_unchanged.py`.
"""

import subprocess
import tokenize
from pathlib import Path

# ! Bound to a NAME so no `except` clause here holds a tuple LITERAL. Under
# `target-version = "py314"` a formatter rewrites `except (A, B):` into PEP
# 758's unparenthesised form, a SyntaxError on every older interpreter. This
# file ships into other repositories and is formatted by THEIR config, so the
# floor in our own pyproject reaches it nowhere: code with nothing to rewrite
# is the whole defence. A `noqa` silences the report, and the rewrite stands.
READ_ERRORS = (OSError, UnicodeDecodeError)

# ! ValueError included: `ast.parse` raises it (not SyntaxError) on a source
# string containing a NUL byte -- a file that decoded as valid UTF-8 and so
# passed `READ_ERRORS` cleanly. `code_names` walks the whole repo, so one such
# file would crash the entire census rather than degrade one file's harvest.
# !! `tokenize.TokenError` is included and is NOT a SyntaxError -- it derives
# straight from Exception. `blocks_stdlib` calls `tokenize.generate_tokens`,
# which raises it on an unterminated triple-quote or bracket, so one such file
# anywhere in a corpus aborted a whole run with a traceback. Every caller here
# already treats a parse failure as ONE file degrading, never as the run ending.
PARSE_ERRORS = (
    OSError,
    UnicodeDecodeError,
    SyntaxError,
    ValueError,
    tokenize.TokenError,
)

# ! UnicodeDecodeError included, deliberately: `git()` pins `encoding="utf-8"`
# with the default `errors="strict"`, so a tracked path or a blob outside UTF-8
# raises OUT OF `subprocess.run` itself, before any caller sees a return code.
# Every caller of `git()` already reads `GIT_ERRORS` as "git could not produce
# this" and degrades accordingly (`None`, or `(None, reason)` where a reason is
# threaded through). A decode failure is the same kind of non-answer, so it is
# declared here rather than crashing `git_ls_files` / `_grep` / `_show` on the
# first non-UTF-8 path.
GIT_ERRORS = (OSError, subprocess.SubprocessError, UnicodeDecodeError)

# A virtualenv in the tree POISONS the name corpus: every installed package's
# methods become "known", so a real obituary is HIDDEN because some library
# happens to define that name. It also makes the count depend on what is
# installed, so the same file censuses differently on two machines.
EXCLUDED_DIRS = frozenset(
    {"__pycache__", ".venv", "venv", "site-packages", "node_modules", ".git"}
)


def read_raw(path: Path) -> str:
    r"""The file's own line endings, untranslated.

    `Path.read_text` (and a plain `open` with no `newline=`) applies
    universal-newline translation, collapsing every `\r\n` to `\n` before the
    caller ever sees it -- so a CRLF file and an LF file become
    indistinguishable to anything that then asks which ending the text uses.
    `newline=""` disables that translation.

    !! TWO CALLERS NEED IT AND BOTH ARE ABOUT COMPARING A FILE TO ITSELF.
    `prove_unchanged` asks whether the code is byte-identical; `galley` writes a
    copy meant to be diffed against its original. Measured 2026-08-17: the
    galley read with `read_text` instead, so a 245-line CRLF source was written
    out with 223 bare LF and every line of the diff was an ending change.

    ! `Path.read_text`'s own `newline=` parameter arrived in Python 3.13, and
    the floor here is 3.11, where passing it raises `TypeError`.
    `check_shipped_syntax.py` reads syntax and two runtime shapes, so a keyword
    argument that exists only on a newer interpreter gets past it.
    `open(...).read()` works at the floor and does the same thing.

    Args:
        path: the file to read.

    Returns:
        Its text, with every line ending exactly as it sits on disk.
    """
    with open(path, encoding="utf-8", newline="") as f:
        return f.read()


def git(repo: Path, *args: str, timeout: int = 30) -> subprocess.CompletedProcess:
    r"""Every git invocation this plugin makes. ONE place, on purpose.

    ! `core.quotePath` DEFAULTS TO TRUE, so git renders a non-ASCII path as
    octal escapes -- `"caf\303\251.py"`, quotes included. Measured: a tracked
    path holding one non-ASCII letter, defining `helper_name`, dropped out of
    the live-name corpus and
    `unread` stayed empty, so every symbol defined only there became a false
    obituary behind a silent coverage hole. The same escaping makes
    `path_index` report a comment citing that file as UNRESOLVED -- a false
    finding handed to four reviewers as settled fact.

    ! The encoding is PINNED for the same reason: git writes UTF-8, and
    `text=True` alone decodes with the machine's locale, so a non-ASCII path
    arrives corrupted on this repo's own cp1252 machine.

    Both are one-line fixes, and both were applied per call site -- three
    scripts each received the encoding fix independently, and the quoting fix
    reached none of them. Routing every call through here makes the NEXT
    git-decoding hazard a one-place fix.

    Exceptions are RAISED to the caller: `GIT_ERRORS` and a nonzero return code
    mean different things at each call site (None as a third state, a real
    zero-match search), and catching them here would erase that.

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
    """Tracked, repo-relative posix paths -- or None when git cannot answer.

    None is a THIRD state: "this is not a git checkout" and "this checkout
    tracks nothing" lead to different fallbacks, and collapsing them lets a
    working tree with no index produce an empty corpus in silence.

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
    often than repo-relative, and a run's working directory may sit anywhere
    under the root. Resolving against the repo root alone produced FALSE
    dangling reports on nearly every citation of one repository -- an
    annotation handed to four reviewers as settled fact.

    A suffix set answers "is this citation ANY file in the tree" in one lookup,
    which is the question prose is actually asking. Walking the tree once and
    indexing beats trying N candidate roots per citation.

    ! TRACKED files only, via `git ls-files`. That is faster than walking a tree
    full of generated data, and more correct: a citation into gitignored runtime
    state is UNVERIFIABLE (absent from every fresh checkout), which is a
    different finding from a citation that resolves nowhere.
    """
    out: set[str] = set()
    if not repo.is_dir():
        return out
    rels = git_ls_files(repo)
    # ! Written out rather than collapsed to `if not rels`. The two states DO
    # take the same fallback here -- an index that tracks nothing indexes the
    # same set as no index at all -- and `git_ls_files` documents None as a
    # THIRD state, so a reader who saw them collapsed would learn the opposite
    # of what that docstring says.
    if rels is None or not rels:  # not a git repo, git unavailable, or empty
        rels = [
            p.relative_to(repo).as_posix()
            for p in repo.rglob("*")
            # ! RELATIVE to the repo, not absolute: an ancestor named `venv`
            # excluded the whole checkout. See `census._walk`.
            if p.is_file() and not EXCLUDED_DIRS.intersection(p.relative_to(repo).parts)
        ]
    for rel in rels:
        parts = rel.split("/")
        for i in range(len(parts)):
            out.add("/".join(parts[i:]))
    return out
