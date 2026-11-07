"""`page_for` builds a page from every adversarial input the suite holds.

! THE PAGE REFUSES A READ WHOSE PARAGRAPHS SHARE AN ADDRESS (`held_twice`), so a
reader that mis-cuts a file fails the case below by name instead of the
compositor silently writing one paragraph and dropping the other. The inputs are
`helpers.FORMS` and `helpers.RUST_ITEMS`.
"""

import pytest
from conftest import build
from helpers import FORMS, RUST_ITEMS

CASES = {
    **{f"form-{k}": v for k, v in FORMS.items()},
    "rust-items": ("m.rs", RUST_ITEMS),
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
