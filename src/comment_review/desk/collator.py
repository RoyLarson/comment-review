"""SOURCE-VERIFICATION: one role's marks against the tree they were read from.

    known_addresses()          every address the binder carries
    base_texts()               every address -> the paragraph the binder
                               seeded there
    claim_verbatim_problems()  the sentence the claim quotes is really in a
                               text at its place
    source_problems()          every `cite` resolves inside the checkout, and
                               its `verbatim` sits near the line it names
    source_verification()      those three, over one mark
    verify_report()            those three, over every ruled mark of one
                               edit_copy
    Problem                    one thing wrong with one mark, named to route
    tally()                    how many of each instruction the edit_copy carries

!! TWO KINDS OF CHECK, AND WHAT EACH NEEDS IS WHAT SEPARATES THEM. NAMED BY
MEMBER, NOT BY FILE-ORDER RANGE -- `desk/marks/mark.py` answers everything a
mark can be judged by on its own. One kind needs the PAGE the role read and the
FILES it cited: `claim_verbatim_problems`, `source_problems`,
`source_verification` and `verify_report` measure a mark against the texts
`flows.verify` reads off the page, and against those files -- never a mark's
own `raw_text`, the base a party being checked could have altered.
! WHETHER THE ADDRESS IS ONE
THE BINDER CARRIES IS NOT ASKED, since 2026-09-05 -- `decision-log.md Process:
#97`. The binder is filtered to the places holding prose, so an `add` cites a
place it dropped and a `move` may cite a file it never held; the write end
opens the page and is the one thing that can say whether the place exists.
`known_addresses` stays for the revise diff; the coverage count asks what came
back against what was handed out, and reads `binder.addresses.handed` for that.
One kind needs only the report itself, and nothing outside it (`Problem`,
`tally`) -- `decision-log.md Process: #54` put them here because they ask
about the SET, and one mark cannot answer for the set alone. ! TWO MORE
STOOD IN THAT GROUP UNTIL `P52`; `flows.mark_errors` answers what they did.
Nothing here compares a returned `raw_text` with what was seeded: the middle
does not ask whether a page changed, so there is no drift check
(`decision-log.md Process: #62`, `#185`).

!! HOW ONE ROLE'S MARKS MEET ANOTHER'S IS NOT ASKED HERE AT ALL. It was:
`places` grouped a master proof's marks by the addresses they land on and
`reconcile` ruled each group settled, escalated or re-read, raising
`MalformedMark` where an entry would not parse. `flows.places.places_of`
builds the places now and `desk.evaluate` rules them, from each place's own
record, and an entry that will not parse is `Sheet.refused` before either
runs.

!! EVERYTHING HERE RETURNS A `Problem` PER BROKEN RULE, so a whole report is
checked in one pass and every problem is read at once. ! IT RETURNED SENTENCES
UNTIL 2026-08-31, each opening with the mark it was about; `P25` gave it a
production caller and `Problem` is what a caller can ROUTE -- see that type,
and `verify_report`. One `Problem` is about the COPY rather than about any one
mark: an entry that is not an object produces one carrying `address=""`, with
nothing in the message naming a mark at all.

!! EVERY FUNCTION HERE TAKES A CONTAINER, NEVER A WIRE DICT, since 2026-08-31
-- `P42`, `decision-log.md Process: #65`. `verify_report` and `tally` take an
`EditCopy`.

!! AND THE DOCKET IS NOT BUILT HERE, since `P55`. `docket_from` and
`_real_pages` lived in this file and imported `Alteration`, `Schedule` and
`Docket` -- the only MIDDLE-to-WRITE-END import in the tree. The transcription
is `flows/revise.py::docket_of`, which takes an `EditCopy`, because a FLOW may
reach both ends and neither end may reach the other. `decision-log.md Process:
#76`.

!! AND THE THREE VERIFICATION QUESTIONS ARE ASKED IN PRODUCTION, which
this file's prose assumed the opposite of until 2026-08-31.
`flows.bus` calls `verify_report` per copy; `grep -rn "verify_report" src/`
returns a caller outside this module, where before it returned only sentences
inside it. `decision-log.md Process: #58`, `P25`.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from comment_review.binder.binder import Binder
from comment_review.desk.containers import EditCopy
from comment_review.desk.marks.mark import (
    Instruction,
    Mark,
    filled,
    without_location,
)
from comment_review.desk.marks.table import INSTRUCTIONS
from comment_review.machine import constants
from comment_review.machine.exceptions import READ_ERRORS
from comment_review.machine.repo import can_escape, read_raw

#: How far from the line a `source` cites its `verbatim` may sit, in lines, on
#: either side. A role reads a paragraph and cites the line it was looking at,
#: so the window is what admits a cite that is off by a line or two while still
#: refusing one that names a place the text is not.
WITHIN = 3

#: The cited path, exactly as the `cite` spelled it, -> that file's lines, or
#: None where it could not be read. ! KEYED ON THE PATH ALONE, so one cache
#: belongs to one root.
Cache = dict[str, tuple[str, ...] | None]


def known_addresses(binder: Binder) -> frozenset[str]:
    """Every address the binder's rows carry, as a set to test membership on.

    Args:
        binder: the deserialized binder. Each row already knows its own path
            and address -- a page rejoins them when it is read back.

    Returns:
        The addresses. A row carrying an empty one is dropped.
    """
    return frozenset(b.address for b in binder.paragraphs if b.address)


def base_texts(binder: Binder) -> dict[str, str]:
    """Every address the binder carries -> the paragraph it seeded there.

    `flows.bus` hands it to the fold as each place's base. It is the binder's,
    never a returned mark's: `raw_text` is seeded and comes back on the mark,
    so reading it off the mark would measure against text the party being
    checked supplied. `docs/gates.md` holds the measured case: the round-trip
    identity scored 699 of 699 on its first run by rebuilding each file from
    line positions it had just read out of that file.

    A quoted clause is not checked against it. The binder is the seed for
    what can be ruled on, not every place or file that can be, so the flow
    reads the page's text at a mark's place and hands it to
    `claim_verbatim_problems` -- `decision-log.md Process: #119`.

    Args:
        binder: the deserialized binder.

    Returns:
        address -> that place's `raw_text`. A row carrying no address is
        dropped, matching `known_addresses`.
    """
    return {b.address: b.raw_text for b in binder.paragraphs if b.address}


def claim_verbatim_problems(
    where: str, mark: Mark, texts: tuple[str, ...]
) -> list[str]:
    """Whether the sentence this mark's claim quotes is really in a text at its place.

    !! WHICH KEY HOLDS IT IS READ OFF THE ROW, never branched on the
    instruction: `INSTRUCTIONS[...].quotes_original` names it -- `claim.drop`
    for a `drop`, `claim.false` for a `correct`, `claim.from` for a `patch` --
    and is "" for the rows that quote no existing sentence, which are passed
    over here entirely.

    It passes when one of `texts` holds the quote, by a substring test over
    each whole text: the quoted text may run across several of its lines, and
    is anchored at neither end.

    Args:
        where: how to name this mark in a message -- its address, or a position.
        mark: one role's ruling, already through `desk.marks.mark.parse`.
        texts: every text at this place the quote may be in, as the flow reads
            them (`decision-log.md Process: #119`): the page's text at the
            mark's address, whether or not the binder holds that place or its
            file, and for a place a turn's batch sent the role, the text sent
            there. Where no page can be read the page's text is "", so a quote
            nothing else holds is refused. Never `mark.raw_text`, which is what
            came back -- a check reading its own base off the thing it is
            checking cannot disagree with it.

    Returns:
        One message, or an empty list. A key that is absent, is not a string,
        or holds only whitespace says nothing here -- `desk.marks.mark.parse` is what
        refuses those, and this step has nothing to compare.
    """
    key = INSTRUCTIONS[mark.instruction].quotes_original
    if not key:
        return []
    value = mark.claim.get(key)
    if not filled(value):
        return []
    if not any(value in text for text in texts):
        return [f"{where}: `claim.{key}` is not in the paragraph at this place"]
    return []


def cite_at(cite: str) -> tuple[str, int] | None:
    """`path:line` split at the LAST colon, or None where it is not that form.

    ! THE LAST COLON, so a path carrying one of its own -- a Windows drive,
    `C:/pkg/mod.py:12` -- keeps it and only the line number is taken off.

    ! PUBLIC SINCE 2026-09-07: `flows.fill` reads the cited line to fill a
    source's `verbatim`, and it has to split the cite the way this check does
    or the two would disagree about which line was cited.

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

    The checks are `cited_problems`, over the mark's own `sources`. An answer
    a turn brings back cites its evidence the same way and is held to the same
    checks (`decision-log.md Process: #181`), which is why they take a list of
    sources rather than the mark that carries them.
    """
    return cited_problems(where, mark.sources, root, cache)


def cited_problems(where: str, sources: object, root: Path, cache: Cache) -> list[str]:
    """Every source in this list, checked against the file it cites.

    !! IT WALKS THE SOURCES AS HANDED. Each entry is typed `object` and
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
    all is `desk.marks.mark.parse`'s question, off `INSTRUCTIONS[...].owes_sources`;
    this step rules only on what it can resolve.

    Args:
        where: how to name the citing ruling in a message -- its address, or
            a position.
        sources: what it cites, as a mark or an answer carries them.
        root: the checkout every `cite` is resolved against.
        cache: shared across the rulings of one report so a file cited many
            times is read once.

    Returns:
        One message per refused source, each opening `{where}: source {n}` and
        numbered from 1 in the order they were carried.
    """
    out = []
    if not isinstance(sources, (list, tuple)):
        return out
    for i, source in enumerate(sources, 1):
        at = f"{where}: source {i}"
        if not isinstance(source, dict):
            out.append(f"{at} is not an object -- a bare string cannot be resolved")
            continue
        cite = source.get("cite")
        verbatim = source.get("verbatim")
        if not filled(cite):
            continue
        parsed = cite_at(cite)
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
    texts: tuple[str, ...],
    root: Path,
    cache: Cache,
) -> list[str]:
    """The two checks over one mark.

    ! WHAT IT ADDS IS THE ORDER AND NOTHING ELSE -- the quoted sentence, then
    the sources. The two lists are concatenated and neither short-circuits, so
    one mark can come back carrying problems from both at once.

    Args:
        where: how to name this mark in a message -- its address, or a position.
        mark: one role's ruling, already through `desk.marks.mark.parse`.
        texts: every text at this place the quoted sentence may be in -- see
            `claim_verbatim_problems`.
        root: the checkout every `cite` is resolved against.
        cache: path -> lines, shared across the marks of one report.
    """
    return claim_verbatim_problems(where, mark, texts) + source_problems(
        where, mark, root, cache
    )


@dataclass(frozen=True)
class Problem:
    """One thing wrong with one mark, named so a reader can ROUTE it.

    !! STRUCTURED RATHER THAN A SENTENCE, ruled by Roy 2026-08-30: *"the errors
    should be stacked and capable of being read off correctly so that each can
    be fixed or sent back to the role."* `desk.marks.mark.parse` returns flat strings
    each opening with a `where`, and a caller cannot route on a sentence -- so
    the role and the address ride beside the message.

    ! THERE IS NO `kind` FIELD. The questions -- is this mark well formed, is
    what it quotes and cites really there, did anyone rule here -- stay
    separate lists. A `kind` would only restate which list a Problem is
    already in.

    Attributes:
        role: the `edit_copy` this came back in -- WHO to send it back to.
        address: the place, or "" for a problem about the copy itself rather
            than about any one mark.
        message: the rule broken, worded by whichever check found it.
    """

    role: str
    address: str
    message: str


def verify_report(
    copy: EditCopy, texts: Mapping[str, tuple[str, ...]], root: Path, cache: Cache
) -> list[Problem]:
    """Source-verification over every ruled mark of ONE role's edit_copy.

    Args:
        copy: one parsed edit_copy, as `flows.distribute.seed` hands it out and
            a role hands it back. Its `role` names who to send a finding back
            to, and `EditCopy.deserialize` has already refused a copy that
            carries none.
        texts: address -> every text a quote there may be in, as
            `flows.verify.texts_at` reads them. An address it lacks is
            checked against nothing, so a quote there is refused.
        root: the checkout every `cite` is resolved against.
        cache: a `Cache` to read cited files through.
            !! REQUIRED, AND ONE PER STAGE. `flows.bus` calls this
            once per copy, and a cache built per call re-reads a file for every
            citing role -- MEASURED 2026-08-31: four roles citing the same line
            read it from disk four times. The note below already promised "a
            file twenty sources cite is read once", which held inside one copy
            and not across the stage that copy belongs to.
            ! IT IS NOT OPTIONAL, deliberately. A default would let a caller
            get the per-call cache back by saying nothing, which is exactly the
            defect this parameter exists to remove -- and a caller who has no
            stage to share one across can still pass `{}` and say so.

    Returns:
        Every problem found, in sheet order and then in mark order.

        !! `Problem`s RATHER THAN SENTENCES, since 2026-08-31, when this got a
        production caller. It is the same decision the per-copy check made
        on 2026-08-30 and for the same reason -- see `Problem`: a caller cannot
        route on a sentence, and every one of these findings names a mark, so
        it has both a role and an address to route on. ! THE THREE LEAF
        FUNCTIONS STILL RETURN STRINGS. They answer about one mark and are
        handed a `where`; assembling the routing is this function's job,
        because it is the one that holds the copy and therefore the role.

    !! AN UNTOUCHED SLOT IS SKIPPED, and so is AN UNPARSEABLE ENTRY -- the
    second only since 2026-08-31. The first is `desk.marks.mark.untouched`: a
    coverage gap, a place no role wrote in. The second has no `Mark` to check,
    and its parse messages belong to `flows.mark_errors`.

    !! IT USED TO REPORT THEM, AND THAT WAS RIGHT WHILE THIS HAD NO PRODUCTION
    CALLER. `P25` put it in the fold beside the per-copy check,
    which parsed every entry already -- so a malformed mark came back **twice
    with a BYTE-IDENTICAL message**, measured on an emptied `claim`:
    `m.py@b1: correct needs `claim` to carry false, true (missing false, true)`,
    reported once by each -- the same sentence twice.

    ! SO THE TWO QUESTIONS THIS FUNCTION OWNS ARE THE ONLY ONES IT ANSWERS --
    is the quoted sentence really in the paragraph, does every `cite` resolve.
    Whether the mark is well formed at all is asked once, one function over.
    !! IT ASKED A THIRD UNTIL 2026-09-05 -- is the address one the binder
    carries -- and `Process: #97` retired it: the binder is a filtered view, an
    `add` cites a place the filter dropped, and only the write end can say
    whether the page has it. Two live runs lost four `add`s to the refusal.

    ! A MARK IS NAMED BY ITS OWN `address`, falling back to `mark {n}` where it
    carries none. ! `n` COUNTS EVERY ENTRY WALKED, untouched slots included, so
    it is a position in the report rather than a count of rulings.

    ! ONE CACHE PER STAGE, threaded in by the caller and through every mark, so
    a file twenty sources cite is read once no matter how many roles cite it.
    ! IT READ *"one cache per report, BUILT HERE"* until 2026-08-31, which was
    this function's own contradiction: `Args: cache` said one per stage and
    this said one per report, and the second is what the code did.
    """
    out: list[Problem] = []
    for sheet in copy.sheets:
        # !! IT WALKS PARSED MARKS AND PARSES NOTHING, since `P51`. This held
        # its own untouched test, its own `mark {n}` fallback and its own
        # `Mark.deserialize` -- one of the four sites that each parsed every
        # ruled entry. `Sheet.marks` holds only what ruled, so an untouched
        # slot and an unparseable entry are both already elsewhere.
        for mark in sheet.marks:
            # ! THE ADDRESS IS `Problem.address`, SO IT IS NOT ALSO THE OPENING
            # OF EVERY MESSAGE -- T3 of `collate-command-defects`. The three
            # leaf checks are handed a `where` and prefix it, which is right for
            # a caller holding nothing else; this one records it as a field.
            out += [
                Problem(
                    copy.role, mark.address, without_location(mark.address, message)
                )
                for message in source_verification(
                    mark.address,
                    mark,
                    texts=texts.get(mark.address, ()),
                    root=root,
                    cache=cache,
                )
            ]
    return out


#: !! `problems_in` AND `unruled` ARE DELETED, `P52`. Both walked a copy and
#: reported what a role still owed -- `problems_in` turning `Sheet.refused` into
#: `Problem`s, `unruled` naming `Sheet.unruled` -- and `flows.mark_errors`
#: answers both, as addresses and reasons, per `decision-log.md Process: #72`.
#: ! `problems_in` ALSO RETURNED A `ruled` COUNT that nothing in production ever
#: read: the fold discarded it at the call. The claim it carried -- a mark
#: a role wrote in and got WRONG still counts as ruled, and is not a coverage gap
#: -- survives in `tests/test_collator.py::_ruled_places`, derived from the
#: container where the cases that assert it live.


def tally(copy: EditCopy) -> dict[Instruction, int]:
    """How many of each instruction the edit_copy carries, for a one-line summary.

    !! WALKED A TOP-LEVEL `marks` KEY UNTIL 2026-08-29 -- one `seed()` no
    longer writes, since an edit_copy's marks nest one level down inside
    `sheets`. On the reshaped report that read a KEY THAT NO LONGER EXISTS, so
    the walk silently fell back to `[]` and this returned `{}` for every real
    edit_copy, ruled or not -- a crash turned silent. ! THAT IS UNREACHABLE
    NOW rather than merely fixed: an `EditCopy` has no such key to read.
    """
    # ! IT COUNTS `Mark.instruction`, WHICH IS THE MEMBER, since `P51`. It read
    # the wire string and matched it against the members -- `Instruction` is a
    # `StrEnum`, so `"clean"` found its counter -- and a parsed mark carries the
    # member itself, so the string round trip has nothing left to do.
    counts = dict.fromkeys(INSTRUCTIONS, 0)
    for sheet in copy.sheets:
        for mark in sheet.marks:
            counts[mark.instruction] += 1
    return {name: n for name, n in counts.items() if n}
