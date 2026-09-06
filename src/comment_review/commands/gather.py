"""The `gather` command: its argument parsing, its printing and its exit code.

The work is `flows.gather`; this is only the console face of it. It builds no
page and resolves no annotation -- `tests/test_gather_command.py` reads this
file to say so.

!! A MODULE DOES ONE JOB AND HAS NO CLI; A FLOW CALLS MODULES;
A COMMAND EXPOSES A FLOW. Ruled 2026-08-24 -- `decision-log.md Process: #12`.
"""

import argparse
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path

from comment_review.binder.addresses import unaddressed
from comment_review.flows.gather import (
    Gathering,
    gather,
    not_gathered,
    unaddressed_report,
)
from comment_review.reading.lexer import LANGUAGES, tier_for


def main() -> int:
    """Gather the pages in scope, then print the binder."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--repo", default=".", help="repo root for citation resolution")
    ap.add_argument(
        "--revise",
        type=int,
        default=0,
        help="the revise `--repo` is -- 0 for the original, a later stage's"
        " number for a revise root pulled after it. Stamped into `read_from`"
        " so a role can tell which tree the binder was gathered from",
    )
    ap.add_argument(
        "--include-absent",
        action="store_true",
        help="carry the EMPTY places too -- a place where prose could go but does"
        " not. Dropped by default: they are 91%% of the rows and a reviewer rules"
        " on prose that is there. Ask the addresser for one instead, by its anchor",
    )
    ap.add_argument(
        "--out", metavar="PATH", help="write the binder to PATH, not stdout"
    )
    ap.add_argument(
        "--languages",
        action="store_true",
        help="list known languages and the tier each reaches, then exit",
    )
    args = ap.parse_args()

    # !! NO PATHS IS A REFUSAL, NOT AN EMPTY BINDER. `paths` is `nargs="*"` so
    # `--languages` can run without one, and everything else with none produced
    # `[]` at exit 0 -- which the collator then reads as a complete binder and
    # certifies. Measured 2026-08-24: `gather --repo . --json` printed `[]`
    # and returned 0, and the collator over it printed "Every finding is
    # admissible. Stage 5 may rule."
    #
    # ! REACHABLE WITHOUT ANYONE TYPING IT: stage 1 takes its paths from a
    # merge-base diff, and a diff that touches no reviewable file hands this
    # nothing. The run then reads as complete BECAUSE there was nothing to be
    # incomplete about -- the failure the collator states the rule against, one
    # stage earlier. ! Refused BEFORE `--out` opens anything, so a usage error
    # leaves no empty binder behind for the next stage to read as an answered one.
    if not args.languages and not args.paths:
        print(
            "REFUSED: no paths. A gather over nothing is not an empty binder --"
            " it is a run with no scope, and every check downstream would pass"
            " on it. Name the files, or pass --languages to list what is known."
        )
        return 2

    # ! WRITES ITS OWN FILE. A shell redirect is refused outright by a
    # worktree-isolated harness -- "too complex to verify that it stays inside
    # the worktree" -- and the JSON binder is what the stage-5 collator reads, so
    # the only documented route to it was unrunnable there.
    if args.out:
        with open(args.out, "w", encoding="utf-8", newline="") as fh:
            with redirect_stdout(fh):
                return _report(args)
    return _report(args)


def _report(args: argparse.Namespace) -> int:
    """Everything the run prints, so `--out` can wrap it in one place."""
    if args.languages:
        print(f"{'language':<10} {'tier':<11} extensions")
        for lang in LANGUAGES:
            exts = " ".join(lang.extensions)
            print(f"{lang.name:<10} {tier_for(lang):<11} {exts}")
        print("\nA suffix not listed is named, and the gather exits nonzero.")
        return 0

    repo = Path(args.repo).resolve()
    got = gather(
        repo, [Path(p) for p in args.paths], args.revise, absent=args.include_absent
    )

    # !! THE GATE FIRST. `--out` is the route SKILL.md mandates for the binder
    # stage 5 parses, and this returned 0 with a SHORT array for a file that
    # could not be read -- so a file with no language record, or one that
    # failed to parse, vanished, and the coverage check then certified "every
    # paragraph accounted for" over paragraphs never collected.
    if got.unreadable:
        print(not_gathered(got.files, got.unreadable), file=sys.stderr)
        return 1
    # !! AN UNADDRESSED PARAGRAPH IS UNCITABLE, so a binder holding one is a
    # binder nobody can rule on -- and it fails SILENTLY: the collator builds
    # its accountability set from the addresses, so paragraphs with none are
    # simply not accountable and the run reads as complete. Measured 2026-08-20:
    # a 5-paragraph binder with its addresses stripped certified "Every finding
    # is admissible. Stage 5 may rule." at exit 0.
    #
    # ! ASKED AT BOTH ENDS. This is the EMIT side, catching the binder where it
    # is built; the collator asks the same function on READ, for a file that
    # reached it some other way. ONE implementation, in `addresser` -- Roy,
    # 2026-08-20: *"one source of truth, else something will parse that
    # something else will fail."*
    # !! THE GATE READS THE BINDER BACK, rather than checking the list that
    # was about to be written. `Binder.paragraphs` is what every consumer
    # reads, so a shape it cannot read is caught HERE -- at the one moment
    # the writer and the reader are both present -- instead of at whichever
    # command opens the file next.
    missing = unaddressed(got.binder.paragraphs)
    if missing:
        print(unaddressed_report(missing), file=sys.stderr)
        return 1
    # !! THE SERIALIZE IS THE CONTAINER'S AND THE DUMP IS THE FLOW'S --
    # `decision-log.md Process: #67`. This is the read flow's save end, and
    # the only place a binder becomes text.
    print(json.dumps(got.binder.serialize(), indent=1, default=str))
    _passed_over(got)
    return 0


def _passed_over(got: Gathering) -> None:
    """The two gap reports, on stderr so the binder on stdout stays parseable.

    Both are gaps and not passes, and both were said only by the text report
    that stage 2 no longer prints; a gather that stopped saying them would
    read as complete over files it never read.
    """
    if got.unread:
        print("NOT CHECKED -- these are gaps, not passes:", file=sys.stderr)
        for u in got.unread:
            print(f"    {u}", file=sys.stderr)
        print(
            "    !! A file missing from the name corpus turns every symbol defined\n"
            "      only there into a false obituary. Treat symbol notes as weaker\n"
            "      until this list is empty.",
            file=sys.stderr,
        )
    if got.no_record:
        # !! SAID, NOT REFUSED, and it used to be neither. A file the walk came
        # across with no language record simply vanished, so a directory target
        # reported a complete binder of whatever it happened to understand --
        # the false completeness this command's own contract exists to prevent.
        # ! A NAMED file still ERRORS: the caller asked for that one. This is the
        # other half, where the caller asked for a tree and cannot know what was
        # in it. MEASURED 2026-08-22 on a two-file directory: named, exit 1;
        # walked, gone at exit 0.
        print(
            f"PASSED OVER -- {len(got.no_record)} file(s) under a directory target"
            " have no language record, so nothing read them:",
            file=sys.stderr,
        )
        for row in got.no_record[:20]:
            print(f"    {row}", file=sys.stderr)
        if len(got.no_record) > 20:
            print(f"    ... and {len(got.no_record) - 20} more", file=sys.stderr)
        print(
            "  ! Name one on the command line to make it an ERROR instead --"
            " `--languages` lists what is known.",
            file=sys.stderr,
        )
