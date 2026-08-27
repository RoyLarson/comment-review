"""The `referrers` command: its argument parsing and its exit code.

The work is `referrers`; this is only the console face of it.

!! A MODULE DOES ONE JOB AND HAS NO CLI; A FLOW CALLS MODULES;
A COMMAND EXPOSES A FLOW. Ruled 2026-08-24 -- `decision-log.md Process: #12`.
"""

import argparse
from collections import defaultdict
from contextlib import redirect_stdout
from pathlib import Path

from comment_review.concordance.referrers import _grep, tokens_for
from comment_review.machine import exceptions
from comment_review.machine.repo import git_ls_files


def main() -> int:
    """Print the REFERENCE ONLY candidates for the named targets."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("targets", nargs="+")
    ap.add_argument("--repo", default=".", help="repo root")
    ap.add_argument(
        "--out", metavar="PATH", help="write the report to PATH, not stdout"
    )
    args = ap.parse_args()

    # ! WRITES ITS OWN FILE, for the reason `census.py:276` carries: a
    # worktree-isolated harness REFUSES a command carrying a shell redirect,
    # and the REFERENCE ONLY list is what stage 3 keeps -- so the only route to
    # holding it was unrunnable in the session type the skill is written for.
    if args.out:
        with open(args.out, "w", encoding="utf-8", newline="") as fh:
            with redirect_stdout(fh):
                return _report(args)
    return _report(args)


def _report(args: argparse.Namespace) -> int:
    """Everything the run prints, so `--out` can wrap it in one place."""
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
        except exceptions.READ_ERRORS as e:
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
