"""Stage 5's gate: join four reviewers' reports against the census.

    python verdicts.py --census census.json --level full --repo D <report>...

Checks the task agent was asked to perform by hand, every one mechanical:

  COVERAGE      every census index accounted for, by every angle that ran
  EVIDENCE      each finding's citation resolves, and says what was quoted
  LOCATION      the prose citation resolves too -- checked the same way
  PAYLOAD       the verdict carries what its row of the table requires
  LEVEL         the verdict is one this run's level carries
  CONTRADICTION `drop` against `correct`/`patch` on one block -- a re-review
  STANDS        blocks every angle that ran returned clean on
  ANGLE         (only with `--angles`) every expected reviewer actually reported

⚠ Exits nonzero on a coverage gap or an unverifiable citation. Measured: one
graded run had FABRICATED 5 of its 7 reviewer reports and did not notice until
asked to grade itself. A report is not evidence that a file was read.

⚠ It cannot tell a correct verdict from an incorrect one. It tells you which
findings are ADMISSIBLE. Ruling remains stage 5's, and the synthesis order in
SKILL.md is unchanged.

⚠ `--angles` is OPTIONAL, and its absence is announced, not swallowed: without
it, a reviewer that never reported at all is invisible to this tool -- the
easier version of the fabrication this whole script exists to catch.
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
    "reanchor",
    "split",
)

# What each level ADDS to the one above it, per SKILL.md's level table.
LEVELS = {
    "fact-check": {"correct", "query", "clean"},
    "line": {"correct", "query", "clean", "drop", "move", "reanchor", "split", "add"},
    "full": set(VERDICTS),
    "proof": set(),
}

RECORD = re.compile(r"^---\s*FINDING\s*$(.*?)^---\s*$", re.M | re.S)
# Counts "--- FINDING" OPENERS on their own, independent of whether a closing
# "---" was ever found. A first record missing its close makes RECORD's
# non-greedy search skip straight past the second record's opener (it is not a
# bare "---" line) and swallow both into one match -- the second record's
# fields silently overwrite the first's and a finding vanishes with no output.
# Comparing this count against RECORD's match count is how that is caught.
OPENER = re.compile(r"^---\s*FINDING\s*$", re.M)
FIELD = re.compile(
    r"^\s*(BLOCK|VERDICT|LOCATION|EVIDENCE|SUMMARY|FINDING|CHANGE)\s+(.*)$"
)
# ⚠ `[ \t]`, never `\s`. `\s` matches a newline, and inside a greedy character
# class under re.MULTILINE that let a CLEAN line's range swallow whatever the
# NEXT line held -- "CLEAN 1-9" followed by a stray "50" parsed as one range
# "1-950" and declared 950 blocks clean. A wrapped CLEAN line must fail LOUD
# (an unaccounted block is a coverage gap) rather than SILENT (a false clean).
CLEAN_LINE = re.compile(r"^[ \t]*CLEAN[ \t]+([\d,\- \t]+)$", re.M)
# `file:line` or `file:start-end`, shared by EVIDENCE and LOCATION -- a
# fabricated prose location is exactly as inadmissible as a fabricated
# citation once both are resolved the same way.
CITE = re.compile(r"^(.+?):(\d+)(?:-(\d+))?$")

# How far from the cited line the quoted text may sit. Prose wraps and code
# moves; a hard equality would reject honest citations, and a wide window would
# accept a fabricated one.
EVIDENCE_WINDOW = 3

# A needle shorter than this could match almost any file by accident --
# `SUMMARY "..." || e` passed against nearly anything. The forcing function
# only forces if the quote is long enough to have required reading the line.
MIN_NEEDLE = 12


@dataclass
class Finding:
    """One reviewer's ruling on one census block."""

    angle: str
    block: int
    verdict: str
    location: str
    evidence: str
    summary: str
    finding: str
    change: str


def _n(count: int, noun: str) -> str:
    """`"1 block"`, `"2 blocks"` -- this output decides whether an agent proceeds."""
    return f"{count} {noun}" if count == 1 else f"{count} {noun}s"


