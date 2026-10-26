"""`Paragraph.text`: one derivation, `reading.lexer.comment_form`, for every language.

The derivation is tested on `comment_form` with raw lines handed to it; the page
is tested for calling it, on a fresh page and on a place read back off the wire.
"""

from dataclasses import replace
from pathlib import Path

import pytest

from comment_review.binder import page as page_mod
from comment_review.binder.page import Page, page_for
from comment_review.flows.reading_context import context_for
from comment_review.reading.diagnostics import ReadFailure
from comment_review.reading.docstring import Docstring
from comment_review.reading.language import INSTALLED_REGISTRY
from comment_review.reading.lexer import comment_form
from comment_review.reading.series import Series

PROSE = ("One wrapped claim that", "runs onto a second line.")


@pytest.mark.parametrize(
    ("path", "marker"),
    [("m.py", "#"), ("m.rs", "//"), ("m.go", "//")],
)
def test_one_comment_run_reads_as_one_text_in_every_language(path, marker):
    raw = "\n".join(f"    {marker} {line}" for line in PROSE)
    form = comment_form(Path(path), Series.GAP, raw)
    assert form.text == " ".join(PROSE)


@pytest.mark.parametrize(
    ("path", "raw", "text"),
    [
        ("m.c", "/* abi_only */", "abi_only"),
        (
            "m.c",
            "/** One wrapped claim that\n * runs on. */",
            "One wrapped claim that runs on.",
        ),
        (
            "m.rs",
            "/*\n * One wrapped claim\n * runs on.\n */",
            "One wrapped claim runs on.",
        ),
        ("m.rs", "/** Doc\n * more\n */", "Doc more"),
    ],
)
def test_block_comment_markers_are_not_prose(path, raw, text):
    assert comment_form(Path(path), Series.GAP, raw).text == text


def test_a_rust_shebang_is_its_own_fragment_and_the_comment_keeps_no_marker():
    form = comment_form(Path("m.rs"), Series.COVERS, "#!/usr/bin/env rust\n// Licence")
    assert [part.text for part in form.fragments] == ["#!/usr/bin/env rust", "Licence"]


def test_python_docstring_escapes_keep_their_source_spelling():
    raw = '    """Takes \\\\*args."""'
    assert comment_form(Path("m.py"), Series.DECLARED, raw).text == "Takes \\\\*args."


@pytest.mark.parametrize(
    ("raw", "text"),
    [
        ('    """Doc.""" \\', "Doc."),
        ('    """Doc.\n    more""" \\\n', "Doc. more"),
        ('    """Doc. """ """More.""" \\', "Doc. More."),
    ],
    ids=["one-line", "two-lines", "concatenated"],
)
def test_a_python_docstring_ending_in_a_continuation_has_no_quotes_in_its_text(
    raw, text
):
    assert comment_form(Path("m.py"), Series.DECLARED, raw).text == text


def test_a_docstrings_language_definition_is_not_part_of_its_value():
    form = comment_form(Path("m.py"), Series.DECLARED, '    """A. """ """B."""')
    assert isinstance(form, Docstring)
    other = INSTALLED_REGISTRY.for_path(Path("m.rs"))
    assert other is not None
    assert replace(form, definition=other) == form
    assert "definition" not in repr(form)


def _page(name: str, text: str) -> Page:
    path = Path(name)
    context = context_for(path, {})
    assert not isinstance(context, ReadFailure)
    page = page_for(path, text, sha="held", reading=context)
    assert isinstance(page, Page)
    return page


SOURCES = {
    "m.c": (
        "/* File matter. */\n\n"
        "int x = 1; /* abi_only */\n"
        "/** Doc for f. */\n"
        "int f(void);\n"
    ),
    "m.rs": "//! Module doc.\n\n/// Adds one.\nfn f() {} // trailing\n",
    "m.py": '"""Module doc."""\n\n# A comment\nx = 1  # trailing\n',
}


TEXTS = {
    "m.c": {"f0": "File matter.", "c0": "abi_only", "b1": "Doc for f."},
    "m.rs": {"a0": "Module doc.", "a1": "Adds one.", "c0": "trailing"},
    "m.py": {"a0": "Module doc.", "b0": "A comment", "c0": "trailing"},
}


@pytest.mark.parametrize("name", sorted(SOURCES))
def test_the_page_fills_text_from_comment_form(name):
    page = _page(name, SOURCES[name])
    assert {
        b.address.rsplit("@", 1)[-1]: b.text
        for b in page.paragraphs
        if "".join(b.raw_lines).strip()
    } == TEXTS[name]


def test_a_c_block_comment_on_the_page_has_no_markers():
    page = _page("m.c", SOURCES["m.c"])
    texts = {b.text for b in page.paragraphs if b.text}
    assert "abi_only" in texts
    assert not any("/*" in t or "*/" in t for t in texts)


@pytest.mark.parametrize("name", sorted(SOURCES))
def test_a_place_read_back_has_the_text_of_the_fresh_paragraph(name):
    page = _page(name, SOURCES[name])
    for b in page.paragraphs:
        if "@" not in b.address:
            continue
        back = page_mod._paragraph(page_mod._place(b), page.path)
        assert back.text == b.text, b.address
