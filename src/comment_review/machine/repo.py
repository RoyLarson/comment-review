"""Facts about the checkout: git, the filesystem, exception tuples, and text identity.

Every function here answers a question about the tree the review runs in, and
carries the NON-ANSWER in its return type -- `None` for "git could not tell me",
a named list for "these files were unread". A caller that reads a non-answer as
an empty answer produces the failure this whole skill exists to catch.

`read_source` and `sha_of` answer a different question -- not what the
checkout contains, but what was actually read -- and belong here rather than
downstream because a sha taken by a caller depends on which of this module's
two readers that caller happened to use.
"""

import hashlib
import subprocess
from pathlib import Path
from typing import NamedTuple

from comment_review.machine import exceptions

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

    !! THREE SITES CALL IT DIRECTLY, AND `galley` IS NOT ONE OF THEM ANYMORE.
    MEASURED over `src/comment_review/`: `read_source` below (which every other
    reader goes through), `commands/prove_unchanged.py` and
    `results/prove_unchanged.py` -- both about comparing a file to itself
    byte-identically, which is why they read raw rather than through the sha
    pairing `read_source` gives everyone else. `commands/galley.py` imports
    `read_source` now, not this function; it reaches `read_raw` only through
    that call. Measured 2026-08-17, when this was true directly: the galley
    read with `read_text` instead, so a 245-line CRLF source was written out
    with 223 bare LF and every line of the diff was an ending change.

    ! FIVE MODULES REACH IT THROUGH `read_source`: `commands/census.py`,
    `commands/galley.py`, `flows/page_for.py`, `flows/proof_setter.py` (twice)
    and `results/compositor.py` (twice) -- MEASURED by import, 2026-08-25.

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


class Source(NamedTuple):
    """A file's text and the sha of that exact text, read together.

    !! THEY TRAVEL AS ONE BECAUSE A SHA OF THE WRONG READING IS WORSE THAN NO
    SHA. Roy, 2026-08-25: *"that is the only place to properly ensure it gets
    read exactly the same and the middle things shouldn't depend on the
    external things."*

    Attributes:
        text: as `read_raw` returns it -- the file's own line endings.
        sha: of that text, so a caller cannot pair the two wrongly.
    """

    text: str
    sha: str


