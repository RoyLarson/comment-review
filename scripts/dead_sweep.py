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
`addresser.line_address()` with them, 63 lines and zero callers anywhere.

! A DEAD NAME IS NOT TIDY-UP. Each was a CLAIM: the file still said what the
constant was FOR, so a reader -- human or agent -- learned a rule the system no
longer had. That is the defect class this plugin exists to catch, in the one
place its four editorial roles cannot look.

!! THE METHOD, RULED BY ROY 2026-08-21 AFTER TWO WRONG ONES:

    1. build the reference graph from the AST -- names DEFINED, names READ
    2. CUT every reference that comes from a test
    3. what is left with a caller is fine. *"Python has to have a tree, not a
       cycle"*, so something reached at all is reached from somewhere real
    4. what is left with NO caller is what needs a person
    5. only THAT set is worth grepping -- *"and code comments and other
       documentation prose is suspect"*

!! STEP 5 IS THE ONE THAT WAS BACKWARDS. An earlier version used the grep as
CONFIRMATION: a name mentioned anywhere read as live. That is how
`addresser.triggers` survived -- `page.py` names it once, in a docstring
describing a parameter, and a text scan called that a caller. Prose does not
CLEAR a name; finding it there is a reason to look harder.

! AND THE INDEX HAD IT RIGHT. CodeGraph listed `triggers` with one caller, a
test, which is the correct answer -- and the grep overrode it. Roy: *"technically
codegraph probably gave you the graph and you decided it was not right even
though it was probably right."*

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
# ! ONLY SHIPPED NAMES ARE REPORTED. `tests/` defines classes unittest finds by
# REFLECTION, and every one would read as unreferenced.
REPORTED = ("plugins",)
# !! WORKING CODE, as against code that only HOLDS a name. A development script
# reading a shipped name is a real consumer; a TEST reading one proves nothing
# about whether the system uses it, so `tests/` is a holder and not a reader.
DEV = ("scripts", "evals")
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
    """Every name a file defines that something else could read.

    Module-level constants, functions and classes, and the METHODS on those
    classes.

    ! A LOCAL is ruff's to see, and a nested definition is read by its enclosing
    scope whether or not anything calls it -- so neither is here.

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
        # !! A METHOD IS A NAME TOO, and leaving them out left real ground
        # uncovered: `Paragraph.widest` was a property nothing read -- not code,
        # not a test, not prose -- and sat outside both this sweep and ruff.
        # Found 2026-08-21 by asking what the sweep did NOT look at.
        #
        # ! A DUNDER IS NOT REPORTED. `__post_init__` and friends are called by
        # the runtime, which no reference graph sees.
        if isinstance(node, ast.ClassDef):
            out += [
                item.name
                for item in node.body
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                and not item.name.startswith("__")
            ]
    return out


def referenced_names(path: Path) -> set[str]:
    """Every name a file's CODE reads -- not what its prose mentions.

    !! A TEXT SCAN CANNOT ANSWER THIS, and believing it could is what hid
    `addresser.triggers` twice. `page.py` contains the word `triggers` once, in a
    docstring describing a parameter, and a grep over the tree counted that as a
    caller. ! The AST sees names, so a word inside a comment or a docstring is
    not one.

    ! A DEFINITION IS NOT A REFERENCE. `def triggers(...)` is a `FunctionDef`
    and never an `ast.Name`, so a file defining something without using it
    contributes nothing here -- which is the whole question.

    Args:
        path: the file to read.

    Returns:
        Every identifier read as a name or an attribute. Empty when it does not
        parse.
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return set()
    out: set[str] = set()
    for node in ast.walk(tree):
        # !! READ, NOT WRITTEN. `ALIVE = 1` puts `ALIVE` in an `ast.Name` too --
        # with a STORE context -- so counting every Name made each constant its
        # own reader and the sweep reported nothing at all. A `def` escaped it,
        # being a `FunctionDef` rather than a Name, which is why functions
        # surfaced and constants never did.
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            out.add(node.id)
        elif isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Load):
            out.add(node.attr)
        elif isinstance(node, ast.alias):
            # ! `from record import Finding` reads `Finding`.
            out.add((node.asname or node.name).split(".")[-1])
    return out


def unread_names() -> tuple[list[tuple[Path, str]], list[tuple[Path, str, list[str]]]]:
    """Shipped names no WORKING code reads, and who is left holding each one.

    !! THREE ANSWERS, NOT TWO, and the middle one is the question this exists to
    ask. A name is live when other WORKING code reads it -- another shipped
    module, or a development script. What is left over is raised, never passed:

        held by a TEST   the shipped system does not use it. A test is a reader,
                         so a count of readers says LIVE -- but the thing is
                         held UP by its test rather than covered by one.
        held by PROSE    `SKILL.md` and the agent files NAME what a script
                         exposes, and an agent acting on that sentence is a
                         caller no import graph sees. ! Or the sentence is
                         ABANDONED HISTORY. Roy, 2026-08-21: *"a call still in
                         the agents file stating something that is possible
                         because it USED to be possible."*

    !! THE TEST BUCKET WAS ADDED AFTER IT MISSED SOMETHING REAL. `addresser.triggers`
    is called by exactly one test and by no shipped code, while its own docstring
    claims *"ONE LIST, SO THE THREE SERIES CANNOT DRIFT APART"* -- the guarantee
    it was written to provide, documented, tested for SHAPE, and not implemented.
    An earlier sweep cleared it because a test calls it and because `page.py`
    contains the WORD in a docstring. Roy, 2026-08-21: *"I thought we just sliced
    out all of the functions that have only callers in tests?"*

    ! `main` and any `_private` name are skipped: the first is an entry point
    every CLI defines and nothing imports, the second is ruff's to see within
    its own file.

    Returns:
        `(dead, raised)`. `dead` is `(file, name)` for a name nothing mentions at
        all; `raised` adds the files that still hold it.
    """
    working: set[str] = set()
    for p in _python_files(*REPORTED, *DEV):
        working |= referenced_names(p)
    # ! A TEST holds by REFERENCE and prose holds by MENTION, so the two are
    # asked differently -- there is no AST to consult for a markdown file.
    holders: dict[Path, set[str] | str] = {
        p: referenced_names(p) for p in _python_files("tests")
    }
    for p in sorted((ROOT / "plugins").rglob("*.md")):
        holders[p] = p.read_text(encoding="utf-8", errors="replace")

    dead: list[tuple[Path, str]] = []
    raised: list[tuple[Path, str, list[str]]] = []
    for path in sorted(_python_files(*REPORTED)):
        for name in defined_names(path):
            if name.startswith("_") or name == "main":
                continue
            if name in working:
                continue
            word = re.compile(rf"\b{re.escape(name)}\b")
            held_by = [
                p.relative_to(ROOT).as_posix()
                for p, held in holders.items()
                if (name in held if isinstance(held, set) else word.search(held))
            ]
            if held_by:
                raised.append((path, name, held_by))
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
        # input. A TEST holding a name means the shipped system does not use it;
        # PROSE holding one means an agent may be the only caller, or the
        # sentence is abandoned history. Neither is answerable mechanically.
        print("HELD BY A TEST OR BY PROSE -- does the shipped system use it?")
        for path, name, held_by in raised:
            print(f"  {path.relative_to(ROOT).as_posix():<62} {name}")
            for where in held_by:
                print(f"  {'':<62} held by {where}")
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
