"""The `addresser` command: its argument parsing and its exit code.

The work is `reading.addresser`; this is only the console face of it.

!! A MODULE DOES ONE JOB AND HAS NO CLI; A FLOW CALLS MODULES;
A COMMAND EXPOSES A FLOW. Ruled 2026-08-24 -- `decision-log.md Process: #12`.
"""

import argparse
from collections.abc import Sequence
from pathlib import Path

from comment_review.binder.addresses import _by_path, resolve, stable, unaddressed
from comment_review.binder.binder import Binder
from comment_review.flows.page_for import page_of
from comment_review.flows.proof_io import load_binder
from comment_review.machine.constants import text_lines
from comment_review.reading.addresser import (
    DECLARED,
    SERIES,
    address_for,
    cue_of,
    unflatten,
)
from comment_review.reading.paragraph import Paragraph


def main() -> int:
    """Print every binder entry's ADDRESS and the kind of place it names.

    ! One address column, not two. The LINE form it once printed beside this one
    was deleted 2026-08-20; see `docs/history.md`.

    Returns:
        0 when every entry was addressed, 1 when any could not be, 2 when the
        binder could not be read. ! Only `--line` opens a source file -- the one
        it asks about, at the binder's root; every other question reads the
        binder alone.
    """
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--binder", required=True, help="the binder JSON")
    ap.add_argument(
        "--check",
        action="store_true",
        help="verify every address resolves back to its own paragraph, and stop",
    )
    ap.add_argument(
        "--file",
        metavar="PATH",
        help="a file of the binder's root, as the binder names it -- with --line"
        " and --series, the address of the place at that line",
    )
    ap.add_argument(
        "--line",
        type=int,
        metavar="N",
        help="a line NUMBER of that file as it was gathered",
    )
    ap.add_argument(
        "--series",
        choices=SERIES,
        help="which place AT that line: a the documentation of the declaration"
        " opening there, b the gap it falls in, c the room beside it, f the"
        " file's own matter",
    )
    ap.add_argument(
        "--resolve",
        metavar="ADDRESS",
        help="an address in, the LINES that cover it out -- read it against a "
        "binder of the file as it is NOW",
    )
    args = ap.parse_args()

    # !! THE LOAD IS THE FLOW'S AND THE DESERIALIZE IS THE CONTAINER'S --
    # `decision-log.md Process: #67`. `flows.proof_io.load_binder` is the read,
    # the decode and `Binder.deserialize`'s refusal, as three steps.
    #
    # ! REFUSED BY NAME, not read as empty. An empty binder is indistinguishable
    # downstream from a run with nothing in scope.
    binder, problems = load_binder(Path(args.binder))
    if binder is None:
        for line in problems:
            print(line)
        return 2
    paragraphs = binder.paragraphs
    if not paragraphs:
        print(f"{args.binder} carries no paragraphs")
        return 2
    # !! THE PER-ENTRY MAPPING CHECK IS GONE, AND THE CONTAINER IS WHY. It read
    # `[b for b in raw if isinstance(b, dict)]` and refused a binder whose rows
    # were not mappings -- a check every reader below needed because the flat
    # row walk
    # handed back whatever it found. `Binder.deserialize` refuses that artifact
    # at the boundary and by name, so what reaches here is `Paragraph`s or
    # nothing. ! **A CONTAINER EARNS ITS KEEP BY DELETING THE RE-CHECKS**, not
    # by sitting beside them: this is the second reader that stopped asking.

    # !! NO STALENESS SWEEP. This module answers about the BINDER IT WAS GIVEN,
    # and every question it takes but one is binder-internal: does each address
    # resolve to one paragraph, what lines does this binder say an address
    # names. Neither reads the tree.
    #
    # !! `--line` IS THE ONE EXCEPTION, AND THE BINDER IS WHY. A role is handed
    # the binder FILTERED to the places holding prose, because ruling on empty
    # places is noise -- so the place an `add` wants is exactly the one the
    # binder does not carry. `decision-log.md Process: #96`: the lookup opens
    # the file at the binder's root and answers from the page. It read the
    # binder's rows until 2026-09-05, and a live run lost four `add`s to
    # *"no `b` place"* on gaps the file plainly had.
    #
    # !! CHECKING THE FILE WOULD ASSERT THAT LINE NUMBERS STILL MATTER, which is
    # the thing an address exists to stop mattering. So long as the binder is
    # the document the caller means, it does not matter that the file has
    # changed lines underneath it.
    #
    # ! STALENESS MATTERS WHERE A FILE IS WRITTEN, and `galley.drifted` used to
    # refuse a moved anchor there -- retired, see `docs/history.md`. A sweep
    # here refuses a binder built seconds earlier on every non-Python file
    # carrying a trailing comment, with a message re-running never fixes, and
    # masks the collisions `--check` exists to report.
    #
    # ! THE CALLER CHOOSES THE BINDER, which is what makes this safe. Stage 8
    # gathers the file as it now stands and resolves against that, so the two
    # agree by construction rather than by inspection.

    if args.line is not None or args.file:
        if not (args.file and args.line is not None and args.series):
            # ! THE SET IS DERIVED, and this line hand-wrote "a, b, c or f"
            # until 2026-08-28 -- the defect `T1.16` names, surviving in a
            # RUNTIME message after it was removed from every help string.
            # `SERIES` comes from the `Series` enum, so adding a series carries
            # this sentence with it.
            print(f"--line needs --file and --series: {', '.join(SERIES)}")
            return 2
        return _at_line(binder, args.file, args.line, args.series)
    if args.resolve:
        return _resolve_one(args.resolve, paragraphs)
    if args.check:
        return _check(paragraphs)

    # !! ASKED, NOT RE-DERIVED -- the rule `_check` states below, which this
    # listing was the one caller to break. It counted every entry with an empty
    # address as UNPLACED, while `--check` on the SAME binder answered that
    # every paragraph was addressed. MEASURED 2026-08-22 on
    # `tests/fixtures/sample.py`: "3 entries could not be addressed", exit 1,
    # beside "18 of 18 paragraphs addressed", exit 0.
    missing = unaddressed(paragraphs)
    for i, paragraph in enumerate(paragraphs, 1):
        # ! UNPLACED names an entry nothing can cite -- the fault this exit code
        # is about. It was preceded by a `symbol` fallback for a paragraph owing
        # no address; leading is the only such paragraph and `bind()` emits no
        # row for one, so the fallback could not fire.
        where = stable(paragraph) or "UNPLACED"
        print(f"{i:4d}  {where:<34} {cue_of(paragraph.address).cue}")
    if missing:
        print(f"\n{len(missing)} entries could not be addressed:")
        for line in missing:
            print(f"  {line}")
    return 1 if missing else 0


