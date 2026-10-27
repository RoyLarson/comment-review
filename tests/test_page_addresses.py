"""`page_for` builds a page from every adversarial input the suite holds.

! THE PAGE REFUSES A READ WHOSE PARAGRAPHS SHARE AN ADDRESS (`held_twice`), so a
reader that mis-cuts a file fails the case below by name instead of the
compositor silently writing one paragraph and dropping the other. The inputs are
`helpers.FORMS`, `helpers.LEXICAL_INPUTS` (the lexical reader's own cases, read
by `reading/test_lexical.py`), `helpers.RUST_ITEMS`, and one sample per
installed language built from that language's own row.
"""

import pytest
from conftest import build
from helpers import FORMS, LEXICAL_INPUTS, RUST_ITEMS

from comment_review.reading.language import (
    INSTALLED_DEFINITIONS,
    language_from_definition,
)


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
    **{f"lexical-{k}": v for k, v in LEXICAL_INPUTS.items()},
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
