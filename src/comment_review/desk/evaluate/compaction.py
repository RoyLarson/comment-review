"""Which decided places may take a compacted text, and which may not.

`decision-log.md Process: #191`: stage 6 condenses text the fold has already
decided, so the compacted text is written onto the place that holds it.
The rule is here rather than in the flow because it is a rule about a place's
state, the way the passes beside this file are.

Four refusals, and every one of them is a place where a shorter wording would
be replacing something other than a decided text:

    the proof carries no place here    nothing was decided to condense
    the place settled on no text       it stands on the paragraph already there
    the place has not settled          carried forward, held for the human, refused
    the compacted text is empty        compaction condenses, it does not delete

The last is the pass's own rule read back from
`skills/comment-review/references/compact.md`: a paragraph that cannot be
brought under the cap is reported at length, never cut away, and a `drop` is
an instruction a role files at stage 4 and the fold rules on.

What it does not ask is whether the paragraph is a comment or a docstring.
That rule is compact.md's -- a cap never applies to a docstring -- and no
ruling puts it here.

A move's two ends are two places with two texts, and one may be condensed
without the other: `flows.transcribe.docket_of_proof` sets each end from its
own place, so a shorter wording at one end changes nothing about what the
other end writes. That is not true of approving one end alone, which is why
the filter there refuses a half move and this does not.
"""

from comment_review.desk.evaluate.place import Place
from comment_review.desk.evaluate.state import SETTLED


def compacted(
    places: dict[str, Place], rows: list
) -> tuple[dict[str, str], list[tuple[str, str]]]:
    """The text to write at each place, or every reason one may not be written.

    Args:
        places: address -> the place, as the closed proof carries it.
        rows: what stage 6 handed back -- `{"address", "change"}` per place
            it condensed, `change` being the paragraph as it will now read.

    Returns:
        `(address -> the compacted text, the problems)`, a problem being
        `(where, why)`. `where` is the row's own address wherever it has one
        and its position in the file where it has none, so a reader always
        has somewhere to look. All or nothing: one problem and the texts are
        empty, since a compaction that wrote the places it could would leave
        the proof holding some condensed paragraphs and some not, with
        nothing saying which.
    """
    texts: dict[str, str] = {}
    problems: list[tuple[str, str]] = []
    for i, row in enumerate(rows, 1):
        named = str(row.get("address") or "") if isinstance(row, dict) else ""
        where = named or f"compaction {i}"
        if not isinstance(row, dict) or not named:
            problems.append(
                (
                    where,
                    "a compaction is an object naming its `address` and its `change`",
                )
            )
            continue
        change = row.get("change")
        if not isinstance(change, str):
            problems.append(
                (where, "a compaction carries the condensed paragraph as `change`")
            )
            continue
        place = places.get(named)
        if place is None:
            problems.append((where, "this proof carries no place here"))
            continue
        if place.state not in SETTLED or place.text is None:
            problems.append((where, _why_not(place)))
            continue
        if not change and place.text:
            problems.append(
                (
                    where,
                    "the compacted text is empty and this place decided one --"
                    " compaction condenses, it does not delete",
                )
            )
            continue
        texts[named] = change
    return ({}, problems) if problems else (texts, [])


def _why_not(place: Place) -> str:
    """Why this place holds no decided text for a compaction to replace."""
    if place.state in SETTLED:
        return (
            f"{place.state} on the paragraph already there -- this place settled"
            " on no text, so there is nothing here to condense"
        )
    return (
        f"{place.state} -- this place has not settled on a text, so what a"
        " compaction would condense is not decided yet"
    )
