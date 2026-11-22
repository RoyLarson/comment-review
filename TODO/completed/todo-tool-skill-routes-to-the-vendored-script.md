# The todo-tool skill sends board writes to the vendored script

```
Status:   closed
Progress: 1 of 1 tasks closed
Owner:    systems
Requires-Roy: false
Raised:   2026-11-22 (review)
```

## Objective

The todo-tool skill sends board writes to the vendored script.

## Tasks

- [-] T1 | The skill and the vendored script are deleted | 744ae5fb6f241f3f6c75ddc6cb85b8676d0b0a35 | Point
      .claude/skills/todo-tool/SKILL.md's board writes at the installed
      job-board, not scripts/todo_tool.py
        > 2026-11-22 Check: grep todo_tool.py in the skill's SKILL.md is empty
