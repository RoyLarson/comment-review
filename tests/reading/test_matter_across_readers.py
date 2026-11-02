"""Readers that call `reading.matter` agree on the same matter-only input."""

import pytest
from conftest import kinds

from comment_review.reading.series import Kind


@pytest.mark.parametrize(
    ("name", "text"),
    [
        ("m.rs", "// licence\n// more\n\nuse a::b;\n\n// tail one\n\n// tail two\n"),
        ("m.py", "# licence\n# more\n\nimport a.b\n\n# tail one\n\n# tail two\n"),
    ],
    ids=["rs", "py"],
)
def test_readers_hand_back_matter_on_the_same_runs_for_a_licence_then_an_import(
    name, text
):
    # The code after the licence declares nothing in any of them: where a
    # comment documents a declaration is each reader's own rule.
    expected = [(1, 2, Kind.MATTER), (6, 6, Kind.COMMENT), (8, 8, Kind.MATTER)]
    assert kinds(name, text) == expected
