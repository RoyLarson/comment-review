"""What a RECORD is: the shape a reviewer fills, and the file that carries them.

    python record.py --seed  --census census.json --reviewer ROLE --out DIR/ROLE.json
    python record.py --check DIR/ROLE.json --census census.json

A record is one ruling on one sentence. It used to travel as prose that
`verdicts.py` reconstructed a table from by guessing where each field ended,
and every guess was a defect surface -- a malformed citation absorbed into the
valid one above it, a bare label absorbed into the field above it, a dropped
span absorbing the punctuation beside it. Each of those reported its error
against work that was CORRECT.

!! A REVIEWER FILLS A TEMPLATE; IT DOES NOT COMPOSE A DOCUMENT. `--seed` writes
one slot per prose block with `block` and `address` already in it, so the
reviewer sets only what it decides: `verdict`, `claim`, `reason`, `sources`,
`change`. **Validation then asks whether the answer is COMPLETE rather than
whether the syntax can be parsed** -- a missing field is visibly empty, not
absent.

!! THE REVIEWER NEVER TRANSCRIBES THE BLOCK, and that retires a whole class of
refusal rather than a bug in one. Measured 2026-08-17: **83 refusals in one run
were spent on transcription fidelity, and not one of them was about a finding.**

!! IT IS NOT GIVEN THE TEXT EITHER -- only where to find it. A record carrying
the prose lets a reviewer rule without opening the file, which every role's
remit forbids and no check can detect. `slot()` carries the argument.

! `change` is a LINE ARRAY, which is what the census stores and what a diff can
compare without aligning tokens. A token diff had to decide where a span BEGAN,
and got it wrong on a trailing full stop and on markdown emphasis; lines have
no such question.

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
from verdicts import (  # noqa: E402  -- path shim must run first
    OUT_OF_ROLE,
    QUERY_SHAPES,
    VERDICTS,
)

# The fields the TOOL fills from the census. ! A mismatch here means the file
# was CORRUPTED, never that the reviewer misquoted -- it never typed them.
SEEDED = ("block", "address")
# !! THE SHAPE IS VERSIONED, so a held report stays a REGRESSION TEST rather than
# becoming an archive the day the format moves. Replaying stage-4 output is what
# made 0.2.1 and 0.2.2 cheap to validate -- five joins over one set of reports,
# ~1.6M tokens of review reused -- and that property dies silently when the
# shape changes and nothing says so.
#
# ! PINNING THE CENSUS IS NOT ENOUGH. `SOURCES` cites the WORKING TREE, so a
# replay needs the tree at the run's commit too. Measured 2026-08-17: the same
# four reports joined green against a worktree at their commit and produced 78
# "SOURCES not found" against HEAD, 197 lines later in one file. Neither the
# reader nor the reports were wrong.
RECORD_VERSION = "1"
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
        # !! THE ADDRESS AND NOTHING ELSE. The record does not carry the block's
        # text, so a reviewer cannot rule on it without OPENING THE FILE -- and
        # every role's remit requires that: block-context checks a claim against
        # the code it sits with, ownership-context cannot resolve an anchor
        # without reading, function-context reads name, signature and body
        # together.
        #
        # !! THE TWO ERRORS ARE NOT SYMMETRIC, which is what decides this. Hand
        # a reviewer the prose and it can produce a complete, admissible record
        # without opening anything, and NOTHING in the gate can tell that from
        # real work. Hand it only the address and it may read the wrong lines --
        # but then its `CLAIM` quotes a sentence the census block does not
        # contain, and `block_problem` already catches exactly that, using a
        # census the gate has already loaded. **One error is checked; the other
        # is invisible.**
        #
        # ! Re-check that asymmetry before reversing this. It has flipped three
        # times, and it is the only argument here that does not rest on taste.
        "address": f"{block['path']}:{block['start']}-{block['end']}",
        # ! `null`, not `""`. An unruled block must be distinguishable from one
        # ruled with an empty verdict, and only one of those is a coverage gap.
        "verdict": None,
        "claim": {},
        "reason": "",
        "sources": [],
        "change": [],
    }


def allowed() -> dict:
    """What may go in each CONSTRAINED field, stated in the file itself.

    !! A TEMPLATE THAT CONSTRAINS A FIELD WITHOUT SAYING WHAT IS ALLOWED HAS
    ONLY MOVED THE GUESSING. Half of *"fill out THIS message"* is the message
    saying what may go in each slot -- otherwise the reviewer is back to
    remembering a contract, which is the thing the template replaces.

    !! DERIVED FROM THE VERDICT TABLE, never restated. A JSON claim key is the
    table's marker minus its colon, so adding a verdict stays a ROW and this
    block cannot drift from what the gate enforces. `tests/test_record.py` pins
    that correspondence.

    Returns:
        `verdict` -> the seven; `claim` -> the keys each verdict's claim must
        carry; `values` -> the fields whose value is itself a closed set.
    """
    claims: dict[str, list[str]] = {}
    for name, spec in VERDICTS.items():
        keys = [marker.rstrip(":") for marker in spec.claim_all]
        # ! `query` is the one whose claim_any is a set of PHRASES rather than
        # keys -- it names its SHAPE. The phrase is the value; the key is fixed.
        if spec.claim_any:
            keys.append("shape")
        if spec.needs_attempted:
            keys.append("attempted")
        if spec.needs_settles:
            keys.append("settles")
        if spec.needs_anchor:
            keys += ["anchor", "side"]
        claims[name] = keys
    return {
        "verdict": sorted(VERDICTS),
        "claim": claims,
        "values": {
            "shape": list(QUERY_SHAPES),
            "side": ["above", "below"],
        },
        # ! The one shape that is a BOUNDARY REPORT rather than work, named so a
        # reader of this file can tell the three apart without the brief.
        "scope_shape": OUT_OF_ROLE,
    }


def seed(census: list[dict], reviewer: str) -> dict:
    """The whole file a reviewer is handed, ready to fill."""
    return {
        "record_version": RECORD_VERSION,
        "reviewer": reviewer,
        # ! FIRST, so it is read before the records it governs.
        "allowed": allowed(),
        "records": [slot(i, b) for i, b in prose_blocks(census)],
        # ! Code problems get one line each and carry no verdict. A list rather
        # than a section to find with a regex, which is one more boundary that
        # cannot be guessed wrong.
        "code_concerns": [],
    }


# What each answered field must BE, once it is filled. ! Shape only -- whether a
# citation resolves and whether the claim is true are `verdicts.py`'s, and
# splitting them is what makes these two files one subject each.
SHAPES: dict[str, type] = {
    "claim": dict,
    "reason": str,
    "sources": list,
    "change": list,
}


def seeded_problems(where: str, rec: dict, block: dict | None) -> list[str]:
    """Did the fields the TOOL wrote survive being filled in?

    !! THE MESSAGE MUST NOT ACCUSE THE REVIEWER OF MISQUOTING. It never typed
    these: `--seed` did. A mismatch means the FILE WAS EDITED -- a value
    clipped while its neighbour was filled -- and saying otherwise sends the
    reader to fix work that was correct, which is the defect class this whole
    format change exists to end.
    """
    if block is None:
        return [f"{where}: block {rec.get('block')!r} is not in the census"]
    want = f"{block['path']}:{block['start']}-{block['end']}"
    if rec.get("address") != want:
        return [
            f"{where}: `address` reads {rec.get('address')!r} and the census says"
            f" {want!r}. This field was WRITTEN BY THE TOOL, so it was edited"
            " after seeding -- restore it rather than re-deriving it."
        ]
    return []


def claim_problems(where: str, rec: dict) -> list[str]:
    """Does `claim` carry the keys this verdict's row requires, and no others?"""
    verdict = rec.get("verdict")
    spec = allowed()["claim"].get(verdict)
    if spec is None:
        return []
    claim = rec.get("claim")
    if not isinstance(claim, dict):
        return [f"{where}: `claim` is {type(claim).__name__}, not an object"]
    missing = [k for k in spec if k not in claim]
    extra = [k for k in claim if k not in spec]
    out = []
    if missing:
        out.append(
            f"{where}: {verdict} needs `claim` keys {missing} -- it carries"
            f" {sorted(claim) or 'none'}"
        )
    if extra:
        # ! An unexpected key is a finding, not noise. It is how a reviewer that
        # reached for another verdict's shape shows up before the join.
        out.append(f"{where}: {verdict} has no `claim` key {extra}")
    return out


