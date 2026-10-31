"""`comment_form`: the one derivation of a paragraph's prose, for every language.

Tested with raw lines handed to it; `Paragraph.text` calling it is tested on
`Paragraph`.
"""

from dataclasses import replace
from pathlib import Path

import pytest

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
    ("path", "marker"),
    [("m.py", "#"), ("m.rs", "//"), ("m.js", "//"), ("m.c", "/*")],
)
def test_a_byte_order_mark_before_the_first_marker_is_not_prose(path, marker):
    mark = chr(0xFEFF)
    raw = f"{mark}{marker} Licence MIT"
    assert comment_form(Path(path), Series.COVERS, raw).text == "Licence MIT"


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


@pytest.mark.parametrize(
    ("path", "raw", "text"),
    [
        ("m.c", "/* licence */ /* more */\n// note", "licence more note"),
        ("m.c", "/* a\n b */ /* c\n d */", "a b c d"),
        ("m.c", "/* a */ // b", "a b"),
        ("m.c", "/* a\n b */ // c", "a b c"),
        ("m.lua", "--[[ a ]]-- b", "a b"),
        ("m.lua", "--[[\n  Licence MIT\n]]--\n-- Module foo", "Licence MIT Module foo"),
    ],
    ids=[
        "two-blocks",
        "two-spanning-blocks",
        "block-then-line",
        "closer-then-line",
        "lua-long-then-line",
        "lua-empty-line-comment",
    ],
)
def test_each_comment_on_a_line_gives_its_own_text(path, raw, text):
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


@pytest.mark.parametrize(
    ("raw", "text"),
    [
        ('    ("doc")', "doc"),
        ('    ("doc")  # c', "doc"),
        ('    "doc"  # c', "doc"),
        ('    ("a"\n     "b")', "ab"),
        ('    ("a"\n     "b")  # c', "ab"),
        ('    (\n        "doc"\n    )', "doc"),
    ],
    ids=[
        "parenthesised",
        "parenthesised-comment",
        "bare-comment",
        "two-lines",
        "two-lines-comment",
        "own-lines",
    ],
)
def test_a_parenthesised_python_docstring_reads_as_its_literal(raw, text):
    assert comment_form(Path("m.py"), Series.DECLARED, raw).text == text


def test_a_docstrings_language_definition_is_not_part_of_its_value():
    form = comment_form(Path("m.py"), Series.DECLARED, '    """A. """ """B."""')
    assert isinstance(form, Docstring)
    other = INSTALLED_REGISTRY.for_path(Path("m.rs"))
    assert other is not None
    assert replace(form, definition=other) == form
    assert "definition" not in repr(form)
