"""The `prove_unchanged` command: its argument parsing and its exit code.

The work is `flows.prove_unchanged`; this is only the console face of it.

!! A MODULE DOES ONE JOB AND HAS NO CLI; A FLOW CALLS MODULES;
A COMMAND EXPOSES A FLOW. Ruled 2026-08-24 -- `decision-log.md Process: #12`.
"""

import argparse
from pathlib import Path

from comment_review.flows.prove_unchanged import run


def main() -> int:
    """Prove every named path, and report what could not be proven."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--base", required=True, help="ref holding the pre-edit text")
    ap.add_argument("--repo", default=".", help="repo root")
    args = ap.parse_args()

    report = run(Path(args.repo), args.base, [Path(raw) for raw in args.paths])
    for message in report.messages:
        print(message)
    print()
    if report.failures:
        print(f"{report.failures} unproven. WRITE's claim does NOT hold.")
        return 1
    proven = len(args.paths) - report.freeform
    counts = []
    if proven:
        counts.append(f"{proven} proven")
    if report.freeform:
        counts.append(f"{report.freeform} UNCHECKED (no reader)")
    print(", ".join(counts) + ".")
    if report.unchecked:
        print(
            f"{report.unchecked} with line endings UNCHECKED "
            "(no readable untouched sibling to compare against)."
        )
    return 0
