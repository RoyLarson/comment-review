"""The plugin's Python: read a page, hand it to the roles, set back what returns.

The packages beneath this one are the stages in that order:

    machine      what the CHECKOUT and the interpreter say
    reading      a file becomes places and prose
    binder       the pages, and the record a reviewer fills
    concordance  the checkout INDEXED, so a claim can be resolved off-page
    desk         what a role is GIVEN, and what it HANDS BACK
    results      the answer set into a file, and the proof code survived
    flows        one whole run, calling the above
    commands     the entry points

!! A MODULE DOES ONE JOB AND HAS NO CLI; A FLOW CALLS MODULES; A
COMMAND EXPOSES A FLOW. Ruled 2026-08-24 -- `docs/decision-log.md Process: #12`.

! IT IS NOT YET TRUE OF `flows`. Lifting the entry points out showed the
census's orchestration was inside `main` all along, so `commands/census.py`
still builds pages that a flow should build -- see
`TODO/the-flow-lives-in-the-command.md`.

! NOTHING SITS AT THIS ROOT ANY MORE. `referrers` did, meaning UNPLACED rather
than top-level, until `concordance` was ruled on 2026-08-24.
"""
