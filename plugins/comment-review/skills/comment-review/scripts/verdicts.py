"""Stage 5's gate: join four reviewers' reports against the census.

    python verdicts.py --census census.json --repo D <report>...

Checks the task agent was asked to perform by hand, every one mechanical:

  COVERAGE      every census index accounted for, by every reviewer that ran
  EVIDENCE      each finding's citation resolves, and the QUOTE is really there
  LOCATION      the prose citation resolves too -- checked the same way
  PAYLOAD       the verdict carries what its row of the table requires
  CONTRADICTION `drop` or `move` against `correct`/`patch` -- a re-review.
                Counted apart from the fatal checks, and named in the closing
                line so the summary says which blocks are still out
  STANDS        blocks every reviewer that ran returned clean on
  SCOPED OUT    blocks nobody found anything in and nobody certified
  WORK LIST     each block needing a ruling, with the verdicts held on it
  CODE CONCERNS carried through, attributed, gated by nothing
  REVIEWER      every report is named for a PUBLISHED role, and (only with
                `--reviewers`) every expected reviewer actually reported

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

from vocabulary import Reviewer

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

# What a contradiction IS: one role ruling on where the prose lives, another on
# what it says. Named rather than inlined so the join's message and this test
# cannot drift apart.
RELOCATES = frozenset({"drop", "move"})
RULES_ON_TEXT = frozenset({"correct", "patch"})

# ⚠⚠ The THREE shapes `reviewer-brief.md` says reach `query`, and a query must
# NAME the one it is. A closed set beats guessing at free text: the shape decides
# whether the block is work (the author must answer) or a boundary report (the
# role is saying which scope owns it), and that is not something to infer from
# whether a sentence happens to contain the word "resolved".
OUT_OF_ROLE = "outside my role"
QUERY_SHAPES = (OUT_OF_ROLE, "outside the checkout", "outside the code")

RECORD = re.compile(r"^---\s*RECORD\s*$(.*?)^---\s*$", re.M | re.S)
# Counts "--- RECORD" OPENERS on their own, independent of whether a closing
# "---" was ever found. A first record missing its close makes RECORD's
# non-greedy search skip straight past the second record's opener (it is not a
# bare "---" line) and swallow both into one match -- the second record's
# fields silently overwrite the first's and a finding vanishes with no output.
# Comparing this count against RECORD's match count is how that is caught.
OPENER = re.compile(r"^---\s*RECORD\s*$", re.M)
# The section `reviewer-brief.md` sends code problems to. Matched to the next
# heading or the end, because it is the LAST section of a report by contract.
CODE_CONCERNS = re.compile(r"^#+\s*CODE CONCERNS\s*$(.*?)(?=^#|\Z)", re.M | re.S | re.I)
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

# The floor on a QUOTE, and it is ONE: a zero-length quote is not a quote. It was
# 12, which refused `x = 1`, `pass` and `return` -- real short lines whose only
# route through was to quote MORE than was read.
MIN_NEEDLE = 1

# What an `add`'s PAYLOAD must carry: a SIDE, and the anchor NAMED.
#
# ⚠ Backticks are the repo's own citation form -- the brief says cite by symbol
# or path, never by line number, and every record in it writes a symbol that way.
# So "named" is checkable without guessing which token is an identifier.
ANCHOR_SIDE = re.compile(r"\b(above|below|before|after)\b", re.I)
ANCHOR_NAME = re.compile(r"`[^`\s][^`]*`")

# What a `query`'s PAYLOAD must name: a check that was attempted, and the thing
# that would settle the claim.
#
# ⚠ A SHAPE check: it removes the query that names no check at all, and the
# word "grepped" passes it. A query owes EVIDENCE and a QUOTE on top of this --
# `evidence_problem` exempts `clean` alone.
#
# Matched on WORD BOUNDARIES. As substrings, "ran" hit *b**ran**ch*,
# *****ran***ge* and *t**ran**sfer*, and "settle" hit *un**settle**d*, so
# ordinary English naming no check passed while an honest query worded with
# "requires" / "resolves" / "determined by" was refused. `grep` is the one
# deliberate exception, left unanchored on its left so "ripgrep" counts:
# English words carry "ran" and "read" by accident, and "grep" they do not.
#
# ⚠⚠ The vocabulary is DERIVED from the verbs a reviewer is instructed in, never
# invented. The brief and the four agent files say resolve, enumerate, verify,
# list, trace, follow, compare, read, grep, count and open, so every one is here.
# Measured: a run refused 65 of 65 module-context queries whose CHANGE read
# "resolved the enclosing definition at ..." -- `resolve` was in QUERY_SETTLES
# and missing here, so reports that were substantively complete were lexically
# refused, and the only route through was to reword another agent's report.
QUERY_ATTEMPTED = re.compile(
    r"\bran\b|\bcheck\w*|grep\w*|\bread\w*|\bsearch\w*|\bopen\w*|\bcount\w*"
    r"|\blook\w*|\bresolv\w*|\benumerat\w*|\bverif\w*|\btrac(ed|ing|e)\b"
    r"|\bfollow\w*|\bcompar\w*|\blisted\b|\binspect\w*",
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


def parse_report(text: str, reviewer: str) -> tuple[list[Finding], list[str]]:
    """Every record in one reviewer's report, `clean` included.

    Args:
        text: the report as the reviewer returned it. Prose around the records
            is ignored, so a reviewer may still explain itself.
        reviewer: the editorial role's name, attached to every finding it made.

    Returns:
        `(findings, malformed)`. Coverage is computed from the findings alone --
        a block a reviewer never recorded is a block it never accounted for.
        `malformed` holds one sentence per record that names no block, which
        `main()` reports and counts fatal.

    ⚠ A malformed record used to be a `Finding` carrying `block=-1`, and its
    reason was stuffed into `FINDING`. That made one field mean two things,
    distinguished by a sentinel in another, and every consumer had to filter on
    the sentinel before reading anything. They are separate now, so `FINDING`
    holds a reviewer's clause and only that.
    """
    found: list[Finding] = []
    malformed: list[str] = []
    bodies = RECORD.findall(text)
    openers = len(OPENER.findall(text))
    if openers != len(bodies):
        malformed.append(
            f"{_n(openers, 'RECORD opener')} but"
            f" {_n(len(bodies), 'closed record')}"
            " -- an unterminated record swallows the next one"
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
            malformed.append("a record with no BLOCK index")
    return found, malformed


def code_concerns(text: str) -> list[str]:
    """The `CODE CONCERNS` lines a report carries, if it has the section.

    ⚠ NOT a verdict and NOT gated. `reviewer-brief.md` sends a code problem here
    -- "one line each ... with no verdict" -- because a reviewer that opens the
    code to settle a comment will sometimes find the code wrong. Nothing here
    reads them for admissibility; they are carried so they reach the author with
    everything else, which is the half the brief could not do on its own.

    Everything after the heading is taken, one finding per non-blank line, until
    the next heading or the end.
    """
    m = CODE_CONCERNS.search(text)
    if not m:
        return []
    out: list[str] = []
    for line in m.group(1).splitlines():
        line = line.strip().lstrip("-*+ ").strip()
        if line.startswith("#"):
            break
        if line:
            out.append(line)
    return out


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

    `query` is checked in the most detail, because it is the one verdict whose
    payload has a fixed shape the brief spells out.
    """
    # ⚠ Every verdict but `clean` states WHY, and `FINDING` is the field that
    # holds it. It went unchecked while it doubled as a diagnostic slot for
    # malformed records; those are separate now, so it can be required.
    if f.verdict != "clean" and not f.finding.strip():
        return f"{f.verdict} states no FINDING — the reason the verdict was made"
    change = f.change.lower()
    if f.verdict == "query":
        named = [s for s in QUERY_SHAPES if s in change]
        if not named:
            return (
                "query must NAME its shape — one of "
                + ", ".join(f"'{s}'" for s in QUERY_SHAPES)
                + " — so the reason is attached to the ruling"
            )
        # ⚠ The shape is REMOVED before the word search. `check\w*` matches
        # "checkout", so "outside the checkout" would satisfy the attempted-check
        # test by naming itself -- a query could pass by declaring its shape and
        # doing nothing.
        for shape in named:
            change = change.replace(shape, " ")
        if not QUERY_ATTEMPTED.search(change):
            return (
                "query needs the check you ATTEMPTED — a query naming none"
                " hands the judgement back"
            )
        if not QUERY_SETTLES.search(change):
            return "query needs what WOULD settle the claim"
    if f.verdict == "correct" and not ("false:" in change and "true:" in change):
        return "correct needs a true/false pair in CHANGE"
    if f.verdict == "add":
        # ⚠ The brief asks for "the text AND its anchor — which code, above or
        # below": a NAMED site and a side. This used to accept the bare word
        # "anchor", so `CHANGE  add an anchor comment` passed while
        # `CHANGE  above `retry_budget`` failed for not saying "anchor".
        if not ANCHOR_SIDE.search(change):
            return "add needs a side — is the text above or below the anchor"
        if not ANCHOR_NAME.search(f.change):
            return (
                "add needs the anchor NAMED in backticks — which declaration,"
                " not the word 'anchor'"
            )
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

    ⚠ The only floor is `MIN_NEEDLE`, which is ONE. What binds is that the quote
    be THERE: a short needle absent from the file is refused like any other.

    ⚠ QUOTE is checked, and `SUMMARY`'s right half is the DERIVED statement —
    *"31 callers, all under tests/"* — which is the reviewer's own sentence, so
    checking it here made every counted claim structurally inadmissible. The
    forcing function lands on a field that carries verbatim text alone.

    ⚠⚠ `query` is NOT exempt. `reviewer-brief.md` has always said a query
    "requires `EVIDENCE` and `QUOTE`(s), by construction -- this is where you
    looked", and this script waived both; Roy ruled the brief right on
    2026-08-16. Where you looked is a real line in the checkout on all three
    query shapes, so it resolves like any other citation. Only `clean` is
    exempt, because a `clean` reports no claim to cite.
    """
    if f.verdict == "clean":
        return None
    resolved = _resolve_lines(f.evidence, repo, allow_range=False)
    if isinstance(resolved, str):
        return f"EVIDENCE {resolved}"
    _target, lineno, _end, lines = resolved
    needle = " ".join(f.quote.split()).strip().strip('"')
    if len(needle) < MIN_NEEDLE:
        return f"no QUOTE — nothing was read out of {f.evidence}"
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


def declares_scope(f: Finding) -> bool:
    """A `query` saying the block is not this role's to read.

    Not a ruling: nothing is asked of the task agent, and the role is reporting
    the boundary it was told to report. Every other `query` IS work -- it names a
    claim nobody could settle, and the brief sends it to the author.
    """
    return f.verdict == "query" and OUT_OF_ROLE in f.change.lower()


def by_block(found: list[Finding]) -> dict[int, list[Finding]]:
    """Every finding, grouped by the block it rules on.

    This is what stage 5 works from: several roles rule on one block and the
    task agent emits ONE replacement, so the grouping IS the work list. It was
    computed inside `contradictions`, used for one boolean and dropped, leaving
    the agent to rebuild it from the report files by hand.

    Every finding here names a block, because a record that named none never
    became a `Finding` -- `parse_report` returns those separately.
    """
    out: dict[int, list[Finding]] = defaultdict(list)
    for f in found:
        out[f.block].append(f)
    return out


def contradictions(grouped: dict[int, list[Finding]]) -> list[int]:
    """Blocks where one role rules on the TEXT and another on WHERE it lives.

    `drop` against `correct`/`patch` is one role saying the sentence should not
    exist and another saying it should exist and be fixed. `move` against either
    is the same collision one step earlier: a claim is measured against the code
    it sits with, so a `correct` written at an anchor another role says is wrong
    was measured against the wrong code. Both go back for re-review.
    """
    return sorted(
        b
        for b, fs in grouped.items()
        if (RELOCATES & {f.verdict for f in fs})
        and (RULES_ON_TEXT & {f.verdict for f in fs})
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
    # ⚠⚠ ADDRESSABLE is not ACCOUNTABLE. Every interval between two lines of
    # code is a block, so an `add` -- a finding about prose that is MISSING --
    # has an index to cite instead of borrowing a neighbour's. Most of them hold
    # nothing, and a reviewer owes no record on an empty one: coverage is over
    # the blocks that HOLD PROSE. Measured: `census.py` over itself is 546
    # blocks, 48 of them prose. Owing a record on all 546 would make `CLEAN 1-N`
    # -- the cheapest fabrication there is -- nine parts out of ten true.
    all_blocks = {i for i, b in enumerate(blocks, 1) if b.get("kind") != "interval"}

    fatal = 0

    # ⚠ Refused on every run, `--reviewers` or not: a reviewer is keyed by its
    # report's stem, so two files with the same stem put one reviewer's
    # coverage in place of the other's.
    stems = [Path(r).stem for r in args.reports]
    expected = {a.strip() for a in args.reviewers.split(",") if a.strip()}
    for stem in sorted({s for s, n in Counter(stems).items() if n > 1}):
        print(f"  DUPLICATE report stem {stem!r} — two files claim the same reviewer")
        fatal += 1

    # ⚠ A stem was taken as a role name on sight, so `ownershp-context.md` was
    # accepted as a reviewer called `ownershp-context` and every line below
    # named a role that does not exist. `Reviewer` is the published list.
    published = {r.value for r in Reviewer}
    for name in sorted(set(stems) | expected):
        if name not in published:
            print(
                f"  UNKNOWN reviewer {name!r} — not one of"
                f" {', '.join(sorted(published))}"
            )
            fatal += 1

    found: list[Finding] = []
    reported: set[str] = set()
    concerns: list[tuple[str, str]] = []
    malformed: list[tuple[str, str]] = []
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
        records, unattributable = parse_report(text, reviewer)
        found.extend(records)
        malformed.extend((reviewer, why) for why in unattributable)
        for line in code_concerns(text):
            concerns.append((reviewer, line))
        reported.add(reviewer)

    print(
        f"{_n(len(found), 'finding')} from {_n(len(args.reports), 'reviewer')}"
        f" over {_n(len(all_blocks), 'prose block')}"
        f" ({_n(len(blocks), 'block')} in the census, the rest empty intervals"
        " an `add` may cite)\n"
    )

    # ⚠ DECLARED, the way this repo names a population everywhere else. Without
    # --reviewers, "every reviewer" means "every file I was handed", so a
    # reviewer that reported nothing at all passes unseen.
    if args.reviewers:
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

    for reviewer, why in malformed:
        print(f"  MALFORMED {reviewer}: {why}")
        fatal += 1

    for f in found:
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

    grouped = by_block(found)
    clash = contradictions(grouped)
    if clash:
        print(f"\nRE-REVIEW — drop/move against correct/patch on: {clash}")
        print(
            "  Not a tie-break. Send the block back; the synthesis order"
            " must not decide it."
        )

    # ⚠⚠ THREE STATES, NOT TWO. A block covered only by `clean` and out-of-role
    # queries is neither: no role certified it -- module-context returns `query`
    # rather than `clean` so it does not certify what it never read -- and
    # nothing is asked of stage 5 either. Counting those as work buried 76 real
    # verdicts inside 1159 on a measured run.
    ran = sorted(reported | {f.reviewer for f in found})
    in_range = [f for f in found if 1 <= f.block <= len(blocks)]
    ruled = {
        f.block for f in in_range if f.verdict != "clean" and not declares_scope(f)
    }
    scoped_out = {f.block for f in in_range if declares_scope(f)} - ruled
    stands = sorted(all_blocks - ruled - scoped_out)
    print(
        f"\nSTANDS UNCHANGED: {_n(len(stands), 'block')} — clean from all"
        f" {_n(len(ran), 'reviewer')} that ran"
    )
    print(f"NEEDS A RULING:   {_n(len(ruled), 'block')}")
    if scoped_out:
        print(
            f"NO FINDING, NOT CERTIFIED: {_n(len(scoped_out), 'block')} — every"
            " role that read it was `clean`, and at least one said it was outside"
            " its role. Nothing to rule; nothing certified either."
        )
    if gaps:
        print("  ⚠ counts above are provisional: coverage is incomplete.")

    # ⚠ The WORK LIST. Stage 5 holds several rulings per block and must emit ONE
    # replacement, so this grouping is what it works from -- and rebuilding it
    # from the report files by hand is the step this tool can do exactly and a
    # reader cannot.
    # ⚠ Withheld when anything is FATAL. The gate has just refused the report,
    # so a work list here reads as permission to start on it.
    out_for_rereview = set(clash)
    if ruled and not fatal:
        print("\nPER BLOCK — what you hold, in census order:")
        for b in sorted(ruled):
            marks = "  ".join(
                f"{f.verdict}({f.reviewer})"
                for f in sorted(grouped[b], key=lambda f: (f.verdict, f.reviewer))
                if f.verdict != "clean" and not declares_scope(f)
            )
            flag = "   ⚠ RE-REVIEW" if b in out_for_rereview else ""
            print(f"  {b:4d}  {marks}{flag}")

    # ⚠ Printed whether or not the gate refuses, and counted toward nothing. A
    # code problem is not a verdict, so it is neither admissible nor
    # inadmissible -- but a run that stops at stage 5 must still carry it, or the
    # defect dies with the refusal.
    if concerns:
        print(f"\nCODE CONCERNS — {_n(len(concerns), 'line')}, no verdict, not gated:")
        for reviewer, line in concerns:
            print(f"  {reviewer}: {line}")

    if fatal:
        print(f"\n{_n(fatal, 'problem')}. Resolve or send back before stage 5 rules.")
        return 1
    if clash:
        # ⚠ A contradiction is counted apart from the fatal checks: it is a
        # re-review, and both records are well formed.
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
