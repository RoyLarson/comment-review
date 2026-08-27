"""`binder/addresses.py`'s row readers, exercised over a REAL binder.

Filed against the xhigh wave-B review of `feat/the-write-chain-of-command`:
`unaddressed` and `for_anchor` each still read a field the eleven-field row cut
(`e56bea9`) removed -- `start`/`end` and `anchor_line`. Every row here comes
from `bind()` over a page `page_for` actually built, never a hand-written dict,
matching `tests/test_addresser_command.py`'s own rule: a fixture written in the
shape the code expects can only confirm.
"""

from conftest import SAMPLE, build

from comment_review.binder.addresses import for_anchor, unaddressed
from comment_review.binder.binder import bind, rows_of
from comment_review.reading.addresser import GAP, ON


def _rows(absent: bool = False):
    page = build(SAMPLE)
    return rows_of(bind([page], absent=absent))


class TestUnaddressedReadsTheSurvivingFields:
    """`unaddressed` read `paragraph.get('start')`/`.get('end')`, fields no
    row has carried since `e56bea9` -- so its report named every entry's span
    as `None-None` regardless of where it actually sits."""

    def test_reports_the_real_span_not_none_none(self):
        rows = _rows()
        target = next(r for r in rows if r["cue"] == "a1")
        # ! No row `bind()` produces is ever missing its address -- `unaddressed`
        # exists to catch a binder that reached this some OTHER way, e.g. hand
        # edited. Strip one row's address to reproduce that shape.
        stripped = dict(target) | {"address": ""}
        mine = [r for r in rows if r is not target] + [stripped]

        out = unaddressed(mine)

        assert len(out) == 1
        assert "None-None" not in out[0]
        span = f"{target['original_start']}-{target['original_end']}"
        assert span in out[0]


class TestForAnchorNoLongerFallsThroughADeadBranch:
    """The fallback below `direct` resolved by an `anchor_line` field no row
    has carried since `e56bea9`, so it was unreachable except for its `if not
    at` arm, which always fired and always returned `[]` -- reading as an
    answer for a place `cue()` never emits in the first place."""

    def test_module_has_no_b_place_and_says_so_plainly(self):
        rows = _rows(absent=True)
        assert for_anchor("<module>", GAP, rows) == []

    def test_module_has_no_c_place_and_says_so_plainly(self):
        rows = _rows(absent=True)
        assert for_anchor("<module>", ON, rows) == []

    def test_module_a_place_still_resolves_through_direct(self):
        # ! Not a fallback case -- `direct` (series_of(b) == series) already
        # answers this, before the deleted branch was ever reached. Kept here
        # to show the deletion left the real answer untouched.
        rows = _rows()
        found = for_anchor("<module>", "a", rows)
        assert [r["cue"] for r in found] == ["a0"]
