"""The step that produces a PAGE, which nothing in the tree named until now.

! FOUR SITES still run the same calls inline -- `read_source`, `language_for`,
`page_for`, carrying the sha -- and none of them is a named step. MEASURED
2026-08-26: `commands/census.py`, `results/compositor.py` twice (`lossless` and
`identity`), and `scripts/render_page.py`'s `render`. This is that step; both of
`flows/proof_setter.py`'s reads ask it, and see `page_of` for why the other
four sites are not repointed here.

! THE READ IS ITS OWN HALF, `source_of`, so a caller that must ask something of
the BYTES before paying for the parse can -- `proof_setter._one` compares the
binder's recorded sha that way. Splitting it is what keeps that comparison from
re-spelling the read and its error handling at the call site.
"""

from pathlib import Path

from comment_review.binder.page import Page, page_for
from comment_review.machine import exceptions
from comment_review.machine.repo import Source, read_source
from comment_review.reading.lexer import language_for


def source_of(path: Path) -> tuple[Source | None, str]:
    """The bytes and the sha for one file, or the reason there are none.

    ! IT IS `page_of`'s FIRST STEP, EXPOSED. A caller comparing a recorded sha
    wants the sha and not yet the page; without this it either reads the file a
    second time or spells `read_source` and `READ_ERRORS` out again, which is
    the inline-read shape this module exists to end.

    Args:
        path: the file to read.

    Returns:
        The source and an empty reason, or `None` and why it could not be read.
    """
    try:
        return read_source(path), ""
    except exceptions.READ_ERRORS as e:
        return None, f"could not be read ({e})"


def page_of(
    path: Path, rel: str | None = None, source: Source | None = None
) -> tuple[Page | None, str]:
    """The page for one file, or the reason there is none.

    !! IT IS THE STEP THAT WAS MISSING. Roy, 2026-08-25: the tree had *"only a
    step that produces a binder"*, so anything wanting a PAGE either rebuilt one
    inline -- MEASURED at five sites -- or reached for the binder. Reaching for
    the binder is what pulled `rows_of` into `docket/docket.py` and had to be
    undone.

    ! A REFUSAL IS RETURNED, NOT RAISED, in the shape `binder.read` and
    `docket.read` already use: `(page, "")` or `(None, reason)`.

    !! THAT COVERS `exceptions.Refused` TOO, and it did not until 2026-08-25.
    `page_for` raises it at `binder/page.py:521` and `:578` -- a `c` place whose
    anchor has no line, and a series with no branch -- and every one of the
    inline sites this consolidates handles it: `results/compositor.py` catches
    `Refused`, `commands/census.py` catches a bare `Exception`. Catching only
    `READ_ERRORS` here made this function narrower than the code it replaced, so
    such a file took `proof_setter.run` down with a traceback while this
    docstring promised a reason.

    ! A `Refused` IS A `ValueError`, so it is caught by name rather than by
    class ordering -- the tuple rule forbids an `except` holding a literal, and
    a bound name is what `exceptions` exists to supply.

    ! REPOINTING THE REMAINING FOUR SITES IS NOT THIS BRANCH'S -- it touches the
    census, both compositor gates and `render_page.py`. Filed as
    `TODO/no-step-produces-a-page.md` rather than widened here.

    Args:
        path: the file to read.
        rel: how the repo names it. `page_for` stamps addresses from this, so a
            page built without one carries none.
        source: the bytes already in hand, from `source_of`. Read here when a
            caller has none. ! It is not checked against `path`: a caller
            passing one file's bytes under another's name gets a page whose sha
            does not describe the file, which is what `source_of` exists to
            make unnecessary.

    Returns:
        The page and an empty reason, or `None` and why there is no page.
    """
    if source is None:
        source, why = source_of(path)
        if source is None:
            return None, why
    lang = language_for(path)
    if lang is None:
        return None, "no language record for its suffix"
    try:
        return page_for(path, source.text, lang, rel=rel, sha=source.sha), ""
    except exceptions.Refused as e:
        return None, f"has no page ({e})"
