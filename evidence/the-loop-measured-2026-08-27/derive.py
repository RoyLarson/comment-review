"""Re-derive every number in this package from `marks.jsonl`.

    uv run python evidence/the-loop-measured-2026-08-27/derive.py

! It exists because a count in prose and the data it describes drift silently.
`measurements.md` states what this prints; running it is what settles whether
those statements are still true.
"""

import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).parent

#: The two full-binder rounds. Byte-identical inputs, so a difference between
#: them is the system's own variance and nothing else.
FULL = ("round2", "round3")

#: A verdict that proposes work. `clean` is the COVERAGE record and `query` hands
#: the place on, so neither is a finding.
FIX = {"correct", "patch", "drop", "add", "move"}


def load() -> list[dict]:
    """Every mark, one per line of `marks.jsonl`."""
    text = (HERE / "marks.jsonl").read_text(encoding="utf-8")
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def findings(marks: list[dict]) -> list[dict]:
    """The marks that propose work -- `clean` and `query` are neither."""
    return [m for m in marks if m["verdict"] in FIX]


def main() -> None:
    """Print every number `measurements.md` states."""
    marks = load()
    rounds: dict[str, list[dict]] = defaultdict(list)
    for mark in marks:
        rounds[mark["round"]].append(mark)

    print(f"{len(marks)} marks over {len(rounds)} rounds\n")

    print("PER ROUND")
    for name in sorted(rounds):
        got = rounds[name]
        counts = Counter(m["verdict"] for m in got)
        print(
            f"  {name:8} {len(got):4d} marks  {len(findings(got)):3d} findings"
            f"  {len({m['role'] for m in got})} role(s)  {dict(sorted(counts.items()))}"
        )

    print("\nCONSISTENCY -- the two full rounds, keyed on (role, address)")
    print("  ! NOT on the proposed text: two roles fixing one defect write")
    print("    different prose, so that key escalates what agrees best.")
    sets = {n: {(m["role"], m["address"]) for m in findings(rounds[n])} for n in FULL}
    a, b = (sets[n] for n in FULL)
    print(
        f"  round2 {len(a)}   round3 {len(b)}"
        f"   shared {len(a & b)}   union {len(a | b)}"
    )
    print(f"  Jaccard {len(a & b) / len(a | b):.2f}")

    print("\nFAN-OUT -- round4 gave block-context ONE file each")
    fanned = defaultdict(int)
    for mark in findings([m for m in marks if m["fanout"]]):
        fanned[mark["path"]] += 1
    per_round: dict[str, Counter] = {}
    for name in FULL:
        per_round[name] = Counter(
            m["path"] for m in findings(rounds[name]) if m["role"] == "block-context"
        )
    union = defaultdict(set)
    for name in FULL:
        for mark in findings(rounds[name]):
            if mark["role"] == "block-context":
                union[mark["path"]].add(mark["address"])

    print(f"  {'file':46} {'r2':>4} {'r3':>4} {'r2|r3':>6} {'fanned':>7}")
    tot = [0, 0, 0, 0]
    for path in sorted(set(fanned) | set(union)):
        row = (
            per_round["round2"].get(path, 0),
            per_round["round3"].get(path, 0),
            len(union.get(path, ())),
            fanned.get(path, 0),
        )
        print(f"  {path:46} {row[0]:4d} {row[1]:4d} {row[2]:6d} {row[3]:7d}")
        tot = [t + r for t, r in zip(tot, row, strict=True)]
    print(f"  {'TOTAL':46} {tot[0]:4d} {tot[1]:4d} {tot[2]:6d} {tot[3]:7d}")

    print("\nTHE ADDRESS FORM -- whether a mark's address carried its path")
    for label, subset in (
        ("full binder", [m for m in marks if not m["fanout"]]),
        ("fanned out", [m for m in marks if m["fanout"]]),
    ):
        carried = sum(m["address_carried_path"] for m in subset)
        print(f"  {label:12} {carried:4d} of {len(subset):4d}")

    print("\nSOURCES")
    roots = json.loads((HERE / "source-roots.json").read_text(encoding="utf-8"))
    print(f"  {sum(m['n_sources'] for m in marks)} citations across {len(roots)} roots")
    for root, n in sorted(roots.items(), key=lambda kv: -kv[1]):
        print(f"      {n:4d}  {root}")
    print(f"  marks carrying a `ran`: {sum(1 for m in marks if m['has_ran'])}")


if __name__ == "__main__":
    main()
