"""The containers a mark travels in -- the sheet, the edit_copy, the master_proof.

    Sheet              one PAGE's marks, with that page's path and sha
    EditCopy           one ROLE's sheets, with the binder it was seeded from
    MasterProof        one STAGE's edit_copies
    parse_sheet()      the boundary parse for one sheet
    parse_edit_copy()  for one edit_copy, and every sheet under it
    parse_master_proof()  for one master_proof, and every copy under it

!! THE TYPE IS THE DEFINITION AND THERE IS NO MARKDOWN SOURCE, ruled
`decision-log.md Vocabulary: #30`. `docs/the-mark.md` exists because an agent
AUTHORS a mark, so a mark's shape must be published to a role. No agent ever
authors a container -- `flows.marks.seed`, `flows.fan_out.fan` and
`desk.proof.gather` build them -- so the type is where the shape lives, the way
`desk/mark.py` defines `Mark`.

!! THE WIRE STAYS DICTS. Each parse has `desk.mark.parse`'s own contract --
`(T, [])` or `(None, [one message per broken rule])` -- so a caller holds a
checked object and consumers stop re-deriving the same keys with `isinstance`
ladders. `desk/collator.py` alone did that in four functions.

! THE CHIEF'S COPY IS AN ORDINARY `EditCopy`. `Vocabulary: #30`: after the fold
every place has exactly one answer, and one mark per place is an ordinary copy.
There is no second shape and no second parse.

! `marks` IS TYPED `tuple[object, ...]`, matching `Mark.sources` and for the
same reason: an entry that is not an object is CARRIED so `desk.mark.parse` can
refuse it by name. Filtering to dicts here would make a bare string vanish
instead of being flagged.
"""

from dataclasses import dataclass

from comment_review.binder.binder import _read_from_problem


@dataclass(frozen=True)
class Sheet:
    """One page's marks, inside the `edit_copy` that seeded them.

    Attributes:
        path: the page's real repo path, as the binder stated it.
        sha: that page's sha when it was censused. Read by `docket_from`, which
            writes it onto the docket page so the setter can refuse a page that
            moved underneath the run.
        marks: one entry per place on the page, as they came back.
    """

    path: str
    sha: str
    marks: tuple[object, ...]


@dataclass(frozen=True)
class EditCopy:
    """One role's copy of the binder -- what goes out, and what comes back.

    Attributes:
        role: the editorial role that filled it, or `copy-chief` for the fold's
            result. It is what an outcome is decided from and what a place is
            sent back to.
        read_from: `{root, revise}` -- which tree this copy was censused from.
            `decision-log.md Process: #34`: the field exists so a later role can
            know it holds a REVISE and not the original.
        sheets: one per page.
    """

    role: str
    read_from: dict
    sheets: tuple[Sheet, ...]


@dataclass(frozen=True)
class MasterProof:
    """Every `edit_copy` of one stage, gathered.

    Attributes:
        stage: the label the copies were dispatched under -- `SKILL.md`'s "4a",
            "4c".
        read_from: taken from the first copy; `desk.proof.gather` refuses a set
            that disagrees.
        edit_copies: one per role, or one per SHARD under fan-out.
    """

    stage: str
    read_from: dict
    edit_copies: tuple[EditCopy, ...]


def parse_sheet(where: str, data: object) -> tuple[Sheet | None, list[str]]:
    """One sheet, checked.

    Args:
        where: how to name this sheet in a message.
        data: one entry of an edit_copy's `sheets`, as it came back.

    Returns:
        `(Sheet, [])` or `(None, [messages])`. An absent `sha` is admitted as
        "" -- a page can be censused from a tree that is not a repo, which is
        what `flows.revise.pull` produces.
    """
    if not isinstance(data, dict):
        return None, [f"{where}: a sheet must be an object"]
    path = data.get("path")
    if not isinstance(path, str) or not path.strip():
        return None, [f"{where}: a sheet needs the `path` of the page it holds"]
    marks = data.get("marks")
    if not isinstance(marks, list):
        return None, [f"{where}: {path} needs a `marks` list"]
    return Sheet(path=path, sha=str(data.get("sha", "")), marks=tuple(marks)), []


def parse_edit_copy(where: str, data: object) -> tuple[EditCopy | None, list[str]]:
    """One edit_copy and every sheet under it, checked.

    ! EVERY BAD SHEET IS REPORTED, not the first. A copy handed back with two
    malformed sheets is two things to fix, and a parse that stopped at the
    first would make the second invisible until the next run.

    Args:
        where: how to name this copy in a message.
        data: one edit_copy, as `flows.marks.seed` builds one.

    Returns:
        `(EditCopy, [])` or `(None, [messages])`.
    """
    if not isinstance(data, dict):
        return None, [f"{where}: an edit_copy must be an object"]
    # ! REBOUND, ANNOTATED -- `ty` loses the `isinstance` narrowing above by
    # the time `data["read_from"]` is read past the `for` loop below; this
    # matches `desk.mark.parse`'s own `data: dict = entry` for the same gate.
    data: dict = data
    role = data.get("role")
    if not isinstance(role, str) or not role.strip():
        return None, [f"{where}: an edit_copy needs the `role` that wrote it"]
    why_header = _read_from_problem(data)
    if why_header:
        return None, [f"{where}: {role}'s {why_header}"]
    raw_sheets = data.get("sheets")
    if not isinstance(raw_sheets, list):
        return None, [f"{where}: {role} needs a `sheets` list"]
    sheets: list[Sheet] = []
    problems: list[str] = []
    for i, raw in enumerate(raw_sheets, 1):
        sheet, why = parse_sheet(f"{where}: {role} sheet {i}", raw)
        if sheet is None:
            problems += why
        else:
            sheets.append(sheet)
    if problems:
        return None, problems
    return (
        EditCopy(
            role=role,
            # ! COPIED, NOT ALIASED -- `bind`, `seed` and `gather` all do the
            # same with this field, so a caller mutating its own dict cannot
            # change what a parsed copy already holds.
            read_from={**data["read_from"]},
            sheets=tuple(sheets),
        ),
        [],
    )


def parse_master_proof(
    where: str, data: object
) -> tuple[MasterProof | None, list[str]]:
    """One master_proof and every copy under it, checked.

    Args:
        where: how to name this proof in a message -- its stage label.
        data: a master_proof, as `desk.proof.gather` returns one.

    Returns:
        `(MasterProof, [])` or `(None, [messages])`. Every bad copy is reported.
    """
    if not isinstance(data, dict):
        return None, [f"{where}: a master_proof must be an object"]
    raw_copies = data.get("edit_copies")
    if not isinstance(raw_copies, list):
        return None, [f"{where}: a master_proof needs an `edit_copies` list"]
    copies: list[EditCopy] = []
    problems: list[str] = []
    for i, raw in enumerate(raw_copies, 1):
        copy, why = parse_edit_copy(f"{where}: edit_copy {i}", raw)
        if copy is None:
            problems += why
        else:
            copies.append(copy)
    if problems:
        return None, problems
    read_from = data.get("read_from")
    return (
        MasterProof(
            stage=str(data.get("stage", "")),
            read_from={**read_from} if isinstance(read_from, dict) else {},
            edit_copies=tuple(copies),
        ),
        [],
    )
