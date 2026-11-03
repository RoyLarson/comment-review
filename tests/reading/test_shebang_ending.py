from pathlib import Path

import pytest

from comment_review.reading.readers import read_source

# name -> (interpreter line, that language's own code)
FILES = {
    "a.rs": ("#!/usr/bin/env rust-script", "fn f() {}\n"),
    "a.py": ("#!/usr/bin/env python3", "x = 1\n"),
}

BOM = chr(0xFEFF)


def _read(name: str, text: str):
    return read_source(Path(name), text)


@pytest.mark.parametrize("name", FILES)
def test_a_shebang_gaining_a_cr_is_not_proven(name):
    line, body = FILES[name]

    before = _read(name, line + "\n" + body)
    after = _read(name, line + "\r\n" + body)

    result = before.preserved(after)
    assert not result.unchanged
    assert [d.code for d in result.diagnostics] == ["protected-source-changed"]


@pytest.mark.parametrize("name", FILES)
def test_a_crlf_shebang_that_stays_proves(name):
    line, body = FILES[name]
    text = line + "\r\n" + body

    assert _read(name, text).preserved(_read(name, text)).unchanged


@pytest.mark.parametrize(
    ("name", "codes"),
    [
        ("a.rs", ["protected-source-changed"]),
        # Python proves: the line behind the mark is a comment to its reader.
        ("a.py", []),
    ],
)
def test_a_bom_prefixed_shebang_gaining_a_cr(name, codes):
    line, body = FILES[name]

    before = _read(name, BOM + line + "\n" + body)
    after = _read(name, BOM + line + "\r\n" + body)

    result = before.preserved(after)
    assert [d.code for d in result.diagnostics] == codes
    assert result.unchanged == (not codes)


@pytest.mark.parametrize("name", FILES)
def test_a_shebang_with_no_line_ending_proves_against_itself(name):
    text = FILES[name][0]

    assert _read(name, text).preserved(_read(name, text)).unchanged
