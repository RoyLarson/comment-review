import pytest

from comment_review.binder.page import Page
from comment_review.flows import on_the_page as flow
from comment_review.machine.repo import Source
from comment_review.reading.diagnostics import ReadFailure


@pytest.fixture
def selectable_context(monkeypatch):
    from dataclasses import replace
    from pathlib import Path

    from comment_review.flows import reading_context as metadata

    installed = metadata.reader_for(Path("m.py"))
    assert installed is not None and not isinstance(installed, ReadFailure)
    definition, binding = installed
    selected = replace(
        definition, defaults={"mode": ""}, choices={"mode": ("", "wide")}
    )
    monkeypatch.setattr(metadata, "reader_for", lambda _: (selected, binding))
    return metadata.context_for(Path("m.py"), {"mode": "wide"})


def test_same_path_two_settings_retains_first_valid_read(tmp_path, selectable_context):
    path = tmp_path / "m.py"
    path.write_bytes(b"# note\r\nx = 1\r\n")
    cache = {}
    _, page = flow.page_named(
        "m.py", [], tmp_path, cache, reading_context=selectable_context
    )
    assert isinstance(page, Page)
    assert page.reading == selectable_context
    assert cache["m.py"].source.text == "# note\r\nx = 1\r\n"
    _, failure = flow.page_named("m.py", [], tmp_path, cache, settings={"mode": ""})
    assert isinstance(failure, ReadFailure)
    assert failure.diagnostics[0].code == "held-context-mismatch"
    assert flow.page_named("m.py", [], tmp_path, cache)[1] is page


@pytest.mark.parametrize(
    "route", ["fill", "check", "texts", "resolution", "copy", "docket"]
)
def test_saved_nondefault_context_reaches_shared_read_routes(
    tmp_path, monkeypatch, selectable_context, route
):
    from helpers import a_clean, returned

    from comment_review.commands import check
    from comment_review.desk.proof.sheet import Sheet
    from comment_review.flows import fill, transcribe, verify

    (tmp_path / "m.py").write_text(
        "x = 0\n# one\n# two\n# three\nx = 1\n", encoding="utf-8"
    )
    wire = {
        "role": "block-context",
        "read_from": {"root": str(tmp_path), "revise": 0},
        "sheets": [
            Sheet.seed("m.py", "", [a_clean("m.py@b1")], reading=selectable_context)
        ],
    }
    copy = returned(wire)
    calls = []
    actual = flow.page_of

    def read(*args, **kwargs):
        calls.append(kwargs["reading_context"])
        return actual(*args, **kwargs)

    monkeypatch.setattr(flow, "page_of", read)
    if route == "fill":
        assert fill.page_text_at([wire], "m.py@b1", tmp_path) == "# one\n# two\n# three"
    elif route == "check":
        assert check._row_problems(copy, ["m.py"], tmp_path, {}) == []
    elif route == "texts":
        assert verify.texts_at(copy, ["m.py"], tmp_path, {}) == {
            "m.py@b1": ("# one\n# two\n# three",)
        }
    elif route == "resolution":
        assert verify.resolution_problems(copy, ["m.py"], tmp_path, {}) == []
    elif route == "copy":
        assert verify.copy_problems(copy, ["m.py"], tmp_path, {}, {}) == []
    else:
        assert transcribe.docket_of(copy, tmp_path).schedules == ()
    assert calls == [selectable_context]


def test_supplied_source_must_match_first_snapshot(tmp_path):
    cache = {}
    first = Source("# note\nx = 1\n", "first")
    _, page = flow.page_named("m.py", ["m.py"], tmp_path, cache, source=first)
    assert isinstance(page, Page)
    _, same = flow.page_named("m.py", ["m.py"], tmp_path, cache, source=first)
    assert same is page
    _, refused = flow.page_named(
        "m.py", ["m.py"], tmp_path, cache, source=Source("x = 2\n", "second")
    )
    assert isinstance(refused, ReadFailure)
    assert flow.page_named("m.py", ["m.py"], tmp_path, cache)[1] is page


