"""What a `Paragraph` derives from the raw lines a reader hands it."""

from pathlib import Path

import pytest

from comment_review.reading import lexer
from comment_review.reading.lexer import comment_form
from comment_review.reading.paragraph import MARKERS, Paragraph
from comment_review.reading.series import Series


def paragraph(*raw_lines: str) -> Paragraph:
    return Paragraph("m.py", 1, len(raw_lines), "comment", raw_lines=[*raw_lines])


def test_every_prose_line_counts():
    assert paragraph("# one", "# two", "# three").lines == 3


def test_a_blank_line_inside_the_run_is_free():
    assert paragraph("# one", "", "# two").lines == 2


@pytest.mark.parametrize("marker", MARKERS)
def test_a_work_marker_line_is_free(marker):
    assert paragraph("# one", f"# {marker}: filed", "# two").lines == 2


def test_a_marker_continuation_line_counts():
    assert paragraph("# TODO: filed", "#   and its reason").lines == 1


def test_a_word_that_only_starts_like_a_marker_counts():
    assert paragraph("# TODOS are filed", "# BUGGY input").lines == 2


def test_an_empty_place_counts_nothing():
    assert paragraph().lines == 0
    assert paragraph("").lines == 0


@pytest.mark.parametrize(
    ("path", "address", "anchor", "raw_lines", "text"),
    [
        (
            "m.rs",
            "m.rs@a1",
            "fn f() {}",
            ["/// Adds one.", "/// Twice."],
            "Adds one. Twice.",
        ),
        ("m.c", "m.c@c0", "int x = 1;", [" /* abi_only */"], "abi_only"),
        ("m.py", "m.py@a0", "<module>", ['"""Module doc."""'], "Module doc."),
        (
            "m.py",
            "m.py@b0",
            "x = 1",
            ["# A comment", "# runs on."],
            "A comment runs on.",
        ),
    ],
)
def test_text_is_comment_forms_text_of_the_raw_lines(
    path, address, anchor, raw_lines, text
):
    one = Paragraph(
        path, 1, 1, "comment", anchor=anchor, address=address, raw_lines=raw_lines
    )
    raw = "\n".join(raw_lines)
    cue = address.rsplit("@", 1)[-1]
    assert one.text == comment_form(Path(path), Series.of(cue), raw, anchor).text
    assert one.text == text


def test_a_paragraph_holding_no_prose_has_no_text():
    assert paragraph().text == ""
    assert paragraph("", "  ").text == ""


def test_text_is_derived_when_read_and_again_only_when_its_inputs_change(
    monkeypatch,
):
    calls = []
    real = lexer.comment_form

    def counting(*args):
        calls.append(args)
        return real(*args)

    monkeypatch.setattr(lexer, "comment_form", counting)
    one = paragraph("# one")
    assert calls == []
    assert (one.text, one.text) == ("one", "one")
    assert len(calls) == 1
    one.raw_lines = ["# two"]
    assert one.text == "two"
    assert len(calls) == 2
