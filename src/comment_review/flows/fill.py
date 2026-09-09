"""FILL -- place one role's ruling on its edit copy, in place.

    fill(copy, entry, root) -> (the entry as placed, []) or (None, problems)

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
                             from the first's own anchor and raw_text
    no slot, a real place    appended to that page's sheet with the anchor the
                             role gave and an empty raw_text -- an `add` on an
                             empty place, which the binder does not carry
    no slot, no such page    refused
    no slot, no such place   refused -- the page carries every place, absent
                             and present, so a cue it does not hold names
                             nothing there

!! THE COPY IS A WIRE DICT, NEVER AN `EditCopy`. `flows.proof_io`'s header
says why: a role's copy mid-fill holds slots nobody has ruled on, and
`Sheet.serialize` writes only the rulings, so parsing the copy to save it would
drop every null slot -- the coverage the seeded shape exists to keep.

! THE FLOW READS THE CHECKOUT AND THE DESK DOES NOT. `desk.mark.derived_change`
is the pure half -- the paragraph and the claim in, the change out -- and the
cited line is read here, through `machine.repo.read_raw`, the same reader and
the same splitter `desk.collator.source_problems` will check the result with.
"""

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
from comment_review.flows.page_for import page_of
from comment_review.machine import constants
from comment_review.machine.exceptions import READ_ERRORS
from comment_review.machine.repo import can_escape, read_raw
from comment_review.reading.addresser import unflatten

#: The fields a role decides, in the order a mark carries them. `address` is
#: how the entry is placed and `anchor` is read only for a slot that must be
#: created; neither is copied from the entry onto the mark.
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


def _quoted(root: Path | None, sources: object) -> tuple[list | None, list[str]]:
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


def fill(copy: dict, entry: dict, root: Path | None) -> tuple[dict | None, list[str]]:
    """One ruling, placed on the copy.

    Args:
        copy: a role's edit_copy as its wire dict, as `load_copy` returns it.
            MUTATED on success, and only then.
        entry: what the role decided -- `address`, `instruction`, and whichever
            of `claim`, `reason`, `sources` and `change` its row owes. `change`
            may be left out where the row quotes a clause; `derived_change`
            builds it from the slot's `raw_text`. `anchor` is read only when a
            slot has to be created.
        root: the checkout a bare `cite` is read from, or None.

    Returns:
        `(mark, [])` -- the dict now on the copy -- or `(None, [messages])` with
        the copy untouched. The messages are `Mark.deserialize`'s own wording
        where the parse is what refused, so a role learns the contract from the
        refusal.
    """
    address = entry.get("address")
    if not filled(address):
        return None, ["names no `address`"]
    named = entry.get("instruction")
    if not isinstance(named, str) or named not in INSTRUCTIONS:
        return None, [f"`instruction` must be one of {', '.join(sorted(INSTRUCTIONS))}"]
    instruction = Instruction(named)

    marks, at = _slot_at(copy, address)
    if marks is None:
        marks, rel = _sheet_for(copy, address)
        if marks is None:
            return None, [f"{address} names a page this copy has no sheet for"]
        if root is None:
            return None, [f"{address}: no checkout to resolve its page against"]
        page, why_page = page_of(root / rel, rel=rel)
        if page is None:
            return None, [f"{address}: {why_page}"]
        if address.partition("@")[2] not in page.cues.places:
            return None, [f"{address} names no place on that page"]
        seeded = Mark.seed(address, str(entry.get("anchor") or ""), "")
        in_place = False
    else:
        slot = marks[at]
        seeded = Mark.seed(
            address, str(slot.get("anchor") or ""), str(slot.get("raw_text") or "")
        )
        in_place = untouched(slot)

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
            if INSTRUCTIONS[instruction].owes_change:
                return None, [
                    f"{instruction} needs `change` -- its row quotes no clause to "
                    "derive it from"
                ]
        else:
            mark["change"] = derived

    if "sources" in mark:
        quoted, why = _quoted(root, mark["sources"])
        if why:
            return None, why
        mark["sources"] = quoted

    parsed, why = Mark.deserialize(address, mark)
    if parsed is None:
        return None, why

    if in_place:
        slot = marks[at]
        slot.clear()
        slot.update(mark)
        return slot, []
    marks.insert(at + 1 if at >= 0 else len(marks), mark)
    return mark, []
