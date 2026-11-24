import pytest

from comment_review.binder.page import Page
from comment_review.flows import on_the_page as flow
from comment_review.machine.repo import Source
from comment_review.reading.context import Imprint
from comment_review.reading.diagnostics import ReadFailure


@pytest.fixture
def saved_context():
    from pathlib import Path

    from comment_review.flows import reading_context as metadata

    context = metadata.context_for(Path("m.py"))
    assert not isinstance(context, ReadFailure)
    return context


def _clean_here(address: str) -> dict:
    """A `clean` citing its own tmp page's first line, which every page here
    opens with -- the helpers' cite names a file this tmp tree does not hold."""
    from helpers import a_clean

    path = address.partition("@")[0]
    return {**a_clean(address), "sources": [{"cite": f"{path}:1", "verbatim": "x = 0"}]}


def test_a_held_page_keeps_the_reading_it_was_first_read_under(
    tmp_path, monkeypatch, saved_context
):
    from conftest import install_another_reader

    path = tmp_path / "m.py"
    path.write_bytes(b"# note\r\nx = 1\r\n")
    cache = {}
    imprints = {"m.py": Imprint("", saved_context)}
    _, page = flow.page_named("m.py", ["m.py"], tmp_path, cache, imprints=imprints)
    assert isinstance(page, Page)
    assert page.reading == saved_context
    assert cache["m.py"].source.text == "# note\r\nx = 1\r\n"
    with monkeypatch.context() as patch:
        install_another_reader(patch)
        assert flow.page_named("m.py", [], tmp_path, cache)[1] is page


@pytest.mark.parametrize("route", ["admit", "docket"])
def test_saved_context_reaches_shared_read_routes(
    tmp_path, monkeypatch, saved_context, route
):
    from helpers import returned

    from comment_review.desk.proof.sheet import Sheet
    from comment_review.flows import reading_context, transcribe, verify

    (tmp_path / "m.py").write_text(
        "x = 0\n# one\n# two\n# three\nx = 1\n", encoding="utf-8"
    )
    wire = {
        "role": "block-context",
        "read_from": {"root": str(tmp_path)},
        "sheets": [
            Sheet.seed("m.py", "", [_clean_here("m.py@b1")], reading=saved_context)
        ],
    }
    copy = returned(wire)
    imprints, why = reading_context.admit_pages(("copy", copy.sheets))
    assert why == []
    calls = []
    actual = flow.page_of

    def read(*args, **kwargs):
        calls.append(kwargs["reading_context"])
        return actual(*args, **kwargs)

    monkeypatch.setattr(flow, "page_of", read)
    if route == "admit":
        admission = verify.admit([copy], tmp_path)
        assert admission.imprints == imprints
        assert admission.problems == []
    else:
        assert transcribe.docket_of(copy, tmp_path).schedules == ()
    assert calls == [saved_context]


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
        flow.held_at("m.py@b1", ["m.py"], tmp_path, {}, imprints={}), ReadFailure
    )


def test_fill_move_reads_destination_under_saved_context(
    tmp_path, monkeypatch, saved_context
):
    from comment_review.binder.binder import bind
    from comment_review.flows.distribute import seed
    from comment_review.flows.fill import fill

    path = tmp_path / "m.py"
    path.write_text("x = 0\n# one\n# two\n# three\nx = 1\ny = 2\n", encoding="utf-8")
    page = flow.page_of(path, rel="m.py", reading_context=saved_context)
    assert isinstance(page, Page)
    copy = seed(bind([page], read_from={"root": str(tmp_path)}), "block-context")
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
    assert calls == [saved_context]


def test_disjoint_saved_paths_supply_destination_context(
    tmp_path, monkeypatch, saved_context
):
    from helpers import a_move, returned

    from comment_review.desk.proof.sheet import Sheet
    from comment_review.flows.verify import admit

    for name in ("m.py", "n.py"):
        (tmp_path / name).write_text(
            "x = 0\n# one\n# two\n# three\nx = 1\n", encoding="utf-8"
        )
    copy = returned(
        {
            "role": "block-context",
            "read_from": {"root": str(tmp_path)},
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
                    reading=saved_context,
                )
            ],
        }
    )
    admission = admit([copy], tmp_path)
    problems = [*admission.unadmitted, *admission.problems]
    assert not any("reading context" in problem.message for problem in problems)
    held = admission.pages["n.py"].result
    assert isinstance(held, Page) and held.reading == saved_context


def test_disjoint_shard_move_uses_full_stage_contexts(
    tmp_path, monkeypatch, saved_context
):
    from dataclasses import replace

    from helpers import a_move, returned

    from comment_review.binder.binder import bind
    from comment_review.flows.bus import CopiesReturned, handle
    from comment_review.flows.distribute import seed

    pages = []
    for name in ("m.py", "n.py"):
        path = tmp_path / name
        path.write_text("x = 0\n# one\n# two\n# three\nx = 1\n", encoding="utf-8")
        page = flow.page_of(path, rel=name, reading_context=saved_context)
        assert isinstance(page, Page)
        pages.append(page)
    binder = bind(pages, read_from={"root": str(tmp_path)})
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
                    mark.update(_clean_here(mark["address"]))
        copies.append(returned(wire))
    seen = {}
    actual = flow.page_of

    def read(path, **kwargs):
        seen[kwargs["rel"]] = kwargs["reading_context"]
        return actual(path, **kwargs)

    monkeypatch.setattr(flow, "page_of", read)
    out, result = handle(CopiesReturned("4c", copies, binder, tmp_path, binders=shards))
    assert result is not None, out
    assert seen["n.py"] == saved_context


@pytest.mark.parametrize("known", [False, True])
@pytest.mark.parametrize("saved", [False, True])
def test_resolution_context_admission_precedes_acquisition(
    tmp_path, monkeypatch, saved_context, known, saved
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
        {"m.py": Imprint("", saved_context)} if saved else {},
    )
    if known and not saved:
        assert "saved reading context is missing" in why
        assert calls == []
        assert cache == {}
    else:
        assert why == ""
        assert calls == [path]
        if saved:
            held = cache["m.py"].result
            assert isinstance(held, Page) and held.reading == saved_context
