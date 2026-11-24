from inspect import Parameter, signature
from pathlib import Path

import pytest
from conftest import READ_FROM, build

from comment_review.binder.binder import Binder, bind
from comment_review.binder.page import Page, RedactedPage, page_for
from comment_review.flows import page_for as page_flow
from comment_review.flows.distribute import assigned_binder
from comment_review.machine.repo import Source
from comment_review.reading.context import ReadingContext


@pytest.mark.parametrize("text", ["", "x = 1\n", "# note\nx = 1\n"])
@pytest.mark.parametrize("absent", [False, True])
def test_binding_and_decoding_retain_context(text, absent):
    page = build(text)
    binder = bind([page], read_from=READ_FROM, absent=absent)
    assert binder.pages[0].reading is page.reading
    wire = binder.serialize()
    assert wire["version"] == "4"
    assert wire["pages"][0]["reading"] == {
        "format": 1,
        "language": page.reading.language,
        "reader": page.reading.reader,
    }
    decoded, why = Binder.deserialize("fixture", wire)
    assert why == []
    assert decoded is not None
    assert decoded.pages[0].reading == page.reading
    wire["pages"][0]["reading"]["reader"] = "changed"
    assert decoded.pages[0].reading == page.reading
    assert binder.pages[0].reading == page.reading


def test_version_two_requires_regather():
    wire = bind([build("")], read_from=READ_FROM).serialize()
    wire["version"] = "2"
    decoded, why = Binder.deserialize("fixture", wire)
    assert decoded is None
    assert "regather" in " ".join(why)


@pytest.mark.parametrize("reading", [None, {}, {"format": 99}])
def test_invalid_saved_context_refuses(reading):
    wire = bind([build("")], read_from=READ_FROM).serialize()
    wire["pages"][0]["reading"] = reading
    decoded, why = Binder.deserialize("fixture", wire)
    assert decoded is None
    assert "regather" in " ".join(why)


def test_context_is_required_on_all_page_constructors():
    for constructor in (Page, RedactedPage, page_for):
        parameter = signature(constructor).parameters["reading"]
        assert parameter.default is Parameter.empty
    assert signature(page_for).parameters["reading"].kind is Parameter.KEYWORD_ONLY


def test_fresh_flow_retains_admitted_context_and_held_source(monkeypatch):
    from comment_review.flows import reading_context

    context = reading_context.context_for(Path("missing.py"))
    assert isinstance(context, ReadingContext)
    received = []

    def selected(path, **kwargs):
        received.append(path)
        return context

    def unexpected_acquisition(path):
        pytest.fail("held source was reacquired")

    monkeypatch.setattr(page_flow, "context_for", selected)
    monkeypatch.setattr(page_flow, "source_of", unexpected_acquisition)
    page = page_flow.page_of(
        Path("missing.py"),
        source=Source("", "supplied"),
        reading_context=context,
    )
    assert isinstance(page, Page)
    assert page.reading is context
    assert page.sha == "supplied"
    # A supplied reading is the caller's, derived or admitted; it is not derived again.
    assert received == []
    assigned = assigned_binder(bind([page], read_from=READ_FROM))
    assert assigned.pages[0].reading is context


def test_decoded_rows_are_detached_from_wire():
    wire = bind([build("# note\nx = 1\n")], read_from=READ_FROM).serialize()
    decoded, why = Binder.deserialize("fixture", wire)
    assert decoded is not None, why
    before = decoded.paragraphs[0].raw_text
    wire["pages"][0]["rows"][0]["raw_text"] = "changed"
    assert decoded.paragraphs[0].raw_text == before


def test_literal_version_four_wire_needs_no_installed_language():
    wire = {
        "version": "4",
        "read_from": {"root": "fixture"},
        "freeform": [],
        "pages": [
            {
                "path": "saved.unknown",
                "sha": "supplied",
                "rows": [],
                "reading": {
                    "format": 1,
                    "language": "uninstalled",
                    "reader": "saved-reader",
                },
            }
        ],
    }
    decoded, why = Binder.deserialize("literal", wire)
    assert decoded is not None, why
    assert decoded.pages[0].reading == ReadingContext("uninstalled", "saved-reader")
    assert decoded.serialize() == wire
