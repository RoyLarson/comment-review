"""FILL -- place one role's ruling on its edit copy, in place.

    fill(copy, entry, root) -> (the entry as placed, []) or (None, problems)
    place_on_the_page(copies, address, root) -> (that sheet's marks, a slot, [])
                                                or (None, {}, problems)
    row_problems(mark, base_at) -> what the mark's row finds against its bases
    quoted_sources(root, sources) -> each source with its `verbatim` read in
    page_text_at(copies, address, root) -> the page's paragraph at one place

! `row_problems` IS THE RULE, AND `commands/check.py` RUNS THE SAME CALL over a
whole copy. A role may write a copy with its file-write tool instead of placing
each ruling here, so the check a ruling passes on the way in is the check a
hand-written copy is held to -- one function, two callers, no second reading of
the rows.

!! IT DOES WHAT THE ROLES' OWN HELPERS DID. In the runs of 2026-09-06 and
2026-09-07 every role wrote a script that found the slot by address, set the
fields it had decided, built `change` by substituting the false clause inside
the slot's `raw_text`, and appended a second entry for a second ruling -- and
each one broke the brief's one-file rule to do it. Roy, watching: *"we should
have made a script that fills it in for them."* `TODO/a-role-writes-its-own-
mark-tool.md`. This is that script, and `commands/mark.py` exposes it.

!! ONE RULING PER CALL, AND IT WRITES NOTHING UNTIL EVERY CHECK HAS PASSED.
The entry is built whole -- placed, derived, quoted -- and then run through
`desk.mark.Mark.deserialize`, the same boundary the fold applies; only a mark
that parses lands on the copy. A refusal leaves the copy exactly as it was, so
a role reads the reasons and calls again.

! WHERE A RULING LANDS is decided by what the copy already holds at the address:

    an untouched slot        filled in place -- the seeded dict object itself
    a slot already ruled     a second entry, inserted right after it, seeded
                             from the first's own anchor and raw_text -- or
                             from the page, where that ruling's row wrote its
                             own raw_text and the first no longer holds the
                             paragraph as the page has it
    no slot, a real place    appended to that page's sheet with the page's own
                             anchor and raw_text at that place -- empty at an
                             empty place, which the binder does not carry, and
                             the page's prose at an `f` place, which no role
                             is handed. The base is the page's, never the
                             role's own entry -- `desk.collator.base_texts`'s
                             rule for base texts, applied one layer up.
    no slot, no such page    refused
    no slot, no such place   refused -- the page carries every place, absent
                             and present, so a cue it does not hold names
                             nothing there

The three "no slot" rows are `place_on_the_page`, which `flows.turn.apply`
also calls for a composition answer at a place the role's copy holds no
slot for.

!! THE COPY IS A WIRE DICT, NEVER AN `EditCopy`. `flows.proof_io`'s header
says why: a role's copy mid-fill holds slots nobody has ruled on, and
`Sheet.serialize` writes only the rulings, so parsing the copy to save it would
drop every null slot -- the coverage the seeded shape exists to keep.

! THE FLOW READS THE CHECKOUT AND THE DESK DOES NOT. `desk.mark.derived_change`
is the pure half -- the paragraph and the claim in, the change out -- and the
cited line is read here, through `machine.repo.read_raw`, the same reader and
the same splitter `desk.collator.source_problems` will check the result with.
"""

from collections.abc import Callable
from pathlib import Path

from comment_review.desk.collator import cite_at
from comment_review.desk.mark import (
    INSTRUCTIONS,
    Instruction,
    Mark,
    derived_change,
    filled,
    untouched,
)
from comment_review.desk.marks.table import Touch
from comment_review.flows.page_for import page_of
from comment_review.machine import constants
from comment_review.machine.exceptions import READ_ERRORS
from comment_review.machine.repo import can_escape, read_raw
from comment_review.reading.addresser import cue_of, unflatten

