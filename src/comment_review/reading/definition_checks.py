"""Value checks every language definition validator applies to its rules."""

from collections.abc import Mapping
from typing import cast


def require_table(value: object, path: str, keys: str) -> Mapping[str, object]:
    """Require a table holding exactly the space-separated `keys`.

    Raises:
        ValueError: `value` is no table, or a key is missing or unknown.
    """
    if not isinstance(value, Mapping):
        raise ValueError(f"{path} must be a table")
    table = cast(Mapping[str, object], value)
    required = set(keys.split())
    missing = required - table.keys()
    unknown = table.keys() - required
    if missing:
        raise ValueError(f"{path}.{sorted(missing)[0]} is required")
    if unknown:
        raise ValueError(f"{path}.{sorted(unknown)[0]} is unknown")
    return table


def require_scalar(value: object, path: str, supported: str | bool | int) -> None:
    """Require `value` to equal `supported` and share its type.

    Raises:
        ValueError: the type or the value differs.
    """
    kind = (
        "boolean"
        if isinstance(supported, bool)
        else "string"
        if isinstance(supported, str)
        else "integer"
    )
    if type(value) is not type(supported):
        raise ValueError(f"{path} must be a {kind}")
    if value != supported:
        raise ValueError(f"{path} has unsupported value {value!r}")


def require_array(value: object, path: str, supported: tuple[object, ...]) -> None:
    """Require a tuple whose items equal `supported` in order and type.

    Raises:
        ValueError: the length, an item's type or an item's value differs.
    """
    if not isinstance(value, tuple):
        raise ValueError(f"{path} must be an array")
    if len(value) != len(supported):
        raise ValueError(f"{path} has unsupported items")
    for item, expected in zip(value, supported, strict=True):
        if type(item) is not type(expected):
            raise ValueError(f"{path} contains an ill-typed item")
        if item != expected:
            raise ValueError(f"{path} has unsupported item {item!r}")
