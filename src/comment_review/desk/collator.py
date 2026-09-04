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
    drift_in()                 every ruled mark whose returned `raw_text`
                               is not the one `base_texts` named for its
                               address
    tally()                    how many of each instruction the edit_copy carries
    places()                   every ruled mark of a master_proof, grouped by
                               the address it TOUCHES
    reconcile()                each place -> settled, escalation or re-read

!! FOUR KINDS OF CHECK, AND WHAT EACH NEEDS IS WHAT SEPARATES THEM. NAMED BY
MEMBER, NOT BY FILE-ORDER RANGE -- `desk/mark.py` answers everything a mark
can be judged by on its own. One kind needs the PAGE the role read and the
FILES it cited: `known_addresses` and `base_texts` turn the binder into what
`address_problems`, `claim_verbatim_problems`, `source_problems`,
`source_verification` and `verify_report` measure a mark against -- never a
mark's own `raw_text`, the base a party being checked could have altered.
One kind needs only the report itself, and nothing outside it (`Problem`,
`tally`) -- `decision-log.md Process: #54` put them here because they ask
about the SET, and one mark cannot answer for the set alone. ! TWO MORE
STOOD IN THAT GROUP UNTIL `P52`; `flows.mark_errors` answers what they did. One
kind needs the marks the OTHER roles handed back (`places`, `reconcile`).
A FOURTH kind compares what came back against what went
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
One of coverage's is about the COPY rather than about any one mark: an entry
that is not an object produces a `Problem` carrying `address=""`, with nothing
in the message naming a mark at all. Reconciliation RAISES -- `MalformedMark`
-- because a mark it cannot read is a mark it cannot group, and a place grouped
wrongly is settled wrongly.

!! EVERY FUNCTION HERE TAKES A CONTAINER, NEVER A WIRE DICT, since 2026-08-31
-- `P42`, `decision-log.md Process: #65`. `verify_report`, `drift_in` and
`tally` take an `EditCopy`; `places`, `reconcile` and `_roles_of_stage`
take a `MasterProof`.

!! AND THE DOCKET IS NOT BUILT HERE ANY MORE, since `P55`. `docket_from` and
`_real_pages` lived in this file and imported `Alteration`, `Schedule` and
`Docket` -- the only MIDDLE-to-WRITE-END import in the tree. The transcription
is `flows/revise.py::docket_of`, which takes an `EditCopy` rather than a
`(Reconciled, MasterProof)` pair, because a FLOW may reach both ends and neither
end may reach the other. `decision-log.md Process: #76`.
! WHAT WENT WITH THE SIGNATURES is every re-derivation of the same walk --
`report.get("sheets")`, `isinstance(sheets, list)`, `sheet.get("marks") if
isinstance(sheet, dict)` -- which stood at five sites in this file, and
`UnnamedRole`, which `EditCopy.deserialize` makes unconstructable.

!! AND THE THREE VERIFICATION QUESTIONS ARE NOW ASKED IN PRODUCTION, which
this file's prose assumed the opposite of until 2026-08-31.
`flows.collate.collate` calls `verify_report` per copy; `grep -rn
"verify_report" src/` returns a caller outside this module, where before it
returned only sentences inside it. `decision-log.md Process: #58`, `P25`.

! WHAT IS STILL OWED IS T7: `MasterProof.deserialize` compares `read_from` against
`copies[0]` only, never 2..N.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple

from comment_review.binder.binder import Binder
from comment_review.desk.containers import EditCopy, MasterProof
from comment_review.desk.mark import (
    INSTRUCTIONS,
    Instruction,
    Mark,
    Shape,
    filled,
    without_location,
)
from comment_review.machine import constants
from comment_review.machine.exceptions import READ_ERRORS
from comment_review.machine.repo import can_escape, read_raw
from comment_review.reading.addresser import cue_of, flatten

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
    """Every address the binder carries -> the paragraph it SEEDED there.

    !! THE BASE IS THE BINDER'S, NEVER A RETURNED MARK'S. `raw_text` is seeded
    and comes back on the mark, so a compose or a verbatim check reading it off
    the mark would measure a claim against text the party being checked
    supplied. `docs/gates.md` holds the measured case: the round-trip identity
    scored 699 of 699 on its first run by rebuilding each file from line
    positions it had just read out of that file.

    Args:
        binder: the deserialized binder.

    Returns:
        address -> that place's `raw_text`. A row carrying no address is
        dropped, matching `known_addresses`.
    """
    return {b.address: b.raw_text for b in binder.paragraphs if b.address}


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


