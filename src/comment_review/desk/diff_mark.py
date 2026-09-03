"""A PROTOTYPE. `DiffMark`: a role's answer to "does your finding still stand".

!! NOTHING WIRES THIS IN YET. Roy, 2026-09-03: *"That looks like a good prototype
to test out the workflow. Keep it a prototype until we get all of the pieces
together."* `docs/plans/0.2.4-the-mark-and-the-collator.md` P20 (`DiffMark`
itself) and P21 (`batch_of`) are this file; P16 (the return and parse), P17
(the recollate) and P18/P19 (the round counter and the chief's cap ruling)
are what would make a `DiffMark` reach a role or come back from one. Until
they land this module has no caller.

=== WHY IT IS NOT A `Mark`

`docs/the-revise.md`, `decision-log.md Process: #22`: a `DiffMark` is *"a
DIFFERENT ARTIFACT answering a different question -- does your finding still
stand rather than what is wrong with this page -- so it carries its own closed
set. The seven stay seven."* Its closed set is `hold`, `withdraw`, `correct`,
`patch`.

=== WHY IT CARRIES FEWER FIELDS THAN `Mark`

`docs/the-revise.md` never asks a `DiffMark` for a structured `claim` or for
`sources`: a `Mark` builds an evidentiary case from nothing, a `DiffMark`
revisits one that already went through that. `desk.mark.Mark`'s spec is
`docs/the-mark.md`, which this shape is deliberately NOT added to -- that file
is what `Row` and `Mark` are checked against
(`tests/gates/test_mark_shape.py`), and `desk/mark.py`'s own header states its
contract is to implement that spec and *"define nothing"* of its own.
`Process: #37` records what an unapproved field scheme cost that file once
already; this stays a separate module for the same reason
`desk/external_address.py` does.

=== WHAT IS OPEN, AND NOT GUESSED

Which of the four answers is legal for a COMPOSITION re-read versus a
CONFLICT is `docs/plans/0.2.4-the-mark-and-the-collator.md` P1/P4/P5/P6, and
is not decided here. `docs/the-revise.md` reads as though a composition
re-read goes back through `Mark`'s own `clean`/`query` rather than through a
`DiffMark` at all -- NOT RULED, and this module takes no side on it.
"""

from dataclasses import dataclass, fields
from enum import StrEnum, auto

from comment_review.desk.mark import INSTRUCTIONS, filled


class DiffInstruction(StrEnum):
    """The four, closed. `docs/the-revise.md` is the source; this only names them.

    ! Value derived from the member name via `_generate_next_value_`, following
    `desk.mark.Instruction`'s own precedent -- `DiffInstruction.HOLD == "hold"`
    holds without a hand-typed string.
    """

    @staticmethod
    def _generate_next_value_(
        name: str, start: int, count: int, last_values: list[str]
    ) -> str:
        return name.lower()

    HOLD = auto()
    WITHDRAW = auto()
    CORRECT = auto()
    PATCH = auto()


