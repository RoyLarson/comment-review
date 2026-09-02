# An empty --edits file now REFUSES, and SKILL.md still wires a live stage to that command

```
Status:   open
Progress: 0 of 2 tasks closed
Owner:    agents
Requires-Roy: false
Raised:   2026-08-26 (xhigh wave-D review of feat/the-write-chain-of-command,
          2026-08-26)
```

## Objective

`commands/galley.py --edits` was read with a bare `json.loads` until 2026-08-25 and
printed `0 page(s) set, 0 edit(s) refused` at exit 0 on `{}`. It is now read through
`docket/docket.py:read`, which refuses an empty object by name and exits **2**.

**`SKILL.md` still wires a stage to that command**, so a run whose verdicts were all
`clean` -- legitimately nothing to set -- writes `{}` and FAILS the stage.

!! **THE REFUSAL IS KEPT, and `backend` ruled that deliberately on 2026-08-26.**
`--edits` is machine-written from approved text exactly as `--docket` is, so an
empty file and a crashed upstream are the same bytes here too; and reading the same
format a second way inside the command is what `docket.read` exists to end.

! **The fix is on the reader's side, not the refusal's**: a run with nothing to set
does not need a galley, so the stage is SKIPPED rather than called with an empty file.
That is a condition in `SKILL.md`, which is `agents` lane and not `backend`'s to write.

! `commands/galley.py` is DEPRECATED for the write chain -- `commands/proof.py` runs the
full chain from a binder -- but it still runs and `SKILL.md` still names it, so the
stage is live until the skill is rewired.

## Tasks

- [ ] T1 | SKILL.md: the stage that calls commands/galley.py SKIPS the call when
      the edits object would be empty
- [ ] T2 | SKILL.md: say that an empty --edits is an exit-2 refusal, so a reader
      does not read it as a run with nothing to do
