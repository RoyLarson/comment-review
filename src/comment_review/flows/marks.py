"""Hand a role a sheet to fill, and check what comes back.

    seed(binder, role)     one entry per row, ADDRESS ALREADY WRITTEN
    problems_in(report)    every rule `desk.mark` settles, over a whole file

!! THE SHEET IS SEEDED BECAUSE THE ADDRESS IS THE PART ROLES GET WRONG.
MEASURED 2026-08-27: with a one-file binder every fanned-out agent wrote a bare
cue -- 62 of 78 marks -- despite the row carrying the full address and the packet
saying to copy it. With one file in play the path READS as redundant. **A bare
cue collides on merge: `a0` then means four different places**, and the fan-out
results showed zero overlap with the full rounds until the differing form was
noticed. ! Seeding removes the transcription rather than instructing against it.

! A seeded entry's `mark` is `None` -- not ruled yet. A place left `None` when
the sheet comes back is a COVERAGE GAP, which is a different thing from `clean`:
`clean` says a role read this and had nothing to report.

!! WHAT THIS FLOW DOES NOT DO IS CHECK A CLAIM AGAINST THE PAGE. Whether
`claim.false` appears VERBATIM in the paragraph, whether a `move`'s destination
is addressable -- both need the page the role read, and both belong to
SOURCE-VERIFICATION in `collator`, which is not built. `desk.mark.problems`
says the same about its own half.
"""

from comment_review.binder.binder import rows_of
from comment_review.desk.mark import INSTRUCTIONS, problems


def seed(binder: dict, role: str) -> dict:
    """A fillable sheet for one role, one entry per row in the binder.

    Args:
        binder: as `binder.read` returns it.
        role: the editorial role this sheet is for.

    Returns:
        `{"role": ..., "read_from": ..., "marks": [...]}` -- `read_from` is
        copied from the binder as-is, naming the root and revise this sheet
        was censused from. Each mark entry carries the `address`, `anchor`
        and `raw_text` copied from its row, and `mark: None` for the role to
        fill. `raw_text` is the paragraph the role's `change` diffs against
        -- see `docs/the-mark.md`.

    Raises:
        KeyError: the binder carries no `read_from`.

    !! ABSENT IS REFUSED HERE TOO, AND WAS DEFAULTED TO `{}` UNTIL 2026-08-28.
    `bind` refuses a binder that cannot say which root it read; this function
    read the same key with a `{}` fallback, so a binder that reached it by any
    other path -- an artifact read from disk, a hand-built dict -- produced a
    sheet whose `read_from` was empty. ! THAT IS THE AMBIGUITY THE FIELD WAS
    ADDED TO REMOVE, one function downstream of the refusal: a role holding an
    empty `read_from` cannot tell a revise from the original, which is the
    whole question `decision-log.md Process: #34` turns on.
    """
    return {
        "role": role,
        "read_from": binder["read_from"],
        "marks": [
            {
                "address": row.get("address", ""),
                "anchor": row.get("anchor", ""),
                "raw_text": row.get("raw_text", ""),
                "mark": None,
            }
            for row in rows_of(binder)
        ],
    }


def problems_in(report: dict) -> tuple[list[str], int]:
    """Every rule broken in a filled sheet, and how many places were ruled on.

    ! A `mark` of `None` is NOT a problem -- it is an unruled place, and the
    count returned is what says how much of the sheet was answered. Refusing it
    here would make an unfinished sheet indistinguishable from a malformed one.

    Returns:
        `(messages, ruled)` -- one message per broken rule, and the number of
        entries carrying an instruction.
    """
    if not isinstance(report.get("marks"), list):
        return ["the report needs a `marks` list"], 0

    out, ruled = [], 0
    if not isinstance(report.get("role"), str) or not report["role"].strip():
        out.append("the report needs the `role` that wrote it")

    for i, mark in enumerate(report["marks"], 1):
        if not isinstance(mark, dict):
            out.append(f"mark {i} is not an object")
            continue
        if mark.get("mark") is None:
            continue
        ruled += 1
        where = mark.get("address") or f"mark {i}"
        out += problems(where, mark)
    return out, ruled


def unruled(report: dict) -> list[str]:
    """The addresses left `None` -- the coverage gap, named rather than counted."""
    marks = report.get("marks")
    if not isinstance(marks, list):
        return []
    return [
        str(m.get("address", ""))
        for m in marks
        if isinstance(m, dict) and m.get("mark") is None
    ]


def tally(report: dict) -> dict[str, int]:
    """How many of each instruction the sheet carries, for a one-line summary."""
    counts = dict.fromkeys(INSTRUCTIONS, 0)
    for mark in report.get("marks", []):
        if isinstance(mark, dict) and mark.get("mark") in counts:
            counts[mark["mark"]] += 1
    return {name: n for name, n in counts.items() if n}