def sha_of(text: str) -> str:
    """The identity of a text, truncated to 16 hex characters.

    ! WHAT IT ANSWERS is one question -- *are these the bytes that were
    reviewed?* Roy, 2026-08-21: *"if the file shifted at all it is dead and so
    are the edits."*

    Args:
        text: the text to identify.

    Returns:
        The first 16 hex characters of its UTF-8 SHA-256.
    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def read_source(path: Path) -> Source:
    r"""Read a file and identify what was read, in one act.

    !! THE READING AND THE HASHING CANNOT BE SEPARATED WITHOUT LOSING THE
    GUARANTEE. MEASURED 2026-08-25 over `b"# one\r\ndef f():\r\n    return
    1\r\n"`, with this tree's two readers:

        read_raw    newline=""            f13497990c3d92d0
        read_text   universal newlines    83ec58343641fd11

    ! ONE FILE, ONE SET OF BYTES, TWO SHAS. A sha taken downstream of whichever
    reader a consumer happened to use answers *which reader ran*, not *did the
    file change* -- so a byte-identical CRLF checkout refuses.

    ! AND THE DEFECT WAS LIVE WHEN THIS LANDED: `census.py` read through
    `Path.read_text` and the binder hashed that, so the recorded sha described
    the TRANSLATED text and not the file.

    Args:
        path: the file to read.

    Returns:
        Its text with line endings untouched, and the sha of that text.
    """
    text = read_raw(path)
    return Source(text, sha_of(text))


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

    Exceptions are RAISED to the caller -- `exceptions.GIT_ERRORS` -- and a
    nonzero return code
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
    except exceptions.GIT_ERRORS:
        return None
    if listed.returncode != 0:
        return None
    return listed.stdout.splitlines()


def undraftable(into: Path, repo: Path) -> str:
    """Why drafts of files under `repo` cannot be written into `into`, or "".

    !! `into` MUST BE DISJOINT FROM `repo`, AND NO PER-FILE GUARD CAN ASK IT.
    A per-file guard checks that a target lands inside `into`; on an OVERLAP
    that is satisfied by the SOURCE FILE ITSELF, so the guard passes and the
    draft is written over the file under review. MEASURED 2026-08-22 on
    `commands/galley.py`, which did exactly that and printed `1 page(s) set` at
    exit 0; MEASURED again 2026-08-25 on `flows.proof_setter.run(notations,
    binder, repo, repo)`, which answered `refused=[]` while the source file on
    disk held the replacement text.

    !! IT LIVES HERE BECAUSE THREE CALLERS ASK IT -- `flows/proof_setter.run`,
    `commands/proof.py` and `commands/galley.py`. It was spelled out twice, in
    the two commands, and the flow -- which the commands' own docstrings say
    anyone may call -- asked it nowhere.

    ! `is_relative_to` IS TRUE OF A PATH AND ITSELF, which is why both
    directions are tested and an equality test would be redundant.

    ! THE `is_dir` CLAUSE IS FIRST BECAUSE THE MKDIR IS WHAT FAILS.
    `into.mkdir(parents=True, exist_ok=True)` raises `FileExistsError` when
    `into` names a regular file -- `exist_ok` covers an existing DIRECTORY only
    -- and that reached `commands/proof.py`'s console as a traceback while
    every other bad input there printed a reason.

    Args:
        into: the directory drafts are written to. RESOLVED by the caller;
            an unresolved path is never a prefix of a resolved one.
        repo: the checkout the pages are read from, resolved the same way.

    Returns:
        The reason, or "" when `into` may receive drafts.
    """
    if into.exists() and not into.is_dir():
        return f"{into} is not a directory, so no draft can be written into it"
    if into.is_relative_to(repo) or repo.is_relative_to(into):
        return (
            f"{into} overlaps {repo}, so a draft would be written over the files"
            " under review"
        )
    return ""


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
            # excluded the whole checkout. See `walk_files` below.
            if p.is_file() and not EXCLUDED_DIRS.intersection(p.relative_to(repo).parts)
        ]
    for rel in rels:
        parts = rel.split("/")
        for i in range(len(parts)):
            out.add("/".join(parts[i:]))
    return out


def walk_files(root: Path):
    """Every file under `root`. It ENUMERATES; it classifies nothing.

    !! IT FILTERED ON `BY_EXT` AND THAT WAS A SECOND POLICY. `main` already asks
    `language_for(path) is None` and REFUSES at exit 1 -- the caller asked for
    that file -- so the same question was answered in two places with two
    different consequences, and the silent one won for a directory. MEASURED
    2026-08-22 on a two-file directory: an unsupported file NAMED exits 1, the
    same file WALKED vanished at exit 0. `every file handed in is censused or
    this errors` was true of explicit paths and false of directories.

    ! SO THE WALK STOPPED DECIDING. Whether a file with no language record is a
    refusal or a note is the CENSUS's call, and it turns on something only the
    census knows: whether the path was NAMED or merely FOUND. A directory holds
    READMEs, images and lockfiles; refusing on those makes the form unusable,
    and skipping them in silence is the false completeness this warns about.

    ! `EXCLUDED_DIRS` IS THIS MODULE'S, which is why the walk sits here rather
    than in the census that used to hold it. It is not the same question. It is about
    where the walk may GO -- a vendored tree is not this repo's code at all --
    rather than about what a file is once found.
    """
    if root.is_file():
        yield root
        return
    for p in sorted(root.rglob("*")):
        if p.is_file():
            # !! RELATIVE to the root being walked. Matched against `p.parts`
            # this tested every ANCESTOR too, so a checkout living anywhere
            # under a directory called `venv`, `.venv`, `node_modules`,
            # `site-packages`, `__pycache__` or `.git` excluded ITSELF.
            # Measured 2026-08-17: `code_names` harvested 0 names from a repo
            # under `.../venv/myproject`, and nothing joined `unread`, so the
            # NOT CHECKED list stayed empty and the run read as complete --
            # every `names-a-symbol` a false obituary, handed to four reviewers
            # as settled fact.
            if not EXCLUDED_DIRS.intersection(p.relative_to(root).parts):
                yield p
