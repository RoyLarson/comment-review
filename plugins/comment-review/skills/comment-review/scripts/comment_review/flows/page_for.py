"""The step that produces a PAGE, which nothing in the tree named until now.

! FIVE SITES ran the same four calls inline -- `read_source`, `language_for`,
`page_for`, carrying the sha -- and none of them was a named step:
`commands/census.py`, `commands/galley.py`, `results/compositor.py` twice
(`lossless` and `identity`), and `scripts/render_page.py:184`.
`flows/proof_setter.py` would have been the sixth. This is that step, for
`proof_setter._one`'s read only -- `_reread`, in the same file, still inlines
its own copy of the same four calls; see `page_of` for why the other five
sites are not repointed here.
"""

from pathlib import Path

from comment_review.binder.page import Page, page_for
from comment_review.machine import exceptions
from comment_review.machine.repo import read_source
from comment_review.reading.lexer import language_for


def page_of(path: Path, rel: str | None = None) -> tuple[Page | None, str]:
    """The page for one file, or the reason there is none.

    !! IT IS THE STEP THAT WAS MISSING. Roy, 2026-08-25: the tree had *"only a
    step that produces a binder"*, so anything wanting a PAGE either rebuilt one
    inline -- MEASURED at five sites -- or reached for the binder. Reaching for
    the binder is what pulled `rows_of` into `desk/notations.py` and had to be
    undone.

    ! A REFUSAL IS RETURNED, NOT RAISED, in the shape `binder.read` and
    `notations.read` already use: `(page, "")` or `(None, reason)`.

    ! REPOINTING THE OTHER FIVE SITES IS NOT THIS BRANCH'S -- it touches the
    census, the galley CLI, both compositor gates and `render_page.py`. Filed
    as `TODO/no-step-produces-a-page.md` rather than widened here.

    Args:
        path: the file to read.
        rel: how the repo names it. `page_for` stamps addresses from this, so a
            page built without one carries none.

    Returns:
        The page and an empty reason, or `None` and why there is no page.
    """
    try:
        source = read_source(path)
    except exceptions.READ_ERRORS as e:
        return None, f"could not be read ({e})"
    lang = language_for(path)
    if lang is None:
        return None, "no language record for its suffix"
    return page_for(path, source.text, lang, rel=rel, sha=source.sha), ""
