"""The `census` command: its argument parsing and its exit code.

The work is `flows.census`; this is only the console face of it.

!! A LIBRARY MODULE DOES ONE JOB AND HAS NO CLI; A FLOW CALLS LIBRARIES;
A COMMAND EXPOSES A FLOW. Ruled 2026-08-24 -- `decision-log.md Process: #12`.
"""

import argparse
import json
import sys
from collections import Counter, defaultdict
from contextlib import redirect_stdout
from pathlib import Path

from comment_review.binder.addresses import series_of, unaddressed
from comment_review.binder.annotate import annotate, prose_numbers
from comment_review.binder.page import page_for
from comment_review.concordance.code_names import code_names
from comment_review.flows.census import (
    _not_censused,
    _repo_relative,
    _unaddressed,
    carried,
    emitted_row,
)
from comment_review.machine import exceptions
from comment_review.machine.repo import path_index, tracked_paths, walk_files
from comment_review.reading.addresser import COVERS, SEPARATOR
from comment_review.reading.lexer import (
    LANGUAGES,
    Kind,
    Paragraph,
    language_for,
    tier_for,
)


def main() -> int:
    """Build the census, resolve its annotations, print both."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--repo", default=".", help="repo root for citation resolution")
    ap.add_argument("--census-only", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument(
        "--filtered",
        action="store_true",
        help="the reviewer's view: prose paragraphs, and one line per run of intervals",
    )
    ap.add_argument(
        "--include-matter",
        action="store_true",
        help="keep the file's OWN matter -- a licence, a shebang, an index --"
        " in a --filtered listing (it is dropped by default); no effect on an"
        " unfiltered run or on --json, which never drop it",
    )
    ap.add_argument(
        "--out", metavar="PATH", help="write the report to PATH, not stdout"
    )
    ap.add_argument(
        "--languages",
        action="store_true",
        help="list known languages and the tier each reaches, then exit",
    )
    args = ap.parse_args()

    # !! NO PATHS IS A REFUSAL, NOT AN EMPTY CENSUS. `paths` is `nargs="*"` so
    # `--languages` can run without one, and everything else with none produced
    # `[]` at exit 0 -- which the join then reads as a complete census and
    # certifies. Measured 2026-08-24: `census.py --repo . --json` printed `[]`
    # and returned 0, and `verdicts.py` over it printed "Every finding is
    # admissible. Stage 5 may rule."
    #
    # ! REACHABLE WITHOUT ANYONE TYPING IT: stage 1 takes its paths from a
    # merge-base diff, and a diff that touches no reviewable file hands this
    # nothing. The run then reads as complete BECAUSE there was nothing to be
    # incomplete about -- the failure `verdicts.py` states the rule against, one
    # stage earlier. ! Refused BEFORE `--out` opens anything, so a usage error
    # leaves no empty census behind for the next stage to read as an answered one.
    if not args.languages and not args.paths:
        print(
            "REFUSED: no paths. A census over nothing is not an empty census --"
            " it is a run with no scope, and every check downstream would pass"
            " on it. Name the files, or pass --languages to list what is known."
        )
        return 2

    # ! WRITES ITS OWN FILE. A shell redirect is refused outright by a
    # worktree-isolated harness -- "too complex to verify that it stays inside
    # the worktree" -- and the JSON census is what the stage-5 join parses, so
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
        print("\nA suffix not listed is named, and the census exits nonzero.")
        return 0

    repo = Path(args.repo).resolve()
    targets = [Path(p) for p in args.paths]
    # ! WALKED ONCE PER TARGET. The emptiness test below re-walked every tree a
    # second time to ask `not any(walk_files(t))`, which this already knows.
    by_target = {t: sorted(walk_files(t)) for t in targets}
    # !! NAMED, AS AGAINST FOUND -- the distinction the walk is no longer making.
    # A file the caller NAMED is refused when nothing can read it; a file the
    # walk came across is reported and skipped, because a directory holds
    # READMEs and lockfiles and refusing on those makes the form unusable.
    named = {t.resolve() for t in targets if t.is_file()}
    no_record: list[str] = []
    files = []
    for path in sorted({f for found in by_target.values() for f in found}):
        if language_for(path) is None and path.resolve() not in named:
            no_record.append(path.as_posix())
        else:
            files.append(path)
    known, unread = code_names([repo], tracked_paths(repo))
    paths = path_index(repo)

    census: list[Paragraph] = []
    # A path argument that matched no file joins `unreadable`, so a typo errors
    # on the same rule every other gap does.
    unreadable: list[str] = [
        f"{t.as_posix()} (matched no files)"
        for t, found in by_target.items()
        if not found
    ]
    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
        except exceptions.READ_ERRORS as e:
            unreadable.append(f"{path.as_posix()} ({type(e).__name__})")
            continue
        lang = language_for(path)
        if lang is None:
            unreadable.append(f"{path.as_posix()} (no language record for its suffix)")
            continue
        # !! EVERY PARAGRAPH'S PATH IS REPO-RELATIVE. It is what `--repo` is for:
        # the census, the file lists and every citation a reviewer writes all
        # resolve against that root, so a paragraph carrying an absolute path is a
        # paragraph no consumer can place. It happened whenever the run was handed
        # absolute file arguments, which is how a task agent that resolved its
        # own paths would call this.
        #
        # !! Measured 2026-08-17: `galley.py` joins `out / paragraph["path"]`, and
        # in Python an absolute right-hand side WINS a join -- so the galley
        # wrote over the source file, put nothing under `--out`, and printed
        # that it had succeeded. The module whose one promise is "nothing under
        # `--repo` is touched" was editing the tree under review.
        #
        # ! A file outside the repo keeps the path AS IT WAS PASSED -- see
        # `_repo_relative`, which says what that means. `galley.py` refuses to
        # write such a paragraph rather than guessing where it belongs.
        # ! HOISTED. `_repo_relative` calls `Path.resolve()`, a filesystem
        # call, and both arguments are the same for every paragraph of a file.
        # Measured 2026-08-18: 120 us a call, so one 793-paragraph file spent
        # 95 ms resolving one path 793 times.
        rel = _repo_relative(path, repo)
        # !! A PATH HOLDING THE SEPARATOR CANNOT BE ADDRESSED, so it is a GAP
        # and not a paragraph with a broken name. `flatten` joins segments on `:`,
        # which Windows forbids in a filename; POSIX forbids only `/` and NUL,
        # so a POSIX checkout can hold `a:b.py`, whose address would be the
        # address of `a/b.py`. That is the collision the separator was chosen to
        # end -- it was `.` until 2026-08-19, and `a/b.py` and `a.b.py` shared
        # every address they had.
        #
        # ! IT READS THE REPO-RELATIVE PATH, WHICH IS THE ONE ADDRESSED. The
        # absolute path holds a colon on every Windows run -- the drive letter
        # -- so checking `path` here refuses the whole tree.
        if SEPARATOR in rel:
            unreadable.append(f"{rel} (a path may not hold '{SEPARATOR}')")
            continue
        # ! THE REPO-RELATIVE PATH GOES IN, so the census comes back addressed
        # against the root every citation resolves to. It was stamped afterwards
        # for as long as `page_for` returned an unaddressed census, which is
        # the split that let a direct caller receive half a census.
        try:
            got = page_for(path, text, lang, rel)
        except Exception as e:  # a parse failure is REPORTED, as a gap
            unreadable.append(f"{path.as_posix()} ({type(e).__name__}: {e})")
            continue
        census.extend(carried(got))

    for b in census:
        annotate(b, known, paths, repo)

    # repeated-literal needs the whole census, so it is a second pass. A number
    # written twice is a hand-copied value, and the copies drift; one written
    # once is just a number.
    seen: Counter[str] = Counter()
    where: dict[str, set[str]] = defaultdict(set)
    for b in census:
        for n in prose_numbers(b.text, b.raw_lines):
            seen[n] += 1
            where[n].add(f"{b.path}:{b.start}")
    for b in census:
        for n in prose_numbers(b.text, b.raw_lines):
            if seen[n] > 1 and len(where[n]) > 1:
                b.annotations.add("repeated-literal")
                others = sorted(where[n] - {f"{b.path}:{b.start}"})[:3]
                b.notes.append(f"{n} also in prose at {', '.join(others)}")

    if args.json:
        # !! THE GATE FIRST. `--json --out` is the route SKILL.md mandates for
        # the census stage 5 parses, and this returned 0 with a SHORT array for
        # a file that could not be read -- so a file with no language record,
        # or one that failed to parse, vanished, and the coverage check then
        # certified "every paragraph accounted for" over paragraphs never collected.
        # The text path errored on exactly the same input.
        if unreadable:
            print(_not_censused(files, unreadable), file=sys.stderr)
            return 1
        # !! AN UNADDRESSED PARAGRAPH IS UNCITABLE, so a census holding one is a
        # census nobody can rule on -- and it fails SILENTLY: `verdicts.py` builds
        # its accountability set from the addresses, so paragraphs with none are
        # simply not accountable and the run reads as complete. Measured 2026-08-20:
        # a 5-paragraph census with its addresses stripped certified "Every finding
        # is admissible. Stage 5 may rule." at exit 0.
        #
        # ! ASKED AT BOTH ENDS. This is the EMIT side, catching the census where it
        # is built; `verdicts.py` asks the same function on READ, for a file that
        # reached it some other way. ONE implementation, in `addresser` -- Roy,
        # 2026-08-20: *"one source of truth, else something will parse that
        # something else will fail."*
        # ! SERIALISED ONCE. This list was built twice -- once to check and once
        # to print -- which is two full dict copies and a re-sort of every
        # annotation set over a census that runs to thousands of paragraphs.
        rows = [emitted_row(b) for b in census]
        missing = unaddressed(rows)
        if missing:
            print(_unaddressed(missing), file=sys.stderr)
            return 1
        print(json.dumps(rows, indent=1, default=str))
        return 0

    # !! NO TIER COUNTS, AND NO `tier` ON A ROW. Ruled 2026-08-24 -- Roy: *"their
    # level gets dropped entirely. Not necessary and the parser tier isn't long
    # for this world."* ! The field stamped one of two words onto every
    # paragraph of a file and this counter was its ONLY reader, so what it bought
    # was a line of preamble about a distinction `python-cannot-read-python` is
    # about to erase. ! `--languages` still reports which tier a LANGUAGE
    # reaches, because that is a fact about the language and not about a place.
    langs = Counter(lang.name for f in files if (lang := language_for(f)) is not None)
    deferred = [b for b in census if "doc-kind-unresolved" in b.annotations]

    print(f"comment-review stages 2-3 - {len(files)} files, {len(census)} paragraphs")
    print(f"  languages: {', '.join(f'{k} {v}' for k, v in sorted(langs.items()))}")
    print(
        "  ! EVERY address carries an anchor -- the LINE OF CODE it attaches\n"
        "    to, at both tiers. What still needs READING is whether the prose\n"
        "    belongs to it, so a placement finding is a CANDIDATE."
    )
    if deferred:
        print(
            f"  kind unresolved: {len(deferred)} -- a positional doc comment."
            " Confirm the kind before compacting; a cap governs one and not"
            " the other"
        )
    print()

    if args.filtered:
        # !! A PROJECTION, NEVER A RENUMBERING. Each paragraph keeps the index it
        # has in the full census, because that index is what the join resolves
        # and what a record cites -- renumber and every citation from a filtered
        # reviewer resolves to the wrong paragraph, with nothing able to tell.
        print("CENSUS - the paragraphs holding prose, numbered as in the full census.")
    else:
        print("CENSUS - every paragraph, numbered.")
    # !! THE FILE IS STATED ONCE, not on every row. Measured 2026-08-18 over
    # the 13 shipped scripts: 778 rows repeated their path 1,556 times, 80,912
    # of the listing's 205,753 bytes -- 39% -- and every reviewer gets an
    # identical copy of it. A place and a line range mean nothing without a
    # file, so the file heads its own rows instead.
    seen_path = ""
    run: list[int] = []
    # ! Which file the open run belongs to, so it can be closed at the boundary.
    run_path = ""

    def heading(path: str) -> None:
        """Announce the file these rows belong to, once."""
        nonlocal seen_path
        if path != seen_path:
            seen_path = path
            print(f"\n== {path}")

    def flush_run() -> None:
        """One line for a stretch of code no prose sits in."""
        if not run:
            return
        first, last = census[run[0] - 1], census[run[-1] - 1]
        heading(first.path)
        span = f"{first.start}-{last.end}"
        # ! The FIRST index sits in the same column a paragraph's does, so the
        # numbering reads down the page as one sequence -- a run carries census
        # indices, not a different kind of row. `1-interval` and not
        # `1-intervals`, because this is prose a reviewer reads.
        where = f"{run[0]:4d}" if len(run) == 1 else f"{run[0]:4d}-{run[-1]}"
        # ! A run spans several PLACES, so it names its ends. Each is still
        # cited singly, by its own address.
        # !! IT NAMES ITS ADDRESSED ENDS, and not simply its first and last.
        # `leading` carries no address -- it names no place and nothing can cite
        # it -- so a run that opens or closes on one rendered `@..c0`, an end a
        # reviewer cannot use and a range that reads as truncated. MEASURED
        # 2026-08-22 on `--filtered`, the command SKILL.md hands a reviewer.
        cited = [
            b.address.split("@")[-1] for b in (census[i - 1] for i in run) if b.address
        ]
        at = cited[0] if cited else ""
        seat = at if len(cited) < 2 else f"{at}..{cited[-1]}"
        # !! THE SAME COLUMNS AS A PARAGRAPH ROW -- index, address, KIND, lines,
        # notes -- because this listing is pasted into a reviewer's prompt and
        # is read down its columns. Written as prose (`no prose (5 intervals)`)
        # the third column read `no`, which is where a paragraph states its kind,
        # so a run and a paragraph could not be told apart by anything mechanical.
        # ! The notes column names what it counts, in the hyphenated form the
        # annotations use, so the row is readable without the header.
        # ! It names WHAT it collapsed rather than assuming one kind. A run
        # mixes `interval`, `margin` and `undocumented` -- the gap above a line
        # of code, the room beside it, and a declaration with no docstring --
        # and a reviewer citing into one needs to know which are in there.
        kinds = Counter(census[n - 1].kind for n in run)
        counted = ", ".join(
            f"{n}-{kind}" + ("" if n == 1 else "s") for kind, n in sorted(kinds.items())
        )
        print(f"{where}  @{seat}  {span}  no-prose  0L  {counted}")
        run.clear()

    for i, b in enumerate(census, 1):
        # !! FILTERED, and every place that HOLDS NO PROSE becomes one line per
        # run rather than vanishing. It collapsed `interval` alone until
        # 2026-08-19, which was the whole set when it was written and is now a
        # third of it: `margin` and `undocumented` arrived with the `c` and `a`
        # series and were listed one row each. **Measured over this repo's own
        # 15 shipped scripts: 3,282 bare `margin` rows against 484 rows of
        # prose -- 87% of what a reviewer reads, four times over.**
        #
        # ! Collapsing rather than dropping keeps what an `add` is about
        # visible: a stretch of code carrying no commentary. The run NAMES ITS
        # ENDS, so every place inside it is still citable by address.
        # !! THE FILE'S OWN MATTER IS DROPPED FROM WHAT A REVIEWER READS, not
        # into a run. A licence header or a shebang is not a claim about the
        # code, so no role can settle it and every role would return `clean` on
        # it every run. It keeps its address and its index, so a `move` may
        # still cite it; what it loses is a reviewer's attention and a record it
        # owes.
        # ! `--include-matter` OVERRIDES that, and is the only way to see it in
        # a filtered listing. The `f` series is the one prose a filtered run
        # drops entirely rather than collapsing into a run, so without an
        # explicit flag a reader comparing the two listings cannot tell a file
        # with a licence header from one without.
        # !! A RUN ENDS AT THE FILE IT IS IN, and nothing said so until
        # 2026-08-22. Neither `continue` below reaches `flush_run`, and no test
        # was on the PATH at all -- so a run opened in one file carried into the
        # next and the row named ends from two different files.
        #
        # ! MEASURED: `constants.py`, 43 lines, carried a row reading
        # `15-72 @c2..b58 41-0` -- `repo.py`'s 53 intervals attributed to it, a
        # span running BACKWARDS, and an `add` composed from that row citing an
        # address that does not exist on the file it names.
        if b.path != run_path:
            flush_run()
            run_path = b.path
        # ! `b.address` FIRST: a `d` names no place, so it has no series to
        # compare. It fell through this test to the `holds_no_prose` branch
        # below, which is where it always belonged.
        if args.filtered and not args.include_matter and b.address:
            if series_of(vars(b)) == COVERS:
                # ! FLUSHED, NOT SKIPPED. Front matter is PROSE that this
                # listing drops; a run that continued across it would claim no
                # prose over a stretch that has some.
                flush_run()
                continue
        if args.filtered and Kind.holds_no_prose(b.kind):
            run.append(i)
            continue
        flush_run()
        notes = ",".join(sorted(b.annotations)) or "-"
        anchor = f"  ({b.anchor})" if b.anchor else ""
        heading(b.path)
        # !! THE PLACE COMES FIRST because it is what a record CITES. The line
        # range beside it is the reader's cursor into the file as it stands
        # now, and it is stale the moment this run edits anything above it.
        at = b.address.split("@")[-1]
        span = f"{b.start}-{b.end}"
        print(f"{i:4d}  @{at}  {span}  {b.kind}  {b.lines}L  {notes}{anchor}")
        if not args.census_only:
            for note in b.notes:
                print(f"        -> {note}")
    flush_run()
    print()

    if unread or unreadable:
        print("NOT CHECKED -- these are gaps, not passes:")
        for u in unread + unreadable:
            print(f"    {u}")
        print(
            "    !! A file missing from the name corpus turns every symbol defined\n"
            "      only there into a false obituary. Treat symbol notes as weaker\n"
            "      until this list is empty."
        )
        print()

    print(
        f"{len(census)} paragraphs censused. `names-a-symbol` and `counted` are\n"
        "CANDIDATES a reviewer confirms; a resolved path is a fact about the\n"
        "filesystem, already settled. The whole list is printed every run."
    )
    if no_record:
        # !! SAID, NOT REFUSED, and it used to be neither. A file the walk came
        # across with no language record simply vanished, so a directory target
        # reported a complete census of whatever it happened to understand --
        # the false completeness this script's own contract exists to prevent.
        # ! A NAMED file still ERRORS: the caller asked for that one. This is the
        # other half, where the caller asked for a tree and cannot know what was
        # in it. MEASURED 2026-08-22 on a two-file directory: named, exit 1;
        # walked, gone at exit 0.
        print(
            f"\nPASSED OVER -- {len(no_record)} file(s) under a directory target"
            " have no language record, so nothing read them:"
        )
        for row in no_record[:20]:
            print(f"    {row}")
        if len(no_record) > 20:
            print(f"    ... and {len(no_record) - 20} more")
        print(
            "  ! Name one on the command line to make it an ERROR instead --"
            " `--languages` lists what is known."
        )
    # The reviewers are handed the CENSUS, so a file missing from it is paragraphs
    # nobody reviews and there is nothing downstream that notices. Exit on it.
    if unreadable:
        print("\n" + _not_censused(files, unreadable))
        return 1
    # ! The same refusal on the text path. It is the one a person reads, and a
    # census that cannot be cited is no more usable for being legible.
    missing = unaddressed([emitted_row(b) for b in census])
    if missing:
        print("\n" + _unaddressed(missing))
        return 1
    return 0
