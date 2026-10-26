from pathlib import Path

import pytest

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
