"""Score one candidate SKILL.md by what its review pass actually found.

Fitness is RECALL against the prose blocks that really changed, with a
precision term so a candidate cannot win by reporting every line. A finding
counts as a hit when its line falls within (or within `--slack` lines of) a
ground-truth block; each block can be hit only once, so duplicates do not pay.

    uv run python score.py --gt gt.json --findings f.json --slice slice.txt

`findings.json` is `[{"file": "...", "line": 123}, ...]` — the shape every
reviewer already returns.
"""

from __future__ import annotations

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
    hits = 0
    for f in findings:
        path = str(f.get("file", "")).replace("\\", "/")
        try:
            line = int(f.get("line", 0))
        except (TypeError, ValueError):
            continue
        for i, (lo, hi) in enumerate(gt.get(path, [])):
            if (path, i) in matched:
                continue
            if lo - args.slack <= line <= hi + args.slack:
                matched.add((path, i))
                hits += 1
                break

    n = len(findings)
    recall = hits / total if total else 0.0
    precision = hits / n if n else 0.0
    f1 = 2 * recall * precision / (recall + precision) if (recall + precision) else 0.0
    # F2 is the ranked score: the goal is "as many of the real changes as
    # possible in ONE pass", which is recall. Precision still counts — a
    # candidate cannot win by flagging every block — but at a third the weight.
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
