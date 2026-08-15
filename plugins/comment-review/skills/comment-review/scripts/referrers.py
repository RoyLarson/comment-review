"""Stage 3, inbound: which tracked files NAME the files under review.

    python referrers.py --repo D <targets...>

The census resolves what a comment CITES. This resolves the other direction --
who cites the code being edited -- and it is the half that decides the
REFERENCE ONLY list. Without it that list is assembled from memory, and a
`target` run has no diff to widen from at all.

Read-only, and always exits 0: this is an input to a review, not a gate. Every
line it prints is a CANDIDATE. A file that names a token is a file to READ, not
a file with a defect, and not a file a verdict may target.

⚠ A token too common to discriminate is reported as SUPPRESSED with its hit
count, never dumped. A detector below roughly 10% precision buries its own
hits, so the list a human is asked to read must stay readable.
"""

from __future__ import annotations

import argparse
import ast
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from census import GIT_ERRORS, git_ls_files  # noqa: E402  -- path shim first

# ⚠ Bound to a NAME so no `except` clause here holds a tuple LITERAL. This
# file ships under `plugins/` into other people's repositories and is
# formatted by THEIR ruff config; a `target-version` newer than this file's
# floor rewrites `except (A, B):` into PEP 758's unparenthesised form, a
# SyntaxError on every older interpreter. `check_shipped_syntax.py` cannot
# catch this class of defect -- it verifies the file parses today, not that
# it survives a rewrite nobody here will see. Matches `census.py`'s
# `READ_ERRORS` / `GIT_ERRORS` and `prove_unchanged.py`'s same construct.
READ_ERRORS = (OSError, UnicodeDecodeError)
PARSE_ERRORS = (OSError, UnicodeDecodeError, SyntaxError)
NAMED_DEFS = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)

# Above this many hits a token is describing the codebase, not this file.
NOISE_FLOOR = 40


def tokens_for(path: Path, text: str) -> set[str]:
    """Every name by which prose elsewhere would refer to this file.

    Args:
        path: the file's repo-relative path.
        text: its contents, parsed for top-level names when it is Python.

    Returns:
        The stem, the posix path and each of its trailing suffixes, and the
        PUBLIC top-level definitions. Underscored names are excluded: prose
        does not cite them, and they collide with unrelated private helpers.
    """
    out = {path.stem}
    parts = path.as_posix().split("/")
    for i in range(len(parts)):
        out.add("/".join(parts[i:]))
    if path.suffix.lower() in (".py", ".pyi"):
        try:
            tree = ast.parse(text)
        except PARSE_ERRORS:
            return out
        for node in tree.body:
            if isinstance(node, NAMED_DEFS) and not node.name.startswith("_"):
                out.add(node.name)
    return {t for t in out if len(t) > 2}


def _grep(repo: Path, token: str) -> list[str]:
    """Tracked files containing `token` as a fixed string.

    ⚠ The encoding is PINNED. git emits UTF-8; `text=True` alone decodes with
    whatever locale the user's machine has, and a non-ASCII path then arrives
    corrupted — so a real referrer is reported under a name that resolves to
    nothing. Measured on this repo's own `cp1252` machine against the same
    construct in `prove_unchanged.py`.
    """
    try:
        got = subprocess.run(
            ["git", "-C", str(repo), "grep", "-l", "-F", "--", token],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=60,
            check=False,
        )
    except GIT_ERRORS:
        return []
    return got.stdout.splitlines() if got.returncode == 0 else []


def main() -> int:
    """Print the REFERENCE ONLY candidates for the named targets."""
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("targets", nargs="+")
    ap.add_argument("--repo", default=".", help="repo root")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    if git_ls_files(repo) is None:
        print("NO GIT INDEX — cannot resolve referrers. Say so in the stage 3 report.")
        return 0

    under_review = set()
    for raw in args.targets:
        try:
            under_review.add(Path(raw).resolve().relative_to(repo).as_posix())
        except ValueError:
            print(f"  skipped {raw}: outside --repo")

    hits: dict[str, set[str]] = defaultdict(set)
    suppressed: list[str] = []
    unreadable: list[str] = []
    for rel in sorted(under_review):
        target = repo / rel
        try:
            text = target.read_text(encoding="utf-8")
        except READ_ERRORS as e:
            text = ""
            unreadable.append(f"{rel} ({type(e).__name__})")
        for token in sorted(tokens_for(Path(rel), text)):
            found = [f for f in _grep(repo, token) if f not in under_review]
            if len(found) > NOISE_FLOOR:
                suppressed.append(f"{token} ({len(found)} files)")
                continue
            for f in found:
                hits[f].add(token)

    print(f"REFERENCE ONLY candidates for {len(under_review)} file(s) under review")
    print(
        "Every line is a file to READ. None of them may be the target of a verdict.\n"
    )
    if not hits:
        print("  none — nothing tracked names these files.")
    for f in sorted(hits):
        print(f"  {f}\n      names: {', '.join(sorted(hits[f]))}")
    if suppressed:
        print("\nSUPPRESSED — too common to discriminate, triage by hand if needed:")
        for s in suppressed:
            print(f"  {s}")
    if unreadable:
        print("\nNOT CHECKED — these are gaps, not passes:")
        for u in unreadable:
            print(f"    {u}")
        print(
            "    !! Path and stem tokens for this file were still searched;\n"
            "      its public top-level definitions were NOT harvested. The\n"
            "      candidate list for it is incomplete until this list is empty."
        )
    print(
        "\n⚠ CANDIDATES, not findings. A file here is REFERENCE ONLY unless it is "
        "also under review."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
