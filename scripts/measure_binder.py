"""What the binder emits per page, and what each candidate trim would take off it.

    uv run python scripts/measure_binder.py <paths...> [--fields]

! ONE ARTIFACT. The binder is what every later command reads and what each
reviewer's copy is seeded from; `gather` writes nothing else.

! MEASURED, NEVER A GATE, on the ruling `dead_sweep.py` already carries. It always
exits 0, and every number is re-derived from a live run rather than read from a file.

! WHY IT EXISTS: a trim is argued from these numbers, and a before-and-after a
stranger cannot re-run is a claim rather than a result.

! THE TRIMS ARE CANDIDATES, NOT PROPOSALS. `CARRIES` is the seven fields a 2026-08-22
reading found holding information; which fields a reviewer NEEDS is an owed ruling.
This tool says what each cut would cost, not which cut to make.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

# A Windows console is cp1252; one non-ASCII glyph kills the run.
# ! Spelled out rather than bound to a short name, because
# `tests/test_shipped_cli_encoding.py` matches this call TEXTUALLY.
reconfigure = getattr(sys.stdout, "reconfigure", None)
if callable(reconfigure):
    reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
# ! THE SOURCE, since the move on 2026-08-24. `plugins/` holds a built copy.
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))
# ! AND ON `PYTHONPATH`, because the census below runs as a CHILD and a child
# inherits the environment rather than this process's `sys.path`.
os.environ["PYTHONPATH"] = str(SRC)

from comment_review.reading.lexer import Kind  # noqa: E402

# The four roles stage 4 dispatches. Every per-page figure is paid once each.
ROLES = 4
# The seven fields a 2026-08-22 reading found carrying information on an empty place.
CARRIES = ("path", "kind", "anchor", "anchor_line", "anchor_num", "tier", "address")
# File facts, repeated per row, that `record.py` already states once per page.
ENVELOPE = ("path", "tier")
# Every spelling of absent the binder currently uses, gathered in one place.
EMPTY = (None, "", [], {}, 0, -1)


def binder_of(target: Path) -> str:
    """Run the shipped gather over one file and return exactly what it printed."""
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "comment_review",
            "gather",
            "--repo",
            str(ROOT),
            str(target),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    ).stdout


def rows_of(target: Path) -> list[dict]:
    """The binder's rows, flattened across its pages, as the collator reads them."""
    binder = json.loads(binder_of(target))
    return [row for page in binder["pages"] for row in page["rows"]]


def holds_prose(row: dict) -> bool:
    """Would a reviewer have anything to read here?"""
    return not Kind.holds_no_prose(str(row.get("kind", "")))


def json_table(target: Path) -> None:
    """What the binder's rows cost, and what each candidate trim takes off them."""
    rows = rows_of(target)
    prose = [r for r in rows if holds_prose(r)]
    full = len(json.dumps(rows, indent=1))
    cuts = {
        "as it ships": rows,
        "carrying fields only": [
            {k: v for k, v in r.items() if k in CARRIES} for r in rows
        ],
        "path+tier to an envelope": [
            {k: v for k, v in r.items() if k not in ENVELOPE} for r in rows
        ],
        "prose rows only": prose,
        "both cuts together": [
            {k: v for k, v in r.items() if k in CARRIES and k not in ENVELOPE}
            for r in prose
        ],
    }
    print(f"\n  {target.name}: {len(rows)} rows, {len(prose)} hold prose")
    for label, sub in cuts.items():
        size = len(json.dumps(sub, indent=1))
        share = 100 * size // full if full else 0
        print(
            f"    {label:<26} {size:>9,}  {share:>3}%   x{ROLES} = {ROLES * size:>10,}"
        )


def fields_table(target: Path) -> None:
    """Per key: how many rows carry it, and how many say something in it."""
    rows = rows_of(target)
    keys = sorted({k for r in rows for k in r})
    print(f"\n  {target.name}: {len(keys)} distinct keys over {len(rows)} rows")
    print(f"    {'key':<18} {'present':>8} {'carries':>8} {'bytes':>9}")
    for key in keys:
        present = sum(1 for r in rows if key in r)
        carries = sum(1 for r in rows if key in r and r[key] not in EMPTY)
        size = sum(len(json.dumps(r[key])) for r in rows if key in r)
        print(f"    {key:<18} {present:>8} {carries:>8} {size:>9,}")


def main() -> int:
    """Print whichever tables were asked for. Always exits 0."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--fields", action="store_true")
    args = ap.parse_args()
    targets = [Path(p) for p in args.paths]

    if not args.fields:
        print("=== THE BINDER -- what the collator parses, and what a cut saves")
        for target in targets:
            json_table(target)
    if args.fields:
        print("\n=== EVERY KEY, and how many rows say something in it")
        for target in targets:
            fields_table(target)

    print("\n(a measurement, not a gate -- the cuts are candidates, not proposals)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
