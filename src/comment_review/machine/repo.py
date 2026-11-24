"""The checkout's I/O: git, reading, writing and removing files, and text identity.

Where git cannot answer, the return type says so: `git_ls_files` and
`tracked_paths` return `None` for "git could not tell me". A caller that reads a
non-answer as an empty answer produces the failure this whole skill exists to
catch.

`read_source` and `sha_of` answer what was actually read, not what the checkout
contains, and belong here rather than downstream because a sha taken by a caller
depends on which of this module's two readers that caller happened to use.

!! And `write_raw` is `read_raw`'s pair, here for the same reason. A changed
code file is written through this module. The two halves of the byte-identity
this system rests on -- the untranslated read and the untranslated write -- are
one rule, and a rule stated in two areas is a rule that will disagree with
itself.
"""

import hashlib
import shutil
import stat
import subprocess
from pathlib import Path
from typing import NamedTuple

from comment_review import exceptions

# A virtualenv in the tree poisons the name corpus: every installed package's
# methods become "known", so a real obituary is hidden because some library
# happens to define that name. It also makes the count depend on what is
# installed, so the same file gathers differently on two machines.
EXCLUDED_DIRS = frozenset(
    {"__pycache__", ".venv", "venv", "site-packages", "node_modules", ".git"}
)


def read_raw(path: Path) -> str:
    """Read strict UTF-8 text, preserving BOM, Unicode and line endings.

    Args:
        path: the file to read.

    Returns:
        Its text, with every line ending exactly as it sits on disk.
    """
    return read_source(path).text


def write_raw(path: Path, text: str) -> Path:
    r"""Write text with its own line endings, untranslated. The pair to `read_raw`.

    Strict UTF-8 encoding completes before creating parents or opening the
    target, so an encoding failure leaves the filesystem untouched. Writing
    the encoded bytes avoids newline translation and preserves the exact
    source bytes, including CRLF, bare CR, and bare LF endings.

    ! The mkdir is part of the write, not the caller's. A draft lands under a
    tree built from the repo's own paths, so the parent may not exist yet; a
    caller that had to remember the mkdir is a caller that will forget it. !
    `flows.proof_setter._one` records which parents it created before calling,
    so a refused draft can remove them -- that bookkeeping stays with the flow,
    because only the flow knows what a failed page should leave behind.

    Args:
        path: the file to write. Its parents are created if they do not exist.
        text: written exactly as given.

    Returns:
        `path`, so a caller can chain.
    """
    raw = text.encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    return path


class Source(NamedTuple):
    """A file's text and the sha of that exact text, read together.

    !! They travel as one because a sha of the wrong reading is worse than no
    sha. Reading and identifying in one place is what ensures a file is read
    exactly the same way each time, and keeps the middle from depending on how
    a caller read it.

    Attributes:
        text: as `read_raw` returns it -- the file's own line endings.
        sha: of that text, so a caller cannot pair the two wrongly.
    """

    text: str
    sha: str


