"""`binder.bind`: the root and revise it was censused from.

`the-flow-assumes-every-role-reads-at-once` T2 -- a sheet seeded from a binder
names the revise and the original in its header, and a binder built from the
original says so rather than leaving the field absent.
"""

from pathlib import Path

import pytest
from helpers import binder_of, pages_of

from comment_review.binder.binder import Binder, bind
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
    assert binder.pages, "censused no page -- the rest of this test is vacuous"
    assert Path(binder.read_from["root"]) == DESK
    assert binder.read_from["revise"] == 0


def test_a_binder_that_cannot_say_which_root_it_read_is_refused():
    with pytest.raises(TypeError):
        # !! DELIBERATELY OMITS `read_from` -- proves the required parameter is
        # enforced at runtime. ty: ignore[missing-argument] because the call is
        # invalid ON PURPOSE; that is what this test asserts.
        bind(pages_of(DESK))  # ty: ignore[missing-argument]


def test_the_binder_does_not_alias_the_caller_s_read_from():
    # ! The suite feeds one module-level `conftest.READ_FROM` into many binders,
    # so an aliased dict made every binder, every sheet seeded from one, and
    # that global a single object -- a test writing `["revise"] = 1` would have
    # changed what every later test in the session saw.
    mine = {"root": str(DESK), "revise": 0}
    binder = bind(pages_of(DESK), read_from=mine)
    binder.read_from["revise"] = 99
    assert mine["revise"] == 0
    assert seed(binder, "block-context")["read_from"]["revise"] == 99


def test_the_sheet_header_names_the_revise():
    sheet = seed(binder_of(DESK, 0), "block-context")
    assert sheet["read_from"]["revise"] == 0


def test_a_binder_that_names_no_root_is_REFUSED_AT_THE_BOUNDARY():
    # !! THIS ASKED `seed` TO RAISE UNTIL 2026-08-31 -- `Process: #67`.
    # `bind` refused the shape, so the test built one WITHOUT it (the shape an
    # artifact read from disk could still take) and expected `seed`'s
    # `KeyError`. A `Binder` cannot hold that shape at all now: `deserialize`
    # refuses it by name, so `seed` is never handed one and its own refusal
    # became unreachable rather than being removed.
    #
    # ! THE REFUSAL IS THE SAME ONE, ONE STEP EARLIER, and it gained a message
    # a reader can act on -- `seed` raised an eight-frame traceback past
    # `main`'s own promise of "2 when an input could not be read".
    wire = binder_of(DESK, 0).serialize()
    del wire["read_from"]
    got, problems = Binder.deserialize("b.json", wire)
    assert got is None
    assert any("carries no `read_from`" in p for p in problems)
