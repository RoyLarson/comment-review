"""The brief's verdict table, written from the verdict row that defines it.

    python scripts/render_brief.py            # check, exit 1 if the brief drifted
    python scripts/render_brief.py --write    # rewrite the brief's block in place

!! ONE SOURCE, ONE WAY TO COPY IT. `VERDICTS` in `record.py` already decides
what each verdict's `claim` must carry -- the keys through `claim_keys`, the
prose through `payload` -- and `reviewer-brief.md` restated it by hand. Roy,
2026-08-18: it all moves to the Python file, definitions and prose, and the
script writes it in.

!! THE HAND COPY HAD ALREADY DRIFTED, which is why this exists rather than a
rule telling an author to keep them equal. Measured 2026-08-18: the table
taught the 0.2.x MARKER form -- `false: "..." / true: "..."` -- forty lines
under a JSON worked example, `query`'s row never named `settles` at all, and
**ten of the eleven keys a reviewer must type appeared nowhere in the brief as
keys**. The record became a typed object on this branch and the table below it
did not.

! It writes ONE fenced region, between the markers below, and touches nothing
else in the file. The prose around the table is still hand-written and stays
that way -- what is generated is exactly what `VERDICTS` knows.

! A dev script, not shipped: the brief is generated at authoring time and
pasted whole into a reviewer's prompt, so nothing runs this during a review.
`tests/test_brief_table.py` is the gate.
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "plugins/comment-review/skills/comment-review/scripts"
BRIEF = (
    ROOT / "plugins/comment-review/skills/comment-review/references/reviewer-brief.md"
)

sys.path.insert(0, str(SCRIPTS))

from record import VERDICTS, claim_keys  # noqa: E402  -- path shim must run first

# ! The markers are HTML comments so they render as nothing and survive a
# formatter. `ruff format` excludes `**/*.md`, but a future tool might not.
OPEN = "<!-- BEGIN GENERATED: verdict table -- scripts/render_brief.py -->"
CLOSE = "<!-- END GENERATED -->"

READ_ERRORS = (OSError, UnicodeDecodeError)


def table() -> str:
    """The verdict table, as the brief should carry it.

    ! Rows in `VERDICTS` order, which is the order the seven are taught
    everywhere else: the null verdict, the unsettled one, then the six that ask
    something of stage 5.

    Returns:
        The fenced region's contents, without the markers.
    """
    lines = [
        "| verdict | `claim` keys | what they carry |",
        "| --- | --- | --- |",
    ]
    for name, spec in VERDICTS.items():
        markers, extras = claim_keys(spec)
        keys = ", ".join(f"`{k}`" for k in markers + extras) or "none"
        lines.append(f"| `{name}` | {keys} | {spec.payload} |")
    return "\n".join(lines)


def rendered(brief: str) -> str:
    """`brief` with the generated region replaced by the current table."""
    start, end = brief.index(OPEN), brief.index(CLOSE)
    return brief[: start + len(OPEN)] + "\n\n" + table() + "\n\n" + brief[end:]


def main() -> int:
    """Check the brief against the verdict row, or write it."""
    # A Windows console is cp1252; one non-ASCII glyph in a report kills the run.
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="replace")

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--write", action="store_true", help="rewrite the brief instead of checking it"
    )
    args = ap.parse_args()

    try:
        brief = BRIEF.read_text(encoding="utf-8")
    except READ_ERRORS as e:
        print(f"CANNOT READ {BRIEF} ({type(e).__name__})")
        return 2
    if OPEN not in brief or CLOSE not in brief:
        print(f"{BRIEF.name} carries no generated region -- expected {OPEN}")
        return 2

    want = rendered(brief)
    if args.write:
        if want == brief:
            print(f"{BRIEF.name} already matches the verdict row.")
            return 0
        BRIEF.write_text(want, encoding="utf-8")
        print(f"{BRIEF.name}: verdict table written from VERDICTS.")
        return 0

    if want == brief:
        print(f"{len(VERDICTS)} verdicts; the brief's table matches the row.")
        return 0
    print(
        f"{BRIEF.name}: the verdict table has DRIFTED from `VERDICTS`."
        " Run `python scripts/render_brief.py --write`."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