def value_problems(where: str, rec: dict) -> list[str]:
    """Are the CONSTRAINED values among the ones the template offered?"""
    out = []
    claim = rec.get("claim")
    if not isinstance(claim, dict):
        return out
    for field, permitted in allowed()["values"].items():
        if field in claim and claim[field] not in permitted:
            out.append(
                f"{where}: `claim.{field}` reads {claim[field]!r}, and the"
                f" template offers {permitted}"
            )
    return out


def record_problems(where: str, rec: dict, block: dict | None) -> list[str]:
    """Everything wrong with the SHAPE of one record."""
    out = list(seeded_problems(where, rec, block))
    verdict = rec.get("verdict")
    if verdict is not None and verdict not in VERDICTS:
        out.append(f"{where}: verdict {verdict!r} is not one of {sorted(VERDICTS)}")
    for field, want in SHAPES.items():
        if field not in rec:
            out.append(f"{where}: no `{field}` -- the seeded template carries one")
        elif not isinstance(rec[field], want):
            out.append(
                f"{where}: `{field}` is {type(rec[field]).__name__}, not"
                f" {want.__name__}"
            )
    for i, source in enumerate(rec.get("sources") or [], 1):
        if not isinstance(source, dict) or {"cite", "verbatim"} - set(source):
            out.append(
                f"{where}: source {i} is not `{{cite, verbatim}}` -- it reads"
                f" {source!r}"
            )
    out += claim_problems(where, rec)
    out += value_problems(where, rec)
    return out


