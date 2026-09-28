"""One role's copy of the binder -- what goes out, and what comes back.

! THE CHIEF'S COPY IS AN ORDINARY `EditCopy`. `Vocabulary: #30`: after the fold
every place has exactly one answer, and one mark per place is an ordinary copy.
There is no second shape and no second parse.
"""

from dataclasses import dataclass

from comment_review.binder.binder import _read_from_problem
from comment_review.desk.proof.mark import filled
from comment_review.desk.proof.sheet import Sheet
from comment_review.desk.proof.validators import Validators
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
            so a role reads which stage's row refused its ruling.
        admits: the instructions this stage's roles may file, by name, or
            empty for every one of them (`decision-log.md Process: #193`).
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
        cls, where: str, data: object, validators: Validators
    ) -> "tuple[EditCopy | None, list[str]]":
        """One edit_copy and every sheet under it, checked.

        ! EVERY BAD SHEET IS REPORTED, not the first. A copy handed back with two
        malformed sheets is two things to fix, and a parse that stopped at the
        first would make the second invisible until the next run.

        Args:
            where: how to name this copy in a message.
            data: one edit_copy, as `flows.distribute.seed` builds one.
            validators: the rule checks every sheet's ruled entries are held to.

        Returns:
            `(EditCopy, [])` or `(None, [messages])`.
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
            sheet, why = Sheet.deserialize(
                f"{where}: {role} sheet {i}", raw, validators
            )
            if sheet is None:
                problems += why
            else:
                sheets.append(sheet)
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
                # Both are read where present and defaulted where not. A
                # copy written before `#193`, and one from a stage whose row
                # says nothing more, carries neither -- and an ordinary
                # stage is exactly the case where both are empty.
                stage=str(checked.get("stage") or ""),
                admits=tuple(
                    one for one in (checked.get("admits") or []) if isinstance(one, str)
                ),
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
