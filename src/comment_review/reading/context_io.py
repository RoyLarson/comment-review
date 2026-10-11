"""Encode and decode saved reading contexts without installed-language lookup."""

from typing import cast

from comment_review.reading.context import ReadingContext


def context_to_wire(context: ReadingContext) -> dict:
    """Return a detached version-one wire object with sorted settings."""
    return {
        "format": 1,
        "language": context.language,
        "reader": context.reader,
        "compatibility": context.compatibility,
        "settings": dict(sorted(context.settings)),
    }


def context_from_wire(
    where: str, value: object
) -> tuple[ReadingContext | None, list[str]]:
    """Decode the strict wire shape and locate expected validation failures."""

    def failure(message: str) -> tuple[None, list[str]]:
        return None, [f"{where}: {message}; regather to save a fresh reading context"]

    if value is None:
        return failure("reading context is missing")
    if type(value) is not dict:
        return failure("reading context must be an object")
    wire = cast(dict[object, object], value)
    required = {"format", "language", "reader", "compatibility", "settings"}
    missing = required - wire.keys()
    if missing:
        return failure(f"reading context is missing keys: {', '.join(sorted(missing))}")
    if wire.keys() != required:
        return failure("reading context contains unknown keys")
    if type(wire["format"]) is not int or wire["format"] != 1:
        return failure("unsupported reading context format; expected integer 1")
    for name in ("language", "reader", "compatibility"):
        if type(wire[name]) is not str:
            return failure(f"reading context {name} must be a string")
    settings = wire["settings"]
    if type(settings) is not dict:
        return failure("reading context settings must be an object")
    entries = cast(dict[object, object], settings)
    if any(
        type(key) is not str or type(item) is not str for key, item in entries.items()
    ):
        return failure("reading context settings require string keys and values")
    try:
        context = ReadingContext(
            cast(str, wire["language"]),
            cast(str, wire["reader"]),
            cast(str, wire["compatibility"]),
            tuple(cast(dict[str, str], entries).items()),
        )
    except ValueError as exc:
        return failure(str(exc))
    return context, []
