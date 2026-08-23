"""Stage 3, inbound: which tracked files NAME the files under review.

    python referrers.py --repo D <targets...>

The census resolves what a comment CITES. This resolves the other direction --
who cites the code being edited -- and it is the half that decides the
REFERENCE ONLY list. Without it that list is assembled from memory, and a
`target` run has no diff to widen from at all.

Read-only, always exits 0: an INPUT to a review. Every line it prints is a
CANDIDATE -- a file that names a token is a file to READ, and stays outside what
a verdict may target.
"""

import argparse
import ast
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import constants  # noqa: E402  -- path shim must run first

# ! The exception tuples are IMPORTED. Each is bound to a NAME so no `except`
# clause here holds a tuple literal; `repo.py` carries that reason once.
from repo import (  # noqa: E402  -- path shim must run first
    GIT_ERRORS,
    PARSE_ERRORS,
    READ_ERRORS,
    git,
    git_ls_files,
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
        except PARSE_ERRORS:
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
    except GIT_ERRORS as e:
        return None, type(e).__name__
    if got.returncode == 0:
        return got.stdout.splitlines(), ""
    if got.returncode == 1:
        return [], ""
    return None, f"git grep exit {got.returncode}"


def main() -> int:
    """Print the REFERENCE ONLY candidates for the named targets."""
    constants.utf8_console()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("targets", nargs="+")
    ap.add_argument("--repo", default=".", help="repo root")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    if git_ls_files(repo) is None:
        print("NO GIT INDEX -- cannot resolve referrers. Say so in the stage 3 report.")
        return 0

    under_review = set()
    for raw in args.targets:
        try:
            under_review.add(Path(raw).resolve().relative_to(repo).as_posix())
        except ValueError:
            print(f"  skipped {raw}: outside --repo")

    hits: dict[str, set[str]] = defaultdict(set)
    unreadable: list[str] = []
    # A set, so two targets sharing a token print it once.
    unsearched: set[str] = set()
    for rel in sorted(under_review):
        target = repo / rel
        try:
            text = target.read_text(encoding="utf-8")
        except READ_ERRORS as e:
            text = ""
            unreadable.append(f"{rel} ({type(e).__name__})")
        for token in sorted(tokens_for(Path(rel), text)):
            found, reason = _grep(repo, token)
            if found is None:
                # ! The search never completed, so a real referrer for this
                # token may exist unreported. A different state from
                # "searched, found nothing".
                unsearched.add(f"token {token!r} could not be searched ({reason})")
                continue
            found = [f for f in found if f not in under_review]
            for f in found:
                hits[f].add(token)

    print(f"REFERENCE ONLY candidates for {len(under_review)} file(s) under review")
    print(
        "Every line is a file to READ. None of them may be the target of a verdict.\n"
    )
    if not hits:
        if unsearched:
            # ! A weaker claim than the plain-absence line below. `hits` being
            # empty here may only mean every search that COULD run found
            # nothing -- some did not run at all, and a real referrer may be
            # sitting behind one of them.
            print(
                "  none among the tokens that could be searched -- but some\n"
                "  searches did not complete; see NOT CHECKED below before\n"
                "  treating this as a complete result."
            )
        else:
            print("  none -- nothing tracked names these files.")
    for f in sorted(hits):
        print(f"  {f}\n      names: {', '.join(sorted(hits[f]))}")
    if unreadable or unsearched:
        print("\nNOT CHECKED -- these are gaps, not passes:")
        for u in unreadable:
            print(f"    {u}")
        for u in sorted(unsearched):
            print(f"    {u}")
        if unreadable:
            print(
                "    !! Path and stem tokens for these were still searched; their\n"
                "      public top-level definitions were NOT harvested. The candidate\n"
                "      list for them is incomplete until this list is empty."
            )
        if unsearched:
            print(
                "    !! A token whose search could not complete may have real\n"
                "      referrers this report never saw. The candidate list is\n"
                "      incomplete for these tokens until this list is empty."
            )
    print(
        "\n! CANDIDATES, not findings. A file here is REFERENCE ONLY unless it is "
        "also under review."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