def _resolve_one(address: str, paragraphs: Sequence[Paragraph]) -> int:
    """An address in, the LINES that now cover it out.

    !! THIS IS THE DIRECTION STAGE 8 NEEDS, and it needs it because 7b has
    already written. Roy, 2026-08-18: *"in goes an address out comes the line
    numbers that cover that address ... particularly important after 7b and
    stage 8 wants to look something up to double check."* Every line number a
    record carried is stale by then; the ADDRESS is not, so a binder of the
    file AS IT IS NOW turns it back into lines to read.

    ! Gather the CURRENT file, not the one the run started from. The address is
    what survives an edit; the lines are what moved, and reading a pre-edit
    binder here would hand back exactly the numbers 7b invalidated.

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
    real = unflatten(path, sorted({b.path for b in paragraphs}))
    if not real:
        print(f"no file in this binder flattens to {path!r}")
        return 1
    mine = [b for b in paragraphs if b.path == real]
    hits = resolve(address, mine)
    if not hits:
        print(f"{address} names no entry in this binder")
        return 1
    for i in hits:
        paragraph = mine[i - 1]
        span = f"{paragraph.original_start}-{paragraph.original_end}"
        print(f"{real}:{span}\t{cue_of(paragraph.address).cue}")
    return 0


def _at_line(binder: Binder, file: str, line: int, series: str) -> int:
    """Print the address of one series' place at one line of one file.

    !! ANSWERED FROM THE PAGE, NOT FROM THE BINDER'S ROWS. The binder is a
    filtered view and a filter is not the set of places a page has --
    `decision-log.md Process: #96`. The file is opened at the binder's root,
    the tree the binder was gathered from, so the line a role reads off the
    listing is the line this takes.

    ! EACH LINE PRINTED SAYS WHETHER THE BINDER HOLDS THE PLACE. `HELD` means a
    row was seeded there; `ABSENT` means the filter dropped it as holding no
    prose, and a mark may still cite it -- the write end reads the page, not
    the binder (`Process: #97`).

    ! THE FILE'S OWN MATTER ANSWERS TWICE, head and foot, since no line tells
    them apart; a caller chooses by address, the same rule an anchor spelled
    twice already follows.

    Returns:
        0 when a place was named, 1 when the page has no such place at that
        line, 2 when the file could not be read as a page.
    """
    given = Path(file)
    try:
        rel = (
            given.relative_to(binder.root).as_posix()
            if given.is_absolute()
            else given.as_posix()
        )
    except ValueError:
        print(f"{file} is not under the binder's root {binder.root}")
        return 2
    page, why = page_of(binder.root / rel, rel=rel)
    if page is None:
        print(f"{rel} {why}")
        return 2
    count = len(text_lines(page.text))
    if not 1 <= line <= count:
        print(f"{rel} has {count} lines; line {line} is not one of them")
        return 1
    found = page.cues.at_line(line, series)
    if not found:
        what = "holds no code"
        if series == DECLARED:
            what = "declares nothing documentable"
        print(f"line {line} of {rel} {what}, so it has no `{series}` place")
        if series == DECLARED and page.cues.documents(0):
            head = address_for(rel, page.cues.documents(0))
            print(f"  the module's own documentation is {head}")
        return 1
    held = {b.address for b in binder.paragraphs}
    for c in found:
        address = address_for(rel, c)
        state = "HELD" if address in held else "ABSENT"
        print(f"{address}\t{page.cues.anchor_of(c)!r}\t{state}")
    if len(found) > 1:
        print(
            f"\n{len(found)} places answer to line {line} in `{series}`."
            " Choose by ADDRESS."
        )
    return 0


def _check(paragraphs: Sequence[Paragraph]) -> int:
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

    ! Two reports, and only the first is a fault. UNADDRESSED means the binder
    cannot name the place at all -- no `original_start`, or no position -- and
    nothing can cite it.

    !! SHARED IS NOW A FAULT TOO, AND ITS OLD REMEDY IS GONE. It meant several
    paragraphs sat in one gap, and the advice was to cite the binder INDEX
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
    # `gather` and the collator ask the same one.
    missing = unaddressed(paragraphs)
    shared: dict[str, list[str]] = {}
    # ! The path is not read here -- an address already names its own file, and
    # this only needs each file's paragraphs grouped to resolve within one.
    for mine in _by_path(paragraphs).values():
        for paragraph in mine:
            where = stable(paragraph)
            if where and len(resolve(where, mine)) > 1:
                shared.setdefault(where, []).append(
                    f"{paragraph.original_start}-{paragraph.original_end}"
                    f" {cue_of(paragraph.address).cue}"
                )
    for line in missing:
        print(f"UNADDRESSED  {line}")
    for where, rows in sorted(shared.items()):
        print(f"SHARED       {where}  <- {' | '.join(rows)}")
    # !! THE SAME POPULATION `unaddressed` ASKED ABOUT. Counting every paragraph
    # here and only some of them there is what made the sentence false: MEASURED
    # 2026-08-22 over this repo's own scripts, `8542 of 8542 paragraphs
    # addressed` while 392 of them carried no address at all. It is one
    # population now because every row `bind()` emits carries an address --
    # leading is the paragraph that owed none, and no row is made for one.
    named = len(paragraphs) - len(missing)
    files = len(_by_path(paragraphs))
    print(f"\n{named} of {len(paragraphs)} paragraphs addressed over {files} files.")
    if shared:
        # ! Advice only where it applies. Printing it against zero shared places
        # tells a reader to guard something that did not happen.
        print(
            f"{len(shared)} places hold more than one paragraph"
            f" ({sum(len(v) for v in shared.values())} paragraphs) -- cite the binder"
            f" index alongside the address for those."
        )
    if missing:
        print(
            f"{len(missing)} paragraphs could not be addressed at all."
            " A binder with no `original_start` cannot name a gap; re-run gather."
        )
    return 1 if missing else 0
