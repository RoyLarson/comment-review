"""An address that survives the edits this tool makes.

    python addresser.py --census census.json --repo D

`address()` names a block against the CODE -- `pkg:core.py@a5`. The form it
replaced named it by LINE, `a.py:33-34`, which answers "where is this in the file
I just read" and cannot answer "which place is this": this tool EDITS PROSE, and
every prose edit moves the line numbers of the code below it, so two files
differing only in comments disagree about where the same statement is.
`line_address()` still reads the old form, warns, and is kept only to parse runs
already recorded.

!! AN ADDRESS IS NOT A SPAN OF LINES. EVERY LINE HAS EXACTLY ONE ADDRESS, AND A
BLOCK IS JUST THE LINES THAT SHARE ONE. Ruled 2026-08-19. ! Read it as a range
and the old system is back under a new name: you start asking which lines a
block "covers", whether two blocks overlap, and how wide to make an addressing
range -- all questions a line-numbered address had and an address does not.
Three sessions in one day reached for a range after this was settled; it is
written here because the reflex is strong, not because it is subtle.

! An ANCHOR is the exception that proves it. A declaration carries prose at
several addresses -- the `b` above it, the `c` beside it, its own `a`, the `b`s
in its body -- so an anchor has many addresses. A LINE still has one.

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

! What MAKES it constant across this tool's own work is stage 7b's CODE CHECK.
It does NOT prove the code byte-identical, and saying so overstates it: for
Python it compares an `ast.dump`, so the bytes may differ while the statements
and their ORDER do not; elsewhere it compares the stripped text. Either way what
holds is that the Nth code line is still the same statement -- which is exactly
what an ordinal counts. The line numbers move with the prose; the ordinal does
not.

! `ast.dump` would carry every DOCSTRING into that fingerprint, so rewriting one
-- the commonest edit this system makes -- would read as a code change.
`_blank_docstrings` empties each docstring's value before the dump: its CONTENT
is out of the proof, its PRESENCE is not. ! So adding or deleting a docstring
still changes the body's shape and still fails -- filed as
`TODO/the-code-check-refuses-add-and-drop-on-a-docstring.md`, and the reason an
`add` on a declaration cannot be written today.

!! AND IT PROVES NOTHING AT ALL ON AN UNPROVABLE FILE, which is the hard
exception this scheme rests on and must name. `prove_unchanged` returns
`unprovable` for a comment delimiter sharing a line with code, for an
unterminated block comment, and for a census that disagrees with the file. Such
a run is REPORTED and counted a failure rather than passed -- so there is no
stage 8 to hand an address to, and the guarantee above is never claimed for a
file it does not cover.

! The numbering is invariant by construction rather than by luck -- but only
while the enumeration underneath it is complete.

Three series, because prose answers to one of exactly three subjects:

    package:core.py@a5    the 5th DECLARATION's documentation
    package:core.py@c3    ON code line 3 -- shares the line with the statement
    package:core.py@b3    the GAP after code line 3, before code line 4

! `b0` is the gap before the first code line; `bN` after the last. A file with N
code lines has N+1 gaps, and every comment run and empty interval sits in one.

!! `b` AND `c` ARE SEPARATE ON PURPOSE. `c3` says this prose belongs BESIDE code
line 3; `b3` says it belongs ABOVE code line 4. Roy, 2026-08-18: the split
"allows the editors to say this single line edit belongs next to the code not
above the code" -- an editorial choice line numbers conflated, because both sit
on adjacent lines.

!! THE SAME NUMBER NAMES DIFFERENT STATEMENTS IN THE TWO SERIES, and reading it
otherwise attaches a comment one statement too high. `c3` is ON the 3rd code
line; `b3` is the gap AFTER it, so the statement `b3` sits above is the 4th.
Every code line N therefore owns two folios -- `b(N-1)` above it and `cN` beside
it -- and a DECLARATION owns those plus its own `a`, which is why an anchor can
carry blocks from all three series.

!! `a` IS SEPARATE FOR A DIFFERENT REASON: IT NAMES A SUBJECT, NOT A POSITION.
A docstring is about its DECLARATION, and `a0` is the module with `a1..aN` its
declarations in source order. Roy, 2026-08-18: *"a docstring is about the thing
above not the thing below"* -- so the direction question disappears, and Python's
docstring after its `def` and Rust's `///` before its `fn` number alike.

! Which declaration a doc belongs to is the CENSUS's to state and never this
module's to infer, because it is language-dependent and a parser knows it while
a position does not.

!! THE `a` NUMBER COUNTS DECLARATIONS, NOT CODE LINES, AND THAT IS A RULING.
Numbering each declaration by the `c` of its own `def` line would put all three
series on one count and was REJECTED 2026-08-19. Roy: `a` as "the module, class,
function, method definitions in order ... will make it easier for the agents to
use, vs having to cross-reference where cs are and then jump to there to see the
as." `a5` read directly is "the 5th definition in this file"; aligned to code
lines it is a number that means nothing until it is resolved against another
series.

!! THE SAME PLACE IS THE SAME ADDRESS WHETHER PROSE FILLS IT OR NOT, which is
the property line numbers cannot give. A comment block occupying three lines and
an empty interval in the same position are both `b1`; a documented and an
undocumented declaration are both `a5`. So a finding can say where prose belongs
in a file that does not have it yet, and two versions of a file compare place by
place.

!! AN ADDRESS IS A SINGLE FACT, and the `a` series is what makes it one.
Measured 2026-08-18 over 9,975 blocks in this repo, 28 places were answered by
two blocks -- and 28 of 28 were a docstring sharing a gap with the comment run
beneath it, because a docstring was being named for the gap it sat in rather
than for the declaration it is about. With `a` the docstring leaves the `b`
series: re-measured over 10,744 blocks, 0 shared places.

! So an address alone identifies a place, and a record needs nothing beside it.
`--check` re-reads that claim on every run rather than trusting this paragraph.

!! BOTH NAMINGS LIVE HERE, which is what the module is named for -- `address`,
and the `line_address` it replaced. One owner is what stops them drifting: they
were computed in two modules for an hour and agreed, which is exactly the
property that cannot be relied on.
"""

