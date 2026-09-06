"""`flows/topology.py::compose`: a topology written from directives fits its binder.

The stdlib reads TOML and does not write it, so `compose` emits text and the
proof that the text is a topology is `read` accepting it and `fit` passing it.
"""

import pytest
from helpers import a_binder_over

from comment_review.desk.topology import read
from comment_review.flows.topology import compose, fit

FOUR = {f"{n}.py@a0": f"Doc for {n}." for n in "abcd"}


def test_a_composed_topology_reads_and_fits():
    binder = a_binder_over(FOUR)
    text = compose(
        [
            ("4a", [("ownership-context", 1)]),
            (
                "4c",
                [("block-context", 2), ("function-context", 1), ("module-context", 1)],
            ),
        ],
        binder,
    )
    stages, why = read(text)
    assert not why, why
    assert [s.name for s in stages] == ["4a", "4c"]
    assert stages[1].reads == "revise:4a"
    assert fit(stages, binder) == []


def test_a_split_role_gets_that_many_dispatches_dealing_the_pages_round_robin():
    text = compose([("4c", [("block-context", 2)])], a_binder_over(FOUR))
    stages, _ = read(text)
    paths = [d.paths for d in stages[0].dispatches]
    assert paths == [("a.py", "c.py"), ("b.py", "d.py")]


def test_an_unsplit_role_gets_one_dispatch_with_no_paths():
    text = compose([("4c", [("module-context", 1)])], a_binder_over(FOUR))
    stages, _ = read(text)
    assert [d.paths for d in stages[0].dispatches] == [()]


@pytest.mark.parametrize(
    "bad",
    [
        ("4c", [("no-such-role", 1)]),
        ("4c", [("block-context", 0)]),
        ("4c", [("block-context", 5)]),
    ],
)
def test_a_directive_the_binder_cannot_honour_is_refused(bad):
    with pytest.raises(ValueError):
        compose([bad], a_binder_over(FOUR))


def test_a_path_with_a_quote_in_it_is_still_valid_toml():
    binder = a_binder_over({'we"ird.py@a0': "x", "plain.py@a0": "y"})
    text = compose([("4c", [("block-context", 2)])], binder)
    stages, why = read(text)
    assert not why, why
    assert sorted(p for d in stages[0].dispatches for p in d.paths) == [
        "plain.py",
        'we"ird.py',
    ]
