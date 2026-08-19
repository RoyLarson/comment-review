# The deprecated reader cannot replay a held run, which is the only reason it exists

```
Status:   open
Progress: 0 of 3 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-19 (the seven-agent address review, 2026-08-19)
```

## Objective

The deprecated reader cannot replay a held run, which is the only reason it exists.

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
