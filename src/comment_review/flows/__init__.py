"""One whole run, calling the libraries. A flow decides ORDER, not behaviour.

    census   stages 2-3 -- every page in scope, formatted for the agents

!! A FLOW IS WHERE A SEQUENCE LIVES so that no library module has to know it is
part of one. Ruled 2026-08-24 -- `docs/decision-log.md Process: #12`.

! `census` IS THREE SUBJECTS AND IS NOT YET SPLIT -- P10. The flow half belongs
here; the row shape it emits is the binder's, and `code_names` builds a corpus
over the whole checkout and belongs to neither (P11).

! THE RESULTS-SIDE FLOW DOES NOT EXIST YET. It is what would call the galley,
the compositor and `prove_unchanged` in order, instead of each carrying a CLI.
"""
