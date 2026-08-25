"""The `addresser` command: its argument parsing and its exit code.

The work is `reading.addresser`; this is only the console face of it.

!! A LIBRARY MODULE DOES ONE JOB AND HAS NO CLI; A FLOW CALLS LIBRARIES;
A COMMAND EXPOSES A FLOW. Ruled 2026-08-24 -- `decision-log.md Process: #12`.
"""

import argparse
from pathlib import Path

from comment_review.binder.addresses import (
    _by_path,
    for_anchor,
    owes_address,
    resolve,
    stable,
    unaddressed,
)
from comment_review.binder.binder import read as read_binder
from comment_review.binder.binder import rows_of
from comment_review.machine import exceptions
from comment_review.reading.addresser import SERIES, cue_of, unflatten


def main() -> int:
    """Print every census entry's ADDRESS and the kind of place it names.

    ! One address column, not two. The LINE form it once printed beside this one
    was deleted 2026-08-20; see `docs/history.md`.

    Returns:
        0 when every entry was addressed, 1 when any could not be, 2 when the
        census could not be read. ! This module reads no source file -- the
        census is the only input.
    """
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--census", required=True, help="the census JSON")
    ap.add_argument(
        "--check",
        action="store_true",
        help="verify every address resolves back to its own paragraph, and stop",
    )
    ap.add_argument(
        "--anchor",
        metavar="LINE",
        help="a LINE OF CODE, verbatim -- with --series, the address of that place",
    )
    ap.add_argument(
        "--series",
        choices=SERIES,
        help="which place OF that anchor: a its documentation, b the gap above"
        " its opening line, c the room beside it, f the file's own matter",
    )
    ap.add_argument(
        "--resolve",
        metavar="ADDRESS",
        help="an address in, the LINES that cover it out -- read it against a "
        "census of the file as it is NOW",
    )
    args = ap.parse_args()

    try:
        text = Path(args.census).read_text(encoding="utf-8")
    except exceptions.READ_ERRORS as e:
        print(f"CANNOT READ {args.census} ({type(e).__name__})")
        return 2
    # ! REFUSED BY NAME, not read as empty. `rows_of` alone answers `[]` for a
    # file it cannot understand, and an empty binder is indistinguishable
    # downstream from a run with nothing in scope.
    binder, why = read_binder(text)
    if why:
        print(f"{args.census}: {why}")
        return 2
    raw = rows_of(binder)
    if not raw:
        print(f"{args.census} carries no paragraphs")
        return 2
    # !! EVERY ENTRY IS CHECKED, not just the list around them. A census row that
    # is not a mapping cannot carry an address, a kind or a symbol, and every
    # reader below calls `.get` on it -- so a hand-edited or truncated census
    # arrived as an `AttributeError` naming neither the file nor the row.
    # ! It is also what lets the type checker see this list as paragraphs. Before
    # the check, each entry was `object` and three call sites here were reading
    # attributes off it that the annotation said were not there.
    paragraphs: list[dict] = [b for b in raw if isinstance(b, dict)]
    if len(paragraphs) != len(raw):
        print(f"{args.census}: {len(raw) - len(paragraphs)} entries are not paragraphs")
        return 2

    # !! NO STALENESS SWEEP. This module answers about the CENSUS IT WAS GIVEN,
    # and every question it takes is census-internal: does each address resolve
    # to one paragraph, what lines does this census say an address names, which
    # place is this anchor's `c`. None of them reads the tree.
    #
    # !! CHECKING THE FILE WOULD ASSERT THAT LINE NUMBERS STILL MATTER, which is
    # the thing an address exists to stop mattering. So long as the census is
    # the document the caller means, it does not matter that the file has
    # changed lines underneath it.
    #
    # ! STALENESS MATTERS WHERE A FILE IS WRITTEN, and `galley.drifted` refuses a
    # moved anchor there. A sweep here refuses a census built seconds earlier on
    # every non-Python file carrying a trailing comment, with a message
    # re-running never fixes, and masks the collisions `--check` exists to
    # report.
    #
    # ! THE CALLER CHOOSES THE CENSUS, which is what makes this safe. Stage 8
    # censuses the file as it now stands and resolves against that, so the two
    # agree by construction rather than by inspection.

    if args.anchor:
        if not args.series:
            print("--anchor needs --series: a, b, c or f")
            return 2
        return _for_anchor(args.anchor, args.series, paragraphs)
    if args.resolve:
        return _resolve_one(args.resolve, paragraphs)
    if args.check:
        return _check(paragraphs)

    # !! ASKED, NOT RE-DERIVED -- the rule `_check` states below, which this
    # listing was the one caller to break. It counted every entry with an empty
    # address as UNPLACED, while `--check` on the SAME census answered that
    # every paragraph was addressed. MEASURED 2026-08-22 on
    # `tests/fixtures/sample.py`: "3 entries could not be addressed", exit 1,
    # beside "18 of 18 paragraphs addressed", exit 0.
    # ! The half it dropped is the SYMBOL. Leading names no place -- see
    # `SERIES` -- so it owes no address and cannot be cited; `unaddressed` knows
    # that and a re-derivation of it did not.
    missing = unaddressed(paragraphs)
    for i, paragraph in enumerate(paragraphs, 1):
        # ! A paragraph that owes no address shows the SYMBOL it is known by,
        # which is the only handle it has. UNPLACED is kept for an entry nothing
        # can cite -- the fault this exit code is about.
        where = stable(paragraph) or str(paragraph.get("symbol", "")) or "UNPLACED"
        print(f"{i:4d}  {where:<34} {paragraph.get('kind', '')}")
    if missing:
        print(f"\n{len(missing)} entries could not be addressed:")
        for line in missing:
            print(f"  {line}")
    return 1 if missing else 0


