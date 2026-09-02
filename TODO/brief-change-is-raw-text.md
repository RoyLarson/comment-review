# The brief tells roles to write change as raw text; the checker refuses anything but an array of lines

```
Status:   open
Progress: 2 of 2 tasks closed
Owner:    agents
Requires-Roy: false
Raised:   2026-08-29 (found sweeping reviewer-brief.md against its consumers on
          feat/the-mark-and-the-collator, 2026-08-29)
```

## Objective

The brief tells roles to write change as raw text; the checker refuses anything but an array of lines.

## Tasks

- [x] T1 | RULED 2026-08-28 -- the form is RAW TEXT, decision-log Vocabulary 27, and both sides already say it: reviewer-brief.md and desk/mark.py, which refuses a non-str by name | b9dce3d | Decide
      which form a role writes, and make reviewer-brief.md:140 and desk/mark.py
      say the same one
- [x] T2 | FINISHED -- the worked example's raw string is the ruled form; tests/test_brief_worked_example.py runs it through mark --check | b9dce3d | Carry
      the decision into the worked example, which still shows a raw string
