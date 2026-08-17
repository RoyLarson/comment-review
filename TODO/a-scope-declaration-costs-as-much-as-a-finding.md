# A scope declaration costs as much as a finding

```
Status:   open
Progress: 0 of 4 tasks done
Owner:    session * Roy (* 1 ruling)
Raised:   2026-08-17, the day the query contract landed. `module-context`'s report on a
          1,174-block repo is 1.1 MB and most of it is the words "outside my role".
```

## Objective

**`outside my role` now carries the same payload as a real finding, and on most repos it is
most of what one role emits.**

The contract landed 2026-08-17: a `query` must NAME its shape in the brief's own words, carry
`EVIDENCE` and a `QUOTE` that resolve, and say what WOULD settle it. Roy ruled it, and the
reason holds -- *"Not mine"* is an admission, a showing is a finding, and the block otherwise
leaves the report certified by nobody.

! The cost was not measured at the time. Measured now, on a 1,174-prose-block repo where
`module-context`'s remit covers 175:

| role | report |
| --- | --- |
| `module-context` | **1.1 MB** |
| `ownership-context` | 660 KB |
| `function-context` | 512 KB |
| `block-context` | 486 KB and still writing |

`module-context` files the fewest substantive findings and writes the largest report, because
roughly a thousand blocks are outside its remit and each one now costs a full record.

!! **It pulls against the change made the same day.** The interval exemption freed budget by
removing records a role did not owe -- measured, `function-context` went from 11 findings to 68
because *"the role spent its budget reading instead of accounting."* The query contract spends
budget by making each remaining out-of-role record heavier. Both are right on their own terms
and they are pulling on the same rope.

## ! What is NOT established

- **That the reports are too large for anything.** Nothing failed. `verdicts.py` parses them
  mechanically and the task agent reads the JOIN, not the reports.
- **That the payload is wasted.** An `outside my role` query with a `QUOTE` proves the role read
  the block. That is the fabricated-`clean` defence, and it is the reason the contract exists.
- **The token cost specifically.** `block-context` was measured at ~21 minutes and 491k tokens
  as the heaviest role, and its remit is every claim in every block -- that is a different cause
  from this one and must not be folded into it.

## Tasks

- [ ] Measure it before changing anything: what fraction of `module-context`'s report is
      out-of-role queries, by bytes and by record count. ! The 1.1 MB figure is a file size and
      attributing it is an inference this file has not earned.

- [ ] * Rule on whether an `outside my role` query may carry a LIGHTER payload than the other
      two shapes. ! The three shapes already route differently -- the first says which scope owns
      the block and asks nothing of the author, the other two are work. A payload that follows
      the routing is consistent with that. **Against it:** the `QUOTE` is what proves the block
      was read, and dropping it on the shape a reviewer reaches for when it has nothing to say
      is dropping it exactly where the fabrication risk is highest.

- [ ] If it stays as it is, say so where the cost lands. A role writing a megabyte of scope
      declarations is the contract working, and nothing tells an operator that.

- [ ] ! Do not solve this by exempting a role from blocks outside its remit. That is the
      forced-record problem in reverse, and `module-context` returning `query` rather than
      `clean` on a block it never read is deliberate -- it does not certify what it has not seen.
