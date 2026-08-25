"""One whole run, calling the libraries. A flow decides ORDER, not behaviour.

    census   stages 2-3 -- every page in scope, formatted for the agents

!! A FLOW IS WHERE A SEQUENCE LIVES so that no library module has to know it is
part of one. Ruled 2026-08-24 -- `docs/decision-log.md Process: #12`.

! `census` WAS THREE SUBJECTS. `code_names` left for `concordance` on
2026-08-24; the row shape it emits is still the binder's -- P10. ! And the flow
half is not here at all yet: it is inside `commands/census.py`, which is
`TODO/the-flow-lives-in-the-command.md`.

! THE RESULTS-SIDE FLOW DOES NOT EXIST YET. It is what would call the galley,
the compositor and `prove_unchanged` in order, instead of each carrying a CLI.
"""
