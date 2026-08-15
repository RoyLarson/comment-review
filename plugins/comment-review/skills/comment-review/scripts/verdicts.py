"""Stage 5's gate: join four reviewers' reports against the census.

    python verdicts.py --census census.json --level full --repo D <report>...

Six checks the task agent was asked to perform by hand, every one mechanical:

  COVERAGE      every census index accounted for, by every angle that ran
  EVIDENCE      each finding's citation resolves, and says what was quoted
  PAYLOAD       the verdict carries what its row of the table requires
  LEVEL         the verdict is one this run's level carries
  CONTRADICTION `drop` against `correct`/`patch` on one block -- a re-review
  STANDS        blocks every angle that ran returned clean on

⚠ Exits nonzero on a coverage gap or an unverifiable citation. Measured: one
graded run had FABRICATED 5 of its 7 reviewer reports and did not notice until
asked to grade itself. A report is not evidence that a file was read.

⚠ It cannot tell a correct verdict from an incorrect one. It tells you which
findings are ADMISSIBLE. Ruling remains stage 5's, and the synthesis order in
SKILL.md is unchanged.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
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
FIELD = re.compile(
    r"^\s*(BLOCK|VERDICT|LOCATION|EVIDENCE|SUMMARY|FINDING|CHANGE)\s+(.*)$"
)
CLEAN_LINE = re.compile(r"^\s*CLEAN\s+([\d,\s-]+)$", re.M)
CITE = re.compile(r"^(.+?):(\d+)$")

# How far from the cited line the quoted text may sit. Prose wraps and code
# moves; a hard equality would reject honest citations, and a wide window would
# accept a fabricated one.
EVIDENCE_WINDOW = 3


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


def _expand(ranges: str) -> set[int]:
    """`"1-3,7"` to `{1, 2, 3, 7}`."""
    out: set[int] = set()
    # ⚠ Strips ALL whitespace, not just spaces. CLEAN_LINE's capture group
    # includes `\s`, which is greedy enough to swallow the trailing newline
    # after the last digit -- `replace(" ", "")` alone left "2-3\n" un-stripped
    # and every range silently expanded to the empty set.
    for part in re.sub(r"\s+", "", ranges).split(","):
        if not part:
            continue
        if "-" in part:
            lo, _, hi = part.partition("-")
            if lo.isdigit() and hi.isdigit():
                out.update(range(int(lo), int(hi) + 1))
        elif part.isdigit():
            out.add(int(part))
    return out


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
    for body in RECORD.findall(text):
        fields: dict[str, str] = {}
        for line in body.splitlines():
            m = FIELD.match(line)
            if m:
                fields[m.group(1)] = m.group(2).strip()
        raw_block = fields.get("BLOCK", "")
        found.append(
            Finding(
                angle=angle,
                block=int(raw_block) if raw_block.isdigit() else -1,
                verdict=fields.get("VERDICT", "").strip().lower(),
                location=fields.get("LOCATION", ""),
                evidence=fields.get("EVIDENCE", ""),
                summary=fields.get("SUMMARY", ""),
                finding=fields.get("FINDING", ""),
                change=fields.get("CHANGE", ""),
            )
        )
    clean: set[int] = set()
    for ranges in CLEAN_LINE.findall(text):
        clean |= _expand(ranges)
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


def evidence_problem(f: Finding, repo: Path) -> str | None:
    """Why this finding's citation cannot be trusted, or None.

    Reads the cited line out of the file and looks for the SUMMARY's right half
    within a few lines of it. A finding whose evidence is not there is not a
    finding — the report is not evidence that the file was read.
    """
    if f.verdict == "clean":
        return None
    m = CITE.match(f.evidence.strip())
    if not m:
        return f"EVIDENCE {f.evidence!r} is not file:line"
    target, lineno = repo / m.group(1), int(m.group(2))
    if not target.is_file():
        return f"EVIDENCE {f.evidence} does not resolve to a file"
    try:
        lines = target.read_text(encoding="utf-8", errors="replace").splitlines()
    except READ_ERRORS as e:
        return f"EVIDENCE unreadable ({type(e).__name__})"
    if lineno > len(lines):
        return (
            f"EVIDENCE line {lineno} is past the end of {m.group(1)} "
            f"({len(lines)} lines)"
        )
    _, _, right = f.summary.partition("||")
    needle = " ".join(right.split()).strip().strip('"')
    if not needle:
        return "SUMMARY has no right half — nothing was checked against the code"
    lo = max(0, lineno - 1 - EVIDENCE_WINDOW)
    window = " ".join(
        " ".join(ln.split()) for ln in lines[lo : lineno + EVIDENCE_WINDOW]
    )
    head = needle[:40]
    if head.lower() not in window.lower():
        return f"quoted evidence not found near {f.evidence}: {head!r}"
    return None


def contradictions(found: list[Finding]) -> list[int]:
    """Blocks where one angle says delete and another says fix. Re-review."""
    by_block: dict[int, set[str]] = defaultdict(set)
    for f in found:
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
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    blocks = json.loads(Path(args.census).read_text(encoding="utf-8"))
    all_blocks = set(range(1, len(blocks) + 1))

    found: list[Finding] = []
    clean: dict[str, set[int]] = {}
    for raw in args.reports:
        path = Path(raw)
        angle = path.stem
        got, cl = parse_report(path.read_text(encoding="utf-8"), angle)
        found.extend(got)
        clean[angle] = cl

    print(
        f"{len(found)} findings from {len(args.reports)} angles"
        f" over {len(blocks)} blocks\n"
    )

    fatal = 0
    gaps = coverage_gaps(all_blocks, clean, found)
    if gaps:
        print("COVERAGE GAPS — a block nobody mentioned is a gap, not a pass:")
        for angle, missing in sorted(gaps.items()):
            shown = ", ".join(str(n) for n in missing[:20])
            more = f" (+{len(missing) - 20} more)" if len(missing) > 20 else ""
            print(f"  {angle}: {len(missing)} unaccounted — {shown}{more}")
            fatal += 1
        print()

    for f in found:
        if f.block < 0:
            print(f"  MALFORMED {f.angle}: a record with no BLOCK index")
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
        payload = payload_problem(f)
        if payload:
            print(f"  BLOCK {f.block} {f.angle}: {payload}")

    clash = contradictions(found)
    if clash:
        print(f"\nRE-REVIEW — drop against correct/patch on: {clash}")
        print(
            "  Not a tie-break. Send the block back; the synthesis order"
            " must not decide it."
        )

    # A block stands only when EVERY angle that ran returned clean on it. With
    # coverage gaps already reported as fatal above, "no angle ruled on it" and
    # "every angle cleaned it" are the same set -- so this subtraction is the
    # clean-arithmetic, not an approximation of it.
    ran = sorted(set(clean) | {f.angle for f in found})
    ruled = {f.block for f in found if f.verdict != "clean"}
    stands = sorted(all_blocks - ruled)
    print(
        f"\nSTANDS UNCHANGED: {len(stands)} blocks — clean from all"
        f" {len(ran)} angles that ran"
    )
    print(f"NEEDS A RULING:   {len(ruled)} blocks")
    if gaps:
        print("  ⚠ counts above are provisional: coverage is incomplete.")

    if fatal:
        print(f"\n{fatal} inadmissible. Resolve or send back before stage 5 rules.")
        return 1
    print("\nEvery finding is admissible. Stage 5 may rule.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
