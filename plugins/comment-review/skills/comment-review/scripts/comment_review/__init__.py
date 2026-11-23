"""The plugin's Python: read a page, hand it to the roles, set back what returns.

The packages beneath this one are the stages in that order:

    machine      what the checkout and the interpreter say
    reading      a file becomes places and prose
    binder       the pages, and the record a reviewer fills
    concordance  the checkout indexed, so a claim can be resolved off-page
    desk         what a role is given, and what it hands back
    docket       every alteration the run is asked to make
    results      the answer set into a file
    flows        one whole run, calling the above
    commands     the entry points

!! A module does one job and has no CLI; a flow calls modules; a command
exposes a flow. Stage 2's orchestration is `flows/gather.py`'s `STEPS`, and
`commands/gather.py` builds no page.

! Beside the packages sit the leaves -- `constants`, `exceptions`,
`differences` and `read_from` -- which any area may import, and `__main__`,
which dispatches `python -m comment_review <command>`.
"""
