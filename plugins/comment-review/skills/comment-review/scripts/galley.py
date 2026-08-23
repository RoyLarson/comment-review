"""The proposed text, SET AS FILES, so it can be read and censused like any tree.

    python galley.py --repo D --census census.json --edits edits.json --out DIR

`--edits` is `{"<address>": "<the replacement text>"}` -- the same address the
record carries, so nothing between stage 5 and the galley has to convert.

A galley is the trial impression: the text set, but not yet made into pages, so
that it can be corrected before anything is committed. That is exactly what
this writes -- every paragraph a stage proposes to change, put on a copy of its
page under `--out`. Nothing under `--repo` is touched.

!! "NOT YET MADE INTO PAGES" AND "A COPY OF ITS PAGE" ARE BOTH TRUE HERE, and
reading the first as a contradiction of the second is the wrong inference this
paragraph invites. Roy, 2026-08-22: *"Galley still works because our pages are
infinite lengths, and can be reordered at will to make them look like one
unordered length."* ! A page here is a FILE: unbounded, no verso, and nothing
pushes its last line onto a next sheet. Making up copy into fixed-height sheets
-- the step a galley precedes -- never happens in this system at all, so setting
text onto a page does not stop it being galley copy.

! AND THE STACK IS ORDER-FREE, which is the second half of what makes the word
hold. Every address carries its own path, so nothing downstream depends on which
page precedes which. MEASURED 2026-08-22: three files censused forward and
reversed gave 179 paragraphs whose address, kind, text and anchor were identical
in both orders. ! Order is load-bearing WITHIN a page -- that is what an
address's cue counts -- and free between them.

!! IT RENDERS; IT DOES NOT RULE. A stage that both produced the galley and
judged it would be MARK and APPLY in one actor, which is the separation the
pipeline exists to keep.

Two things need it, and they needed the same thing:

  round 2   A re-review rules on the SYNTHESISED paragraph -- text on no disk and
            in no census -- so `address_problem` refuses it and `edit_problem`
            measures one claim against one edit where the paragraph now holds
            several. Censusing the galley gives that text a real address and a
            real transcription, so every check in `verdicts.py` works on it
            UNCHANGED.
  stage 7a  What lands at 7b is a paragraph set into a page, and the galley is
            the first time anyone sees the two together. `git diff --no-index`
            over it shows the author what will land, including whether a
            neighbour moved -- which a `CHANGE` cannot show, because each one
            carries only its own surrounding context.

!! IT DOES TWO THINGS AND THEY ARE SEPARATE ACTS. Roy, 2026-08-21: *"galley gets
the old page - updates the old page with the verdict/record/marks and then a
page-setter sets the page to rewrite the output text."*

    RESET   the verdicts are put on the page, by ADDRESS
    SET     `compositor.set_page` turns the page back into text

! THIS MODULE OWNS ONLY THE FIRST. Setting belongs to the compositor, which is
the only writer, and it decides nothing.

!! NO LINE NUMBER APPEARS IN THIS FILE. Until 2026-08-21 the whole module was
line arithmetic -- a splice over `(start, end, column)` ranges applied in
descending order so that earlier edits did not shift later ones, with a
staleness check comparing stored text against the file's lines. Roy: *"how do I
get you to stop thinking in line numbers? You keep defaulting to that and it
makes a mess."* A page addresses its paragraphs, so a replacement is an
assignment and the arithmetic has nothing left to be wrong about. See
`docs/history.md` for the mechanism that was removed.

! A CHANGE THAT CANNOT BE MADE IS REPORTED, NEVER GUESSED. An address no page
carries, or an anchor that moved since the census, stops that file rather than
writing a galley nobody can trust.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import compositor  # noqa: E402  -- path shim must run first
import constants  # noqa: E402  -- path shim must run first
import exceptions  # noqa: E402  -- path shim must run first

# !! THE ONE `cue_of`, since 2026-08-22. This module had a second of its own --
# `str(address).split("@")[-1]` -- and the two DISAGREED on a malformed address:
# a bare `b3` with no `@` came back as the cue `b3` here and as *not an
# address* from `addresser`, which returns two blanks when there is no separator.
# Both were live in one process. ! The shared one answers `(path, cue)`, so
# every site here takes `[1]`.
from addresser import ON, cue_of  # noqa: E402  -- path shim must run first
from lexer import language_for  # noqa: E402  -- path shim must run first
from page import page_for  # noqa: E402  -- path shim must run first
from repo import read_raw  # noqa: E402  -- path shim must run first


def reset(page, edits: dict[str, str]) -> list[str]:
    """Put each replacement on the page, at the address it names.

    !! THE ADDRESS IS THE WHOLE OF THE PLACEMENT. A paragraph knows which place
    it sits in, and the compositor sets the places in order, so a replacement is
    an assignment to one paragraph and nothing below it moves. That is the
    difference between this and the splice it replaces: growing a paragraph from
    one line to four used to shift every range below it.

    !! A PLACE IS NEVER REMOVED -- IT IS VACATED. Places are involatile: the
    place takes the empty sentinel and does not itself disappear, so `drop`
    deletes nothing and the paragraph stays, at the same address, holding no
    lines. That is what keeps it citable afterwards --
    an `add` can fill the very place a `drop` emptied.

    !! `drop` AND THE SOURCE HALF OF A `move` ARE THE SAME OPERATION, and both
    go through `_vacate`. A `move` is expressed as two edits -- the destination
    takes the text, the source takes an empty replacement -- and the source is
    vacated exactly as a `drop` vacates, because in both cases the prose is no
    longer there and the space it introduced is no longer owed.

    ! THE LEADING BELOW IT IS VACATED TOO, for the same reason and by the same
    rule -- the live first key keeps its leading, the dropped one loses it. The
    `d` becomes the empty sentinel; it does not cease to exist.
    Without it the blank line the paragraph introduced stands over whatever
    follows.

    !! AND IT IS AN EDITORIAL DECISION MADE HERE, not in the compositor. It read
    as a side-effect there until 2026-08-22 -- the loop skipped a place that set
    nothing, so its edge was never asked for -- which had the module chartered
    to decide NOTHING carrying out a `drop`. ! It could not have been right
    there in any case: an emptied place and an always-empty one hold the SAME
    empty sentinel, so the compositor cannot tell them apart. Only the EDIT
    knows.

    ! A `c` TAKES ONLY THE PROSE. The compositor sets the line of code and joins
    what sits beside it, so the replacement is the comment and its separator --
    never the statement. That is what makes `c` writable without a column.

    Args:
        page: the page to change, built from the file as it reads NOW.
        edits: address -> the replacement paragraph, as text.

    Returns:
        One sentence per edit that could not be placed. Empty means every one
        landed.
    """
    by_place: dict[str, list] = {}
    # ! The `d` a place owns, so a `drop` can empty it too. Leading carries a
    # SYMBOL and never an address -- it names no place -- so it is found here by
    # that symbol and nowhere by a cue.
    by_symbol = {b.symbol: b for b in page if b.symbol}
    for b in page:
        if b.address:
            by_place.setdefault(cue_of(b.address).cue, []).append(b)
    refused = []
    for address, replacement in edits.items():
        found = by_place.get(cue_of(address).cue)
        if not found:
            refused.append(f"{address}: this page carries no such place")
            continue
        # !! ONE PLACE, ONE PARAGRAPH. Two paragraphs sharing an address was a
        # real defect until 2026-08-21 -- 157 of them in one tree -- and it is
        # the one shape that would make a replacement ambiguous here. It is
        # reported rather than resolved: picking either would write the author's
        # approved text over prose nobody looked at.
        if len(found) > 1:
            refused.append(
                f"{address}: {len(found)} paragraphs share this place, so no"
                " replacement can be placed against it"
            )
            continue
        # !! A REPLACEMENT IS TEXT, AND ONLY AN EMPTY STRING IS A VACATION. This
        # asked whether the value was TRUTHY, so every falsy value took the drop
        # path below and every non-string truthy one reached the SPLITTER.
        # MEASURED 2026-08-22 against a scratch checkout: `{"m.py@b1": null}`
        # exited 0 reporting `1 page(s) set, 0 edit(s) refused` with the comment
        # GONE, and `{"m.py@b1": 123}` died on an uncaught `AttributeError`, on a
        # value with no lines to take.
        # ! A NULL IS NOT A DECISION. `--edits` is machine-written from approved
        # text; a key whose value failed to serialise arrives as `null`, and
        # reading that as "the author asked to delete this" turns a bug upstream
        # into a deletion here, at exit 0.
        if not isinstance(replacement, str):
            refused.append(
                f"{address}: a replacement must be text, not"
                f" {type(replacement).__name__} -- an empty string is the only drop"
            )
            continue
        if replacement:
            found[0].raw_lines = constants.text_lines(replacement)
            continue
        # ! AN EMPTY REPLACEMENT IS A VACATION -- a `drop`, or the source half
        # of a `move`. Anything else leaves the space below untouched, because
        # the separation a reader saw is not the author's to lose by editing the
        # text above it.
        #
        # !! A `c` GIVES UP NO LEADING, and this vacated it unconditionally when
        # `_vacate` was written on 2026-08-22. A `c` sits BESIDE code: dropping
        # the trailing comment leaves the statement exactly where it was, so the
        # blank below it separates that CODE from what follows and was never the
        # comment's to lose. ! `prove_unchanged` cannot see the difference --
        # the AST is identical either way -- so it would land silently at 7b.
        where = cue_of(address).cue
        owns_leading = not where.startswith(ON)
        _vacate(
            found[0],
            by_symbol.get(page.leading.get(where, "")) if owns_leading else None,
        )
    return refused


def _vacate(paragraph, leading) -> None:
    """Empty this place and the space below it, without removing either.

    !! THE EMPTY SENTINEL IS THE POINT: the place takes it, and does not itself
    disappear. Both paragraphs keep their address, their anchor and their
    position in the reading order; they hold no lines. A place that vanished
    could not be cited
    by the `add` that fills it next.

    Args:
        paragraph: the place being vacated.
        leading: the `d` it owns, or None where nothing blank follows it.
    """
    paragraph.raw_lines = []
    if leading is not None:
        leading.raw_lines = []


def drifted(page, census: list[dict]) -> list[str]:
    """Addresses whose ANCHOR is no longer the one the census recorded.

    !! THIS IS THE WHOLE STALENESS CHECK, AND IT ASKS THE WHOLE FILE. Roy,
    2026-08-21, ruling on the scope after a narrower reading was measured: *"If
    the file shifted at all it is dead and so are the edits. There is no way we
    can know if we are setting things correctly ... IT failing loudly is the
    'right' call on any modification to the anchors."*

    !! CHECKING ONLY THE ADDRESS BEING WRITTEN IS NOT ENOUGH, MEASURED. Rename
    `def f():` to `def RENAMED():` and edit a comment inside its body: that
    comment's own address is anchored to `    return 1`, which did not move, so
    a per-address check ALLOWS IT -- and the approved text describing `f` is
    written onto a declaration that no longer carries the name. The paragraph a
    reviewer read did not move; the thing it is ABOUT did.

    !! AND RE-ADDRESSING THE EDITS WOULD NOT SAVE THEM, WHICH IS WHY THERE IS NO
    PARTIAL ANSWER. Roy: *"it seems easy just keep applying until it no longer
    applies, but then the edits also no longer apply ... what is stated in the
    edits could be stale and need something else."*

    ! THE STALENESS IS IN THE TEXT, NOT ONLY IN THE PLACEMENT. A replacement is
    prose ABOUT code, approved against the code as it read. Move that code and
    the sentence can become false where it was true -- a comment that described
    `f` is not made correct by finding the right place to put it on `RENAMED`.
    So there is no re-keying shortcut: the shortcut assumes the words still
    hold, and that is the assumption the shift breaks.

    ! WHAT IS OWED IS A NEW REVIEW, not a new address. Re-censusing and
    re-running is the answer, and it is the author's to trigger.

    ! SO AN UNRELATED APPEND AT THE FOOT OF THE FILE REFUSES THE WHOLE PAGE, and
    that is the rule rather than a cost of it -- measured as case D of the sweep
    above: `X = 1` appended below everything moves the closing gap's anchor.

    ! IT REPLACES A COMPARISON OF STORED TEXT AGAINST THE FILE'S LINES. That one
    asked whether the paragraph still reads as it did, which is a fact about
    lines and needed a case for every kind -- a `c` compared in two halves, an
    empty place compared for emptiness, an undocumented declaration exempted.
    The anchor is one comparison and it holds for every series that has one.

    ! A SERIES WITH NO ANCHOR IS NOT CHECKED, and that is not a hole. Leading
    answers to nothing by ruling, and the file's own matter answers to the
    module -- neither can drift against a line of code, because neither is tied
    to one.

    Args:
        page: the page as the file reads NOW.
        census: the paragraphs the reviewers read.

    Returns:
        One sentence per address whose anchor moved.
    """
    now = {}
    prose_now: dict[str, list[str]] = {}
    for b in page:
        if b.address and b.anchor:
            now[cue_of(b.address).cue] = b.anchor
        if b.address:
            prose_now[cue_of(b.address).cue] = list(b.raw_lines)
    out = []
    for b in census:
        address = str(b.get("address", ""))
        # !! THE PROSE IS CHECKED TOO, and only the anchor was. An anchor is a
        # line of CODE, so a comment edited since the census moved nothing the
        # anchor can see -- and the galley wrote the reviewer's approved text
        # over prose nobody had read. MEASURED 2026-08-22 side by side on one
        # census: a code change refused correctly at exit 1 naming three moved
        # anchors, while replacing one comment with two unreviewed lines gave
        # exit 0 and overwrote both.
        #
        # ! IT IS THE RULE THIS FUNCTION ALREADY QUOTES. Roy: *"If the file
        # shifted at all it is dead and so are the edits."* A prose edit is the
        # file shifting; the anchor comparison simply could not see it.
        #
        # ! ONE COMPARISON, EVERY KIND -- which was the objection to the text
        # check this replaced. That one asked whether the paragraph still READS
        # as it did and needed a case per kind; `raw_lines` is the lines
        # themselves, and the census records them for every paragraph it carries.
        #
        # ! IT ALSO COVERS THE SERIES WITH NO ANCHOR. Leading and the file's own
        # matter answer to no line of code, so the anchor test skipped them
        # entirely; their prose can still be edited, and now that is seen.
        # ! NOTHING WITHOUT AN ADDRESS IS COMPARED AT ALL, so it is asked here
        # rather than in each of the two checks below -- which tested it in
        # opposite directions inside one loop body, with nothing between them
        # that could change the answer.
        if not address:
            continue
        stored = b.get("raw_lines")
        if isinstance(stored, list):
            here_lines = prose_now.get(cue_of(address).cue)
            if here_lines is not None and here_lines != stored:
                out.append(
                    f"{address}: the prose here changed since the census"
                    f" -- {len(stored)} line(s) read, {len(here_lines)} now"
                )
        was = str(b.get("anchor", ""))
        if not was:
            continue
        here = now.get(cue_of(address).cue)
        if here is not None and here != was:
            out.append(
                f"{address}: the census read {was!r}, the file now reads {here!r}"
            )
    return out


def main() -> int:
    """Set a galley of every page an edit touches, and report what refused."""
    # A Windows console is cp1252; one non-ASCII glyph in a report kills the run.
    constants.utf8_console()

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", default=".", help="repo root the census resolves against")
    ap.add_argument("--census", required=True, help="the JSON census these edits cite")
    ap.add_argument(
        "--edits",
        required=True,
        help='JSON: {"<address>": "<replacement paragraph>"}',
    )
    ap.add_argument("--out", required=True, help="directory the galley is written to")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    out = Path(args.out).resolve()
    # !! `--out` MUST BE DISJOINT FROM `--repo`, AND NOTHING ASKED UNTIL
    # 2026-08-22. The per-file guard below checks that a target lands inside
    # `--out`; on an OVERLAP that is satisfied by the source file itself, so the
    # guard passed and `compositor.draft` OVERWROTE the file under review --
    # printing `1 page(s) set` and exiting 0.
    #
    # ! IT IS THE SAME DESTRUCTIVE OUTCOME THE GUARD BELOW RECORDS from
    # 2026-08-17. That fix closed the absolute-path cause and left this one, and
    # a per-file test cannot close it: the question is about the two ROOTS and
    # has to be asked once, here, before any file is read.
    #
    # ! REFUSED WHOLE. Nothing under `--repo` is touched by this module, so a
    # run that could touch it is not a run with some bad files in it.
    # ! `is_relative_to` IS TRUE OF A PATH AND ITSELF, so the equality test
    # that stood here first was covered by the one beside it.
    if out.is_relative_to(repo) or repo.is_relative_to(out):
        print(
            f"REFUSED: --out {out} overlaps --repo {repo}, so a galley would be"
            " written over the files under review -- no galley written"
        )
        return 2
    try:
        census = json.loads(Path(args.census).read_text(encoding="utf-8"))
        edits = json.loads(Path(args.edits).read_text(encoding="utf-8"))
    except exceptions.READ_ERRORS as e:
        print(f"CANNOT READ ({type(e).__name__}) -- no galley written")
        return 2
    except json.JSONDecodeError as e:
        print(f"CANNOT PARSE as JSON ({e}) -- no galley written")
        return 2

    paragraphs = census["paragraphs"] if isinstance(census, dict) else census
    # !! AN UNADDRESSED CENSUS MATCHES NOTHING. `--edits` is keyed by address, so
    # every edit would be refused one at a time with a message about the EDIT
    # rather than about the census. ! `page_for` does not stamp addresses -- the
    # run loop does, once the path is repo-relative -- so a census built by
    # calling that function directly reaches here looking complete.
    if paragraphs and not any(str(b.get("address", "")) for b in paragraphs):
        print(
            f"CANNOT USE {args.census}: it carries no addresses, so no edit can"
            " be keyed against it. Write it with `census.py --json`"
        )
        return 2

    # ! Which page each address is on comes from the CENSUS, which is the only
    # thing that knows -- an address names a place, and the page it sits on is
    # the record's to state.
    where = {str(b.get("address", "")): str(b.get("path", "")) for b in paragraphs}
    by_path: dict[str, dict[str, str]] = {}
    refused = 0
    for address, replacement in edits.items():
        rel = where.get(str(address), "")
        if not rel:
            print(
                f"REFUSED  {address!r}: no paragraph in this census"
                " carries that address"
            )
            refused += 1
            continue
        by_path.setdefault(rel, {})[str(address)] = replacement

    written = 0
    for rel, file_edits in sorted(by_path.items()):
        # !! REFUSE ANYTHING THAT WOULD LAND OUTSIDE `--out`, BEFORE READING.
        # `out / rel` is the source path itself when `rel` is absolute --
        # Python's join lets an absolute right-hand side win -- and an absolute
        # path is exactly what a census taken before that was fixed carries.
        # Measured 2026-08-17: the galley overwrote the file under review,
        # wrote nothing under `--out`, and reported success.
        target = (out / rel).resolve()
        if not target.is_relative_to(out):
            print(f"REFUSED  {rel}: would be written outside --out")
            refused += len(file_edits)
            continue
        source = repo / rel
        try:
            # !! READ RAW. `read_text` collapses every `\r\n` to `\n`, so the
            # compositor would never see a CRLF file and every line of the
            # galley would differ from its original by its ending -- which is
            # the whole thing this module is diffed for.
            text = read_raw(source)
        except exceptions.READ_ERRORS as e:
            print(f"REFUSED  {rel}: {type(e).__name__}")
            refused += len(file_edits)
            continue

        lang = language_for(source)
        if lang is None:
            print(f"REFUSED  {rel}: no language record, so it has no page")
            refused += len(file_edits)
            continue
        page = page_for(source, text, lang, rel=rel)

        # ! The CHEAPER refusal first, and the one that is about the FILE rather
        # than about any one edit: a census taken before the code moved names
        # places that no longer sit where the reviewers read them.
        moved = drifted(page, [b for b in paragraphs if str(b.get("path", "")) == rel])
        if moved:
            print(f"REFUSED  {rel}: {len(moved)} anchor(s) moved since the census")
            for line in moved[:3]:
                print(f"           {line}")
            refused += len(file_edits)
            continue

        problems = reset(page, file_edits)
        if problems:
            # ! Every edit is placed BEFORE anything is written, so one that
            # cannot be refuses its file rather than half-setting it.
            print(f"REFUSED  {rel}: {len(problems)} edit(s) could not be placed")
            for line in problems[:3]:
                print(f"           {line}")
            refused += len(file_edits)
            continue

        target.parent.mkdir(parents=True, exist_ok=True)
        compositor.draft(page, target)
        print(f"galley   {rel} ({len(file_edits)} paragraph(s))")
        written += 1

    print(f"\n{written} page(s) set, {refused} edit(s) refused -> {out}")
    # ! Nonzero when anything refused. A galley missing a paragraph is not a
    # galley of the proposal, and censusing it would measure a text nobody
    # proposed.
    return 1 if refused else 0


if __name__ == "__main__":
    sys.exit(main())