import argparse
import json
import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pcst import OCCUPIES_NOTHING  # noqa: E402  -- path shim must run first
from repo import READ_ERRORS  # noqa: E402  -- path shim must run first

ON = "c"
GAP = "b"
DECLARED = "a"


def line_address(block: dict) -> str:
    """DEPRECATED. `path:start-end` -- how this system named a block until 0.2.4.

    !! IT IS DEPRECATED BECAUSE IT IS TRUE OF ONE FILE STATE ONLY, and this
    tool edits prose: every prose edit moves the line numbers of the code below
    it. Roy ruled it out 2026-08-18 -- the one reason to keep reading it is to
    parse RUNS ALREADY RECORDED, so `evidence/` can be compared against the
    format that replaced it. `address()` is that format.

    !! IT WARNS ON EVERY CALL, deliberately. Roy: "any function method or
    otherwise that uses that form gets a deprecated warning on it now. To make
    certain it comes out." A note would have to be found; this arrives at
    whoever runs the code. `tests/test_addresser.py` holds the shipped tree to
    zero callers outside the legacy reader.

    ! It was one format with one owner, and that is why it is still readable:
    the four sites that wrote it had drifted, and the one measured divergence
    cost 268 refusals in a single run, every one of them a correct address.

    !! IT NAMES TWO DIFFERENT THINGS AND THE FORMAT CANNOT TELL YOU WHICH.
    On a block that HOLDS prose, `start-end` is the lines that prose occupies,
    inclusive. On an INTERVAL it is the two lines of CODE that BOUND a gap --
    `a.py:33-34` there means "between 33 and 34", where the same string on a
    comment means "lines 33 through 34".

    ! The gap is not necessarily empty of LINES: it is whatever sits between
    those two, nothing or blank lines, and `reviewer-brief.md` tells a reviewer
    its `change` replaces all of it. What it holds no more of is PROSE, which is
    why an interval is always `0L`. Read the KIND, or that count, to know which
    reading applies -- a block holding prose is never `0L`.

    !! AND IT IS TRUE OF ONE FILE STATE ONLY. This tool EDITS PROSE, and every
    prose edit moves the line numbers of the code below it, so an address is
    valid for the file its census was built from and no other. Measured
    2026-08-18 on a prose-only edit to a single docstring: 2 of 3 prose blocks
    took a NEW line address, and 0 of 3 took a new one from `addresser.py`,
    which names a place against the CODE rather than the lines. Use this to say
    where a thing is in the file you just read; use the addresser to say which
    PLACE it is across two states of that file.

    ! The consequence is not cosmetic: a range REPLACE over an interval's
    address deletes both bounding statements instead of inserting between them.
    `galley.py` avoids that by branching on `kind == "interval"`, which is a
    consumer inferring what this producer knows -- the record should carry the
    OPERATION instead. Raised by Roy 2026-08-18 reading a filtered census.

    Args:
        block: one census entry, as a dict.

    Returns:
        The block's line address, in the format retired at 0.2.4.
    """
    warnings.warn(
        "line_address() is deprecated: a line address is true of ONE file"
        " state, and this tool edits prose. Use address(), which names a place"
        " against the code. This form is read only to parse runs already"
        " recorded.",
        DeprecationWarning,
        stacklevel=2,
    )
    path = str(block.get("path", "")).replace("\\", "/")
    return f"{path}:{block.get('start')}-{block.get('end')}"