def _malformed(angle: str, why: str) -> Finding:
    """A record that cannot be attributed to any real block.

    `block=-1` is the sentinel `main()` treats as fatal on sight, whatever the
    reason -- a missing BLOCK, an unparseable CLEAN range, or a record whose
    closing "---" was never found.
    """
    return Finding(
        angle=angle,
        block=-1,
        verdict="malformed",
        location="",
        evidence="",
        summary="",
        finding=why,
        change="",
    )


def _expand(ranges: str) -> tuple[set[int], list[str]]:
    """`"1-3,7"` to `({1, 2, 3, 7}, [])`. Unparseable parts are RETURNED, not dropped.

    A range list that does not parse is a malformed record, not an empty one.
    `"9-2"` and `"1820-45"` are reversed; `"0-3"` starts below the 1-based
    census floor. Each is reported by name rather than silently vanishing (the
    old failure) or silently admitting an out-of-range index (the newer one).
    """
    out: set[int] = set()
    bad: list[str] = []
    for part in re.sub(r"[ \t]+", "", ranges).split(","):
        if not part:
            continue
        if "-" in part:
            lo, _, hi = part.partition("-")
            if lo.isdecimal() and hi.isdecimal() and 1 <= int(lo) <= int(hi):
                out.update(range(int(lo), int(hi) + 1))
            else:
                bad.append(part)
        elif part.isdecimal() and int(part) >= 1:
            out.add(int(part))
        else:
            bad.append(part)
    return out, bad


def parse_report(text: str, angle: str) -> tuple[list[Finding], set[int]]:
    """Findings and clean-block indices from one reviewer's report.

    Args:
        text: the report as the reviewer returned it. Prose around the records
            is ignored, so a reviewer may still explain itself.
        angle: the reviewer's name, attached to every finding it produced.

    Returns:
        The parsed findings, and the set of indices declared clean by range.
    """
    found: list[Finding] = []
    bodies = RECORD.findall(text)
    openers = len(OPENER.findall(text))
    if openers != len(bodies):
        found.append(
            _malformed(
                angle,
                f"{_n(openers, 'FINDING opener')} but"
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
                    angle=angle,
                    block=int(raw_block),
                    verdict=fields.get("VERDICT", "").strip().lower(),
                    location=fields.get("LOCATION", ""),
                    evidence=fields.get("EVIDENCE", ""),
                    summary=fields.get("SUMMARY", ""),
                    finding=fields.get("FINDING", ""),
                    change=fields.get("CHANGE", ""),
                )
            )
        else:
            found.append(_malformed(angle, "a record with no BLOCK index"))

    clean: set[int] = set()
    for ranges in CLEAN_LINE.findall(text):
        expanded, bad = _expand(ranges)
        clean |= expanded
        for part in bad:
            found.append(_malformed(angle, f"CLEAN range {part!r} does not parse"))
    return found, clean


def coverage_gaps(
    all_blocks: set[int], clean: dict[str, set[int]], found: list[Finding]
) -> dict[str, list[int]]:
    """Indices each angle never accounted for. A gap is not a pass."""
    by_angle: dict[str, set[int]] = defaultdict(set)
    for f in found:
        by_angle[f.angle].add(f.block)
    gaps: dict[str, list[int]] = {}
    for angle in set(list(clean) + list(by_angle)):
        missing = sorted(all_blocks - by_angle[angle] - clean.get(angle, set()))
        if missing:
            gaps[angle] = missing
    return gaps


def allowed(verdict: str, level: str) -> bool:
    """Does this run's level carry this verdict?"""
    return verdict in LEVELS.get(level, set())


def payload_problem(f: Finding) -> str | None:
    """What the verdict's required payload is missing, or None."""
    change = f.change.lower()
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
    if f.verdict == "reanchor" and not change.strip():
        return "reanchor needs the declaration it constrains"
    if f.verdict == "split" and change.count("/") < 1:
        return "split needs each fragment and its own anchor"
    if f.verdict not in ("clean",) and not f.change.strip():
        return f"{f.verdict} carries no payload — the judgement was handed back"
    return None


