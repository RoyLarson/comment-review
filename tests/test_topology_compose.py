"""`flows/topology.py::compose`: a topology written from directives fits its binder.

The stdlib reads TOML and does not write it, so `compose` emits text and the
proof that the text is a topology is `read` accepting it and `fit` passing it.
"""

import json
from dataclasses import replace

import pytest
from conftest import run_command
from helpers import a_binder_over

from comment_review.binder.binder import bind
from comment_review.commands import topology as topology_command
from comment_review.desk.stages import Dispatch, Kind, Role, Stage
from comment_review.desk.topology import read
from comment_review.flows.fan_out import OverlappingShards, UncoveredPage, partition
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
    ("literal", "lookalike"),
    [
        ("app/[id]/page.tsx", "app/i/page.tsx"),
        ("app/[!id]/page.tsx", "app/x/page.tsx"),
        ("app/file?.tsx", "app/file1.tsx"),
        ("app/file*.tsx", "app/file-more.tsx"),
        ("app/[id]/page.rs", "app/i/page.rs"),
        ("app/[!id]/page.rs", "app/x/page.rs"),
        ("app/file?.rs", "app/file1.rs"),
        ("app/file*.py", "app/file-more.py"),
    ],
)
def test_composed_dispatches_select_literal_paths_without_claiming_lookalikes(
    literal, lookalike
):
    binder = a_binder_over({f"{literal}@b1": "one", f"{lookalike}@b1": "two"})
    text = compose([("4c", [("block-context", 2)])], binder)
    stages, why = read(text)
    assert not why, why
    assert fit(stages, binder) == []
    assert {
        tuple(page.path for page in pages)
        for _, pages, _ in partition(binder, stages[0])
    } == {
        (literal,),
        (lookalike,),
    }


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


def _freeform_only(tmp_path, *paths: str):
    """A saved binder that holds freeform paths and no page."""
    binder = bind([], read_from={"root": ".", "revise": 0}, freeform=paths)
    where = tmp_path / "binder.json"
    where.write_text(json.dumps(binder.serialize()), encoding="utf-8")
    return where


def _build(tmp_path, monkeypatch, capsys, where, stage: str):
    return run_command(
        monkeypatch,
        capsys,
        topology_command,
        "--build",
        "--binder",
        str(where),
        "--out",
        str(tmp_path / "t.toml"),
        "--stage",
        stage,
        with_stderr=True,
    )


def test_topology_builds_over_a_freeform_only_binder(tmp_path, monkeypatch, capsys):
    where = _freeform_only(tmp_path, "a.js", "b.js")
    code, printed = _build(
        tmp_path, monkeypatch, capsys, where, "4a=ownership-context/2"
    )
    assert code == 0, printed
    stages, why = read((tmp_path / "t.toml").read_text(encoding="utf-8"))
    assert not why, why
    assert [d.paths for d in stages[0].dispatches] == [("a.js",), ("b.js",)]


def test_a_binder_holding_nothing_says_why_no_topology_builds(
    tmp_path, monkeypatch, capsys
):
    where = _freeform_only(tmp_path)
    code, printed = _build(tmp_path, monkeypatch, capsys, where, "4a=ownership-context")
    assert code == 2, printed
    assert "over 0 files" in printed


def test_compose_sorts_page_and_freeform_paths_together():
    binder = replace(a_binder_over(FOUR), freeform=("a.js", "c.js"))
    stages, why = read(compose([("4c", [("block-context", 2)])], binder))
    assert not why, why
    assert fit(stages, binder) == []
    assert [d.paths for d in stages[0].dispatches] == [
        ("a.js", "b.py", "c.py"),
        ("a.py", "c.js", "d.py"),
    ]


def _stage(*dispatches: tuple[Role, tuple[str, ...]]) -> Stage:
    return Stage(
        "4c",
        Kind.EDITORIAL,
        dispatches=tuple(Dispatch(role, paths) for role, paths in dispatches),
    )


def test_partition_deals_a_freeform_path_to_one_shard_of_each_role():
    binder = replace(a_binder_over(FOUR), freeform=("x.js", "y.js"))
    stage = _stage(
        (Role.BLOCK_CONTEXT, ("x.js", "*.py")),
        (Role.BLOCK_CONTEXT, ("y.js",)),
        (Role.MODULE_CONTEXT, ()),
    )
    assert [
        ([page.path for page in pages], free)
        for _, pages, free in partition(binder, stage)
    ] == [
        (["a.py", "b.py", "c.py", "d.py"], ["x.js"]),
        ([], ["y.js"]),
        (["a.py", "b.py", "c.py", "d.py"], ["x.js", "y.js"]),
    ]


def test_a_freeform_path_no_dispatch_reaches_is_uncovered():
    binder = replace(a_binder_over(FOUR), freeform=("x.js",))
    with pytest.raises(UncoveredPage, match="x.js"):
        partition(binder, _stage((Role.BLOCK_CONTEXT, ("*.py",))))


def test_a_freeform_path_two_dispatches_of_one_role_reach_overlaps():
    binder = replace(a_binder_over(FOUR), freeform=("x.js",))
    stage = _stage(
        (Role.BLOCK_CONTEXT, ("*.py", "x.js")),
        (Role.BLOCK_CONTEXT, ("x.js",)),
    )
    with pytest.raises(OverlappingShards, match="x.js"):
        partition(binder, stage)
