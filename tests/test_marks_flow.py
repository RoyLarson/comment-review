"""`flows/marks.py`: the seeded row carries `raw_text`, and the sheet's shape.

! `test_a_sheet_carrying_a_code_concern_validates` is an EXPECTATION test, not
an INPUT one -- the sheet is a literal a human checked, per
`decision-log.md Vocabulary: #23`.
"""

from pathlib import Path

from helpers import binder_of

from comment_review.flows.marks import problems_in, seed


def test_a_seeded_row_carries_the_paragraph_bytes():
    # INPUT FROM REALITY: a real page of this repo through the real binder.
    # ! `binder_of` is the helper above; Task 7 makes `read_from` required and
    # this call already goes through it, so nothing here moves then.
    binder = binder_of(Path("src/comment_review/desk"), 0)
    sheet = seed(binder, "block-context")
    # ! `desk/` holds three files, each with its own `@a0` -- narrowed to
    # `mark.py`'s so the match is not the first file the walk happens to
    # visit.
    row = next(r for r in sheet["marks"] if r["address"].endswith("mark.py@a0"))
    source = Path("src/comment_review/desk/mark.py").read_text(encoding="utf-8")
    assert row["raw_text"] in source


def test_a_sheet_carrying_a_code_concern_validates():
    sheet = {
        "role": "block-context",
        # ! `read_from` IS PART OF A WELL-FORMED SHEET since 2026-08-28 --
        # `seed` puts it there and `problems_in` now rules on it, so a literal
        # that omits it is testing a sheet no role can return.
        "read_from": {"root": "src/comment_review/desk", "revise": 0},
        "marks": [],
        "code_concerns": [
            {"where": "src/m.py:12", "concern": "the guard admits a negative"}
        ],
    }
    assert problems_in(sheet) == ([], 0)
