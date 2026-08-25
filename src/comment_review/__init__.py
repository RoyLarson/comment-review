"""The plugin's Python: read a page, hand it to the roles, set back what returns.

The packages beneath this one are the stages in that order:

    machine   what the CHECKOUT and the interpreter say
    reading   a file becomes places and prose
    binder    the pages, and the record a reviewer fills
    desk      what a role is GIVEN, and what it HANDS BACK
    results   the answer set into a file, and the proof code survived
    flows     one whole run, calling the above
    commands  the entry points -- P2, not yet split out

!! A LIBRARY MODULE DOES ONE JOB AND HAS NO CLI; A FLOW CALLS LIBRARIES; A
COMMAND EXPOSES A FLOW. Ruled 2026-08-24 -- `docs/decision-log.md Process: #12`.
! It is NOT yet true here: ten modules still carry a `main()`, which is P2 of
`docs/plans/0.2.4-rework-the-boundaries-are-not-real.md`.

!! `referrers` SITS AT THIS ROOT BECAUSE NOTHING HAS RULED WHERE IT GOES, and
root means UNPLACED rather than top-level. It and `flows.census.code_names` both
build a corpus out of the whole checkout so a claim on a page can be resolved
against something other than itself; neither performs an operation ON the
machine, and neither knows anything about a page. Open as P11 of that plan.
"""