def _resolve_one(address: str, paragraphs: list[dict]) -> int:
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
    path, where = cue_of(address)
    if not where:
        print(f"{address!r} is not an address -- it needs a `@place`")
        return 2
    real = unflatten(path, sorted({str(b.get("path", "")) for b in paragraphs}))
    if not real:
        print(f"no file in this census flattens to {path!r}")
        return 1
    mine = [b for b in paragraphs if str(b.get("path", "")) == real]
    hits = resolve(address, mine)
    if not hits:
        print(f"{address} names no entry in this census")
        return 1
    for i in hits:
        paragraph = mine[i - 1]
        span = f"{paragraph.get('start')}-{paragraph.get('end')}"
        print(f"{real}:{span}\t{paragraph.get('kind', '')}")
    return 0


def _for_anchor(anchor: str, series: str, paragraphs: list[dict]) -> int:
    """Print the address of one anchor's place in one series.

    Returns:
        0 when a place was named, 1 when the census carries none for that
        anchor and series -- which is a fact about the run, not a fault: a
        language whose tier resolves no anchors has none to give.
    """
    found = for_anchor(anchor, series, paragraphs)
    if not found:
        known = sorted({str(b.get("anchor")) for b in paragraphs if b.get("anchor")})
        print(f"no `{series}` place for anchor {anchor!r}")
        if known:
            print(f"  anchors this census carries: {', '.join(known[:12])}")
        return 1
    for b in found:
        where = stable(b)
        span = f"{b.get('start')}-{b.get('end')}"
        print(f"{where}	{span}	{b.get('kind', '')}	{b.get('anchor', '')}")
    # !! AN ANCHOR HAS MANY ADDRESSES, so this direction is not a lookup that
    # returns one. Roy, 2026-08-19, on two identical statements in one file:
    # *"for the addresses this is still exact -- for looking up the anchors to
    # get the addresses, not so exact."* `X=2  # initial` and `X=2  # reseting
    # X` are two anchors spelled the same, and the census carries five places
    # under that spelling. Every match is printed and the CALLER picks by
    # address; taking the first would silently rule on the wrong statement.
    if len(found) > 1:
        print(
            f"\n{len(found)} places answer to anchor {anchor!r} in `{series}`."
            " An anchor has many addresses and an address has one anchor, so"
            " two identical lines of code are two anchors spelled alike."
            " Choose by ADDRESS."
        )
    return 0


