# The deprecated reader cannot replay a held run, which is the only reason it exists

```
Status:   open
Progress: 0 of 3 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-19 (the seven-agent address review, 2026-08-19)
```

## Objective

!! **`--convert` DROPS 100% OF A HELD 0.2.x REPORT AND EXITS 0.** Measured 2026-08-19: 2 findings
in, 0 filled records out, return code 0.

**Replaying held reports is the only reason the deprecated parser was kept**, and it is how 0.2.1
and 0.2.2 were validated cheaply -- five joins over one set of reports, ~1.6M tokens of review
reused. `record.py` says so at the reader: it exists to parse runs already recorded so
`evidence/` can be compared against the format that replaced it.

**The cause is a guard that never fires.** The 0.2.x `BLOCK` form is
`<index> | <path>:<start>-<end>`, so `parse_report` puts that LINE address into `Finding.address`.
`verdicts.py`'s index translation is written `if not f.address` -- and the field is already full,
of the retired form. So the address reaches `entry_for`, resolves to nothing, and every record
joins as *"names no block"*.

! **`record.convert` keys entirely on `f.address` and never reads `f.block`**, so the bridge
carries nothing across, in silence. ! A held report is a REGRESSION TEST; nothing in the suite
would notice this happening again.

## Tasks

- [ ] !! **A LINE address lands in `Finding.address` and can never join.** The
      0.2.x `BLOCK` form is `&lt;index&gt; |
      &lt;path&gt;:&lt;start&gt;-&lt;end&gt;`, and `parse_report` puts that tail
      into `address`. `verdicts.py`'s index translation is guarded by `if not
      f.address`, so it never fires. **Fix: ignore the tail unless it holds an
      `@`, then fall through to the index.**
- [ ] **`record.convert` keys entirely on `f.address` and never reads `f.block`**,
      so the bridge carries nothing across, silently. Measured: 2 findings -> 0
      filled records, rc=0.
- [ ] **A held report is a REGRESSION TEST, and this is the gate that says so.**
      Add one: a 0.2.x report in the repo, converted against a census, asserting
      every record arrives. Nothing today would notice this again.