def verify_report(
    copy: EditCopy, binder: Binder, root: Path, cache: Cache
) -> list[Problem]:
    """Source-verification over every ruled mark of ONE role's edit_copy.

    Args:
        copy: one parsed edit_copy, as `flows.distribute.seed` hands it out and
            a role hands it back. Its `role` names who to send a finding back
            to, and `EditCopy.deserialize` has already refused a copy that
            carries none.
        binder: the binder the edit_copy was seeded from -- what each
            `address` is measured against.
        root: the checkout every `cite` is resolved against.
        cache: a `Cache` to read cited files through.
            !! REQUIRED, AND ONE PER STAGE. `flows.collate.collate` calls this
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
    second only since 2026-08-31. The first is `desk.mark.untouched`: a
    coverage gap, a place no role wrote in. The second has no `Mark` to check,
    and its parse messages belong to `flows.mark_errors`.

    !! IT USED TO REPORT THEM, AND THAT WAS RIGHT WHILE THIS HAD NO PRODUCTION
    CALLER. `P25` put it in `flows.collate.collate` beside the per-copy check,
    which parsed every entry already -- so a malformed mark came back **twice
    with a BYTE-IDENTICAL message**, measured on an emptied `claim`:
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

    ! ONE CACHE PER STAGE, threaded in by the caller and through every mark, so
    a file twenty sources cite is read once no matter how many roles cite it.
    ! IT READ *"one cache per report, BUILT HERE"* until 2026-08-31, which was
    this function's own contradiction: `Args: cache` said one per stage and
    this said one per report, and the second is what the code did.
    """
    known = known_addresses(binder)
    base = base_texts(binder)
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
                    base=base.get(mark.address, ""),
                    known=known,
                    root=root,
                    cache=cache,
                )
            ]
    return out


#: !! `problems_in` AND `unruled` ARE DELETED, `P52`. Both walked a copy and
#: reported what a role still owed -- `problems_in` turning `Sheet.refused` into
#: `Problem`s, `unruled` listing `Sheet.unruled` -- and `flows.mark_errors`
#: answers both, as addresses and reasons, per `decision-log.md Process: #72`.
#: ! `problems_in` ALSO RETURNED A `ruled` COUNT that nothing in production ever
#: read: `flows.collate` discarded it at the call. The claim it carried -- a mark
#: a role wrote in and got WRONG still counts as ruled, and is not a coverage gap
#: -- survives in `tests/test_collator.py::_ruled_places`, derived from the
#: container where the cases that assert it live.


