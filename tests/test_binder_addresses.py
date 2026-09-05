"""`binder/addresses.py`'s row readers, exercised over a REAL binder.

Filed against the xhigh wave-B review of `feat/the-write-chain-of-command`:
`unaddressed` still read a field the eleven-field row cut
(`e56bea9`) removed -- `start`/`end` and `anchor_line`. Every row here comes
from `bind()` over a page `page_for` actually built, never a hand-written dict,
matching `tests/test_addresser_command.py`'s own rule: a fixture written in the
shape the code expects can only confirm.
"""

from dataclasses import replace

from conftest import READ_FROM, SAMPLE, build, cue

from comment_review.binder.addresses import unaddressed
from comment_review.binder.binder import bind


def _rows():
    page = build(SAMPLE)
    return bind([page], read_from=READ_FROM).paragraphs


class TestUnaddressedReadsTheSurvivingFields:
    """`unaddressed` read `paragraph.get('start')`/`.get('end')`, fields no
    row has carried since `e56bea9` -- so its report named every entry's span
    as `None-None` regardless of where it actually sits."""

    def test_reports_the_real_span_not_none_none(self):
        rows = _rows()
        target = next(r for r in rows if cue(r) == "a1")
        # ! No row `bind()` produces is ever missing its address -- `unaddressed`
        # exists to catch a binder that reached this some OTHER way, e.g. hand
        # edited. Strip one row's address to reproduce that shape.
        stripped = replace(target, address="")
        mine = [r for r in rows if r is not target] + [stripped]

        out = unaddressed(mine)

        assert len(out) == 1
        assert "None-None" not in out[0]
        span = f"{target.original_start}-{target.original_end}"
        assert span in out[0]