def _check(paragraphs: list[dict]) -> int:
    """Does every address resolve back to the one paragraph that carries it?

    !! THE REFERENCE HAS TO MATCH THE ANCHOR, and that is the whole worth of an
    address. Roy, 2026-08-18: an agent will grep and read the file anyway, so
    the lookup is convenience -- what a citation buys is that it names the place
    it claims. An address two paragraphs answer to resolves to the wrong prose, and
    nothing downstream can tell.

    ! THE SAME SHAPE `source_problem` ALREADY ENFORCES ON `SOURCES`. Roy: "same
    on the sources". There a citation carries `file:line | verbatim` and the
    check resolves the line and looks for the words; here an address carries a
    place and the check resolves it back to the entry. Both say: the reference
    is only worth what re-reading it proves.

    ! Two reports, and only the first is a fault. UNADDRESSED means the census
    cannot name the place at all -- no `original_start`, or no position -- and
    nothing can cite it.

    !! SHARED IS NOW A FAULT TOO, AND ITS OLD REMEDY IS GONE. It meant several
    paragraphs sat in one gap, and the advice was to cite the census INDEX
    alongside the address -- a field retired 2026-08-19, so a record carries an
    address and an anchor and nothing that tells two such paragraphs apart. The
    one shape that produced it is fixed: a licence header and the run below the
    module docstring both answered to `b0`, and `b0` is now the file's own front
    matter alone.

    Returns:
        1 when anything is UNADDRESSED, 0 otherwise. ! A shared place does not
        fail the check -- it is a fact about the file, and refusing it would
        refuse every docstring with a comment beneath it.
    """
    # ! ASKED, NOT RE-DERIVED. `unaddressed` is the one implementation, and
    # `census.py` and `verdicts.py` ask the same one.
    missing = unaddressed(paragraphs)
    shared: dict[str, list[str]] = {}
    # ! The path is not read here -- an address already names its own file, and
    # this only needs each file's paragraphs grouped to resolve within one.
    for mine in _by_path(paragraphs).values():
        for paragraph in mine:
            where = stable(paragraph)
            if where and len(resolve(where, mine)) > 1:
                shared.setdefault(where, []).append(
                    f"{paragraph.get('start')}-{paragraph.get('end')}"
                    f" {paragraph.get('kind', '')}"
                )
    for line in missing:
        print(f"UNADDRESSED  {line}")
    for where, rows in sorted(shared.items()):
        print(f"SHARED       {where}  <- {' | '.join(rows)}")
    # ! THE SAME POPULATION `unaddressed` ASKED ABOUT, via the same predicate.
    # Counting every paragraph here and only the owing ones there is what made
    # the sentence false.
    owed = [b for b in paragraphs if owes_address(b)]
    exempt = len(paragraphs) - len(owed)
    named = len(owed) - len(missing)
    files = len(_by_path(paragraphs))
    print(f"\n{named} of {len(owed)} paragraphs addressed over {files} files.")
    if exempt:
        # ! SAID, NOT SILENTLY DROPPED. A reader comparing this against the
        # census's own total needs to know why the two differ, and `leading` is
        # the whole of the difference.
        print(f"{exempt} carry a symbol instead, and are owed no address.")
    if shared:
        # ! Advice only where it applies. Printing it against zero shared places
        # tells a reader to guard something that did not happen.
        print(
            f"{len(shared)} places hold more than one paragraph"
            f" ({sum(len(v) for v in shared.values())} paragraphs) -- cite the census"
            f" index alongside the address for those."
        )
    if missing:
        print(
            f"{len(missing)} paragraphs could not be addressed at all."
            " A census with no `original_start` cannot name a gap; re-run census.py."
        )
    return 1 if missing else 0
