"""The line endings a language row states, and what a reader does with them."""

from dataclasses import replace
from pathlib import Path

import pytest

from comment_review.reading.diagnostics import ReadFailure
from comment_review.reading.language import (
    INSTALLED_REGISTRY,
    LANGUAGES,
    validate_language_definition,
)
from comment_review.reading.lexer import language_for, read_lexical
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


@pytest.mark.parametrize("invalid", [("\n",), ("\r",), ("ab",), ("",), (1,)])
def test_a_row_states_only_single_characters_beyond_lf_and_cr(invalid) -> None:
    value = INSTALLED_REGISTRY.for_language("javascript")
    assert value is not None
    changed = replace(value, rules={**value.rules, "line_endings": invalid})
    failure = validate_language_definition("javascript", changed)
    assert failure is not None
    assert "line_endings" in failure.diagnostics[0].message


@pytest.mark.parametrize(("name", "ending"), STATED)
def test_a_comment_holding_a_stated_ending_is_marked(name, ending) -> None:
    path = Path(name)
    language = language_for(path)
    assert language is not None
    found = read_lexical(path, f"// a{ending}evil();\n", language).found
    assert "line-ending-in-comment" in found[0].annotations


@pytest.mark.parametrize(("name", "ending"), STATED)
def test_the_read_refuses_it_naming_the_character_and_line(name, ending) -> None:
    result = read_source(Path(name), f"let x;\n// a{ending}evil();\n")
    assert isinstance(result, ReadFailure)
    diagnostic = result.diagnostics[0]
    assert diagnostic.code == "line-ending-in-comment"
    assert f"U+{ord(ending):04X}" in diagnostic.message
    assert "line 2" in diagnostic.message


@pytest.mark.parametrize(("name", "ending"), STATED)
def test_the_comparison_cannot_prove_it(name, ending) -> None:
    text = f"// a{ending}evil();\n"
    assert code_fingerprint(text, Path(name)) == ("unprovable", "")


@pytest.mark.parametrize("name", ["m.go", "m.java", "m.c", "m.rb", "m.lua"])
def test_a_row_stating_none_reads_it_as_comment_text(name) -> None:
    mark = {"m.rb": "#", "m.lua": "--"}.get(name, "//")
    assert not isinstance(read_source(Path(name), f"{mark} a{LS}b\n"), ReadFailure)


@pytest.mark.parametrize("ending", [LS, PS])
def test_inside_a_string_literal_it_is_not_a_comment(ending) -> None:
    text = f'let s = "a{ending}b";\n'
    assert not isinstance(read_source(Path("m.js"), text), ReadFailure)
    assert code_fingerprint(text, Path("m.js"))[0] == "stripped"


@pytest.mark.parametrize("name", ["m.py", "m.rs"])
def test_a_reader_with_its_own_scanner_is_unchanged(name) -> None:
    mark = "#" if name == "m.py" else "//"
    assert not isinstance(read_source(Path(name), f"{mark} a{LS}b\n"), ReadFailure)