def _resolve_lines(cite: str, repo: Path) -> tuple[Path, int, int, list[str]] | str:
    """Resolve a `file:line` or `file:start-end` citation, or say why not.

    Shared by EVIDENCE and LOCATION: both are inadmissible on exactly the same
    grounds -- an unparseable citation, a file that is not there, or a line
    number past the end of it (or below 1, which no file has).

    Returns:
        `(path, start, end, lines)` when it resolves, else the problem string.
    """
    m = CITE.match(cite.strip())
    if not m:
        return f"{cite!r} is not file:line or file:start-end"
    rel, start_s, end_s = m.group(1), m.group(2), m.group(3)
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

    Reads the cited line out of the file and looks for the SUMMARY's right half
    within a few lines of it. A finding whose evidence is not there is not a
    finding — the report is not evidence that the file was read.
    """
    if f.verdict == "clean":
        return None
    resolved = _resolve_lines(f.evidence, repo)
    if isinstance(resolved, str):
        return f"EVIDENCE {resolved}"
    _target, lineno, _end, lines = resolved
    _, _, right = f.summary.partition("||")
    needle = " ".join(right.split()).strip().strip('"')
    if not needle:
        return "SUMMARY has no right half — nothing was checked against the code"
    if len(needle) < MIN_NEEDLE:
        return (
            f"SUMMARY's right half {needle!r} is too short to have been "
            "checked against the code"
        )
    lo = max(0, lineno - 1 - EVIDENCE_WINDOW)
    window = " ".join(
        " ".join(ln.split()) for ln in lines[lo : lineno + EVIDENCE_WINDOW]
    )
    head = needle[:40]
    if head.lower() not in window.lower():
        return f"quoted evidence not found near {f.evidence}: {head!r}"
    return None


def location_problem(f: Finding, repo: Path) -> str | None:
    """Why this finding's LOCATION cannot be trusted, or None.

    Checked with the same `file:line` resolution as EVIDENCE. A fabricated
    prose location used to be admissible while a fabricated citation was not
    — the same report is not evidence that either half was read.
    """
    if f.verdict == "clean":
        return None
    resolved = _resolve_lines(f.location, repo)
    if isinstance(resolved, str):
        return f"LOCATION {resolved}"
    return None


def contradictions(found: list[Finding]) -> list[int]:
    """Blocks where one angle says delete and another says fix. Re-review."""
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
    ap.add_argument("reports", nargs="+", help="one report file per angle")
    ap.add_argument("--census", required=True, help="census.py --json output")
    ap.add_argument("--level", default="full", choices=sorted(LEVELS))
    ap.add_argument("--repo", default=".", help="repo root for evidence resolution")
    ap.add_argument(
        "--angles",
        default="",
        help="comma-separated expected angle names; one missing a report is fatal",
    )
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    blocks = json.loads(Path(args.census).read_text(encoding="utf-8"))
    all_blocks = set(range(1, len(blocks) + 1))

    fatal = 0

    # ⚠ Refused ALWAYS, not just when --angles is given: `clean[angle] = cl`
    # overwrites, so two report files with the same stem would otherwise
    # silently replace one angle's coverage with another's.
    stems = [Path(r).stem for r in args.reports]
    for stem in sorted({s for s, n in Counter(stems).items() if n > 1}):
        print(f"  DUPLICATE report stem {stem!r} — two files claim the same angle")
        fatal += 1

    found: list[Finding] = []
    clean: dict[str, set[int]] = {}
    for raw in args.reports:
        path = Path(raw)
        angle = path.stem
        try:
            text = path.read_text(encoding="utf-8")
        except READ_ERRORS as e:
            print(f"  CANNOT READ {raw} ({type(e).__name__}) — {angle} did not report")
            fatal += 1
            continue
        got, cl = parse_report(text, angle)
        found.extend(got)
        if angle not in clean:  # first file for a stem wins; a dupe is fatal above
            clean[angle] = cl

    print(
        f"{_n(len(found), 'finding')} from {_n(len(args.reports), 'angle')}"
        f" over {_n(len(blocks), 'block')}\n"
    )

    # ⚠ Declared, never inferred -- this repo's rule everywhere else. Without
    # --angles, a reviewer that never reported at all is invisible: "every
    # angle" silently means "every file I was handed," which is the easier
    # version of the fabrication this tool exists to catch.
    if args.angles:
        expected = {a.strip() for a in args.angles.split(",") if a.strip()}
        for angle in sorted(expected - set(clean)):
            print(
                f"  NO REPORT from angle {angle!r} — a missing report is the"
                " easier version of a fabricated one"
            )
            fatal += 1
    else:
        print(
            "⚠ --angles not given: whether every expected reviewer reported was"
            " NOT checked.\n"
        )

    gaps = coverage_gaps(all_blocks, clean, found)
    if gaps:
        print("COVERAGE GAPS — a block nobody mentioned is a gap, not a pass:")
        for angle, missing in sorted(gaps.items()):
            shown = ", ".join(str(n) for n in missing[:20])
            more = f" (+{len(missing) - 20} more)" if len(missing) > 20 else ""
            print(f"  {angle}: {_n(len(missing), 'block')} unaccounted — {shown}{more}")
            fatal += 1
        print()

    for f in found:
        if f.block < 0:
            print(f"  MALFORMED {f.angle}: {f.finding}")
            fatal += 1
            continue
        if not 1 <= f.block <= len(blocks):
            print(
                f"  BLOCK {f.block} {f.angle}: out of range for a"
                f" {_n(len(blocks), 'block')} census"
            )
            fatal += 1
            continue
        if f.verdict not in VERDICTS:
            print(f"  BLOCK {f.block} {f.angle}: {f.verdict!r} is not one of the nine")
            fatal += 1
        elif not allowed(f.verdict, args.level):
            print(
                f"  BLOCK {f.block} {f.angle}: {f.verdict} not carried at {args.level}"
            )
            fatal += 1
        problem = evidence_problem(f, repo)
        if problem:
            print(f"  BLOCK {f.block} {f.angle}: {problem}")
            fatal += 1
        loc_problem = location_problem(f, repo)
        if loc_problem:
            print(f"  BLOCK {f.block} {f.angle}: {loc_problem}")
            fatal += 1
        payload = payload_problem(f)
        if payload:
            print(f"  BLOCK {f.block} {f.angle}: {payload}")
            fatal += 1

    clash = contradictions(found)
    if clash:
        print(f"\nRE-REVIEW — drop against correct/patch on: {clash}")
        print(
            "  Not a tie-break. Send the block back; the synthesis order"
            " must not decide it."
        )

    # A block stands only when EVERY angle that ran returned clean on it. With
    # coverage gaps and out-of-range indices already reported as fatal above,
    # "no angle ruled on it" and "every angle cleaned it" are the same set --
    # so this subtraction is the clean-arithmetic, not an approximation of it.
    ran = sorted(set(clean) | {f.angle for f in found})
    ruled = {
        f.block for f in found if f.verdict != "clean" and 1 <= f.block <= len(blocks)
    }
    stands = sorted(all_blocks - ruled)
    print(
        f"\nSTANDS UNCHANGED: {_n(len(stands), 'block')} — clean from all"
        f" {_n(len(ran), 'angle')} that ran"
    )
    print(f"NEEDS A RULING:   {_n(len(ruled), 'block')}")
    if gaps:
        print("  ⚠ counts above are provisional: coverage is incomplete.")

    if fatal:
        print(f"\n{_n(fatal, 'problem')}. Resolve or send back before stage 5 rules.")
        return 1
    print("\nEvery finding is admissible. Stage 5 may rule.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
