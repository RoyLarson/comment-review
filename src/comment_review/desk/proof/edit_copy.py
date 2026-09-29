"""One role's copy of the binder -- what goes out, and what comes back.

! THE CHIEF'S COPY IS AN ORDINARY `EditCopy`. `Vocabulary: #30`: after the fold
every place has exactly one answer, and one mark per place is an ordinary copy.
There is no second shape and no second parse.
"""

from dataclasses import dataclass

from comment_review.binder.binder import _read_from_problem
from comment_review.desk.proof.mark import (
    Instruction,
    a_type,
    filled,
    read_member,
    read_text,
)
from comment_review.desk.proof.sheet import Sheet
from comment_review.desk.proof.wire import _written


@dataclass(frozen=True)
class EditCopy:
    """One role's copy of the binder -- what goes out, and what comes back.

    Attributes:
        role: the editorial role that filled it, or `copy-chief` for the fold's
            result. It is what an outcome is decided from and what a place is
            sent back to.
        read_from: `{root, revise}` -- which tree this copy was gathered from.
            `decision-log.md Process: #34`: the field exists so a later role can
            know it holds a REVISE and not the original.
        stage: the stage this copy was dealt in, as the run's topology names
            it, or "" where the seed was handed no stage. A refusal names it,
            so a role reads which stage's row refused its ruling, and the
            collate handler folds a copy only in the stage it names.
        admits: the instructions this stage's roles may file, by name, or
            empty for every one of them (`decision-log.md Process: #193`).
            Each is one of the seven instructions.
            It rides on the copy for the reason `read_from` does: the rule
            is about the artifact in hand, so `commands/mark.py` and
            `commands/check.py` hold a copy to it without being handed the
            run's topology beside it. `flows.bus._on_copies` holds the
            returned marks to the stage's own row instead.
        sheets: one per page.
    """

    role: str
    read_from: dict
    sheets: tuple[Sheet, ...]
    stage: str = ""
    admits: tuple[str, ...] = ()

    @classmethod
    def seed(
        cls,
        role: str,
        read_from: dict,
        sheets: list,
        stage: str = "",
        admits: list | None = None,
    ) -> dict:
        """One edit_copy as the wire dict `flows.distribute.seed` hands out.

        Args:
            role: the editorial role this copy is for.
            read_from: `{root, revise}` -- which tree it was gathered from.
            sheets: one `Sheet.seed` dict per page.
            stage: the stage being dealt, or "" where the caller names none.
            admits: the instructions its roles may file, or None for all.

        Returns:
            `{role, read_from, sheets, stage, admits}`. ! `read_from` IS
            COPIED, NOT ALIASED, as `bind`, `seed` and the bus's `_on_copies`
            all do with this field: a caller mutating its own dict afterward
            cannot change what this copy holds.
        """
        return _written(
            cls,
            {
                "role": role,
                "read_from": {**read_from},
                "sheets": list(sheets),
                "stage": stage,
                "admits": list(admits or []),
            },
        )

    @classmethod
    def deserialize(
        cls, where: str, data: object
    ) -> "tuple[EditCopy | None, list[str]]":
        """One edit_copy and every sheet under it, checked.

        ! EVERY BAD SHEET IS REPORTED, not the first. A copy handed back with two
        malformed sheets is two things to fix, and a parse that stopped at the
        first would make the second invisible until the next run.

        Args:
            where: how to name this copy in a message.
            data: one edit_copy, as `flows.distribute.seed` builds one.

        Returns:
            `(EditCopy, [])` or `(None, [messages])`. A `stage` that is not a
            string, an `admits` that is not a list, and an `admits` entry that
            names no instruction are each refused by name. An absent or null
            `stage` reads as "", no stage named; an absent or null `admits` as
            empty, every instruction admitted -- what a copy seeded without a
            stage row carries.
        """
        if not isinstance(data, dict):
            return None, [f"{where}: an edit_copy must be an object"]
        # !! DECLARED, NOT NARROWED, because the read at `checked["read_from"]`
        # below sits past a loop. An `isinstance` narrow is invalidated at a loop
        # back-edge, so `ty` loses it before that read; an explicit annotation is
        # a declaration and survives.
        checked: dict = data
        role = checked.get("role")
        if not filled(role):
            return None, [f"{where}: an edit_copy needs the `role` that wrote it"]
        why_header = _read_from_problem(checked)
        if why_header:
            return None, [f"{where}: {role}'s {why_header}"]
        raw_sheets = checked.get("sheets")
        if not isinstance(raw_sheets, list):
            return None, [f"{where}: {role} needs a `sheets` list"]
        sheets: list[Sheet] = []
        problems: list[str] = []
        for i, raw in enumerate(raw_sheets, 1):
            sheet, why = Sheet.deserialize(f"{where}: {role} sheet {i}", raw)
            if sheet is None:
                problems += why
            else:
                sheets.append(sheet)
        stage, why = read_text(f"{where}: {role}", "stage", checked.get("stage"))
        problems += why
        admits, why = _admits_of(f"{where}: {role}", checked.get("admits"))
        problems += why
        if problems:
            return None, problems
        return (
            EditCopy(
                role=role,
                # ! COPIED, NOT ALIASED -- `bind`, `seed` and the bus's `_on_copies`
                # all do the same with this field, so a caller mutating its own
                # dict cannot change what a parsed copy already holds.
                read_from={**checked["read_from"]},
                sheets=tuple(sheets),
                stage=stage,
                admits=admits,
            ),
            [],
        )

    def serialize(self) -> dict:
        """This edit_copy as the wire dict, the shape `seed` writes.

        ! `read_from` IS COPIED, NOT ALIASED, matching `seed` and every other
        producer of this field.
        """
        return {
            "role": self.role,
            "read_from": {**self.read_from},
            "sheets": [sheet.serialize() for sheet in self.sheets],
            "stage": self.stage,
            "admits": list(self.admits),
        }


def _admits_of(where: str, value: object) -> "tuple[tuple[str, ...], list[str]]":
    """A copy's `admits`, each entry one of the seven, or one problem per bad one.

    Absent or null is empty -- every instruction admitted.
    """
    if value is None:
        return (), []
    if not isinstance(value, list):
        return (), [
            f"{where}: `admits` must be a list of instructions, not {a_type(value)}"
        ]
    admits: list[str] = []
    problems: list[str] = []
    for one in value:
        member, why = read_member(where, "admits", one, Instruction)
        problems += why
        if member is not None:
            admits.append(str(member))
    return tuple(admits), problems