@pytest.mark.parametrize("text", [None, '""" unclosed\n'])
def test_one_acquisition_and_cached_failure(tmp_path, monkeypatch, text):
    if text is not None:
        (tmp_path / "missing.py").write_text(text, encoding="utf-8")
    calls = []
    real = flow.source_of

    def acquire(path):
        calls.append(path)
        return real(path)

    monkeypatch.setattr(flow, "source_of", acquire)
    cache = {}
    _, failure = flow.page_named("missing.py", [], tmp_path, cache)
    assert isinstance(failure, ReadFailure)
    assert flow.page_named("missing.py", [], tmp_path, cache)[1] is failure
    assert calls == [tmp_path / "missing.py"]


def test_valid_page_retains_original_disk_snapshot(tmp_path, monkeypatch):
    path = tmp_path / "m.py"
    path.write_bytes(b"x = 1\r\n")
    calls = []
    real = flow.source_of

    def acquire(path):
        calls.append(path)
        return real(path)

    monkeypatch.setattr(flow, "source_of", acquire)
    cache = {}
    _, page = flow.page_named("m.py", [], tmp_path, cache)
    assert isinstance(page, Page)
    path.write_bytes(b"x = 2\n")
    assert flow.page_named("m.py", [], tmp_path, cache)[1] is page
    assert cache["m.py"].source.text == "x = 1\r\n"
    assert calls == [path]


def test_known_saved_path_cannot_default_missing_context(tmp_path):
    (tmp_path / "m.py").write_text("x = 1\n", encoding="utf-8")
    assert isinstance(
        flow.held_at("m.py@b1", ["m.py"], tmp_path, {}, contexts={}), ReadFailure
    )


def test_fill_move_reads_destination_under_saved_context(
    tmp_path, monkeypatch, selectable_context
):
    from comment_review.binder.binder import bind
    from comment_review.flows.distribute import seed
    from comment_review.flows.fill import fill

    path = tmp_path / "m.py"
    path.write_text("x = 0\n# one\n# two\n# three\nx = 1\ny = 2\n", encoding="utf-8")
    page = flow.page_of(path, rel="m.py", reading_context=selectable_context)
    assert isinstance(page, Page)
    copy = seed(
        bind([page], read_from={"root": str(tmp_path), "revise": 0}), "block-context"
    )
    calls = []
    actual = flow.page_of

    def read(*args, **kwargs):
        calls.append(kwargs["reading_context"])
        return actual(*args, **kwargs)

    monkeypatch.setattr(flow, "page_of", read)
    placed, why = fill(
        copy,
        {
            "address": "m.py@b1",
            "instruction": "move",
            "claim": {"from": "m.py@b1", "to": "m.py@b2"},
            "change": "# two",
            "raw_text": "# two",
            "reason": "belongs beside the next statement",
            "sources": [{"cite": "m.py:5"}],
        },
        tmp_path,
    )
    assert why == [] and placed is not None
    assert calls == [selectable_context]


def test_disjoint_saved_paths_supply_destination_context(
    tmp_path, monkeypatch, selectable_context
):
    from helpers import a_move, returned

    from comment_review.desk.proof.sheet import Sheet
    from comment_review.flows.verify import copy_problems

    for name in ("m.py", "n.py"):
        (tmp_path / name).write_text(
            "x = 0\n# one\n# two\n# three\nx = 1\n", encoding="utf-8"
        )
    copy = returned(
        {
            "role": "block-context",
            "read_from": {"root": str(tmp_path), "revise": 0},
            "sheets": [
                Sheet.seed(
                    "m.py",
                    "",
                    [
                        a_move(
                            "m.py@b1",
                            "n.py@b1",
                            "# two",
                            "# one\n# two\n# three\n# two",
                        )
                    ],
                    reading=selectable_context,
                )
            ],
        }
    )
    cache = {}
    problems = copy_problems(
        copy,
        ["m.py", "n.py"],
        tmp_path,
        {},
        cache,
        contexts={"m.py": selectable_context, "n.py": selectable_context},
    )
    assert not any("reading context" in problem.message for problem in problems)
    assert cache["n.py"].context == selectable_context


