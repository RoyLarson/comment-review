# SKILL.md names six commands that moved to prototype

```
Status:   open
Progress: 0 of 4 tasks done
Owner:    agents
Requires-Roy: true
Raised:   2026-08-25 (the prototype move, 2026-08-25)
Updated:  2026-08-26 — galley is now a SEVENTH command needing rewiring, and it is the
          one that still runs. commands/galley.py was emptied on 2026-08-26 (Roy:
          'Create the galley entry_point function that points to proof_setter and delete
          the unused command') and is now the old NAME for proof: main() calls
          proof.main(). The NAME still resolves through __main__.py, so a SKILL.md stage
          that invokes galley reaches the chain -- but the FLAGS do not carry over.
          SKILL.md line 918 spells --census/--edits; proof takes --binder/--docket,
          so the old invocation reaches proof's parser and is refused as an unrecognised
          argument. Rewiring that stage is agents lane. See docs/history.md for what the
          command used to do.
```

## Objective

SKILL.md names six commands that moved to prototype.

## Tasks

- [ ] Decide what replaces the record as what a role hands back -- alterations, per
      decision-log Process #14
- [ ] Rewrite the stages that invoke the four moved commands
- [ ] Say what regenerates the brief verdict table, or that nothing does
- [ ] SKILL.md:741 also still spells the retired subcommand token `verdicts`
      (check_vocabulary.py RETIRED now includes the plural, added while retiring
      `verdict` -> `instruction`). Renaming the token needs the same design
      decision as the rest of this TODO -- what replaces the stage-5 collator
      invocation -- so it was left as-is rather than inventing a placeholder
      command name.