@dataclass(frozen=True)
class DiffMark:
    """One role's answer to one disagreement -- does its finding still stand.

    Attributes:
        address: `path@cue`. WHICH PLACE -- seeded, copied from the
            escalation or reread entry, never built.
        anchor: the line of code the place sits on -- seeded.
        instruction: one of the four, as a `DiffInstruction` member.
        reason: WHY, in prose. No checker settles it.
        change: the RESULT -- the updated paragraph, as raw text, for
            `correct` and `patch`. Empty for `hold` and `withdraw`.
    """

    address: str
    anchor: str
    instruction: DiffInstruction
    reason: str
    change: str

    #: The fields SEEDED onto every slot before a role sees it, following
    #: `Mark.SEEDED`'s own convention.
    SEEDED = ("address", "anchor")

    @classmethod
    def seed(cls, address: str, anchor: str) -> dict:
        """One fillable slot, keyed by this class's OWN field names.

        Args:
            address: `path@cue`, the place going back out.
            anchor: the line of code the place sits on, or "".

        Returns:
            `{address, anchor, instruction: None}` -- the slot as a role
            receives it.

        Raises:
            AttributeError: `SEEDED` names something `DiffMark` does not
                declare -- the same guard `Mark.seed` carries, for the same
                reason: a rename breaks HERE, loudly, rather than one module
                away.
        """
        declared = {f.name for f in fields(cls)}
        row: dict = {}
        for name, value in zip(cls.SEEDED, (address, anchor), strict=True):
            if name not in declared:
                raise AttributeError(
                    f"DiffMark.seed writes `{name}`, which DiffMark does not declare"
                )
            row[name] = value
        row["instruction"] = None
        return row

    def serialize(self) -> dict:
        """This diff mark as the wire entry a sheet carries -- its OWN field names.

        Returns:
            A dict `deserialize` accepts and returns an equal `DiffMark` from.
        """
        entry = {f.name: getattr(self, f.name) for f in fields(self)}
        entry["instruction"] = str(self.instruction)
        return entry

    @classmethod
    def deserialize(
        cls, where: str, entry: object
    ) -> "tuple[DiffMark | None, list[str]]":
        """THE BOUNDARY -- one entry becomes a `DiffMark`, or becomes named problems.

        !! A `Mark` IS REFUSED HERE, BY NAME. An `instruction` naming one of
        `Mark`'s seven that is not also one of the four -- `clean`, `query`,
        `drop`, `add`, `move` -- means a role answered with a fresh finding
        where a diff mark was owed, and this says so rather than reading it
        as one of the four it happens to share a spelling with.

        Args:
            where: how to name this diff mark in a message.
            entry: one role's answer to a disagreement, as it came back.

        Returns:
            `(DiffMark, [])` or `(None, [one message per broken rule])`.
        """
        if not isinstance(entry, dict):
            return None, [f"{where}: a diff mark must be an object"]
        data: dict = entry
        if "instruction" not in data:
            return None, [
                f"{where}: carries no `instruction` -- the field naming which of "
                f"{', '.join(sorted(DiffInstruction))} this diff mark is"
            ]
        named = data["instruction"]
        if (
            isinstance(named, str)
            and named in INSTRUCTIONS
            and named not in set(DiffInstruction)
        ):
            return None, [
                f"{where}: `{named}` is one of Mark's own seven, not one of "
                f"{', '.join(sorted(DiffInstruction))} -- a diff mark is owed here, "
                "not a fresh finding"
            ]
        if not isinstance(named, str) or named not in set(DiffInstruction):
            return None, [
                f"{where}: `instruction` must be one of "
                f"{', '.join(sorted(DiffInstruction))}"
            ]

        instruction = DiffInstruction(named)
        out = []
        if not filled(entry.get("address")):
            out.append(
                f"{where}: {instruction} needs the `address`, copied from the row"
            )
        if not filled(entry.get("reason")):
            out.append(f"{where}: {instruction} needs a `reason`")
        change = entry.get("change")
        owes_change = instruction in (DiffInstruction.CORRECT, DiffInstruction.PATCH)
        if owes_change and not filled(change):
            out.append(f"{where}: {instruction} needs a `change`")
        if out:
            return None, out

        return (
            DiffMark(
                address=str(entry.get("address") or ""),
                anchor=str(entry.get("anchor") or ""),
                instruction=instruction,
                reason=str(entry.get("reason") or ""),
                change=change if isinstance(change, str) else "",
            ),
            [],
        )


def batch_of(escalations: list[dict], rereads: list[dict]) -> dict[str, list[dict]]:
    """Every disagreement, grouped into one payload per role -- P21.

    `docs/the-revise.md`: *"all of the disagreements are sent out as one
    batch with the diffs to the agents."* One entry per role in the result,
    holding every place that role owes -- ONE SEND PER ROLE WHATEVER THE
    PLACE COUNT, which is P21's own verify.

    Args:
        escalations: `desk.collator.Reconciled.escalations`, or the same
            shape narrowed by a round -- `flows.collate.Collated.escalations`
            after the places that resolved on their own are gone. Each entry
            is `{"address", "roles", "marks": list[Placed]}`.
        rereads: the same shape, for places whose composition did not
            resolve.

    Returns:
        role -> the `DiffMark` slots that role owes, each seeded via
        `DiffMark.seed` and carrying `marks` -- `{"role", **mark.serialize()}`
        for every mark already at that place, INCLUDING the role's own.
        `role` rides beside the mark rather than inside it because `Mark`
        carries no such field -- `desk.collator.Placed` is the pair, the same
        reason it exists there. That list is THE DIFF: a role answering "does
        your finding still stand" is comparing its own entry against
        whoever it disagrees with, and needs to see whose is whose.
    """
    batch: dict[str, list[dict]] = {}
    for entry in (*escalations, *rereads):
        marks = entry["marks"]
        anchor = marks[0].mark.anchor if marks else ""
        context = [{"role": placed.role, **placed.mark.serialize()} for placed in marks]
        for role in entry["roles"]:
            slot = DiffMark.seed(entry["address"], anchor)
            slot["marks"] = context
            batch.setdefault(role, []).append(slot)
    return batch
