"""Readers that call `reading.matter` agree on the same matter-only input."""

from conftest import kinds

from comment_review.reading.series import Kind


def test_kt_and_rs_hand_back_matter_on_the_same_runs_for_a_licence_then_an_import():
    # The code after the licence declares nothing in either language: where a
    # comment documents a declaration is each reader's own rule.
    kotlin = "// licence\n// more\n\nimport a.b\n\n// tail one\n\n// tail two\n"
    rust = "// licence\n// more\n\nuse a::b;\n\n// tail one\n\n// tail two\n"
    expected = [(1, 2, Kind.MATTER), (6, 6, Kind.COMMENT), (8, 8, Kind.MATTER)]
    assert kinds("m.kt", kotlin) == expected
    assert kinds("m.rs", rust) == expected
