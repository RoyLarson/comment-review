"""Readers that call `reading.matter` agree on the same matter-only input."""

from pathlib import Path

from comment_review.reading.diagnostics import ReadFailure
from comment_review.reading.lexer import LexicalRead
from comment_review.reading.readers import read_source
from comment_review.reading.series import Kind


def kinds(name: str, text: str) -> list[tuple[int, int, str]]:
    result = read_source(Path(name), text)
    assert isinstance(result, LexicalRead)
    found = result.paragraphs(Path(name))
    return [(p.start, p.end, p.kind) for p in found]


def test_kt_and_rs_hand_back_matter_on_the_same_runs_for_a_licence_then_an_import():
    # The code after the licence declares nothing in either language: where a
    # comment documents a declaration is each reader's own rule.
    kotlin = "// licence\n// more\n\nimport a.b\n\n// tail one\n\n// tail two\n"
    rust = "// licence\n// more\n\nuse a::b;\n\n// tail one\n\n// tail two\n"
    expected = [(1, 2, Kind.MATTER), (6, 6, Kind.COMMENT), (8, 8, Kind.MATTER)]
    assert kinds("m.kt", kotlin) == expected
    rust_read = read_source(Path("m.rs"), rust)
    assert not isinstance(rust_read, ReadFailure)
    found = rust_read.paragraphs(Path("m.rs"))
    assert not isinstance(found, ReadFailure)
    assert [(p.start, p.end, p.kind) for p in found] == expected
