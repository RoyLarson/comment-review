# One obvious way

```
Status:   open
Progress: 0 of 21 tasks closed
Owner:    backend
Requires-Roy: true
Raised:   2026-11-05 (Process #281 and the three flow audits, 2026-11-05)
```

## Objective

Every job in the flows is done one way: one implementation is kept and the
others are removed (Process #281).

Three read-only audits on 2026-11-05 found jobs done by two or more code paths.
The highest risks are where two stages can disagree about the same file or
address: whether an address is real (verify, fill and held_at decide it three
ways), how a flattened name becomes a path (real_path, printed_name, fill's
_sheet_for, master_proof), and whether a file outside --repo is in the run
(gather admits it, prove_unchanged refuses it). The rest are artifact loading
and saving, root handling, refusal reporting, and logic that sits in commands
instead of flows. The audits read the code and reproduced nothing; each task's
evidence is checked when the task is worked.

## Tasks

- [ ] T1 | Make fill read the page an address names through page_named
- [ ] T2 | Make held_at refuse a cue its page lacks instead of returning empty
      text
- [ ] T3 | Make one rule, folded or exact, decide an address's path half for
      verify, transcribe, fill, bus and check
- [ ] T4 | Make master_proof and fill invert a flattened name through real_path
- [ ] T5 | Make gather refuse a file outside --repo, as prove_unchanged does
- [ ] T6 | Make fill split an address with cue_of
- [ ] T7 | Make page.py and paragraph.py read a cue with cue_of
- [ ] T8 | Make carry print addresses with address_for
- [ ] T9 | Make the compositor, prove_unchanged and taken_in read a file through
      one page reader
- [ ] T10 | Make fill's quoted_sources use the collator's line reader
- [ ] T11 | Make every command save its JSON through proof_io
- [ ] T12 | Add load_topology to proof_io for collate, distribute and topology
- [ ] T13 | Make the answers file read through proof_io with READ_ERRORS
- [ ] T14 | Make every command resolve its repo root once, from the binder's
      root where it has one
- [ ] T15 | Move the exit codes and refusal printing into one console module
- [ ] T16 | Remove the reading-context checks repeated in bus, the carry command
      and the collate command
- [ ] T17 | Move the flow logic out of the commands into flows
- [ ] T18 | Remove stable() from binder/addresses
- [ ] T19 | Add load_docket to proof_io
- [ ] T20 | Make proof load its proof, copy and docket through proof_io
- [?] T21 | Decide how a flow reports a refusal
        > 2026-11-05 Today: raise, return a reason tuple, or emit events
