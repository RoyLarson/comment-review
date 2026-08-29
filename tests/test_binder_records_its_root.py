"""`binder.bind`: the root and revise it was censused from.

`the-flow-assumes-every-role-reads-at-once` T2 -- a sheet seeded from a binder
names the revise and the original in its header, and a binder built from the
original says so rather than leaving the field absent.
"""

from pathlib import Path

import pytest
from helpers import binder_of, pages_of

from comment_review.binder.binder import bind
from comment_review.flows.marks import seed


def test_a_binder_built_from_the_original_says_so():
    # !! RULING, pre-flight: COMPARE `Path`s, NEVER PATH STRINGS. This repo is
    # developed on Windows, where `str(Path("a/b"))` is `a\b` -- a string literal
    # here is green on one machine and red on the other.
    root = Path("src/comment_review/desk")
    binder = binder_of(root, 0)
    assert Path(binder["read_from"]["root"]) == root
    assert binder["read_from"]["revise"] == 0


def test_a_binder_that_cannot_say_which_root_it_read_is_refused():
    with pytest.raises(TypeError):
        bind(pages_of(Path("src/comment_review/desk")))


def test_the_sheet_header_names_the_revise():
    sheet = seed(binder_of(Path("src/comment_review/desk"), 0), "block-context")
    assert sheet["read_from"]["revise"] == 0


def test_a_sheet_cannot_be_seeded_from_a_binder_that_names_no_root():
    # ! `bind` refuses this, so the binder here is built WITHOUT it -- the shape
    # an artifact read from disk or a hand-built dict can still take. `seed`
    # defaulted it to `{}` until 2026-08-28, which put the ambiguity back one
    # function downstream of the refusal that removes it.
    binder = binder_of(Path("src/comment_review/desk"), 0)
    del binder["read_from"]
    with pytest.raises(KeyError):
        seed(binder, "block-context")
