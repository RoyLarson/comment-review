"""Stage 2, COLLATE: every PAGE in scope, formatted for the agents.

    python census.py [--repo D] [--census-only] [--json] [--out PATH] <paths>

A page is one file -- its paragraphs in order among the code they sit with --
and `page.py` builds one. This walks the files in scope, stacks their pages, and
renders them into what a reviewer reads.

!! THAT IS THE WHOLE SUBJECT. Roy, 2026-08-20: *"the census's job should be to
take the output of all of the pages and reformat it into the (most) usable
format for the agents."* It built one file's paragraphs AND addressed them AND
aggregated them until then, which is three subjects and why it ran to 1,759
lines. ! *most* is subjective and MEASURABLE -- formats can be compared -- and
until one is measured against hazard recall the word does not ship. See
`TODO/census-emits-no-page.md`.

! Most of a page holds no prose -- an empty `interval`, an `undocumented`
declaration, a bare `margin`. Those are ADDRESSABLE, so an `add` can cite the
place its missing sentence belongs in, and nobody owes them a record. Coverage
is over the paragraphs that HOLD prose.

**Every file handed in is censused, or this errors** -- a file it could not read
or parse, or whose suffix has no language record, is named and the run exits
nonzero, because a paragraph missing from the census is a paragraph nobody
reviews.

Read-only. It calls `annotate.py` on each paragraph for stage 3, and `repo.py`
for the facts about the checkout that both need.

! Tier counts are AGGREGATED over the run, because a tier is per FILE and a
polyglot run mixes them. Read the per-file tier stamp to see which file reached
which; `--languages` lists the languages known and the tier each reaches.
"""

import argparse
import ast
import json
import sys
from collections import Counter, defaultdict
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from annotate import (  # noqa: E402  -- path shim must run first
    SYMBOLISH,
    annotate,
    prose_numbers,
)
from foliator import (  # noqa: E402  -- path shim must run first
    SEPARATOR,
)
from lexer import (  # noqa: E402  -- path shim must run first
    BY_EXT,
    LANGUAGES,
    NAMED_DEFS,
    TIER_ANSWERS,
    Paragraph,
    language_for,
    tier_for,
)
from page import (  # noqa: E402  -- path shim must run first
    FRONT_MATTER,
    HOLDS_NO_PROSE,
    page_for,
)
from repo import (  # noqa: E402  -- path shim must run first
    EXCLUDED_DIRS,
    PARSE_ERRORS,
    READ_ERRORS,
    path_index,
    tracked_paths,
)


def _walk(root: Path):
    """Every file under `root` this script has a language record for.

    ! Filters on `BY_EXT`, so every language `--languages` advertises is walked.
    Hardcoded to `*.py`, the scan went Python-only, and a file the walk skips is
    absent from the NOT CHECKED list too -- the run then reports a full census of
    a fraction of the tree.
    """
    if root.is_file():
        yield root
        return
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.suffix.lower() in BY_EXT:
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


# The two gaps in the name corpus that are NOT read failures, named so a caller
# can tell them apart from one. Every row `code_names` returns reads alike --
# `<path> (<reason>)` -- and a reporting caller that treated all of them as
# unreadable files told a polyglot repo that six files "could not be read" and
# then instructed the reader to wait for a list that can never empty.
NO_HARVESTER = "no name harvester for"
WALKED_TREE = "name corpus built by WALKING the tree"


def code_names(
    roots: list[Path], tracked: set[Path] | None = None
) -> tuple[set[str], list[str]]:
    """Every name the tree DEFINES, harvested from the AST.

    A corpus built from raw text contains the comments being checked, so every
    obituary resolves against itself and the check always passes. Unreadable
    files are RETURNED alongside the names: a hole in the corpus turns every
    symbol defined only there into a false obituary, which fails loud and wrong.

    ! TRACKED files only, when git can say which. A vendored, generated or
    gitignored tree under the repo root otherwise donates its whole namespace,
    so a symbol the repo defines nowhere resolves ALIVE. That failure is SILENT
    and one-sided: it can hide an obituary, and manufactures none.

    Args:
        roots: directories or files to harvest.
        tracked: absolute paths git reports as tracked, or None when git could
            not answer -- in which case the whole tree is walked and the caller
            is told, so a change in coverage arrives with the result.

    Returns:
        The set of defined names, and the rows naming every gap in it. A row
        holding `NO_HARVESTER` is a KNOWN hole and a row holding `WALKED_TREE`
        is a caveat about the whole corpus; anything else is a file this
        process genuinely could not read or parse. A caller that tells the
        three apart says so with those two constants -- the three read alike as
        prose, and a caller matching on the prose reclassifies them silently
        the next time this wording changes.
    """
    names: set[str] = set()
    unread: list[str] = []
    if tracked is None:
        unread.append(
            f"{WALKED_TREE} (not a git checkout, or git unavailable) -- "
            "untracked or vendored code may mask an obituary"
        )
    for root in roots:
        for p in _walk(root):
            if tracked is not None and p.resolve() not in tracked:
                continue
            lang = language_for(p)
            # ! A non-Python file is a KNOWN hole, reported as one. Parsed as
            # Python it came back `a.go (SyntaxError)`, which reads as "your
            # file is malformed" and sends a reviewer after an invented defect.
            # Liveness in these languages needs its own harvester; this names
            # the gap until there is one.
            if lang is None or lang.name != "python":
                name = lang.name if lang else "unknown"
                unread.append(f"{p.as_posix()} ({NO_HARVESTER} {name})")
                continue
            try:
                tree = ast.parse(p.read_text(encoding="utf-8"))
            except PARSE_ERRORS as e:
                unread.append(f"{p.as_posix()} ({type(e).__name__})")
                continue
            names.add(p.stem)
            harvest_constants = not (p.name.startswith("test_") or "tests" in p.parts)
            for node in ast.walk(tree):
                if isinstance(node, NAMED_DEFS):
                    names.add(node.name)
                elif isinstance(node, ast.Name):
                    names.add(node.id)
                elif isinstance(node, ast.Attribute):
                    names.add(node.attr)
                elif isinstance(node, ast.arg):
                    names.add(node.arg)
                elif isinstance(node, ast.alias):
                    names.add((node.asname or node.name).split(".")[0])
                elif harvest_constants and isinstance(node, ast.Constant):
                    if isinstance(node.value, str) and SYMBOLISH.match(node.value):
                        names.add(node.value)
    return names, unread