def address(block: dict, code: list[int]) -> str:
    """`pkg:mod.py@b3` -- WHICH PLACE this is, as against where it sits.

    !! `address` NAMES A POSITION; THIS NAMES A PLACE, and only the second
    survives an edit. This tool rewrites prose, and every prose edit moves the
    line numbers of the code below it -- so `path:start-end` is true of one file
    state and no other. A place is counted against the CODE instead:

        pkg:mod.py@a5   the 5th DECLARATION's documentation
        pkg.mod.py@c3   ON code line 3 -- shares the line with the statement
        pkg.mod.py@b3   the GAP after code line 3, before code line 4

    `b0` is the gap before the first code line, `bN` after the last, and every
    comment run and empty interval sits in one of them.

    !! THE `a` SERIES COUNTS DECLARATIONS, WHICH IS WHY IT CANNOT RENUMBER
    UNDER THIS TOOL. `a0` is the module and `a1..aN` its declarations in source
    order, assigned whether or not each holds a docstring. Adding a docstring
    does not add a declaration, so filling `a2` moves nothing; only a CODE
    change shifts the series, and stage 7b proves this tool makes none.

    !! AND IT IS WHAT MAKES AN ADDRESS A SINGLE FACT. Measured 2026-08-18 over
    9,975 blocks in this repo: 28 places were answered by two blocks, and 28 of
    28 were a docstring sharing a gap with the comment run beneath it. A
    docstring is about its DECLARATION, not about the gap it happens to sit in,
    so naming it `bN` put two different subjects at one address. With the `a`
    series the docstring leaves the `b` series and the collision is gone by
    construction rather than by tolerance.

    ! The ordinal is the CENSUS's to state, never this function's to infer.
    Which declaration a docstring documents is language-dependent -- Python's
    subject is the code ABOVE it, Rust's is BELOW -- and a parser knows it while
    a position does not.

    !! IT IS READ FROM `edit_start`, THE STATED INSERTION POINT. A file whose
    only code line is line 1 -- every one-line `__init__.py` -- emits TWO
    intervals both spanning `1-1`, the gap before that line and the gap after
    it, and `address` cannot tell them apart. Their `edit_start` can: 1 and 2.

    ! The path is FLATTENED on `:` and KEEPS its extension, so `b.py` and `b.rs` cannot
    collide in a repo holding both -- which this census supports by design.

    ! An ADDRESS is the whole citation, `pkg:mod.py@b3`; the FOLIO is the `b3`
    half of it, which is what `folio_of` returns. ! It is not called a PLACE:
    measured 2026-08-18, `place` appears 119 times in the shipped tree and every
    one is ordinary English -- including `ownership-context`'s own instruction,
    *"still be in the wrong place"*, read by the role whose whole remit is
    placement. A term of art there would put a second meaning on the sentence
    that role works from. `folio` is a leaf's number in publishing, which is
    what `b3` is, and it collides with nothing.

    Args:
        block: one census entry, as a dict.
        code: that file's code lines, in order, from `code_lines`.

    Returns:
        The block's address, or "" when it carries no usable position.
    """
    path = flatten(block.get("path", ""))
    start = block.get("start")
    if not isinstance(start, int):
        return ""
    # The census STATES the ordinal; -1 says this block documents no declaration.
    declares = block.get("declares", -1)
    if isinstance(declares, int) and declares >= 0:
        return f"{path}@{DECLARED}{declares}"
    # !! ONE FACT DECIDES THIS, AND THE PRODUCER STATES IT. `edit_column` is
    # non-zero exactly when code precedes the prose on its first line -- a
    # trailing comment, a bare `margin`, a block comment opened after a
    # statement. It was decided here from the KIND and in `code_lines_of` from
    # the block, and the two disagreed on the one kind that is in neither list: a
    # `comment` opened mid-line took a `b` folio for a line it sits ON, so that
    # folio named the comment AND the gap. Measured 2026-08-19 on
    # `let b = 2; /* opens`.
    if block.get("edit_column", 0) and start in code:
        return f"{path}@c{code.index(start)}"
    at = block.get("edit_start")
    if not isinstance(at, int):
        return ""
    return f"{path}@b{sum(1 for n in code if n < at)}"


