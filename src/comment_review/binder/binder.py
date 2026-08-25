"""What a BINDER is on disk, and how one is read back.

A binder is the artifact the gatherer hands over -- a folder of pages, each
naming its file, with the rows an agent rules on. Roy, 2026-08-24: *"The
gatherer/census hands over the binder as in a 3-ring binder full of stuff."*

!! ONE MODULE OWNS BOTH DIRECTIONS, and the reason is what happened without it.
MEASURED 2026-08-24: the census wrote a bare list and FOUR commands each decided
for themselves what a census file is --

    addresser   loaded.get("paragraphs", []) if isinstance(loaded, dict) else loaded
    galley      census["paragraphs"] if isinstance(census, dict) else census
    record      loaded["paragraphs"] if isinstance(loaded, dict) else loaded
    verdicts    json.loads(census_text)          -- no envelope handling at all

Three spellings of one guess and one absence. They already disagreed: the first
tolerates a missing key, the next two raise `KeyError`, and the last would
iterate a dict's KEYS. ! All three guesses anticipated an envelope NOTHING
PRODUCED -- so the format lived in five places, none of which could be checked
against the others.

! THE FORMAT IS A CONTRACT AND BELONGS TO NEITHER END. That is the answer to the
locality question: scattering it across the consumers is what broke locality,
and one module both sides import is the fix rather than the compromise. Roy:
*"we should have a module that does the serialization/deserialization work not
just let each parse its own."*

!! IT IS NOT A METHOD ON `Page`, AND THAT IS DELIBERATE. `vars(b)` WAS the wire
format once -- the internals as protocol, unable to diverge without breaking
silently -- and a `.to_dict()` puts that decision back inside the object in a
politer form. What an agent sees is an EDITORIAL ruling (`decision-log.md
Addressing: #12`), not a fact about what a `Paragraph` is. ! And one page serves
two audiences that disagree: an agent gets seven fields and no fences, the
compositor needs everything including them.
"""

import hashlib
import json

from comment_review.binder.page import Page
from comment_review.reading.addresser import address_for
from comment_review.reading.lexer import Paragraph

# ! The shape's own version, so a reader can say WHICH format it refused rather
# than only that it could not read one.
VERSION = "1"


def page_row(paragraph: Paragraph) -> dict:
    """One paragraph as an agent receives it.

    !! SEVEN FIELDS, RULED ONE BY ONE -- `decision-log.md Addressing: #12`. The
    row carried nineteen until 2026-08-24; eleven went, and `path` moved to the
    page that holds the row rather than being repeated on every one of them.

    ! THE PROSE LEAVES AS ONE STRING. Roy: *"LLMs and the token parsers read
    this as a complete and coherent statement. They do not read this as the same
    thing: ['LLMs and the token', 'parsers read this as a', ...]."* The four
    reviewers ARE token parsers and prose is what they judge, so fragments make
    each role reassemble the sentence before it can ask whether it is true.
    """
    return {
        "cue": paragraph.address.split("@")[-1],
        # !! THE KIND STAYED, AND THE CUT'S REASON FOR DROPPING IT WAS HALF
        # TRUE. It read *"they are stating something that the cue letter
        # states"* -- and the letter states the SERIES, while the kind states
        # WHICH HALF OF THE PAIR: `b` is GAP, and `comment` against `interval`
        # is whether any prose is there. A letter cannot answer that.
        #
        # ! IT IS ONE OF A PAIR, WHICH IS WHY IT IS CHEAP TO SAY. `Series` gives
        # each letter its `present` and its `absent`, so a row carrying `b` and
        # `interval` is stating one bit the letter does not hold.
        "kind": paragraph.kind,
        "anchor": paragraph.anchor,
        "anchor_num": paragraph.anchor_num,
        "original_start": paragraph.original_start,
        "original_end": paragraph.original_end,
        "raw_text": "\n".join(paragraph.raw_lines),
    }


def sha_of(text: str) -> str:
    """The page's identity: a hash of the bytes it was read from.

    ! IT ANSWERS ONE QUESTION -- *did this file move under us* -- and it is the
    galley's, which is handed updates against a page it did not read. A hash of
    the SOURCE, so a page rebuilt from the same file answers the same.
    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def bind(pages: list[Page]) -> dict:
    """Every page in scope, as the binder that is handed over.

    ! THE FILE IS NAMED ONCE PER PAGE. It was on every row, which is the same
    string repeated as many times as the file has paragraphs -- 4,464 bytes of
    one path over 124 rows in a file measured 2026-08-24.

    ! A FENCE IS NOT CARRIED. Leading names no place and there is nothing to
    rule on; see `flows.census.carried`.
    """
    return {
        "version": VERSION,
        "pages": [
            {
                "path": page.path,
                "sha": sha_of(page.text),
                "rows": [page_row(b) for b in page.paragraphs if b.address],
            }
            for page in pages
        ],
    }


def read(text: str) -> tuple[dict, str]:
    """A binder read back, or the reason it could not be.

    !! IT REFUSES RATHER THAN COPING. Every one of the four readers this
    replaces guessed at the shape, and a guess that is wrong reads as an EMPTY
    binder -- which downstream is indistinguishable from a run with nothing to
    do. `verdicts.py` was measured certifying exactly that on 2026-08-20.

    Returns:
        `(binder, "")` when it reads, or `({}, reason)` when it does not.
    """
    try:
        loaded = json.loads(text)
    except json.JSONDecodeError as e:
        return {}, f"not JSON ({e})"
    if not isinstance(loaded, dict):
        return {}, f"a JSON {type(loaded).__name__}, not a binder"
    if "pages" not in loaded:
        return {}, "carries no `pages` -- is this the output of `census --json`?"
    return loaded, ""


def rows_of(binder: dict) -> list[dict]:
    """Every row in the binder, each stamped with the page that holds it.

    !! THE PATH AND THE ADDRESS ARE PUT BACK HERE, and that is what makes the
    envelope a change to the WIRE alone. The file is stored once per page
    because repeating it per row is the same string as many times as the file
    has paragraphs; every consumer still wants both per row, so the one module
    that knows the shape rejoins them rather than four callers each
    remembering to.

    ! `address_for` COMPOSES IT, not an f-string here. It is the only place the
    two halves are joined and it flattens the path itself -- the compositor was
    MEASURED disagreeing with itself on 2026-08-22 for re-deriving exactly this.
    """
    out = []
    for page in binder.get("pages", []):
        path = str(page.get("path", ""))
        for row in page.get("rows", []):
            cue = str(row.get("cue", ""))
            out.append(row | {"path": path, "address": address_for(path, cue)})
    return out