#: The fields a role decides, in the order a mark carries them. `address` is
#: how the entry is placed; `anchor` is never read off the entry at all --
#: a slot that must be created takes its anchor from the page. `raw_text` is
#: read only for a row whose `carries_raw_text` is True, and refused on every
#: other row -- see `_composed_text`.
ROLE_FIELDS = ("claim", "reason", "sources", "change")


def _slot_at(copy: dict, address: str) -> tuple[list | None, int]:
    """The sheet's `marks` list holding `address`, and where on it, or `(None, -1)`.

    The index is the LAST entry at that address, so a second ruling lands
    after every earlier one.
    """
    for sheet in copy.get("sheets", []):
        if not isinstance(sheet, dict):
            continue
        marks = sheet.get("marks")
        if not isinstance(marks, list):
            continue
        hits = [
            i
            for i, entry in enumerate(marks)
            if isinstance(entry, dict) and entry.get("address") == address
        ]
        if hits:
            return marks, hits[-1]
    return None, -1


def _sheet_for(copy: dict, address: str) -> tuple[list | None, str]:
    """The `marks` list of the sheet whose page `address` names.

    Returns that sheet's own path alongside it, or `(None, "")` if no
    sheet names the page at all.
    """
    name = address.partition("@")[0]
    sheets = [s for s in copy.get("sheets", []) if isinstance(s, dict)]
    by_path = {str(s.get("path", "")): s for s in sheets}
    path = unflatten(name, list(by_path))
    if not path:
        return None, ""
    marks = by_path[path].get("marks")
    return (marks if isinstance(marks, list) else None), path


def place_on_the_page(
    copies: list[dict], address: str, root: Path | None
) -> tuple[list | None, dict, list[str]]:
    """The sheet an address with no slot belongs on, and a slot seeded from the page.

    Args:
        copies: one role's copies as wire dicts -- one, or one per shard. The
            first whose sheets name the address's page is the one used.
        address: `path@cue`, a place none of `copies` holds a slot for.
        root: the checkout the page is read from, or None.

    Returns:
        `(that sheet's marks list, the seeded slot, [])`, the slot carrying the
        page's own anchor and `raw_text` at that place, and not yet on the
        sheet. Or `(None, {}, [message])` where no copy has a sheet for
        the page, there is no checkout, the page cannot be read, or the page
        carries no such place.
    """
    found = next(
        (
            (marks, rel)
            for copy in copies
            for marks, rel in [_sheet_for(copy, address)]
            if marks is not None
        ),
        None,
    )
    if found is None:
        return None, {}, [f"{address} names a page this copy has no sheet for"]
    marks, rel = found
    if root is None:
        return None, {}, [f"{address}: no checkout to resolve its page against"]
    page, why_page = page_of(root / rel, rel=rel)
    if page is None:
        return None, {}, [f"{address}: {why_page}"]
    cue = address.partition("@")[2]
    if cue not in page.cues.places:
        return None, {}, [f"{address} names no place on that page"]
    raw_text = next(
        (p.raw_text for p in page.paragraphs if cue_of(p.address).cue == cue), ""
    )
    return marks, Mark.seed(address, page.cues.anchor_of(cue), raw_text), []


