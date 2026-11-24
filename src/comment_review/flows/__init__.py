"""One whole run, calling the modules. A flow decides ORDER, not behaviour.

    gather          stage 2 -- every page in scope, bound into the binder.
                    `STEPS` is the chain, as data
    referrers       stage 3, inbound -- the `git grep` behind `referrers`
    page_for        acquires a source snapshot and admits it as a complete page
    source          source acquisition outcomes for filesystem and revision
                    reads
    compositor      acquires, admits and sets one held source snapshot
    on_the_page     reads addressed pages once per caller-owned snapshot cache
    addresses       looks a place up on the page it names, by line or by
                    address
    reading_context resolves installed reading metadata and validates fresh
                    per-file overrides
    read_diagnostics retained source context and report formatting for read
                    failures
    carry           makes the binder carry an empty place it dropped, so an
                    `add` has an address to cite
    fan_out         splits a binder by a stage's dispatches -- one seeded
                    edit_copy per dispatch, refusing an overlap or a gap
    distribute      seeds the edit_copy a role fills, one entry per row it is
                    dealt, with the address already written
    fill            places one role's ruling on its edit copy, refusing any
                    ruling a mark's own rules would refuse
    topology        whether a topology fits a binder, and writes one that does
    places          places from reviewer copies
    answers         reads one role's answers against the slots that went out
                    to it
    mark_errors     every place a role must go back to, as addresses and
                    reasons
    verify          what a stage's returned copies can be wrong about against
                    the pages and the files they cite
    human           finds a human question in the copies or a turn's answers,
                    before the fold, and reads the human's answers file
    bus             the stage transitions as messages, one handler each --
                    copies returned, answers returned, dispositions written.
                    The turn and the master proof between turns live here
    proof_io        the middle's artifacts on disk -- binder, copy, proof,
                    batch: the load and the save, raw JSON at those two
                    ends only
    transcribe      decided places, as the docket the write chain reads
    proof_setter    the results-side flow -- calls the galley and the
                    compositor from a role's alterations to a drafted file a
                    human can read, then proves only comments changed
    prove_unchanged admits exact current and revision pages before comparing
                    executable code
    revise          pulls one revise -- drafts the docket's pages through
                    `proof_setter` and writes each at its repo path, copying
                    no other file

A flow is where a sequence lives, so that no module has to know it is part of
one. Not every module here is a flow: `page_for`, `source`, `on_the_page`,
`addresses`, `reading_context`, `read_diagnostics`, `places`, `proof_io`,
`human` and `referrers` decide no order, and hold the reads, writes and
conversions the flows share.

Every module here that reads a page reads it through `page_for.page_of` -- the
flows `gather`, `proof_setter`, `fill`, `revise`, `compositor` and
`prove_unchanged`, and the shared `on_the_page` -- so a change to how a page is read
is one edit.
"""