#: The character that joins path segments in an address. A path may not hold it
#: -- Windows forbids it outright, and `census.py` refuses a POSIX path that
#: does -- which is what makes `flatten` invertible. See `flatten`.
SEPARATOR = ":"


def flatten(path: str) -> str:
    """`pkg/sub/mod.py` as `pkg:sub:mod.py` -- the whole path, extension kept.

    !! THE ADDRESS IS THE FULL PATH from the runner's root, not the file name.
    Roy, 2026-08-18: "the address is the full thing not just `__init__@b0`".
    Files form a tree, so two complete paths differ somewhere, and the
    separator below carries that difference through into the address.

    !! THE EXTENSION STAYS. Dropping it reads better and reintroduces collisions
    the moment a repo holds `b.py` beside `b.rs` -- which this census supports by
    design, eleven languages in one run. Roy ruled it 2026-08-18: "we could have
    mixed languages in the system with the same names that without that we are
    back to collisions."

    !! THE SEPARATOR IS A CHARACTER A PATH CANNOT HOLD, and that is what makes
    this INVERTIBLE. It was `.` until 2026-08-19, and a dot is ordinary in a
    filename -- `app.test.js`, `types.d.ts` -- so `a/b.py` and `a.b.py` both read
    `a.b.py` and every one of their addresses collided. Roy: *"lets use an
    illegal symbol for the separator then."*

    ! `:` is the one Windows forbids that is NOT shell-special, so an address is
    safe as a bare command-line argument where `<`, `>`, `|`, `?` and `*` are
    not. Measured 2026-08-19 over 2,472 source paths in seven corpora: zero hold
    any of the seven. ! POSIX forbids only `/` and NUL, so a POSIX path CAN
    hold a colon and this would be ambiguous again -- `census.py` refuses such a
    file rather than addressing it.
    """
    return str(path).replace("\\", "/").replace("/", SEPARATOR)


