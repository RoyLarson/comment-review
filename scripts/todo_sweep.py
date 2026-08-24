"""What the backlog says that it cannot mean.

A closed file with open work, a flag that disagrees with its own boxes, a link or a
hash that resolves nowhere.

    uv run python scripts/todo_sweep.py [--closed] [--flags] [--links] [--hashes]

!! AN INPUT, NOT A GATE, on the ruling `dead_sweep.py` already carries. Roy,
2026-08-21: *"I don't think it deserves a gating. I do think it is a genuinely good
idea to run every now and then."* It always exits 0. `todo_tool.py resync` REFUSES,
because a count it can recompute is a fact; every row here is a candidate a person
confirms.

!! WHY IT EXISTS: EACH CHECK WAS FOUND BY HAND, ONCE, AND WAS THEN EVERYWHERE.
`requires-roy-never-goes-back-down` sat in `completed/` carrying FIVE unchecked boxes
and `Status: deferred` -- found only because `resync` refused to reconcile the README
around it. Swept 2026-08-24, EIGHT files were in that state, four with every box open.

! THE FLAG CHECK IS THE ONE THAT COSTS ROY DIRECTLY. `Requires-Roy` is how he pulls the
queue of what waits on him; an owed ruling whose file says `false` is invisible to it.
Measured the same day: TEN files carried an unchecked `*` box -- an owed ruling -- with
the flag down and no `deferred` or `blocked` status to explain it. ! A deferred ruling
with the flag down is CORRECT and is reported separately: what blocks it is work.

!! AND A STALE HASH READS EXACTLY LIKE A GOOD ONE. The 2026-08-23 history rewrite killed
six commits this backlog cites, and nothing noticed -- `git log` cannot tell a purged
path from one that never existed, so absence proves nothing and only `cat-file` answers.

! WHAT IT DOES NOT DO is decide. A closed file with an open box may need the box ticked
or the file reopened; a dead link may need repointing or deleting. Both are judgements
about what the work IS, which is why this prints and stops.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

# A Windows console is cp1252; one non-ASCII glyph kills the run.
# ! Spelled out rather than bound to a short name, because
# `tests/test_shipped_cli_encoding.py` matches this call TEXTUALLY -- it caught the
# abbreviated form on the day this file was written.
reconfigure = getattr(sys.stdout, "reconfigure", None)
if callable(reconfigure):
    reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
TODO = ROOT / "TODO"
LANES = ("agents", "backend", "testing", "systems")

BOX = re.compile(r"^- \[([ xX])\]", re.M)
# An owed ruling is an UNCHECKED box whose prose opens with `*`, per the task rules.
OWED = re.compile(r"^- \[ \] (?:\*\*)?T\d+ -- \*", re.M)
FIELD = re.compile(r"^(Status|Owner|Requires-Roy):\s*(.*)$", re.M)
LINK = re.compile(r"\[[^\]]*\]\((?!https?:)([^)#]+\.md)\)")
HASH = re.compile(r"`([0-9a-f]{7,40})`")
# A status naming what it waits on: `deferred (...)`, `blocked (on ...)`.
WAITING = re.compile(r"\b(deferred|blocked)\b", re.I)


def read(p: Path) -> str:
    """Read a TODO, tolerating whatever encoding it landed in."""
    return p.read_text(encoding="utf-8", errors="replace")


def fields(text: str) -> dict[str, str]:
    """The header fields, as a dict -- `Status`, `Owner`, `Requires-Roy`."""
    return {m.group(1): m.group(2).strip() for m in FIELD.finditer(text)}


def open_todos() -> list[Path]:
    """Every open TODO. `README.md` is the tool's own index, not a TODO."""
    return sorted(p for p in TODO.glob("*.md") if p.stem != "README")


def closed_todos() -> list[Path]:
    """Every TODO that has been moved into `completed/`."""
    return sorted((TODO / "completed").glob("*.md"))


def check_closed() -> list[str]:
    """A file in `completed/` with an unchecked box claims work that nothing counts."""
    out = []
    for p in closed_todos():
        marks = BOX.findall(read(p))
        n = sum(1 for m in marks if m == " ")
        if n:
            out.append(f"{p.name}: {n} of {len(marks)} boxes unchecked")
    return out


def check_flags() -> tuple[list[str], list[str], list[str]]:
    """Where `Requires-Roy` and the boxes disagree about whether a decision is owed."""
    missing, spurious, waiting = [], [], []
    for p in open_todos():
        text = read(p)
        f = fields(text)
        flagged = f.get("Requires-Roy", "").lower() == "true"
        owed = bool(OWED.search(text))
        status = f.get("Status", "")
        if owed and not flagged:
            (waiting if WAITING.search(status) else missing).append(
                f"{p.name}  [{status[:44]}]"
            )
        if flagged and not owed:
            spurious.append(p.name)
    return missing, spurious, waiting


def check_owner() -> list[str]:
    """An `Owner:` that names no lane, so nobody is answerable for it."""
    out = []
    for p in open_todos():
        owner = fields(read(p)).get("Owner", "")
        if owner and owner.split()[0].lower() not in LANES:
            out.append(f"{p.name}: {owner!r}")
    return out


def check_links() -> list[str]:
    """A markdown link to a file that is not there."""
    out = []
    for p in open_todos() + closed_todos():
        for m in LINK.finditer(read(p)):
            if not (p.parent / m.group(1)).resolve().exists():
                out.append(f"{p.name} -> {m.group(1)}")
    return out


def check_hashes() -> list[str]:
    """A hash the rewrite killed. `git log` cannot answer this; `cat-file` can."""
    wanted = {h for p in open_todos() + closed_todos() for h in HASH.findall(read(p))}
    if not wanted:
        return []
    proc = subprocess.run(
        ["git", "cat-file", "--batch-check"],
        cwd=ROOT, input="\n".join(sorted(wanted)).encode(), stdout=subprocess.PIPE,
    )
    return [
        line.split()[0]
        for line in proc.stdout.decode("utf-8", "replace").splitlines()
        if "missing" in line
    ]


def show(title: str, rows: list[str], limit: int = 20) -> None:
    """Print one section, capped, saying how many rows were not shown."""
    print(f"\n=== {title}: {len(rows)}")
    for r in rows[:limit]:
        print(f"    {r}")
    if len(rows) > limit:
        print(f"    ... {len(rows) - limit} more")


def main() -> int:
    """Run the selected checks and report. Always exits 0."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--closed", action="store_true")
    ap.add_argument("--flags", action="store_true")
    ap.add_argument("--links", action="store_true")
    ap.add_argument("--hashes", action="store_true")
    args = ap.parse_args()
    everything = not any((args.closed, args.flags, args.links, args.hashes))

    if everything or args.closed:
        show("CLOSED, with work still claimed", check_closed())
    if everything or args.flags:
        missing, spurious, waiting = check_flags()
        show("OWED a ruling, and Roy's queue does not show it", missing)
        show("FLAGGED for Roy, with no `*` box naming the ruling", spurious)
        show("OWED but DEFERRED or BLOCKED -- correct, listed to be re-read", waiting)
        show("OWNER is not one of the four lanes", check_owner())
    if everything or args.links:
        show("LINK resolves nowhere", check_links())
    if everything or args.hashes:
        show("HASH no longer resolves -- re-locate before trusting the claim",
             check_hashes())

    print("\n(an input, not a gate -- every row needs a person)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
