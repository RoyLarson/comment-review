"""The seed half of the round trip: a container as the wire dict it is written as.

    _wire_fields(cls)       the field names on the wire, in the class's order
    _written(cls, values)   `values` as the wire dict, refusing a wrong key set

!! THE WIRE STAYS DICTS. Each parse has `desk.proof.mark.read_mark`'s own
contract -- `(T, [])` or `(None, [one message per broken rule])` -- so a caller holds a
checked object rather than re-deriving the same keys with `isinstance`
ladders.

!! BOTH HALVES OF THE ROUND TRIP LIVE ON THE CLASS. `Sheet.seed` and
`EditCopy.seed` write a container from the class's own field names through
`_written` -- `Process: #64` -- and each class's `deserialize` reads one back.
Renaming a field breaks at construction rather than folding to a default one
module away, which `desk.proof.mark.BlankMark` holds one level down by writing
a slot from its own field names.

!!! **`seed` RETURNS THE WIRE DICT AND THAT IS CORRECT** -- `Process: #66`. A
seed is an EMPTY FORM, not a ruling: `desk.proof.mark.BlankMark` writes three of
a mark's eight fields plus `instruction: None`, and is its own type rather than
a `Mark` with five optionals, so holding a `Mark` still means the ruling is
complete. **The split is `parse` versus `seed`, not container
versus dict** -- a parse answers *is this a filled, well-formed X* and returns
the type; a seed answers *what does an unfilled X look like on the wire*.

! **THIS PARAGRAPH SAID THE OPPOSITE FOR ABOUT AN HOUR ON 2026-08-31**, claiming
`Process: #65` overrode the return type and citing the mark's seed/`serialize`
split as the precedent. **Both of those return dicts.** `#65` governs what a
flow CARRIES between its load and its save; a seed is emitted AT a save --
`flows.distribute.seed` builds one and the command writes it as the JSON a role
is handed -- so the dict is where that ruling puts it.
"""

from dataclasses import fields


def _wire_fields(cls) -> list[str]:
    """The field names that are on the WIRE, in the class's own order.

    !! NOT EVERY FIELD IS A WIRE FIELD, since `P51`. `Sheet.unruled` and
    `Sheet.refused` are DERIVED by the parse -- they are what the entries that
    are not a `Mark` came to -- so a producer must not be asked to write them
    and `_written` must not demand them. A field is off the wire when its
    metadata says `wire: False`; everything else is on it, which keeps the
    default the safe one.
    """
    return [f.name for f in fields(cls) if f.metadata.get("wire", True)]


def _written(cls, values: dict) -> dict:
    """One container as the wire dict, keyed by `cls`'s OWN field names.

    !! THE WRITE HALF OF THE ROUND TRIP LIVES WITH THE READ HALF, ruled
    `decision-log.md Process: #64`: every producer spelled these keys as
    literals, so renaming a field left another module writing the old key and
    NOTHING could notice -- `Sheet.deserialize` folds an absent `sha` to `""`
    and reports no problem.

    Args:
        cls: the container dataclass being written.
        values: one entry per declared field, by name.

    Returns:
        `values`, in the class's own field order.

    Raises:
        AttributeError: `values` names a field the class does not declare, or
            omits one it does. ! THIS IS THE WHOLE GUARD, and it fires at the
            point the row is built rather than silently one module away.
    """
    declared = _wire_fields(cls)
    if set(values) != set(declared):
        raise AttributeError(
            f"{cls.__name__}.seed writes {sorted(values)}, "
            f"which is not {cls.__name__}'s wire fields {sorted(declared)}"
        )
    return {name: values[name] for name in declared}
