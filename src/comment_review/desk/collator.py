"""SOURCE-VERIFICATION and RECONCILIATION: marks against the tree, then each other.

    known_addresses()          every address the binder carries
    base_texts()               every address -> the paragraph the binder
                               seeded there
    address_problems()         a mark's address is one of them
    claim_verbatim_problems()  the sentence the claim quotes is really in the
                               paragraph the row seeded
    source_problems()          every `cite` resolves inside the checkout, and
                               its `verbatim` sits near the line it names
    source_verification()      those three, over one mark
    verify_report()            those three, over every ruled mark of one
                               edit_copy
    Problem                    one thing wrong with one mark, named to route
    problems_in()              every rule `desk.mark` settles, over a whole
                               edit_copy
    drift_in()                 every ruled mark whose returned `raw_text`
                               is not the one `base_texts` named for its
                               address
    unruled()                  the addresses nobody wrote in
    tally()                    how many of each instruction the edit_copy carries
    places()                   every ruled mark of a master_proof, grouped by
                               the address it TOUCHES
    reconcile()                each place -> settled, escalation or re-read
    docket_from()              the settled places, as a docket

!! FOUR KINDS OF CHECK, AND WHAT EACH NEEDS IS WHAT SEPARATES THEM. NAMED BY
MEMBER, NOT BY FILE-ORDER RANGE -- `desk/mark.py` answers everything a mark
can be judged by on its own. One kind needs the PAGE the role read and the
FILES it cited: `known_addresses` and `base_texts` turn the binder into what
`address_problems`, `claim_verbatim_problems`, `source_problems`,
`source_verification` and `verify_report` measure a mark against -- never a
mark's own `raw_text`, the base a party being checked could have altered.
One kind needs only the report itself, and nothing outside it (`Problem`,
`problems_in`, `unruled`, `tally`) -- `decision-log.md Process: #54` put
them here because they ask whether every place in the copy was ruled on, a
question about the SET, and one mark cannot answer for the set alone. One
kind needs the marks the OTHER roles handed back (`places`, `reconcile`,
`docket_from`). A FOURTH kind compares what came back against what went
out: `drift_in`, which needs both the returned report and the base
`base_texts` derived from the binder it was seeded from -- checking the
SAME field of the SAME entry at two different times, what it was seeded
with against what came back, rather than checking a claim against evidence
(the first kind) or one role's mark against another's (the third).
Nothing above `places` compares two marks, and nothing below `verify_report`
opens a file.

!! AND THEY REFUSE DIFFERENTLY. Verification and coverage both RETURN a
`Problem` per broken rule, so a whole report is checked in one pass and every
problem is read at once. ! VERIFICATION RETURNED SENTENCES UNTIL 2026-08-31,
each opening with the mark it was about; `P25` gave it a production caller and
`Problem` is what a caller can ROUTE -- see that type, and `verify_report`.
Some of coverage's are about the COPY rather than about any one mark: no
`sheets` list, no `role`, or an entry that is not an object each produce a
`Problem` carrying `address=""`, with nothing in the message naming a mark at
all. Reconciliation RAISES -- `UnnamedRole`, `MalformedMark` -- because a mark
it cannot read is a mark it cannot group, and a place grouped wrongly is
settled wrongly.

!! AND THE THREE VERIFICATION QUESTIONS ARE NOW ASKED IN PRODUCTION, which
this file's prose assumed the opposite of until 2026-08-31.
`flows.collate.collate` calls `verify_report` per copy; `grep -rn
"verify_report" src/` returns a caller outside this module, where before it
returned only sentences inside it. `decision-log.md Process: #58`, `P25`.

! WHAT IS STILL OWED IS T7: `parse_master_proof` compares `read_from` against
`copies[0]` only, never 2..N.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple

from comment_review.binder.binder import _read_from_problem, rows_of
from comment_review.desk.mark import (
    INSTRUCTIONS,
    Instruction,
    Mark,
    filled,
    parse,
    untouched,
)
from comment_review.machine import constants
from comment_review.machine.exceptions import READ_ERRORS
from comment_review.machine.repo import can_escape, read_raw
from comment_review.reading.addresser import cue_of, flatten, unflatten

#: How far from the line a `source` cites its `verbatim` may sit, in lines, on
#: either side. A role reads a paragraph and cites the line it was looking at,
#: so the window is what admits a cite that is off by a line or two while still
#: refusing one that names a place the text is not.
WITHIN = 3

#: The cited path, exactly as the `cite` spelled it, -> that file's lines, or
#: None where it could not be read. ! KEYED ON THE PATH ALONE, so one cache
#: belongs to one root.
Cache = dict[str, tuple[str, ...] | None]


def known_addresses(binder: dict) -> frozenset[str]:
    """Every address the binder's rows carry, as a set to test membership on.

    Args:
        binder: as `rows_of` reads one -- `{"pages": [{"path", "rows": [...]}]}`,
            with the address rejoined onto each row there rather than here.

    Returns:
        The addresses. A row carrying none, or an empty one, is dropped.
    """
    return frozenset(row["address"] for row in rows_of(binder) if row.get("address"))


def base_texts(binder: dict) -> dict[str, str]:
    """Every address the binder carries -> the paragraph it SEEDED there.

    !! THE BASE IS THE BINDER'S, NEVER A RETURNED MARK'S. `raw_text` is seeded
    and comes back on the mark, so a compose or a verbatim check reading it off
    the mark would measure a claim against text the party being checked
    supplied. `docs/gates.md` holds the measured case: the round-trip identity
    scored 699 of 699 on its first run by rebuilding each file from line
    positions it had just read out of that file.

    Args:
        binder: as `binder.read` returns one.

    Returns:
        address -> that place's `raw_text`. A row carrying no address is
        dropped, matching `known_addresses`.
    """
    return {
        row["address"]: str(row.get("raw_text", ""))
        for row in rows_of(binder)
        if row.get("address")
    }


def address_problems(where: str, mark: Mark, known: frozenset[str]) -> list[str]:
    """Whether this mark's address names a place the binder carries.

    ! AN EMPTY ADDRESS PASSES, and that is not a hole. `desk.mark.parse` owes
    the address only where `INSTRUCTIONS[...].substantive` is True, and `clean`
    is the one row it is False for -- so a `clean` reaches here carrying none.

    Args:
        where: how to name this mark in a message -- its address, or a position.
        mark: one role's ruling, already through `desk.mark.parse`.
        known: `known_addresses` of the binder this mark was seeded from.

    Returns:
        One message, or an empty list. Never more than one.
    """
    if mark.address and mark.address not in known:
        return [
            f"{where}: `address` {mark.address!r} names no place the binder carries"
        ]
    return []


def claim_verbatim_problems(where: str, mark: Mark, base: str) -> list[str]:
    """Whether the sentence this mark's claim quotes is really in the paragraph.

    !! WHICH KEY HOLDS IT IS READ OFF THE ROW, never branched on the
    instruction: `INSTRUCTIONS[...].quotes_original` names it -- `claim.drop`
    for a `drop`, `claim.false` for a `correct`, `claim.from` for a `patch` --
    and is "" for the rows that quote no existing sentence, which are passed
    over here entirely.

    ! A SUBSTRING TEST OVER THE WHOLE PARAGRAPH. The quoted text may run across
    several of its lines, and is anchored at neither end.

    Args:
        where: how to name this mark in a message -- its address, or a position.
        mark: one role's ruling, already through `desk.mark.parse`.
        base: the paragraph THE BINDER SEEDED at this place, from `base_texts`.
            ! NOT `mark.raw_text`, which is what came BACK -- a check reading
            its own base off the thing it is checking cannot disagree with it.

    Returns:
        One message, or an empty list. A key that is absent, is not a string,
        or holds only whitespace says nothing here -- `desk.mark.parse` is what
        refuses those, and this step has nothing to compare.
    """
    key = INSTRUCTIONS[mark.instruction].quotes_original
    if not key:
        return []
    value = mark.claim.get(key)
    if not filled(value):
        return []
    if value not in base:
        return [f"{where}: `claim.{key}` is not in the paragraph this row seeded"]
    return []


def _cite_at(cite: str) -> tuple[str, int] | None:
    """`path:line` split at the LAST colon, or None where it is not that form.

    ! THE LAST COLON, so a path carrying one of its own -- a Windows drive,
    `C:/pkg/mod.py:12` -- keeps it and only the line number is taken off.

    Returns:
        `(path, lineno)`, or None for an empty path, a line that is not
        digits, or a line below 1.
    """
    path, sep, line = cite.rpartition(":")
    if not sep or not path or not line.strip().isdigit():
        return None
    lineno = int(line)
    return (path, lineno) if lineno >= 1 else None


def _lines(root: Path, path: str, cache: Cache) -> tuple[str, ...] | None:
    """One cited file's lines, read at most once per path.

    !! SPLIT BY `constants.text_lines`, WHICH BREAKS ON CR, LF AND CRLF AND ON
    NOTHING ELSE. A role cites the number the page handed it, so the count here
    has to be a count of line ENDINGS; `str.splitlines()` also breaks on the
    vertical tab, the form feed, the three ASCII separators, NEL and Unicode's
    own line and paragraph separators, every one of which a file may hold
    inside a string literal.

    ! `read_raw` LEAVES THE ENDINGS ALONE, so a CRLF checkout and an LF one
    number the same file identically -- the three sequences the splitter breaks
    on are the three universal-newline translation would have collapsed.

    Returns:
        The lines, or None where the file could not be read. ! THE None IS
        CACHED TOO, so an unreadable path is attempted once however many
        sources cite it.
    """
    if path not in cache:
        try:
            text = read_raw(root / path)
        except READ_ERRORS:
            cache[path] = None
        else:
            cache[path] = tuple(constants.text_lines(text))
    return cache[path]


def source_problems(where: str, mark: Mark, root: Path, cache: Cache) -> list[str]:
    """Every source on this mark, checked against the file it cites.

    !! IT WALKS `mark.sources` AS HANDED. The field is typed `object` and
    nothing narrows it first, so an entry that is not an object is REFUSED BY
    NAME rather than filtered out and lost.

    The refusals, in the order they are asked, each one ending that source:

        not an object            a bare string cannot be resolved
        `cite` not `path:line`   nothing to open and nothing to number
        the path can escape      `root / path` DISCARDS `root` when `path` is
                                 absolute, so this is asked BEFORE any file is
                                 opened and the cache stays untouched
        the file cannot be read
        the line is past the end of the file
        `verbatim` out of reach  more than `WITHIN` lines from the cited line

    ! A SOURCE WITH NO USABLE `cite` IS PASSED OVER, and so is one with no
    usable `verbatim` once its cite has resolved. Whether a source was OWED at
    all is `desk.mark.parse`'s question, off `INSTRUCTIONS[...].owes_sources`;
    this step rules only on what it can resolve.

    Args:
        where: how to name this mark in a message -- its address, or a position.
        mark: one role's ruling, already through `desk.mark.parse`.
        root: the checkout every `cite` is resolved against.
        cache: shared across the marks of one report so a file cited many
            times is read once.

    Returns:
        One message per refused source, each opening `{where}: source {n}` and
        numbered from 1 in the order the mark carries them.
    """
    out = []
    for i, source in enumerate(mark.sources, 1):
        at = f"{where}: source {i}"
        if not isinstance(source, dict):
            out.append(f"{at} is not an object -- a bare string cannot be resolved")
            continue
        cite = source.get("cite")
        verbatim = source.get("verbatim")
        if not filled(cite):
            continue
        parsed = _cite_at(cite)
        if parsed is None:
            out.append(f"{at}: `cite` {cite!r} is not `path:line`")
            continue
        path, lineno = parsed
        if can_escape(path):
            out.append(f"{at}: `cite` {cite!r} names a path outside the checkout")
            continue
        lines = _lines(root, path, cache)
        if lines is None:
            out.append(
                f"{at}: `cite` {cite!r} does not resolve -- the file cannot be read"
            )
            continue
        if lineno > len(lines):
            out.append(f"{at}: `cite` {cite!r} names a line past the end of the file")
            continue
        if not filled(verbatim):
            continue
        # ! The cited line plus `WITHIN` on each side, clamped at both ends of
        # the file, and rejoined with `\n` whatever the file's own endings are
        # -- so a `verbatim` may span lines of the window, and one quoting a
        # CRLF file's own endings will not be found in it.
        lo = max(0, lineno - 1 - WITHIN)
        hi = min(len(lines), lineno + WITHIN)
        window = "\n".join(lines[lo:hi])
        if verbatim not in window:
            out.append(f"{at}: `verbatim` is not within {WITHIN} lines of {cite}")
    return out


def source_verification(
    where: str,
    mark: Mark,
    *,
    base: str,
    known: frozenset[str],
    root: Path,
    cache: Cache,
) -> list[str]:
    """The three checks over one mark.

    ! WHAT IT ADDS IS THE ORDER AND NOTHING ELSE -- address, then the quoted
    sentence, then the sources. The three lists are concatenated and none of
    them short-circuits, so one mark can come back carrying problems from all
    three at once.

    Args:
        where: how to name this mark in a message -- its address, or a position.
        mark: one role's ruling, already through `desk.mark.parse`.
        base: the paragraph THE BINDER SEEDED at this place, for the quoted
            sentence -- see `claim_verbatim_problems`.
        known: `known_addresses` of the binder the mark was seeded from.
        root: the checkout every `cite` is resolved against.
        cache: path -> lines, shared across the marks of one report.
    """
    return (
        address_problems(where, mark, known)
        + claim_verbatim_problems(where, mark, base)
        + source_problems(where, mark, root, cache)
    )


@dataclass(frozen=True)
class Problem:
    """One thing wrong with one mark, named so a reader can ROUTE it.

    !! STRUCTURED RATHER THAN A SENTENCE, ruled by Roy 2026-08-30: *"the errors
    should be stacked and capable of being read off correctly so that each can
    be fixed or sent back to the role."* `desk.mark.parse` returns flat strings
    each opening with a `where`, and a caller cannot route on a sentence -- so
    the role and the address ride beside the message.

    ! THERE IS NO `kind` FIELD. The three questions -- is this mark well formed,
    did its base drift, did anyone rule here -- stay three separate lists. A
    `kind` would only restate which list a Problem is already in.

    Attributes:
        role: the `edit_copy` this came back in -- WHO to send it back to.
        address: the place, or "" for a problem about the copy itself rather
            than about any one mark.
        message: the rule broken, worded by whichever check found it.
    """

    role: str
    address: str
    message: str


def verify_report(report: dict, binder: dict, root: Path) -> list[Problem]:
    """Source-verification over every ruled mark of ONE role's edit_copy.

    Args:
        report: one edit_copy -- `{"sheets": [{"path", "sha", "marks": [...]}]}`,
            as `flows.distribute.seed` hands it out and a role hands it back. A
            `sheets` that is not a list gives an empty result, and so does a
            sheet whose `marks` is not one. The `role` is read from it, so a
            finding names who to send it back to.
        binder: the binder the edit_copy was seeded from -- what each
            `address` is measured against.
        root: the checkout every `cite` is resolved against.

    Returns:
        Every problem found, in sheet order and then in mark order.

        !! `Problem`s RATHER THAN SENTENCES, since 2026-08-31, when this got a
        production caller. It is the same decision `problems_in` made on
        2026-08-30 and for the same reason -- see `Problem`: a caller cannot
        route on a sentence, and every one of these findings names a mark, so
        it has both a role and an address to route on. ! THE THREE LEAF
        FUNCTIONS STILL RETURN STRINGS. They answer about one mark and are
        handed a `where`; assembling the routing is this function's job,
        because it is the one that holds the copy and therefore the role.

    !! AN UNTOUCHED SLOT IS SKIPPED, and so is AN UNPARSEABLE ENTRY -- the
    second only since 2026-08-31. The first is `desk.mark.untouched`: a
    coverage gap, a place no role wrote in. The second has no `Mark` to check,
    and its parse messages belong to `problems_in`.

    !! IT USED TO REPORT THEM, AND THAT WAS RIGHT WHILE THIS HAD NO PRODUCTION
    CALLER. `P25` put it in `flows.collate.collate` beside `problems_in`, which
    parses every entry already -- so a malformed mark came back **twice with a
    BYTE-IDENTICAL message**, measured on an emptied `claim`:
    `m.py@b1: correct needs `claim` to carry false, true (missing false, true)`,
    reported once by each. That is not two vocabularies for one fact, which
    `drift_in` already forbids; it is the same sentence twice.

    ! SO THE THREE QUESTIONS THIS FUNCTION OWNS ARE THE ONLY ONES IT ANSWERS --
    is the address one the binder carries, is the quoted sentence really in the
    paragraph, does every `cite` resolve. Whether the mark is well formed at
    all is asked once, one function over.

    ! A MARK IS NAMED BY ITS OWN `address`, falling back to `mark {n}` where it
    carries none. ! `n` COUNTS EVERY ENTRY WALKED, untouched slots included, so
    it is a position in the report rather than a count of rulings.

    ! ONE CACHE PER REPORT, built here and threaded through every mark, so a
    file twenty sources cite is read once.
    """
    sheets = report.get("sheets")
    if not isinstance(sheets, list):
        return []
    role = report.get("role")
    named = role if filled(role) else ""
    known = known_addresses(binder)
    base = base_texts(binder)
    cache: Cache = {}
    out: list[Problem] = []
    i = 0
    for sheet in sheets:
        marks = sheet.get("marks") if isinstance(sheet, dict) else None
        if not isinstance(marks, list):
            continue
        for entry in marks:
            i += 1
            if untouched(entry):
                continue
            # ! THE ADDRESS AND THE `where` PART COMPANY WHEN THERE IS NO
            # ADDRESS. `where` falls back to a POSITION so a message can name
            # something; `Problem.address` stays empty, because a position is
            # not an address and writing one there would make a place that does
            # not exist look citable.
            raw = entry.get("address") if isinstance(entry, dict) else None
            address = str(raw) if filled(raw) else ""
            where = address or f"mark {i}"
            # ! `why` IS DELIBERATELY DROPPED -- `problems_in` reports it, and
            # reporting it here too gave the same sentence twice. See above.
            mark, _why = parse(where, entry)
            if mark is None:
                continue
            out += [
                Problem(named, mark.address, message)
                for message in source_verification(
                    where,
                    mark,
                    base=base.get(mark.address, ""),
                    known=known,
                    root=root,
                    cache=cache,
                )
            ]
    return out


def problems_in(report: dict) -> tuple[list[Problem], int]:
    """Every rule broken in a filled edit_copy, and how many places were ruled on.

    ! AN UNTOUCHED SLOT IS NOT A PROBLEM -- it is an unruled place, and the
    count returned is what says how much of the edit_copy was answered. Refusing it
    here would make an unfinished edit_copy indistinguishable from a malformed one.

    !! BUT A SLOT A ROLE WROTE IN AND LEFT WITHOUT AN INSTRUCTION IS REFUSED BY
    NAME, and was silently skipped until 2026-08-29 -- `desk.mark.untouched`
    holds the distinction and the measurement behind it. Such an entry counts
    towards `ruled`: a role DID rule here, and reporting it as unruled sends a
    reader looking for a coverage gap that is really a malformed mark.

    !! WALKS `report["sheets"]` THEN EACH SHEET'S `marks`, since 2026-08-29 --
    `seed()` nests every mark inside its own page's sheet; a walk that read
    `report["marks"]` would see nothing at all.

    !! IT RETURNS `Problem`s, NOT SENTENCES, since 2026-08-30. See `Problem`.

    !! AND IT MOVED HERE FROM `flows/distribute.py`, per `decision-log.md
    Process: #54` -- "did every place get ruled on" is a question about the SET,
    which is this module's, while `desk/mark.py` answers for one mark alone.

    Returns:
        `(problems, ruled)` -- one `Problem` per broken rule, and the number of
        entries carrying an instruction.
    """
    # !! THE THREE HEADER CHECKS BELOW ARE DEPTH, NOT THE DEFINITION, since
    # 2026-08-31. `desk.containers.parse_edit_copy` decides what a well-formed
    # copy is, and `flows.collate.collate` runs it FIRST -- so in production a
    # report reaching here has already been ruled a copy, and none of these can
    # fire. `P21`, `Process: #57`.
    #
    # ! THEY STAY BECAUSE THIS IS A MODULE BOUNDARY, not a step inside one
    # flow. `problems_in` is a public name a caller may reach without a
    # container, and `TODO/galley-refusals-cannot-fire.md`'s rule is that a
    # guard at the boundary AND at the point of use is defensible depth --
    # what is not defensible is prose claiming the guard is load-bearing when
    # the enforcement is upstream. This comment is that prose, corrected.
    #
    # ! THE GUARDS THAT WERE CUT INSTEAD are the ones inside `flows/collate.py`,
    # downstream of the envelope in the same flow, where nothing else can reach
    # them.
    role = report.get("role")
    named = role if filled(role) else ""
    if not isinstance(report.get("sheets"), list):
        return [Problem(named, "", "the report needs a `sheets` list")], 0

    out: list[Problem] = []
    ruled = 0
    if not named:
        out.append(Problem("", "", "the report needs the `role` that wrote it"))
    # !! THE HEADER IS CHECKED ON THE WAY BACK, and was not until 2026-08-28.
    # `seed` refuses a binder that cannot say which root it read, and this side
    # -- the per-copy check -- ruled only on `marks` and `role`, so an edit_copy whose
    # `read_from` had been STRIPPED or EMPTIED passed at exit 0. ! That is the
    # same asymmetry as the one fixed at `bind` and `seed` earlier the same
    # day, one step further along the chain.
    #
    # !! IT REUSES `binder`'s OWN CHECKER, and hand-rolled `isinstance(..., dict)
    # and truthy` for one commit. That weaker form let `{"junk": 1}` and
    # `{"root": 7, "revise": "x"}` through at exit 0 while `bind` REFUSED the
    # identical value -- two spellings of one rule, disagreeing.
    #
    # ! AND THE COMMENT CLAIMED MORE THAN THE CODE DID: it offered *"rewritten
    # to a DIFFERENT root"* as motivation, which is not answerable here at all.
    # `problems_in` holds an edit_copy and no binder, so it can rule on the field's
    # SHAPE and not on whether the root is the one the edit_copy was seeded from.
    # That comparison needs the binder, and belongs wherever the two meet.
    why_header = _read_from_problem(report)
    if why_header:
        out.append(Problem(named, "", f"the report's {why_header}"))

    i = 0
    for sheet in report["sheets"]:
        marks = sheet.get("marks") if isinstance(sheet, dict) else None
        if not isinstance(marks, list):
            continue
        for mark in marks:
            i += 1
            if not isinstance(mark, dict):
                out.append(Problem(named, "", f"mark {i} is not an object"))
                continue
            if untouched(mark):
                continue
            ruled += 1
            address = str(mark.get("address") or "")
            where = address or f"mark {i}"
            _, why = parse(where, mark)
            out += [Problem(named, address, message) for message in why]
    return out, ruled


def drift_in(report: dict, base: dict[str, str]) -> list[Problem]:
    """Every ruled mark whose returned `raw_text` is not the one it was handed.

    ! REPORTED, NOT REFUSED. The tree can move between `seed` and the return,
    which is an ordinary thing rather than a malformed copy -- so a whole copy
    is never discarded over it. What a run must not do is compose over a base
    nobody sanctioned, which `base_texts` prevents separately.

    ! AN UNTOUCHED SLOT IS SKIPPED. Nobody wrote there, so nothing drifted.

    ! AN ADDRESS THE BINDER DOES NOT CARRY IS NOT DRIFT EITHER -- that is
    `address_problems`' question, and reporting it twice in two vocabularies is
    the duplication `Problem` exists to avoid.

    Args:
        report: one edit_copy, as it came back.
        base: `base_texts` of the binder it was seeded from.

    Returns:
        One `Problem` per drifted place, in sheet then mark order.
    """
    role = report.get("role")
    named = role if isinstance(role, str) else ""
    sheets = report.get("sheets")
    if not isinstance(sheets, list):
        return []
    out: list[Problem] = []
    for sheet in sheets:
        marks = sheet.get("marks") if isinstance(sheet, dict) else None
        if not isinstance(marks, list):
            continue
        for entry in marks:
            if not isinstance(entry, dict) or untouched(entry):
                continue
            address = str(entry.get("address") or "")
            if address not in base:
                continue
            got = str(entry.get("raw_text") or "")
            if got != base[address]:
                out.append(
                    Problem(
                        named,
                        address,
                        "`raw_text` is not the paragraph this place was seeded "
                        "with -- the copy came back with a different base",
                    )
                )
    return out


def unruled(report: dict) -> list[str]:
    """The addresses nobody wrote in -- the coverage gap, named not counted.

    !! WALKS `report["sheets"]` THEN EACH SHEET'S `marks`, matching
    `problems_in`, since 2026-08-29.

    ! READS `desk.mark.untouched`, the same question `problems_in` asks, so a
    mark refused for naming no instruction can never also be listed here. The
    two answers were derived separately from `mark is None` and agreed on a
    place that had been ruled on.
    """
    sheets = report.get("sheets")
    if not isinstance(sheets, list):
        return []
    out = []
    for sheet in sheets:
        marks = sheet.get("marks") if isinstance(sheet, dict) else None
        if not isinstance(marks, list):
            continue
        out += [str(m.get("address", "")) for m in marks if untouched(m)]
    return out


def tally(report: dict) -> dict[Instruction, int]:
    """How many of each instruction the edit_copy carries, for a one-line summary.

    !! WALKED `report["marks"]` UNTIL 2026-08-29 -- a top-level key `seed()`
    no longer writes, since an edit_copy's marks nest one level down inside
    `sheets`. On the reshaped report that read a KEY THAT NO LONGER EXISTS, so
    `report.get("marks", [])` silently fell back to `[]` and this returned
    `{}` for every real edit_copy, ruled or not -- a crash turned silent.
    """
    counts = dict.fromkeys(INSTRUCTIONS, 0)
    for sheet in report.get("sheets", []):
        marks = sheet.get("marks") if isinstance(sheet, dict) else None
        if not isinstance(marks, list):
            continue
        for mark in marks:
            if isinstance(mark, dict) and mark.get("instruction") in counts:
                counts[mark["instruction"]] += 1
    return {name: n for name, n in counts.items() if n}


def _touches(mark: Mark) -> list[str]:
    """Every address this one mark lands on.

    Its own `address`, and for a `move` its `claim.to` as well -- a move is a
    delete at one end and a write at the other, so it is present at BOTH places
    when marks are grouped and can meet whatever another role marked there.

    Returns:
        One address, or two. Empty for a mark carrying none; never the same
        address twice, so a `move` whose destination is its own origin gives
        one.
    """
    touched = []
    if mark.address:
        touched.append(mark.address)
    if mark.instruction is Instruction.MOVE:
        destination = mark.claim.get("to")
        if isinstance(destination, str) and destination and destination not in touched:
            touched.append(destination)
    return touched


class UnnamedRole(Exception):
    """An `edit_copy` carrying no `role`, or a blank one.

    Raised by `places` for every copy, BEFORE its sheets are read -- so a copy
    that holds no ruled mark refuses on the same terms as one that holds ten,
    and the refusal does not depend on where a role happened to leave a mark.

    ! Every mark that copy holds would otherwise be grouped under a name no
    reader can route on, and `role` is what an outcome is decided from.
    """


class MalformedMark(Exception):
    """An entry `desk.mark.parse` refused, met while grouping.

    Raised by `places`, carrying `parse`'s own messages joined with `"; "`.

    !! RECONCILIATION REFUSES WHERE VERIFICATION REPORTS, and the difference is
    what can be done afterwards. A list of problems can be handed back for
    someone to answer; a mark whose shape is unreadable cannot be grouped by
    the place it touches, and a place grouped wrongly is settled wrongly.
    """


class Placed(NamedTuple):
    """One mark and the role whose `edit_copy` it came back in.

    ! `role` IS THE EDIT_COPY'S, NOT THE MARK'S. `Mark` carries no such field,
    and the pair is what makes a place answerable: whether it settles turns on
    how many marks reached it, and the entry that records it names the roles.

    Attributes:
        mark: one role's ruling, through `desk.mark.parse`.
        role: the name on the `edit_copy` this mark came back in.
    """

    mark: Mark
    role: str


def places(proof: dict) -> dict[str, list[Placed]]:
    """Every ruled mark of a master_proof, grouped by the address it TOUCHES.

    A mark lands under its own `address`; a `move` lands under its destination
    as well, so the destination's group holds the move alongside anything
    another role marked there.

    Args:
        proof: a master_proof -- `{"edit_copies": [{"role", "sheets": [...]}]}`,
            as `desk.proof.gather` returns it. A sheet whose `marks` is not a
            list contributes nothing.

    Returns:
        address -> the `Placed`s touching it, in the order the copies, their
        sheets and their marks were walked. An address nobody ruled on is
        absent rather than empty.

    Raises:
        UnnamedRole: an edit_copy carries no `role`.
        MalformedMark: an entry that is neither untouched nor parseable.

    ! AN UNTOUCHED SLOT IS SKIPPED, the same coverage gap `verify_report`
    skips: nobody wrote there, so there is nothing to group.
    """
    out: dict[str, list[Placed]] = {}
    for i, copy in enumerate(proof.get("edit_copies", [])):
        role = copy.get("role")
        if not filled(role):
            raise UnnamedRole(
                f"edit_copy {i} carries no `role` -- every mark it holds would "
                "be grouped under a name no reader can route on"
            )
        for sheet in copy.get("sheets", []):
            marks = sheet.get("marks") if isinstance(sheet, dict) else None
            if not isinstance(marks, list):
                continue
            for entry in marks:
                if untouched(entry):
                    continue
                where = str(
                    (entry.get("address") if isinstance(entry, dict) else None)
                    or f"a mark of {role}"
                )
                mark, why = parse(where, entry)
                if mark is None:
                    raise MalformedMark("; ".join(why))
                placed = Placed(mark, role)
                for address in _touches(mark):
                    out.setdefault(address, []).append(placed)
    return out


class Reconciled(NamedTuple):
    """What reconciliation decided about each place, in three lists.

    Every entry is `{"address": str, "roles": sorted list[str], "marks":
    list[Placed]}`, and `marks` holds only the marks that OWE A CHANGE -- so a
    place where every role returned a `clean` or a `query` produces no entry at
    all, in any of the three.

    Attributes:
        settled: one owing mark, nothing composed with it. ONE role, one
            change, and the only list `docket_from` writes from.
        escalations: two or more owing marks that all rule on the SAME
            sentence -- two answers to one question.
        rereads: every other place with more than one owing mark, plus every
            place an `add` touches.
    """

    settled: list[dict]
    escalations: list[dict]
    rereads: list[dict]


def _owes_change(mark: Mark) -> bool:
    return INSTRUCTIONS[mark.instruction].owes_change


def _sentence_key(mark: Mark) -> object:
    """What two marks at one place are compared ON -- the sentence each rules on.

    The row's `quotes_original` names the claim key holding it. Where the row
    quotes no existing sentence -- `add` and `move`, the two owing rows that
    carry "" -- this returns `id(mark)`, which nothing else can equal, so two
    of them at one place are never found to have named the SAME sentence and
    the place is re-read rather than escalated.
    """
    key = INSTRUCTIONS[mark.instruction].quotes_original
    if key:
        return mark.claim.get(key)
    return id(mark)


def _roles_of_stage(proof: dict, path: str) -> set[str]:
    """Every role of this proof whose edit_copy holds a sheet for one page.

    Args:
        proof: a master_proof, as `places` reads one.
        path: the FLATTENED path, as an address carries it. Each sheet states a
            real repo path, so it is `flatten`ed to compare.

    Returns:
        The role names. ! A ROLE SHARDED ONTO OTHER PAGES IS NOT AMONG THEM,
        so widening a place to "the roles of the stage" reaches only the roles
        that actually read this file.
    """
    out: set[str] = set()
    for copy in proof.get("edit_copies", []):
        role = copy.get("role")
        if not isinstance(role, str):
            continue
        for sheet in copy.get("sheets", []):
            sheet_path = sheet.get("path") if isinstance(sheet, dict) else None
            if isinstance(sheet_path, str) and flatten(sheet_path) == path:
                out.add(role)
                break
    return out


#: The three outcomes, WEAKEST FIRST. `_join_moves` takes `max` by this order,
#: so an escalation beats a re-read and a re-read beats a settlement; `reconcile`
#: keys its own three lists by these same names.
OUTCOMES = ("settled", "rereads", "escalations")


def _outcome(proof: dict, address: str, owing: list[Placed]) -> tuple[str, dict]:
    """Which outcome one place gets, and the entry that records it.

    Asked in this order, first match winning:

        an `add` among them   RE-READ, and the roles widen to every role of
                              the stage that read this page -- two adds at two
                              addresses never meet under per-place grouping, so
                              nothing narrower can see a comment added twice
        one owing mark        SETTLED
        one sentence key      ESCALATION -- every mark rules on the same
                              sentence, so they answer each other
        anything else         RE-READ -- marks on different sentences of one
                              paragraph, which compose or do not, and this
                              step cannot say which

    Args:
        proof: the master_proof, read only to widen an `add`'s roles.
        address: the place being decided. Its path is what an `add` widens over.
        owing: the marks at this place that owe a change. Never empty --
            `reconcile` does not call this for a place with none.

    Returns:
        `(one of OUTCOMES, {"address", "roles", "marks"})`, `roles` sorted and
        `marks` the `owing` list as given.
    """
    roles = {placed.role for placed in owing}
    if any(placed.mark.instruction is Instruction.ADD for placed in owing):
        roles |= _roles_of_stage(proof, cue_of(address).path)
        kind = "rereads"
    elif len(owing) == 1:
        kind = "settled"
    elif len({_sentence_key(placed.mark) for placed in owing}) == 1:
        kind = "escalations"
    else:
        kind = "rereads"
    return kind, {"address": address, "roles": sorted(roles), "marks": owing}


def _join_moves(outcomes: dict[str, tuple[str, dict]]) -> None:
    """Give both ends of every `move` the same outcome. MUTATES `outcomes`.

    !! A `move` IS ONE INSTRUCTION AT TWO PLACES -- a delete at the origin and
    a write at the destination -- so an end settled while the other escalated
    would apply half of it: the paragraph read twice, or deleted and never
    rewritten. Each pair takes the STRONGEST outcome either end reached, by
    `OUTCOMES` order.

    !! A PROMOTED END'S ENTRY IS REBUILT FROM BOTH ENDS' `roles` AND `marks`,
    not only re-labelled with the stronger `kind`. Until 2026-08-30 a promoted
    end kept its own single-role entry, so a reader of `reconcile()`'s
    `rereads` or `escalations` -- or of `commands/collate.py`'s printout --
    saw the WEAKER end named for carry-forward with no trace of the role or
    mark that forced it there. MEASURED: a `move`'s origin, ruled by one role
    alone and settled on its own, is pulled to `rereads` because another role
    also ruled at the destination -- and the origin's entry named only the
    mover, never the role that collided at the far end. The union is taken
    over BOTH ends because either can hold information the other lacks: the
    destination's own entry already carries what touched it, but a mark at
    the ORIGIN that touches no other place -- another role's `correct` on the
    same paragraph the move is emptying -- is invisible from the destination
    unless it is carried across too.

    ! EACH END KEEPS ITS OWN `address`. Only `kind`, `roles` and `marks` are
    shared; the entry at each end still names that end.

    ! IT RUNS TO A FIXED POINT, because moves chain: one move's destination can
    be another move's origin, and promoting the first pair can promote the
    second. The loop stops on the pass that changes nothing.

    !! PROVISIONAL. Roy, 2026-08-30, ruling AGAINST the shape this whole
    function joins: *"A move needs to be what it is and that is a composite
    Mark - Drop Here Add There. They have to go together ... Nothing else
    acts on two places at once."* This function exists because today's `move`
    is ONE `Mark` touching two addresses, so "settle at one end, escalate at
    the other" is a state this module has to notice and repair after the
    fact -- a promotion hack. Once a move is a composite of two ordinary
    marks (a `drop`, an `add`), each with its own `address`, atomicity is
    STRUCTURAL: nothing groups two addresses under one mark to begin with, so
    there is no split outcome to detect or merge, and this function -- the
    whole of `_join_moves` -- has nothing left to do. The composite is a
    separate scope; this fix only stops the promoted-entry data loss within
    today's shape.

    Args:
        outcomes: address -> `(kind, entry)`, as `_outcome` built each. Both
            ends of a move are present, since a move owes a change and so is
            owing at each place it touches.
    """
    ends_of = {
        tuple(_touches(placed.mark))
        for _, entry in outcomes.values()
        for placed in entry["marks"]
        if placed.mark.instruction is Instruction.MOVE
        and len(_touches(placed.mark)) > 1
    }
    changed = True
    while changed:
        changed = False
        for ends in ends_of:
            kinds = [outcomes[end][0] for end in ends]
            strongest = max(kinds, key=OUTCOMES.index)
            if len(set(kinds)) == 1:
                continue
            roles: set[str] = set()
            marks: list[Placed] = []
            seen: set[tuple[str, int]] = set()
            for end in ends:
                _, entry = outcomes[end]
                roles.update(entry["roles"])
                for placed in entry["marks"]:
                    key = (placed.role, id(placed.mark))
                    if key not in seen:
                        seen.add(key)
                        marks.append(placed)
            sorted_roles = sorted(roles)
            for end in ends:
                address = outcomes[end][1]["address"]
                outcomes[end] = (
                    strongest,
                    {"address": address, "roles": sorted_roles, "marks": marks},
                )
            changed = True


def reconcile(proof: dict) -> Reconciled:
    """Every place a role ruled on, decided -- settled, escalated or re-read.

    !! ONLY THE MARKS THAT OWE A CHANGE TAKE PART.
    `INSTRUCTIONS[...].owes_change` is False for `clean` and `query`, so
    neither can turn a place another role settled into a contest, and a place
    holding nothing else produces no entry in any of the three lists.

    Args:
        proof: a master_proof, as `places` reads one.

    Returns:
        A `Reconciled`. Entries keep the order `places` grouped the addresses
        in, split across the three lists.

    Raises:
        UnnamedRole: from `places`.
        MalformedMark: from `places`.
    """
    outcomes: dict[str, tuple[str, dict]] = {}
    for address, marks in places(proof).items():
        owing = [placed for placed in marks if _owes_change(placed.mark)]
        if owing:
            outcomes[address] = _outcome(proof, address, owing)
    _join_moves(outcomes)
    settled: list[dict] = []
    escalations: list[dict] = []
    rereads: list[dict] = []
    into = {"settled": settled, "escalations": escalations, "rereads": rereads}
    for kind, entry in outcomes.values():
        into[kind].append(entry)
    return Reconciled(settled, escalations, rereads)


def _real_pages(proof: dict) -> tuple[list[str], dict[str, str]]:
    """The repo paths this proof's sheets name, and each page's sha.

    Returns:
        `(paths in first-seen order, path -> sha)`. A page several edit_copies
        carry keeps the FIRST sha seen. The paths are what `unflatten` resolves
        an address's flattened path against, which is why the list is kept
        beside the mapping. A missing OR a null `sha` reads as "".
    """
    paths: list[str] = []
    shas: dict[str, str] = {}
    for copy in proof.get("edit_copies", []):
        for sheet in copy.get("sheets", []):
            path = sheet.get("path") if isinstance(sheet, dict) else None
            if isinstance(path, str) and path and path not in shas:
                paths.append(path)
                # ! `.get("sha", "")` DEFAULTS ONLY WHEN THE KEY IS ABSENT. A
                # sheet carrying `"sha": null` reaches here with the key
                # PRESENT and holding None, so `.get` returns None and
                # `str(None)` is the four-character word "None" -- folded
                # into the same missing-sha case instead.
                raw_sha = sheet.get("sha")
                shas[path] = raw_sha if isinstance(raw_sha, str) else ""
    return paths, shas


def _alteration_text(address: str, mark: Mark) -> str | None:
    """The text to set at ONE end of one settled mark, or None to delete.

    A `move` at its ORIGIN is the delete, which is why the address is passed
    in: the same mark writes its `change` at the other end, and writing it at
    both is the duplication the one instruction exists to prevent.

    ! AN EMPTY `change` IS ALSO A DELETE. `desk.mark.parse` admits one only
    where the row's `may_empty` is True -- `drop`, whose claim can name the
    whole paragraph -- so the empty string reaching here is the edit.
    """
    if mark.instruction is Instruction.MOVE and address == mark.address:
        return None
    return mark.change or None


def docket_from(reconciled: Reconciled, proof: dict) -> dict:
    """The settled places, as a docket -- one page per file, in settled order.

    !! ESCALATIONS AND RE-READS ARE NOT WRITTEN AT ALL. A place that did not
    settle appears nowhere, which is what keeps a `move` whole: `_join_moves`
    has already given its two ends one outcome, so either both are here or
    neither is, and no docket carries one end of one.

    Args:
        reconciled: as `reconcile` returns it. Only `settled` is read.
        proof: the same master_proof, for the real page paths and shas. An
            address carries the FLATTENED path; `unflatten` resolves it against
            the sheets' own paths, and one it cannot resolve is written through
            flattened, with an empty sha.

    Returns:
        `{"pages": [{"path", "sha", "alterations": [{"cue", "text"}], "role"}]}`,
        one alteration per settled place. `text` is None where the alteration
        deletes the paragraph.

    ! `role` IS DROPPED FROM A PAGE TWO ROLES SETTLED ON rather than naming one
    of them. The field is per page and there is one line for it, so a page
    holding two roles' places can only ever name half of what set it.
    """
    paths, shas = _real_pages(proof)
    pages: dict[str, dict] = {}
    roles_of: dict[str, set[str]] = {}
    for entry in reconciled.settled:
        address = entry["address"]
        mark = entry["marks"][0].mark
        role = entry["roles"][0]
        addr = cue_of(address)
        real_path = unflatten(addr.path, paths) or addr.path
        page = pages.setdefault(
            real_path,
            {
                "path": real_path,
                "sha": shas.get(real_path, ""),
                "role": role,
                "alterations": [],
            },
        )
        roles_of.setdefault(real_path, set()).add(role)
        page["alterations"].append(
            {"cue": addr.cue, "text": _alteration_text(address, mark)}
        )
    for real_path, page in pages.items():
        if len(roles_of[real_path]) != 1:
            del page["role"]
    return {"pages": list(pages.values())}
