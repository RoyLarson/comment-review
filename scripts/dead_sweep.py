"""What nothing points at: a shipped name no code reads, a link that resolves nowhere.

    uv run python scripts/dead_sweep.py [--names] [--links]

!! AN INPUT, NOT A GATE, AND THAT IS A RULING. Roy, 2026-08-21: *"I don't think
it deserves a gating. I do think it is a genuinely good idea to run every now and
then."* It always exits 0. `check_vocabulary.py` refuses and this reports, for
the same reason `vocabulary_sweep.py` does: a row here is a candidate a person
confirms, and a check that blocks a commit over a false positive gets switched
off rather than fixed.

!! WHY IT EXISTS: FOUR NAMES WENT DEAD IN ONE DAY AND NO GATE SAW ANY OF THEM.
Ruff flags an unused IMPORT and an unused LOCAL; a module-level constant nobody
reads is invisible to it. `record.ANCHOR_SIDE` survived long enough to be found
by a code-review agent READING the file, and `OPENER`, `CODE_CONCERNS` and
`PATHISH` each died the moment their last reader was deleted --
`foliator.line_address()` with them, 63 lines and zero callers anywhere.

! A DEAD NAME IS NOT TIDY-UP. Each was a CLAIM: the file still said what the
constant was FOR, so a reader -- human or agent -- learned a rule the system no
longer had. That is the defect class this plugin exists to catch, in the one
place its four editorial roles cannot look.

!! ITS ERRORS RUN ONE WAY, AND THAT IS WHY THE TEXT SCAN IS ENOUGH. A name
MENTIONED in a comment counts as a use, so a dead constant some docstring happens
to name reads as live -- a FALSE NEGATIVE. It under-reports and never invents.
! The reverse was tried and is what makes a gate untenable: an earlier version
asked the CodeGraph index for callers outside the defining file, and reported 32
false positives in one run -- every one a function reached through its own
module's `main`, which is live, because the CLI is a consumer. A second version
fixed that and still called four dataclasses dead, because an index does not
resolve a class used as a type annotation.

! LINKS ARE SWEPT AND NEVER FIXED. Roy, 2026-08-21, on the 13 that dangle out of
`TODO/completed/`: *"it orphans the references but only down to the completed
folder, and if the plan and the todo are completed then it is unlikely that it
matters except back checking. It also seems like it would require files to be
rewritten for history, which has been denied several times."* So this prints
them and stops.
"""

import argparse
import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# ! REPORTED FROM `plugins/` AND SEARCHED EVERYWHERE. Only shipped names are
# worth reporting -- `tests/` defines classes unittest finds by REFLECTION, and
# every one would read as unreferenced -- but a test IS a reader, so the search
# for uses covers the whole tree.
REPORTED = ("plugins",)
SEARCHED = ("plugins", "scripts", "tests", "evals")
LINKED = ("docs", "TODO")
LINK = re.compile(r"\[[^\]]*\]\((?!https?:|#)([^)#]+)")
# ! A link inside BACKTICKS is an example, not a link. `complete-breaks-links.md`
# writes `[x](sibling.md)` to describe the defect and was reported for it.
CODE_SPAN = re.compile(r"`[^`\n]*`")


def _python_files(*trees: str) -> list[Path]:
    """Every `.py` under those trees, skipping caches and fetched corpora."""
    return [
        p
        for tree in trees
        for p in (ROOT / tree).rglob("*.py")
        if "__pycache__" not in p.parts and "corpora" not in p.parts
    ]


