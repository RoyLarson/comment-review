# Route every machine read and write through a flow

```
Status:   open
Progress: 0 of 6 tasks closed
Owner:    backend
Requires-Roy: true
Raised:   2026-09-03 (systems)
```

## Objective

**Only a flow reaches the machine.** A piece that needs text written returns a
string; the flow hands it to `machine.repo`. `decision-log.md Process: #80`.

Roy, 2026-09-03, ruling `results.compositor.approve` deleted: *"that is not the
way it is acceptable to happen anymore. The flows get a string from things that
need to write and sends it to the machine to be written. Nothing in the
beginning, middle, end pieces gets to do that. It is all flow and only flow can
go to the machine and get text or send text to be written."*

    READ    a flow calls the machine, and hands the text down
    WORK    binder, desk, docket, results take and return VALUES
    WRITE   a piece returns a string; the FLOW gives it to the machine

! **IT EXTENDS `Process: #65` FROM CONTAINERS TO BYTES**, and it is the rule
`docs/conventions.md` already states one level up -- *"No direct coupling inside
of ends and middle, flows are neither they run the steps."* I/O is a coupling to
the checkout, and the ends were reaching it directly.

!! **THE RULING IS WIDER THAN THE FUNCTION IT WAS GIVEN ON.** MEASURED
2026-09-03, every call into `machine.repo` from outside `machine/` and outside
`flows/`:

| site | what it does | T |
| --- | --- | --- |
| `results/compositor.py:364 approve` | `write_raw` over the REAL file, no caller anywhere | T1 |
| `results/compositor.py:361 draft` | `write_raw` into a scratch path -- **live**, so a refactor | T2 |
| `results/compositor.py:404, :436` | `read_source` in `lossless` and the identity check | T3 |
| `results/prove_unchanged.py:245` | `read_raw` over a sibling | T4 |
| `desk/collator.py:239` | `read_raw` for a cited source | T5 |

! **ONLY T1 IS A DELETE.** The rest have callers, so each is a move: the piece
returns or receives text and the flow performs the I/O.

!! **`desk/collator.py` IS THE INTERESTING ONE.** `Process: #62`'s 2026-08-30
qualification PERMITS that read -- *the middle touches no PAGES; a cited evidence
file carries no `sha` and may be read.* **That permission was about WHAT may be
read, not about WHO reads it.** Under `#80` the read still happens; the flow
performs it and hands the text to `verify_report`.

! **T6 IS OPEN AND IS ROY'S.** His sentence says *only flow*, and
`conventions.md` puts `flows` and `commands` together as neither end nor middle.
Four command sites do I/O today -- `commands/census.py:163`,
`commands/proof.py:206`, `commands/prove_unchanged.py:84-85`. Reading it either
way changes real code, so it is asked rather than inferred.

## Tasks

- [ ] T1 | Delete results.compositor.approve, which has no caller and writes the
      real file
- [ ] T2 | Move the write in results.compositor.draft out to the flow that calls
      it
- [ ] T3 | Move read_source out of results.compositor lossless and the identity
      check
- [ ] T4 | Move read_raw out of results.prove_unchanged
- [ ] T5 | Move the cited-source read out of desk.collator into the flow
- [?] T6 | Decide whether commands may reach the machine, or only flows
