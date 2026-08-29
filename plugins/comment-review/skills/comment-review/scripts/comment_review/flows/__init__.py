"""One whole run, calling the modules. A flow decides ORDER, not behaviour.

    census         stages 2-3 -- every page in scope, formatted for the agents
    page_for       the read-and-build step a flow needs a page from; decides
                    no order itself -- see below for why it sits here anyway
    proof_setter   the results-side flow -- calls the galley, the compositor
                    and `prove_unchanged` in order, from a role's alterations to
                    a drafted file a human can read
    revise         pulls one revise -- copies the repo, calls `proof_setter`,
                    overlays the drafts -- for `TODO/the-flow-assumes-every-
                    role-reads-at-once.md` T3

!! A FLOW IS WHERE A SEQUENCE LIVES so that no module has to know it is
part of one. Ruled 2026-08-24 -- `docs/decision-log.md Process: #12`.

! `census` WAS THREE SUBJECTS. `code_names` left for `concordance` on
2026-08-24; the row shape it emits is still the binder's -- P10. ! And the flow
half is not here at all yet: it is inside `commands/census.py`, which is
`TODO/the-flow-lives-in-the-command.md`.

! `page_for` DECIDES NO ORDER, AND SITS HERE ANYWAY. It was cut from five
sites duplicating the same read (`read_source`, `language_for`, `page_for`,
carry the sha), commit `4290bfe`, but only `proof_setter.run`'s two reads were
repointed at it -- the other four (`commands/census.py`,
`results/compositor.py` twice, `scripts/render_page.py`) are
`TODO/no-step-produces-a-page.md`. So the module reads as a step the write
chain depends on, not yet as a step every caller shares.
"""
