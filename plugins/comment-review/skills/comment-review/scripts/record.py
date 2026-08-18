"""What a RECORD is: the shape a reviewer fills, and the file that carries them.

    python record.py --seed --census census.json --reviewer block-context --out DIR/block-context.json

A record is one ruling on one sentence. It used to travel as prose that
`verdicts.py` reconstructed a table from by guessing where each field ended,
and every guess was a defect surface -- a malformed citation absorbed into the
valid one above it, a bare label absorbed into the field above it, a dropped
span absorbing the punctuation beside it. Each of those reported its error
against work that was CORRECT.

!! A REVIEWER FILLS A TEMPLATE; IT DOES NOT COMPOSE A DOCUMENT. `--seed` writes
one slot per prose block with `block`, `address` and `original` already in it,
so the reviewer sets only what it decides: `verdict`, `claim`, `reason`,
`sources`, `change`. **Validation then asks whether the answer is COMPLETE
rather than whether the syntax can be parsed** -- a missing field is visibly
empty, not absent.

!! THE REVIEWER NEVER TRANSCRIBES THE BLOCK, and that retires a whole class of
refusal rather than a bug in one. Measured 2026-08-17: **83 refusals in one run
were spent on transcription fidelity, and not one of them was about a finding.**

! `original` and `change` are LINE ARRAYS, which is what the census stores and
what a diff can compare without aligning tokens. A token diff had to decide
where a span BEGAN, and got it wrong on a trailing full stop and on markdown
emphasis; lines have no such question.

! COVERAGE IS STRUCTURAL. Every prose block gets a slot, so a block nobody
ruled on is a slot with a null verdict rather than an index missing from a
list, and nothing has to reconcile what was expected against what arrived.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from repo import READ_ERRORS  # noqa: E402  -- path shim must run first

# The fields the TOOL fills from the census, and which `--check` verifies are
# unchanged. ! A mismatch here means the file was CORRUPTED, never that the
# reviewer misquoted -- it never typed them.
SEEDED = ("block", "address", "original")
# The fields the REVIEWER fills. Empty is a legitimate answer for every one of
# them except `verdict`, which is the ruling itself.
ANSWERED = ("verdict", "claim", "reason", "sources", "change")


def prose_blocks(census: list[dict]) -> list[tuple[int, dict]]:
    """Every census block that HOLDS PROSE, with its 1-based index.

    ! An `interval` holds nothing and no reviewer owes it a record. It stays
    ADDRESSABLE so an `add` can cite the gap it is about, which is why the
    census numbers every one -- but it is not accountable, and seeding a slot
    for each would bury 224 real questions under 1730 empty ones.
    """
    return [(i, b) for i, b in enumerate(census, 1) if b.get("kind") != "interval"]


def slot(index: int, block: dict) -> dict:
    """One record, seeded from the census and otherwise empty.

    Args:
        index: the block's 1-based census index, which is its identity.
        block: the census entry.

    Returns:
        The record as the reviewer receives it.
    """
    return {
        "block": index,
        "address": f"{block['path']}:{block['start']}-{block['end']}",
        # ! The lines AS THE FILE READS THEM, which is what the census stores
        # and what a reviewer needs in front of it. Not the joined text: that
        # is a normalisation, and normalising before a diff is what made a
        # token comparison necessary in the first place.
        "original": list(block.get("raw_lines") or []),
        # ! `null`, not `""`. An unruled block must be distinguishable from one
        # ruled with an empty verdict, and only one of those is a coverage gap.
        "verdict": None,
        "claim": {},
        "reason": "",
        "sources": [],
        "change": [],
    }


def seed(census: list[dict], reviewer: str) -> dict:
    """The whole file a reviewer is handed, ready to fill."""
    return {
        "reviewer": reviewer,
        "records": [slot(i, b) for i, b in prose_blocks(census)],
        # ! Code problems get one line each and carry no verdict. A list rather
        # than a section to find with a regex, which is one more boundary that
        # cannot be guessed wrong.
        "code_concerns": [],
    }


def main() -> int:
    """Seed a reviewer's record file from the census."""
    # A Windows console is cp1252; one non-ASCII glyph in a report kills the run.
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="replace")

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seed", action="store_true", help="write an empty record file")
    ap.add_argument("--census", required=True, help="census.py --json output")
    ap.add_argument("--reviewer", required=True, help="the editorial role's name")
    ap.add_argument("--out", required=True, help="the file to write")
    args = ap.parse_args()

    if not args.seed:
        print("nothing to do: pass --seed")
        return 2
    try:
        loaded = json.loads(Path(args.census).read_text(encoding="utf-8"))
    except READ_ERRORS as e:
        print(f"CANNOT READ {args.census} ({type(e).__name__})")
        return 2
    except json.JSONDecodeError as e:
        print(f"CANNOT PARSE {args.census} as JSON ({e})")
        return 2

    census = loaded["blocks"] if isinstance(loaded, dict) else loaded
    report = seed(census, args.reviewer)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=1), encoding="utf-8")

    prose = len(report["records"])
    print(f"{args.reviewer}: {prose} records seeded from {len(census)} blocks -> {out}")
    print(
        f"  the reviewer fills {', '.join(ANSWERED)}; {', '.join(SEEDED)} are already there"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
