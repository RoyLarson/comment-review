"""Render the instruction table `reviewer-brief.md` publishes to a role.

    uv run python scripts/render_brief.py --print
    uv run python scripts/render_brief.py --write

!! TWO SOURCES, AND THE SCRIPT INVENTS NEITHER. The instruction names and the
`claim` keys are a fact the code owns -- `INSTRUCTIONS` in `desk/mark.py`,
each row's `claim_all`. The prose naming WHAT a claim carries is a fact the
spec owns -- `docs/the-mark.md`'s "What each instruction owes" table, the
row's own flags column, written by a human. This script JOINS the two on the
instruction name and writes nothing that is not already stated in one of
them.

! EXITS NONZERO IF THE TWO SOURCES NAME DIFFERENT INSTRUCTIONS -- the drift
that let `add`'s row go stale while the brief still claimed to be generated,
because nothing checked the two against each other.
"""

import argparse
import os
import re
import sys
from pathlib import Path

# A Windows console is cp1252; one non-ASCII glyph kills the run.
reconfigure = getattr(sys.stdout, "reconfigure", None)
if callable(reconfigure):
    reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))
os.environ["PYTHONPATH"] = str(SRC)

from comment_review.desk.mark import INSTRUCTIONS  # noqa: E402

SPEC_PATH = ROOT / "docs" / "the-mark.md"
BRIEF_PATH = (
    ROOT
    / "plugins"
    / "comment-review"
    / "skills"
    / "comment-review"
    / "references"
    / "reviewer-brief.md"
)

BEGIN_MARKER = "<!-- BEGIN GENERATED: instruction table -- scripts/render_brief.py -->"
END_MARKER = "<!-- END GENERATED -->"

#: The "What each instruction owes" table's own header names the "row's own
#: flags" column at a fixed offset -- read from the header itself, not
#: hand-copied, so a column that moves in the spec moves this too.
_FLAGS_COLUMN = "the row's own flags"
_NAME_WIDTH = 11


def _prose_by_instruction() -> dict[str, str]:
    """The "what they carry" sentence for each instruction.

    Read out of `docs/the-mark.md`'s "What each instruction owes" table --
    its own last column, joined across any wrapped continuation lines.

    Returns:
        instruction name -> the row's flags-column text, verbatim.
    """
    spec = SPEC_PATH.read_text(encoding="utf-8")
    match = re.search(
        r"^## What each instruction owes\n.*?```\n(.*?)\n```",
        spec,
        re.MULTILINE | re.DOTALL,
    )
    if not match:
        raise SystemExit(
            f"{SPEC_PATH}: 'What each instruction owes' table not found"
        )
    lines = match.group(1).splitlines()
    header, rows = lines[0], lines[2:]  # lines[1] is the '---' rule
    flags_start = header.index(_FLAGS_COLUMN)

    prose: dict[str, list[str]] = {}
    order: list[str] = []
    for line in rows:
        if not line.strip():
            continue
        name = line[:_NAME_WIDTH].strip()
        if name:
            order.append(name)
            prose[name] = []
        fragment = line[flags_start:].strip()
        if fragment:
            prose[order[-1]].append(fragment)
    return {name: " ".join(parts) for name, parts in prose.items()}


def _claim_cell(claim_all: tuple[str, ...]) -> str:
    """"none" for an empty claim; otherwise each key in backticks, comma-joined."""
    if not claim_all:
        return "none"
    return ", ".join(f"`{key}`" for key in claim_all)


def render() -> str:
    """The instruction table, joined from `INSTRUCTIONS` and the spec.

    Returns:
        The markdown table as it belongs between the GENERATED markers.

    Raises:
        SystemExit: the two sources name different instructions.
    """
    prose = _prose_by_instruction()
    code_names = set(INSTRUCTIONS)
    spec_names = set(prose)
    if code_names != spec_names:
        raise SystemExit(
            "render_brief: INSTRUCTIONS (desk/mark.py) and docs/the-mark.md "
            "name different instructions -- code only: "
            f"{sorted(code_names - spec_names)}, spec only: "
            f"{sorted(spec_names - code_names)}"
        )

    lines = [
        "| instruction | `claim` keys | what they carry |",
        "| --- | --- | --- |",
    ]
    for name, spec in INSTRUCTIONS.items():
        lines.append(f"| `{name}` | {_claim_cell(spec.claim_all)} | {prose[name]} |")
    return "\n".join(lines)


def _write(table: str) -> None:
    """Rewrite the block between the GENERATED markers in `reviewer-brief.md`.

    ! Reads and writes with `newline=""` so a CRLF-checked-out file round-trips
    byte-for-byte outside the block -- a naive text-mode write flips the whole
    file to LF, which reads as an unrelated diff under `core.autocrlf=true`.
    The inserted block matches whichever line ending the file already uses.
    """
    with BRIEF_PATH.open(encoding="utf-8", newline="") as f:
        text = f.read()
    if BEGIN_MARKER not in text:
        raise SystemExit(f"{BRIEF_PATH}: BEGIN GENERATED marker not found")
    if END_MARKER not in text:
        raise SystemExit(f"{BRIEF_PATH}: END GENERATED marker not found")

    eol = "\r\n" if "\r\n" in text else "\n"
    before, rest = text.split(BEGIN_MARKER, 1)
    _, after = rest.split(END_MARKER, 1)
    body = table.replace("\n", eol)
    new_text = (
        f"{before}{BEGIN_MARKER}{eol}{eol}{body}{eol}{eol}{END_MARKER}{after}"
    )

    with BRIEF_PATH.open("w", encoding="utf-8", newline="") as f:
        f.write(new_text)


def main() -> None:
    """CLI entry point: `--print` to stdout, or `--write` in place."""
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--print", action="store_true", help="write the table to stdout"
    )
    group.add_argument(
        "--write",
        action="store_true",
        help="rewrite the block in reviewer-brief.md, in place",
    )
    args = parser.parse_args()

    table = render()
    if args.print:
        print(table)
    else:
        _write(table)


if __name__ == "__main__":
    main()
