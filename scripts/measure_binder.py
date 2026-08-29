"""What the binder emits per page, and what each candidate trim would take off it.

    uv run python scripts/measure_binder.py <paths...> [--fields]

!! THE TWO ARTIFACTS ARE MEASURED SEPARATELY, because they have different consumers
and different defects. The JSON census is what the stage-5 join parses; the listing
is what stage 4 pastes into four prompts. `--filtered` acts on the second and NOT on
the first -- measured 2026-08-24, `--json` returns the same rows and the same bytes
either way -- so a figure taken from one says nothing about the other.

! MEASURED, NEVER A GATE, on the ruling `dead_sweep.py` already carries. It always
exits 0, and every number is re-derived from a live run rather than read from a file.

! WHY IT EXISTS: the trim is argued from these numbers, and a before-and-after a
stranger cannot re-run is a claim rather than a result. It is the instrument for P1
and P11 of `docs/plans/0.2.4-rework-the-binder-hands-the-repo.md`.

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
# Every spelling of absent the census currently uses, gathered in one place.
EMPTY = (None, "", [], {}, 0, -1)
# The heading the run-wide gap report opens with, and where a listing is split.
GAP_REPORT = "NOT CHECKED"


def census(target: Path, *flags: str) -> str:
    """Run the shipped census over one file and return exactly what it printed."""
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "comment_review",
            "census",
            "--repo",
            str(ROOT),
            *flags,
            str(target),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    ).stdout


def rows_of(target: Path) -> list[dict]:
    """The JSON census, as the collator would parse it."""
    return json.loads(census(target, "--json"))


def holds_prose(row: dict) -> bool:
    """Would a reviewer have anything to read here?"""
    return not Kind.holds_no_prose(str(row.get("kind", "")))


def json_table(target: Path) -> None:
    """What the JSON costs, and what each candidate trim takes off it."""
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


def listing_table(target: Path) -> None:
    """What the listing costs, split at the run-wide gap report."""
    out = census(target, "--filtered").splitlines()
    # ! The gap report is a fact about the REPO, so it is the same block on every
    # page. Splitting there is what shows it does not scale with the work.
    cut = next((i for i, ln in enumerate(out) if ln.startswith(GAP_REPORT)), None)
    head = out if cut is None else out[:cut]
    tail = [] if cut is None else out[cut:]
    hb = sum(len(ln) + 1 for ln in head)
    tb = sum(len(ln) + 1 for ln in tail)
    share = f"{100 * tb // (hb + tb):>3}%" if hb + tb else "  -"
    print(
        f"    {target.name:<20} census {len(head):>4} lines {hb:>8,} b"
        f"   gap report {len(tail):>4} lines {tb:>8,} b  = {share}"
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
    ap.add_argument("--json-only", action="store_true")
    ap.add_argument("--listing-only", action="store_true")
    ap.add_argument("--fields", action="store_true")
    args = ap.parse_args()
    targets = [Path(p) for p in args.paths]
    everything = not (args.json_only or args.listing_only or args.fields)

    if everything or args.json_only:
        print("=== THE JSON CENSUS -- what the collator parses, and what a cut saves")
        for target in targets:
            json_table(target)
    if everything or args.listing_only:
        print("\n=== THE LISTING -- what stage 4 pastes, split at the gap report")
        for target in targets:
            listing_table(target)
    if args.fields:
        print("\n=== EVERY KEY, and how many rows say something in it")
        for target in targets:
            fields_table(target)

    print("\n(a measurement, not a gate -- the cuts are candidates, not proposals)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