def _repo_relative(path: Path, repo: Path) -> str:
    """`path` as `repo` sees it: posix, relative, no `..`.

    Args:
        path: the file censused.
        repo: the root every citation resolves against.

    Returns:
        The posix path relative to `repo`. ! A file NOT under `repo` keeps the
        path AS IT WAS PASSED, which may itself be relative -- run from a
        subdirectory, `--repo /r ../other/x.py` records `../other/x.py`. There
        is no relative-to-`repo` form of such a file and inventing one with
        `..` would hand a consumer a path that escapes the root it was given,
        so it is passed through unresolved and the consumers refuse it:
        `galley.py` writes nothing that lands outside `--out`.
    """
    try:
        return path.resolve().relative_to(repo).as_posix()
    except ValueError:
        return path.as_posix()


def _not_censused(files: list[Path], unreadable: list[str]) -> str:
    """The refusal, worded ONCE for both output modes.

    !! The reviewers are handed the census, so a file missing from it is paragraphs
    nobody reviews and nothing downstream notices. `--json` used to return 0
    with a SHORT array on exactly the input the text path refused -- and
    `--json --out` is the route `SKILL.md` mandates for the census stage 5
    parses, so the coverage check then certified every paragraph accounted for over
    paragraphs that were never collected.
    """
    listed = "\n".join(f"    {u}" for u in unreadable)
    return (
        f"NOT CENSUSED -- these are gaps, not passes:\n{listed}\n"
        f"ERROR: {len(unreadable)} of {len(files)} files handed in were not"
        " censused. Every file is censused or this errors."
    )


def main() -> int:
    """Build the census, resolve its annotations, print both."""
    # UTF-8 with replacement, so an em-dash in someone's docstring still prints
    # on a console whose encoding lacks it.
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="replace")
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
        "--include-front-matter",
        action="store_true",
        help="keep front matter in a --filtered listing (it is dropped by default);"
        " no effect on an unfiltered run or on --json, which never drop it",
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
    files = sorted({f for t in targets for f in _walk(t)})
    known, unread = code_names([repo], tracked_paths(repo))
    paths = path_index(repo)

    census: list[Paragraph] = []
    # A path argument that matched no file joins `unreadable`, so a typo errors
    # on the same rule every other gap does.
    unreadable: list[str] = [
        f"{t.as_posix()} (matched no files)" for t in targets if not any(_walk(t))
    ]
    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
        except READ_ERRORS as e:
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
        for b in got:
            b.path = rel
        census.extend(got)

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
        print(
            json.dumps(
                [vars(b) | {"annotations": sorted(b.annotations)} for b in census],
                indent=1,
                default=str,
            )
        )
        return 0

    # ! A tier is per FILE: a polyglot repo mixes them in one census. Reported
    # as one global mode, a finding from the lexical floor read like one from
    # the tokenized tier.
    tiers = Counter(b.tier for b in census)
    langs = Counter(lang.name for f in files if (lang := language_for(f)) is not None)
    deferred = [b for b in census if "doc-kind-unresolved" in b.annotations]

    print(f"comment-review stages 2-3 - {len(files)} files, {len(census)} paragraphs")
    print(f"  languages: {', '.join(f'{k} {v}' for k, v in sorted(langs.items()))}")
    for name in ("tokenized", "lexical"):
        if tiers.get(name):
            print(f"  tier {name}: {tiers[name]} paragraphs - {TIER_ANSWERS[name]}")
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
        at = first.address.split("@")[-1]
        seat = at if len(run) == 1 else f"{at}..{last.address.split('@')[-1]}"
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
        # !! FRONT MATTER IS DROPPED FROM WHAT A REVIEWER READS, not collapsed
        # into a run. A licence header or a shebang is not a claim about the
        # code, so no role can settle it and every role would return `clean` on
        # it every run -- see `mark_front_matter`. It keeps its address and its
        # index, so a `move` may still cite it; what it loses is a reviewer's
        # attention and a record it owes.
        # ! `--include-front-matter` OVERRIDES that, and is the only way to see
        # it in a filtered listing. Front matter is the one prose a filtered run
        # drops entirely rather than collapsing into a run, so without an
        # explicit flag a reader comparing the two listings cannot tell a file
        # with a licence header from one without.
        if args.filtered and not args.include_front_matter:
            if FRONT_MATTER in b.annotations:
                continue
        if args.filtered and b.kind in HOLDS_NO_PROSE:
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
    # The reviewers are handed the CENSUS, so a file missing from it is paragraphs
    # nobody reviews and there is nothing downstream that notices. Exit on it.
    if unreadable:
        print("\n" + _not_censused(files, unreadable))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
