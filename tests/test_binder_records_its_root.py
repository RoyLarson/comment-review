"""`binder.bind`: the root and revise it was censused from.

`the-flow-assumes-every-role-reads-at-once` T2 -- a sheet seeded from a binder
names the revise and the original in its header, and a binder built from the
original says so rather than leaving the field absent.
"""

from pathlib import Path

import pytest
from helpers import binder_of, pages_of

from comment_review.binder.binder import bind
from comment_review.flows.distribute import seed

# !! ABSOLUTE, AND IT WAS `Path("src/comment_review/desk")` UNTIL 2026-08-28.
# MEASURED: run from any directory but the repo root, `pages_of` rglobbed a
# directory that does not exist, returned `[]`, `bind([], ...)` succeeded, and
# the headline assertion reduced to checking that `bind` returned the dict it
# was handed -- 4 passed, having read no page at all. `tests/helpers.py` solves
# this one line away with the same `Path(__file__).resolve()` construction.
DESK = Path(__file__).resolve().parents[1] / "src" / "comment_review" / "desk"


def test_a_binder_built_from_the_original_says_so():
    # !! RULING, pre-flight: COMPARE `Path`s, NEVER PATH STRINGS. This repo is
    # developed on Windows, where `str(Path("a/b"))` is `a\b` -- a string literal
    # here is green on one machine and red on the other.
    binder = binder_of(DESK, 0)
    # ! THE PAGE COUNT IS ASSERTED FIRST, and that is what stops the whole
    # module passing over an empty read: every assertion below holds trivially
    # when nothing was censused.
    assert binder["pages"], "censused no page -- the rest of this test is vacuous"
    assert Path(binder["read_from"]["root"]) == DESK
    assert binder["read_from"]["revise"] == 0


def test_a_binder_that_cannot_say_which_root_it_read_is_refused():
    with pytest.raises(TypeError):
        bind(pages_of(DESK))


def test_the_binder_does_not_alias_the_caller_s_read_from():
    # ! The suite feeds one module-level `conftest.READ_FROM` into many binders,
    # so an aliased dict made every binder, every sheet seeded from one, and
    # that global a single object -- a test writing `["revise"] = 1` would have
    # changed what every later test in the session saw.
    mine = {"root": str(DESK), "revise": 0}
    binder = bind(pages_of(DESK), read_from=mine)
    binder["read_from"]["revise"] = 99
    assert mine["revise"] == 0
    assert seed(binder, "block-context")["read_from"]["revise"] == 99


def test_the_sheet_header_names_the_revise():
    sheet = seed(binder_of(DESK, 0), "block-context")
    assert sheet["read_from"]["revise"] == 0


def test_a_sheet_cannot_be_seeded_from_a_binder_that_names_no_root():
    # ! `bind` refuses this, so the binder here is built WITHOUT it -- the shape
    # an artifact read from disk or a hand-built dict can still take. `seed`
    # defaulted it to `{}` until 2026-08-28, which put the ambiguity back one
    # function downstream of the refusal that removes it.
    binder = binder_of(DESK, 0)
    del binder["read_from"]
    with pytest.raises(KeyError):
        seed(binder, "block-context")
