"""SOURCE-VERIFICATION and RECONCILIATION: marks against the tree, then each other.

    known_addresses()          every address the binder carries
    address_problems()         a mark's address is one of them
    claim_verbatim_problems()  the sentence the claim quotes is really in the
                               paragraph the row seeded
    source_problems()          every `cite` resolves inside the checkout, and
                               its `verbatim` sits near the line it names
    source_verification()      those three, over one mark
    verify_report()            those three, over every ruled mark of one
                               edit_copy
    places()                   every ruled mark of a master_proof, grouped by
                               the address it TOUCHES
    reconcile()                each place -> settled, escalation or re-read
    docket_from()              the settled places, as a docket

!! TWO STEPS, AND WHAT EACH NEEDS IS WHAT SEPARATES THEM. `desk/mark.py`
answers everything a mark can be judged by on its own. The first half here
needs the PAGE the role read and the FILES it cited; the second half needs the
marks the OTHER roles handed back. Nothing above `places` compares two marks,
and nothing below it opens a file.

!! AND THE TWO HALVES REFUSE DIFFERENTLY. Verification RETURNS a message per
broken rule, each opening with the mark it is about, so a whole report is
checked in one pass and every problem is read at once. Reconciliation RAISES
-- `UnnamedRole`, `MalformedMark` -- because a mark it cannot read is a mark it
cannot group, and a place grouped wrongly is settled wrongly.
"""

from pathlib import Path
from typing import NamedTuple

from comment_review.binder.binder import rows_of
from comment_review.desk.mark import INSTRUCTIONS, Instruction, Mark, parse, untouched
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
    return frozenset(
        row["address"] for row in rows_of(binder) if row.get("address")
    )

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

def claim_verbatim_problems(where: str, mark: Mark, raw_text: str) -> list[str]:
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
        raw_text: the paragraph the ROW seeded. It is the seeded row's field
            and not one of `Mark`'s seven, which is why it is passed in.

    Returns:
        One message, or an empty list. A key that is absent, is not a string,
        or holds only whitespace says nothing here -- `desk.mark.parse` is what
        refuses those, and this step has nothing to compare.
    """
    key = INSTRUCTIONS[mark.instruction].quotes_original
    if not key:
        return []
    value = mark.claim.get(key)
    if not isinstance(value, str) or not value.strip():
        return []
    if value not in raw_text:
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
        if not isinstance(cite, str) or not cite.strip():
            continue
        parsed = _cite_at(cite)
        if parsed is None:
            out.append(f"{at}: `cite` {cite!r} is not `path:line`")
            continue
        path, lineno = parsed
        if can_escape(path):
            out.append(f"{at}: `cite` {cite!r} names a path outside the "
                        "checkout")
            continue
        lines = _lines(root, path, cache)
        if lines is None:
            out.append(f"{at}: `cite` {cite!r} does not resolve -- the file "
                        "cannot be read")
            continue
        if lineno > len(lines):
            out.append(f"{at}: `cite` {cite!r} names a line past the end of "
                        "the file")
            continue
        if not isinstance(verbatim, str) or not verbatim.strip():
            continue
        # ! The cited line plus `WITHIN` on each side, clamped at both ends of
        # the file, and rejoined with `\n` whatever the file's own endings are
        # -- so a `verbatim` may span lines of the window, and one quoting a
        # CRLF file's own endings will not be found in it.
        lo = max(0, lineno - 1 - WITHIN)
        hi = min(len(lines), lineno + WITHIN)
        window = "\n".join(lines[lo:hi])
        if verbatim not in window:
            out.append(
                f"{at}: `verbatim` is not within {WITHIN} lines of {cite}"
            )
    return out

def source_verification(
    where: str,
    mark: Mark,
    *,
    raw_text: str,
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
        raw_text: the paragraph the row seeded, for the quoted sentence.
        known: `known_addresses` of the binder the mark was seeded from.
        root: the checkout every `cite` is resolved against.
        cache: path -> lines, shared across the marks of one report.
    """
    return (
        address_problems(where, mark, known)
        + claim_verbatim_problems(where, mark, raw_text)
        + source_problems(where, mark, root, cache)
    )

def verify_report(report: dict, binder: dict, root: Path) -> list[str]:
    """Source-verification over every ruled mark of ONE role's edit_copy.

    Args:
        report: one edit_copy -- `{"sheets": [{"path", "sha", "marks": [...]}]}`,
            as `flows.marks.seed` hands it out and a role hands it back. A
            `sheets` that is not a list gives an empty result, and so does a
            sheet whose `marks` is not one.
        binder: the binder the edit_copy was seeded from -- what each
            `address` is measured against.
        root: the checkout every `cite` is resolved against.

    Returns:
        Every problem found, in sheet order and then in mark order.

    !! AN UNTOUCHED SLOT IS SKIPPED AND AN UNPARSEABLE ENTRY IS NOT. The first
    is `desk.mark.untouched` -- a coverage gap, a place no role wrote in. The
    second contributes `desk.mark.parse`'s own messages and is then checked no
    further, since there is no `Mark` to check.

    ! A MARK IS NAMED BY ITS OWN `address`, falling back to `mark {n}` where it
    carries none. ! `n` COUNTS EVERY ENTRY WALKED, untouched slots included, so
    it is a position in the report rather than a count of rulings.

    ! ONE CACHE PER REPORT, built here and threaded through every mark, so a
    file twenty sources cite is read once.
    """
    sheets = report.get("sheets")
    if not isinstance(sheets, list):
        return []
    known = known_addresses(binder)
    cache: Cache = {}
    out: list[str] = []
    i = 0
    for sheet in sheets:
        marks = sheet.get("marks") if isinstance(sheet, dict) else None
        if not isinstance(marks, list):
            continue
        for entry in marks:
            i += 1
            if untouched(entry):
                continue
            where = str(
                (entry.get("address") if isinstance(entry, dict) else None)
                or f"mark {i}"
            )
            mark, why = parse(where, entry)
            if mark is None:
                out += why
                continue
            raw_text = entry.get("raw_text")
            out += source_verification(
                where,
                mark,
                raw_text=raw_text if isinstance(raw_text, str) else "",
                known=known,
                root=root,
                cache=cache,
            )
    return out

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
        if not isinstance(role, str) or not role.strip():
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
    `OUTCOMES` order, and each end keeps its own entry.

    ! IT RUNS TO A FIXED POINT, because moves chain: one move's destination can
    be another move's origin, and promoting the first pair can promote the
    second. The loop stops on the pass that changes nothing.

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
            strongest = max((outcomes[end][0] for end in ends), key=OUTCOMES.index)
            for end in ends:
                kind, entry = outcomes[end]
                if kind != strongest:
                    outcomes[end] = (strongest, entry)
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
        beside the mapping.
    """
    paths: list[str] = []
    shas: dict[str, str] = {}
    for copy in proof.get("edit_copies", []):
        for sheet in copy.get("sheets", []):
            path = sheet.get("path") if isinstance(sheet, dict) else None
            if isinstance(path, str) and path and path not in shas:
                paths.append(path)
                shas[path] = str(sheet.get("sha", ""))
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