def defined_names(path: Path) -> list[str]:
    """Every MODULE-LEVEL name a file defines -- constants, functions, classes.

    ! Module level only. A local or an attribute is ruff's to see, and a nested
    definition is read by its enclosing scope whether or not anything calls it.

    Args:
        path: the file to read.

    Returns:
        The names, in source order. Empty when the file does not parse.
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return []
    out: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            out += [t.id for t in node.targets if isinstance(t, ast.Name)]
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            out.append(node.target.id)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out.append(node.name)
    return out


def unread_names() -> tuple[list[tuple[Path, str]], list[tuple[Path, str, list[str]]]]:
    """Shipped names no CODE reads, split by whether shipped PROSE still names one.

    !! PROSE IS NOT EVIDENCE OF LIFE, AND NOT EVIDENCE OF DEATH. `SKILL.md` and
    the agent files NAME what a script exposes, and an agent acting on that
    sentence is a consumer no import graph can see -- so a name reached only
    that way is alive. ! But the same sentence may be ABANDONED HISTORY. Roy,
    2026-08-21: *"a call still in the agents file stating something that is
    possible because it USED to be possible."*

    ! Counting prose as a use hides the second; ignoring it invents the first.
    So a prose-only name is neither passed nor reported dead -- it is RAISED,
    with the files that name it, for a person to answer: dead code, or a tool
    the prose is the only caller of?

    ! `main` and any `_private` name are skipped: the first is an entry point
    every CLI defines and nothing imports, the second is ruff's to see within
    its own file.

    Returns:
        `(dead, prose_only)`. The first is `(file, name)` for a name nothing
        mentions at all; the second adds the shipped markdown files that do.
    """
    code = "\n".join(
        p.read_text(encoding="utf-8", errors="replace")
        for p in _python_files(*SEARCHED)
    )
    prose = {
        p: p.read_text(encoding="utf-8", errors="replace")
        for p in sorted((ROOT / "plugins").rglob("*.md"))
    }
    dead: list[tuple[Path, str]] = []
    raised: list[tuple[Path, str, list[str]]] = []
    for path in sorted(_python_files(*REPORTED)):
        for name in defined_names(path):
            if name.startswith("_") or name == "main":
                continue
            word = re.compile(rf"\b{re.escape(name)}\b")
            # ! ITS OWN DEFINITION IS THE ONE OCCURRENCE THAT DOES NOT COUNT.
            if len(word.findall(code)) > 1:
                continue
            named_in = [
                p.relative_to(ROOT).as_posix()
                for p, t in prose.items()
                if word.search(t)
            ]
            if named_in:
                raised.append((path, name, named_in))
            else:
                dead.append((path, name))
    return dead, raised


def dangling_links() -> list[tuple[Path, str]]:
    """Relative markdown links under `docs/` and `TODO/` that resolve to nothing.

    Returns:
        `(file, link)` for each, in file order.
    """
    out: list[tuple[Path, str]] = []
    for tree in LINKED:
        for md in sorted((ROOT / tree).rglob("*.md")):
            prose = CODE_SPAN.sub("", md.read_text(encoding="utf-8", errors="replace"))
            for m in LINK.finditer(prose):
                target = m.group(1).strip()
                if not (md.parent / target).resolve().exists():
                    out.append((md, target))
    return out


def main() -> int:
    """Report both sweeps. ! ALWAYS 0 -- it is an input, and a person judges."""
    # A Windows console is cp1252; one non-ASCII glyph kills the run.
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="replace")

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--names", action="store_true", help="only the unread names")
    ap.add_argument("--links", action="store_true", help="only the dangling links")
    args = ap.parse_args()
    both = not (args.names or args.links)

    if both or args.names:
        dead, raised = unread_names()
        print("SHIPPED NAMES NOTHING READS")
        for path, name in dead:
            print(f"  {path.relative_to(ROOT).as_posix():<62} {name}")
        print(f"  {len(dead)} of them.\n")

        # !! THE QUESTION A PERSON HAS TO ANSWER, and the reason this is an
        # input. Prose may be the ONLY caller -- an agent acting on a sentence
        # in `SKILL.md` -- or it may be abandoned history, still describing
        # something that used to be possible.
        print("NAMED ONLY IN SHIPPED PROSE -- dead code, or a tool prose calls?")
        for path, name, named_in in raised:
            print(f"  {path.relative_to(ROOT).as_posix():<62} {name}")
            for where in named_in:
                print(f"  {'':<62} still in {where}")
        print(f"  {len(raised)} of them.\n")

    if both or args.links:
        found = dangling_links()
        print("RELATIVE LINKS THAT RESOLVE NOWHERE")
        for md, target in found:
            print(f"  {md.relative_to(ROOT).as_posix():<62} -> {target}")
        # ! Most of these are a completed TODO citing a sibling that was
        # completed after it. Fixing one means rewriting an archived file, which
        # this repo does not do -- read them, do not repair them.
        print(f"  {len(found)} of them.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