def quoted_sources(root: Path | None, sources: object) -> tuple[list | None, list[str]]:
    """Every source with its `verbatim` filled from the cited line.

    A source already carrying `verbatim` is kept as given. One carrying only a
    `cite` has the line read out of the checkout and stripped -- the collator
    asks whether the text sits within three lines of the cite, and a stripped
    line does. ! THE REFUSALS ARE THE COLLATOR'S OWN, asked before the send: a
    cite that is not `path:line`, a path that escapes the root, a file that
    cannot be read, a line past the end.
    """
    if not isinstance(sources, list):
        return None, ["`sources` must be a list of `{cite, verbatim}` objects"]
    out: list = []
    for i, source in enumerate(sources, 1):
        if not isinstance(source, dict):
            return None, [f"source {i} must be an object with `cite` and `verbatim`"]
        cite = source.get("cite")
        if filled(source.get("verbatim")) or not filled(cite):
            out.append(dict(source))
            continue
        parsed = cite_at(cite)
        if parsed is None:
            return None, [f"source {i}: `cite` {cite!r} is not `path:line`"]
        path, lineno = parsed
        if can_escape(path):
            return None, [
                f"source {i}: `cite` {cite!r} names a path outside the checkout"
            ]
        if root is None:
            return None, [
                f"source {i}: `cite` {cite!r} carries no `verbatim` and there is no "
                "checkout to read the line from"
            ]
        try:
            lines = constants.text_lines(read_raw(root / path))
        except READ_ERRORS:
            return None, [
                f"source {i}: `cite` {cite!r} does not resolve -- the file "
                "cannot be read"
            ]
        if lineno > len(lines):
            return None, [
                f"source {i}: `cite` {cite!r} names a line past the end of the file"
            ]
        verbatim = lines[lineno - 1].strip()
        if not verbatim:
            return None, [
                f"source {i}: the line {cite!r} names is blank; give `verbatim`"
            ]
        out.append({**source, "verbatim": verbatim})
    return out, []


def row_problems(mark: Mark, base_at: Callable[[str], str]) -> list[str]:
    """Every problem this mark's row finds, at each place the row writes.

    The row says which places it touches and what it reads at each; this walks
    them and asks. A `move` is the row with two, so its origin is read against
    the origin's paragraph and its destination against the destination's --
    `decision-log.md Process: #172` and `#175`.

    Args:
        mark: one parsed mark.
        base_at: address -> the page's paragraph there, "" where the page
            holds none. The caller supplies it because the two callers reach
            a page differently: `fill` has the slot it seeded and reads one
            more page at most, and `check` walks a whole copy through a cache.

    Returns:
        The row's own messages, in the order its touches are stated. Empty
        where the row finds nothing.
    """
    row = INSTRUCTIONS[mark.instruction]
    out: list[str] = []
    for touch in row.touches:
        where = (
            str(mark.claim.get("to", ""))
            if touch is Touch.DESTINATION
            else mark.address
        )
        out += row.reads(mark, touch, base_at(where))
    return out


def page_text_at(copies: list[dict], address: str, root: Path | None) -> str:
    """The page's paragraph at `address`, or "" where no page answers for it.

    ! "" IS NOT A CLAIM THAT THE PLACE IS EMPTY, and nothing here turns an
    unreadable page into a refusal: an address no page resolves is
    `flows.collate.resolution_problems`' finding, which `check` and the fold
    both run, and reporting it twice would refuse at `mark` what the parity
    case (`no-command-for-the-middle` T99) exists to have `check` name.
    """
    marks, seeded, _why = place_on_the_page(copies, address, root)
    return str(seeded.get("raw_text", "")) if marks is not None else ""


def _base_beside(copy: dict, seeded: dict, address: str, root: Path | None) -> str:
    """The page's paragraph at `address`, taking the slot already in hand first.

    The seeded slot carries the page's text at the mark's own address, so only
    a second place -- a move's destination -- costs a read.
    """
    if address == seeded["address"]:
        return str(seeded["raw_text"])
    return page_text_at([copy], address, root)


def _row_of(named: object):
    """The row a placed entry's `instruction` names, or None if it names none."""
    if isinstance(named, str) and named in INSTRUCTIONS:
        return INSTRUCTIONS[Instruction(named)]
    return None


def _seeded_beside(
    copy: dict, slot: dict, address: str, root: Path | None
) -> tuple[dict | None, list[str]]:
    """A slot seeded as the place was handed out, given a ruling already there.

    The anchor and the paragraph come off the entry already at the address,
    which is where they were copied to -- except where that entry's row wrote
    its own `raw_text`, the paragraph as it will READ rather than as it stands
    (`decision-log.md Process: #175`, `#176`). Reseeding from that would give
    the next ruling at the place a base the page never held, so the page is
    read again instead.
    """
    row = _row_of(slot.get("instruction"))
    if row is not None and row.carries_raw_text:
        marks, from_page, why = place_on_the_page([copy], address, root)
        return (from_page, []) if marks is not None else (None, why)
    return Mark.seed(
        address, str(slot.get("anchor") or ""), str(slot.get("raw_text") or "")
    ), []


