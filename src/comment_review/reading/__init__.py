"""A file becomes places and prose. Nothing here knows what a page is.

    language    the shipped language definitions, one file per language
    readers     picks a file's reader: `python/` or `rust/`, which find its prose
    paragraph   one unit of prose, as a reader produces it
    series      what a SERIES is -- its cue letter, and the two kinds a place
                 in it can be
    addresser   the places a file HAS, filled or not

!! THE ADDRESSER KNOWS NOTHING ABOUT PROSE. That is what lets a page be one
subject -- a place has no prose in it, and prose has no place until a page puts
the two together.

! `addresser` IS THREE SUBJECTS AND IS NOT YET SPLIT -- P10. Its place-emitting
half belongs here; the half that answers binder queries is the binder's.
"""