def test_disjoint_shard_move_uses_full_stage_settings(
    tmp_path, monkeypatch, selectable_context
):
    from dataclasses import replace

    from helpers import a_clean, a_move, returned

    from comment_review.binder.binder import bind
    from comment_review.flows.bus import CopiesReturned, handle
    from comment_review.flows.distribute import seed

    pages = []
    for name in ("m.py", "n.py"):
        path = tmp_path / name
        path.write_text("x = 0\n# one\n# two\n# three\nx = 1\n", encoding="utf-8")
        page = flow.page_of(path, rel=name, reading_context=selectable_context)
        assert isinstance(page, Page)
        pages.append(page)
    binder = bind(pages, read_from={"root": str(tmp_path), "revise": 0})
    shards = tuple(replace(binder, pages=(page,)) for page in binder.pages)
    copies = []
    for shard in shards:
        wire = seed(shard, "block-context")
        for sheet in wire["sheets"]:
            for mark in sheet["marks"]:
                if mark["address"] == "m.py@b1":
                    mark.update(
                        a_move(
                            "m.py@b1",
                            "n.py@b1",
                            "# two",
                            "# one\n# two\n# three\n# two",
                        )
                    )
                    mark["sources"] = [{"cite": "m.py:5", "verbatim": "x = 1"}]
                else:
                    mark.update(a_clean(mark["address"]))
        copies.append(returned(wire))
    seen = {}
    actual = flow.page_of

    def read(path, **kwargs):
        seen[kwargs["rel"]] = kwargs["reading_context"]
        return actual(path, **kwargs)

    monkeypatch.setattr(flow, "page_of", read)
    out, result = handle(CopiesReturned("4c", copies, binder, tmp_path, binders=shards))
    assert result is not None, out
    assert seen["n.py"] == selectable_context


def test_context_merge_conflict_refuses_before_source(
    tmp_path, monkeypatch, selectable_context
):
    from pathlib import Path

    from helpers import a_clean, returned

    from comment_review.desk.proof.sheet import Sheet
    from comment_review.flows.reading_context import context_for
    from comment_review.flows.verify import copy_problems

    copy = returned(
        {
            "role": "block-context",
            "read_from": {"root": str(tmp_path), "revise": 0},
            "sheets": [
                Sheet.seed("m.py", "", [a_clean("m.py@b1")], reading=selectable_context)
            ],
        }
    )

    def forbidden(path):
        pytest.fail("conflicting saved contexts acquired source")

    monkeypatch.setattr(flow, "source_of", forbidden)
    current = context_for(Path("m.py"), {})
    assert not isinstance(current, ReadFailure)
    problems = copy_problems(
        copy, ["m.py"], tmp_path, {}, {}, contexts={"m.py": current}
    )
    assert problems and all(problem.role == "block-context" for problem in problems)
    assert "conflicting reading contexts" in problems[0].message


@pytest.mark.parametrize("known", [False, True])
@pytest.mark.parametrize("saved", [False, True])
def test_resolution_context_admission_precedes_acquisition(
    tmp_path, monkeypatch, selectable_context, known, saved
):
    from comment_review.flows.verify import _unresolved

    path = tmp_path / "m.py"
    path.write_text("x = 1\n", encoding="utf-8")
    calls = []
    acquire = flow.source_of

    def read(path):
        calls.append(path)
        return acquire(path)

    monkeypatch.setattr(flow, "source_of", read)
    cache = {}
    why = _unresolved(
        "m.py@b1",
        ["m.py"] if known else [],
        tmp_path,
        cache,
        {"m.py": selectable_context} if saved else {},
    )
    if known and not saved:
        assert "saved reading context is missing" in why
        assert calls == []
        assert cache == {}
    else:
        assert why == ""
        assert calls == [path]
        if saved:
            assert cache["m.py"].context == selectable_context


def test_incompatible_context_refused_before_cached_address(tmp_path):
    from dataclasses import replace

    cache = {}
    _, page = flow.page_named(
        "m.py", [], tmp_path, cache, source=Source("# note\nx = 1\n", "first")
    )
    assert isinstance(page, Page)
    result = flow.held_at(
        "m.py@b1",
        [],
        tmp_path,
        cache,
        reading_context=replace(page.reading, compatibility="0" * 64),
    )
    assert isinstance(result, ReadFailure)
