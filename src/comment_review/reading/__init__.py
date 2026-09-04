"""A file becomes places and prose. Nothing here knows what a page is.

    language    one row per language -- its comment syntax and its keywords
    lexer       the prose in a file, and where each paragraph starts and ends
    series      what a SERIES is -- its cue letter, and the two kinds a place
                 in it can be
    addresser   the places a file HAS, filled or not

! `series` WAS ABSENT FROM THIS INVENTORY UNTIL 2026-08-29. It was cut out of
`addresser` and `lexer` on Roy's 2026-08-25 retraction, quoted at its own head.

!! THE TWO LEAVES DO NOT KNOW EACH OTHER: the addresser knows nothing about
prose, the lexer nothing about places. That is what lets a page be one subject --
a place has no prose in it, and prose has no place until a page puts the two
together. `tests/test_page.py::TestTheTwoLeaves` enforces it.

! `addresser` IS THREE SUBJECTS AND IS NOT YET SPLIT -- P10. Its place-emitting
half belongs here; the half that answers census queries is the binder's.
"""
