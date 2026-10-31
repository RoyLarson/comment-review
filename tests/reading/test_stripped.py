from pathlib import Path

import pytest

from comment_review import constants
from comment_review.reading.stripped import StrippedRead

BODY = "// Licence MIT\n\nfunction f() {}\n"


def _preserved(before: str, after: str, name: str):
    path = Path(name)
    return StrippedRead(before, path).preserved(StrippedRead(after, path))


@pytest.mark.parametrize("name", ["m.js", "m.ts"])
@pytest.mark.parametrize(
    ("before", "after"),
    [
        ("#!/usr/bin/env node\n" + BODY, BODY),
        ("#!/usr/bin/env node\n" + BODY, "#!/usr/bin/env deno\n" + BODY),
        (BODY, "#!/usr/bin/env node\n" + BODY),
    ],
)
def test_an_interpreter_line_change_is_protected_source(name, before, after):
    result = _preserved(before, after, name)

    assert not result.unchanged
    assert [d.code for d in result.diagnostics] == ["protected-source-changed"]


@pytest.mark.parametrize("name", ["m.js", "m.ts"])
@pytest.mark.parametrize("space", ["  ", "\t"])
def test_a_file_whose_prose_lines_end_in_whitespace_is_provable(name, space):
    text = f"#!/usr/bin/env node{space}\n// note{space}\nlet x = 1; // why{space}\n"

    result = _preserved(text, text, name)

    assert result.unchanged
    assert result.diagnostics == ()


@pytest.mark.parametrize(
    ("name", "header"),
    [
        ("m.js", "/* Licence MIT */\n"),
        ("m.js", "/** Module doc. */\n"),
        ("m.java", "/*\n * Licence\n */\n"),
        ("m.cs", "/* Licence */\n"),
    ],
)
def test_a_byte_order_mark_before_a_block_comment_does_not_make_the_file_unprovable(
    name, header
):
    text = chr(0xFEFF) + header + "x = 1\n"

    assert _preserved(text, text, name).unchanged
    changed = _preserved(text, text.replace("x = 1", "x = 2"), name)
    assert [d.code for d in changed.diagnostics] == ["code-changed"]


@pytest.mark.parametrize(
    ("name", "line"),
    [
        ("m.c", "    /* a */ /* b */"),
        ("m.c", "/* a */ // b"),
        ("m.c", "/* a\n b */ /* c\n d */"),
    ],
    ids=["two-blocks", "block-then-line", "closer-then-open-block"],
)
def test_a_line_of_comments_after_a_closer_is_provable(name, line):
    code = ("int x;", "int y;")
    text = f"{code[0]}\n{line}\n{code[1]}\n"

    assert _preserved(text, text, name).unchanged
    changed = _preserved(text, text.replace(code[1], code[1] + " "), name)
    assert changed.unchanged
    changed = _preserved(text, text.replace(code[1], code[0]), name)
    assert [d.code for d in changed.diagnostics] == ["code-changed"]


@pytest.mark.parametrize("name", ["m.js", "m.ts"])
def test_an_interpreter_line_with_trailing_space_still_protects_it(name):
    before = "#!/usr/bin/env node  \nlet x = 1;\n"

    result = _preserved(before, before.replace("node", "deno"), name)

    assert [d.code for d in result.diagnostics] == ["protected-source-changed"]


@pytest.mark.parametrize("name", ["m.js", "m.ts"])
def test_the_matter_below_an_interpreter_line_may_change(name):
    before = "#!/usr/bin/env node\n" + BODY

    result = _preserved(before, before.replace("MIT", "Apache-2.0"), name)

    assert result.unchanged


def test_a_shebang_gaining_a_cr_is_protected_source():
    before = "#!/bin/sh\necho a\n"

    result = _preserved(before, before.replace("sh\n", "sh\r\n"), "a.sh")

    assert not result.unchanged
    assert [d.code for d in result.diagnostics] == ["protected-source-changed"]


def test_a_crlf_shebang_that_stays_proves():
    before = "#!/bin/sh\r\necho a\r\n"

    assert _preserved(before, before, "a.sh").unchanged


def test_a_crlf_shebang_with_changed_code_is_code_changed():
    before = "#!/bin/sh\r\necho a\r\n"

    result = _preserved(before, before.replace("a", "b"), "a.sh")

    assert [d.code for d in result.diagnostics] == ["code-changed"]


def test_a_draft_holding_a_lone_cr_is_unprovable():
    before = "# x\ntouch PWNED\n"
    after = "# y\rtouch PWNED\n"

    assert _preserved(before, after, "m.sh").unprovable


def test_a_crlf_file_is_no_lone_cr():
    assert not constants.holds_lone_cr("a\r\nb\r\n")
    assert constants.holds_lone_cr("a\rb\n")


@pytest.mark.parametrize(
    ("before", "after"),
    [
        ("echo a \\\n  b\n", "echo a \\  # n\n  b\n"),
        ("echo a \\  # n\n  b\n", "echo a \\\n  b\n"),
        ("echo a \\\n  b\n", "echo a \\\n# n\n  b\n"),
        ("echo a \\\n# n\n  b\n", "echo a \\\n  b\n"),
        ("echo a \\\n\n  b\n", "echo a \\\n  b\n"),
    ],
)
def test_an_edit_at_a_continuation_is_changed_code(before, after):
    result = _preserved(before, after, "a.sh")

    assert [d.code for d in result.diagnostics] == ["code-changed"]


def test_rewording_a_comment_past_a_broken_continuation_proves():
    before = "echo a \\  # one\n  b\n"

    assert _preserved(before, before.replace("one", "two"), "a.sh").unchanged


def test_two_backslashes_do_not_continue():
    before = "echo a\\\\\n# one\n"

    assert _preserved(before, before.replace("one", "two"), "a.sh").unchanged


def test_a_row_with_no_continuation_reads_its_comment_as_prose():
    before = "x = a \\\n-- one\n"

    assert _preserved(before, before.replace("one", "two"), "a.lua").unchanged