def check(report: dict, census: list[dict]) -> tuple[list[str], int]:
    """Every shape problem in a filled report, and how many slots are UNRULED.

    Returns:
        `(problems, unruled)`. ! Unruled is counted, not refused: a reviewer
        checking its own work part-way through needs to know how many slots
        are left, and that is the whole point of a template you FILL. The
        coverage GATE is `verdicts.py`'s, at the join.
    """
    problems: list[str] = []
    if not isinstance(report.get("records"), list):
        return (["no `records` list -- this is not a seeded report"], 0)
    unruled = 0
    for rec in report["records"]:
        index = rec.get("block")
        where = f"block {index}"
        known = isinstance(index, int) and 1 <= index <= len(census)
        block = census[index - 1] if known else None
        if rec.get("verdict") is None:
            unruled += 1
            # ! A slot nobody filled is not MALFORMED, so it is counted rather
            # than reported field by field.
            continue
        problems += record_problems(where, rec, block)
    return (problems, unruled)


def main() -> int:
    """Seed a reviewer's record file from the census."""
    # A Windows console is cp1252; one non-ASCII glyph in a report kills the run.
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="replace")

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seed", action="store_true", help="write an empty record file")
    ap.add_argument("--check", metavar="PATH", help="check a filled record file")
    ap.add_argument("--census", required=True, help="census.py --json output")
    ap.add_argument("--reviewer", help="the editorial role's name (--seed only)")
    ap.add_argument("--out", help="the file to write (--seed only)")
    args = ap.parse_args()

    if not args.seed and not args.check:
        print("nothing to do: pass --seed or --check")
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

    if args.check:
        try:
            report = json.loads(Path(args.check).read_text(encoding="utf-8"))
        except READ_ERRORS as e:
            print(f"CANNOT READ {args.check} ({type(e).__name__})")
            return 2
        except json.JSONDecodeError as e:
            # !! THE ONE FAILURE THIS FORMAT ADDS, and it names its own
            # position where a merged field never could.
            print(f"CANNOT PARSE {args.check} as JSON ({e})")
            return 2
        problems, unruled = check(report, census)
        for problem in problems:
            print(f"  {problem}")
        total = len(report.get("records") or [])
        print(f"\n{total - unruled} of {total} records ruled; {unruled} still empty.")
        if problems:
            print(f"{len(problems)} problem(s). The shape is wrong, not the finding.")
            return 1
        # ! An unfilled report is INCOMPLETE, not malformed, and the two exit
        # differently: a reviewer part-way through is not in error.
        print("Every filled record is well formed." if total else "No records.")
        return 0

    if not args.reviewer or not args.out:
        print("--seed needs --reviewer and --out")
        return 2
    report = seed(census, args.reviewer)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=1), encoding="utf-8")

    prose = len(report["records"])
    print(f"{args.reviewer}: {prose} records seeded from {len(census)} blocks -> {out}")
    print(f"  the reviewer fills {', '.join(ANSWERED)}")
    print(f"  {', '.join(SEEDED)} are already there")
    return 0


if __name__ == "__main__":
    sys.exit(main())