def _composed_text(
    row, instruction: Instruction, entry: dict, seeded: dict, change: object
) -> tuple[str | None, list[str]]:
    """The `raw_text` this mark carries -- the role's, the seed's, or a refusal.

    `decision-log.md Process: #175` and `#176`: on a row whose
    `carries_raw_text` is True the field is the paragraph as it will READ, with
    the added or moved text in, and the role writes it. A row that touches a
    destination always owes one, since the paragraph it describes is at the
    other end and nothing here stands in for it. A row that does not owes one
    only where the place already holds prose -- at an empty place the snippet
    and the paragraph as it will read are the same text.

    Returns:
        `(the text, [])`, or `(None, [one message])`. The text is the seeded
        paragraph for every row that composes none.
    """
    given = entry.get("raw_text")
    if not row.carries_raw_text:
        if filled(given) and given != seeded["raw_text"]:
            return None, [
                f"{seeded['address']}: {instruction} takes no `raw_text` -- the"
                " paragraph is seeded from the page, and only a row that writes"
                " the paragraph as it will read carries one"
            ]
        return seeded["raw_text"], []
    if filled(given):
        return str(given), []
    if row.owes_destination:
        return None, [
            f"{seeded['address']}: {instruction} needs `raw_text` (--raw-text)"
            " -- the destination paragraph as it will read, with the moved"
            " text in"
        ]
    if filled(seeded["raw_text"]):
        return None, [
            f"{seeded['address']} holds prose, so {instruction} there needs"
            " `raw_text` (--raw-text) -- the paragraph as it will read, with"
            " the added text in, keeping every word already there"
        ]
    return change if isinstance(change, str) else "", []


def fill(copy: dict, entry: dict, root: Path | None) -> tuple[dict | None, list[str]]:
    """One ruling, placed on the copy.

    Args:
        copy: a role's edit_copy as its wire dict, as `load_copy` returns it.
            MUTATED on success, and only then.
        entry: what the role decided -- `address`, `instruction`, and whichever
            of `claim`, `reason`, `sources` and `change` its row owes. `change`
            may be left out where the row quotes a clause; `derived_change`
            builds it from the slot's `raw_text`. An `anchor` here is never
            read -- a slot that has to be created takes its anchor from the
            page, not from the entry.
        root: the checkout a bare `cite` is read from, or None.

    Returns:
        `(mark, [])` -- the dict now on the copy -- or `(None, [messages])` with
        the copy untouched. The messages are `Mark.deserialize`'s own wording
        where the parse is what refused, so a role learns the contract from the
        refusal.

    The row is what decides whether the ruling stands: `row_problems` runs its
    `reads` at every place it writes, against the pages, and a problem there is
    a refusal in the row's own words. An `add` over prose keeps every word of
    that prose in order (`decision-log.md Process: #132` and `#176`); a `move`
    subtracts its snippet from the origin exactly once and lands a destination
    paragraph holding both (`#172`, `#175`).
    """
    address = entry.get("address")
    if not filled(address):
        return None, ["names no `address`"]
    named = entry.get("instruction")
    if not isinstance(named, str) or named not in INSTRUCTIONS:
        return None, [f"`instruction` must be one of {', '.join(sorted(INSTRUCTIONS))}"]
    instruction = Instruction(named)
    row = INSTRUCTIONS[instruction]

    marks, at = _slot_at(copy, address)
    if marks is None:
        marks, seeded, why = place_on_the_page([copy], address, root)
        if marks is None:
            return None, why
        in_place = False
    else:
        seeded, why = _seeded_beside(copy, marks[at], address, root)
        if seeded is None:
            return None, why
        in_place = untouched(marks[at])

    mark: dict = {**seeded, "instruction": named}
    for key in ROLE_FIELDS:
        if key in entry and entry[key] is not None:
            mark[key] = entry[key]

    if "change" not in mark:
        derived, why = derived_change(
            instruction, mark.get("claim"), seeded["raw_text"]
        )
        if why:
            return None, why
        if derived is None:
            if row.owes_change:
                return None, [
                    f"{instruction} needs `change` -- its row quotes no clause to "
                    "derive it from"
                ]
        else:
            mark["change"] = derived

    composed, why = _composed_text(row, instruction, entry, seeded, mark.get("change"))
    if composed is None:
        return None, why
    mark["raw_text"] = composed

    if "sources" in mark:
        quoted, why = quoted_sources(root, mark["sources"])
        if why:
            return None, why
        mark["sources"] = quoted

    parsed, why = Mark.deserialize(address, mark)
    if parsed is None:
        return None, why

    # ! THE ROW READS THE PAGES LAST, after the parse: `Mark.deserialize` is
    # what settles a destination that is not addressable at all, and a row
    # asked to read against a place no address names has nothing to say.
    found = row_problems(parsed, lambda where: _base_beside(copy, seeded, where, root))
    if found:
        return None, [f"{address}: {why}" for why in found]

    if in_place:
        slot = marks[at]
        slot.clear()
        slot.update(mark)
        return slot, []
    marks.insert(at + 1 if at >= 0 else len(marks), mark)
    return mark, []


