"""The line endings a language row states, and what a reader does with them."""

from pathlib import Path

import pytest

from comment_review.reading.diagnostics import ReadFailure
from comment_review.reading.language import (
    LANGUAGES,
)
from comment_review.reading.readers import read_source
from comment_review.reading.stripped import code_fingerprint

LS, PS, NEL = " ", " ", "\x85"
STATED = [("m.js", LS), ("m.js", PS), ("m.ts", LS), ("m.ts", PS)]
STATED += [("m.cs", NEL), ("m.cs", LS), ("m.cs", PS)]


def test_each_row_states_what_its_grammar_defines() -> None:
    stated = {row.name: row.line_endings for row in LANGUAGES if row.line_endings}
    assert stated == {
        "javascript": (LS, PS),
        "typescript": (LS, PS),
        "csharp": (NEL, LS, PS),
    }


@pytest.mark.parametrize(("name", "ending"), STATED)
def test_the_comparison_cannot_prove_it(name, ending) -> None:
    text = f"// a{ending}evil();\n"
    assert code_fingerprint(text, Path(name)) == ("unprovable", "")


@pytest.mark.parametrize("name", ["m.py", "m.rs"])
def test_a_reader_with_its_own_scanner_is_unchanged(name) -> None:
    mark = "#" if name == "m.py" else "//"
    assert not isinstance(read_source(Path(name), f"{mark} a{LS}b\n"), ReadFailure)
