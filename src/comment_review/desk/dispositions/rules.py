"""The rules a chief's ruling is held to, read off its row in the dispositions table.

    validate()   one ruling against its row -- every broken rule, named
    side_of()    the side a ruling takes -- its own, or the one its row fixes

The ruling itself -- its fields and its structural read -- is
`desk.proof.disposition`, and `read_disposition` applies this after that read
(`decision-log.md Process: #203`).
"""

from comment_review.desk.answers.table import ANSWERS
from comment_review.desk.dispositions.table import DISPOSITIONS
from comment_review.desk.marks.table import INSTRUCTIONS
from comment_review.desk.proof.disposition import Disposition
from comment_review.desk.proof.mark import filled


def validate(where: str, disposition: Disposition) -> list[str]:
    """Every rule `disposition`'s row states that the ruling breaks.

    Args:
        where: how to name this ruling in a message -- its address.
        disposition: the entry as `Disposition.deserialize` read it, a field
            of the wrong type already read as absent.

    Returns:
        One message per broken rule; empty for a ruling that keeps its row. A
        name that is a role's instruction or answer, or no row's at all, is
        one message, and nothing else is asked of it.
    """
    name = disposition.name
    if name in INSTRUCTIONS or any(name == n for _, n in ANSWERS):
        return [
            f"{where}: `{name}` is a role's answer; the chief's ruling is owed here"
        ]
    row = DISPOSITIONS.get(name)
    if row is None:
        return [f"{where}: `answer` must be one of {', '.join(sorted(DISPOSITIONS))}"]
    out = []
    if not filled(disposition.address):
        out.append(f"{where}: {name} needs the `address`")
    if not filled(disposition.reason):
        out.append(f"{where}: {name} needs a `reason`")
    for key in row.owes:
        if not filled(getattr(disposition, key)):
            out.append(f"{where}: {name} needs `{key}`")
    return out


def side_of(disposition: Disposition) -> str:
    """The side `disposition` takes: its own, or where it names none, its row's.

    The row's `side` is `CHIEF` on `recast` and "" elsewhere, so a recast that
    names no side takes the chief's own, and the table is the one place that
    says so.
    """
    return disposition.side or DISPOSITIONS[disposition.name].side