def withdraw(
    copy: dict, address: str, root: Path | None = None
) -> tuple[dict | None, list[str]]:
    """Every ruling the copy holds at `address`, taken back.

    `mark-defects` T24. A second ruling at an address lands beside the first,
    so a role had no way to take back a mark it placed -- and a refused mark is
    sent back to the role that wrote it, which then had nothing to fix it with
    but the JSON. A place the seed gave a slot -- one holding prose, outside
    the file's own matter, which is never seeded -- keeps one untouched slot,
    as it was handed; a place the role created for an `add` at an empty place
    is left with nothing, as it was before.

    ! THE SEED IS READ OFF THE PAGE where any ruling at the place wrote its own
    `raw_text` -- `add` and `move` carry the paragraph as it will READ
    (`decision-log.md Process: #175`, `#176`), so handing that back would seed
    the place with a paragraph the page never held. That read needs `root`, and
    without one the withdrawal is refused rather than guessed at.

    Args:
        copy: a role's edit_copy as its wire dict. MUTATED on success, and only
            then.
        address: `path@cue`, as the slot carries it.
        root: the checkout the page is read from, where one has to be.

    Returns:
        `(the slot left, [])`, `({}, [])` where the place is left with no slot,
        or `(None, [message])` with the copy untouched where nothing is placed.
    """
    marks, _ = _slot_at(copy, address)
    if marks is None:
        return None, [f"{address}: this copy holds no slot there"]
    here = [
        i
        for i, entry in enumerate(marks)
        if isinstance(entry, dict) and entry.get("address") == address
    ]
    if all(untouched(marks[i]) for i in here):
        return None, [f"{address}: nothing is placed there to withdraw"]
    first = marks[here[0]]
    anchor = str(first.get("anchor") or "")
    raw_text = str(first.get("raw_text") or "")
    composed = [
        i
        for i in here
        if (row := _row_of(marks[i].get("instruction"))) is not None
        and row.carries_raw_text
    ]
    if composed:
        on_page, from_page, why = place_on_the_page([copy], address, root)
        if on_page is None:
            return None, why
        anchor, raw_text = from_page["anchor"], from_page["raw_text"]
    for i in reversed(here):
        del marks[i]
    if not filled(raw_text) or address.partition("@")[2].startswith("f"):
        return {}, []
    slot = Mark.seed(address, anchor, raw_text)
    marks.insert(here[0], slot)
    return slot, []
