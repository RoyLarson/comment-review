"""Stage 5's gate: join four reviewers' reports against the census.

    python verdicts.py --census census.json --repo D <report>...

Checks the task agent was asked to perform by hand, every one mechanical:

  COVERAGE      every census index accounted for, by every reviewer that ran
  EVIDENCE      each finding's citation resolves, and the QUOTE is really there
  LOCATION      the prose citation resolves too -- checked the same way
  PAYLOAD       the verdict carries what its row of the table requires
  CONTRADICTION `drop` against `correct`/`patch` on one block -- a re-review.
                Counted apart from the fatal checks, and named in the closing
                line so the summary says which blocks are still out
  STANDS        blocks every reviewer that ran returned clean on
  REVIEWER      (only with `--reviewers`) every expected reviewer actually reported

⚠ Exits nonzero on a coverage gap or an unverifiable citation.

⚠ It reports which findings are ADMISSIBLE. The ruling is stage 5's, in
SKILL.md's synthesis order.

⚠ Every block is accounted for by a RECORD, `clean` included. A `clean` record
carries a BLOCK, a VERDICT and a LOCATION, and the LOCATION resolves against the
tree, so covering N blocks costs N records that each name a real prose range. A
`clean` record carries no QUOTE, so it stops short of proof the file was read:
grade a run from its DIFF, and not from this exit code.

⚠ `--reviewers` is OPTIONAL, and its absence is ANNOUNCED: without it, a
reviewer that never reported at all passes this tool unseen.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

READ_ERRORS = (OSError, UnicodeDecodeError)

VERDICTS = (
    "clean",
    "query",
    "drop",
    "correct",
    "patch",
    "add",
    "move",
)

RECORD = re.compile(r"^---\s*RECORD\s*$(.*?)^---\s*$", re.M | re.S)
# Counts "--- RECORD" OPENERS on their own, independent of whether a closing
# "---" was ever found. A first record missing its close makes RECORD's
# non-greedy search skip straight past the second record's opener (it is not a
# bare "---" line) and swallow both into one match -- the second record's
# fields silently overwrite the first's and a finding vanishes with no output.
# Comparing this count against RECORD's match count is how that is caught.
OPENER = re.compile(r"^---\s*RECORD\s*$", re.M)
FIELD = re.compile(
    r"^\s*(BLOCK|VERDICT|LOCATION|EVIDENCE|QUOTE|SUMMARY|FINDING|CHANGE)\s+(.*)$"
)
# `file:line` or `file:start-end`, shared by EVIDENCE and LOCATION -- a
# fabricated prose location is exactly as inadmissible as a fabricated
# citation once both are resolved the same way.
CITE = re.compile(r"^(.+?):(\d+)(?:-(\d+))?$")

# How far from the cited line the quoted text may sit. Prose wraps and code
# moves; a hard equality would reject honest citations, and a wide window would
# accept a fabricated one.
EVIDENCE_WINDOW = 3

# A needle shorter than this could match almost any file by accident --
# `QUOTE e` passed against nearly anything. The forcing function only forces if
# the quote is long enough to have required reading the line.
MIN_NEEDLE = 12

# What a `query`'s PAYLOAD must name: a check that was attempted, and the thing
# that would settle the claim.
#
# ⚠ A SHAPE check: it removes the query that names no check at all, and the
# word "grepped" passes it. See `evidence_problem` for the DISPUTED question of
# whether a query owes EVIDENCE on top of this.
#
# Matched on WORD BOUNDARIES. As substrings, "ran" hit *b**ran**ch*,
# *****ran***ge* and *t**ran**sfer*, and "settle" hit *un**settle**d*, so
# ordinary English naming no check passed while an honest query worded with
# "requires" / "resolves" / "determined by" was refused. `grep` is the one
# deliberate exception, left unanchored on its left so "ripgrep" counts:
# English words carry "ran" and "read" by accident, and "grep" they do not.
QUERY_ATTEMPTED = re.compile(
    r"\bran\b|\bcheck\w*|grep\w*|\bread\w*|\bsearch\w*|\bopen\w*|\bcount\w*|\blook\w*",
    re.I,
)
QUERY_SETTLES = re.compile(
    r"\bsettl\w*|\bwould\s+\w+|\brequires?\b|\bresolv\w*|\bdetermined\s+by\b",
    re.I,
)


@dataclass
class Finding:
    """One reviewer's ruling on one census block.

    Field order follows the record in `reviewer-brief.md`. `quote` is the
    VERBATIM text at `evidence`; `summary`'s right half is the DERIVED
    statement, where a count and its population live, so it is the reviewer's
    own sentence rather than a line any file carries.
    """

    reviewer: str
    block: int
    verdict: str
    location: str
    evidence: str
    quote: str
    summary: str
    finding: str
    change: str


def _n(count: int, noun: str) -> str:
    """`"1 block"`, `"2 blocks"` -- this output decides whether an agent proceeds."""
    return f"{count} {noun}" if count == 1 else f"{count} {noun}s"


def _malformed(reviewer: str, why: str) -> Finding:
    """A record that cannot be attributed to any real block.

    `block=-1` is the sentinel `main()` treats as fatal on sight, for either
    reason -- a missing BLOCK, or a record whose closing "---" is absent.
    """
    return Finding(
        reviewer=reviewer,
        block=-1,
        verdict="malformed",
        location="",
        evidence="",
        quote="",
        summary="",
        finding=why,
        change="",
    )


def parse_report(text: str, reviewer: str) -> list[Finding]:
    """Every record in one reviewer's report, `clean` included.

    Args:
        text: the report as the reviewer returned it. Prose around the records
            is ignored, so a reviewer may still explain itself.
        reviewer: the editorial role's name, attached to every finding it made.

    Returns:
        The parsed findings. Coverage is computed from these alone -- a block a
        reviewer never recorded is a block it never accounted for.
    """
    found: list[Finding] = []
    bodies = RECORD.findall(text)
    openers = len(OPENER.findall(text))
    if openers != len(bodies):
        found.append(
            _malformed(
                reviewer,
                f"{_n(openers, 'RECORD opener')} but"
                f" {_n(len(bodies), 'closed record')}"
                " -- an unterminated record swallows the next one",
            )
        )
    for body in bodies:
        fields: dict[str, str] = {}
        for line in body.splitlines():
            m = FIELD.match(line)
            if m:
                fields[m.group(1)] = m.group(2).strip()
        raw_block = fields.get("BLOCK", "")
        if raw_block.isdecimal():
            found.append(
                Finding(
                    reviewer=reviewer,
                    block=int(raw_block),
                    verdict=fields.get("VERDICT", "").strip().lower(),
                    location=fields.get("LOCATION", ""),
                    evidence=fields.get("EVIDENCE", ""),
                    quote=fields.get("QUOTE", ""),
                    summary=fields.get("SUMMARY", ""),
                    finding=fields.get("FINDING", ""),
                    change=fields.get("CHANGE", ""),
                )
            )
        else:
            found.append(_malformed(reviewer, "a record with no BLOCK index"))
    return found


def coverage_gaps(
    all_blocks: set[int], reported: set[str], found: list[Finding]
) -> dict[str, list[int]]:
    """Indices each reviewer left unaccounted for. A gap is a gap, not a pass.

    `reported` is who handed in a file, and the findings say who produced a
    record. A report that parsed to nothing is a reviewer that accounted for
    nothing, so taking the population from the findings alone would drop it.
    """
    by_reviewer: dict[str, set[int]] = defaultdict(set)
    for f in found:
        by_reviewer[f.reviewer].add(f.block)
    gaps: dict[str, list[int]] = {}
    for reviewer in reported | set(by_reviewer):
        missing = sorted(all_blocks - by_reviewer[reviewer])
        if missing:
            gaps[reviewer] = missing
    return gaps


def payload_problem(f: Finding) -> str | None:
    """What the verdict's required payload is missing, or None.

    `query` is the one row checked in any detail here, because `evidence_problem`
    exempts it — see the DISPUTED note there.
    """
    change = f.change.lower()
    if f.verdict == "query":
        if not QUERY_ATTEMPTED.search(change):
            return (
                "query needs the check you ATTEMPTED — a query naming none"
                " hands the judgement back"
            )
        if not QUERY_SETTLES.search(change):
            return "query needs what WOULD settle the claim"
    if f.verdict == "correct" and not ("false:" in change and "true:" in change):
        return "correct needs a true/false pair in CHANGE"
    if (
        f.verdict == "add"
        and "anchor" not in change
        and "above" not in change
        and "below" not in change
    ):
        return "add needs an anchor (which declaration, above or below)"
    if f.verdict == "move" and "->" not in change and " to " not in change:
        return "move needs a destination and the verbatim extract"
    if f.verdict not in ("clean",) and not f.change.strip():
        return f"{f.verdict} carries no payload — the judgement was handed back"
    return None


def _resolve_lines(
    cite: str, repo: Path, *, allow_range: bool = True
) -> tuple[Path, int, int, list[str]] | str:
    """Resolve a `file:line` or `file:start-end` citation, or say why not.

    Shared by EVIDENCE and LOCATION: both are inadmissible on exactly the same
    grounds -- an unparseable citation, a missing file, or a line number past
    the end of it (or below 1, which is off every file).

    Args:
        cite: the `file:line` or `file:start-end` text.
        repo: the repo root the path is relative to.
        allow_range: EVIDENCE is `file:line` in the record format; only
            LOCATION may carry `file:start-end`. The shared regex is wide
            enough for both, and this holds EVIDENCE to the narrow form.

    Returns:
        `(path, start, end, lines)` when it resolves, else the problem string.
    """
    m = CITE.match(cite.strip())
    if not m:
        return f"{cite!r} is not file:line or file:start-end"
    rel, start_s, end_s = m.group(1), m.group(2), m.group(3)
    if end_s and not allow_range:
        return f"{cite} is file:start-end; EVIDENCE must be file:line, not a range"
    start = int(start_s)
    end = int(end_s) if end_s else start
    if start < 1 or end < 1:
        return f"{cite} -- line numbers are 1-based, 0 is not one"
    target = repo / rel
    if not target.is_file():
        return f"{cite} does not resolve to a file"
    try:
        lines = target.read_text(encoding="utf-8", errors="replace").splitlines()
    except READ_ERRORS as e:
        return f"{cite} unreadable ({type(e).__name__})"
    if end > len(lines):
        return (
            f"{cite} -- line {end} is past the end of {rel} ({_n(len(lines), 'line')})"
        )
    return target, start, end, lines


def evidence_problem(f: Finding, repo: Path) -> str | None:
    """Why this finding's citation cannot be trusted, or None.

    Reads the cited line out of the file and looks for the QUOTE within a few
    lines of it. A finding whose quote is absent from the file it cites is a
    finding the file did not supply — a report is evidence of nothing on its own.

    ⚠ QUOTE is checked, and `SUMMARY`'s right half is the DERIVED statement —
    *"31 callers, all under tests/"* — which is the reviewer's own sentence, so
    checking it here made every counted claim structurally inadmissible. The
    forcing function lands on a field that carries verbatim text alone.

    ⚠ `query` is exempt alongside `clean`, and `payload_problem` checks it
    instead. DISPUTED and UNRESOLVED: `reviewer-brief.md` requires EVIDENCE and
    a QUOTE of a `query`, and this script requires neither.
    """
    if f.verdict in ("clean", "query"):
        return None
    resolved = _resolve_lines(f.evidence, repo, allow_range=False)
    if isinstance(resolved, str):
        return f"EVIDENCE {resolved}"
    _target, lineno, _end, lines = resolved
    needle = " ".join(f.quote.split()).strip().strip('"')
    if not needle:
        return f"no QUOTE — nothing was read out of {f.evidence}"
    if len(needle) < MIN_NEEDLE:
        return f"QUOTE {needle!r} is too short to have been read off a line"
    if not f.summary.partition("||")[2].strip():
        return "SUMMARY has no right half — the finding states nothing derived"
    lo = max(0, lineno - 1 - EVIDENCE_WINDOW)
    window = " ".join(
        " ".join(ln.split()) for ln in lines[lo : lineno + EVIDENCE_WINDOW]
    )
    head = needle[:40]
    if head.lower() not in window.lower():
        return f"QUOTE not found near {f.evidence}: {head!r}"
    return None


def location_problem(f: Finding, repo: Path) -> str | None:
    """Why this finding's LOCATION cannot be trusted, or None.

    Checked with the same `file:line` resolution as EVIDENCE, so a fabricated
    prose location is as inadmissible as a fabricated citation.
    """
    if f.verdict == "clean":
        return None
    resolved = _resolve_lines(f.location, repo)
    if isinstance(resolved, str):
        return f"LOCATION {resolved}"
    return None


def contradictions(found: list[Finding]) -> list[int]:
    """Blocks where one reviewer says delete and another says fix. Re-review."""
    by_block: dict[int, set[str]] = defaultdict(set)
    for f in found:
        if f.block < 0:
            continue  # a malformed record names no real block
        by_block[f.block].add(f.verdict)
    return sorted(
        b for b, vs in by_block.items() if "drop" in vs and ({"correct", "patch"} & vs)
    )


def main() -> int:
    """Join the reports, report what is inadmissible, and gate on it."""
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("reports", nargs="+", help="one report file per reviewer")
    ap.add_argument("--census", required=True, help="census.py --json output")
    ap.add_argument("--repo", default=".", help="repo root for evidence resolution")
    ap.add_argument(
        "--reviewers",
        default="",
        help=(
            "comma-separated expected reviewer names, matched against each report"
            " file's STEM (ownership-context.md -> ownership-context); one missing"
            " a report is fatal"
        ),
    )
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    # ⚠ Guarded like a report file, so a missing census prints which file and
    # why in one line.
    try:
        census_text = Path(args.census).read_text(encoding="utf-8")
    except READ_ERRORS as e:
        print(
            f"CANNOT READ {args.census} ({type(e).__name__})"
            " — no census to join against"
        )
        return 1
    try:
        blocks = json.loads(census_text)
    except json.JSONDecodeError as e:
        print(
            f"CANNOT PARSE {args.census} as JSON ({e})"
            " — is this census.py --json output?"
        )
        return 1
    all_blocks = set(range(1, len(blocks) + 1))

    fatal = 0

    # ⚠ Refused on every run, `--reviewers` or not: a reviewer is keyed by its
    # report's stem, so two files with the same stem put one reviewer's
    # coverage in place of the other's.
    stems = [Path(r).stem for r in args.reports]
    for stem in sorted({s for s, n in Counter(stems).items() if n > 1}):
        print(f"  DUPLICATE report stem {stem!r} — two files claim the same reviewer")
        fatal += 1

    found: list[Finding] = []
    reported: set[str] = set()
    for raw in args.reports:
        path = Path(raw)
        reviewer = path.stem
        try:
            text = path.read_text(encoding="utf-8")
        except READ_ERRORS as e:
            print(
                f"  CANNOT READ {raw} ({type(e).__name__}) — {reviewer} did not report"
            )
            fatal += 1
            continue
        found.extend(parse_report(text, reviewer))
        reported.add(reviewer)

    print(
        f"{_n(len(found), 'finding')} from {_n(len(args.reports), 'reviewer')}"
        f" over {_n(len(blocks), 'block')}\n"
    )

    # ⚠ DECLARED, the way this repo names a population everywhere else. Without
    # --reviewers, "every reviewer" means "every file I was handed", so a
    # reviewer that reported nothing at all passes unseen.
    if args.reviewers:
        expected = {a.strip() for a in args.reviewers.split(",") if a.strip()}
        for reviewer in sorted(expected - reported):
            print(
                f"  NO REPORT from reviewer {reviewer!r} — a missing report is the"
                " easier version of a fabricated one. --reviewers is matched against"
                f" each report file's STEM, so a report for {reviewer!r} must be"
                f" named {reviewer}.md"
            )
            fatal += 1
    else:
        print(
            "⚠ --reviewers not given: whether every expected reviewer reported was"
            " NOT checked.\n"
        )

    gaps = coverage_gaps(all_blocks, reported, found)
    if gaps:
        print("COVERAGE GAPS - indices no reviewer accounted for:")
        for reviewer, missing in sorted(gaps.items()):
            shown = ", ".join(str(n) for n in missing[:20])
            more = f" (+{len(missing) - 20} more)" if len(missing) > 20 else ""
            print(
                f"  {reviewer}: {_n(len(missing), 'block')} unaccounted — {shown}{more}"
            )
            fatal += 1
        print()

    for f in found:
        if f.block < 0:
            print(f"  MALFORMED {f.reviewer}: {f.finding}")
            fatal += 1
            continue
        if not 1 <= f.block <= len(blocks):
            print(
                f"  BLOCK {f.block} {f.reviewer}: out of range for a"
                f" {_n(len(blocks), 'block')} census"
            )
            fatal += 1
            continue
        if f.verdict not in VERDICTS:
            print(
                f"  BLOCK {f.block} {f.reviewer}: {f.verdict!r} is not a verdict"
                f" ({', '.join(VERDICTS)})"
            )
            fatal += 1
        problem = evidence_problem(f, repo)
        if problem:
            print(f"  BLOCK {f.block} {f.reviewer}: {problem}")
            fatal += 1
        loc_problem = location_problem(f, repo)
        if loc_problem:
            print(f"  BLOCK {f.block} {f.reviewer}: {loc_problem}")
            fatal += 1
        payload = payload_problem(f)
        if payload:
            print(f"  BLOCK {f.block} {f.reviewer}: {payload}")
            fatal += 1

    clash = contradictions(found)
    if clash:
        print(f"\nRE-REVIEW — drop against correct/patch on: {clash}")
        print(
            "  Not a tie-break. Send the block back; the synthesis order"
            " must not decide it."
        )

    # A block stands only when EVERY reviewer that ran returned `clean` on it.
    # Coverage gaps and out-of-range indices are already fatal above, so "no
    # reviewer ruled on it" and "every reviewer returned `clean`" are the same
    # set here and this subtraction is exact.
    ran = sorted(reported | {f.reviewer for f in found})
    ruled = {
        f.block for f in found if f.verdict != "clean" and 1 <= f.block <= len(blocks)
    }
    stands = sorted(all_blocks - ruled)
    print(
        f"\nSTANDS UNCHANGED: {_n(len(stands), 'block')} — clean from all"
        f" {_n(len(ran), 'reviewer')} that ran"
    )
    print(f"NEEDS A RULING:   {_n(len(ruled), 'block')}")
    if gaps:
        print("  ⚠ counts above are provisional: coverage is incomplete.")

    if fatal:
        print(f"\n{_n(fatal, 'problem')}. Resolve or send back before stage 5 rules.")
        return 1
    if clash:
        # ⚠ A contradiction is counted apart from the fatal checks: `drop`
        # against `correct` is a re-review, and both records are well formed.
        # The closing line still has to say so -- printing "send the block back"
        # and then "Stage 5 may rule" four lines later made the summary
        # contradict its own body at exit 0.
        print(
            f"\nEvery finding is admissible. {_n(len(clash), 'block')} still OUT"
            " for re-review — stage 5 may rule on the rest."
        )
        return 0
    print("\nEvery finding is admissible. Stage 5 may rule.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
