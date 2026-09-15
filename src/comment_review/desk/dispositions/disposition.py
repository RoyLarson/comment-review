"""What the chief rules at a carried-forward place."""

from dataclasses import dataclass, fields

from comment_review.desk.marks.mark import filled

ORIGINAL = "original"
CHIEF = "copy-chief"


@dataclass(frozen=True)
class Disposition:
    """One chief's ruling on one carried-forward place."""

    address: str
    name: str
    side: str
    prose: str
    reason: str

    def serialize(self) -> dict:
        """This ruling as the wire entry a docket carries -- its OWN field names."""
        out = {f.name: getattr(self, f.name) for f in fields(self)}
        out["answer"] = out.pop("name")
        return out

    @classmethod
    def deserialize(
        cls, where: str, entry: object
    ) -> "tuple[Disposition | None, list[str]]":
        """One entry becomes a `Disposition`, or becomes named problems."""
        from comment_review.desk.answers.table import ANSWERS
        from comment_review.desk.dispositions.table import DISPOSITIONS
        from comment_review.desk.marks.table import INSTRUCTIONS

        if not isinstance(entry, dict):
            return None, [f"{where}: a ruling must be an object"]
        data: dict = entry
        name = str(data.get("answer"))
        if name in INSTRUCTIONS or any(name == n for _, n in ANSWERS):
            return None, [
                f"{where}: `{name}` is a role's answer; the chief's ruling is owed here"
            ]
        row = DISPOSITIONS.get(name)
        if row is None:
            return None, [
                f"{where}: `answer` must be one of {', '.join(sorted(DISPOSITIONS))}"
            ]
        out = []
        if not filled(data.get("address")):
            out.append(f"{where}: {name} needs the `address`")
        if not filled(data.get("reason")):
            out.append(f"{where}: {name} needs a `reason`")
        for key in row.owes:
            if not filled(data.get(key)):
                out.append(f"{where}: {name} needs `{key}`")
        if out:
            return None, out
        return (
            cls(
                address=str(data.get("address") or ""),
                name=name,
                side=str(data.get("side") or row.side),
                prose=str(data.get("prose") or ""),
                reason=str(data.get("reason") or ""),
            ),
            [],
        )
