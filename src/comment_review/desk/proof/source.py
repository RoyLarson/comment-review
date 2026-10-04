"""The fields and intrinsic checks of a supplied source entry."""

REQUIRED = ("cite", "verbatim")
OPTIONAL = ("ran",)


def contract() -> dict[str, list[str]]:
    """The required and optional source keys published to a role."""
    return {"required": list(REQUIRED), "optional": list(OPTIONAL)}


def entry_problems(
    where: str, source: object, *, completing: bool = False
) -> list[str]:
    """Check one entry, allowing an omitted quote during cite-only completion."""
    if not isinstance(source, dict):
        return [f"{where} must be an object with `cite` and `verbatim`"]
    out = []
    for key in REQUIRED:
        if completing and key == "verbatim" and key not in source:
            continue
        value = source.get(key)
        if not isinstance(value, str) or not value.strip():
            out.append(f"{where} needs `{key}`")
    return out


def problems(where: str, sources: tuple[object, ...]) -> list[str]:
    """Check every supplied entry in order, keeping its source position."""
    return [
        problem
        for i, source in enumerate(sources, 1)
        for problem in entry_problems(f"{where}: source {i}", source)
    ]
