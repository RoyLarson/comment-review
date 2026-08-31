"""Text off disk as a JSON OBJECT, or the reason it is not one.

!! A LEAF, LIKE `constants` AND `exceptions`. It imports nothing from this
package, so a reader of one format may take it without acquiring the other's
subject -- which is the whole reason it is here rather than in either reader.
The binder's reader and `docket.read` are in different areas and neither may
import the other: a binder helper reaching into `docket/docket.py` was
measured on 2026-08-25 and had to be undone.

!! ITS TWO CALLERS NOW DIFFER, since 2026-08-31. `docket.read` still calls
this ITSELF, taking text; the binder's `deserialize` does not, because a
flow owns its load -- so the four binder COMMANDS call this and then
`Binder.deserialize`. `decision-log.md Process: #67`, and `P40`/`P41` are
where the docket follows.

!! IT EXISTS BECAUSE THE TWO READERS HELD ONE PREAMBLE TWICE. The parse and the
dict guard were byte-identical in both, differing only in the trailing noun,
and the comment on one of the copies said so -- *"This is the spelling
`binder.read` uses"*. `binder.py`'s own header names that failure: four
commands each deciding what a census file is, *"three spellings of one guess
and one absence"*, which is the reason that module owns the format at all.

! WHAT IS NOT SHARED IS EVERY CHECK PAST THE OBJECT. A binder must carry
`pages` as a list of pages; a docket must be non-empty and hold text or
null. Those are the formats, and they stay with their own readers.

! THE NAME IS DESCRIPTIVE AND PROVISIONAL, the way `machine` itself is: it says
what the function returns rather than naming a category this system has shown
it needs.
"""

import json


def object_of(text: str, noun: str) -> tuple[dict, str]:
    """This text as a JSON object, or `({}, reason)`.

    Args:
        text: the file's contents.
        noun: what the caller is reading, for the refusal -- `"binder"`,
            `"docket"`. It is written after "not a".

    Returns:
        `(the object, "")` when it reads, or `({}, reason)` when it does not.
    """
    try:
        loaded = json.loads(text)
    # ! ONE CLASS, NOT A TUPLE, so the shipped-code rule against a tuple literal
    # in an `except` does not bite.
    except json.JSONDecodeError as e:
        return {}, f"not JSON ({e})"
    if not isinstance(loaded, dict):
        return {}, f"a JSON {type(loaded).__name__}, not a {noun}"
    return loaded, ""
