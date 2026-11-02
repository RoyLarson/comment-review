"""What the generic lexical reader hands the page: its paragraphs and code lines."""

from pathlib import Path

import pytest

from comment_review.reading.language import Language
from comment_review.reading.lexer import (
    LexicalRead,
)
from comment_review.reading.readers import read_source
from comment_review.reading.series import Kind


def read(name: str, text: str) -> LexicalRead:
    result = read_source(Path(name), text)
    assert isinstance(result, LexicalRead)
    return result


DOC = Kind.DOCSTRING
NOTE = Kind.COMMENT


ROYS_CASE = "// M1\n/** D1 */\n// C1\n/** D2 */\n// C2\n/** D3 */\n// C3\n"


@pytest.mark.parametrize(
    ("doc_line", "doc_block", "declares", "closing"),
    [
        (("///",), (), (), True),
        ((), ("/**",), (), True),
        ((), (), ("def",), False),
        ((), (), (), False),
    ],
    ids=["doc-line", "doc-block", "keywords-alone", "neither"],
)
def test_a_row_holds_a_closing_docstring_when_it_has_a_doc_marker(
    doc_line, doc_block, declares, closing
):
    row = Language(
        "x",
        (".x",),
        ("//",),
        doc_line=doc_line,
        doc_block=doc_block,
        declares=declares,
    )
    assert row.closing_docstring is closing


def _paragraphs(name: str, text: str):
    return read(name, text).paragraphs(Path(name))
