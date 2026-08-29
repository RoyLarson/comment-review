"""The pages, and the folder of them that is handed over.

    page       ONE FILE -- its paragraphs tied to the places on it
    binder     what a BINDER is on disk, and how one is read back
    annotate   the resolution a reviewer would otherwise do by hand
    addresses  which paragraph of a census sits at which address

!! A PAGE AND A RECORD ARE IMMUTABLE ARTIFACTS THE SYSTEM CREATES. Ruled by Roy,
2026-08-24. Nothing downstream may treat a record as the thing that carries an
answer BACK to the page -- what does is undecided, and twelve tests are held
rather than patched because of it. See `TODO/nothing-makes-the-fair-copy.md`.

! `annotation` IS THE BINDER'S WORD and only one thing in this system may carry
it -- the sticky note a page gets for information a reader needs. Ruled
2026-08-24 by testing both candidates on agents; `docs/decision-log.md
Vocabulary: #13`. The lexer's three diagnostics are ERRORS, not notes.

!! THE INVENTORY ABOVE LISTED `record` AND `held` UNTIL 2026-08-29, AND BOTH
LEFT ON `b50e7a4` -- so `from comment_review.binder.record import seed`, written
by anyone following it, was an ImportError; and `binder.py`, which every other
module in this package imports, was named nowhere. ! The line *"`record` IS FOUR
SUBJECTS AND IS NOT YET SPLIT -- P10"* is superseded with the module: what a
role fills is now `flows/marks.py`'s edit_copy, seeded per role and checked by
`desk/mark.py`.
"""