def sha_of(text: str) -> str:
    """The identity of a text, truncated to 16 hex characters.

    ! What it answers is one question -- *are these the bytes that were
    reviewed?* If the file shifted at all, it and its edits are void.

    Args:
        text: the text to identify.

    Returns:
        The first 16 hex characters of its UTF-8 SHA-256.
    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def source_from_bytes(raw: bytes) -> Source:
    """Decode strict UTF-8 without translation and identify that exact text."""
    text = raw.decode("utf-8")
    return Source(text, sha_of(text))


def read_source(path: Path) -> Source:
    """Read filesystem bytes once, decode strict UTF-8 and identify the text.

    Args:
        path: the file to read.

    Returns:
        Its text with line endings untouched, and the sha of that text.
    """
    return source_from_bytes(path.read_bytes())


def read_revision_source(repo: Path, ref: str, rel: str) -> Source:
    """Read a revision blob as strict UTF-8, preserving its exact contents.

    Args:
        repo: repository directory; relative paths start here.
        ref: Git revision to read.
        rel: path relative to the repository directory.

    Returns:
        The blob's text and identity, including for an empty blob.

    Raises:
        subprocess.CalledProcessError: Git cannot resolve the revision or path.
        UnicodeDecodeError: the blob is not valid UTF-8.
    """
    got = subprocess.run(
        [
            "git",
            "-c",
            "core.quotePath=false",
            "-C",
            str(repo),
            "show",
            f"{ref}:./{rel}",
        ],
        capture_output=True,
        timeout=30,
        check=True,
    )
    return source_from_bytes(got.stdout)


def git(repo: Path, *args: str, timeout: int = 30) -> subprocess.CompletedProcess:
    r"""Every text-mode git invocation this plugin makes.

    This module is the only one that runs git. The one other invocation is
    `read_revision_source`, which reads a blob as bytes and so cannot decode
    here; it passes the same `core.quotePath=false`.

    ! `core.quotePath` defaults to true, so git renders a non-ASCII path as
    octal escapes -- `"caf\303\251.py"`, quotes included. Measured: a tracked
    path holding one non-ASCII letter, defining `helper_name`, dropped out of
    the live-name corpus and
    `unread` stayed empty, so every symbol defined only there became a false
    obituary behind a silent coverage hole.

    ! The encoding is pinned for the same reason: git writes UTF-8, and
    `text=True` alone decodes with the machine's locale, so a non-ASCII path
    arrives corrupted on a cp1252 machine.

    Routing every text-mode call through here makes the next git-decoding
    hazard a one-place fix.

    Exceptions -- `exceptions.GIT_ERRORS` -- and a nonzero return code mean
    different things at each call site (None as a third state, a real
    zero-match search), so both go to the caller; catching them here would
    erase that.

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

    None is a third state: "this is not a git checkout" and "this checkout
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
        listed = git(repo, "ls-files", "-z")
    except exceptions.GIT_ERRORS:
        return None
    if listed.returncode != 0:
        return None
    return nul_separated(listed.stdout)


def git_untracked(repo: Path) -> list[str] | None:
    """Untracked, unignored, repo-relative posix paths, or None as `git_ls_files`."""
    if not repo.is_dir():
        return None
    try:
        listed = git(repo, "ls-files", "-z", "--others", "--exclude-standard")
    except exceptions.GIT_ERRORS:
        return None
    if listed.returncode != 0:
        return None
    return nul_separated(listed.stdout)


def nul_separated(out: str) -> list[str]:
    """The paths a git command run with `-z` printed, verbatim.

    Without `-z`, git quotes a path holding a tab, a newline, a quote or a
    backslash, and a newline in a name splits it in two.
    """
    return [p for p in out.split("\0") if p]


def commit_of(repo: Path, ref: str) -> str | None:
    """The full sha of the commit `ref` names in `repo`, or None when none does."""
    # A ref starting with "-" would be read as an option, not a name.
    if not repo.is_dir() or not ref or ref.startswith("-"):
        return None
    try:
        got = git(repo, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}")
    except exceptions.GIT_ERRORS:
        return None
    sha = got.stdout.strip()
    return sha if got.returncode == 0 and sha else None


def git_worktree_add(repo: Path, path: Path, ref: str) -> str:
    """Check `ref` out, detached, as a worktree of `repo` at `path`; why not, or ""."""
    try:
        got = git(repo, "worktree", "add", "--detach", str(path), ref, timeout=120)
    except exceptions.GIT_ERRORS as err:
        return f"git could not add a worktree at {path}: {err}"
    if got.returncode != 0:
        return f"git could not add a worktree at {path}: {got.stderr.strip()}"
    return ""


def git_worktree_remove(repo: Path, path: Path) -> None:
    """Remove the worktree of `repo` at `path`, whatever it holds; never raises."""
    try:
        git(repo, "worktree", "remove", "--force", str(path), timeout=120)
    except exceptions.GIT_ERRORS:
        pass
    if path.exists():
        remove_tree(path, ignore_errors=True)


