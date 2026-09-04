"""`commands/addresser.py`: the CLI's console face, exercised over a REAL binder.

`commands/` ran at 0.0% coverage -- 537 statements -- before this file: nothing
had ever watched `_resolve_one`, `_for_anchor` or `_check` run. Filed against
`TODO/addresser-answers-wrongly-at-exit-0.md`, which found all three answering
wrongly at exit 0 after the eleven-field row cut (`e56bea9`) removed `start`,
`end`, `kind` and `declares` -- fields these three still read.

Every row here comes from `bind()` over a page `page_for` actually built, never
a hand-written dict -- a fixture written in the shape the code expects can only
confirm.
"""

import io
from contextlib import redirect_stdout
from dataclasses import replace

from conftest import READ_FROM, SAMPLE, build, cue

from comment_review.binder.binder import bind
from comment_review.commands.addresser import _check, _for_anchor, _resolve_one
from comment_review.reading.addresser import DECLARED


def _rows():
    page = build(SAMPLE)
    return bind([page], read_from=READ_FROM).paragraphs


def test_resolve_prints_the_real_lines_not_none_none():
    """`_resolve_one` used to read `start`/`end`, fields no row carries since
    `e56bea9` -- printing `alpha.py:None-None` at exit 0 for every address."""
    rows = _rows()
    target = next(r for r in rows if r.anchor == "def f(x):" and cue(r) == "a1")
    address = target.address

    out = io.StringIO()
    with redirect_stdout(out):
        code = _resolve_one(address, rows)

    assert code == 0
    printed = out.getvalue()
    assert "None-None" not in printed
    assert f"{target.original_start}-{target.original_end}" in printed


def test_for_anchor_finds_the_a_place_a_declared_docstring_owns():
    """`for_anchor`'s `DECLARED` short-circuit read `b.get("declares")`, a field
    no row carries since `e56bea9` -- so it always returned `[]` and reported
    "no `a` place" for an anchor whose `a` row the census plainly holds."""
    rows = _rows()
    target = next(r for r in rows if r.anchor == "def f(x):" and cue(r) == "a1")

    out = io.StringIO()
    with redirect_stdout(out):
        code = _for_anchor("def f(x):", DECLARED, rows)

    assert code == 0
    printed = out.getvalue()
    assert "no `a` place" not in printed
    assert f"{target.original_start}-{target.original_end}" in printed


def test_check_reports_the_real_span_for_a_shared_address():
    """`_check`'s SHARED report read `paragraph.get('start')`/`.get('end')`,
    fields no row carries since `e56bea9` -- so a shared address always
    reported `None-None` regardless of where it actually sits.

    Two real rows made to share one address by duplicating a row `bind()`
    produced -- not a hand-written dict -- so the values checked are the ones a
    census would actually carry for a comment run and the interval it fills.
    """
    rows = _rows()
    target = next(r for r in rows if r.anchor == "def f(x):" and cue(r) == "a1")
    mine = [*rows, replace(target)]

    out = io.StringIO()
    with redirect_stdout(out):
        _check(mine)

    printed = out.getvalue()
    assert "SHARED" in printed
    assert "None-None" not in printed
    assert f"{target.original_start}-{target.original_end}" in printed
