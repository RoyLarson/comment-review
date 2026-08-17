"""Score one candidate SKILL.md by what its review pass actually found.

Fitness is RECALL against the prose blocks that really changed, with a
precision term so a candidate cannot win by reporting every line. A finding
counts as a hit when its line falls within (or within `--slack` lines of) a
ground-truth block; each block can be hit only once, so duplicates do not pay.

    uv run python score.py --gt gt.json --findings f.json --slice slice.txt

`findings.json` is `[{"file": "...", "line": 123}, ...]` -- the shape every
reviewer already returns.
"""

import argparse
import json
import sys
from pathlib import Path


def _max_hits(eligible: list[list[tuple[str, int]]]) -> int:
    """The most ground-truth blocks these findings can cover between them.

    !! THE COUNT MUST NOT DEPEND ON THE ORDER of the candidate's findings, and
    picking a block per finding cannot deliver that however the block is
    chosen: whichever finding is considered first takes a block a later one may
    have been the only claimant for. Closest-first narrowed the cases and did
    not remove them -- measured 2026-08-17 on the committed file, with
    gt {"a.py": [[10,12],[13,15]]} and --slack 3, findings [12, 9] scored f2
    0.5 and the same two as [9, 12] scored 1.0. Two candidates that found
    identical things were given different fitness, which ranks the GA on the
    JSON's line order.

    A MAXIMUM MATCHING has no such choice to make: its cardinality is a
    property of the eligibility graph, so every ordering of the same findings
    yields the same number. This is Kuhn's algorithm -- offer each finding a
    block, and when the block is taken, ask its holder to move.

    Args:
        eligible: per finding, the blocks it could be counted against, nearest
            first. The order within a row breaks ties between matchings of
            equal size; it cannot change how many there are.

    Returns:
        How many distinct blocks are covered.
    """
    owner: dict[tuple[str, int], int] = {}

    def claim(u: int, tried: set[tuple[str, int]]) -> bool:
        # `tried` bounds the recursion at one entry per BLOCK, so the depth is
        # the number of ground-truth blocks and not the number of findings.
        for block in eligible[u]:
            if block in tried:
                continue
            tried.add(block)
            if block not in owner or claim(owner[block], tried):
                owner[block] = u
                return True
        return False

    return sum(claim(u, set()) for u in range(len(eligible)))


def main() -> int:
    """Score one candidate's findings against the ground truth."""
    # A Windows console is cp1252; one non-ASCII glyph in a report kills the
    # run, and `--help` prints this module's docstring, which holds an em dash.
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--gt", required=True)
    ap.add_argument("--findings", required=True)
    ap.add_argument("--slice", default="", help="file listing the paths in scope")
    ap.add_argument("--slack", type=int, default=3)
    ap.add_argument("--name", default="candidate")
    args = ap.parse_args()

    gt: dict[str, list[list[int]]] = json.loads(
        Path(args.gt).read_text(encoding="utf-8")
    )
    if args.slice:
        scope = {
            ln.strip()
            for ln in Path(args.slice).read_text(encoding="utf-8").splitlines()
            if ln.strip()
        }
        gt = {k: v for k, v in gt.items() if k in scope}

    raw = json.loads(Path(args.findings).read_text(encoding="utf-8"))
    findings = raw.get("findings", raw) if isinstance(raw, dict) else raw

    total = sum(len(v) for v in gt.values())
    # ! The same `file:line` may be offered many times; it is one finding.
    seen_lines: set[tuple[str, int]] = set()
    eligible: list[list[tuple[str, int]]] = []
    for f in findings:
        path = str(f.get("file", "")).replace("\\", "/")
        try:
            line = int(f.get("line", 0))
        except (TypeError, ValueError):
            continue
        # !! ONE FINDING SCORES ONCE. The `continue` walked on to the NEXT
        # ground-truth block, which the SAME line could also satisfy once
        # `--slack` was applied -- so three identical findings at `a.py:12`
        # scored two distinct blocks and recall 1.0, directly contradicting
        # this module's own "duplicates do not pay". A candidate could inflate
        # its rank by repeating one line wherever two blocks sit within twice
        # the slack of each other.
        if (path, line) in seen_lines:
            continue
        seen_lines.add((path, line))
        # Nearest block first. Which blocks a finding is ELIGIBLE for is all
        # that decides the score; `_max_hits` uses this order only to break a
        # tie between two coverings of the same size.
        near = sorted(
            (abs(line - (lo + hi) / 2), i)
            for i, (lo, hi) in enumerate(gt.get(path, []))
            if lo - args.slack <= line <= hi + args.slack
        )
        if near:
            eligible.append([(path, i) for _, i in near])
    hits = _max_hits(eligible)

    n = len(findings)
    recall = hits / total if total else 0.0
    precision = hits / n if n else 0.0
    f1 = 2 * recall * precision / (recall + precision) if (recall + precision) else 0.0
    # F2 is the ranked score: the goal is "as many of the real changes as
    # possible in ONE pass", which is recall. Precision still counts -- a
    # candidate cannot win by flagging every block -- but at a QUARTER the
    # weight: b2 is beta squared, and beta = 2 weights recall four times
    # precision. The comment said a third, which is beta squared = 3.
    b2 = 4.0
    f2 = (
        (1 + b2) * precision * recall / (b2 * precision + recall)
        if (precision + recall)
        else 0.0
    )
    print(
        json.dumps(
            {
                "name": args.name,
                "blocks": total,
                "findings": n,
                "hits": hits,
                "recall": round(recall, 4),
                "precision": round(precision, 4),
                "f1": round(f1, 4),
                "f2": round(f2, 4),
            }
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
