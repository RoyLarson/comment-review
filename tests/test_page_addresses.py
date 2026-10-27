"""`page_for` builds a page from every adversarial input the suite holds.

! THE PAGE REFUSES A READ WHOSE PARAGRAPHS SHARE AN ADDRESS (`held_twice`), so a
reader that mis-cuts a file fails the case below by name instead of the
compositor silently writing one paragraph and dropping the other. The inputs are
the compositor's `FORMS`, the lexical reader's cases that pair a file name with
its text, the Rust items, and one sample per installed language built from that
language's own row.
"""

import pytest
from conftest import build
from reading import test_lexical
from test_compositor import FORMS
from test_page_for import RUST_ITEMS

from comment_review.reading.language import (
    INSTALLED_DEFINITIONS,
    language_from_definition,
)


def _named_and_texted(module) -> dict[str, tuple[str, str]]:
    """Every `(name, text)` a module's tests parametrize over, keyed by test and id."""
    found: dict[str, tuple[str, str]] = {}
    for fn_name, fn in vars(module).items():
        if not fn_name.startswith("test_"):
            continue
        for mark in getattr(fn, "pytestmark", []):
            if mark.name != "parametrize":
                continue
            argnames = mark.args[0]
            if not isinstance(argnames, (tuple, list)):
                argnames = [n.strip() for n in argnames.split(",")]
            if "name" not in argnames or "text" not in argnames:
                continue
            ids = mark.kwargs.get("ids")
            for n, values in enumerate(mark.args[1]):
                row = dict(zip(argnames, values, strict=False))
                label = ids[n] if ids else str(n)
                found[f"{fn_name}-{label}"] = (row["name"], row["text"])
    return found


def _sample_for(definition) -> tuple[str, str]:
    """A file in this language holding every shape its row can state."""
    language = language_from_definition(definition)
    name = f"m{language.extensions[0]}"
    code = f"{language.declares[0]} f" if language.declares else "x = 1"
    if language.line_comment:
        line = language.line_comment[0]
        lines = [f"{line} front", "", f"{line} note", code, f"{line} back"]
        lines += [f"{code} {line} beside"]
    else:
        opener, closer = language.block_comment[0]
        lines = [f"{opener} front {closer}", "", code, f"{opener} back {closer}"]
    for doc in language.doc_line[:1]:
        lines += [f"{doc} doc", code]
    return name, "\n".join(lines) + "\n"


CASES = {
    **{f"form-{k}": v for k, v in FORMS.items()},
    **{f"lexical-{k}": v for k, v in _named_and_texted(test_lexical).items()},
    "rust-items": ("m.rs", RUST_ITEMS),
    **{
        f"sample-{definition.language}": _sample_for(definition)
        for definition in INSTALLED_DEFINITIONS
        if not language_from_definition(definition).doc_inside
    },
}


@pytest.mark.parametrize(
    ("name", "text"),
    [pytest.param(n, t, id=k) for k, (n, t) in CASES.items()],
)
def test_no_input_holds_two_paragraphs_at_one_address(name, text):
    # `build` asserts the page is not a `ReadFailure`; the address check is
    # the other thing it would be refused for.
    page = build(text, name)
    held = [p.address for p in page.paragraphs if p.address]
    assert len(held) == len(set(held))
