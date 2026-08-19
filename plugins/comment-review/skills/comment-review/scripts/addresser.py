"""An address that survives the edits this tool makes.

    python addresser.py --census census.json --repo D

`census.address` names a place by LINE -- `a.py:33-34`. That is the right answer
to "where is this in the file I just read" and the wrong answer to "which place
is this", because this tool EDITS PROSE and every prose edit moves the line
numbers of the code below it. Two files differing only in comments disagree
about where the same statement is.

!! THIS RESTS ENTIRELY ON THE CENSUS BEING WHAT ROY CALLED IT, 2026-08-18: a
HASHED STATIC TABLE -- exact, constant, FULLY ENUMERATED. Take away any one of
those and the scheme collapses without saying so:

  fully enumerated  a code line missed anywhere above a place SHIFTS ITS NAME.
                    `b7` is "after the seventh code line", so a partial
                    enumeration does not fail -- it renames every place below
                    the hole, silently and consistently
  constant          the same file must count the same way twice, or two runs
                    cannot be compared, which is the whole point
  exact             a heuristic that is usually right is a table that is
                    occasionally renumbered

! And what MAKES it constant across this tool's own work is stage 7b: it proves
the executable code BYTE-IDENTICAL, so every edit moves prose and nothing else.
The code-line numbering is invariant by construction rather than by luck --
but only while the enumeration underneath it is complete.

Two forms, because a place is one of exactly two things:

    package.core.py@c3    ON code line 3 -- shares the line with the statement
    package.core.py@b3    the GAP after code line 3, before code line 4

! `b0` is the gap before the first code line; `bN` after the last. A file with N
code lines has N+1 gaps, and every comment run, docstring and empty interval
sits in one of them.

!! THE TWO FORMS ARE SEPARATE ON PURPOSE. `c3` says this prose belongs BESIDE
the statement; `b3` says it belongs ABOVE it. Roy, 2026-08-18: the split "allows
the editors to say this single line edit belongs next to the code not above the
code" -- an editorial choice line numbers conflated, because both sit on
adjacent lines.

!! THE SAME GAP IS THE SAME ADDRESS WHETHER PROSE FILLS IT OR NOT, which is the
property line numbers cannot give. A comment block occupying three lines and an
empty interval in the same position are both `b1` -- so a finding can say where
it belongs in a file that does not have the prose yet, and two versions of a
file can be compared place by place.

!! IT NAMES A PLACE, NOT A BLOCK, and those are not the same thing. One gap can
hold SEVERAL prose blocks -- a docstring on one line and a comment run under it,
with no code between them, are both "after code line 37". Measured 2026-08-18
over this repo's own thirteen shipped scripts: 24 of 2,963 blocks share a place
with a neighbour, 0.8%.

! So an address is NOT a unique key on its own, and a record must not cite one
alone. A record already carries the census `block` index beside it: the INDEX
says which block, the ADDRESS says which place, and only the second survives an
edit. `--check` reports every place that more than one block answers to, which
is where citing the address alone would resolve to the wrong prose.

! It does NOT replace `census.address`. A reviewer reads a file and a line
number is what it has in hand; this is what a record should CARRY. Which of the
two a record cites is unruled -- see
`TODO/address-is-not-stable-under-prose-edits.md`.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from census import address  # noqa: E402  -- path shim must run first
from galley import block_matches  # noqa: E402  -- path shim must run first
from repo import READ_ERRORS  # noqa: E402  -- path shim must run first

ON = "c"
GAP = "b"
# A block that shares its line with code, so it sits ON one rather than between.
SHARES_ITS_LINE = ("trailing-comment",)


def dotted(path: str) -> str:
    """`pkg/sub/mod.py` as `pkg.sub.mod.py` -- the whole path, extension kept.

    !! THE ADDRESS IS THE FULL PATH from the runner's root, not the file name.
    Roy, 2026-08-18: "the address is the full thing not just `__init__@b0`".
    Files form a tree, so a complete path cannot collide, and the form is safe
    if verbose.

    !! THE EXTENSION STAYS. Dropping it reads better and reintroduces collisions
    the moment a repo holds `b.py` beside `b.rs` -- which this census supports by
    design, eleven languages in one run. Roy ruled it 2026-08-18: "we could have
    mixed languages in the system with the same names that without that we are
    back to collisions."
    """
    return str(path).replace("\\", "/").replace("/", ".")


def undot(name: str, paths: list[str]) -> str:
    """The real path a dotted one names, or "" if the census cannot say.

    !! THE DOTTED FORM IS NOT SELF-INVERTIBLE, so this resolves against the
    census rather than by string surgery. `a/b.py` and `a.b.py` both read
    `a.b.py`, and a dot in a FILE name is ordinary in most of the eleven
    languages this census reads -- `app.test.js`, `types.d.ts`.

    ! Ambiguity is REFUSED, not resolved by preferring one. Two real paths that
    dot alike means the address names both, and picking either would answer a
    question nobody asked. The caller reports it.

    Args:
        name: the dotted path from an address, without the `@place`.
        paths: the paths the census carries.

    Returns:
        The one path whose dotted form is `name`, or "" when none or several do.
    """
    hits = {p for p in paths if dotted(p) == name}
    return hits.pop() if len(hits) == 1 else ""


def place_of(address: str) -> tuple[str, str]:
    """An address split into its dotted path and its place, or two blanks."""
    path, sep, where = address.rpartition("@")
    return (path, where) if sep else ("", "")


def resolve(address: str, blocks: list[dict], code: list[int]) -> list[int]:
    """Which census entries carry this address, as 1-based census indices.

    !! THE INVERSE IS A LOOKUP, NOT ARITHMETIC. `bN` is "the gap after code line
    N", and which entries sit there is a fact the census holds -- an empty
    interval, or a comment run filling the same gap, or both. Recomputing a line
    range from N would answer where the gap IS while the question asked which
    entries are THERE.

    ! Several entries can share one address and that is not an error: `c1` and
    `b1` are different places, but a comment run and the interval it occupies
    are the same place seen twice by a census built before an edit.

    Args:
        address: `pkg.mod.py@b3` or `pkg.mod.py@c3`.
        blocks: the census entries FOR THAT FILE, in census order.
        code: that file's code lines, from `code_lines_of`.

    Returns:
        The 1-based positions within `blocks`, in order. Empty when nothing
        carries it -- which a caller reports rather than treating as "none".
    """
    return [i for i, b in enumerate(blocks, 1) if stable(b, code) == address]


def code_lines_of(text: str, blocks: list[dict]) -> list[int]:
    """The 1-based line numbers holding code, in order.

    ! The same rule `census.code_lines` applies, over census entries as DICTS:
    a comment or docstring occupies its lines entirely, a trailing comment and
    an interval pass through, and a block that does not occupy its whole first
    line leaves that line as code.
    """
    occupied: set[int] = set()
    for b in blocks:
        if b.get("kind") in ("trailing-comment", "interval"):
            continue
        start, end = b.get("start"), b.get("end")
        if not isinstance(start, int) or not isinstance(end, int):
            continue
        occupied.update(range(start, end + 1))
        if not b.get("whole_lines", True):
            occupied.discard(start)
    return [
        n
        for n, line in enumerate(text.splitlines(), 1)
        if line.strip() and n not in occupied
    ]


def stable(block: dict, code: list[int]) -> str:
    """This block's address in code-line terms, or "" if it has no place.

    Args:
        block: one census entry, as a dict.
        code: the file's code lines, from `code_lines_of`.

    Returns:
        `path@cN` when the block sits ON code line N, `path@bN` when it sits in
        the gap after code line N. ! "" when the census entry carries no usable
        range -- reported by the caller, never guessed at.
    """
    path = dotted(str(block.get("path", "")))
    start = block.get("start")
    if not isinstance(start, int):
        return ""
    if block.get("kind") in SHARES_ITS_LINE and start in code:
        return f"{path}@{ON}{code.index(start) + 1}"
    # !! READ FROM `edit_start`, THE STATED INSERTION POINT, and not from the
    # addressing range. A file whose only code line is line 1 -- every one-line
    # `__init__.py` in every package -- emits TWO intervals both spanning
    # `1-1`, the gap BEFORE that line and the gap AFTER it, and
    # `census.address` cannot tell them apart. Their `edit_start` can: 1 and 2.
    # Counting the code lines before that point names them `b0` and `b1`.
    #
    # ! NO COUNTER, deliberately. This is a pure function of one entry and its
    # file's code lines, so nothing depends on traversal order. A draft that
    # accumulated a running count while walking the census was refused -- Roy,
    # 2026-08-18: a name that depends on the walk "is absolutely filled with
    # edge cases and incrementing problems and ordering problems".
    #
    # ! A CENSUS WITHOUT THE FIELD IS REFUSED, not guessed at. Falling back to
    # `start` answers confidently and wrongly -- it is the range that cannot
    # separate the two gaps of a one-line file, which is the whole reason this
    # reads `edit_start`. `galley.py` refuses an old census for the same reason,
    # and the one default that was tried there put a deleted statement back.
    at = block.get("edit_start")
    if not isinstance(at, int):
        return ""
    return f"{path}@{GAP}{sum(1 for n in code if n < at)}"


def main() -> int:
    """Print every census entry's line address beside its stable one.

    Returns:
        0 when every entry was addressed, 1 when any could not be, 2 when the
        census or a file could not be read.
    """
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--census", required=True, help="the census JSON")
    ap.add_argument("--repo", default=".", help="repo root the paths are under")
    ap.add_argument(
        "--check",
        action="store_true",
        help="verify every address resolves back to its own block, and stop",
    )
    ap.add_argument(
        "--resolve",
        metavar="ADDRESS",
        help="an address in, the LINES that cover it out -- read it against a "
        "census of the file as it is NOW",
    )
    args = ap.parse_args()

    try:
        loaded = json.loads(Path(args.census).read_text(encoding="utf-8"))
    except READ_ERRORS as e:
        print(f"CANNOT READ {args.census} ({type(e).__name__})")
        return 2
    except json.JSONDecodeError as e:
        print(f"{args.census} is not JSON ({e})")
        return 2
    blocks = loaded.get("blocks", []) if isinstance(loaded, dict) else loaded
    if not isinstance(blocks, list) or not blocks:
        print(f"{args.census} carries no blocks")
        return 2

    repo = Path(args.repo).resolve()
    code: dict[str, list[int]] = {}
    moved: list[str] = []
    for path in sorted({str(b.get("path", "")) for b in blocks}):
        try:
            text = (repo / path).read_text(encoding="utf-8")
        except READ_ERRORS as e:
            print(f"CANNOT READ {path} ({type(e).__name__})")
            return 2
        mine = [b for b in blocks if b.get("path") == path]
        # !! REFUSE A CENSUS OLDER THAN THE FILE, rather than answering from it.
        # Every line number here is read against the tree, so a file edited
        # since the census was built produces confident nonsense -- a place
        # named for code that has moved. `galley.block_matches` already asks
        # exactly this before it splices, for exactly this reason.
        #
        # ! Written after doing it FOUR TIMES in one session: an oracle diff, a
        # reachability call, a coverage figure of 51%, and a `SHARED` row that
        # listed one block. Each time the artifact was three edits old and the
        # answer looked like a defect in the code. A note to remember would have
        # failed a fifth time; this cannot.
        stale = [b for b in mine if not block_matches(text.splitlines(), b)]
        if stale:
            moved.append(f"{path}: {len(stale)} of {len(mine)} blocks no longer match")
        code[path] = code_lines_of(text, mine)
    if moved:
        for line in moved:
            print(f"STALE CENSUS  {line}")
        print(
            "\nThe tree has moved since this census was built, so no address it"
            " names can be trusted. Re-run census.py."
        )
        return 2

    if args.resolve:
        return _resolve_one(args.resolve, blocks, code)
    if args.check:
        return _check(blocks, code)

    unplaced = 0
    for i, block in enumerate(blocks, 1):
        where = stable(block, code.get(str(block.get("path", "")), []))
        if not where:
            unplaced += 1
        kind = block.get("kind", "")
        print(f"{i:4d}  {address(block):<40} {where or 'UNPLACED':<22} {kind}")
    if unplaced:
        print(f"\n{unplaced} entries could not be addressed.")
    return 1 if unplaced else 0


def _resolve_one(address: str, blocks: list[dict], code: dict[str, list[int]]) -> int:
    """An address in, the LINES that now cover it out.

    !! THIS IS THE DIRECTION STAGE 8 NEEDS, and it needs it because 7b has
    already written. Roy, 2026-08-18: *"in goes an address out comes the line
    numbers that cover that address ... particularly important after 7b and
    stage 8 wants to look something up to double check."* Every line number a
    record carried is stale by then; the ADDRESS is not, so a census of the
    file AS IT IS NOW turns it back into lines to read.

    ! Census the CURRENT file, not the one the run started from. The address is
    what survives an edit; the lines are what moved, and reading a pre-edit
    census here would hand back exactly the numbers 7b invalidated.

    ! Several entries can answer to one address -- a docstring and the comment
    run beneath it sit in the same gap -- so every match is printed. Measured
    2026-08-18: 12 such places in this repo's own 13 shipped scripts.

    Returns:
        0 when the address named something, 1 when nothing carries it.
    """
    path, where = place_of(address)
    if not where:
        print(f"{address!r} is not an address -- it needs a `@place`")
        return 2
    real = undot(path, sorted(code))
    if not real:
        print(f"no file in this census dots to {path!r}")
        return 1
    mine = [b for b in blocks if str(b.get("path", "")) == real]
    hits = resolve(address, mine, code[real])
    if not hits:
        print(f"{address} names no entry in this census")
        return 1
    for i in hits:
        block = mine[i - 1]
        print(
            f"{real}:{block.get('start')}-{block.get('end')}\t{block.get('kind', '')}"
        )
    return 0


def _check(blocks: list[dict], code: dict[str, list[int]]) -> int:
    """Does every address resolve back to the one block that carries it?

    !! THE REFERENCE HAS TO MATCH THE ANCHOR, and that is the whole worth of an
    address. Roy, 2026-08-18: an agent will grep and read the file anyway, so
    the lookup is convenience -- what a citation buys is that it names the place
    it claims. An address two blocks answer to resolves to the wrong prose, and
    nothing downstream can tell.

    ! THE SAME SHAPE `source_problem` ALREADY ENFORCES ON `SOURCES`. Roy: "same
    on the sources". There a citation carries `file:line | verbatim` and the
    check resolves the line and looks for the words; here an address carries a
    place and the check resolves it back to the entry. Both say: the reference
    is only worth what re-reading it proves.

    ! Two reports, and only the first is a fault. UNADDRESSED means the census
    cannot name the place at all -- no `edit_start`, or no position -- and
    nothing can cite it. SHARED means several blocks sit in one gap, which is
    ordinary and true: a docstring and the comment run under it are both after
    the same code line. It is reported because citing that address ALONE would
    resolve to the wrong one of them; the record's `block` index is what
    separates them.

    Returns:
        1 when anything is UNADDRESSED, 0 otherwise. ! A shared place does not
        fail the check -- it is a fact about the file, and refusing it would
        refuse every docstring with a comment beneath it.
    """
    unaddressed: list[str] = []
    shared: dict[str, list[str]] = {}
    for path, lines in sorted(code.items()):
        mine = [b for b in blocks if str(b.get("path", "")) == path]
        for i, block in enumerate(mine, 1):
            where = stable(block, lines)
            if not where:
                unaddressed.append(f"{path} entry {i}: {address(block)}")
                continue
            if len(resolve(where, mine, lines)) > 1:
                shared.setdefault(where, []).append(
                    f"{address(block)} {block.get('kind', '')}"
                )
    for line in unaddressed:
        print(f"UNADDRESSED  {line}")
    for where, rows in sorted(shared.items()):
        print(f"SHARED       {where}  <- {' | '.join(rows)}")
    named = len(blocks) - len(unaddressed)
    print(f"\n{named} of {len(blocks)} blocks addressed over {len(code)} files.")
    if shared:
        # ! Advice only where it applies. Printing it against zero shared places
        # tells a reader to guard something that did not happen.
        print(
            f"{len(shared)} places hold more than one block"
            f" ({sum(len(v) for v in shared.values())} blocks) -- cite the census"
            f" index alongside the address for those."
        )
    if unaddressed:
        print(
            f"{len(unaddressed)} blocks could not be addressed at all."
            " A census with no `edit_start` cannot name a gap; re-run census.py."
        )
    return 1 if unaddressed else 0


if __name__ == "__main__":
    sys.exit(main())
