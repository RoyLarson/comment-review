"""Sheets retain the reading supplied by their page or sheet."""

from copy import deepcopy
from dataclasses import replace

import pytest
from helpers import a_binder_over

from comment_review.desk.proof.edit_copy import EditCopy
from comment_review.desk.proof.mark import CleanMark
from comment_review.desk.proof.sheet import Sheet
from comment_review.desk.stages import Dispatch, Kind, Role, Stage
from comment_review.flows.distribute import assigned_binder, seed
from comment_review.flows.fan_out import fan
from comment_review.reading.context import ReadingContext
from comment_review.reading.context_io import context_to_wire


def mixed_binder():
    binder = a_binder_over({"a.py@b1": "# a\n", "b.py@b1": "# b\n"})
    return replace(
        binder,
        pages=tuple(
            replace(
                page, reading=replace(page.reading, settings=(("mode", page.path),))
            )
            for page in binder.pages
        ),
    )


def test_distribution_preserves_mixed_reading_on_disjoint_empty_sheets():
    binder = mixed_binder()
    stage = Stage(
        "sample",
        Kind.EDITORIAL,
        "original",
        (),
        tuple(Dispatch(Role.BLOCK_CONTEXT, (page.path,)) for page in binder.pages),
        series=("z",),
    )
    received = assigned_binder(binder, stage)
    assert [page.reading for page in received.pages] == [
        page.reading for page in binder.pages
    ]
    expected = {page.path: context_to_wire(page.reading) for page in binder.pages}
    copies = fan(binder, stage)
    assert len(copies) == 2
    for copy in copies:
        for sheet in copy["sheets"]:
            assert sheet["reading"] == expected[sheet["path"]]
            assert sheet["marks"] == []


def test_sheet_reading_exact_round_trip_and_detached_json():
    page = replace(
        mixed_binder().pages[0],
        reading=ReadingContext(
            "sample", "sample-reader", "a" * 64, (("mode", "wide"),)
        ),
    )
    marks = [
        CleanMark(
            address="sample.py@b1",
            anchor="",
            raw_text="",
            reason="",
            sources=({"cite": "sample.py:1", "verbatim": "example"},),
        ).serialize()
    ]
    wire = Sheet.seed(page.path, page.sha, marks, reading=page.reading)
    original = deepcopy(wire)
    assert wire["reading"] == {
        "format": 1,
        "language": "sample",
        "reader": "sample-reader",
        "compatibility": "a" * 64,
        "settings": {"mode": "wide"},
    }
    marks[0]["instruction"] = "drop"
    assert wire == original
    sheet, why = Sheet.deserialize("sample", wire)
    assert why == []
    assert sheet is not None
    assert sheet.reading == page.reading
    assert sheet.serialize() == original
    wire["marks"][0]["sources"][0]["verbatim"] = "changed source"
    outgoing_marks = sheet.serialize()
    outgoing_marks["marks"][0]["sources"][0]["verbatim"] = "changed output"
    assert sheet.serialize()["marks"] == original["marks"]
    wire["reading"]["settings"]["mode"] = "changed"
    outgoing = sheet.serialize()
    outgoing["reading"]["settings"]["mode"] = "also changed"
    assert sheet.reading == page.reading
    copy_wire = EditCopy.seed("sample", {"root": "."}, [original])
    original["reading"]["settings"]["mode"] = "changed again"
    assert copy_wire["sheets"][0]["reading"] == context_to_wire(page.reading)


@pytest.mark.parametrize(
    "reading",
    [
        None,
        [],
        {},
        {
            "format": 2,
            "language": "sample",
            "reader": "sample-reader",
            "compatibility": "a" * 64,
            "settings": {},
        },
    ],
)
def test_sheet_refuses_missing_malformed_future_reading(reading):
    wire = {"path": "sample.py", "sha": "same", "marks": []}
    if reading is not None:
        wire["reading"] = reading
    sheet, why = Sheet.deserialize("sample sheet", wire)
    assert sheet is None
    assert why and "sample sheet" in why[0] and "regather" in why[0]


def test_edit_copy_decode_does_not_consult_installed_compatibility():
    binder = mixed_binder()
    wire = seed(binder, "block-context")
    for sheet in wire["sheets"]:
        sheet["reading"]["compatibility"] = "f" * 64
    copy, why = EditCopy.deserialize("sample", wire)
    assert why == []
    assert copy is not None
    assert all(sheet.reading.compatibility == "f" * 64 for sheet in copy.sheets)