def unflatten(name: str, paths: list[str]) -> str:
    """The real path a flattened one names, or "" if the census cannot say.

    ! It resolves against the CENSUS rather than by string surgery, because the
    census is what knows which paths exist. With `:` as the separator the form
    is invertible, so this now answers for exactly one path or none.

    ! Ambiguity is still REFUSED rather than resolved by preferring one. It was
    reachable while the separator was `.`; it is kept because `census.py`'s
    refusal is what makes it unreachable, and a reader here should not have to
    know that to trust the answer.

    Args:
        name: the flattened path from an address, without the `@folio`.
        paths: the paths the census carries.

    Returns:
        The one path whose flattened form is `name`, or "" when none or several
        do.
    """
    hits = {p for p in paths if flatten(p) == name}
    return hits.pop() if len(hits) == 1 else ""


def folio_of(address: str) -> tuple[str, str]:
    """An address split into its flattened path and its folio, or two blanks."""
    path, sep, where = address.rpartition("@")
    return (path, where) if sep else ("", "")


def resolve(address: str, blocks: list[dict]) -> list[int]:
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
        address: `pkg:mod.py@b3` or `pkg:mod.py@c3`.
        blocks: the census entries FOR THAT FILE, in census order.

    Returns:
        The 1-based positions within `blocks`, in order. Empty when nothing
        carries it -- which a caller reports rather than treating as "none".
    """
    return [i for i, b in enumerate(blocks, 1) if stable(b) == address]


def for_anchor(anchor: str, series: str, blocks: list[dict]) -> list[dict]:
    """The blocks of one SERIES belonging to one anchor -- `go`'s `c`, say.

    !! AN ANCHOR OWNS A PLACE IN EVERY SERIES, and asking for one by POSITION
    breaks the moment a language puts it elsewhere. Python's docstring sits
    AFTER its `def` and Rust's `///` BEFORE its `fn`, so "the block above the
    declaration" names the doc in one language and the comment above it in the
    other. This asks the CENSUS, which parsed the file, instead of counting.

    The three, for a declaration:

      a   its documentation -- the docstring, or the place one would go
      c   the room BESIDE its opening line -- a trailing comment, or the place
      b   the gap ABOVE its opening line -- a comment run, or the place

    ! The MODULE has no line to open on, so it has an `a` and no `c`; its `b`
    is the gap before the first code line, which is where a licence header or
    a shebang sits.

    ! It returns a LIST because a census may carry none -- a language whose
    tier resolves no anchors at all -- and the caller reports that rather than
    receiving a guess. More than one is a census defect `--check` reports.

    Args:
        anchor: the declaration's name, as the census stamped it.
        series: `a`, `b` or `c`.
        blocks: the census entries. Pass the FULL census; a filtered one is
            missing exactly the empty places this is most often asked for.

    Returns:
        The matching entries, in census order.
    """
    mine = [b for b in blocks if str(b.get("anchor", "")) == anchor]
    if series == DECLARED:
        return [
            b for b in mine if isinstance(b.get("declares"), int) and b["declares"] >= 0
        ]
    at = next(
        (b.get("declared_at") for b in mine if isinstance(b.get("declared_at"), int)),
        0,
    )
    path = {str(b.get("path", "")) for b in mine}
    here = [b for b in blocks if str(b.get("path", "")) in path]
    if not at:
        # !! THE MODULE HAS NO OPENING LINE, so it has no `c` and its `b` is
        # `b0` by definition -- the gap before the first code line, which is
        # where a licence header or a shebang sits. Every other anchor without
        # a line is a tier that resolved no declaration, and has neither.
        if series == GAP and any(b.get("declares") == 0 for b in mine):
            return [b for b in here if stable(b).endswith(f"@{GAP}0")]
        return []
    if series == ON:
        return [b for b in here if b.get("start") == at and b.get("end") == at]
    if series == GAP:
        # ! The gap ABOVE the declaration: the block whose lines end just before
        # it. An empty gap holds no line, so it answers by its EDIT range.
        return [
            b
            for b in here
            if str(b.get("address", "")).split("@")[-1].startswith(GAP)
            and (b.get("end") == at - 1 or b.get("edit_end") == at - 1)
        ]
    return []


def code_lines_of(text: str, blocks: list[dict]) -> list[int]:
    """Which lines of this file are LINES OF CODE, at the tier the census ran.

    A line is code when it holds something that is not blank and not prose. The
    two tiers cannot answer that identically, and the difference is the
    docstring: `tokenized` knows a string literal is a declaration's
    documentation, `lexical` knows only what its comment-syntax record spells.
    So a block's BOUNDS are tier-dependent while its CONTENT is not.

    ! A `trailing-comment` sits ON a code line, so that line stays code. A
    `comment` or `docstring` block occupies its lines entirely, so those lines
    are not. An `interval` occupies nothing, which is what makes this safe to
    run over a census that already holds intervals.

    !! A BLOCK'S FIRST LINE IS STILL CODE WHEN CODE PRECEDES ITS TEXT.
    `int b = 2; /* opens` spans from that line, and taking the whole span
    dropped the statement from the code set, moving every interval boundary
    below it.

    !! THE BLOCK SAYS SO, via `edit_column`. This tested whether the stored
    text was a proper SUFFIX of the physical line, which is an inference and
    was wrong in both directions: `blocks_stdlib` stores the WHOLE line for a
    trailing comment, so the test never fired for one -- and a block comment
    opened after a statement had its declaration line dropped from the code
    set, moving every interval boundary in the file. Measured 2026-08-18.

    ! It takes DICTS, so it reads a census off disk and a census still being
    built alike -- `census.code_lines` is this function over its own `Block`s.
    An address counts code lines, so the count has to be the same one the
    census used or the two disagree about what `@b3` means.
    """
    occupied: set[int] = set()
    for b in blocks:
        if b.get("kind") in OCCUPIES_NOTHING:
            continue
        start, end = b.get("start"), b.get("end")
        if not isinstance(start, int) or not isinstance(end, int):
            continue
        occupied.update(range(start, end + 1))
        if b.get("edit_column", 0):
            occupied.discard(start)
    return [
        n
        for n, line in enumerate(text.splitlines(), 1)
        if line.strip() and n not in occupied
    ]


def stable(block: dict) -> str:
    """The place the census STAMPED on this block, or "" if it carries none.

    !! IT READS; `place` COMPUTES. One implementation, one caller that runs it
    -- `census_for`, which holds the file text and the finished block list at
    once -- and everything downstream reads the result. Two computations that
    agree today is not the property wanted, because only one of them can be
    right tomorrow.

    ! "" means the census predates the field. A caller REPORTS that rather than
    deriving a place from a census that never had one.
    """
    return str(block.get("address", ""))


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
    ap.add_argument(
        "--check",
        action="store_true",
        help="verify every address resolves back to its own block, and stop",
    )
    ap.add_argument(
        "--anchor",
        metavar="NAME",
        help="a declaration's name -- with --series, the address of that place",
    )
    ap.add_argument(
        "--series",
        choices=(DECLARED, GAP, ON),
        help="which place OF that anchor: a its documentation, b the gap above"
        " its opening line, c the room beside it",
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

    # !! NO STALENESS SWEEP. This module answers about the CENSUS IT WAS GIVEN,
    # and every question it takes is census-internal: does each address resolve
    # to one block, what lines does this census say an address names, which
    # place is this anchor's `c`. None of them reads the tree.
    #
    # !! CHECKING THE FILE WOULD ASSERT THAT LINE NUMBERS STILL MATTER, which is
    # the thing an address exists to stop mattering. Roy, 2026-08-19: *"not
    # necessary for addresser to do the staleness sweep as long as the original
    # census is still an available document ... it doesn't matter that the file
    # changed lines underneath it. In a small way it is the addresser stating
    # the line numbers matter still."*
    #
    # ! A sweep WAS here, added after four artifacts three edits old were each
    # read as a defect in the code. That failure was real and the guard was in
    # the wrong module: staleness matters where a file is WRITTEN, and
    # `galley.block_matches` already refuses a stale range before it splices.
    # Here it refused a census built seconds earlier on every non-Python file
    # carrying a trailing comment, with a message that re-running never fixed --
    # and it masked a genuine collision `--check` exists to report.
    #
    # ! THE CALLER CHOOSES THE CENSUS, which is what makes this safe. Stage 8
    # censuses the file as it now stands and resolves against that, so the two
    # agree by construction rather than by inspection.

    if args.anchor:
        if not args.series:
            print("--anchor needs --series: a, b or c")
            return 2
        return _for_anchor(args.anchor, args.series, blocks)
    if args.resolve:
        return _resolve_one(args.resolve, blocks)
    if args.check:
        return _check(blocks)

    unplaced = 0
    for i, block in enumerate(blocks, 1):
        where = stable(block)
        if not where:
            unplaced += 1
        kind = block.get("kind", "")
        print(f"{i:4d}  {stable(block) or 'UNPLACED':<34} {kind}")
    if unplaced:
        print(f"\n{unplaced} entries could not be addressed.")
    return 1 if unplaced else 0


def _resolve_one(address: str, blocks: list[dict]) -> int:
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
    path, where = folio_of(address)
    if not where:
        print(f"{address!r} is not an address -- it needs a `@place`")
        return 2
    real = unflatten(path, sorted({str(b.get("path", "")) for b in blocks}))
    if not real:
        print(f"no file in this census flattens to {path!r}")
        return 1
    mine = [b for b in blocks if str(b.get("path", "")) == real]
    hits = resolve(address, mine)
    if not hits:
        print(f"{address} names no entry in this census")
        return 1
    for i in hits:
        block = mine[i - 1]
        print(
            f"{real}:{block.get('start')}-{block.get('end')}\t{block.get('kind', '')}"
        )
    return 0


def _for_anchor(anchor: str, series: str, blocks: list[dict]) -> int:
    """Print the address of one anchor's place in one series.

    Returns:
        0 when a place was named, 1 when the census carries none for that
        anchor and series -- which is a fact about the run, not a fault: a
        language whose tier resolves no anchors has none to give.
    """
    found = for_anchor(anchor, series, blocks)
    if not found:
        known = sorted({str(b.get("anchor")) for b in blocks if b.get("anchor")})
        print(f"no `{series}` place for anchor {anchor!r}")
        if known:
            print(f"  anchors this census carries: {', '.join(known[:12])}")
        return 1
    for b in found:
        where = stable(b)
        span = f"{b.get('start')}-{b.get('end')}"
        print(f"{where}	{span}	{b.get('kind', '')}	{b.get('anchor', '')}")
    return 0


def _check(blocks: list[dict]) -> int:
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
    for path in sorted({str(b.get("path", "")) for b in blocks}):
        mine = [b for b in blocks if str(b.get("path", "")) == path]
        for i, block in enumerate(mine, 1):
            where = stable(block)
            if not where:
                unaddressed.append(
                    f"{path} entry {i}: lines {block.get('start')}-{block.get('end')}"
                )
                continue
            if len(resolve(where, mine)) > 1:
                shared.setdefault(where, []).append(
                    f"{block.get('start')}-{block.get('end')} {block.get('kind', '')}"
                )
    for line in unaddressed:
        print(f"UNADDRESSED  {line}")
    for where, rows in sorted(shared.items()):
        print(f"SHARED       {where}  <- {' | '.join(rows)}")
    named = len(blocks) - len(unaddressed)
    files = len({str(b.get("path", "")) for b in blocks})
    print(f"\n{named} of {len(blocks)} blocks addressed over {files} files.")
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
