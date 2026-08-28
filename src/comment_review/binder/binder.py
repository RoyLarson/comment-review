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
    collator    json.loads(census_text)          -- no envelope handling at all

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
two audiences that disagree: an agent gets SIX fields, no fences and no empty
places, while the compositor needs every one of them or the file cannot be set
back.
"""

from comment_review.binder.page import Page
from comment_review.machine.json_object import object_of
from comment_review.reading.addresser import address_for
from comment_review.reading.lexer import Paragraph
from comment_review.reading.series import Kind

# ! The shape's own version, so a reader can say WHICH format it refused rather
# than only that it could not read one.
VERSION = "1"


def page_row(paragraph: Paragraph) -> dict:
    """One paragraph as an agent receives it.

    !! FIVE FIELDS, RULED ONE BY ONE -- `decision-log.md Addressing: #12`. The
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
        # !! `kind` IS GONE AGAIN, AND THE ORIGINAL RULING WAS RIGHT. It read
        # *"they are stating something that the cue letter states"*; I put it
        # back on 2026-08-25 arguing the letter gives the SERIES while the kind
        # gives which half of the pair. Both are true, and the second stopped
        # mattering the moment ABSENT PLACES STOPPED BEING SENT: every row a
        # reviewer receives holds prose, so its kind is its series' `present`
        # and the letter states it after all.
        #
        # ! MEASURED before the cut, over 14,139 rows: `kind` equalled
        # `derive(cue, raw_text)` in 14,136 of them. The three exceptions are
        # `go`, `ruby` and `lua`, where the kind DISAGREES with the cue -- a
        # defect, filed, and not information.
        "anchor": paragraph.anchor,
        # !! `anchor_num` LEFT ON 2026-08-25, and it is the one cut made on the
        # expectation that it MIGHT come back. Roy: *"lets drop it and add it
        # back if it actually becomes necessary. That is safe now."* It was kept
        # in 2026-08-21 because the galley and compositor were thought to need
        # an order the cues could not be trusted to carry -- and the chain ruled
        # since (`Process: #14`) has the write path RELOAD the page from disk,
        # so it takes the anchor order from the page and never from a row.
        #
        # ! MEASURED before removing it: NOTHING read it from a row. `page`
        # stamps it and `addresser` computes it, both on the page side.
        "original_start": paragraph.original_start,
        "original_end": paragraph.original_end,
        "raw_text": "\n".join(paragraph.raw_lines),
    }


def bind(pages: list[Page], absent: bool = False) -> dict:
    """Every page in scope, as the binder that is handed over.

    ! THE SHA IS REPORTED, NOT TAKEN. It arrives on the page from
    `repo.read_source`; this module hashes nothing. Roy, 2026-08-25: *"It is
    information received by page and binder, not something requested by
    page/binder."*

    !! AN ABSENT PLACE IS NOT SENT UNLESS IT IS ASKED FOR. Roy, 2026-08-25:
    *"The absent kinds are not supposed to be sent to the agents unless
    specifically asked for."* MEASURED over this repo's own source before the
    cut: **5,201 of 5,685 rows -- 91% -- held no prose.** 2,692 `margin` and
    2,437 `interval`, which is roughly one empty place per line of code, against
    2 `undocumented` in the whole tree. 850KB, and four roles read it.

    !! AND AN EMPTY PLACE IS STILL ADDRESSED, WHICH IS WHAT MAKES THIS SAFE. The
    walk emits every place, filled or not, so a reviewer that wants to `add`
    ASKS for the one it means:

        comment_review addresser --census C --anchor "<line of code>" --series b

    -- which answers `m.py@b1`. The place is citable without being carried, so
    `add` stays expressible and nothing pays for the other 5,201.

    ! A FENCE IS NEVER CARRIED, asked for or not. It names no place, so there is
    nothing to cite and nothing to rule on.

    Args:
        pages: the pages in scope.
        absent: carry the empty places too. For the caller that specifically
            asks -- a reviewer surveying where prose COULD go rather than
            ruling on prose that is there.
    """
    return {
        "version": VERSION,
        "pages": [
            {
                "path": page.path,
                "sha": page.sha,
                "rows": [
                    page_row(b)
                    for b in page.paragraphs
                    if b.address and (absent or not Kind.holds_no_prose(b.kind))
                ],
            }
            for page in pages
        ],
    }


def read(text: str) -> tuple[dict, str]:
    """A binder read back, or the reason it could not be.

    !! IT REFUSES RATHER THAN COPING. Every one of the four readers this
    replaces guessed at the shape, and a guess that is wrong reads as an EMPTY
    binder -- which downstream is indistinguishable from a run with nothing to
    do. The collator was measured certifying exactly that on 2026-08-20.

    !! THE KEY WAS TESTED FOR PRESENCE AND NOT FOR SHAPE UNTIL 2026-08-25, so
    it coped after all. MEASURED: `{"pages": "oops"}` read CLEAN, and the
    `str(page.get(...))` two callers do over it then raised `AttributeError:
    'str' object has no attribute 'get'` out of `commands/proof.py` as a
    traceback -- past that command's own promise to print `CANNOT READ THE
    BINDER: {why}`. Same for `{"pages": {"a": 1}}` and `{"pages": [1, 2]}`.
    ! WHAT IS CHECKED IS WHAT IS CONSUMED and no more: `rows_of` walks `pages`
    and then each page's `rows`, calling `.get` on both; `proof_setter.run`
    walks `pages` alone, for `path` and `sha`. Nothing here reads a FIELD, so
    nothing here rules on one.

    Returns:
        `(binder, "")` when it reads, or `({}, reason)` when it does not.
    """
    # ! THE PARSE AND THE OBJECT GUARD ARE `json_object.object_of`'s -- see
    # there for why one preamble in two readers was the defect this module's own
    # header describes. What stays here is what a BINDER is.
    loaded, why = object_of(text, "binder")
    if why:
        return {}, why
    if "pages" not in loaded:
        return {}, "carries no `pages` -- is this the output of `census --json`?"
    pages = loaded["pages"]
    if not isinstance(pages, list):
        return {}, f"`pages` is a JSON {type(pages).__name__}, not a list of pages"
    for n, page in enumerate(pages):
        if not isinstance(page, dict):
            return {}, f"page {n} is a JSON {type(page).__name__}, not a page"
        rows = page.get("rows", [])
        if not isinstance(rows, list):
            return {}, f"page {n}: `rows` is a JSON {type(rows).__name__}, not a list"
        for m, row in enumerate(rows):
            if not isinstance(row, dict):
                kind = type(row).__name__
                return {}, f"page {n}, row {m} is a JSON {kind}, not a row"
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
