# The task agent has no vocabulary home and is never told the command set

```
Status:   decision-needed
Progress: 3 of 8 tasks closed
Owner:    agents (the instructions) - backend (the enum they derive from)
Requires-Roy: false
Raised:   2026-08-30 (2026-08-30, filing the distribute vocabulary entry for Task 14:
          the term had no home because the shipped vocabulary is keyed by the four
          editorial roles and the task agent is not one of them, so check_vocabulary
          would have refused it as defined for nobody)
```

## Objective

The task agent has no vocabulary home and is never told the command set.

## Tasks

- [-] T1 | Task-agent role and its gate mapping delivered; distribute left undefined | 5820169c | Implement
      a task-agent entry in `references/vocabulary.toml`'s `[roles]`, so a term
      only the TASK AGENT uses has somewhere to live. Verify: `distribute` is
      defined once and given to that role, and `scripts/check_vocabulary.py`
      passes -- today the gate refuses a definition written for nobody, so a
      command name cannot be defined at all.
- [ ] T2 | Implement the command set reaching the agent-facing instructions,
      DERIVED from `__main__.COMMANDS` rather than typed by hand. Verify: every
      agent- facing command appears in the instructions, and a gate goes red
      when a member is added to the enum without the instructions changing.
- [ ] T3 | Update `tests/gates/test_skill_commands.py` to check the second
      direction. Verify: `test_every_command_named_in_agent_facing_prose_exists`
      checks named-then-exists; add exists-then-named over the agent-facing
      subset, and confirm it goes red when a command is added and left unnamed.
- [x] T4 | Ruled: the 12 a stage runs; filed as T7, T8; Process #349 | 9304a51a21c437f2766cad8cbed14801f062cf7d | Decide
      which commands are agent-facing. Not every member of `COMMANDS` belongs in
      an agent's instructions -- the dev tools and the gates do not -- so the
      second direction needs a stated subset before it can be checked.
        > 2026-11-22 Outcome: the 12 a stage runs; delete carry (Process #349)
- [x] T5 | task-agent role added; check_vocabulary maps it to SKILL.md and write.md; 0 drift | 5820169c | Implement
      the task-agent role in vocabulary.toml and its check_vocabulary mapping;
      verify the gate reports 0 drift
- [ ] T6 | Define distribute in vocabulary.toml and give it to the task-agent
      role; verify check_vocabulary passes
- [ ] T7 | Name compositor and taken_in as dev-only in
      tests/gates/test_skill_commands.py
        > 2026-11-22 Check: the gate lists exactly those two as dev-only
- [ ] T8 | Delete the carry command and flows/carry.py, which no stage runs
        > 2026-11-22 Check: grep carry in src/comment_review/commands is empty