def undraftable(into: Path, repo: Path) -> str:
    """Why drafts of files under `repo` cannot be written into `into`, or "".

    !! `into` must be disjoint from `repo`, and no per-file guard can ask it.
    A per-file guard checks that a target lands inside `into`; on an overlap
    that is satisfied by the source file itself, so the guard passes and the
    draft is written over the file under review. Measured on
    `flows.proof_setter.run(docket, repo, repo)` with this check removed: it
    answered `refused=[]` while the source file on disk held the replacement
    text.

    !! It lives here because more than one caller asks it --
    `flows/proof_setter.run` and `commands/proof.py`.

    ! `is_relative_to` is true of a path and itself, which is why both
    directions are tested and an equality test would be redundant.

    ! The `is_dir` clause is first because the mkdir is what fails.
    `into.mkdir(parents=True, exist_ok=True)` raises `FileExistsError` when
    `into` names a regular file -- `exist_ok` covers an existing directory only
    -- and without this clause that reaches `commands/proof.py`'s console as a
    traceback while every other bad input there prints a reason.

    !! `is_symlink` is asked beside `exists` because `exists` follows the link
    and a dangling one answers `False`. `exists` alone would let a link naming
    nothing through the clause that exists to stop a non-directory -- and
    `mkdir` does not follow a link, so it is the same `FileExistsError` the
    clause is for. `is_symlink` asks about the link itself; a symlink to a real
    directory still passes, because `is_dir` follows it and answers `True`.

    ! What the callers pass is already resolved, so the clause bites for a
    caller that does not resolve -- which this function's own `Args` says is
    the caller's job and cannot check. It is not verified on Windows without
    symlink privilege: creating a symlink there raises `WinError 1314`, and
    `test_a_DANGLING_SYMLINK_is_not_a_directory` skips rather than fake a
    filesystem the case is about.

    Args:
        into: the directory drafts are written to. Resolved by the caller;
            an unresolved path is never a prefix of a resolved one.
        repo: the checkout the pages are read from, resolved the same way.

    Returns:
        The reason, or "" when `into` may receive drafts.
    """
    if (into.is_symlink() or into.exists()) and not into.is_dir():
        return f"{into} is not a directory, so no draft can be written into it"
    if into.is_relative_to(repo) or repo.is_relative_to(into):
        return (
            f"{into} overlaps {repo}, so a draft would be written over the files"
            " under review"
        )
    return ""


def can_escape(rel: str) -> bool:
    """Whether joining this path to a root would land somewhere other than under it.

    !! A question about the string, and only about the string. It answers for
    every root at once, which is what lets a caller stop asking per root -- but
    it cannot answer for the filesystem, so a caller that has a root in hand
    still compares the resolved target.

    ! The drive and the root are asked beside `is_absolute`, because Windows has
    a third form neither covers: `Path("C:util.py").is_absolute()` is `False`
    and it carries a drive, so joining it to a root on any other drive
    discards the root.

    !! It lives here because several callers ask it. `flows/proof_setter.py`
    asks it of a page path the schedule records; `desk/collator.py` asks it of
    the `path` half of a `source`'s `cite`, which a role wrote; `flows/fill.py`
    and `flows/on_the_page.py` ask it of paths before joining them to a root. Measured:
    `Path(root) / "C:/outside/secrets.txt"` is `C:/outside/secrets.txt` --
    `pathlib` discards the left operand when the right is absolute -- so a
    citation check that joined without asking read a file outside the checkout,
    found the `verbatim` in it, and reported the citation verified.

    Args:
        rel: a path that is about to be joined to a root -- a page path in the
            repo's own form, or the `path` half of a `path:line` citation.

    Returns:
        `True` when it is absolute, drive-relative, rooted, or walks up.
    """
    p = Path(rel)
    return bool(p.is_absolute() or p.drive or p.root) or ".." in p.parts


def remove_tree(root: Path, *, ignore_errors: bool = False) -> None:
    r"""`shutil.rmtree`, clearing the read-only bit Windows refuses to unlink.

    !! `shutil.rmtree` alone cannot delete a copied `.git` on Windows. Git
    writes loose objects and `.git/objects/pack/*.pack` read-only, and Windows
    refuses to unlink a read-only file. Measured: `git init` plus one commit
    leaves 3 read-only files under `.git/objects`; `shutil.copytree` preserves
    the mode, and `shutil.rmtree` over the copy raises
    `PermissionError: [WinError 5]`, leaving 15 entries behind.

    ! `shutil.rmtree(ignore_errors=True)` is not a fix for it but the silent
    shape of it: the same case leaves the tree on disk at exit 0 -- a complete,
    ordinary-looking directory that the caller's own contract says is gone.

    ! `onerror`, not `onexc`. `onexc` arrives in 3.12 and the floor here is
    3.11, where it is an unexpected keyword argument.

    ! The hook re-raises rather than reporting, because `shutil.rmtree` calls it
    outside its own `try`, so an exception from it leaves `rmtree` and reaches
    the caller -- which is what makes a tree that could not be removed a
    failure rather than a message.

    Args:
        root: the directory tree to remove.
        ignore_errors: swallow what remains unremovable after the retry.
            `False` -- the default -- lets it raise, which is what a caller
            whose contract says the tree is gone needs.

    Raises:
        OSError: a path could not be removed even with the write bit set, and
            `ignore_errors` is `False`.
    """

    def clear_and_retry(func, path, _exc) -> None:
        try:
            Path(path).chmod(stat.S_IWRITE | stat.S_IREAD)
            func(path)
        except OSError:
            if not ignore_errors:
                raise

    shutil.rmtree(root, onerror=clear_and_retry)


