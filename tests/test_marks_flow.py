"""`flows/marks.py`: the seeded row carries `raw_text`, and the sheet's shape.

! `test_a_sheet_carrying_a_code_concern_validates` is an EXPECTATION test, not
an INPUT one -- the sheet is a literal a human checked, per
`decision-log.md Vocabulary: #23`.
"""

from pathlib import Path

import pytest
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


@pytest.mark.parametrize(
    "bad", [{"junk": 1}, {"root": 7, "revise": "x"}, {}, "oops", None, []]
)
def test_a_sheet_whose_read_from_is_the_wrong_SHAPE_is_refused(bad):
    # !! `problems_in` HAND-ROLLED `isinstance(..., dict) and truthy` FOR ONE
    # COMMIT, so `{"junk": 1}` and `{"root": 7, "revise": "x"}` passed
    # `mark --check` at exit 0 while `bind` REFUSED the identical value -- two
    # spellings of one rule, disagreeing. It reuses `binder`'s checker now.
    sheet = {"role": "block-context", "read_from": bad, "marks": []}
    messages, _ = problems_in(sheet)
    assert any("read_from" in m for m in messages), bad


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
