"""Building a binder for a test, in ONE place.

Fifteen sites across six files wrote a census fixture by hand, each spelling the
format itself. That is the same defect the shipped tree had until 2026-08-24 --
four commands each deciding what a census file is -- reproduced in the tests,
where it costs a day every time the format moves.

! IT WRAPS THE REAL WRITER WHERE IT CAN. `binder.bind` takes pages; a test that
has pages should use it directly. `as_binder` is for a test that has hand-made
ROWS and no page to build them from.
"""

import json

from comment_review.binder.binder import VERSION


def as_binder(rows, path="m.py", sha=""):
    """Hand-made rows, wrapped as the binder a command will read.

    Args:
        rows: the row dicts, already in whatever shape the test needs.
        path: the file the page names. One page unless a test needs more.
        sha: the page's identity. Blank is fine where nothing checks it --
            a test that cares supplies one.

    Returns:
        The binder, as a dict. `json.dumps` it, or use `write_binder`.
    """
    return {"version": VERSION, "pages": [{"path": path, "sha": sha, "rows": rows}]}


def row(cue, text="x", start=1, end=1, anchor="", anchor_num=0):
    """One row in the shape a binder carries TODAY.

    ! IT EXISTS SO A FIXTURE SAYS WHAT IT MEANS. Tests spelled rows out field by
    field, so the eleven fields cut on 2026-08-24 were written into fixtures at
    every site -- `address` where the row now carries a `cue`, `text` where it
    carries `raw_text`, `start`/`end` where it carries the `original_` pair.
    A fixture that names the field is a fixture that has to be found and edited
    the next time the shape moves.

    ! THE PATH IS NOT HERE. It belongs to the PAGE -- pass it to `as_binder`.
    """
    return {
        "cue": cue,
        "anchor": anchor,
        "anchor_num": anchor_num,
        "original_start": start,
        "original_end": end,
        "raw_text": text,
    }


def by_page(pages):
    """Several pages at once: `{path: rows}` in, one binder out."""
    return {
        "version": VERSION,
        "pages": [
            {"path": path, "sha": "", "rows": rows} for path, rows in pages.items()
        ],
    }


def write_binder(target, rows, path="m.py", **kwargs):
    """Write a one-page binder to `target`, and return the path."""
    target.write_text(
        json.dumps(as_binder(rows, path=path, **kwargs), default=list),
        encoding="utf-8",
    )
    return target
