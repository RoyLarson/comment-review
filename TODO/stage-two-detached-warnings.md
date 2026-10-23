# Ask the human about each detached-documentation warning at stage 2

```
Status:   open
Progress: 0 of 1 tasks closed
Owner:    agents
Requires-Roy: false
Raised:   2026-10-23 (decision-log.md Addressing #29; Rust reader spec O4)
```

## Objective

The gather now prints one stderr line per detached doc comment, in the form
`warning: <path>@<cue>: detached documentation for <owner cue>`, and exits as it
would without them. Stage 2 of the skill does not yet act on those lines.

decision-log.md Addressing #29 (Roy, 2026-10-21) settles what the task agent
does with them: *"I would go with a warning and a thing to the task agent to ask
but allow to proceed with"*. The run is not stopped. The task agent asks the
human about each warning, records the answer, and continues whatever the answer
is. Moving the detached run to its owner's `a` place is an ordinary placement
change that `prove_unchanged` permits.

Since decision-log.md Addressing #31 (Roy, 2026-10-23), a detached run shares
its place's paragraph with any other comment at that place, and one paragraph
can carry two warnings.

## Tasks

- [ ] T1 | Update SKILL.md stage 2 to ask about each gather warning line, then
      proceed. Verify: one ask per warning
        > 2026-10-23 Record each answer; the run continues whatever the answer is