def tracked_paths(repo: Path, rels: list[str] | None) -> set[Path] | None:
    """`git_ls_files` output as resolved absolute paths, for membership tests."""
    if rels is None:
        return None
    return {(repo / rel).resolve() for rel in rels}


def walk_files(root: Path):
    """Each file under `root` it may enter. It enumerates; it classifies nothing.

    ! The walk does not decide. What a file no reader claims becomes -- freeform,
    a refusal or a note -- is the gather's call, and it turns on something only
    the gather knows: whether the path was named or merely found. A directory
    holds READMEs, images and lockfiles; refusing on those makes the form
    unusable, and skipping them in silence is the false completeness this warns
    about.

    ! `EXCLUDED_DIRS` is this module's, which is why the walk sits here rather
    than in the gather. It is not the same question. It is about where the walk
    may go -- a vendored tree is not this repo's code at all -- rather than
    about what a file is once found.
    """
    if root.is_file():
        yield root
        return
    for p in sorted(root.rglob("*")):
        if p.is_file():
            # !! Relative to the root being walked. Matched against `p.parts`
            # this tests every ancestor too, so a checkout living anywhere
            # under a directory called `venv`, `.venv`, `node_modules`,
            # `site-packages`, `__pycache__` or `.git` excludes itself:
            # `flows.gather._name_corpus` harvests 0 names from a git repo under
            # `.../venv/myproject`, nothing is added to `unread`, so the not-checked
            # list stays empty and the run reads as complete -- every
            # `names-a-symbol` a false obituary, handed to four reviewers as
            # settled fact.
            if not EXCLUDED_DIRS.intersection(p.relative_to(root).parts):
                yield p


def relative_to(target: Path, start: Path) -> Path:
    """`target` expressed from `start`, walking up with `..` where it must.

    !! `pathlib` alone; this package does not use `os.path`.
    `Path.relative_to` raises when the target is not under the start, and a
    revise root is a temporary directory outside the checkout -- so the `..`
    walk this function does is the part `pathlib` does not ship.

    Args:
        target: the path to express.
        start: the path to express it from -- `Path.cwd()` for the gather.

    Returns:
        A relative path when both share an anchor, `Path(".")` when they are
        the same place, and the resolved absolute `target` when they do not
        share one.

    !! The absolute fallback is the Windows case: a path on drive `D:` from a
    start on drive `C:` (`os.path.relpath` raises `ValueError: path is on mount
    'D:', start on mount 'C:'` there). ! There is no relative path between two
    anchors, so returning one is impossible and raising is unhelpful; the
    resolved target is the only honest answer. This package handles Windows
    paths elsewhere too (`can_escape`, `remove_tree`) and fetches corpora to
    arbitrary roots, which is what makes two drives ordinary rather than exotic.
    """
    here = target.resolve()
    there = start.resolve()
    if here.anchor != there.anchor:
        return here
    shared = 0
    # ! `strict=False` is the answer here, not the lenient one: the two paths
    # are expected to differ in length -- that difference is exactly what the
    # `..` count below is measured from -- so stopping at the shorter one is
    # the intent rather than a tolerated mismatch.
    for mine, yours in zip(here.parts, there.parts, strict=False):
        if mine != yours:
            break
        shared += 1
    up = [".."] * (len(there.parts) - shared)
    rest = here.parts[shared:]
    # ! `Path(".")` for the same place, which is what a gather of the checkout
    # it is standing in reports. `Path()` with no arguments is `Path(".")`
    # already, but saying it is the difference between a value and an accident.
    return Path(*up, *rest) if (up or rest) else Path(".")