def drift_in(copy: EditCopy, base: dict[str, str]) -> list[Problem]:
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
        copy: one parsed edit_copy, as it came back.
        base: `base_texts` of the binder it was seeded from.

    Returns:
        One `Problem` per drifted place, in sheet then mark order.
    """
    # ! AN UNTOUCHED SLOT AND AN UNREADABLE ENTRY ARE BOTH ALREADY ELSEWHERE,
    # so this walks rulings and tests neither -- `P51`.
    return [
        Problem(
            copy.role,
            mark.address,
            "`raw_text` is not the paragraph this place was seeded "
            "with -- the copy came back with a different base",
        )
        for sheet in copy.sheets
        for mark in sheet.marks
        if mark.address in base and mark.raw_text != base[mark.address]
    ]


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


#: !! `MalformedMark` IS DELETED, `P51`. It said *"reconciliation REFUSES where
#: verification REPORTS"*, on the reasoning that a mark whose shape is
#: unreadable cannot be grouped by the place it touches, and a place grouped
#: wrongly is settled wrongly. ! THAT REASONING STILL HOLDS AND IS NOW
#: STRUCTURAL: an unreadable entry never becomes a `Mark`, so `places` has
#: nothing to group wrongly and no raise to make. Where it goes instead is
#: `Sheet.refused` -- an address and its reasons, routed to the role that wrote
#: it, `decision-log.md Process: #72`.


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


def places(proof: MasterProof) -> dict[str, list[Placed]]:
    """Every ruled mark of a master_proof, grouped by the address it TOUCHES.

    A mark lands under its own `address`; a `move` lands under its destination
    as well, so the destination's group holds the move alongside anything
    another role marked there.

    Args:
        proof: a parsed master_proof, as `desk.proof.gather` returns one.

    Returns:
        address -> the `Placed`s touching it, in the order the copies, their
        sheets and their marks were walked. An address nobody ruled on is
        absent rather than empty.

    !! IT RAISED `MalformedMark` UNTIL `P51`, AND CANNOT NOW. `Sheet.marks`
    holds marks that parsed, so there is no unreadable entry left to meet here
    -- and `flows.collate._reconcilable`, whose whole job was dropping them
    before this ran, went with the raise. ! THE REFUSAL DID NOT WEAKEN: an
    entry that will not parse is `Sheet.refused`, which routes to the role that
    wrote it instead of stopping the stage.
    """
    out: dict[str, list[Placed]] = {}
    for copy in proof.edit_copies:
        for sheet in copy.sheets:
            for mark in sheet.marks:
                placed = Placed(mark, copy.role)
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
        settled: one owing mark, nothing composed with it -- a composition of
            ONE side. Its `roles` are every role that marked the place with
            anything but a `query`, because the fold sends it back to them
            before it stands (`decision-log.md Process: #89`); it is no longer
            the list a transcription reads at turn 0.
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


def _roles_of_stage(proof: MasterProof, path: str) -> set[str]:
    """Every role of this proof whose edit_copy holds a sheet for one page.

    Args:
        proof: a parsed master_proof, as `places` reads one.
        path: the FLATTENED path, as an address carries it. Each sheet states a
            real repo path, so it is `flatten`ed to compare.

    Returns:
        The role names. ! A ROLE SHARDED ONTO OTHER PAGES IS NOT AMONG THEM,
        so widening a place to "the roles of the stage" reaches only the roles
        that actually read this file.
    """
    return {
        copy.role
        for copy in proof.edit_copies
        if any(flatten(sheet.path) == path for sheet in copy.sheets)
    }


#: The three outcomes, WEAKEST FIRST. `_join_moves` takes `max` by this order,
#: so an escalation beats a re-read and a re-read beats a settlement; `reconcile`
#: keys its own three lists by these same names.
OUTCOMES = ("settled", "rereads", "escalations")


def _outcome(
    proof: MasterProof, address: str, owing: list[Placed], marks: list[Placed]
) -> tuple[str, dict]:
    """Which outcome one place gets, and the entry that records it.

    Asked in this order, first match winning:

        an `add` among them   RE-READ, and the roles widen to every role of
                              the stage that read this page -- two adds at two
                              addresses never meet under per-place grouping, so
                              nothing narrower can see a comment added twice
        one owing mark        SETTLED -- and its roles are every role that
                              marked the place with anything but a `query`,
                              since the fold sends a lone mark back to them
                              (`decision-log.md Process: #89`)
        one text              ESCALATION -- every mark carries the same
                              `change`, so the fold settles it as agreed
                              (`decision-log.md Process: #88`), whatever
                              instruction or sentence each carried
        one sentence key      ESCALATION -- every mark rules on the same
                              sentence, so they answer each other
        anything else         RE-READ -- marks on different sentences of one
                              paragraph, which compose or do not, and this
                              step cannot say which

    And whatever the outcome, a role whose mark here is a DEFERRING query --
    `outside-my-role`, `unable-to-determine` -- is out of `roles`: it has
    abstained from this place for the review (`decision-log.md Process:
    #90`). A `human-review-necessary` query is the flow's to set aside,
    place and all; this step does not see the difference.

    Args:
        proof: the parsed master_proof, read only to widen an `add`'s roles.
        address: the place being decided. Its path is what an `add` widens over.
        owing: the marks at this place that owe a change. Never empty --
            `reconcile` does not call this for a place with none.
        marks: every mark at this place, `owing` included -- what a settled
            entry's roles are read from.

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
        roles = {
            placed.role
            for placed in marks
            if placed.mark.instruction is not Instruction.QUERY
        }
    elif (
        all(INSTRUCTIONS[placed.mark.instruction].quotes_original for placed in owing)
        and len({placed.mark.change for placed in owing}) == 1
    ):
        # ! ONLY MARKS THAT QUOTE AN ORIGINAL. An `add` or a `move` carries no
        # sentence, and two moves into one place from two origins carrying one
        # text are two edits, not one agreement -- the same reason
        # `_sentence_key` gives them `id(mark)`.
        kind = "escalations"
    elif len({_sentence_key(placed.mark) for placed in owing}) == 1:
        kind = "escalations"
    else:
        kind = "rereads"
    deferring = {
        placed.role
        for placed in marks
        if placed.mark.instruction is Instruction.QUERY
        and placed.mark.claim.get("shape") != Shape.HUMAN_REVIEW_NECESSARY
    }
    roles -= deferring
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


def reconcile(proof: MasterProof) -> Reconciled:
    """Every place a role ruled on, decided -- settled, escalated or re-read.

    !! ONLY THE MARKS THAT OWE A CHANGE TAKE PART.
    `INSTRUCTIONS[...].owes_change` is False for `clean` and `query`, so
    neither can turn a place another role settled into a contest, and a place
    holding nothing else produces no entry in any of the three lists.

    Args:
        proof: a parsed master_proof, as `places` reads one.

    Returns:
        A `Reconciled`. Entries keep the order `places` grouped the addresses
        in, split across the three lists.

    Raises:
        MalformedMark: from `places`.
    """
    outcomes: dict[str, tuple[str, dict]] = {}
    for address, marks in places(proof).items():
        owing = [placed for placed in marks if _owes_change(placed.mark)]
        if owing:
            outcomes[address] = _outcome(proof, address, owing, marks)
    _join_moves(outcomes)
    settled: list[dict] = []
    escalations: list[dict] = []
    rereads: list[dict] = []
    into = {"settled": settled, "escalations": escalations, "rereads": rereads}
    for kind, entry in outcomes.values():
        into[kind].append(entry)
    return Reconciled(settled, escalations, rereads)
