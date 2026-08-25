"""The `prove_unchanged` command: its argument parsing and its exit code.

The work is `results.prove_unchanged`; this is only the console face of it.

!! A LIBRARY MODULE DOES ONE JOB AND HAS NO CLI; A FLOW CALLS LIBRARIES;
A COMMAND EXPOSES A FLOW. Ruled 2026-08-24 -- `decision-log.md Process: #12`.
"""

import argparse
from pathlib import Path

from ..machine import exceptions
from ..machine.repo import git_ls_files, read_raw
from ..results.prove_unchanged import (
    _show,
    _sibling,
    _spec,
    code_fingerprint,
    dominant_ending,
)


def main() -> int:
    """Prove every named path, and report what could not be proven."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--base", required=True, help="ref holding the pre-edit text")
    ap.add_argument("--repo", default=".", help="repo root")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    edited = {Path(p).resolve() for p in args.paths}
    tracked = git_ls_files(repo) or []  # one subprocess for the whole run
    failures = 0
    unchecked = 0

    for raw in args.paths:
        target = Path(raw).resolve()
        try:
            rel = target.relative_to(repo).as_posix()
        except ValueError:
            print(f"FAIL      {raw}: outside --repo")
            failures += 1
            continue

        before = _show(repo, args.base, rel)
        if before is None:
            spec = _spec(args.base, rel)
            print(f"UNPROVABLE {rel}: no {spec} -- new file, or bad ref")
            failures += 1
            continue
        try:
            after = target.read_text(encoding="utf-8")
        except exceptions.READ_ERRORS as e:
            print(f"FAIL      {rel}: {type(e).__name__}")
            failures += 1
            continue

        kind_b, fp_b = code_fingerprint(before, target)
        kind_a, fp_a = code_fingerprint(after, target)
        if kind_a == "unprovable" or kind_b == "unprovable":
            print(
                f"UNPROVABLE {rel}: prose could not be separated from code"
                " -- sameness NOT shown"
            )
            failures += 1
        elif kind_a != kind_b:
            print(
                f"FAIL      {rel}: proof kind changed ({kind_b} -> {kind_a}) "
                "-- likely broke Python syntax"
            )
            failures += 1
        elif fp_a != fp_b:
            print(f"FAIL      {rel}: executable code DIFFERS ({kind_a} proof)")
            failures += 1
        else:
            print(f"PROVEN    {rel}: reads the same ({kind_a})")

        sib = _sibling(repo, target, edited, tracked)
        if sib is None:
            print(f"UNCHECKED  {rel}: no readable untouched sibling -- line endings")
            unchecked += 1
        else:
            want = dominant_ending(read_raw(sib))
            got = dominant_ending(read_raw(target))
            # ! BOTH sides are guarded against "none". A single-line file with
            # no trailing newline has no ending to measure, so it reads "none"
            # and would FAIL against any CRLF sibling on ABSENT endings rather
            # than wrong ones.
            if want != "none" and got != "none" and got != want:
                print(f"FAIL      {rel}: line endings {got}, sibling {sib.name} {want}")
                failures += 1

    print()
    if failures:
        print(f"{failures} unproven. WRITE's claim does NOT hold.")
        return 1
    if unchecked:
        print(
            f"{len(args.paths)} paths proven; {unchecked} with line "
            "endings UNCHECKED (no readable untouched sibling to compare against)."
        )
    else:
        print(
            f"{len(args.paths)} paths proven: prose changed, the rest reads the same."
        )
    return 0
