"""Score one candidate SKILL.md by what its review pass actually found.

Fitness is RECALL against the prose blocks that really changed, with a
precision term so a candidate cannot win by reporting every line. A finding
counts as a hit when its line falls within (or within `--slack` lines of) a
ground-truth block; each block can be hit only once, so duplicates do not pay.

    uv run python score.py --gt gt.json --findings f.json --slice slice.txt

`findings.json` is `[{"file": "...", "line": 123}, ...]` — the shape every
reviewer already returns.
"""

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    """Score one candidate's findings against the ground truth."""
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
    matched: set[tuple[str, int]] = set()
    # ⚠ The same `file:line` may be offered many times; it is one finding.
    seen_lines: set[tuple[str, int]] = set()
    hits = 0
    for f in findings:
        path = str(f.get("file", "")).replace("\\", "/")
        try:
            line = int(f.get("line", 0))
        except (TypeError, ValueError):
            continue
        # ⚠⚠ ONE FINDING SCORES ONCE. The `continue` walked on to the NEXT
        # ground-truth block, which the SAME line could also satisfy once
        # `--slack` was applied -- so three identical findings at `a.py:12`
        # scored two distinct blocks and recall 1.0, directly contradicting
        # this module's own "duplicates do not pay". A candidate could inflate
        # its rank by repeating one line wherever two blocks sit within twice
        # the slack of each other.
        if (path, line) in seen_lines:
            continue
        # ⚠⚠ CLOSEST block, not the first one in list order. Greedy first-fit
        # let a finding consume a block a later finding needed, so the SCORE
        # DEPENDED ON THE ORDER of the candidate's findings. Measured with
        # gt {"a.py": [[10,12],[16,18]]} and --slack 3: findings [15, 11] scored
        # recall 0.5 and the same two as [11, 15] scored 1.0 -- two candidates
        # that found identical things given different fitness, which is a silent
        # ranking error in the GA.
        near = [
            (abs(line - (lo + hi) / 2), i)
            for i, (lo, hi) in enumerate(gt.get(path, []))
            if (path, i) not in matched and lo - args.slack <= line <= hi + args.slack
        ]
        if near:
            _, i = min(near)
            matched.add((path, i))
            seen_lines.add((path, line))
            hits += 1

    n = len(findings)
    recall = hits / total if total else 0.0
    precision = hits / n if n else 0.0
    f1 = 2 * recall * precision / (recall + precision) if (recall + precision) else 0.0
    # F2 is the ranked score: the goal is "as many of the real changes as
    # possible in ONE pass", which is recall. Precision still counts — a
    # candidate cannot win by flagging every block — but at a QUARTER the
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
