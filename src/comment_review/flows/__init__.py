"""One whole run, calling the modules. A flow decides ORDER, not behaviour.

    gather         stage 2 -- every page in scope, annotated and bound into
                    the binder. `STEPS` is the chain, as data
    annotations_for stage 3 as one step of it -- what the concordance can
                    settle, over every paragraph the gather carried
    page_for       the read-and-build step a flow needs a page from; decides
                    no order itself -- see below for why it sits here anyway
    carry          makes the binder carry an empty place it dropped, so an
                    `add` has an address to cite
    fan_out        splits a binder by a stage's dispatches -- one seeded
                    edit_copy per dispatch, refusing an overlap or a gap
    marks          hands a role an edit_copy to fill, and checks what comes
                    back against every rule `desk/marks/mark.py` settles
    human          finds a human question in the copies or a turn's answers,
                    before the fold, and reads the human's answers file
                    (`Process: #197`, `#198`)
    turn          a batch answered, applied to the copies, folded again --
                    and the master proof as the state between turns
    proof_io       that proof on disk: the load and the save, raw JSON at
                    those two ends only (`Process: #65`, `#67`)
    proof_setter   the results-side flow -- calls the galley, the compositor
                    and `prove_unchanged` in order, from a role's alterations to
                    a drafted file a human can read
    revise         pulls one revise -- drafts the docket's pages through
                    `proof_setter` and writes each at its repo path, copying
                    no other file (`Process: #117`) -- for `TODO/the-flow-
                    assumes-every-role-reads-at-once.md` T3

! `carry`, `fan_out` AND `marks` WERE ABSENT FROM THIS INVENTORY UNTIL
2026-08-29, having landed with the mark and the collator.

!! A FLOW IS WHERE A SEQUENCE LIVES so that no module has to know it is
part of one. Ruled 2026-08-24 -- `docs/decision-log.md Process: #12`.

! `gather` WAS THREE SUBJECTS, UNDER THE RETIRED NAME `census`. `code_names`
left for `concordance` on 2026-08-24; the row shape it emits is still the
binder's -- P10. ! And the flow half sat inside the command until `gather`
landed here -- `TODO/the-flow-lives-in-the-command.md` T2.

! `page_for` DECIDES NO ORDER, AND SITS HERE ANYWAY. It was cut from five
sites duplicating the same read (`read_source`, `language_for`, `page_for`,
carry the sha), commit `4290bfe`, but only `proof_setter.run`'s two reads were
repointed at it; `gather` followed. The other three (`results/compositor.py`
twice, `scripts/render_page.py`) are `TODO/no-step-produces-a-page.md`. So
the module reads as a step two chains depend on, not yet as a step every
caller shares.
"""
