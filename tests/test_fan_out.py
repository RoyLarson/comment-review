"""`flows/fan_out.py`: a stage's dispatches split a binder into edit_copies.

! INPUT FROM REALITY, throughout -- a real binder over `DESK` through
`binder_of`, matching `tests/test_marks_flow.py`'s own pattern. Nothing here
hand-writes a page or a row.
"""

import os
from pathlib import Path

import pytest
from helpers import binder_of

from comment_review.desk.stages import Dispatch, Kind, Role, Stage
from comment_review.flows.fan_out import OverlappingShards, UncoveredPage, fan

# !! ABSOLUTE, matching `tests/test_marks_flow.py`'s own `DESK` -- a relative
# `Path("src/comment_review/desk")` only rglobs correctly when the suite runs
# from the repo root.
DESK = Path(__file__).resolve().parents[1] / "src" / "comment_review" / "desk"

#: The whole package, for the one case that needs a page path holding a real
#: `/` -- `DESK` alone is flat, so no pattern over it can demonstrate a glob
#: crossing a directory separator.
SRC = Path(__file__).resolve().parents[1] / "src" / "comment_review"


def test_every_page_reaches_exactly_one_shard_of_each_role():
    binder = binder_of(DESK, 0)
    names = sorted(page["path"] for page in binder["pages"])
    stage = Stage(
        "4c",
        Kind.EDITORIAL,
        "original",
        (),
        (
            Dispatch(Role.BLOCK_CONTEXT, (names[0],)),
            Dispatch(Role.BLOCK_CONTEXT, tuple(names[1:])),
            Dispatch(Role.MODULE_CONTEXT, ()),
        ),
    )
    copies = fan(binder, stage)

    block = [c for c in copies if c["role"] == "block-context"]
    seen = [s["path"] for c in block for s in c["sheets"]]
    assert sorted(seen) == names  # every page, once
    assert len(seen) == len(set(seen))  # no page twice

    whole = [c for c in copies if c["role"] == "module-context"][0]
    assert sorted(s["path"] for s in whole["sheets"]) == names


def test_a_page_in_two_shards_of_one_role_is_refused():
    binder = binder_of(DESK, 0)
    name = binder["pages"][0]["path"]
    stage = Stage(
        "4c",
        Kind.EDITORIAL,
        "original",
        (),
        (
            Dispatch(Role.BLOCK_CONTEXT, (name,)),
            Dispatch(Role.BLOCK_CONTEXT, (name,)),
        ),
    )
    with pytest.raises(OverlappingShards):
        fan(binder, stage)


def test_a_page_no_dispatch_of_a_role_covers_is_refused():
    # A different role's dispatch reaches every page in the binder -- one
    # earlier over `paths` is deliberately narrower, so `names[1:]` never
    # reaches a `block-context` shard at all.
    binder = binder_of(DESK, 0)
    names = sorted(page["path"] for page in binder["pages"])
    assert len(names) > 1, "DESK must hold more than one page for this case"
    stage = Stage(
        "4c",
        Kind.EDITORIAL,
        "original",
        (),
        (
            Dispatch(Role.BLOCK_CONTEXT, (names[0],)),
            Dispatch(Role.MODULE_CONTEXT, ()),
        ),
    )
    with pytest.raises(UncoveredPage):
        fan(binder, stage)


def test_two_different_roles_over_the_same_page_is_not_a_conflict():
    # Four roles reading one binder is the ordinary case -- no overlap guard
    # applies ACROSS roles, only within one role's own dispatches.
    binder = binder_of(DESK, 0)
    stage = Stage(
        "4c",
        Kind.EDITORIAL,
        "original",
        (),
        (
            Dispatch(Role.BLOCK_CONTEXT, ()),
            Dispatch(Role.FUNCTION_CONTEXT, ()),
        ),
    )
    copies = fan(binder, stage)
    assert [c["role"] for c in copies] == ["block-context", "function-context"]


def test_the_glob_matches_across_a_directory_separator():
    # `fnmatch`'s `*` is not path-aware -- documented on `fan_out.py` itself.
    # `DESK` alone is flat, so this uses the whole package, whose pages
    # include a real separator (`tests/helpers.py`'s `pages_of` stamps
    # `path.relative_to(root)` verbatim, so the separator is whatever the
    # platform writes -- `os.sep`, not assumed to be `/`).
    binder = binder_of(SRC, 0)
    names = sorted(page["path"] for page in binder["pages"])
    nested = [n for n in names if os.sep in n]
    assert nested, "SRC must hold at least one nested page for this case"
    stage = Stage(
        "4c",
        Kind.EDITORIAL,
        "original",
        (),
        (Dispatch(Role.BLOCK_CONTEXT, ("*.py",)),),
    )
    copies = fan(binder, stage)
    assert sorted(s["path"] for s in copies[0]["sheets"]) == names
