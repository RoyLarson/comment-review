from pathlib import Path

import pytest

from comment_review import constants
from comment_review.reading.stripped import StrippedRead

BODY = "// Licence MIT\n\nfunction f() {}\n"


def _preserved(before: str, after: str, name: str):
    path = Path(name)
    return StrippedRead(before, path).preserved(StrippedRead(after, path))


def test_a_draft_holding_a_lone_cr_is_unprovable():
    before = "# x\ntouch PWNED\n"
    after = "# y\rtouch PWNED\n"

    assert _preserved(before, after, "m.sh").unprovable


def test_a_crlf_file_is_no_lone_cr():
    assert not constants.holds_lone_cr("a\r\nb\r\n")
    assert constants.holds_lone_cr("a\rb\n")


def test_a_comment_touching_a_continuation_is_unprovable():
    before = "#define A 1 \\\nint x;\n"

    assert _preserved(before, "#define A 1 \\// n\nint x;\n", "a.c").unprovable


def test_a_sql_file_holding_an_escaped_quote_is_unprovable():
    # standard SQL and MySQL end this literal in different places
    text = "SELECT 'it\\'s -- x';\n"

    assert _preserved(text, text.replace("-- x", "-- y"), "a.sql").unprovable


def test_a_shell_ansi_c_string_holding_an_escaped_quote_is_unprovable():
    # bash reads `\'` in `$'...'` as an escape, so the literal runs to the end
    text = "echo $'it\\'s # x'\n"

    assert _preserved(text, text.replace("# x", "# y"), "a.sh").unprovable


def test_a_sql_double_quote_holding_an_escaped_quote_is_unprovable():
    # MySQL reads `\"` in a double-quoted string as an escape
    text = 'SELECT "it\\"s -- x";\n'

    assert _preserved(text, text.replace("-- x", "-- y"), "a.sql").unprovable


@pytest.mark.parametrize(
    "name, text",
    [
        ("a.sh", 'echo "a\n# b\nc"\n'),
        ("a.rb", 'x = "a\n# b\nc"\n'),
        ("a.sql", "SELECT 'a\n-- b\nc';\n"),
        ("a.lua", 'x = "a\\\n-- b\nc"\n'),
        ("a.js", 'x = "a\\\n// b\nc";\n'),
    ],
)
def test_a_comment_inside_an_open_string_is_unprovable(name, text):
    assert _preserved(text, text, name).unprovable


def test_a_comment_trailing_a_line_that_leaves_a_string_open_is_unprovable():
    before = 'echo "a\nb # one\nc"\n'

    assert _preserved(before, before.replace("one", "two"), "a.sh").unprovable


@pytest.mark.parametrize(
    "text",
    [
        "const a = <p>\n  // text\n</p>;\n",
        "const a = <div\n  id='a'\n>\n  // text\n</div>;\n",
        "const a = <>\n  // text\n</>;\n",
        "const a = <p>\n  b // text\n</p>;\n",
        "const a = <p> // text\n</p>;\n",
        "const a = <p>\n  Hello<br/>\n  // text\n</p>;\n",
        "const a = <p>\n  see<b>x</b>\n  // text\n</p>;\n",
        "const a = <p>see<b>x</b>\n  // text\n</p>;\n",
        "const a = <p>\n  (x)<b>y</b>\n  // text\n</p>;\n",
        "const a = <\u00dcnicode>\n// text\n</\u00dcnicode>;\n",
    ],
)
def test_a_comment_inside_an_element_is_unprovable(text):
    assert _preserved(text, text, "a.jsx").unprovable


def test_a_lost_or_moved_mark_is_protected_source():
    text = "\ufeffx=1\n"
    for after in ("x=1\n", "\n\ufeffx=1\n"):
        result = _preserved(text, after, "a.sh")

        assert not result.unchanged
        assert [d.code for d in result.diagnostics] == ["protected-source-changed"]
